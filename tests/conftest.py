"""Pytest configuration and fixtures for Rxiv-Maker tests."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest

# --- Helper Class for Engine Abstraction ---


class ExecutionEngine:
    """A helper class to abstract command execution."""

    def __init__(self, engine_type: str, container_id: str | None = None):
        self.engine_type = engine_type
        self.container_id = container_id
        print(
            f"\n✅ Engine initialized: type={self.engine_type}, container_id={self.container_id}"
        )

    def run(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
        """Runs a command in the selected engine."""
        # Extract check parameter, default to True
        check = kwargs.pop("check", True)

        # Common kwargs for all engines
        run_kwargs = {"text": True, "capture_output": True, "check": check, **kwargs}

        if self.engine_type == "local":
            return subprocess.run(command, **run_kwargs)

        # Assumes podman commands are compatible with docker for exec
        if self.engine_type in ["docker", "podman"]:
            # For containerized engines, handle cwd by using sh -c with cd
            if "cwd" in kwargs:
                cwd = kwargs.pop("cwd")
                # Properly quote command arguments for shell
                import shlex

                quoted_command = " ".join(shlex.quote(arg) for arg in command)
                # Use sh -c to change directory before executing command
                shell_command = f"cd {shlex.quote(cwd)} && {quoted_command}"
                base_command = [
                    self.engine_type,
                    "exec",
                    self.container_id,
                    "sh",
                    "-c",
                    shell_command,
                ]
                return subprocess.run(base_command, **run_kwargs)
            else:
                base_command = [self.engine_type, "exec", self.container_id]
                full_command = base_command + command
                return subprocess.run(full_command, **run_kwargs)

        raise ValueError(f"Unsupported engine type: {self.engine_type}")


# --- Pytest Hooks and Fixtures ---


def pytest_addoption(parser):
    """Adds the --engine command-line option to pytest."""
    parser.addoption(
        "--engine",
        action="store",
        default="local",
        help="Specify the execution engine: local, docker, podman",
    )


@pytest.fixture(scope="session")
def execution_engine(request):
    """
    A session-scoped fixture that sets up and tears down the
    specified execution engine (e.g., a Docker container).
    """
    engine_name = request.config.getoption("--engine")

    if engine_name == "local":
        yield ExecutionEngine("local")
        return

    # --- Containerized Engines (Docker, Podman, etc.) ---
    container_id = None
    try:
        if engine_name in ["docker", "podman"]:
            # Use the existing rxiv-maker base image from Docker Hub
            docker_image = "henriqueslab/rxiv-maker-base:latest"

            print(f"\n🐳 Pulling {engine_name} image: {docker_image}")
            subprocess.run([engine_name, "pull", docker_image], check=True)

            # Run the container in detached mode with workspace mounted
            result = subprocess.run(
                [
                    engine_name,
                    "run",
                    "-d",
                    "--rm",
                    "-v",
                    f"{Path.cwd()}:/workspace",
                    "-w",
                    "/workspace",
                    docker_image,
                    "sleep",
                    "infinity",
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            container_id = result.stdout.strip()
            print(f"\n🚀 Started {engine_name} container: {container_id[:12]}")

            # Install rxiv-maker in the container
            print("\n📦 Installing rxiv-maker in container...")
            subprocess.run(
                [
                    engine_name,
                    "exec",
                    container_id,
                    "pip",
                    "install",
                    "-e",
                    "/workspace",
                ],
                check=True,
            )

            yield ExecutionEngine(engine_name, container_id)
        else:
            pytest.fail(f"Unsupported engine: {engine_name}")

    finally:
        if container_id:
            print(f"\n🛑 Stopping {engine_name} container: {container_id[:12]}")
            subprocess.run(
                [engine_name, "stop", container_id], check=False, capture_output=True
            )


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """---
title: "Test Article"
authors:
  - name: "John Doe"
    affiliation: "Test University"
    email: "john@test.com"
keywords: ["test", "article"]
---

# Introduction

This is a test article with **bold** and *italic* text.

## Methods

We used @testcitation2023 for our methodology.

## Results

See @fig:test for results.

![Test Figure](FIGURES/test.png){#fig:test width="0.8"}
"""


@pytest.fixture
def sample_yaml_metadata():
    """Sample YAML metadata for testing."""
    return {
        "title": "Test Article",
        "authors": [
            {
                "name": "John Doe",
                "affiliation": "Test University",
                "email": "john@test.com",
            }
        ],
        "keywords": ["test", "article"],
    }


@pytest.fixture
def sample_tex_template():
    """Sample LaTeX template for testing."""
    return """\\documentclass{article}
\\title{<PY-RPL:LONG-TITLE-STR>}
\\author{<PY-RPL:AUTHORS-AND-AFFILIATIONS>}
\\begin{document}
\\maketitle
\\begin{abstract}
<PY-RPL:ABSTRACT>
\\end{abstract}
<PY-RPL:MAIN-CONTENT>
\\end{document}
"""


def check_latex_available():
    """Check if LaTeX is available in the system."""
    try:
        result = subprocess.run(
            ["pdflatex", "--version"], capture_output=True, text=True
        )
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def check_r_available():
    """Check if R is available in the system."""
    try:
        result = subprocess.run(["R", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


# Markers for conditional test execution
requires_latex = pytest.mark.skipif(
    not check_latex_available(), reason="LaTeX not available"
)

requires_r = pytest.mark.skipif(not check_r_available(), reason="R not available")
