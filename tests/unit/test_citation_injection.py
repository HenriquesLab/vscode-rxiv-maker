"""Tests for citation injection functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from rxiv_maker.utils.citation_utils import inject_rxiv_citation


class TestCitationInjection:
    """Test the citation injection functionality."""

    def test_inject_rxiv_citation_when_enabled(self):
        """Test that citation is injected when acknowledge_rxiv_maker is True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up test environment
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            
            bib_file = manuscript_dir / "03_REFERENCES.bib"
            bib_file.write_text("% Initial bibliography content\n")
            
            yaml_metadata = {
                "acknowledge_rxiv_maker": True,
                "bibliography": "03_REFERENCES.bib"  
            }
            
            # Set environment variable
            with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                    inject_rxiv_citation(yaml_metadata)
            
            # Check that citation was added
            bib_content = bib_file.read_text()
            assert "saraiva2025rxivmaker" in bib_content
            assert "Rxiv-Maker: An Automated Template Engine for Streamlined Scientific Publications" in bib_content
            assert "2508.00836" in bib_content

    def test_inject_rxiv_citation_when_disabled(self):
        """Test that citation is not injected when acknowledge_rxiv_maker is False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up test environment
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            
            bib_file = manuscript_dir / "03_REFERENCES.bib"
            original_content = "% Initial bibliography content\n"
            bib_file.write_text(original_content)
            
            yaml_metadata = {
                "acknowledge_rxiv_maker": False,
                "bibliography": "03_REFERENCES.bib"  
            }
            
            # Set environment variable
            with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                    inject_rxiv_citation(yaml_metadata)
            
            # Check that citation was NOT added
            bib_content = bib_file.read_text()
            assert bib_content == original_content
            assert "saraiva2025rxivmaker" not in bib_content

    def test_inject_rxiv_citation_when_not_specified(self):
        """Test that citation is not injected when acknowledge_rxiv_maker is not specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up test environment
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            
            bib_file = manuscript_dir / "03_REFERENCES.bib"
            original_content = "% Initial bibliography content\n"
            bib_file.write_text(original_content)
            
            yaml_metadata = {
                "bibliography": "03_REFERENCES.bib"  
            }
            
            # Set environment variable
            with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                    inject_rxiv_citation(yaml_metadata)
            
            # Check that citation was NOT added
            bib_content = bib_file.read_text()
            assert bib_content == original_content
            assert "saraiva2025rxivmaker" not in bib_content

    def test_inject_rxiv_citation_already_exists(self):
        """Test that citation is not duplicated if it already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up test environment
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            
            bib_file = manuscript_dir / "03_REFERENCES.bib"
            existing_content = """% Initial bibliography content

@misc{saraiva2025rxivmaker,
  author       = {Existing citation},
  title        = {Already there},
  journal      = {Test},
  year         = 2025,
}
"""
            bib_file.write_text(existing_content)
            
            yaml_metadata = {
                "acknowledge_rxiv_maker": True,
                "bibliography": "03_REFERENCES.bib"  
            }
            
            # Capture print output
            with patch("builtins.print") as mock_print:
                with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                    with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                        inject_rxiv_citation(yaml_metadata)
            
            # Check that citation was NOT duplicated
            bib_content = bib_file.read_text()
            assert bib_content == existing_content
            # Should have printed that citation already exists
            mock_print.assert_called_with("Rxiv-Maker citation already exists in bibliography")

    def test_inject_rxiv_citation_creates_missing_bib_file(self):
        """Test that bibliography file is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up test environment
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            
            yaml_metadata = {
                "acknowledge_rxiv_maker": True,
                "bibliography": "03_REFERENCES.bib"  
            }
            
            # Capture print output
            with patch("builtins.print") as mock_print:
                with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                    with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                        inject_rxiv_citation(yaml_metadata)
            
            # Check that file was created and citation was added
            bib_file = manuscript_dir / "03_REFERENCES.bib"
            assert bib_file.exists()
            
            bib_content = bib_file.read_text()
            assert "saraiva2025rxivmaker" in bib_content
            assert "Rxiv-Maker: An Automated Template Engine for Streamlined Scientific Publications" in bib_content
            
            # Should have printed warning about creating new file
            assert any(
                "Bibliography file" in str(call) and "not found. Creating new file" in str(call)
                for call in mock_print.call_args_list
            )

    def test_inject_rxiv_citation_custom_bibliography_name(self):
        """Test that citation works with custom bibliography filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up test environment
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            
            bib_file = manuscript_dir / "custom_refs.bib"
            bib_file.write_text("% Initial bibliography content\n")
            
            yaml_metadata = {
                "acknowledge_rxiv_maker": True,
                "bibliography": "custom_refs.bib"  
            }
            
            # Set environment variable
            with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                    inject_rxiv_citation(yaml_metadata)
            
            # Check that citation was added to the custom file
            bib_content = bib_file.read_text()
            assert "saraiva2025rxivmaker" in bib_content
            assert "Rxiv-Maker: An Automated Template Engine for Streamlined Scientific Publications" in bib_content

    def test_inject_rxiv_citation_adds_bib_extension(self):
        """Test that .bib extension is added if not present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up test environment
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            
            bib_file = manuscript_dir / "custom_refs.bib"
            bib_file.write_text("% Initial bibliography content\n")
            
            yaml_metadata = {
                "acknowledge_rxiv_maker": True,
                "bibliography": "custom_refs"  # No .bib extension
            }
            
            # Set environment variable
            with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                    inject_rxiv_citation(yaml_metadata)
            
            # Check that citation was added
            bib_content = bib_file.read_text()
            assert "saraiva2025rxivmaker" in bib_content

    def test_inject_rxiv_citation_preserves_newlines(self):
        """Test that citation injection preserves file formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set up test environment
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
            manuscript_dir.mkdir()
            
            bib_file = manuscript_dir / "03_REFERENCES.bib"
            # Content without newline at end
            original_content = "% Initial bibliography content"
            bib_file.write_text(original_content)
            
            yaml_metadata = {
                "acknowledge_rxiv_maker": True,
                "bibliography": "03_REFERENCES.bib"  
            }
            
            # Set environment variable
            with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                    inject_rxiv_citation(yaml_metadata)
            
            # Check that newline was added properly
            bib_content = bib_file.read_text()
            assert bib_content.startswith(original_content + "\n")
            assert "saraiva2025rxivmaker" in bib_content

    def test_inject_rxiv_citation_handles_errors_gracefully(self):
        """Test that citation injection handles errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"  
            manuscript_dir.mkdir()
            
            yaml_metadata = {
                "acknowledge_rxiv_maker": True,
                "bibliography": "03_REFERENCES.bib"  
            }
            
            # Mock file operations to raise exceptions
            with patch("builtins.open", side_effect=PermissionError("Access denied")):
                with patch("builtins.print") as mock_print:
                    with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                        with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                            # Should not raise exception
                            inject_rxiv_citation(yaml_metadata)
                    
                    # Should have printed error message
                    assert any(
                        "Error reading bibliography file" in str(call)
                        for call in mock_print.call_args_list
                    )


class TestCitationInjectionIntegration:
    """Test citation injection in the context of the full build pipeline."""

    def test_citation_injection_in_generate_preprint(self):
        """Test that citation injection is called during generate_preprint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Add current directory to PYTHONPATH for imports to work
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
            
            try:
                # Set up test environment
                manuscript_dir = Path(tmpdir) / "TEST_MANUSCRIPT"
                manuscript_dir.mkdir()
                
                # Create required files
                config_file = manuscript_dir / "00_CONFIG.yml"
                config_file.write_text("""
title:
  long: "Test Paper"
  short: "Test"
authors:
  - name: "Test Author"
    affiliation: "Test University"
acknowledge_rxiv_maker: true
bibliography: "03_REFERENCES.bib"
""")
                
                main_file = manuscript_dir / "01_MAIN.md"
                main_file.write_text("""---
title:
  long: "Test Paper"
  short: "Test"
authors:
  - name: "Test Author"
    affiliation: "Test University"
acknowledge_rxiv_maker: true
bibliography: "03_REFERENCES.bib"
---

# Abstract

This is a test abstract.

# Main Content

This is the main content.
""")
                
                bib_file = manuscript_dir / "03_REFERENCES.bib"
                bib_file.write_text("% Initial bibliography content\n")
                
                # Mock the template path to avoid file not found errors
                with patch("rxiv_maker.processors.template_processor.get_template_path") as mock_template:
                    # Create a minimal template file
                    template_content = """
\\documentclass{article}
\\begin{document}
<PY-RPL:MAIN-CONTENT>
\\end{document}
"""
                    template_file = Path(tmpdir) / "template.tex"
                    template_file.write_text(template_content)
                    mock_template.return_value = template_file
                    
                    # Import the function to test
                    from rxiv_maker.commands.generate_preprint import generate_preprint
                    from rxiv_maker.processors.yaml_processor import extract_yaml_metadata
                    
                    # Set up environment
                    with patch.dict(os.environ, {"MANUSCRIPT_PATH": "TEST_MANUSCRIPT"}):
                        with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                            # Extract metadata like the real build process does
                            yaml_metadata = extract_yaml_metadata(str(main_file))
                            
                            # Generate preprint (this should call inject_rxiv_citation internally)
                            output_dir = manuscript_dir / "output"
                            output_dir.mkdir()
                            
                            result = generate_preprint(str(output_dir), yaml_metadata)
                            
                            # Check that result is successful
                            assert result is not None
                            
                            # Check that citation was injected
                            bib_content = bib_file.read_text()
                            assert "saraiva2025rxivmaker" in bib_content
                            assert "Rxiv-Maker: An Automated Template Engine for Streamlined Scientific Publications" in bib_content
            finally:
                # Clean up sys.path
                if str(Path(__file__).parent.parent.parent / "src") in sys.path:
                    sys.path.remove(str(Path(__file__).parent.parent.parent / "src"))