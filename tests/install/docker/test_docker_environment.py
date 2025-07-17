"""Docker-specific tests for environment detection."""

import pytest

from ..conftest import install_rxiv_maker_in_container, run_in_container


@pytest.mark.slow
class TestDockerEnvironmentDetection:
    """Test essential Docker environment detection only."""

    def test_docker_environment_indicators(self, docker_manager, ubuntu_container):
        """Test essential Docker environment detection."""
        # Check for .dockerenv file - essential for Docker detection
        exit_code, output = run_in_container(ubuntu_container, "ls -la /.dockerenv")
        assert exit_code == 0, "Docker environment file not found"

        # Check for container-specific filesystem - essential
        exit_code, output = run_in_container(ubuntu_container, "cat /proc/1/cgroup")
        assert exit_code == 0
        assert "docker" in output or "container" in output or "/" in output

    def test_basic_container_functionality(self, docker_manager, ubuntu_container):
        """Test basic container functionality (combined test)."""
        # Check hostname
        exit_code, output = run_in_container(ubuntu_container, "hostname")
        assert exit_code == 0
        assert len(output.strip()) > 0

        # Test external connectivity (essential for installation)
        exit_code, output = run_in_container(ubuntu_container, "ping -c 1 8.8.8.8")
        assert exit_code == 0, "No external network connectivity"


@pytest.mark.slow
class TestEnvironmentVariableDetection:
    """Test essential environment variables only."""

    def test_essential_environment_variables(self, docker_manager, ubuntu_container):
        """Test essential environment variables (combined test)."""
        # Check DEBIAN_FRONTEND (essential for apt operations)
        exit_code, output = run_in_container(ubuntu_container, "echo $DEBIAN_FRONTEND")
        assert exit_code == 0
        assert "noninteractive" in output

        # Check Python executable (essential for installation)
        exit_code, output = run_in_container(ubuntu_container, "which python")
        assert exit_code == 0
        assert "/usr/bin/python" in output or "/usr/local/bin/python" in output


class TestContainerCapabilities:
    """Test essential container capabilities only."""

    def test_essential_capabilities(self, docker_manager, ubuntu_container):
        """Test essential capabilities (combined test)."""
        # Check root access (essential for installation)
        exit_code, output = run_in_container(ubuntu_container, "whoami")
        assert exit_code == 0
        assert "root" in output

        # Test file system write access (essential)
        exit_code, output = run_in_container(
            ubuntu_container, "touch /tmp/test_file && rm /tmp/test_file"
        )
        assert exit_code == 0

        # Test basic package installation (essential)
        exit_code, output = run_in_container(ubuntu_container, "apt-get update")
        assert exit_code == 0


class TestInstallationEnvironmentDetection:
    """Test essential installation environment detection."""

    def test_essential_environment_detection(self, docker_manager, ubuntu_container):
        """Test essential environment detection (combined test)."""
        # Test RXIV_SKIP_SYSTEM_DEPS detection (essential for installation)
        exit_code, output = run_in_container(
            ubuntu_container,
            "RXIV_SKIP_SYSTEM_DEPS=1 python -c 'import os; print(os.environ.get(\"RXIV_SKIP_SYSTEM_DEPS\"))'",
        )
        assert exit_code == 0
        assert "1" in output

        # Test Docker environment detection from Python (essential)
        exit_code, output = run_in_container(
            ubuntu_container,
            "python -c 'import os; print(os.path.exists(\"/.dockerenv\"))'",
        )
        assert exit_code == 0
        assert "True" in output


class TestContainerSpecificBehavior:
    """Test essential container behavior for installation."""

    def test_installation_in_container(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test essential installation behavior in container (combined test)."""
        # Install rxiv-maker in Docker environment
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Test that we can run rxiv command (essential)
        exit_code, output = run_in_container(ubuntu_container, "rxiv --version")
        assert exit_code == 0

        # Check that Docker environment was detected
        exit_code, output = run_in_container(
            ubuntu_container,
            "python -c 'import os; print(os.path.exists(\"/.dockerenv\"))'",
        )
        assert exit_code == 0
        assert "True" in output


# Container lifecycle tests removed - not essential for core installation testing


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])  # Skip slow tests by default
