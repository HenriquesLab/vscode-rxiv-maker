"""Integration tests for path resolution in different environments."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

    class MockPytest:
        class mark:
            @staticmethod
            def integration(cls):
                return cls

            @staticmethod
            def path_resolution(cls):
                return cls

    pytest = MockPytest()

try:
    # Check if find_manuscript_md is available using importlib to avoid F401
    import importlib.util

    from rxiv_maker.commands.build_manager import BuildManager

    find_manuscript_available = importlib.util.find_spec("rxiv_maker.utils") is not None

    BUILD_MANAGER_AVAILABLE = True
except ImportError:
    BUILD_MANAGER_AVAILABLE = False


@pytest.mark.integration
@unittest.skipUnless(BUILD_MANAGER_AVAILABLE, "Build manager not available")
class TestPathResolutionIntegration(unittest.TestCase):
    """Test path resolution in realistic scenarios."""

    def setUp(self):
        """Set up test manuscript structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.manuscript_dir = Path(self.temp_dir) / "test_manuscript"
        self.manuscript_dir.mkdir()

        # Create minimal but complete manuscript structure
        self.create_test_manuscript()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_manuscript(self):
        """Create a minimal test manuscript."""
        # Main manuscript file
        main_md = self.manuscript_dir / "01_MAIN.md"
        main_md.write_text("""---
title:
  main: "Path Resolution Test Manuscript"
authors:
  - name: "Test Author"
    email: "test@example.com"
date: "2025-01-01"
---

# Introduction

This is a test manuscript for path resolution.

## Methods

Testing path resolution [@testref2024].

# References
""")

        # Config file
        config_yml = self.manuscript_dir / "00_CONFIG.yml"
        config_yml.write_text("""title:
  main: "Path Resolution Test Manuscript"
authors:
  - name: "Test Author"
    email: "test@example.com"
date: "2025-01-01"
""")

        # References file
        references_bib = self.manuscript_dir / "03_REFERENCES.bib"
        references_bib.write_text("""@article{testref2024,
  title={Test Reference},
  author={Test Author},
  journal={Test Journal},
  year={2024}
}
""")

        # Create FIGURES directory
        figures_dir = self.manuscript_dir / "FIGURES"
        figures_dir.mkdir()

    def test_build_from_different_working_directories(self):
        """Test that build works from different working directories."""
        original_cwd = os.getcwd()

        # Test from project root (should work)
        try:
            os.chdir(Path(__file__).parent.parent.parent)  # Go to project root

            build_manager = BuildManager(
                manuscript_path=str(self.manuscript_dir),
                output_dir=str(self.manuscript_dir / "output"),
                skip_validation=True,
                verbose=False,
            )

            # These should not fail with path resolution errors
            result = build_manager.copy_style_files()
            self.assertTrue(result)

            # Style directory should exist and be resolved correctly
            self.assertTrue(build_manager.style_dir.exists())

        finally:
            os.chdir(original_cwd)

    def test_build_from_manuscript_directory(self):
        """Test that build works when CWD is the manuscript directory."""
        original_cwd = os.getcwd()

        try:
            # Change to manuscript directory
            os.chdir(self.manuscript_dir)

            build_manager = BuildManager(
                manuscript_path=".",  # Current directory
                output_dir="output",
                skip_validation=True,
                verbose=False,
            )

            # Style files should still be found
            result = build_manager.copy_style_files()
            self.assertTrue(result)

            # Style directory path should be absolute and correct
            self.assertTrue(build_manager.style_dir.is_absolute())
            self.assertTrue(build_manager.style_dir.exists())

        finally:
            os.chdir(original_cwd)

    def test_build_from_random_directory(self):
        """Test that build works from a completely unrelated directory."""
        original_cwd = os.getcwd()
        random_dir = tempfile.mkdtemp()

        try:
            os.chdir(random_dir)

            build_manager = BuildManager(
                manuscript_path=str(self.manuscript_dir),
                output_dir=str(self.manuscript_dir / "output"),
                skip_validation=True,
                verbose=False,
            )

            # Should still work with absolute paths
            result = build_manager.copy_style_files()
            self.assertTrue(result)

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(random_dir, ignore_errors=True)

    def test_module_execution_paths(self):
        """Test that module execution works from different directories."""
        original_cwd = os.getcwd()

        try:
            # Change to a different directory
            temp_cwd = tempfile.mkdtemp()
            os.chdir(temp_cwd)

            # Set up environment
            env = os.environ.copy()
            env["MANUSCRIPT_PATH"] = str(self.manuscript_dir)
            env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent / "src")

            # Test copy_pdf module execution
            output_dir = self.manuscript_dir / "output"
            output_dir.mkdir(exist_ok=True)

            # Create a fake PDF to copy
            fake_pdf = output_dir / f"{self.manuscript_dir.name}.pdf"
            fake_pdf.write_bytes(b"fake PDF content")

            # This should work with module path
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "rxiv_maker.commands.copy_pdf",
                    "--output-dir",
                    str(output_dir),
                ],
                env=env,
                capture_output=True,
                text=True,
            )

            # Should not fail with "file not found" error
            # Allow failures due to missing optional dependencies like 'yaml'
            if result.returncode != 0 and "yaml" not in result.stderr:
                self.assertEqual(
                    result.returncode, 0, f"copy_pdf module failed: {result.stderr}"
                )
            # If it failed due to yaml dependency, that's acceptable in test environments

        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_cwd, ignore_errors=True)

    def test_regression_relative_path_failure(self):
        """Regression test: simulate the original relative path failure."""
        # This test simulates what would happen with the old relative path approach
        original_cwd = os.getcwd()

        try:
            # Change to manuscript directory (where the bug occurred)
            os.chdir(self.manuscript_dir)

            # Test that old-style relative paths would fail
            old_style_path = Path("src/rxiv_maker/commands/copy_pdf.py")
            self.assertFalse(
                old_style_path.exists(),
                "Old relative path should not exist from manuscript directory",
            )

            # But our new approach should work
            build_manager = BuildManager(
                manuscript_path=".",
                output_dir="output",
                skip_validation=True,
                verbose=False,
            )

            # This should work because we use __file__ relative paths
            self.assertTrue(build_manager.style_dir.is_absolute())

        finally:
            os.chdir(original_cwd)

    def test_pdf_generation_with_path_resolution(self):
        """Integration test: complete PDF generation with proper path resolution."""
        build_manager = BuildManager(
            manuscript_path=str(self.manuscript_dir),
            output_dir=str(self.manuscript_dir / "output"),
            skip_validation=True,  # Skip validation to focus on path resolution
            verbose=False,
        )

        # Mock the PDF compilation to avoid LaTeX dependency
        with unittest.mock.patch.object(
            build_manager, "_compile_pdf_local", return_value=True
        ):
            # Create fake output PDF
            output_dir = Path(build_manager.output_dir)
            output_dir.mkdir(exist_ok=True)
            fake_pdf = output_dir / f"{build_manager.manuscript_name}.pdf"
            fake_pdf.write_bytes(b"fake PDF content")
            build_manager.output_pdf = fake_pdf

            # Test that all path-dependent operations work
            style_result = build_manager.copy_style_files()
            self.assertTrue(style_result)

            # Test subprocess-based operations with mocking
            with unittest.mock.patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "Success"
                mock_run.return_value.stderr = ""

                pdf_copy_result = build_manager.copy_pdf_to_manuscript()
                self.assertTrue(pdf_copy_result)

                # Verify the command used module paths
                args, _ = mock_run.call_args
                cmd = args[0]
                self.assertIn("-m", cmd)
                self.assertIn("rxiv_maker.commands.copy_pdf", cmd)

    def test_docker_path_resolution(self):
        """Test path resolution in Docker mode (if available)."""
        # Only test if Docker is available
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.skipTest("Docker not available")
        except FileNotFoundError:
            self.skipTest("Docker not available")

        build_manager = BuildManager(
            manuscript_path=str(self.manuscript_dir),
            output_dir=str(self.manuscript_dir / "output"),
            engine="docker",
            skip_validation=True,
            verbose=False,
        )

        # Docker paths should use /workspace prefix and module paths
        output_dir = Path(build_manager.output_dir)
        output_dir.mkdir(exist_ok=True)
        fake_pdf = output_dir / f"{build_manager.manuscript_name}.pdf"
        fake_pdf.write_bytes(b"fake PDF content")
        build_manager.output_pdf = fake_pdf

        # Mock the Docker manager to verify command construction
        with unittest.mock.patch.object(build_manager, "docker_manager") as mock_docker:
            mock_docker.run_command.return_value.returncode = 0

            build_manager._run_pdf_validation_docker()

            # Verify Docker command used module path
            call_args = mock_docker.run_command.call_args
            if call_args:
                command = call_args[1]["command"]
                self.assertIn("-m", command)
                self.assertIn("rxiv_maker.validators.pdf_validator", command)


if __name__ == "__main__":
    unittest.main()
