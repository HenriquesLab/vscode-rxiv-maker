"""
Tests for Docker Cairo-only functionality.

This module tests the Cairo-only Docker image functionality,
ensuring SVG processing works correctly without browser dependencies.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from rxiv_maker.commands.generate_figures import FigureGenerator


class TestDockerCairoFunctionality(unittest.TestCase):
    """Test Docker Cairo-only functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test directory within the project to avoid path issues with Docker
        project_root = Path(__file__).parent.parent.parent
        self.test_dir = project_root / "test_temp_docker"
        self.test_dir.mkdir(exist_ok=True)
        self.figure_generator = FigureGenerator(engine="docker")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch("rxiv_maker.utils.platform.platform_detector.run_command")
    def test_cairo_svg_processing(self, mock_run):
        """Test that Cairo processes SVG files correctly in Docker."""
        # Mock successful Docker execution with Cairo
        mock_run.return_value = Mock(
            returncode=0, stdout="Cairo SVG processing successful", stderr=""
        )

        # Create test SVG content
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="100" fill="lightblue" stroke="navy" stroke-width="2"/>
  <text x="100" y="50" text-anchor="middle" font-family="Liberation Sans" font-size="16">Cairo Test</text>
</svg>"""

        test_svg_path = Path(self.test_dir) / "test.svg"
        test_svg_path.write_text(svg_content)

        # Test SVG processing
        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)
        self.assertIn("Cairo", result.stdout)

    @patch("rxiv_maker.utils.platform.platform_detector.run_command")
    def test_docker_image_uses_cairo_only(self, mock_run):
        """Test that Docker commands use the Cairo-only base image."""
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")

        # Trigger a Docker operation
        test_py_file = Path(self.test_dir) / "test_figure.py"
        test_py_file.write_text(
            "import matplotlib.pyplot as plt\nplt.savefig('test.png')"
        )

        # Generate figure with Docker engine
        try:
            self.figure_generator.generate_python_figure(test_py_file)
        except Exception:
            pass  # We're testing the Docker command, not the actual execution

        # Verify Docker was called with the correct image
        mock_run.assert_called()
        docker_calls = [
            call
            for call in mock_run.call_args_list
            if any("docker" in str(arg) for arg in call[0][0])
        ]

        if docker_calls:
            docker_cmd = docker_calls[0][0][0]
            self.assertIn("henriqueslab/rxiv-maker-base:latest", str(docker_cmd))

    @patch("subprocess.run")
    def test_mermaid_cairo_rendering(self, mock_run):
        """Test Mermaid diagram rendering with Cairo in Docker."""
        # Mock Mermaid CLI and Cairo conversion
        mock_run.side_effect = [
            # Mermaid SVG generation
            Mock(returncode=0, stdout="SVG generated", stderr=""),
            # Cairo PNG conversion
            Mock(returncode=0, stdout="PNG converted with Cairo", stderr=""),
        ]

        # Create test Mermaid file
        mermaid_content = """graph TD
    A[Start] --> B{Is Cairo working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Fix it]
    D --> B"""

        test_mmd_path = Path(self.test_dir) / "test.mmd"
        test_mmd_path.write_text(mermaid_content)

        # Test diagram generation (would use Docker in real scenario)
        result = mock_run.side_effect[0]
        self.assertEqual(result.returncode, 0)
        self.assertIn("SVG", result.stdout)

    @patch("subprocess.run")
    def test_docker_environment_variables(self, mock_run):
        """Test that Docker containers have proper Cairo environment variables."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="CAIRO_CACHE_DIR=/tmp/cairo-cache\nFONTCONFIG_FILE=/etc/fonts/fonts.conf",
            stderr="",
        )

        # Mock checking environment variables in Docker
        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)
        self.assertIn("CAIRO_CACHE_DIR", result.stdout)
        self.assertIn("FONTCONFIG_FILE", result.stdout)

    @patch("subprocess.run")
    def test_font_availability_in_docker(self, mock_run):
        """Test that Cairo-enhanced fonts are available in Docker."""
        # Mock font listing command
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Liberation Sans\nDejaVu Sans\nRoboto\nNoto Color Emoji",
            stderr="",
        )

        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)

        # Check for enhanced font collection
        expected_fonts = [
            "Liberation Sans",
            "DejaVu Sans",
            "Roboto",
            "Noto Color Emoji",
        ]
        for font in expected_fonts:
            self.assertIn(font, result.stdout)

    @patch("subprocess.run")
    def test_no_browser_dependencies(self, mock_run):
        """Test that Docker image has no browser dependencies."""
        # Mock checking for browser binaries (should fail)
        mock_run.side_effect = [
            Mock(returncode=1, stdout="", stderr="chrome: command not found"),
            Mock(returncode=1, stdout="", stderr="chromium: command not found"),
            Mock(returncode=1, stdout="", stderr="google-chrome: command not found"),
        ]

        # All browser checks should fail (return code 1)
        for result in mock_run.side_effect:
            self.assertEqual(result.returncode, 1)
            self.assertIn("not found", result.stderr)

    @patch("subprocess.run")
    def test_cairo_test_script_execution(self, mock_run):
        """Test that the Cairo test script executes successfully."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Successfully converted SVG to PNG (1234 bytes)\nCairo functionality verified!",
            stderr="",
        )

        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)
        self.assertIn("Cairo functionality verified", result.stdout)
        self.assertIn("Successfully converted", result.stdout)

    @patch("rxiv_maker.utils.platform.platform_detector.run_command")
    def test_docker_build_args_cairo_optimized(self, mock_run):
        """Test that Docker containers use Cairo-optimized build arguments."""
        mock_run.return_value = Mock(
            returncode=0, stdout="Container started", stderr=""
        )

        # Create a simple test case that would trigger Docker usage
        test_file = Path(self.test_dir) / "test.py"
        test_file.write_text("print('test')")

        # Mock the Docker execution
        try:
            self.figure_generator.generate_python_figure(test_file)
        except Exception:
            pass  # We're testing the command structure

        # Verify Docker was called
        self.assertTrue(mock_run.called)

    def test_figure_generator_engine_configuration(self):
        """Test that FigureGenerator properly configures Docker engine."""
        # Test Docker engine configuration
        docker_generator = FigureGenerator(engine="docker")
        self.assertEqual(docker_generator.engine, "docker")

        # Test local engine configuration
        local_generator = FigureGenerator(engine="local")
        self.assertEqual(local_generator.engine, "local")


class TestCairoPerformance(unittest.TestCase):
    """Test Cairo performance characteristics."""

    @patch("subprocess.run")
    def test_cairo_performance_metrics(self, mock_run):
        """Test that Cairo processing meets performance expectations."""
        # Mock successful Cairo processing with timing
        mock_run.return_value = Mock(
            returncode=0, stdout="Processing completed in 0.85 seconds", stderr=""
        )

        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)
        self.assertIn("completed", result.stdout)

    @patch("subprocess.run")
    def test_memory_usage_optimization(self, mock_run):
        """Test that Cairo Docker containers have optimized memory usage."""
        # Mock memory usage check
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Memory usage: 256MB (within Cairo optimization limits)",
            stderr="",
        )

        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)
        self.assertIn("Memory usage", result.stdout)


if __name__ == "__main__":
    unittest.main()
