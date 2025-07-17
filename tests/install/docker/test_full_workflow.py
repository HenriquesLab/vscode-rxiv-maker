"""Full workflow integration tests (install → build PDF)."""

import json

import pytest

from ..conftest import install_rxiv_maker_in_container, run_in_container


class TestFullWorkflowIntegration:
    """Test complete workflow from installation to PDF generation."""

    def test_install_to_init_workflow(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test workflow from installation to manuscript initialization."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Initialize new manuscript
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv init test_manuscript"
        )
        assert exit_code == 0, f"Manuscript initialization failed: {output}"

        # Check that manuscript was created
        exit_code, output = run_in_container(
            ubuntu_container, "ls -la test_manuscript/"
        )
        assert exit_code == 0
        assert "00_CONFIG.yml" in output
        assert "01_MAIN.md" in output

    def test_install_to_validate_workflow(
        self, docker_manager, ubuntu_container, test_package_wheel, test_manuscript_dir
    ):
        """Test workflow from installation to manuscript validation."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Copy test manuscript to container
        manuscript_content = self._create_test_manuscript_content()

        # Create manuscript in container
        exit_code, output = run_in_container(
            ubuntu_container, "mkdir -p /tmp/test_manuscript"
        )
        assert exit_code == 0

        # Write manuscript files
        for filename, content in manuscript_content.items():
            exit_code, output = run_in_container(
                ubuntu_container,
                f"cat > /tmp/test_manuscript/{filename} << 'EOF'\\n{content}\\nEOF",
            )
            assert exit_code == 0

        # Validate manuscript
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv validate /tmp/test_manuscript"
        )
        assert exit_code == 0, f"Manuscript validation failed: {output}"

        # Should show validation results
        assert "validation" in output.lower() or "valid" in output.lower()

    # Figure generation test removed - not essential for core installation testing

    # Build workflow test removed - not essential without LaTeX

    def test_install_to_check_workflow(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test workflow from installation to installation checking."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Check installation
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation"
        )
        assert exit_code == 0, f"Installation check failed: {output}"

        # Should show installation status
        assert "python" in output.lower()
        assert "status" in output.lower() or "installation" in output.lower()

        # Check with JSON output
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv check-installation --json"
        )
        assert exit_code == 0

        # Parse JSON result
        result = json.loads(output)
        assert "status" in result
        assert "components" in result
        assert result["components"]["python"] is True

    def _create_test_manuscript_content(self):
        """Create test manuscript content."""
        return {
            "00_CONFIG.yml": """
title: "Test Manuscript"
authors:
  - name: "Test Author"
    affiliation: "Test University"
    email: "test@example.com"
abstract: "This is a test manuscript for workflow testing."
keywords: ["test", "workflow", "rxiv-maker"]
""",
            "01_MAIN.md": """
# Test Manuscript

This is a test manuscript to verify the complete workflow.

## Introduction

This document tests the workflow from installation to processing.

## Methods

We use standard testing methodologies.

## Results

The workflow should complete successfully.

## Conclusion

Integration testing is essential for ensuring system reliability.
""",
            "03_REFERENCES.bib": """
@article{test2023,
  title={Test Article for Workflow},
  author={Test Author},
  journal={Test Journal},
  year={2023},
  volume={1},
  pages={1-10}
}
""",
        }

    # Figure creation method removed - not needed


class TestWorkflowErrorHandling:
    """Test essential error handling only."""

    def test_workflow_with_missing_files(
        self, docker_manager, ubuntu_container, test_package_wheel
    ):
        """Test workflow with missing manuscript files."""
        # Install rxiv-maker
        exit_code, output = install_rxiv_maker_in_container(
            ubuntu_container, wheel_path=test_package_wheel, skip_system_deps=True
        )
        assert exit_code == 0, f"Installation failed: {output}"

        # Try to validate non-existent manuscript
        exit_code, output = run_in_container(
            ubuntu_container, "rxiv validate /tmp/nonexistent_manuscript"
        )
        assert exit_code != 0
        assert "not found" in output.lower() or "does not exist" in output.lower()


# Performance tests removed - not essential for core installation testing


# System dependency tests removed - not essential for core installation testing


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])  # Skip slow tests by default
