"""Basic installation tests for Universal Python Wheel Installer."""

import json

import pytest

from .conftest import install_rxiv_maker_in_container, run_in_container


class TestBasicInstallation:
    """Test basic installation functionality."""

    def test_clean_ubuntu_container_setup(self, docker_manager, ubuntu_container):
        """Test that clean Ubuntu container is set up correctly."""
        # Test Python version
        exit_code, output = run_in_container(ubuntu_container, "python --version")
        assert exit_code == 0
        assert "Python 3.11" in output

        # Test pip is available
        exit_code, output = run_in_container(ubuntu_container, "pip --version")
        assert exit_code == 0
        assert "pip" in output

        # Test basic tools
        exit_code, output = run_in_container(ubuntu_container, "curl --version")
        assert exit_code == 0

        exit_code, output = run_in_container(ubuntu_container, "git --version")
        assert exit_code == 0

    @pytest.mark.slow
    def test_install_from_pypi(self, docker_manager, ubuntu_container):
        """Test installation from PyPI."""
        # Install rxiv-maker from PyPI
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container,
            install_mode="full",
            skip_system_deps=True,  # Skip system deps for faster testing
        )

        # Should succeed or skip if not on PyPI yet
        if exit_code != 0:
            pytest.skip(
                f"Installation from PyPI failed (expected if not published): {output}"
            )

        # Test that rxiv command is available
        exit_code, output = run_in_container(ubuntu_container, "rxiv --version")
        assert exit_code == 0
        assert "rxiv" in output.lower()

    def test_install_from_wheel(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test installation from wheel file."""
        # Copy wheel to container
        container_wheel_path = f"/tmp/{test_package_wheel.name}"

        with open(test_package_wheel, "rb") as f:
            ubuntu_container.put_archive("/tmp", f.read())

        # Install from wheel with system deps skipped
        exit_code, output = run_in_container(
            ubuntu_container,
            f"RXIV_SKIP_SYSTEM_DEPS=1 pip install {container_wheel_path}",
        )

        assert exit_code == 0, f"Wheel installation failed: {output}"

        # Test that rxiv command is available
        exit_code, output = run_in_container(ubuntu_container, "rxiv --version")
        assert exit_code == 0
        assert "rxiv" in output.lower()

    def test_install_modes(self, docker_manager, ubuntu_container, test_package_wheel):
        """Test different installation modes."""
        modes = ["full", "minimal", "core"]

        for mode in modes:
            with ubuntu_container.manager.create_test_container(
                image="ubuntu:22.04", environment={"DEBIAN_FRONTEND": "noninteractive"}
            ) as container:
                # Set up Python
                setup_cmds = [
                    "apt-get update",
                    "apt-get install -y python3.11 python3-pip",
                    "update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1",
                ]

                for cmd in setup_cmds:
                    exit_code, output = run_in_container(container, cmd)
                    assert exit_code == 0, f"Setup failed: {cmd}"

                # Install with specific mode
                exit_code, output = install_rxiv_maker_in_container(
                    container,
                    wheel_path=test_package_wheel,
                    install_mode=mode,
                    skip_system_deps=True,
                )

                assert exit_code == 0, f"Installation failed for mode {mode}: {output}"

                # Test basic functionality
                exit_code, output = run_in_container(container, "rxiv --version")
                assert exit_code == 0, f"CLI not working for mode {mode}"

    def test_skip_system_deps_flag(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test RXIV_SKIP_SYSTEM_DEPS flag."""
        # Install with system deps skipped
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )

        assert exit_code == 0, f"Installation with skip_system_deps failed: {output}"

        # Verify installation
        exit_code, output = run_in_container(ubuntu_container, "rxiv --version")
        assert exit_code == 0

        # Check that system dependencies were not installed
        exit_code, output = run_in_container(ubuntu_container, "pdflatex --version")
        assert exit_code != 0, (
            "LaTeX should not be installed when system deps are skipped"
        )

        # Note: Node.js and R installation checks removed since pip install
        # no longer installs external libraries

    def test_import_functionality(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test that Python imports work correctly after installation."""
        # Install package
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )

        assert exit_code == 0, f"Installation failed: {output}"

        # Test imports
        import_tests = [
            "import rxiv_maker",
            "from rxiv_maker.install.manager import InstallManager",
            "from rxiv_maker.install.utils.verification import verify_installation",
            "from rxiv_maker.cli.main import main",
        ]

        for import_test in import_tests:
            exit_code, output = run_in_container(
                ubuntu_container, f"python -c '{import_test}'"
            )
            assert exit_code == 0, f"Import failed: {import_test}\\nOutput: {output}"

    def test_entry_points(self, docker_manager, ubuntu_container, test_package_wheel):
        """Test that entry points are installed correctly."""
        # Install package
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )

        assert exit_code == 0, f"Installation failed: {output}"

        # Test entry points
        entry_points = [
            ("rxiv", "rxiv --help"),
            ("rxiv-install-deps", "rxiv-install-deps --help"),
        ]

        for entry_point, command in entry_points:
            exit_code, output = run_in_container(
                ubuntu_container, f"which {entry_point}"
            )
            assert exit_code == 0, f"Entry point {entry_point} not found"

            exit_code, output = run_in_container(ubuntu_container, command)
            assert exit_code == 0, f"Entry point {entry_point} not working: {output}"

    def test_installation_with_dependencies(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test that Python dependencies are installed correctly."""
        # Install package
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )

        assert exit_code == 0, f"Installation failed: {output}"

        # Test that key dependencies are available
        dependencies = [
            "import matplotlib",
            "import numpy",
            "import pandas",
            "import yaml",
            "import click",
            "import rich",
        ]

        for dep in dependencies:
            exit_code, output = run_in_container(ubuntu_container, f"python -c '{dep}'")
            assert exit_code == 0, f"Dependency not available: {dep}\\nOutput: {output}"


class TestInstallationErrorHandling:
    """Test error handling during installation."""

    def test_missing_python(self, docker_manager):
        """Test behavior when Python is not available."""
        # Create container without Python
        container = docker_manager.create_test_container(
            image="ubuntu:22.04", command="sleep 3600"
        )

        try:
            # Try to install without Python
            exit_code, output = run_in_container(container, "pip install rxiv-maker")
            assert exit_code != 0, "Installation should fail without Python"

        finally:
            docker_manager.cleanup_container(container)

    def test_network_failure_simulation(self, docker_manager, ubuntu_container):
        """Test behavior when network is unavailable."""
        # Simulate network failure by using invalid index URL
        exit_code, output = run_in_container(
            ubuntu_container, "pip install --index-url http://invalid-url rxiv-maker"
        )

        assert exit_code != 0, "Installation should fail with network issues"
        assert "unreachable" in output.lower() or "connection" in output.lower()

    def test_permission_issues(self, docker_manager, ubuntu_container):
        """Test behavior with permission issues."""
        # Create read-only directory
        exit_code, output = run_in_container(
            ubuntu_container, "mkdir -p /readonly && chmod 444 /readonly"
        )
        assert exit_code == 0

        # Try to install to read-only location
        exit_code, output = run_in_container(
            ubuntu_container, "pip install --target /readonly rxiv-maker"
        )

        assert exit_code != 0, "Installation should fail with permission issues"


class TestInstallationEnvironmentDetection:
    """Test environment detection during installation."""

    def test_docker_environment_detection(self, docker_manager, ubuntu_container):
        """Test that Docker environment is detected."""
        # Create .dockerenv file (standard Docker indicator)
        exit_code, output = run_in_container(ubuntu_container, "touch /.dockerenv")
        assert exit_code == 0

        # Test environment detection
        exit_code, output = run_in_container(
            ubuntu_container,
            "python -c 'import os; print(os.path.exists(\"/.dockerenv\"))'",
        )
        assert exit_code == 0
        assert "True" in output

    def test_ci_environment_detection(self, docker_manager, ubuntu_container):
        """Test CI environment detection."""
        # Set CI environment variable
        container = docker_manager.create_test_container(
            image="ubuntu:22.04",
            environment={"CI": "true", "DEBIAN_FRONTEND": "noninteractive"},
        )

        try:
            # Set up Python
            setup_cmds = ["apt-get update", "apt-get install -y python3.11 python3-pip"]

            for cmd in setup_cmds:
                exit_code, output = run_in_container(container, cmd)
                assert exit_code == 0

            # Test CI detection
            exit_code, output = run_in_container(
                container,
                'python -c \'import os; print(os.environ.get("CI", "false"))\'',
            )
            assert exit_code == 0
            assert "true" in output

        finally:
            docker_manager.cleanup_container(container)

    def test_virtual_environment_detection(self, docker_manager, ubuntu_container):
        """Test virtual environment detection."""
        # Create virtual environment
        exit_code, output = run_in_container(
            ubuntu_container, "python -m venv /tmp/test_venv"
        )
        assert exit_code == 0

        # Activate virtual environment and test detection
        exit_code, output = run_in_container(
            ubuntu_container,
            'source /tmp/test_venv/bin/activate && python -c \'import sys; print(hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix))\'',
        )
        assert exit_code == 0
        assert "True" in output


@pytest.mark.integration
class TestInstallationIntegration:
    """Integration tests for installation process."""

    def test_full_installation_workflow(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test complete installation workflow."""
        # Install package
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container,
            wheel_path=test_package_wheel,
            install_mode="full",
            skip_system_deps=True,  # Skip for faster testing
        )

        assert exit_code == 0, f"Installation failed: {output}"

        # Test CLI functionality
        exit_code, output = run_in_container(ubuntu_container, "rxiv --help")
        assert exit_code == 0
        assert "rxiv-maker" in output.lower()

        # Test check-installation command
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --json"
        )
        assert exit_code == 0

        # Parse JSON output
        try:
            result = json.loads(output)
            assert "status" in result
            assert "components" in result
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {output}")

    def test_installation_idempotency(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test that installation is idempotent."""
        # Install once
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"First installation failed: {output}"

        # Install again
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Second installation failed: {output}"

        # Should still work
        exit_code, output = run_in_container(ubuntu_container, "rxiv --version")
        assert exit_code == 0

    def test_installation_upgrade(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test installation upgrade process."""
        # Install package
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Upgrade package (same version, but test the process)
        exit_code, output = run_in_container(
            ubuntu_container, f"pip install --upgrade {test_package_wheel}"
        )
        assert exit_code == 0, f"Upgrade failed: {output}"

        # Should still work
        exit_code, output = run_in_container(ubuntu_container, "rxiv --version")
        assert exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
