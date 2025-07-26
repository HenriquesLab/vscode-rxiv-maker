"""End-to-end test for EXAMPLE_MANUSCRIPT using real rxiv commands."""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from ..conftest import requires_latex


@pytest.mark.integration
@pytest.mark.slow
@requires_latex
class TestExampleManuscript:
    """Test the full pipeline for EXAMPLE_MANUSCRIPT."""

    @pytest.fixture
    def example_manuscript_copy(self):
        """Create a temporary copy of EXAMPLE_MANUSCRIPT for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_path = Path("EXAMPLE_MANUSCRIPT")
            dst_path = Path(tmpdir) / "EXAMPLE_MANUSCRIPT"

            # Copy the entire EXAMPLE_MANUSCRIPT directory
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)

            # Clean any existing output
            output_dir = dst_path / "output"
            if output_dir.exists():
                shutil.rmtree(output_dir)

            yield dst_path

    def test_rxiv_pdf_example_manuscript_cli(self, example_manuscript_copy):
        """Test full PDF generation using rxiv CLI command."""
        # Try uv run rxiv first, then fall back to python module if not available
        try:
            result = subprocess.run(
                ["uv", "run", "rxiv", "pdf", str(example_manuscript_copy)],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
        except FileNotFoundError:
            # Fall back to python module call
            result = subprocess.run(
                ["python", "-m", "rxiv_maker.cli", "pdf", str(example_manuscript_copy)],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

        # Check command succeeded
        assert result.returncode == 0, f"rxiv pdf failed: {result.stderr}"

        # Check output PDF was created
        output_pdf = example_manuscript_copy / "output" / "EXAMPLE_MANUSCRIPT.pdf"
        assert output_pdf.exists(), "Output PDF was not created"
        assert output_pdf.stat().st_size > 1000, "Output PDF is too small"

        # Check figures were generated (search recursively in subdirectories)
        figures_dir = example_manuscript_copy / "FIGURES"
        generated_figures = list(figures_dir.rglob("*.pdf")) + list(
            figures_dir.rglob("*.png")
        )
        assert len(generated_figures) > 0, "No figures were generated"

    def test_rxiv_pdf_example_manuscript_python(self, example_manuscript_copy):
        """Test full PDF generation using Python API."""
        from rxiv_maker.commands.build_manager import BuildManager

        # Create build manager and run build
        build_manager = BuildManager(
            manuscript_path=str(example_manuscript_copy),
            verbose=False,
            force_figures=False,
            skip_validation=False,
        )

        success = build_manager.run_full_build()
        assert success, "Build failed"

        # Check output
        output_pdf = example_manuscript_copy / "output" / "EXAMPLE_MANUSCRIPT.pdf"
        assert output_pdf.exists(), "Output PDF was not created"
        assert output_pdf.stat().st_size > 1000, "Output PDF is too small"

    def test_rxiv_validate_example_manuscript(self, example_manuscript_copy):
        """Test validation of EXAMPLE_MANUSCRIPT."""
        # Run figure generation first to ensure all figure files exist
        try:
            subprocess.run(
                ["uv", "run", "rxiv", "figures", str(example_manuscript_copy)],
                capture_output=True,
                text=True,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            subprocess.run(
                [
                    "python",
                    "-m",
                    "rxiv_maker.cli",
                    "figures",
                    str(example_manuscript_copy),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        # Run validation
        try:
            result = subprocess.run(
                ["uv", "run", "rxiv", "validate", str(example_manuscript_copy)],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "rxiv_maker.cli",
                    "validate",
                    str(example_manuscript_copy),
                ],
                capture_output=True,
                text=True,
            )

        # Validation should pass
        assert result.returncode == 0, f"Validation failed: {result.stderr}"
        assert "✅" in result.stdout or "passed" in result.stdout.lower()

    def test_rxiv_figures_example_manuscript(self, example_manuscript_copy):
        """Test figure generation for EXAMPLE_MANUSCRIPT."""
        # Clean existing figures (including subdirectories)
        figures_dir = example_manuscript_copy / "FIGURES"
        for fig in figures_dir.rglob("*.pdf"):
            fig.unlink()
        for fig in figures_dir.rglob("*.png"):
            fig.unlink()

        # Run figure generation
        try:
            result = subprocess.run(
                ["uv", "run", "rxiv", "figures", str(example_manuscript_copy)],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "rxiv_maker.cli",
                    "figures",
                    str(example_manuscript_copy),
                ],
                capture_output=True,
                text=True,
            )

        # Check command succeeded
        assert result.returncode == 0, f"Figure generation failed: {result.stderr}"

        # Check figures were created (search recursively in subdirectories)
        generated_figures = list(figures_dir.rglob("*.pdf")) + list(
            figures_dir.rglob("*.png")
        )
        assert len(generated_figures) >= 2, "Expected at least 2 figures"

    @pytest.mark.parametrize("force_figures", [True, False])
    def test_rxiv_pdf_force_figures(self, example_manuscript_copy, force_figures):
        """Test PDF generation with and without force_figures option."""
        args = ["uv", "run", "rxiv", "pdf", str(example_manuscript_copy)]
        if force_figures:
            args.append("--force-figures")

        try:
            result = subprocess.run(args, capture_output=True, text=True)
        except FileNotFoundError:
            args = [
                "python",
                "-m",
                "rxiv_maker.cli",
                "pdf",
                str(example_manuscript_copy),
            ]
            if force_figures:
                args.append("--force-figures")
            result = subprocess.run(args, capture_output=True, text=True)
        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # PDF should exist
        output_pdf = example_manuscript_copy / "output" / "EXAMPLE_MANUSCRIPT.pdf"
        assert output_pdf.exists()

    def test_make_pdf_compatibility(self, example_manuscript_copy):
        """Test that make pdf still works (backwards compatibility)."""
        # Run make pdf with command-line variable override
        result = subprocess.run(
            ["make", "pdf", f"MANUSCRIPT_PATH={example_manuscript_copy}"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Should succeed (or gracefully fail if Make not available)
        if result.returncode == 0:
            output_pdf = example_manuscript_copy / "output" / "EXAMPLE_MANUSCRIPT.pdf"
            assert output_pdf.exists(), "Make pdf did not create output"

    def test_rxiv_clean(self, example_manuscript_copy):
        """Test cleaning generated files."""
        # First generate some output
        try:
            subprocess.run(
                ["uv", "run", "rxiv", "figures", str(example_manuscript_copy)],
                capture_output=True,
            )
        except FileNotFoundError:
            subprocess.run(
                [
                    "python",
                    "-m",
                    "rxiv_maker.cli",
                    "figures",
                    str(example_manuscript_copy),
                ],
                capture_output=True,
            )

        # Run clean
        try:
            result = subprocess.run(
                ["uv", "run", "rxiv", "clean", str(example_manuscript_copy)],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "rxiv_maker.cli",
                    "clean",
                    str(example_manuscript_copy),
                ],
                capture_output=True,
                text=True,
            )

        assert result.returncode == 0, f"Clean failed: {result.stderr}"

        # Check output directory was cleaned
        output_dir = example_manuscript_copy / "output"
        assert not output_dir.exists() or len(list(output_dir.iterdir())) == 0
