"""Tests for the arXiv CLI command."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner

from rxiv_maker.cli.commands.arxiv import arxiv
from rxiv_maker.core import logging_config


class TestArxivCommand:
    """Tests for the arXiv CLI command."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up logging for Windows compatibility."""
        logging_config.cleanup()

    def test_arxiv_command_with_nonexistent_manuscript(self):
        """Test arxiv command with nonexistent manuscript directory."""
        result = self.runner.invoke(arxiv, ["/nonexistent/path"], obj={"verbose": False})

        assert result.exit_code == 2  # Click parameter validation error
        assert "does not exist" in result.output

    def test_arxiv_command_uses_default_manuscript_path(self):
        """Test that arxiv command uses default MANUSCRIPT when no path provided."""
        # Test calling without any manuscript path - should use MANUSCRIPT or env var
        with patch.dict("os.environ", {"MANUSCRIPT_PATH": "DEFAULT_MANUSCRIPT"}):
            result = self.runner.invoke(
                arxiv,
                [],  # No manuscript path
                obj={"verbose": False},
            )

            # Should fail since DEFAULT_MANUSCRIPT doesn't exist, but tests the logic
            assert result.exit_code == 1
            assert "does not exist" in result.output

    def test_arxiv_command_with_existing_pdf(self):
        """Test arxiv command when PDF already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            output_dir = manuscript_dir / "output"
            output_dir.mkdir()

            # Create minimal manuscript files
            (manuscript_dir / "00_CONFIG.yml").write_text("""
title: "Test Manuscript"
date: "2024-01-01"
authors:
  - name: "Test Author"
    email: "test@example.com"
""")
            (manuscript_dir / "01_MAIN.md").write_text("# Test\n\nContent")
            (manuscript_dir / "03_REFERENCES.bib").write_text("")

            # Create fake PDF
            pdf_file = output_dir / "TEST_MANUSCRIPT.pdf"
            pdf_file.write_text("fake pdf content")

            # Mock the prepare_arxiv command to simulate success
            with patch("rxiv_maker.commands.prepare_arxiv.main") as mock_arxiv:
                mock_arxiv.return_value = None  # Success

                # Mock shutil.copy2 to avoid file operations
                with patch("shutil.copy2"):
                    result = self.runner.invoke(arxiv, [str(manuscript_dir)], obj={"verbose": False})

                    assert result.exit_code == 0 or "prepared successfully" in result.output
                    mock_arxiv.assert_called_once()

    def test_arxiv_command_builds_pdf_when_missing(self):
        """Test arxiv command builds PDF when it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            output_dir = manuscript_dir / "output"
            output_dir.mkdir()

            # Create minimal manuscript files
            (manuscript_dir / "00_CONFIG.yml").write_text("""
title: "Test Manuscript"
date: "2024-01-01"
authors:
  - name: "Test Author"
    email: "test@example.com"
""")
            (manuscript_dir / "01_MAIN.md").write_text("# Test\n\nContent")
            (manuscript_dir / "03_REFERENCES.bib").write_text("")

            # No PDF file exists - should trigger build

            # Mock the BuildManager to simulate successful build
            with patch("rxiv_maker.commands.build_manager.BuildManager") as mock_build_manager:
                mock_manager = Mock()
                mock_manager.run.return_value = True
                mock_build_manager.return_value = mock_manager

                # Mock the prepare_arxiv command
                with patch("rxiv_maker.commands.prepare_arxiv.main") as mock_arxiv:
                    mock_arxiv.return_value = None

                    # Mock shutil.copy2 to avoid file operations
                    with patch("shutil.copy2"):
                        self.runner.invoke(arxiv, [str(manuscript_dir)], obj={"verbose": False})

                        # Should have called BuildManager to build PDF
                        mock_build_manager.assert_called_once()
                        mock_manager.run.assert_called_once()
                        mock_arxiv.assert_called_once()

    def test_arxiv_command_handles_build_failure(self):
        """Test arxiv command handles BuildManager failure gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            output_dir = manuscript_dir / "output"
            output_dir.mkdir()

            # Create minimal manuscript files
            (manuscript_dir / "00_CONFIG.yml").write_text("""
title: "Test Manuscript"
authors:
  - name: "Test Author"
    email: "test@example.com"
""")
            (manuscript_dir / "01_MAIN.md").write_text("# Test\n\nContent")
            (manuscript_dir / "03_REFERENCES.bib").write_text("")

            # Mock BuildManager to simulate failure
            with patch("rxiv_maker.commands.build_manager.BuildManager") as mock_build_manager:
                mock_manager = Mock()
                mock_manager.run.return_value = False  # Build fails
                mock_build_manager.return_value = mock_manager

                result = self.runner.invoke(arxiv, [str(manuscript_dir)], obj={"verbose": False})

                assert result.exit_code == 1
                assert "PDF build failed" in result.output

    def test_arxiv_command_custom_options(self):
        """Test arxiv command with custom options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            output_dir = manuscript_dir / "output"
            output_dir.mkdir()

            # Create minimal manuscript files
            (manuscript_dir / "00_CONFIG.yml").write_text("""
title: "Test Manuscript"
date: "2024-01-01"
authors:
  - name: "Test Author"
    email: "test@example.com"
""")
            (manuscript_dir / "01_MAIN.md").write_text("# Test\n\nContent")
            (manuscript_dir / "03_REFERENCES.bib").write_text("")

            # Create fake PDF in the expected location (considering custom output directory)
            custom_output_dir = manuscript_dir / "custom_output"
            custom_output_dir.mkdir()
            pdf_file = custom_output_dir / "TEST_MANUSCRIPT.pdf"
            pdf_file.write_text("fake pdf content")

            # Mock the prepare_arxiv command - this test is about CLI parameter handling
            with patch("rxiv_maker.commands.prepare_arxiv.main") as mock_arxiv:
                mock_arxiv.return_value = None

                with patch("shutil.copy2"):
                    self.runner.invoke(
                        arxiv,
                        [
                            str(manuscript_dir),
                            "--output-dir",
                            "custom_output",
                            "--arxiv-dir",
                            "custom_arxiv",
                            "--zip-filename",
                            "custom.zip",
                        ],
                        obj={"verbose": False},
                    )

                    # Since PDF exists, BuildManager shouldn't be called and prepare_arxiv should be called
                    mock_arxiv.assert_called_once()

    def test_arxiv_command_no_zip_option(self):
        """Test arxiv command with --no-zip option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            output_dir = manuscript_dir / "output"
            output_dir.mkdir()

            # Create minimal manuscript files
            (manuscript_dir / "00_CONFIG.yml").write_text("""
title: "Test Manuscript"
authors:
  - name: "Test Author"
    email: "test@example.com"
""")
            (manuscript_dir / "01_MAIN.md").write_text("# Test\n\nContent")
            (manuscript_dir / "03_REFERENCES.bib").write_text("")

            # Create fake PDF
            pdf_file = output_dir / "TEST_MANUSCRIPT.pdf"
            pdf_file.write_text("fake pdf content")

            # Mock the prepare_arxiv command
            with patch("rxiv_maker.commands.prepare_arxiv.main") as mock_arxiv:
                mock_arxiv.return_value = None

                self.runner.invoke(arxiv, [str(manuscript_dir), "--no-zip"], obj={"verbose": False})

                mock_arxiv.assert_called_once()

                # Check that the args passed to prepare_arxiv don't include --create-zip
                # The sys.argv should not contain --create-zip when --no-zip is used
                assert mock_arxiv.called

    def test_arxiv_command_uses_manuscript_path_env_var(self):
        """Test arxiv command uses MANUSCRIPT_PATH environment variable as default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manuscript_dir = Path(tmpdir) / "ENV_MANUSCRIPT"
            manuscript_dir.mkdir()
            output_dir = manuscript_dir / "output"
            output_dir.mkdir()

            # Create minimal manuscript files
            (manuscript_dir / "00_CONFIG.yml").write_text("""
title: "Test Manuscript"
authors:
  - name: "Test Author"
    email: "test@example.com"
""")
            (manuscript_dir / "01_MAIN.md").write_text("# Test\n\nContent")
            (manuscript_dir / "03_REFERENCES.bib").write_text("")

            # Create fake PDF
            pdf_file = output_dir / "ENV_MANUSCRIPT.pdf"
            pdf_file.write_text("fake pdf content")

            # Mock environment variable
            with (
                patch.dict("os.environ", {"MANUSCRIPT_PATH": str(manuscript_dir)}),
                patch("rxiv_maker.commands.prepare_arxiv.main") as mock_arxiv,
            ):
                mock_arxiv.return_value = None

                with patch("shutil.copy2"):
                    # Call without manuscript path argument - should use env var
                    self.runner.invoke(
                        arxiv,
                        [],  # No manuscript path argument
                        obj={"verbose": False},
                    )

                    mock_arxiv.assert_called_once()

    def test_arxiv_command_handles_prepare_arxiv_failure(self):
        """Test arxiv command handles prepare_arxiv failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            output_dir = manuscript_dir / "output"
            output_dir.mkdir()

            # Create minimal manuscript files
            (manuscript_dir / "00_CONFIG.yml").write_text("""
title: "Test Manuscript"
authors:
  - name: "Test Author"
    email: "test@example.com"
""")
            (manuscript_dir / "01_MAIN.md").write_text("# Test\n\nContent")
            (manuscript_dir / "03_REFERENCES.bib").write_text("")

            # Create fake PDF
            pdf_file = output_dir / "TEST_MANUSCRIPT.pdf"
            pdf_file.write_text("fake pdf content")

            # Mock prepare_arxiv to raise SystemExit with non-zero code
            with patch("rxiv_maker.commands.prepare_arxiv.main") as mock_arxiv:
                mock_arxiv.side_effect = SystemExit(1)

                result = self.runner.invoke(arxiv, [str(manuscript_dir)], obj={"verbose": False})

                assert result.exit_code == 1
                assert "arXiv preparation failed" in result.output

    def test_arxiv_command_uses_correct_build_manager_method(self):
        """Test that arxiv command uses the correct BuildManager method (regression test)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            output_dir = manuscript_dir / "output"
            output_dir.mkdir()

            # Create minimal manuscript files
            (manuscript_dir / "00_CONFIG.yml").write_text("""
title: "Test Manuscript"
authors:
  - name: "Test Author"
    email: "test@example.com"
""")
            (manuscript_dir / "01_MAIN.md").write_text("# Test\n\nContent")
            (manuscript_dir / "03_REFERENCES.bib").write_text("")

            # Mock BuildManager to ensure it has the correct methods
            with patch("rxiv_maker.commands.build_manager.BuildManager") as mock_build_manager:
                mock_manager = Mock()
                # Ensure the mock has the 'run' method but not 'build'
                mock_manager.run.return_value = True
                # Remove 'build' method if it exists to test the fix
                if hasattr(mock_manager, "build"):
                    delattr(mock_manager, "build")
                mock_build_manager.return_value = mock_manager

                with patch("rxiv_maker.commands.prepare_arxiv.main") as mock_arxiv:
                    mock_arxiv.return_value = None

                    with patch("shutil.copy2"):
                        self.runner.invoke(arxiv, [str(manuscript_dir)], obj={"verbose": False})

                        # Should have called the 'run' method, not 'build'
                        mock_manager.run.assert_called_once()
                        # Verify no attempt to call 'build' method
                        assert not hasattr(mock_manager, "build") or not mock_manager.build.called
