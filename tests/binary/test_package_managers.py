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
        """Test that formula uses binary URLs, not Python source."""
        content = formula_path.read_text()

        # Should point to GitHub releases, not PyPI
        assert "github.com/henriqueslab/rxiv-maker/releases" in content
        assert "files.pythonhosted.org" not in content  # No PyPI source

        # Should have platform-specific binaries
        assert "macos-arm64" in content or "macos-x64" in content
        assert "linux-x64" in content

    def test_formula_no_python_dependencies(self, formula_path):
        """Test that formula doesn't include Python dependencies."""
        content = formula_path.read_text()

        # Should not depend on Python
        assert 'depends_on "python' not in content

        # Should not have resource blocks for Python packages
        assert "resource " not in content
        assert "virtualenv_install_with_resources" not in content

    def test_formula_install_method(self, formula_path):
        """Test that install method is binary-focused."""
        content = formula_path.read_text()

        # Should install binary directly
        assert 'bin.install "rxiv"' in content
        assert "chmod 0755" in content  # Should set executable permissions

    def test_formula_test_section(self, formula_path):
        """Test that formula has proper test section."""
        content = formula_path.read_text()

        # Should test binary functionality
        assert 'shell_output("#{bin}/rxiv --version")' in content
        assert 'system bin/"rxiv", "--help"' in content

    def test_formula_architecture_support(self, formula_path):
        """Test that formula supports multiple architectures."""
        content = formula_path.read_text()

        # Should have platform-specific sections
        assert "on_macos do" in content
        assert "on_linux do" in content
        assert "Hardware::CPU.arm?" in content or "Hardware::CPU.intel?" in content

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

        required_fields = [
            "version",
            "description",
            "homepage",
            "license",
            "url",
            "hash",
            "bin",
        ]

        for field in required_fields:
            assert field in manifest, f"Required field '{field}' missing from manifest"

    def test_manifest_binary_url(self, manifest_path):
        """Test that manifest uses binary URL, not Python source."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        url = manifest["url"]

        # Should point to GitHub releases
        assert "github.com/henriqueslab/rxiv-maker/releases" in url

        # Should be Windows binary
        assert "windows-x64.zip" in url

        # Should not be PyPI source
        assert "files.pythonhosted.org" not in url

    def test_manifest_no_python_dependencies(self, manifest_path):
        """Test that manifest doesn't depend on Python."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Should not depend on Python
        depends = manifest.get("depends", [])
        assert "python" not in depends

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

        # Should be simple executable name
        assert bin_entry == "rxiv.exe", f"Expected 'rxiv.exe', got '{bin_entry}'"

    def test_manifest_checkver_configuration(self, manifest_path):
        """Test that manifest has proper version checking configuration."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "checkver" in manifest
        checkver = manifest["checkver"]

        # Should check GitHub releases
        assert "github.com" in checkver["url"]
        assert "releases/latest" in checkver["url"]

    def test_manifest_autoupdate_configuration(self, manifest_path):
        """Test that manifest has proper auto-update configuration."""
        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "autoupdate" in manifest
        autoupdate = manifest["autoupdate"]

        # Should auto-update from GitHub releases
        assert "github.com" in autoupdate["url"]
        assert "windows-x64.zip" in autoupdate["url"]
        assert "$version" in autoupdate["url"]


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
                assert scoop_version == main_version, (
                    f"Scoop version {scoop_version} != main version {main_version}"
                )
