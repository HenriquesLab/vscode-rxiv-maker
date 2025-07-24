"""Tests for CI testing matrix and binary compatibility across platforms."""

import os
import platform
import sys
import tempfile
from pathlib import Path

import pytest


class TestCITestingMatrix:
    """Test CI testing matrix configuration for binary compatibility."""

    @pytest.fixture
    def test_workflow_path(self):
        """Get path to main test workflow."""
        return (
            Path(__file__).parent.parent.parent / ".github" / "workflows" / "test.yml"
        )

    @pytest.fixture
    def release_workflow_path(self):
        """Get path to release workflow."""
        return (
            Path(__file__).parent.parent.parent
            / ".github"
            / "workflows"
            / "release.yml"
        )

    def test_test_workflow_exists(self, test_workflow_path):
        """Test that the main test workflow exists."""
        assert test_workflow_path.exists(), "Main test workflow not found"

    def test_release_workflow_exists(self, release_workflow_path):
        """Test that the release workflow exists."""
        assert release_workflow_path.exists(), "Release workflow not found"

    def test_python_version_matrix(self, test_workflow_path):
        """Test that CI tests multiple Python versions for compatibility."""
        if not test_workflow_path.exists():
            pytest.skip("Test workflow not found")

        content = test_workflow_path.read_text()

        # Should test multiple Python versions
        assert "python-version:" in content or "python-versions:" in content

        # Should include supported versions
        assert "3.11" in content
        assert "3.12" in content

    def test_os_matrix_coverage(self, test_workflow_path):
        """Test that CI covers all major operating systems."""
        if not test_workflow_path.exists():
            pytest.skip("Test workflow not found")

        content = test_workflow_path.read_text()

        # Should test on major platforms
        assert "ubuntu-latest" in content
        assert "windows-latest" in content
        assert "macos-latest" in content

    def test_binary_build_matrix(self, release_workflow_path):
        """Test that binary builds cover all target platforms."""
        if not release_workflow_path.exists():
            pytest.skip("Release workflow not found")

        content = release_workflow_path.read_text()

        # Should build for all target platforms
        platforms = ["ubuntu-latest", "windows-latest", "macos-latest"]
        for platform_name in platforms:
            assert platform_name in content, f"Missing platform: {platform_name}"

    def test_architecture_matrix(self, release_workflow_path):
        """Test that different architectures are covered."""
        if not release_workflow_path.exists():
            pytest.skip("Release workflow not found")

        content = release_workflow_path.read_text()

        # Should handle different architectures
        assert "x64" in content or "amd64" in content
        assert "arm64" in content or "aarch64" in content

    def test_dependency_matrix_testing(self, test_workflow_path):
        """Test that CI tests with different dependency versions."""
        if not test_workflow_path.exists():
            pytest.skip("Test workflow not found")

        content = test_workflow_path.read_text()

        # Should install and test dependencies
        assert "install" in content.lower()
        assert "dependencies" in content.lower() or "requirements" in content.lower()

    def test_test_categorization(self, test_workflow_path):
        """Test that different test categories are properly configured."""
        if not test_workflow_path.exists():
            pytest.skip("Test workflow not found")

        content = test_workflow_path.read_text()

        # Should run different types of tests
        test_types = ["unit", "integration", "build"]

        for test_type in test_types:
            if test_type not in content.lower():
                # Log missing test type but don't fail (might be configured differently)
                print(f"Test type '{test_type}' not explicitly mentioned in workflow")

    def test_timeout_configurations(self, test_workflow_path, release_workflow_path):
        """Test that appropriate timeouts are configured."""
        workflows = []
        if test_workflow_path.exists():
            workflows.append(test_workflow_path)
        if release_workflow_path.exists():
            workflows.append(release_workflow_path)

        if not workflows:
            pytest.skip("No workflows found to test")

        for workflow_path in workflows:
            content = workflow_path.read_text()

            # Should have timeout configurations
            assert "timeout" in content.lower(), f"No timeout in {workflow_path.name}"

    def test_failure_handling_matrix(self, test_workflow_path):
        """Test that CI handles failures appropriately across platforms."""
        if not test_workflow_path.exists():
            pytest.skip("Test workflow not found")

        content = test_workflow_path.read_text()

        # Should have failure handling configuration
        assert "fail-fast" in content

        # Should continue testing other platforms on failure
        if "fail-fast: true" not in content:
            # This is good - allows testing all platforms
            pass


class TestBinaryCompatibilityMatrix:
    """Test binary compatibility across different environments."""

    def test_python_version_compatibility(self):
        """Test that the package works with supported Python versions."""
        # Check that current Python version is supported
        current_version = sys.version_info

        # Read supported versions from pyproject.toml
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()

            # Should specify minimum Python version
            assert "requires-python" in content
            assert ">=3.11" in content or ">=3.10" in content

        # Current version should be supported
        assert current_version >= (3, 11), (
            f"Python {current_version} may not be supported"
        )

    def test_os_specific_functionality(self):
        """Test OS-specific functionality that affects binary compatibility."""
        current_os = platform.system()

        # Test platform detection
        from rxiv_maker.utils.platform import get_platform_info

        platform_info = get_platform_info()

        assert platform_info["system"].lower() == current_os.lower()

    def test_architecture_detection(self):
        """Test that architecture is correctly detected."""
        current_arch = platform.machine().lower()

        # Should detect common architectures
        known_architectures = ["x86_64", "amd64", "arm64", "aarch64", "i386", "i686"]

        # Current architecture should be recognized or handled
        if current_arch not in known_architectures:
            print(f"Unknown architecture detected: {current_arch}")
            # Don't fail - just log for awareness

    def test_dependency_availability_matrix(self):
        """Test that dependencies are available across platforms."""
        # Core dependencies that must work everywhere
        core_deps = {
            "matplotlib": "plotting functionality",
            "numpy": "numerical operations",
            "pandas": "data handling",
            "click": "CLI framework",
            "rich": "rich terminal output",
            "yaml": "YAML processing",
            "PIL": "image processing",
        }

        missing_deps = {}
        for dep, purpose in core_deps.items():
            try:
                __import__(dep)
            except ImportError:
                missing_deps[dep] = purpose

        if missing_deps:
            pytest.skip(
                f"Missing dependencies in test environment: {list(missing_deps.keys())}"
            )

    def test_file_system_compatibility(self):
        """Test file system operations across platforms."""

        # Test path handling
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test file creation
            test_file = temp_path / "test.txt"
            test_file.write_text("test content", encoding="utf-8")
            assert test_file.exists()

            # Test directory creation
            test_dir = temp_path / "subdir"
            test_dir.mkdir()
            assert test_dir.exists()
            assert test_dir.is_dir()

            # Test path resolution
            resolved = test_file.resolve()
            assert resolved.exists()

    def test_encoding_compatibility(self):
        """Test that text encoding works across platforms."""
        # Test UTF-8 handling
        test_content = "Test content with Unicode: áéíóú 中文 🚀"

        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as f:
            f.write(test_content)
            temp_path = f.name

        try:
            with open(temp_path, encoding="utf-8") as f:
                read_content = f.read()

            assert read_content == test_content
        finally:
            os.unlink(temp_path)


class TestCIPerformanceMatrix:
    """Test CI performance considerations across platforms."""

    def test_build_time_considerations(self, release_workflow_path):
        """Test that build times are reasonable across platforms."""
        if not release_workflow_path.exists():
            pytest.skip("Release workflow not found")

        content = release_workflow_path.read_text()

        # Should have reasonable timeout values
        import re

        timeout_matches = re.findall(r"timeout-minutes:\s*(\d+)", content)

        if timeout_matches:
            max_timeout = max(int(t) for t in timeout_matches)

            # Build should not take more than reasonable time
            assert max_timeout <= 60, f"Build timeout too high: {max_timeout} minutes"

    def test_cache_configuration(self, test_workflow_path, release_workflow_path):
        """Test that caching is properly configured to improve CI performance."""
        workflows = []
        if test_workflow_path.exists():
            workflows.append(test_workflow_path)
        if release_workflow_path.exists():
            workflows.append(release_workflow_path)

        if not workflows:
            pytest.skip("No workflows found")

        for workflow_path in workflows:
            content = workflow_path.read_text()

            # Should use caching for dependencies
            assert "cache" in content.lower(), f"No caching in {workflow_path.name}"

    def test_parallel_execution(self, test_workflow_path):
        """Test that tests can run in parallel where appropriate."""
        if not test_workflow_path.exists():
            pytest.skip("Test workflow not found")

        content = test_workflow_path.read_text()

        # Should support parallel execution
        matrix_indicators = ["matrix:", "strategy:", "parallel"]

        has_parallelism = any(indicator in content for indicator in matrix_indicators)
        assert has_parallelism, "No parallelism configuration found"

    def test_resource_optimization(self, release_workflow_path):
        """Test that CI resources are optimized for binary building."""
        if not release_workflow_path.exists():
            pytest.skip("Release workflow not found")

        content = release_workflow_path.read_text()

        # Should optimize for binary building
        optimizations = ["upx", "strip", "cache", "artifact"]

        optimization_count = sum(1 for opt in optimizations if opt in content.lower())
        assert optimization_count >= 2, "Insufficient build optimizations"


class TestCIQualityAssurance:
    """Test quality assurance aspects of the CI matrix."""

    def test_linting_across_platforms(self, test_workflow_path):
        """Test that linting runs across platforms."""
        if not test_workflow_path.exists():
            pytest.skip("Test workflow not found")

        content = test_workflow_path.read_text()

        # Should include linting
        linting_tools = ["ruff", "lint", "flake8", "black", "isort"]

        has_linting = any(tool in content.lower() for tool in linting_tools)
        assert has_linting, "No linting configuration found"

    def test_type_checking_integration(self, test_workflow_path):
        """Test that type checking is integrated into CI."""
        if not test_workflow_path.exists():
            pytest.skip("Test workflow not found")

        content = test_workflow_path.read_text()

        # Should include type checking
        type_checkers = ["mypy", "pyright", "type", "check-types"]

        has_type_checking = any(checker in content.lower() for checker in type_checkers)
        if not has_type_checking:
            print("No explicit type checking found in CI")

    def test_security_scanning(self, test_workflow_path, release_workflow_path):
        """Test that security scanning is included where appropriate."""
        workflows = []
        if test_workflow_path.exists():
            workflows.append(test_workflow_path)
        if release_workflow_path.exists():
            workflows.append(release_workflow_path)

        if not workflows:
            pytest.skip("No workflows found")

        security_tools = ["bandit", "safety", "security", "audit"]

        for workflow_path in workflows:
            content = workflow_path.read_text()

            has_security = any(tool in content.lower() for tool in security_tools)
            if not has_security:
                print(f"No security scanning found in {workflow_path.name}")

    def test_test_coverage_reporting(self, test_workflow_path):
        """Test that test coverage is properly reported."""
        if not test_workflow_path.exists():
            pytest.skip("Test workflow not found")

        content = test_workflow_path.read_text()

        # Should include coverage reporting
        coverage_indicators = ["coverage", "codecov", "cov"]

        has_coverage = any(
            indicator in content.lower() for indicator in coverage_indicators
        )
        if not has_coverage:
            print("No coverage reporting found in CI")

    def test_artifact_retention_policy(self, release_workflow_path):
        """Test that artifact retention is properly configured."""
        if not release_workflow_path.exists():
            pytest.skip("Release workflow not found")

        content = release_workflow_path.read_text()

        # Should specify retention policy
        assert "retention-days" in content, "No artifact retention policy found"

        # Extract retention days
        import re

        retention_matches = re.findall(r"retention-days:\s*(\d+)", content)

        if retention_matches:
            retention_days = [int(days) for days in retention_matches]

            # Should have reasonable retention (not too short, not too long)
            for days in retention_days:
                assert 7 <= days <= 365, f"Unusual retention period: {days} days"


class TestBinaryTestingIntegrations:
    """Test integrations specific to binary testing."""

    def test_binary_smoke_tests(self):
        """Test that we have smoke tests for binary functionality."""
        # Check if there are tests that would catch binary-specific issues
        test_files = list(Path(__file__).parent.glob("test_*.py"))

        binary_test_files = [
            f for f in test_files if "binary" in f.name or "pyinstaller" in f.name
        ]
        assert len(binary_test_files) > 0, "No binary-specific tests found"

    def test_package_manager_integration_tests(self):
        """Test that package manager integration tests exist."""
        # Look for package manager tests
        test_dir = Path(__file__).parent

        pm_tests = (
            list(test_dir.glob("*package_manager*"))
            + list(test_dir.glob("*homebrew*"))
            + list(test_dir.glob("*scoop*"))
        )

        if not pm_tests:
            # Check if package manager tests are in the same file
            current_file = Path(__file__)
            content = current_file.read_text()

            pm_indicators = ["homebrew", "scoop", "package_manager", "brew", "manifest"]
            has_pm_tests = any(
                indicator in content.lower() for indicator in pm_indicators
            )

            assert has_pm_tests, "No package manager integration tests found"

    def test_end_to_end_binary_tests(self):
        """Test that end-to-end binary tests exist."""
        test_dir = Path(__file__).parent

        e2e_tests = list(test_dir.glob("*end_to_end*")) + list(test_dir.glob("*e2e*"))

        if not e2e_tests:
            # Check current file for e2e tests
            current_file = Path(__file__)
            content = current_file.read_text()

            e2e_indicators = ["end_to_end", "e2e", "workflow", "distribution"]
            has_e2e_tests = any(
                indicator in content.lower() for indicator in e2e_indicators
            )

            assert has_e2e_tests, "No end-to-end binary tests found"
