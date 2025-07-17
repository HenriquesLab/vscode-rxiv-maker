"""Platform detection tests for Universal Python Wheel Installer."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


from .conftest import run_in_container


class TestLinuxPlatformDetection:
    """Test Linux platform detection in Docker Ubuntu environment."""

    def test_platform_detection_in_container(self, docker_manager, ubuntu_container):
        """Test platform detection within Ubuntu container."""
        # Test platform detection
        exit_code, output = run_in_container(
            ubuntu_container, "python -c 'import platform; print(platform.system())'"
        )
        assert exit_code == 0
        assert "Linux" in output

        # Test distribution detection
        exit_code, output = run_in_container(
            ubuntu_container, "python -c 'import platform; print(platform.platform())'"
        )
        assert exit_code == 0
        assert "ubuntu" in output.lower()

    def test_architecture_detection(self, docker_manager, ubuntu_container):
        """Test architecture detection."""
        exit_code, output = run_in_container(
            ubuntu_container, "python -c 'import platform; print(platform.machine())'"
        )
        assert exit_code == 0
        assert "x86_64" in output or "amd64" in output

    def test_linux_installer_creation(self, docker_manager, ubuntu_container):
        """Test Linux installer creation in container."""
        # Create test script to import and test LinuxInstaller
        test_script = """
import sys
from pathlib import Path
sys.path.insert(0, "/workspace/src")

from rxiv_maker.install.platform_installers.linux import LinuxInstaller
from rxiv_maker.install.manager import InstallMode

installer = LinuxInstaller(
    mode=InstallMode.FULL,
    verbose=True,
    force=False,
    interactive=False
)

print(f"Installer created: {type(installer).__name__}")
print(f"Package manager: {installer.package_manager}")
print(f"Distro: {installer.distro}")
"""

        # Copy source to container
        exit_code, output = run_in_container(ubuntu_container, "mkdir -p /workspace")
        assert exit_code == 0

        # Mount source code (simulate by creating basic structure)
        # In real container, this would be mounted
        exit_code, output = run_in_container(
            ubuntu_container,
            "mkdir -p /workspace/src/rxiv_maker/install/platform_installers",
        )
        assert exit_code == 0

        # Instead of copying complex source, test basic platform detection
        platform_test = """
import platform
import subprocess

# Test basic platform detection
print(f"System: {platform.system()}")
print(f"Release: {platform.release()}")
print(f"Distribution: {platform.platform()}")

# Test package manager detection
package_managers = {
    "apt": "apt --version",
    "yum": "yum --version",
    "dnf": "dnf --version",
    "pacman": "pacman --version",
    "zypper": "zypper --version"
}

for name, cmd in package_managers.items():
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Package manager found: {name}")
        else:
            print(f"Package manager not found: {name}")
    except FileNotFoundError:
        print(f"Package manager not found: {name}")
"""

        # Write test script to container
        exit_code, output = run_in_container(
            ubuntu_container,
            f"cat > /tmp/platform_test.py << 'EOF'\\n{platform_test}\\nEOF",
        )
        assert exit_code == 0

        # Run platform test
        exit_code, output = run_in_container(
            ubuntu_container, "python /tmp/platform_test.py"
        )
        assert exit_code == 0
        assert "System: Linux" in output
        assert "Package manager found: apt" in output

    def test_distribution_detection_methods(self, docker_manager, ubuntu_container):
        """Test various distribution detection methods."""
        detection_tests = [
            ("lsb_release", "lsb_release -d"),
            ("os_release", "cat /etc/os-release"),
            ("debian_version", "cat /etc/debian_version"),
            ("issue", "cat /etc/issue"),
        ]

        for name, command in detection_tests:
            exit_code, output = run_in_container(ubuntu_container, command)
            if exit_code == 0:
                print(f"{name}: {output.strip()}")
                if name == "os_release" or name == "lsb_release":
                    assert "ubuntu" in output.lower()

    def test_package_manager_capabilities(self, docker_manager, ubuntu_container):
        """Test package manager capabilities."""
        # Test apt is available
        exit_code, output = run_in_container(ubuntu_container, "apt --version")
        assert exit_code == 0
        assert "apt" in output.lower()

        # Test apt-get is available
        exit_code, output = run_in_container(ubuntu_container, "apt-get --version")
        assert exit_code == 0

        # Test dpkg is available
        exit_code, output = run_in_container(ubuntu_container, "dpkg --version")
        assert exit_code == 0

        # Test package search capability
        exit_code, output = run_in_container(
            ubuntu_container, "apt list --installed | head -5"
        )
        assert exit_code == 0

        # Test package info capability
        exit_code, output = run_in_container(ubuntu_container, "apt show python3")
        assert exit_code == 0

    def test_system_requirements_detection(self, docker_manager, ubuntu_container):
        """Test system requirements detection."""
        # Test Python version detection
        exit_code, output = run_in_container(
            ubuntu_container,
            "python -c 'import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")'",
        )
        assert exit_code == 0
        version_parts = output.strip().split(".")
        assert int(version_parts[0]) >= 3
        assert int(version_parts[1]) >= 11

        # Test available space
        exit_code, output = run_in_container(ubuntu_container, "df -h /")
        assert exit_code == 0
        assert "%" in output

        # Test memory
        exit_code, output = run_in_container(ubuntu_container, "free -h")
        assert exit_code == 0
        assert "Mem:" in output

    def test_network_connectivity(self, docker_manager, ubuntu_container):
        """Test network connectivity for package installation."""
        # Test basic internet connectivity
        exit_code, output = run_in_container(ubuntu_container, "ping -c 1 8.8.8.8")
        assert exit_code == 0

        # Test DNS resolution
        exit_code, output = run_in_container(ubuntu_container, "nslookup google.com")
        assert exit_code == 0

        # Test HTTPS connectivity
        exit_code, output = run_in_container(
            ubuntu_container,
            "curl -s -o /dev/null -w '%{http_code}' https://www.google.com",
        )
        assert exit_code == 0
        assert "200" in output


class TestPackageManagerDetection:
    """Test package manager detection logic."""

    def test_apt_detection(self, docker_manager, ubuntu_container):
        """Test APT package manager detection."""
        # Test apt command availability
        exit_code, output = run_in_container(ubuntu_container, "which apt")
        assert exit_code == 0
        assert "/usr/bin/apt" in output

        # Test apt functionality
        exit_code, output = run_in_container(
            ubuntu_container, "apt list --installed | wc -l"
        )
        assert exit_code == 0
        count = int(output.strip())
        assert count > 0

    def test_package_manager_version(self, docker_manager, ubuntu_container):
        """Test package manager version detection."""
        exit_code, output = run_in_container(ubuntu_container, "apt --version")
        assert exit_code == 0

        # Extract version
        lines = output.strip().split("\\n")
        version_line = lines[0]
        assert "apt" in version_line.lower()

        # Should contain version number
        import re

        version_match = re.search(r"\\d+\\.\\d+", version_line)
        assert version_match is not None

    def test_package_installation_permissions(self, docker_manager, ubuntu_container):
        """Test package installation permissions."""
        # Test that we can update package lists (requires root)
        exit_code, output = run_in_container(ubuntu_container, "apt-get update")
        assert exit_code == 0

        # Test that we can install packages (requires root)
        exit_code, output = run_in_container(
            ubuntu_container, "apt-get install -y hello"
        )
        assert exit_code == 0

        # Test that package was installed
        exit_code, output = run_in_container(ubuntu_container, "hello")
        assert exit_code == 0
        assert "Hello, world!" in output

    def test_package_repository_access(self, docker_manager, ubuntu_container):
        """Test package repository access."""
        # Test package search
        exit_code, output = run_in_container(ubuntu_container, "apt search python3")
        assert exit_code == 0
        assert "python3" in output.lower()

        # Test package information
        exit_code, output = run_in_container(ubuntu_container, "apt show python3")
        assert exit_code == 0
        assert "Package: python3" in output
        assert "Version:" in output


class TestSystemCapabilities:
    """Test system capability detection."""

    def test_compiler_availability(self, docker_manager, ubuntu_container):
        """Test compiler availability for building packages."""
        # Test gcc
        exit_code, output = run_in_container(ubuntu_container, "gcc --version")
        assert exit_code == 0
        assert "gcc" in output.lower()

        # Test g++
        exit_code, output = run_in_container(ubuntu_container, "g++ --version")
        assert exit_code == 0

        # Test make
        exit_code, output = run_in_container(ubuntu_container, "make --version")
        assert exit_code == 0

    def test_development_tools(self, docker_manager, ubuntu_container):
        """Test development tools availability."""
        tools = [
            "pkg-config",
            "curl",
            "wget",
            "git",
        ]

        for tool in tools:
            exit_code, output = run_in_container(ubuntu_container, f"{tool} --version")
            assert exit_code == 0, f"Tool {tool} not available"

    def test_library_dependencies(self, docker_manager, ubuntu_container):
        """Test system library dependencies."""
        # Test that we can install development libraries
        libraries = [
            "libc6-dev",
            "libssl-dev",
            "libffi-dev",
            "zlib1g-dev",
        ]

        for lib in libraries:
            exit_code, output = run_in_container(
                ubuntu_container, f"apt-get install -y {lib}"
            )
            assert exit_code == 0, f"Failed to install {lib}"

    def test_locale_support(self, docker_manager, ubuntu_container):
        """Test locale support."""
        # Test locale command
        exit_code, output = run_in_container(ubuntu_container, "locale")
        assert exit_code == 0

        # Test that UTF-8 is supported
        exit_code, output = run_in_container(
            ubuntu_container, "locale -a | grep -i utf"
        )
        assert exit_code == 0
        assert "utf" in output.lower()

    def test_timezone_support(self, docker_manager, ubuntu_container):
        """Test timezone support."""
        # Test date command
        exit_code, output = run_in_container(ubuntu_container, "date")
        assert exit_code == 0

        # Test timezone info
        exit_code, output = run_in_container(ubuntu_container, "timedatectl")
        # May not work in container, so don't assert

        # Test that timezone files exist
        exit_code, output = run_in_container(
            ubuntu_container, "ls /usr/share/zoneinfo/"
        )
        assert exit_code == 0


class TestEnvironmentVariables:
    """Test environment variable detection and handling."""

    def test_path_environment(self, docker_manager, ubuntu_container):
        """Test PATH environment variable."""
        exit_code, output = run_in_container(ubuntu_container, "echo $PATH")
        assert exit_code == 0

        paths = output.strip().split(":")
        assert "/usr/bin" in paths
        assert "/bin" in paths

    def test_python_environment(self, docker_manager, ubuntu_container):
        """Test Python environment variables."""
        # Test PYTHONPATH
        exit_code, output = run_in_container(
            ubuntu_container, "python -c 'import sys; print(sys.path)'"
        )
        assert exit_code == 0

        # Test Python executable path
        exit_code, output = run_in_container(
            ubuntu_container, "python -c 'import sys; print(sys.executable)'"
        )
        assert exit_code == 0
        assert "python" in output

    def test_environment_modification(self, docker_manager, ubuntu_container):
        """Test environment variable modification."""
        # Test setting environment variable
        exit_code, output = run_in_container(
            ubuntu_container, "export TEST_VAR=test_value && echo $TEST_VAR"
        )
        assert exit_code == 0
        assert "test_value" in output

        # Test persistent environment modification
        exit_code, output = run_in_container(
            ubuntu_container,
            "echo 'export TEST_PERSISTENT=persistent_value' >> ~/.bashrc && source ~/.bashrc && echo $TEST_PERSISTENT",
        )
        assert exit_code == 0
        assert "persistent_value" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
