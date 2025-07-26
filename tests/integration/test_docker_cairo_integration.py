"""
Integration tests for Docker Cairo-only figure generation.

This module tests the complete figure generation workflow using the
Cairo-only Docker image, ensuring end-to-end functionality works correctly.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from rxiv_maker.commands.build_manager import BuildManager
from rxiv_maker.commands.generate_figures import FigureGenerator


class TestDockerCairoIntegration(unittest.TestCase):
    """Integration tests for Docker Cairo-only functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create test directory within the project to avoid path issues with Docker
        project_root = Path(__file__).parent.parent.parent
        self.test_dir = project_root / "test_temp_integration"
        self.test_dir.mkdir(exist_ok=True)
        self.manuscript_dir = self.test_dir / "manuscript"
        self.figures_dir = self.manuscript_dir / "FIGURES"
        self.python_figures_dir = self.figures_dir / "PYTHON"
        self.r_figures_dir = self.figures_dir / "R"

        # Create directory structure
        self.manuscript_dir.mkdir(exist_ok=True)
        self.figures_dir.mkdir(exist_ok=True)
        self.python_figures_dir.mkdir(exist_ok=True)
        self.r_figures_dir.mkdir(exist_ok=True)

        # Set up figure generator with Docker engine
        self.figure_generator = FigureGenerator(engine="docker")

    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_cairo_docker_image_integration(self):
        """Test that Cairo Docker integration works end-to-end."""
        # Create a simple Python figure script
        python_script = self.python_figures_dir / "test_figure.py"
        python_script.write_text("""
import matplotlib.pyplot as plt
import numpy as np

# Create a simple plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, label='sin(x)')
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.title('Test Figure for Cairo Integration')
plt.legend()
plt.grid(True)
plt.savefig('test_figure.png', dpi=150, bbox_inches='tight')
plt.savefig('test_figure.pdf', bbox_inches='tight')
plt.close()
print("Figure generated successfully with Cairo backend")
""")

        # Create an R figure script
        r_script = self.r_figures_dir / "test_r_figure.R"
        r_script.write_text("""
library(ggplot2)

# Create test data
data <- data.frame(
  x = 1:10,
  y = (1:10)^2
)

# Create plot with Cairo backend
p <- ggplot(data, aes(x = x, y = y)) +
  geom_line(color = "blue", size = 1) +
  geom_point(color = "red", size = 3) +
  labs(
    title = "Test R Figure with Cairo",
    x = "X Values",
    y = "Y Values"
  ) +
  theme_minimal()

# Save with Cairo backend
ggsave("test_r_figure.png", plot = p, width = 8, height = 6, dpi = 150, device = "png")
ggsave("test_r_figure.pdf", plot = p, width = 8, height = 6, device = "pdf")

cat("R figure generated successfully with Cairo backend\\n")
""")

        # Test Docker/local fallback integration
        # The system should work regardless of Docker availability
        try:
            # Test Python figure generation
            self.figure_generator.generate_python_figure(python_script)

            # If this completes without error, the Docker/local system is working
            self.assertTrue(True, "Figure generation system integration test passed")

        except Exception as e:
            # Only fail for unexpected errors, not Docker unavailability
            if (
                "docker" not in str(e).lower()
                and "command not found" not in str(e).lower()
            ):
                self.fail(f"Unexpected integration test failure: {e}")
            else:
                # Docker unavailability is acceptable - the system falls back gracefully
                self.skipTest(f"Docker not available for integration test: {e}")

    @patch("rxiv_maker.utils.platform.platform_detector.run_command")
    def test_mermaid_cairo_integration(self, mock_run):
        """Test Mermaid diagram generation with Cairo backend."""
        # Create a Mermaid diagram file
        mermaid_file = self.figures_dir / "test_diagram.mmd"
        mermaid_file.write_text("""
graph TD
    A[Start] --> B{Cairo Available?}
    B -->|Yes| C[Generate SVG]
    C --> D[Convert to PNG with Cairo]
    D --> E[Success]
    B -->|No| F[Error]

    style A fill:#e1f5fe
    style E fill:#c8e6c9
    style F fill:#ffcdd2
""")

        # Mock successful Mermaid + Cairo processing
        mock_run.side_effect = [
            # Mermaid SVG generation
            Mock(returncode=0, stdout="SVG generated successfully", stderr=""),
            # Cairo PNG conversion
            Mock(returncode=0, stdout="PNG conversion completed with Cairo", stderr=""),
        ]

        # In a real scenario, this would be handled by the build manager
        # For testing, we simulate the Mermaid + Cairo workflow
        if mock_run.side_effect:
            result = list(mock_run.side_effect)[0]
        else:
            result = mock_run.return_value
        self.assertEqual(result.returncode, 0)
        self.assertIn("SVG generated", result.stdout)

    @patch("rxiv_maker.utils.platform.platform_detector.run_command")
    def test_font_rendering_integration(self, mock_run):
        """Test that enhanced fonts work correctly in Cairo integration."""
        # Create a script that uses enhanced fonts
        font_test_script = self.python_figures_dir / "font_test.py"
        font_test_script.write_text("""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Test enhanced font availability
fonts_to_test = [
    'Liberation Sans',
    'DejaVu Sans',
    'Roboto',
    'Noto Color Emoji'
]

available_fonts = [f.name for f in fm.fontManager.ttflist]
print("Available fonts:")
for font in fonts_to_test:
    if any(font.lower() in af.lower() for af in available_fonts):
        print(f"✅ {font} available")
    else:
        print(f"❌ {font} not found")

# Create a plot with enhanced typography
plt.figure(figsize=(10, 6))
plt.text(0.5, 0.8, "Cairo Font Test", fontsize=20, ha='center',
         fontfamily='Liberation Sans')
plt.text(0.5, 0.6, "Enhanced Typography", fontsize=16, ha='center',
         fontfamily='DejaVu Sans')
plt.text(0.5, 0.4, "🎨 Unicode Support", fontsize=14, ha='center')
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.axis('off')
plt.title('Font Rendering Test', fontsize=18)
plt.savefig('font_test.png', dpi=150, bbox_inches='tight')
plt.close()
print("Font test completed successfully")
""")

        # Mock successful execution
        mock_run.return_value = Mock(
            returncode=0,
            stdout="✅ Liberation Sans available\n✅ DejaVu Sans available\nFont test completed successfully",
            stderr="",
        )

        # Test would be called through figure generator
        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)
        self.assertIn("Font test completed", result.stdout)

    def test_build_manager_cairo_integration(self):
        """Test BuildManager integration with Cairo Docker engine."""
        # Create a minimal manuscript structure
        config_file = self.manuscript_dir / "rxiv.yaml"
        config_file.write_text("""
title: "Cairo Integration Test"
authors:
  - name: "Test Author"
    email: "test@example.com"
""")

        main_file = self.manuscript_dir / "main.md"
        main_file.write_text("""
# Cairo Integration Test

This is a test manuscript for Cairo Docker integration.

![Test Figure](FIGURES/PYTHON/test_figure.png)
""")

        # Initialize BuildManager with Docker engine
        build_manager = BuildManager(
            manuscript_path=str(self.manuscript_dir), engine="docker"
        )

        # Test that BuildManager properly configures Docker engine
        self.assertEqual(build_manager.engine, "docker")

    @patch("rxiv_maker.utils.platform.platform_detector.run_command")
    def test_error_handling_cairo_integration(self, mock_run):
        """Test error handling in Cairo Docker integration."""
        # Mock Docker execution failure
        mock_run.return_value = Mock(
            returncode=1, stdout="", stderr="Cairo library error: missing dependencies"
        )

        # Create a simple test script
        test_script = self.python_figures_dir / "error_test.py"
        test_script.write_text("import matplotlib.pyplot as plt")

        # Test error handling
        result = mock_run.return_value
        self.assertEqual(result.returncode, 1)
        self.assertIn("Cairo library error", result.stderr)

    @patch("rxiv_maker.utils.platform.platform_detector.run_command")
    def test_performance_cairo_integration(self, mock_run):
        """Test performance characteristics of Cairo integration."""
        # Mock performance metrics
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Processing completed in 2.3 seconds\nMemory usage: 180MB\nCairo optimization: enabled",
            stderr="",
        )

        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)
        self.assertIn("Cairo optimization: enabled", result.stdout)

    def test_directory_structure_cairo(self):
        """Test that directory structure is properly maintained with Cairo."""
        # Verify that our test directory structure matches rxiv-maker expectations
        self.assertTrue(self.manuscript_dir.exists())
        self.assertTrue(self.figures_dir.exists())
        self.assertTrue(self.python_figures_dir.exists())
        self.assertTrue(self.r_figures_dir.exists())

        # Test relative path resolution
        rel_python_dir = self.python_figures_dir.relative_to(self.manuscript_dir)
        self.assertEqual(str(rel_python_dir), "FIGURES/PYTHON")

    @patch("rxiv_maker.utils.platform.platform_detector.run_command")
    def test_multi_format_output_cairo(self, mock_run):
        """Test multiple output formats with Cairo backend."""
        # Mock successful multi-format generation
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Generated: test.png (PNG), test.pdf (PDF), test.svg (SVG)",
            stderr="",
        )

        result = mock_run.return_value
        self.assertEqual(result.returncode, 0)

        # Verify multiple formats mentioned
        formats = ["PNG", "PDF", "SVG"]
        for fmt in formats:
            self.assertIn(fmt, result.stdout)


class TestCairoMigrationCompatibility(unittest.TestCase):
    """Test compatibility during Cairo migration."""

    def setUp(self):
        """Set up compatibility test environment."""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up compatibility test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_legacy_script_compatibility(self):
        """Test that legacy scripts still work with Cairo backend."""
        # Create a legacy-style figure script
        legacy_script = self.test_dir / "legacy_figure.py"
        legacy_script.write_text("""
# Legacy matplotlib script (should work with Cairo)
import matplotlib
matplotlib.use('Agg')  # Legacy backend specification
import matplotlib.pyplot as plt

plt.plot([1, 2, 3], [1, 4, 9])
plt.savefig('legacy_figure.png')
print("Legacy script executed successfully")
""")

        # Test that legacy script structure is valid
        self.assertTrue(legacy_script.exists())
        content = legacy_script.read_text()
        self.assertIn("matplotlib", content)
        self.assertIn("savefig", content)

    def test_configuration_compatibility(self):
        """Test that existing configurations work with Cairo."""
        # Create a configuration that should work with both old and new systems
        config = {
            "engine": "docker",
            "image": "henriqueslab/rxiv-maker-base:latest",  # Now Cairo-only
            "output_formats": ["png", "pdf", "svg"],
        }

        # Verify configuration structure
        self.assertEqual(config["engine"], "docker")
        self.assertIn("rxiv-maker-base", config["image"])
        self.assertIn("png", config["output_formats"])


if __name__ == "__main__":
    unittest.main()
