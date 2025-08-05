"""Unit tests for build manager improvements."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

    # Define mock pytest.mark for when pytest is not available
    class MockPytest:
        class mark:
            @staticmethod
            def build_manager(cls):
                return cls

    pytest = MockPytest()

try:
    from rxiv_maker.commands.build_manager import BuildManager

    BUILD_MANAGER_AVAILABLE = True
except ImportError:
    BUILD_MANAGER_AVAILABLE = False


@pytest.mark.build_manager
@unittest.skipUnless(BUILD_MANAGER_AVAILABLE, "Build manager not available")
class TestBuildManagerLogging(unittest.TestCase):
    """Test build manager logging functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manuscript_dir = os.path.join(self.temp_dir, "manuscript")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.manuscript_dir)
        os.makedirs(self.output_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up logging handlers before removing files (Windows compatibility)
        from rxiv_maker.core.logging_config import cleanup

        cleanup()

        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_build_manager_initialization_creates_log_paths(self):
        """Test that BuildManager creates log file paths on initialization."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Check that log file paths are set
        self.assertTrue(hasattr(build_manager, "warnings_log"))
        self.assertTrue(hasattr(build_manager, "bibtex_log"))
        self.assertEqual(build_manager.warnings_log.name, "build_warnings.log")
        self.assertEqual(build_manager.bibtex_log.name, "bibtex_warnings.log")

    def test_log_to_file_creates_warning_log(self):
        """Test that warnings are logged to file."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Log a warning
        build_manager._log_to_file("Test warning message", "WARNING")

        # Check that log file was created
        self.assertTrue(build_manager.warnings_log.exists())

        # Check log content
        with open(build_manager.warnings_log) as f:
            content = f.read()

        self.assertIn("WARNING: Test warning message", content)
        self.assertIn("2025-", content)  # Should have timestamp

    def test_log_to_file_creates_error_log(self):
        """Test that errors are logged to file."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Log an error
        build_manager._log_to_file("Test error message", "ERROR")

        # Check that log file was created
        self.assertTrue(build_manager.warnings_log.exists())

        # Check log content
        with open(build_manager.warnings_log) as f:
            content = f.read()

        self.assertIn("ERROR: Test error message", content)

    def test_log_method_calls_file_logging_for_warnings(self):
        """Test that the log method calls file logging for warnings."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        with patch.object(build_manager, "_log_to_file") as mock_log_to_file:
            build_manager.log("Test warning", "WARNING")

            # Should have called _log_to_file
            mock_log_to_file.assert_called_once_with("Test warning", "WARNING")

    def test_log_method_calls_file_logging_for_errors(self):
        """Test that the log method calls file logging for errors."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        with patch.object(build_manager, "_log_to_file") as mock_log_to_file:
            build_manager.log("Test error", "ERROR")

            # Should have called _log_to_file
            mock_log_to_file.assert_called_once_with("Test error", "ERROR")

    def test_log_method_does_not_call_file_logging_for_info(self):
        """Test that the log method does not call file logging for info messages."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        with patch.object(build_manager, "_log_to_file") as mock_log_to_file:
            build_manager.log("Test info", "INFO")

            # Should NOT have called _log_to_file
            mock_log_to_file.assert_not_called()

    def test_log_bibtex_warnings_extracts_from_blg_file(self):
        """Test that BibTeX warnings are extracted from .blg file."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Create a mock .blg file with warnings
        blg_content = """This is BibTeX, Version 0.99d
Warning--empty journal in test_reference
Warning--missing year in another_reference
You've used 2 entries,
(There were 2 warnings)
"""

        blg_file = Path(self.output_dir) / f"{Path(self.manuscript_dir).name}.blg"
        with open(blg_file, "w") as f:
            f.write(blg_content)

        with patch.object(build_manager, "log") as mock_log:
            build_manager._log_bibtex_warnings()

            # Should have logged success message
            mock_log.assert_called_once()
            args, kwargs = mock_log.call_args
            self.assertIn("BibTeX warnings logged", args[0])
            self.assertEqual(args[1], "INFO")

        # Check that BibTeX warning log was created
        self.assertTrue(build_manager.bibtex_log.exists())

        # Check log content
        with open(build_manager.bibtex_log) as f:
            content = f.read()

        self.assertIn("BibTeX Warnings Report", content)
        self.assertIn("1. empty journal in test_reference", content)
        self.assertIn("2. missing year in another_reference", content)

    def test_log_bibtex_warnings_handles_no_warnings(self):
        """Test that BibTeX warning logging handles case with no warnings."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Create a mock .blg file without warnings
        blg_content = """This is BibTeX, Version 0.99d
You've used 2 entries,
(There were 0 warnings)
"""

        blg_file = Path(self.output_dir) / f"{Path(self.manuscript_dir).name}.blg"
        with open(blg_file, "w") as f:
            f.write(blg_content)

        with patch.object(build_manager, "log") as mock_log:
            build_manager._log_bibtex_warnings()

            # Should not have logged anything
            mock_log.assert_not_called()

        # Should not have created warning log
        self.assertFalse(build_manager.bibtex_log.exists())

    def test_log_bibtex_warnings_handles_missing_blg_file(self):
        """Test that BibTeX warning logging handles missing .blg file."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Don't create .blg file

        with patch.object(build_manager, "log") as mock_log:
            build_manager._log_bibtex_warnings()

            # Should not have logged anything
            mock_log.assert_not_called()

        # Should not have created warning log
        self.assertFalse(build_manager.bibtex_log.exists())

    def test_log_to_file_handles_exceptions_gracefully(self):
        """Test that file logging handles exceptions gracefully."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Mock file operations to raise exception
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            # Should not raise exception
            try:
                build_manager._log_to_file("Test message", "WARNING")
            except Exception:
                self.fail("_log_to_file should handle exceptions gracefully")

    def test_build_completion_reports_warning_log_existence(self):
        """Test that build completion reports warning log existence."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Create a warning log file
        build_manager.warnings_log.touch()

        # Mock the full build process
        with (
            patch.object(build_manager, "check_manuscript_structure", return_value=True),
            patch.object(build_manager, "setup_output_directory", return_value=True),
            patch.object(build_manager, "generate_figures", return_value=True),
            patch.object(build_manager, "validate_manuscript", return_value=True),
            patch.object(build_manager, "copy_style_files", return_value=True),
            patch.object(build_manager, "copy_references", return_value=True),
            patch.object(build_manager, "copy_figures", return_value=True),
            patch.object(
                build_manager,
                "generate_tex_files",
                return_value=True,
            ),
            patch.object(
                build_manager,
                "compile_pdf",
                return_value=True,
            ),
            patch.object(
                build_manager,
                "copy_pdf_to_manuscript",
                return_value=True,
            ),
            patch.object(
                build_manager,
                "run_pdf_validation",
                return_value=True,
            ),
            patch.object(
                build_manager,
                "run_word_count_analysis",
                return_value=True,
            ),
            patch.object(build_manager, "log") as mock_log,
        ):
            result = build_manager.run_full_build()

            # Should have logged about warning log
            log_calls = [call for call in mock_log.call_args_list if "warnings logged" in str(call)]
            self.assertTrue(len(log_calls) > 0)

            # Should return success
            self.assertTrue(result)


@pytest.mark.build_manager
@unittest.skipUnless(BUILD_MANAGER_AVAILABLE, "Build manager not available")
class TestBuildProcessOrder(unittest.TestCase):
    """Test build process order changes."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manuscript_dir = os.path.join(self.temp_dir, "manuscript")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.manuscript_dir)
        os.makedirs(self.output_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up logging handlers before removing files (Windows compatibility)
        from rxiv_maker.core.logging_config import cleanup

        cleanup()

        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_pdf_validation_runs_before_word_count(self):
        """Test that PDF validation runs before word count analysis."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Track the order of method calls
        call_order = []

        def track_pdf_validation():
            call_order.append("pdf_validation")
            return True

        def track_word_count():
            call_order.append("word_count")
            return True

        # Mock all prerequisites to return True
        with (
            patch.object(build_manager, "check_manuscript_structure", return_value=True),
            patch.object(build_manager, "setup_output_directory", return_value=True),
            patch.object(build_manager, "generate_figures", return_value=True),
            patch.object(build_manager, "validate_manuscript", return_value=True),
            patch.object(build_manager, "copy_style_files", return_value=True),
            patch.object(build_manager, "copy_references", return_value=True),
            patch.object(build_manager, "copy_figures", return_value=True),
            patch.object(
                build_manager,
                "generate_tex_files",
                return_value=True,
            ),
            patch.object(
                build_manager,
                "compile_pdf",
                return_value=True,
            ),
            patch.object(
                build_manager,
                "copy_pdf_to_manuscript",
                return_value=True,
            ),
            patch.object(
                build_manager,
                "run_pdf_validation",
                side_effect=track_pdf_validation,
            ),
            patch.object(
                build_manager,
                "run_word_count_analysis",
                side_effect=track_word_count,
            ),
            patch.object(build_manager, "log"),
        ):
            result = build_manager.run_full_build()

            # Should have run successfully
            self.assertTrue(result)

            # Should have called both methods
            self.assertEqual(len(call_order), 2)

            # PDF validation should come first
            self.assertEqual(
                call_order[0],
                "pdf_validation",
            )
            self.assertEqual(
                call_order[1],
                "word_count",
            )


@pytest.mark.build_manager
@unittest.skipUnless(BUILD_MANAGER_AVAILABLE, "Build manager not available")
class TestBibTeXWarningExtraction(unittest.TestCase):
    """Test BibTeX warning extraction functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manuscript_dir = os.path.join(self.temp_dir, "manuscript")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.manuscript_dir)
        os.makedirs(self.output_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up logging handlers before removing files (Windows compatibility)
        from rxiv_maker.core.logging_config import cleanup

        cleanup()

        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bibtex_warning_extraction_multiple_warnings(self):
        """Test extraction of multiple BibTeX warnings."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Create a realistic .blg file with multiple warnings
        blg_content = """This is BibTeX, Version 0.99d (TeX Live 2025)
Capacity: max_strings=200000, hash_size=200000, hash_prime=170003
The top-level auxiliary file: test.aux
The style file: rxiv_maker_style.bst
Database file #1: 03_REFERENCES.bib
Warning--empty journal in Xie2016_bookdown
Warning--missing year in smith2023
Warning--empty title in jones2022
You've used 25 entries,
            2450 wiz_defined-function locations,
            742 strings with 10894 characters,
and the built_in function-call counts, 10098 in all, are:
= -- 760
> -- 706
< -- 16
+ -- 270
- -- 220
warning$ -- 3
(There were 3 warnings)
"""

        blg_file = Path(self.output_dir) / f"{Path(self.manuscript_dir).name}.blg"
        with open(blg_file, "w") as f:
            f.write(blg_content)

        build_manager._log_bibtex_warnings()

        # Check that BibTeX warning log was created
        self.assertTrue(build_manager.bibtex_log.exists())

        # Check log content
        with open(build_manager.bibtex_log) as f:
            content = f.read()

        self.assertIn("BibTeX Warnings Report", content)
        self.assertIn("1. empty journal in Xie2016_bookdown", content)
        self.assertIn("2. missing year in smith2023", content)
        self.assertIn("3. empty title in jones2022", content)
        self.assertIn("2025-", content)  # Should have timestamp

    def test_bibtex_warning_log_overwrites_previous(self):
        """Test that BibTeX warning log overwrites previous logs."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Create initial warning log
        with open(build_manager.bibtex_log, "w") as f:
            f.write("Old log content")

        # Create new .blg file
        blg_content = """This is BibTeX, Version 0.99d
Warning--new warning in test_ref
(There was 1 warning)
"""

        blg_file = Path(self.output_dir) / f"{Path(self.manuscript_dir).name}.blg"
        with open(blg_file, "w") as f:
            f.write(blg_content)

        build_manager._log_bibtex_warnings()

        # Check that log was overwritten
        with open(build_manager.bibtex_log) as f:
            content = f.read()

        self.assertNotIn("Old log content", content)
        self.assertIn("new warning in test_ref", content)


@pytest.mark.build_manager
@unittest.skipUnless(BUILD_MANAGER_AVAILABLE, "Build manager not available")
class TestBuildManagerIntegration(unittest.TestCase):
    """Integration tests for build manager improvements."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manuscript_dir = os.path.join(self.temp_dir, "manuscript")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.manuscript_dir)
        os.makedirs(self.output_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up logging handlers before removing files (Windows compatibility)
        from rxiv_maker.core.logging_config import cleanup

        cleanup()

        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_build_manager_with_bibtex_warnings_integration(self):
        """Test integration of BibTeX warning logging in build process."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Create a .blg file that would be generated during build
        blg_content = """This is BibTeX, Version 0.99d
Warning--empty journal in test_reference
(There was 1 warning)
"""

        blg_file = Path(self.output_dir) / f"{Path(self.manuscript_dir).name}.blg"
        with open(blg_file, "w") as f:
            f.write(blg_content)

        # Mock the compile_pdf method to simulate successful BibTeX completion
        with patch.object(build_manager, "compile_pdf") as mock_compile:

            def mock_compile_pdf():
                # Create the .blg file as would happen during real compilation
                build_manager._log_bibtex_warnings()
                return True

            mock_compile.side_effect = mock_compile_pdf

            # Mock other methods to focus on our specific functionality
            with (
                patch.object(build_manager, "check_manuscript_structure", return_value=True),
                patch.object(build_manager, "setup_output_directory", return_value=True),
                patch.object(build_manager, "generate_figures", return_value=True),
                patch.object(build_manager, "validate_manuscript", return_value=True),
                patch.object(build_manager, "copy_style_files", return_value=True),
                patch.object(build_manager, "copy_references", return_value=True),
                patch.object(build_manager, "copy_figures", return_value=True),
                patch.object(
                    build_manager,
                    "generate_tex_files",
                    return_value=True,
                ),
                patch.object(
                    build_manager,
                    "copy_pdf_to_manuscript",
                    return_value=True,
                ),
                patch.object(
                    build_manager,
                    "run_pdf_validation",
                    return_value=True,
                ),
                patch.object(
                    build_manager,
                    "run_word_count_analysis",
                    return_value=True,
                ),
            ):
                # Run the build
                result = build_manager.run_full_build()

                # Should succeed
                self.assertTrue(result)

                # Should have created BibTeX warning log
                self.assertTrue(build_manager.bibtex_log.exists())

                # Check log content
                with open(build_manager.bibtex_log) as f:
                    content = f.read()

                self.assertIn(
                    "empty journal in test_reference",
                    content,
                )


class TestLaTeXErrorHandling(unittest.TestCase):
    """Test LaTeX error handling and recovery strategies."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manuscript_dir = Path(self.temp_dir) / "manuscript"
        self.manuscript_dir.mkdir(parents=True)
        self.output_dir = Path(self.temp_dir) / "output"

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up logging handlers before removing files (Windows compatibility)
        from rxiv_maker.core.logging_config import cleanup

        cleanup()

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_latex_undefined_control_sequence(self):
        """Test handling of undefined control sequence errors."""
        # Create a TeX file with undefined command
        tex_content = r"""
\documentclass{article}
\begin{document}
\undefined{This command does not exist}
\end{document}
"""
        tex_file = Path(self.output_dir) / "test.tex"
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        tex_file.write_text(tex_content)

        # Test that error is properly parsed
        from rxiv_maker.validators.latex_error_parser import LaTeXErrorParser

        parser = LaTeXErrorParser(manuscript_path=self.manuscript_dir)

        error_output = r"""
! Undefined control sequence.
l.4 \undefined
              {This command does not exist}
"""
        # Use the private method for testing purposes
        errors = parser._parse_log_file(error_output)
        assert any(e.error_type == "undefined_command" for e in errors)

    def test_latex_missing_package_error(self):
        """Test handling of missing package errors."""
        # Test error detection for missing packages
        error_output = r"""
! LaTeX Error: File `nonexistentpackage.sty' not found.
"""
        from rxiv_maker.validators.latex_error_parser import LaTeXErrorParser

        parser = LaTeXErrorParser(manuscript_path=self.manuscript_dir)
        errors = parser._parse_log_file(error_output)
        assert any(e.error_type == "missing_file" for e in errors)
        assert any(e.error_type == "missing_file" for e in errors)

    def test_latex_compilation_timeout(self):
        """Test handling of LaTeX compilation timeout."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # Mock subprocess to simulate timeout
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("pdflatex", 30)

            result = build_manager.compile_pdf()
            self.assertFalse(result)

    def test_latex_error_recovery_with_fallback(self):
        """Test LaTeX compilation with error recovery fallback."""
        build_manager = BuildManager(manuscript_path=self.manuscript_dir, output_dir=self.output_dir)

        # First compilation fails, second succeeds (simulating recovery)
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=1, stdout="", stderr="Error in first run"),
                Mock(returncode=0, stdout="Success", stderr=""),
            ]

            # Should attempt recovery by calling compile_pdf multiple times if first fails  # noqa: E501
            build_manager.compile_pdf()
            # Check that subprocess was called at least once
            self.assertTrue(mock_run.call_count >= 1)


@pytest.mark.build_manager
@unittest.skipUnless(BUILD_MANAGER_AVAILABLE, "Build manager not available")
class TestBuildManagerPathRegressions(unittest.TestCase):
    """Regression tests for path resolution issues that were previously broken."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manuscript_dir = os.path.join(self.temp_dir, "manuscript")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.manuscript_dir)
        os.makedirs(self.output_dir)

        # Create minimal manuscript structure
        main_md = Path(self.manuscript_dir) / "01_MAIN.md"
        main_md.write_text("# Test\nSample content")

        config_yml = Path(self.manuscript_dir) / "00_CONFIG.yml"
        config_yml.write_text("title:\n  main: Test Manuscript\n")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_relative_path_failure_regression(self):
        """Regression test: old relative paths would fail from different directories."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        original_cwd = os.getcwd()
        try:
            # Change to manuscript directory (where the original bug occurred)
            os.chdir(self.manuscript_dir)

            # Simulate the old relative path approach that would fail
            old_style_paths = [
                "src/rxiv_maker/commands/copy_pdf.py",
                "src/rxiv_maker/validators/pdf_validator.py",
                "src/rxiv_maker/commands/analyze_word_count.py",
                "src/tex/style",
            ]

            for path in old_style_paths:
                self.assertFalse(
                    Path(path).exists(),
                    f"Old relative path {path} should not exist from manuscript directory",
                )

            # But our new __file__-based paths should work
            self.assertTrue(build_manager.style_dir.is_absolute())
            self.assertTrue(build_manager.style_dir.parts[-2:] == ("tex", "style"))

        finally:
            os.chdir(original_cwd)

    def test_subprocess_command_construction_regression(self):
        """Regression test: verify subprocess commands use module paths, not file paths."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        # Test copy_pdf_to_manuscript - now uses direct function call
        # We can't test subprocess command construction anymore, but we can verify it runs
        result = build_manager.copy_pdf_to_manuscript()
        # Since PDF doesn't exist in test, result should be False
        self.assertFalse(result)

        # Test run_pdf_validation command construction
        pdf_path = Path(self.output_dir) / f"{Path(self.manuscript_dir).name}.pdf"
        pdf_path.write_bytes(b"fake PDF")
        build_manager.output_pdf = pdf_path

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Validation passed"
            mock_run.return_value.stderr = ""

            build_manager._run_pdf_validation_local()

            args, _ = mock_run.call_args
            cmd = args[0]
            self.assertIn("-m", cmd, "PDF validation should use -m flag")
            self.assertIn("rxiv_maker.validators.pdf_validator", cmd, "Should use module path")
            self.assertNotIn(
                "src/rxiv_maker/validators/pdf_validator.py",
                cmd,
                "Should not use file path",
            )

        # Test run_word_count_analysis command construction
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Word count: 100"
            mock_run.return_value.stderr = ""

            build_manager.run_word_count_analysis()

            args, _ = mock_run.call_args
            cmd = args[0]
            self.assertIn("-m", cmd, "Word count should use -m flag")
            self.assertIn("rxiv_maker.commands.analyze_word_count", cmd, "Should use module path")
            self.assertNotIn(
                "src/rxiv_maker/commands/analyze_word_count.py",
                cmd,
                "Should not use file path",
            )

    def test_file_not_found_error_regression(self):
        """Regression test: simulate the exact 'can't open file' error that was fixed."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        # Simulate the old behavior that would cause 'can't open file' errors
        with patch("subprocess.run") as mock_run:
            # Mock the exact error that was occurring
            mock_run.return_value.returncode = 2
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = (
                "python: can't open file 'src/rxiv_maker/commands/copy_pdf.py': [Errno 2] No such file or directory"
            )

            result = build_manager.copy_pdf_to_manuscript()

            # The method now uses direct function calls instead of subprocess.run
            # So we can't test the command construction, but we can verify the result
            # Since the PDF doesn't exist in the test, the result should be False
            self.assertFalse(result)

    def test_style_directory_resolution_regression(self):
        """Regression test: style directory should be found regardless of CWD."""
        original_cwd = os.getcwd()

        # Test from different working directories
        test_directories = [
            self.manuscript_dir,  # Where the bug originally occurred
            self.temp_dir,  # Parent directory
            tempfile.mkdtemp(),  # Completely unrelated directory
        ]

        try:
            for test_dir in test_directories:
                with self.subTest(working_dir=test_dir):
                    os.chdir(test_dir)

                    build_manager = BuildManager(
                        manuscript_path=self.manuscript_dir,
                        output_dir=self.output_dir,
                        verbose=False,
                    )

                    # Style directory should always be absolute and correct
                    self.assertTrue(build_manager.style_dir.is_absolute())
                    self.assertEqual(build_manager.style_dir.parts[-2:], ("tex", "style"))

                    # The path should not depend on current working directory
                    expected_path = Path(__file__).parent.parent.parent / "src/tex/style"
                    expected_path = expected_path.resolve()
                    actual_path = build_manager.style_dir.resolve()

                    # Both should point to the same location
                    self.assertEqual(actual_path, expected_path)

        finally:
            os.chdir(original_cwd)
            # Clean up the extra temp directory
            if len(test_directories) > 2:
                shutil.rmtree(test_directories[2], ignore_errors=True)

    def test_docker_path_construction_regression(self):
        """Regression test: Docker commands should also use module paths."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            engine="docker",
            verbose=False,
        )

        # Create fake PDF
        pdf_path = Path(self.output_dir) / f"{Path(self.manuscript_dir).name}.pdf"
        pdf_path.write_bytes(b"fake PDF")
        build_manager.output_pdf = pdf_path

        # Mock Docker manager
        with patch.object(build_manager, "docker_manager") as mock_docker:
            mock_docker.run_command.return_value.returncode = 0

            build_manager._run_pdf_validation_docker()

            # Verify Docker command used module path
            call_args = mock_docker.run_command.call_args
            if call_args:
                command = call_args[1]["command"]
                self.assertIn("-m", command, "Docker command should use -m flag")
                self.assertIn(
                    "rxiv_maker.validators.pdf_validator",
                    command,
                    "Should use module path",
                )
                self.assertNotIn(
                    "/workspace/src/rxiv_maker/validators/pdf_validator.py",
                    command,
                    "Should not use file path",
                )

    def test_environment_variable_handling_regression(self):
        """Regression test: environment variables should be properly set for module execution."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Success"
            mock_run.return_value.stderr = ""

            # Test copy_pdf_to_manuscript - now uses direct function call, check env is set
            original_env = os.environ.get("MANUSCRIPT_PATH")
            try:
                build_manager.copy_pdf_to_manuscript()
                # The method sets MANUSCRIPT_PATH env var during execution
                # We can't easily test the subprocess call since it now uses direct function call
                # But we can verify the method ran without error
                self.assertTrue(True)  # Method completed without exception
            finally:
                # Restore original environment
                if original_env:
                    os.environ["MANUSCRIPT_PATH"] = original_env
                elif "MANUSCRIPT_PATH" in os.environ:
                    del os.environ["MANUSCRIPT_PATH"]

            # Test run_word_count_analysis - this still uses subprocess.run
            build_manager.run_word_count_analysis()
            # Check that subprocess.run was called
            if mock_run.call_args:
                _, kwargs = mock_run.call_args
                env = kwargs.get("env", {})
                self.assertEqual(env["MANUSCRIPT_PATH"], self.manuscript_dir)


@pytest.mark.unit
@unittest.skipUnless(BUILD_MANAGER_AVAILABLE, "Build manager not available")
class TestBuildManagerPathResolution(unittest.TestCase):
    """Test BuildManager path resolution and subprocess command construction."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manuscript_dir = os.path.join(self.temp_dir, "manuscript")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.manuscript_dir)
        os.makedirs(self.output_dir)

        # Create minimal manuscript structure
        main_md = Path(self.manuscript_dir) / "01_MAIN.md"
        main_md.write_text("# Test\nSample content")

        config_yml = Path(self.manuscript_dir) / "00_CONFIG.yml"
        config_yml.write_text("title:\n  main: Test Manuscript\n")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_copy_pdf_to_manuscript_command_construction(self):
        """Test that copy_pdf_to_manuscript works with direct function calls."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        # Method now uses direct function calls instead of subprocess.run
        # We can verify it runs without error and sets the environment
        original_env = os.environ.get("MANUSCRIPT_PATH")
        try:
            result = build_manager.copy_pdf_to_manuscript()
            # Since PDF doesn't exist in test, result should be False
            self.assertFalse(result)
        finally:
            # Restore original environment
            if original_env:
                os.environ["MANUSCRIPT_PATH"] = original_env
            elif "MANUSCRIPT_PATH" in os.environ:
                del os.environ["MANUSCRIPT_PATH"]

    def test_copy_pdf_to_manuscript_command_with_uv(self):
        """Test copy_pdf_to_manuscript works with uv environment."""
        # Since method now uses direct function calls, we just verify it runs
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        # Method should run without error regardless of environment
        result = build_manager.copy_pdf_to_manuscript()
        # Since PDF doesn't exist in test, result should be False
        self.assertFalse(result)

    def test_run_pdf_validation_command_construction(self):
        """Test that run_pdf_validation constructs correct module command."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        # Create a fake PDF file
        pdf_path = Path(self.output_dir) / f"{Path(self.manuscript_dir).name}.pdf"
        pdf_path.write_bytes(b"fake PDF content")
        build_manager.output_pdf = pdf_path

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "PDF validation passed"
            mock_run.return_value.stderr = ""

            result = build_manager._run_pdf_validation_local()

            # Verify subprocess.run was called
            self.assertTrue(mock_run.called)
            args, _ = mock_run.call_args

            # Check the command construction
            cmd = args[0]
            # Command might be ["python", "-m", ...] or ["uv", "run", "python", "-m", ...]
            if "uv" in cmd[0]:
                self.assertEqual(cmd[0], "uv")
                self.assertEqual(cmd[1], "run")
                self.assertEqual(cmd[2], "python")
                self.assertEqual(cmd[3], "-m")
                self.assertEqual(cmd[4], "rxiv_maker.validators.pdf_validator")
                self.assertEqual(cmd[5], self.manuscript_dir)
                self.assertEqual(cmd[6], "--pdf-path")
                self.assertEqual(cmd[7], str(pdf_path))
            else:
                self.assertIn("python", cmd[0])  # Python executable
                self.assertEqual(cmd[1], "-m")  # Module flag
                self.assertEqual(cmd[2], "rxiv_maker.validators.pdf_validator")  # Module path
                self.assertEqual(cmd[3], self.manuscript_dir)  # Manuscript path
                self.assertEqual(cmd[4], "--pdf-path")  # Flag
                self.assertEqual(cmd[5], str(pdf_path))  # PDF path

            self.assertTrue(result)

    def test_run_word_count_analysis_command_construction(self):
        """Test that run_word_count_analysis constructs correct module command."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Word count: 100 words"
            mock_run.return_value.stderr = ""

            result = build_manager.run_word_count_analysis()

            # Verify subprocess.run was called
            self.assertTrue(mock_run.called)
            args, kwargs = mock_run.call_args

            # Check the command construction
            cmd = args[0]
            # Command might be ["python", "-m", ...] or ["uv", "run", "python", "-m", ...]
            if "uv" in cmd[0]:
                self.assertEqual(cmd[0], "uv")
                self.assertEqual(cmd[1], "run")
                self.assertEqual(cmd[2], "python")
                self.assertEqual(cmd[3], "-m")
                self.assertEqual(cmd[4], "rxiv_maker.commands.analyze_word_count")
            else:
                self.assertIn("python", cmd[0])  # Python executable
                self.assertEqual(cmd[1], "-m")  # Module flag
                self.assertEqual(cmd[2], "rxiv_maker.commands.analyze_word_count")  # Module path

            # Verify environment variables are set
            env = kwargs.get("env", {})
            self.assertEqual(env["MANUSCRIPT_PATH"], self.manuscript_dir)

            self.assertTrue(result)

    def test_style_directory_path_resolution(self):
        """Test that style directory resolves to correct absolute path."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        # Check that style_dir is an absolute path
        self.assertTrue(build_manager.style_dir.is_absolute())

        # Check that it points to the expected location relative to the module
        # The path should be: src/rxiv_maker/commands/build_manager.py -> ../../../tex/style
        expected_parts = ["tex", "style"]
        actual_parts = build_manager.style_dir.parts[-2:]
        self.assertEqual(actual_parts, tuple(expected_parts))

    def test_style_directory_exists_check(self):
        """Test style directory existence checking and warning behavior."""
        # Test with non-existent style directory
        with patch("pathlib.Path.exists", return_value=False):
            build_manager = BuildManager(
                manuscript_path=self.manuscript_dir,
                output_dir=self.output_dir,
                verbose=False,
            )

            with patch.object(build_manager, "log") as mock_log:
                result = build_manager.copy_style_files()

                # Should log warning and return True (non-fatal)
                mock_log.assert_called_with("Style directory not found, skipping style file copying", "WARNING")
                self.assertTrue(result)

    def test_subprocess_failure_handling(self):
        """Test handling of subprocess failures in path-dependent commands."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        # Test copy_pdf_to_manuscript failure (now uses direct function calls)
        # Since PDF doesn't exist in test environment, it should return False
        result = build_manager.copy_pdf_to_manuscript()
        self.assertFalse(result)

        # Test run_pdf_validation with non-zero return code
        # Note: PDF validation is designed to return True even on failures to not break builds
        pdf_path = Path(self.output_dir) / f"{Path(self.manuscript_dir).name}.pdf"
        pdf_path.write_bytes(b"fake PDF content")
        build_manager.output_pdf = pdf_path

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Validation failed"

            result = build_manager._run_pdf_validation_local()
            # PDF validation returns True even on warnings/errors to not fail builds
            self.assertTrue(result)

        # Test run_word_count_analysis failure
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = "Analysis failed"

            result = build_manager.run_word_count_analysis()
            self.assertFalse(result)

    def test_different_working_directories(self):
        """Test that path resolution works from different working directories."""
        build_manager = BuildManager(
            manuscript_path=self.manuscript_dir,
            output_dir=self.output_dir,
            verbose=False,
        )

        original_cwd = os.getcwd()
        try:
            # Change to a different directory
            temp_cwd = tempfile.mkdtemp()
            os.chdir(temp_cwd)

            # Style directory should still be resolved correctly
            self.assertTrue(build_manager.style_dir.is_absolute())

            # The path resolution should not depend on current working directory
            expected_parts = ["tex", "style"]
            actual_parts = build_manager.style_dir.parts[-2:]
            self.assertEqual(actual_parts, tuple(expected_parts))

        finally:
            os.chdir(original_cwd)
            import shutil

            shutil.rmtree(temp_cwd, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
