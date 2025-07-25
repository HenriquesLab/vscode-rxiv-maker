"""Nox configuration for Rxiv-Maker testing."""

import os
import subprocess

import nox


def _check_docker_available():
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _install_test_deps(session, include_build=False, include_coverage=False):
    """Install common test dependencies."""
    session.install(".")
    session.install("pytest>=7.4,<8.0", "py>=1.11.0", "pytest-timeout>=2.4.0")

    if include_build:
        session.install("build>=0.10.0", "wheel>=0.40.0")

    if include_coverage:
        session.install("pytest-cov>=4.0", "coverage[toml]>=7.0")


def _setup_engine(session, engine):
    """Setup engine environment and check availability."""
    if engine == "docker" and not _check_docker_available():
        session.skip(
            "Docker is not available. Install Docker to run docker engine tests."
        )
    session.env["RXIV_ENGINE"] = engine.upper()


@nox.session(python=["3.11", "3.12", "3.13"])
@nox.parametrize("engine", ["local", "docker"])
def tests(session, engine):
    """Run the test suite with specified engine (local or docker)."""
    _setup_engine(session, engine)
    _install_test_deps(session)

    session.install("pytest-xdist>=3.8.0", "pytest-notebook>=0.10.0")

    session.run(
        "pytest",
        "tests/",
        "-v",
        "--timeout=120",
        "-m",
        "not slow",
    )


@nox.session(python="3.11")
@nox.parametrize("engine", ["local", "docker"])
def integration(session, engine):
    """Run integration tests with specified engine (local or docker)."""
    _setup_engine(session, engine)
    _install_test_deps(session)

    session.install("pytest-notebook>=0.10.0")

    session.run(
        "pytest",
        "tests/integration/",
        "-v",
        "-s",
        "--timeout=180",
        "-m",
        "not slow",
    )


@nox.session(python="3.11")
@nox.parametrize("engine", ["local", "docker"])
@nox.parametrize("test_type", ["basic", "full"])
def install_tests(session, engine, test_type):
    """Run installation tests with specified engine and scope."""
    _setup_engine(session, engine)
    _install_test_deps(
        session, include_build=True, include_coverage=(test_type == "full")
    )

    # Configure test filters based on engine and test type
    filters = []
    if engine == "local":
        filters.append("not (docker or container)")

    if test_type == "basic":
        filters.extend(
            ["not (performance or system_deps or resource_usage)", "not slow"]
        )
        timeout = 120
    else:  # full
        timeout = 300

    args = [
        "pytest",
        "tests/install/",
        "-v",
        "-s",
        "--tb=short",
        f"--timeout={timeout}",
    ]

    if test_type == "full":
        args.extend(
            [
                "--cov=src/rxiv_maker/install",
                "--cov-report=html:htmlcov/install",
                "--cov-report=term-missing",
            ]
        )

    if filters:
        args.extend(["-k", " and ".join(filters)])

    session.run(*args)


@nox.session(python="3.11")
@nox.parametrize("engine", ["local", "docker"])
def coverage(session, engine):
    """Run tests with coverage reporting using specified engine."""
    _setup_engine(session, engine)
    _install_test_deps(session, include_coverage=True)

    session.install("pytest-notebook>=0.10.0")

    session.run(
        "pytest",
        "tests/",
        "--cov=src/rxiv_maker",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v",
        "-m",
        "not slow",
    )


@nox.session(python="3.11")
def docker_e2e(session):
    """Run end-to-end Docker tests including real manuscript generation."""
    if not _check_docker_available():
        session.skip("Docker is not available.")

    _install_test_deps(session)
    session.install("pytest-xdist>=3.8.0")
    session.env["RXIV_ENGINE"] = "DOCKER"

    # Run Docker-specific unit tests
    session.run(
        "pytest",
        "tests/unit/test_figure_generator.py",
        "tests/cli/test_build.py",
        "tests/cli/test_config.py",
        "-v",
        "-s",
        "--tb=short",
        "--timeout=300",
        "-k",
        "docker or engine",
    )

    # Run real Docker integration test if EXAMPLE_MANUSCRIPT exists
    if os.path.exists("EXAMPLE_MANUSCRIPT"):
        session.log("Running Docker E2E test with EXAMPLE_MANUSCRIPT")
        session.run(
            "python",
            "-m",
            "rxiv_maker.cli.main",
            "--engine",
            "docker",
            "pdf",
            "EXAMPLE_MANUSCRIPT/",
            external=False,
        )
    else:
        session.log("EXAMPLE_MANUSCRIPT not found, skipping E2E test")


@nox.session(venv_backend="none")
def tests_current(session):
    """Run tests in current Python environment (no virtualenv)."""
    session.run("pytest", "tests/", "-v")


@nox.session(python="3.11")
def lint(session):
    """Run linting checks."""
    session.install(".", "ruff>=0.8.0")
    session.run("ruff", "check", "src/")


@nox.session(python="3.11")
def format(session):
    """Format code with ruff."""
    session.install(".", "ruff>=0.8.0")
    session.run("ruff", "format", "src/")


@nox.session(python="3.11")
def type_check(session):
    """Run type checking."""
    session.install(".", "mypy>=1.0", "types-PyYAML>=6.0.0")
    session.run("mypy", "src/")


@nox.session(python="3.11")
def ci_fast(session):
    """Fast CI tests for quick feedback."""
    _install_test_deps(session, include_build=True)

    # Run only the most essential tests
    session.run(
        "pytest",
        "tests/install/test_basic_installation.py",
        "tests/install/test_dependency_installation.py",
        "-v",
        "-s",
        "--tb=short",
        "--timeout=90",
    )
