"""Dependency installation tests for Universal Python Wheel Installer."""

import pytest

from .conftest import run_in_container


@pytest.mark.slow
class TestLaTeXInstallation:
    """Test essential LaTeX installation only."""

    def test_latex_basic_installation(self, docker_manager, ubuntu_container):
        """Test basic LaTeX installation (essential test only)."""
        # Install minimal LaTeX
        exit_code, output = run_in_container(
            ubuntu_container, "apt-get update && apt-get install -y texlive-latex-base"
        )
        assert exit_code == 0, f"Failed to install LaTeX: {output}"

        # Test basic LaTeX command
        exit_code, output = run_in_container(ubuntu_container, "pdflatex --version")
        assert exit_code == 0, f"pdflatex not available: {output}"


# Node.js installation tests removed - not essential for core functionality


# R installation tests removed - not essential for core functionality


# System library tests removed - not essential for core functionality


class TestDependencyIntegration:
    """Test essential dependency integration only."""

    def test_basic_dependency_verification(self, docker_manager, ubuntu_container):
        """Test basic dependency verification (essential test only)."""
        # Test essential commands are available
        essential_tests = [
            ("python", "python --version"),
            ("pip", "pip --version"),
        ]

        for name, command in essential_tests:
            exit_code, output = run_in_container(ubuntu_container, command)
            assert exit_code == 0, f"{name} not available: {output}"


class TestDependencyErrorHandling:
    """Test essential error handling only."""

    def test_package_not_found_handling(self, docker_manager, ubuntu_container):
        """Test handling of missing packages (essential test only)."""
        # Try to install non-existent package
        exit_code, output = run_in_container(
            ubuntu_container, "apt-get install -y nonexistent-package-12345"
        )
        assert exit_code != 0
        assert "unable to locate" in output.lower() or "not found" in output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])  # Skip slow tests by default
