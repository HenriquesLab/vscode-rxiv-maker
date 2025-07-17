"""Pytest configuration and fixtures for installation tests."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

import docker
from docker.errors import DockerException, ImageNotFound
from docker.models.containers import Container

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from rxiv_maker.install.manager import InstallManager, InstallMode


class DockerTestManager:
    """Manager for Docker-based installation tests."""

    def __init__(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
            self.client.ping()
        except DockerException as e:
            pytest.skip(f"Docker not available: {e}")

    def create_test_container(
        self,
        image: str = "ubuntu:22.04",
        command: str | None = None,
        environment: dict[str, str] | None = None,
        volumes: dict[str, dict[str, str]] | None = None,
        working_dir: str = "/workspace",
    ) -> Container:
        """Create a test container for installation testing."""
        container_config = {
            "image": image,
            "command": command
            or "sleep 7200",  # Keep container alive longer for session
            "environment": environment or {},
            "volumes": volumes or {},
            "working_dir": working_dir,
            "detach": True,
            "remove": True,  # Auto-remove when stopped
            "platform": "linux/amd64",  # Consistent platform
        }

        try:
            container = self.client.containers.run(**container_config)

            # Wait for container to be ready
            for _ in range(30):  # 30 second timeout
                container.reload()
                if container.status == "running":
                    break
                time.sleep(1)
            else:
                raise RuntimeError("Container failed to start within timeout")

            return container
        except ImageNotFound:
            pytest.skip(f"Docker image {image} not found")
        except DockerException as e:
            pytest.fail(f"Failed to create container: {e}")

    def prepare_ubuntu_container(self) -> Container:
        """Create Ubuntu container with basic setup for testing."""
        # Create temporary directory for test files
        temp_dir = tempfile.mkdtemp()

        volumes = {temp_dir: {"bind": "/workspace", "mode": "rw"}}

        environment = {
            "DEBIAN_FRONTEND": "noninteractive",
            "TZ": "UTC",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONUNBUFFERED": "1",
        }

        container = self.create_test_container(
            image="ubuntu:22.04",
            environment=environment,
            volumes=volumes,
            working_dir="/workspace",
        )

        # Install basic dependencies
        setup_commands = [
            "apt-get update",
            "apt-get install -y --no-install-recommends python3.11 python3.11-venv python3-pip curl ca-certificates",
            "update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1",
            "update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1",
            "python3 -m pip install --upgrade pip setuptools wheel",
        ]

        for cmd in setup_commands:
            result = container.exec_run(cmd, workdir="/workspace")
            if result.exit_code != 0:
                pytest.fail(
                    f"Setup command failed: {cmd}\\nOutput: {result.output.decode()}"
                )

        return container

    def cleanup_container(self, container: Container):
        """Clean up test container."""
        try:
            container.stop()
        except DockerException:
            pass  # Container might already be stopped/removed


@pytest.fixture(scope="session")
def docker_manager():
    """Provide Docker test manager."""
    return DockerTestManager()


@pytest.fixture(scope="session")
def ubuntu_container_session(docker_manager):
    """Provide session-scoped Ubuntu container for testing."""
    container = docker_manager.prepare_ubuntu_container()
    yield container
    docker_manager.cleanup_container(container)


@pytest.fixture
def ubuntu_container(ubuntu_container_session):
    """Provide Ubuntu container (backed by session-scoped container)."""
    # Clean up any previous test artifacts
    ubuntu_container_session.exec_run("rm -rf /tmp/test_*")
    ubuntu_container_session.exec_run("rm -rf /workspace/test_*")
    yield ubuntu_container_session


@pytest.fixture(scope="session")
def test_package_wheel():
    """Create test wheel package for installation testing (session-scoped)."""
    # Create temporary directory for building wheel
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Copy source code to temp directory
        src_dir = Path(__file__).parent.parent.parent
        shutil.copytree(src_dir / "src", temp_dir / "src")
        shutil.copy2(src_dir / "pyproject.toml", temp_dir / "pyproject.toml")
        shutil.copy2(src_dir / "setup.py", temp_dir / "setup.py")
        shutil.copy2(src_dir / "README.md", temp_dir / "README.md")
        shutil.copy2(src_dir / "LICENSE", temp_dir / "LICENSE")

        # Build wheel
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--outdir",
                str(temp_dir / "dist"),
            ],
            cwd=temp_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to build test wheel: {result.stderr}")

        # Find the wheel file
        wheel_files = list((temp_dir / "dist").glob("*.whl"))
        if not wheel_files:
            pytest.skip("No wheel file created")

        yield wheel_files[0]

    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_install_manager():
    """Provide mock InstallManager for testing."""
    return InstallManager(
        mode=InstallMode.FULL, verbose=True, force=False, interactive=False
    )


@pytest.fixture
def test_manuscript_dir():
    """Create test manuscript directory."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create basic manuscript structure
    manuscript_dir = temp_dir / "test_manuscript"
    manuscript_dir.mkdir()

    # Create config file
    config_content = """
title: "Test Installation Manuscript"
authors:
  - name: "Test Author"
    affiliation: "Test University"
    email: "test@example.com"
abstract: "This is a test manuscript for installation testing."
keywords: ["test", "installation", "rxiv-maker"]
"""

    (manuscript_dir / "00_CONFIG.yml").write_text(config_content)

    # Create main content
    main_content = """
# Test Installation Manuscript

This is a test manuscript to verify that rxiv-maker installation works correctly.

## Introduction

This document tests the basic functionality after installation.

## Methods

We use standard testing methodologies.

## Results

The installation should work correctly.

## Conclusion

Installation testing is important.
"""

    (manuscript_dir / "01_MAIN.md").write_text(main_content)

    # Create bibliography
    bib_content = """
@article{test2023,
  title={Test Article},
  author={Test Author},
  journal={Test Journal},
  year={2023},
  volume={1},
  pages={1-10}
}
"""

    (manuscript_dir / "03_REFERENCES.bib").write_text(bib_content)

    # Create figures directory
    figures_dir = manuscript_dir / "FIGURES"
    figures_dir.mkdir()

    # Create simple Python figure script
    figure_script = """
import matplotlib.pyplot as plt
import numpy as np

# Create simple plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y)
plt.title("Test Figure")
plt.xlabel("X axis")
plt.ylabel("Y axis")
plt.grid(True)
plt.savefig("Figure_1.png", dpi=300, bbox_inches="tight")
plt.close()
"""

    (figures_dir / "Figure_1.py").write_text(figure_script)

    yield manuscript_dir

    shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def docker_image_available():
    """Check if required Docker images are available."""
    try:
        client = docker.from_env()
        client.ping()

        # Try to pull Ubuntu image if not available
        try:
            client.images.get("ubuntu:22.04")
        except ImageNotFound:
            try:
                client.images.pull("ubuntu:22.04")
            except DockerException:
                pytest.skip("Ubuntu 22.04 Docker image not available")

        return True
    except DockerException:
        pytest.skip("Docker not available")


def run_in_container(
    container: Container, command: str, workdir: str = "/workspace"
) -> tuple[int, str]:
    """Run command in container and return exit code and output."""
    result = container.exec_run(command, workdir=workdir)
    return result.exit_code, result.output.decode()


def install_rxiv_maker_in_container(
    container: Container,
    wheel_path: Path | None = None,
    install_mode: str = "full",
    skip_system_deps: bool = False,
) -> tuple[int, str]:
    """Install rxiv-maker in container and return result."""
    if wheel_path:
        # Copy wheel to container using tar archive
        import io
        import tarfile

        # Create tar archive in memory
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            tar.add(wheel_path, arcname=wheel_path.name)

        tar_buffer.seek(0)
        container.put_archive("/workspace", tar_buffer.read())

        install_cmd = f"pip install /workspace/{wheel_path.name}"
    else:
        install_cmd = "pip install rxiv-maker"

    # Set environment variables
    env_vars = {}
    if install_mode != "full":
        env_vars["RXIV_INSTALL_MODE"] = install_mode
    if skip_system_deps:
        env_vars["RXIV_SKIP_SYSTEM_DEPS"] = "1"

    # Run installation command with environment variables
    if env_vars:
        env_str = " ".join(f"{k}={v}" for k, v in env_vars.items())
        install_cmd = f"env {env_str} {install_cmd}"

    return run_in_container(container, install_cmd)


# Mark all tests in this module as requiring Docker
pytestmark = pytest.mark.skipif(
    not os.environ.get("DOCKER_AVAILABLE", "").lower() == "true",
    reason="Docker tests require DOCKER_AVAILABLE=true environment variable",
)
