"""CLI integration tests for check-installation command."""

import json

import pytest

from ..conftest import install_rxiv_maker_in_container, run_in_container


class TestCheckInstallationCommand:
    """Test the rxiv check-installation command."""

    def test_check_installation_basic(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test basic check-installation command."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation"
        )
        assert exit_code == 0, f"check-installation failed: {output}"

        # Should contain status information
        assert "installation" in output.lower()
        assert "components" in output.lower() or "status" in output.lower()

    def test_check_installation_json_output(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation with JSON output."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation with JSON output
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --json"
        )
        assert exit_code == 0, f"check-installation --json failed: {output}"

        # Parse JSON output
        try:
            result = json.loads(output)
            assert "status" in result
            assert "components" in result
            assert "summary" in result

            # Check summary structure
            summary = result["summary"]
            assert "total" in summary
            assert "installed" in summary
            assert "missing" in summary
            assert isinstance(summary["total"], int)
            assert isinstance(summary["installed"], int)
            assert isinstance(summary["missing"], int)

        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {output}")

    def test_check_installation_detailed(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation with detailed output."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation with detailed output
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --detailed"
        )
        assert exit_code == 0, f"check-installation --detailed failed: {output}"

        # Should contain detailed information
        assert "python" in output.lower()
        assert "version" in output.lower() or "path" in output.lower()

    def test_check_installation_help(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation help output."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation help
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --help"
        )
        assert exit_code == 0, f"check-installation --help failed: {output}"

        # Should contain help information
        assert "usage" in output.lower() or "help" in output.lower()
        assert "--detailed" in output
        assert "--json" in output
        assert "--fix" in output

    def test_check_installation_with_missing_deps(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation when dependencies are missing."""
        # Install rxiv-maker with system deps skipped
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation"
        )
        # Should succeed but show missing components
        assert exit_code == 0, f"check-installation failed: {output}"

        # Should indicate missing components
        assert "missing" in output.lower() or "not found" in output.lower()

    def test_check_installation_json_with_missing_deps(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation JSON output with missing dependencies."""
        # Install rxiv-maker with system deps skipped
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation with JSON
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --json"
        )
        assert exit_code == 0, f"check-installation --json failed: {output}"

        # Parse JSON and check for missing components
        try:
            result = json.loads(output)
            assert result["status"] == "incomplete"
            assert result["summary"]["missing"] > 0

            # Should have some components missing
            components = result["components"]
            missing_components = [k for k, v in components.items() if not v]
            assert len(missing_components) > 0

        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {output}")


class TestCheckInstallationFix:
    """Test the check-installation --fix functionality."""

    def test_check_installation_fix_help(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation --fix help."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation to see fix suggestions
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation"
        )
        assert exit_code == 0

        # Should suggest fix option
        assert "--fix" in output or "fix" in output.lower()

    def test_check_installation_fix_simulation(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation --fix command (simulation)."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation --fix
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --fix"
        )

        # Might fail due to missing install manager, but should attempt
        # Expected behavior varies based on implementation
        if exit_code != 0:
            # Check that it attempted to fix
            assert "fix" in output.lower() or "repair" in output.lower()
        else:
            # Should show some fix activity
            assert "fix" in output.lower() or "repair" in output.lower()

    def test_check_installation_without_fix(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation without --fix shows suggestions."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation without --fix
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation"
        )
        assert exit_code == 0

        # Should show suggestions for fixing
        assert "fix" in output.lower() or "repair" in output.lower()
        assert (
            "python -m rxiv_maker" in output
            or "rxiv check-installation --fix" in output
        )


class TestCheckInstallationComponents:
    """Test component checking functionality."""

    def test_python_component_check(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test Python component checking."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation with JSON to get component details
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --json"
        )
        assert exit_code == 0

        result = json.loads(output)
        components = result["components"]

        # Python should be available
        assert "python" in components
        assert components["python"] is True

    def test_latex_component_check(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test LaTeX component checking."""
        # Install rxiv-maker without system deps
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation with JSON
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --json"
        )
        assert exit_code == 0

        result = json.loads(output)
        components = result["components"]

        # LaTeX should be missing when system deps are skipped
        assert "latex" in components
        assert components["latex"] is False

    def test_nodejs_component_check(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test Node.js component checking."""
        # Install rxiv-maker without system deps
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation with JSON
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --json"
        )
        assert exit_code == 0

        result = json.loads(output)
        components = result["components"]

        # Node.js should be missing when system deps are skipped
        assert "nodejs" in components
        assert components["nodejs"] is False

    def test_component_status_consistency(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test that component status is consistent across calls."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation multiple times
        results = []
        for i in range(3):
            exit_code, output = run_in_container(
                ubuntu_container, "rxiv check-installation --json"
            )
            assert exit_code == 0
            results.append(json.loads(output))

        # Results should be consistent
        for i in range(1, len(results)):
            assert results[i]["components"] == results[0]["components"]
            assert results[i]["status"] == results[0]["status"]


class TestCheckInstallationErrorHandling:
    """Test error handling in check-installation command."""

    def test_check_installation_without_rxiv(self, docker_manager, ubuntu_container):
        """Test check-installation when rxiv is not installed."""
        # Don't install rxiv-maker

        # Try to run check-installation
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation"
        )
        assert exit_code != 0
        assert "command not found" in output or "not found" in output.lower()

    def test_check_installation_invalid_option(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation with invalid option."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation with invalid option
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --invalid-option"
        )
        assert exit_code != 0
        assert "error" in output.lower() or "invalid" in output.lower()

    def test_check_installation_permission_issues(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation with permission issues."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Create non-root user
        exit_code, output = run_in_container(ubuntu_container, "useradd -m testuser")
        assert exit_code == 0

        # Run check-installation as non-root user
        exit_code, output = run_in_container(
            ubuntu_container, "su testuser -c 'rxiv check-installation'"
        )
        # Should still work for checking (no write operations)
        assert exit_code == 0, f"check-installation failed for non-root user: {output}"

    def test_check_installation_corrupted_environment(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation with corrupted environment."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Corrupt PATH environment
        exit_code, output = run_in_container(
            ubuntu_container, "PATH=/invalid/path rxiv check-installation"
        )
        # Should handle PATH corruption gracefully
        assert exit_code != 0 or "error" in output.lower()


class TestCheckInstallationOutput:
    """Test output formatting of check-installation command."""

    def test_check_installation_output_format(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation output format."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation"
        )
        assert exit_code == 0

        # Check output format
        lines = output.strip().split("\\n")
        assert len(lines) > 0

        # Should have some structured output
        assert any(
            "status" in line.lower() or "component" in line.lower() for line in lines
        )

    def test_check_installation_json_format(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation JSON format."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation with JSON
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --json"
        )
        assert exit_code == 0

        # Validate JSON structure
        result = json.loads(output)

        # Required fields
        required_fields = ["status", "components", "summary"]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        # Status should be valid
        assert result["status"] in ["complete", "incomplete"]

        # Components should be a dict
        assert isinstance(result["components"], dict)

        # Summary should have required fields
        summary = result["summary"]
        summary_fields = ["total", "installed", "missing"]
        for field in summary_fields:
            assert field in summary, f"Missing summary field: {field}"
            assert isinstance(summary[field], int)

    def test_check_installation_detailed_format(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test check-installation detailed format."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Run check-installation with detailed output
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --detailed"
        )
        assert exit_code == 0

        # Should contain more detailed information
        assert "version" in output.lower() or "path" in output.lower()
        assert len(output.split("\\n")) > 5  # More lines than basic output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
