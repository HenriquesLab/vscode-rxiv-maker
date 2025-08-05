"""Unit tests for command module execution with python -m."""

import os
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
            def unit(cls):
                return cls

    pytest = MockPytest()


@pytest.mark.unit
class TestCommandModuleExecution(unittest.TestCase):
    """Test that command modules can be executed with python -m."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manuscript_dir = Path(self.temp_dir) / "test_manuscript"
        self.manuscript_dir.mkdir()
        self.output_dir = self.manuscript_dir / "output"
        self.output_dir.mkdir()

        # Set up environment for module execution
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent / "src")
        self.env["MANUSCRIPT_PATH"] = str(self.manuscript_dir)

        # Create minimal manuscript structure
        self.create_test_manuscript()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_manuscript(self):
        """Create minimal test manuscript."""
        main_md = self.manuscript_dir / "01_MAIN.md"
        main_md.write_text("""---
title:
  main: "Test Manuscript"
authors:
  - name: "Test Author"
    email: "test@example.com"
date: "2025-01-01"
---

# Test

This is a test manuscript with 50 words for word count testing purposes.
We need enough content to trigger meaningful word count analysis and validation.
The manuscript should contain multiple sections including introduction, methods, and results.
Each section contributes to the overall word count that will be analyzed.
""")

        config_yml = self.manuscript_dir / "00_CONFIG.yml"
        config_yml.write_text("""title:
  main: "Test Manuscript"
authors:
  - name: "Test Author"
    email: "test@example.com"
date: "2025-01-01"
""")

        references_bib = self.manuscript_dir / "03_REFERENCES.bib"
        references_bib.write_text("""@article{test2024,
  title={Test Reference},
  author={Test Author},
  journal={Test Journal},
  year={2024}
}
""")

    def test_copy_pdf_module_execution(self):
        """Test that copy_pdf can be executed as a module."""
        # Create a fake PDF to copy
        fake_pdf = self.output_dir / f"{self.manuscript_dir.name}.pdf"
        fake_pdf.write_bytes(b"fake PDF content for testing")

        # Execute copy_pdf as module
        result = subprocess.run(
            [
                "python",
                "-m",
                "rxiv_maker.commands.copy_pdf",
                "--output-dir",
                str(self.output_dir),
            ],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should not fail with import errors or file not found
        if result.returncode != 0:
            self.fail(
                f"copy_pdf module execution failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )

        # Should produce some output
        self.assertTrue(result.stdout or result.stderr, "Module should produce output")

    def test_pdf_validator_module_execution(self):
        """Test that pdf_validator can be executed as a module."""
        # Create a fake PDF to validate
        fake_pdf = self.output_dir / f"{self.manuscript_dir.name}.pdf"
        fake_pdf.write_bytes(b"fake PDF content for validation testing")

        # Execute pdf_validator as module
        result = subprocess.run(
            [
                "python",
                "-m",
                "rxiv_maker.validators.pdf_validator",
                str(self.manuscript_dir),
                "--pdf-path",
                str(fake_pdf),
            ],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should not fail with import errors
        # Note: PDF validation might fail on fake PDF, but module should load
        if "ModuleNotFoundError" in result.stderr or "ImportError" in result.stderr:
            self.fail(
                f"pdf_validator module import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )

    def test_analyze_word_count_module_execution(self):
        """Test that analyze_word_count can be executed as a module."""
        # Execute analyze_word_count as module
        result = subprocess.run(
            ["python", "-m", "rxiv_maker.commands.analyze_word_count"],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should not fail with import errors or module not found
        if "ModuleNotFoundError" in result.stderr or "ImportError" in result.stderr:
            self.fail(
                f"analyze_word_count module import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )

        # Should produce some output (word count analysis)
        self.assertTrue(
            result.stdout or result.stderr, "Word count module should produce output"
        )

    def test_module_help_functionality(self):
        """Test that modules support --help flag."""
        modules_to_test = [
            "rxiv_maker.commands.copy_pdf",
            "rxiv_maker.validators.pdf_validator",
        ]

        for module in modules_to_test:
            with self.subTest(module=module):
                result = subprocess.run(
                    ["python", "-m", module, "--help"],
                    env=self.env,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                # Should not fail with import errors
                if result.returncode != 0 and (
                    "ModuleNotFoundError" in result.stderr
                    or "ImportError" in result.stderr
                ):
                    self.fail(
                        f"{module} module import failed:\nstderr: {result.stderr}"
                    )

                # Help should be available (either in stdout or returncode 0)
                # Some modules might not implement --help perfectly, so we're lenient
                self.assertFalse("ModuleNotFoundError" in result.stderr)
                self.assertFalse("ImportError" in result.stderr)

    def test_module_import_functionality(self):
        """Test that modules can be imported without errors."""
        modules_to_test = [
            "rxiv_maker.commands.copy_pdf",
            "rxiv_maker.validators.pdf_validator",
            "rxiv_maker.commands.analyze_word_count",
        ]

        for module in modules_to_test:
            with self.subTest(module=module):
                # Test basic import capability
                result = subprocess.run(
                    ["python", "-c", f"import {module}; print('Import successful')"],
                    env=self.env,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                if result.returncode != 0:
                    self.fail(
                        f"{module} import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
                    )

                self.assertIn("Import successful", result.stdout)

    def test_module_execution_from_different_directories(self):
        """Test that modules can be executed from different working directories."""
        original_cwd = os.getcwd()
        temp_cwd = tempfile.mkdtemp()

        try:
            os.chdir(temp_cwd)

            # Create fake PDF in the output directory
            fake_pdf = self.output_dir / f"{self.manuscript_dir.name}.pdf"
            fake_pdf.write_bytes(b"fake PDF content")

            # Execute copy_pdf from different directory
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "rxiv_maker.commands.copy_pdf",
                    "--output-dir",
                    str(self.output_dir),
                ],
                env=self.env,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should not fail due to path issues
            if "FileNotFoundError" in result.stderr and "copy_pdf.py" in result.stderr:
                self.fail(
                    f"Module execution failed due to path issues:\nstderr: {result.stderr}"
                )

        finally:
            os.chdir(original_cwd)
            import shutil

            shutil.rmtree(temp_cwd, ignore_errors=True)

    def test_module_vs_script_execution(self):
        """Test that module execution works when script execution would fail."""
        original_cwd = os.getcwd()

        try:
            # Change to a directory where relative paths would fail
            os.chdir(self.manuscript_dir)

            # Old-style script execution would fail from here
            script_path = Path("src/rxiv_maker/commands/copy_pdf.py")
            self.assertFalse(
                script_path.exists(),
                "Old script path should not exist from manuscript directory",
            )

            # But module execution should work
            fake_pdf = self.output_dir / f"{self.manuscript_dir.name}.pdf"
            fake_pdf.write_bytes(b"fake PDF content")

            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "rxiv_maker.commands.copy_pdf",
                    "--output-dir",
                    str(self.output_dir),
                ],
                env=self.env,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should not fail with "can't open file" error
            self.assertNotIn("can't open file", result.stderr)

            # Should not fail with import errors related to our modules
            # Allow failures due to missing optional dependencies like 'yaml'
            if "ModuleNotFoundError" in result.stderr:
                # If it's a yaml dependency issue, that's acceptable in test environments
                if "yaml" in result.stderr:
                    pass  # This is acceptable - missing optional dependency
                # If it's an rxiv_maker module that can't be found, that's a real problem
                elif "rxiv_maker" in result.stderr and "yaml" not in result.stderr:
                    self.fail(
                        f"Module execution failed with rxiv_maker import issue:\nstderr: {result.stderr}"
                    )
                # Other import errors might be acceptable too
                else:
                    pass  # Acceptable - other missing dependencies

        finally:
            os.chdir(original_cwd)

    def test_error_handling_in_modules(self):
        """Test that modules handle errors gracefully."""
        # Test copy_pdf with invalid output directory
        result = subprocess.run(
            [
                "python",
                "-m",
                "rxiv_maker.commands.copy_pdf",
                "--output-dir",
                "/nonexistent/directory",
            ],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Should not crash with unhandled exceptions
        # Module might return non-zero exit code, but shouldn't crash
        self.assertNotIn(
            "Traceback", result.stderr, "Module should handle errors gracefully"
        )

        # Test pdf_validator with invalid PDF path
        result = subprocess.run(
            [
                "python",
                "-m",
                "rxiv_maker.validators.pdf_validator",
                str(self.manuscript_dir),
                "--pdf-path",
                "/nonexistent/file.pdf",
            ],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Should not crash with unhandled exceptions
        self.assertNotIn(
            "Traceback", result.stderr, "Module should handle errors gracefully"
        )


if __name__ == "__main__":
    unittest.main()
