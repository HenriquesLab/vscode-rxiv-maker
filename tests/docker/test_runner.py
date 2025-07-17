"""Test runner utilities for Docker-based installation testing."""

import logging
import sys
from pathlib import Path

import docker
from docker.errors import DockerException
from docker.models.containers import Container


class DockerTestRunner:
    """Manages Docker containers for installation testing."""

    def __init__(self, verbose: bool = False):
        """Initialize Docker test runner."""
        self.verbose = verbose
        self.logger = self._setup_logger()

        try:
            self.client = docker.from_env()
            self.client.ping()
        except DockerException as e:
            raise RuntimeError(f"Docker not available: {e}")

    def _setup_logger(self) -> logging.Logger:
        """Set up logging."""
        logger = logging.getLogger("docker_test_runner")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        return logger

    def build_test_image(
        self, dockerfile_path: Path, tag: str = "rxiv-maker-install-test:latest"
    ) -> str:
        """Build test Docker image."""
        self.logger.info(f"Building test image: {tag}")

        try:
            # Build image
            image, logs = self.client.images.build(
                path=str(dockerfile_path.parent.parent),
                dockerfile=str(
                    dockerfile_path.relative_to(dockerfile_path.parent.parent)
                ),
                tag=tag,
                pull=True,
                rm=True,
            )

            if self.verbose:
                for log in logs:
                    if "stream" in log:
                        print(log["stream"].strip())

            self.logger.info(f"Successfully built image: {tag}")
            return image.id

        except DockerException as e:
            self.logger.error(f"Failed to build image: {e}")
            raise

    def create_clean_ubuntu_container(
        self, environment: dict[str, str] | None = None
    ) -> Container:
        """Create clean Ubuntu container for testing."""
        self.logger.info("Creating clean Ubuntu container")

        env = {
            "DEBIAN_FRONTEND": "noninteractive",
            "TZ": "UTC",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONUNBUFFERED": "1",
        }

        if environment:
            env.update(environment)

        try:
            container = self.client.containers.run(
                "ubuntu:22.04",
                command="sleep 3600",
                environment=env,
                detach=True,
                remove=True,
                platform="linux/amd64",
            )

            self.logger.info(f"Created container: {container.id[:12]}")
            return container

        except DockerException as e:
            self.logger.error(f"Failed to create container: {e}")
            raise

    def setup_python_in_container(self, container: Container) -> bool:
        """Set up Python 3.11 in container."""
        self.logger.info("Setting up Python 3.11 in container")

        setup_commands = [
            "apt-get update",
            "apt-get install -y --no-install-recommends python3.11 python3.11-venv python3.11-dev python3-pip curl wget git ca-certificates build-essential",
            "update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1",
            "update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1",
            "python3 -m pip install --upgrade pip setuptools wheel build",
        ]

        for cmd in setup_commands:
            exit_code, output = self.run_command_in_container(container, cmd)
            if exit_code != 0:
                self.logger.error(f"Setup command failed: {cmd}")
                self.logger.error(f"Output: {output}")
                return False

        self.logger.info("Python setup completed successfully")
        return True

    def run_command_in_container(
        self, container: Container, command: str, workdir: str = "/"
    ) -> tuple[int, str]:
        """Run command in container and return exit code and output."""
        self.logger.debug(f"Running command: {command}")

        try:
            result = container.exec_run(command, workdir=workdir)
            output = result.output.decode()

            if self.verbose:
                self.logger.debug(f"Command output: {output}")

            return result.exit_code, output

        except DockerException as e:
            self.logger.error(f"Failed to run command: {e}")
            return 1, str(e)

    def install_rxiv_maker_in_container(
        self,
        container: Container,
        wheel_path: Path | None = None,
        install_mode: str = "full",
        skip_system_deps: bool = False,
    ) -> tuple[int, str]:
        """Install rxiv-maker in container."""
        self.logger.info(
            f"Installing rxiv-maker (mode: {install_mode}, skip_system_deps: {skip_system_deps})"
        )

        # Set environment variables
        env_vars = []
        if install_mode != "full":
            env_vars.append(f"RXIV_INSTALL_MODE={install_mode}")
        if skip_system_deps:
            env_vars.append("RXIV_SKIP_SYSTEM_DEPS=1")

        # Determine installation command
        if wheel_path:
            # Copy wheel to container
            with open(wheel_path, "rb") as f:
                container.put_archive("/tmp", f.read())
            install_cmd = f"pip install /tmp/{wheel_path.name}"
        else:
            install_cmd = "pip install rxiv-maker"

        # Add environment variables
        if env_vars:
            env_str = " ".join(env_vars)
            install_cmd = f"{env_str} {install_cmd}"

        return self.run_command_in_container(container, install_cmd)

    def test_installation_in_container(self, container: Container) -> dict[str, bool]:
        """Test installation components in container."""
        self.logger.info("Testing installation components")

        tests = {
            "python": "python --version",
            "pip": "pip --version",
            "rxiv_cli": "rxiv --version",
            "rxiv_check": "rxiv check-installation --json",
        }

        results = {}
        for component, command in tests.items():
            exit_code, output = self.run_command_in_container(container, command)
            results[component] = exit_code == 0

            if self.verbose:
                self.logger.debug(
                    f"{component}: {'PASS' if results[component] else 'FAIL'}"
                )
                if not results[component]:
                    self.logger.debug(f"  Output: {output}")

        return results

    def run_integration_test(self, container: Container, manuscript_dir: Path) -> bool:
        """Run integration test with test manuscript."""
        self.logger.info("Running integration test")

        # Copy test manuscript to container
        manuscript_tar = self._create_tar_from_directory(manuscript_dir)
        container.put_archive("/tmp", manuscript_tar)

        # Run rxiv build
        exit_code, output = self.run_command_in_container(
            container, f"rxiv build /tmp/{manuscript_dir.name}", workdir="/tmp"
        )

        if exit_code == 0:
            self.logger.info("Integration test passed")
            return True
        else:
            self.logger.error(f"Integration test failed: {output}")
            return False

    def _create_tar_from_directory(self, directory: Path) -> bytes:
        """Create tar archive from directory."""
        import io
        import tarfile

        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            tar.add(directory, arcname=directory.name)

        tar_buffer.seek(0)
        return tar_buffer.read()

    def cleanup_container(self, container: Container):
        """Clean up container."""
        try:
            container.stop()
            self.logger.info(f"Stopped container: {container.id[:12]}")
        except DockerException:
            pass  # Container might already be stopped

    def cleanup_image(self, image_id: str):
        """Clean up Docker image."""
        try:
            self.client.images.remove(image_id)
            self.logger.info(f"Removed image: {image_id[:12]}")
        except DockerException:
            pass  # Image might be in use


def main():
    """Run installation tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Run rxiv-maker installation tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--mode",
        default="full",
        choices=["full", "minimal", "core"],
        help="Installation mode",
    )
    parser.add_argument(
        "--skip-system-deps", action="store_true", help="Skip system dependencies"
    )
    parser.add_argument("--wheel", type=Path, help="Path to wheel file for testing")

    args = parser.parse_args()

    runner = DockerTestRunner(verbose=args.verbose)

    try:
        # Create container
        container = runner.create_clean_ubuntu_container()

        # Set up Python
        if not runner.setup_python_in_container(container):
            sys.exit(1)

        # Install rxiv-maker
        exit_code, output = runner.install_rxiv_maker_in_container(
            container,
            wheel_path=args.wheel,
            install_mode=args.mode,
            skip_system_deps=args.skip_system_deps,
        )

        if exit_code != 0:
            print(f"Installation failed: {output}")
            sys.exit(1)

        # Test installation
        results = runner.test_installation_in_container(container)

        # Print results
        print("\\nInstallation Test Results:")
        print("=" * 40)
        for component, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"{component:20} {status}")

        # Overall result
        all_passed = all(results.values())
        print(f"\\nOverall: {'PASS' if all_passed else 'FAIL'}")

        if not all_passed:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    finally:
        try:
            runner.cleanup_container(container)
        except:
            pass


if __name__ == "__main__":
    main()
