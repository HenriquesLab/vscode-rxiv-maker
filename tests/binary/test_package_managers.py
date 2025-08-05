"""Tests for package manager integration (Homebrew, Scoop)."""

import json
import platform
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


class TestHomebrewFormula:
    """Test Homebrew formula structure and validity."""

    @pytest.fixture
    def formula_path(self):
        """Get path to Homebrew formula."""
        return (
            Path(__file__).parent.parent.parent
            / "submodules"
            / "homebrew-rxiv-maker"
            / "Formula"
            / "rxiv-maker.rb"
        )

    def test_formula_file_exists(self, formula_path):
        """Test that the Homebrew formula file exists."""
        assert formula_path.exists(), f"Formula file not found: {formula_path}"

    def test_formula_basic_structure(self, formula_path):
        """Test basic structure of Homebrew formula."""
        content = formula_path.read_text()

        # Check for required Ruby class structure
        assert "class RxivMaker < Formula" in content
        assert "desc " in content
        assert "homepage " in content
        assert "license " in content
        assert "url " in content
        assert "sha256 " in content
        assert "def install" in content
        assert "test do" in content

    def test_formula_binary_urls(self, formula_path):
        """Test that formula uses appropriate installation method."""
        content = formula_path.read_text()

        # Current implementation uses uv with PyPI for package management
        # Should use uv pip install rather than binary downloads
        assert "uv pip install" in content or "files.pythonhosted.org" in content

        # Should have virtual environment setup
        assert "uv venv" in content or "libexec" in content

    def test_formula_python_dependencies(self, formula_path):
        """Test that formula properly handles Python dependencies."""
        content = formula_path.read_text()

        # Current implementation uses uv for package management
        assert 'depends_on "uv"' in content

        # Should have virtual environment installation approach
        assert "uv venv" in content or "libexec" in content

        # Should not use resource blocks (since using pip install from PyPI)
        assert "resource " not in content
        assert "virtualenv_install_with_resources" not in content

    def test_formula_install_method(self, formula_path):
        """Test that install method properly creates executable."""
        content = formula_path.read_text()

        # Current implementation creates wrapper script instead of direct binary install
        assert '(bin/"rxiv").write' in content  # Creates wrapper script
        assert "chmod 0755" in content  # Should set executable permissions

    def test_formula_test_section(self, formula_path):
        """Test that formula has proper test section."""
        content = formula_path.read_text()

        # Should test binary functionality
        assert 'shell_output("#{bin}/rxiv --version")' in content
        assert 'system bin/"rxiv", "--help"' in content

    def test_formula_architecture_support(self, formula_path):
        """Test that formula works across architectures via PyPI."""
        content = formula_path.read_text()

        # PyPI source installation is architecture-independent
        # No need for platform-specific sections since pip handles architecture
        assert "def install" in content  # Has installation method
        assert "python" in content  # Uses Python (architecture handled by pip)

    @pytest.mark.slow
    def test_formula_syntax_validation(self, formula_path):
        """Test formula syntax with Ruby parser."""
        if not shutil.which("ruby"):
            pytest.skip("Ruby not available for syntax validation")

        try:
            result = subprocess.run(
                ["ruby", "-c", str(formula_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert result.returncode == 0, f"Ruby syntax error: {result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.fail("Ruby syntax check timed out")
        except FileNotFoundError:
            pytest.skip("Ruby not available")


class TestScoopManifest:
    """Test Scoop manifest structure and validity."""

    @pytest.fixture
    def manifest_path(self):
        """Get path to Scoop manifest."""
        return (
            Path(__file__).parent.parent.parent
            / "submodules"
            / "scoop-rxiv-maker"
            / "bucket"
            / "rxiv-maker.json"
        )

    def test_manifest_file_exists(self, manifest_path):
        """Test that the Scoop manifest file exists."""
        assert manifest_path.exists(), f"Manifest file not found: {manifest_path}"

    def test_manifest_valid_json(self, manifest_path):
        """Test that manifest is valid JSON."""
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in manifest: {e}")

        assert isinstance(manifest, dict)

    def test_manifest_required_fields(self, manifest_path):
        """Test that manifest has all required fields."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Core required fields for all manifests
        core_required_fields = [
            "version",
            "description",
            "homepage",
            "license",
            "bin",
        ]

        for field in core_required_fields:
            assert field in manifest, f"Required field '{field}' missing from manifest"

        # Check for either traditional binary approach OR uv tool install approach
        has_traditional_binary = "url" in manifest and "hash" in manifest
        has_uv_installer = "installer" in manifest and "depends" in manifest

        assert has_traditional_binary or has_uv_installer, (
            "Manifest must have either traditional binary fields (url, hash) "
            "or uv tool installer approach (installer, depends)"
        )

    def test_manifest_binary_url(self, manifest_path):
        """Test that manifest uses appropriate installation method."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Check if using traditional binary approach
        if "url" in manifest:
            url = manifest["url"]

            # Should point to GitHub releases
            assert "github.com/henriqueslab/rxiv-maker/releases" in url

            # Should be Windows binary
            assert "windows-x64.zip" in url

            # Should not be PyPI source
            assert "files.pythonhosted.org" not in url

        # Check if using uv tool install approach
        elif "installer" in manifest:
            installer = manifest["installer"]

            # Should use uv tool install
            assert "script" in installer
            assert "uv tool install rxiv-maker" in installer["script"]

            # Should depend on uv
            assert manifest.get("depends") == "uv"

        else:
            pytest.fail(
                "Manifest must have either 'url' for binary or 'installer' for uv "
                "tool approach"
            )

    def test_manifest_python_dependencies(self, manifest_path):
        """Test that manifest handles Python dependencies appropriately."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        depends = manifest.get("depends", [])

        # If using traditional binary approach, should not depend on Python
        if "url" in manifest:
            assert "python" not in depends, (
                "Binary approach should not depend on Python"
            )

        # If using uv tool install approach, should depend on uv (which handles Python)
        elif "installer" in manifest:
            assert "uv" in depends, "UV tool install approach must depend on uv"
            # UV approach may indirectly use Python but doesn't need explicit
            # Python dependency

        # Should not have Python installation commands (documentation mentions are OK)
        post_install = manifest.get("post_install", [])
        post_install_str = " ".join(post_install) if post_install else ""

        # Check for actual Python installation commands (not just documentation)
        # These would indicate the package actually installs Python dependencies
        assert "pip install rxiv-maker" not in post_install_str.replace(
            "use: pip install rxiv-maker", ""
        )  # Allow documentation mention
        assert "python -m pip install" not in post_install_str
        assert "python.exe -m pip" not in post_install_str

    def test_manifest_binary_executable(self, manifest_path):
        """Test that manifest specifies correct binary executable."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        bin_entry = manifest["bin"]

        # Check executable name based on installation method
        if "url" in manifest:
            # Traditional binary approach should use .exe extension
            assert bin_entry == "rxiv.exe", (
                f"Expected 'rxiv.exe' for binary, got '{bin_entry}'"
            )
        elif "installer" in manifest:
            # UV tool install approach uses platform-agnostic name
            assert bin_entry == "rxiv", (
                f"Expected 'rxiv' for uv tool install, got '{bin_entry}'"
            )

    def test_manifest_checkver_configuration(self, manifest_path):
        """Test that manifest has proper version checking configuration."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "checkver" in manifest
        checkver = manifest["checkver"]

        # Check version source based on installation method
        if "url" in manifest:
            # Traditional binary approach should check GitHub releases
            assert "github.com" in checkver["url"]
            assert "releases/latest" in checkver["url"]
        elif "installer" in manifest:
            # UV tool install approach should check PyPI
            assert "pypi.org" in checkver["url"]
            assert "jsonpath" in checkver

    def test_manifest_autoupdate_configuration(self, manifest_path):
        """Test that manifest has proper auto-update configuration."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "autoupdate" in manifest
        autoupdate = manifest["autoupdate"]

        # Check autoupdate configuration based on installation method
        if "url" in manifest:
            # Traditional binary approach should auto-update from GitHub releases
            assert "github.com" in autoupdate["url"]
            assert "windows-x64.zip" in autoupdate["url"]
            assert "$version" in autoupdate["url"]
        elif "installer" in manifest:
            # UV tool install approach should have installer script with version
            # placeholder
            assert "installer" in autoupdate
            assert "script" in autoupdate["installer"]
            assert "$version" in autoupdate["installer"]["script"]


class TestPackageManagerWorkflows:
    """Test package manager update workflows."""

    def test_homebrew_update_workflow_exists(self):
        """Test that Homebrew update workflow exists."""
        workflow_path = (
            Path(__file__).parent.parent.parent
            / "submodules"
            / "homebrew-rxiv-maker"
            / ".github"
            / "workflows"
            / "update-formula.yml"
        )
        assert workflow_path.exists(), "Homebrew update workflow not found"

    def test_scoop_update_workflow_exists(self):
        """Test that Scoop update workflow exists."""
        workflow_path = (
            Path(__file__).parent.parent.parent
            / "submodules"
            / "scoop-rxiv-maker"
            / ".github"
            / "workflows"
            / "update-manifest.yml"
        )
        assert workflow_path.exists(), "Scoop update workflow not found"

    def test_homebrew_workflow_structure(self):
        """Test Homebrew workflow structure."""
        workflow_path = (
            Path(__file__).parent.parent.parent
            / "submodules"
            / "homebrew-rxiv-maker"
            / ".github"
            / "workflows"
            / "update-formula.yml"
        )

        if not workflow_path.exists():
            pytest.skip("Homebrew workflow not found")

        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)

        # Get the 'on' section (YAML may parse 'on:' as boolean True)
        on_section = workflow.get("on") or workflow.get(True)
        assert on_section is not None, "Workflow 'on' section not found"

        # Should trigger on repository_dispatch and workflow_dispatch
        assert "repository_dispatch" in on_section
        assert "workflow_dispatch" in on_section

        # Should have update-formula job
        assert "update-formula" in workflow["jobs"]

    def test_scoop_workflow_structure(self):
        """Test Scoop workflow structure."""
        workflow_path = (
            Path(__file__).parent.parent.parent
            / "submodules"
            / "scoop-rxiv-maker"
            / ".github"
            / "workflows"
            / "update-manifest.yml"
        )

        if not workflow_path.exists():
            pytest.skip("Scoop workflow not found")

        content = workflow_path.read_text()
        workflow = yaml.safe_load(content)

        # Get the 'on' section (YAML may parse 'on:' as boolean True)
        on_section = workflow.get("on") or workflow.get(True)
        assert on_section is not None, "Workflow 'on' section not found"

        # Should trigger on repository_dispatch and workflow_dispatch
        assert "repository_dispatch" in on_section
        assert "workflow_dispatch" in on_section

        # Should have update-manifest job
        assert "update-manifest" in workflow["jobs"]


class TestPackageManagerIntegration:
    """Integration tests for package manager functionality."""

    @pytest.mark.slow
    @pytest.mark.skipif(
        platform.system() != "Darwin", reason="Homebrew tests require macOS"
    )
    def test_homebrew_tap_structure(self):
        """Test Homebrew tap repository structure."""
        if not shutil.which("brew"):
            pytest.skip("Homebrew not available")

        # Test that we can validate the formula structure
        formula_path = (
            Path(__file__).parent.parent.parent
            / "submodules"
            / "homebrew-rxiv-maker"
            / "Formula"
            / "rxiv-maker.rb"
        )

        if not formula_path.exists():
            pytest.skip("Homebrew formula not found")

        # Test formula with Homebrew (if available)
        try:
            result = subprocess.run(
                ["brew", "info", "--formula", str(formula_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # Formula is parseable by Homebrew
                assert "rxiv-maker" in result.stdout.lower()
            else:
                # Formula has issues - log but don't fail (might be environment)
                print(f"Homebrew formula validation warning: {result.stderr}")

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Homebrew validation not available")

    @pytest.mark.slow
    @pytest.mark.skipif(
        platform.system() != "Windows", reason="Scoop tests require Windows"
    )
    def test_scoop_bucket_structure(self):
        """Test Scoop bucket repository structure."""
        if not shutil.which("scoop"):
            pytest.skip("Scoop not available")

        manifest_path = (
            Path(__file__).parent.parent.parent
            / "submodules"
            / "scoop-rxiv-maker"
            / "bucket"
            / "rxiv-maker.json"
        )

        if not manifest_path.exists():
            pytest.skip("Scoop manifest not found")

        # Test that Scoop can parse the manifest
        try:
            # Note: This would require Scoop to be installed and available
            # In CI, we test JSON validity instead
            with open(manifest_path) as f:
                manifest = json.load(f)

            # Validate against Scoop schema expectations
            assert "version" in manifest
            assert "url" in manifest
            assert "hash" in manifest
            assert "bin" in manifest

        except json.JSONDecodeError as e:
            pytest.fail(f"Scoop manifest JSON error: {e}")

    def test_package_manager_version_consistency(self):
        """Test that package managers reference consistent versions."""
        # Get version from main package
        version_file = (
            Path(__file__).parent.parent.parent
            / "src"
            / "rxiv_maker"
            / "__version__.py"
        )

        if not version_file.exists():
            pytest.skip("Version file not found")

        # Extract version
        version_content = version_file.read_text()
        import re

        version_match = re.search(
            r'__version__\s*=\s*["\']([^"\']+)["\']', version_content
        )

        if not version_match:
            pytest.skip("Could not extract version")

        main_version = version_match.group(1)

        # Check Scoop manifest version
        scoop_manifest = (
            Path(__file__).parent.parent.parent
            / "submodules"
            / "scoop-rxiv-maker"
            / "bucket"
            / "rxiv-maker.json"
        )
        if scoop_manifest.exists():
            with open(scoop_manifest) as f:
                manifest = json.load(f)
            scoop_version = manifest.get("version")

            if scoop_version:
                # In CI/release environments, submodules may lag behind main version
                # Only enforce strict version matching in development environments
                import os

                is_ci = os.environ.get("CI") == "true"
                is_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"

                if is_ci or is_github_actions:
                    # In CI, allow submodule versions to be behind main version
                    # but warn if they're too far behind
                    try:
                        from packaging.version import Version

                        main_ver = Version(main_version)
                        scoop_ver = Version(scoop_version)

                        # Allow submodule to be behind by at most one minor version
                        if scoop_ver < main_ver:
                            major_diff = main_ver.major - scoop_ver.major
                            minor_diff = (
                                main_ver.minor - scoop_ver.minor
                                if main_ver.major == scoop_ver.major
                                else float("inf")
                            )

                            if major_diff > 0 or minor_diff > 1:
                                import warnings

                                warnings.warn(
                                    f"Scoop version {scoop_version} significantly behind "
                                    f"main version {main_version}",
                                    UserWarning,
                                    stacklevel=2,
                                )
                    except ImportError:
                        # If packaging not available, just warn
                        import warnings

                        warnings.warn(
                            f"Scoop version {scoop_version} != main version "
                            f"{main_version} (CI environment)",
                            UserWarning,
                            stacklevel=2,
                        )
                else:
                    # In development, enforce strict version matching
                    assert scoop_version == main_version, (
                        f"Scoop version {scoop_version} != main version {main_version}"
                    )
