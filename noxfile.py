"""Nox configuration for Rxiv-Maker testing."""

import nox


@nox.session(python=["3.11", "3.12", "3.13"])
def tests(session):
    """Run the test suite."""
    # Install dependencies with explicit versions to avoid conflicts
    session.install(".")
    session.install("pytest>=7.4,<8.0", "py>=1.11.0", "pytest-cov>=4.0")
    session.install("ruff>=0.8.0", "mypy>=1.0", "pytest-notebook>=0.10.0")
    session.install("lazydocs>=0.4.8", "nbstripout>=0.7.1", "pre-commit>=4.0.0")
    session.run(
        "pytest",
        "tests/",
        "-v",
        "--timeout=120",  # 2 minute timeout
        "-m",
        "not slow",  # Skip slow tests by default
    )


@nox.session(venv_backend="none")
def tests_current(session):
    """Run tests in current Python environment (no virtualenv)."""
    session.run("pytest", "tests/", "-v")


@nox.session(python="3.11")
def lint(session):
    """Run linting checks."""
    session.install(".")
    session.install("ruff>=0.8.0")
    session.run("ruff", "check", "src/")


@nox.session(python="3.11")
def type_check(session):
    """Run type checking."""
    session.install(".")
    session.install("mypy>=1.0", "types-PyYAML>=6.0.0")
    session.run("mypy", "src/")


@nox.session(python="3.11")
def format(session):
    """Format code with ruff."""
    session.install(".")
    session.install("ruff>=0.8.0")
    session.run("ruff", "format", "src/")


@nox.session(python="3.11")
def integration(session):
    """Run integration tests that generate actual PDFs."""
    session.install(".")
    session.install("pytest>=7.4,<8.0", "py>=1.11.0", "pytest-cov>=4.0")
    session.install("pytest-notebook>=0.10.0")
    session.run(
        "pytest",
        "tests/integration/",
        "-v",
        "-s",
        "--timeout=180",  # 3 minute timeout for integration tests
        "-m",
        "not slow",  # Skip slow integration tests
    )


@nox.session(python="3.11")
def coverage(session):
    """Run tests with coverage reporting."""
    session.install(".")
    session.install("pytest>=7.4,<8.0", "py>=1.11.0")
    session.install("coverage[toml]>=7.0", "pytest-cov>=4.0")
    session.install("pytest-notebook>=0.10.0")
    session.run(
        "pytest",
        "tests/",
        "--cov=src/rxiv_maker",  # Fixed coverage path
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v",
        "-m",
        "not slow",  # Skip slow tests for coverage
    )


@nox.session(python="3.11")
def install_tests(session):
    """Run essential installation tests."""
    session.install(".")
    session.install("pytest>=7.4,<8.0", "py>=1.11.0", "pytest-cov>=4.0")
    session.install("build>=0.10.0", "wheel>=0.40.0")

    # Run essential installation tests only
    session.run(
        "pytest",
        "tests/install/",
        "-v",
        "-s",
        "--tb=short",
        "--timeout=120",  # 2 minute timeout per test
        "-m",
        "not slow",  # Skip slow tests by default
        "-k",
        "not (performance or system_deps or resource_usage or docker or container)",  # Skip expensive tests and Docker tests
    )


@nox.session(python="3.11")
def install_tests_full(session):
    """Run complete installation tests including slow tests."""
    session.install(".")
    session.install("pytest>=7.4,<8.0", "py>=1.11.0", "pytest-cov>=4.0")
    session.install("build>=0.10.0", "wheel>=0.40.0")

    # Run all installation tests including slow ones
    session.run(
        "pytest",
        "tests/install/",
        "-v",
        "-s",
        "--tb=short",
        "--timeout=300",  # 5 minute timeout per test (reduced from 10)
        "--cov=src/rxiv_maker/install",
        "--cov-report=html:htmlcov/install",
        "--cov-report=term-missing",
        "-k",
        "not (docker or container)",  # Skip Docker tests
    )


@nox.session(python="3.11")
def install_tests_basic(session):
    """Run basic installation tests without Docker."""
    session.install(".")
    session.install("pytest>=7.4,<8.0", "py>=1.11.0")

    # Run only unit tests that don't require Docker
    session.run(
        "pytest",
        "tests/install/",
        "-v",
        "-k",
        "not docker and not container",
        "--tb=short",
        "--timeout=60",  # 1 minute timeout for basic tests
    )


@nox.session(python="3.11")
def install_tests_fast(session):
    """Run fast installation tests for CI."""
    session.install(".")
    session.install("pytest>=7.4,<8.0", "py>=1.11.0")
    session.install("build>=0.10.0", "wheel>=0.40.0")

    # Run only the most essential tests
    session.run(
        "pytest",
        "tests/install/test_basic_installation.py",
        "tests/install/test_dependency_installation.py",
        "-v",
        "-s",
        "--tb=short",
        "--timeout=90",  # 1.5 minute timeout for fast tests
    )
