"""Figure Generation Script for Rxiv-Maker.

This script automatically processes figure files in the FIGURES directory and generates
publication-ready output files. It supports:
- .mmd files: Mermaid diagrams (generates SVG/PNG/PDF)
- .py files: Python scripts for matplotlib/seaborn figures
- .R files: R scripts (executes script and captures output figures)
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to allow imports when run as a script
if __name__ == "__main__":
    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

from rxiv_maker.docker.manager import get_docker_manager
from rxiv_maker.utils.platform import platform_detector


class FigureGenerator:
    """Main class for generating figures from various source formats."""

    def __init__(
        self,
        figures_dir="FIGURES",
        output_dir="FIGURES",
        output_format="png",
        r_only=False,
        engine="local",
    ):
        """Initialize the figure generator.

        Args:
            figures_dir: Directory containing source figure files
            output_dir: Directory for generated output files
            output_format: Default output format for figures
            r_only: Only process R files if True
            engine: Execution engine ("local" or "docker")
        """
        self.figures_dir = Path(figures_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.output_format = output_format.lower()
        self.r_only = r_only
        self.engine = engine
        self.supported_formats = ["png", "svg", "pdf", "eps"]
        self.platform = platform_detector

        # Initialize Docker manager if using docker engine
        self.docker_manager = None
        if self.engine == "docker":
            # Set workspace directory to current working directory to include all files
            workspace_dir = Path.cwd().resolve()
            self.docker_manager = get_docker_manager(workspace_dir=workspace_dir)

        if self.output_format not in self.supported_formats:
            raise ValueError(
                f"Unsupported format: {self.output_format}. "
                f"Supported: {self.supported_formats}"
            )

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_figures(self, parallel: bool = True, max_workers: int = 4):
        """Generate all figures found in the figures directory.

        Args:
            parallel: Enable parallel processing of figures
            max_workers: Maximum number of worker threads for parallel processing
        """
        print("Starting figure generation...")

        if not self.figures_dir.exists():
            print(f"Warning: Figures directory '{self.figures_dir}' does not exist")
            return

        print(f"Scanning for figures in: {self.figures_dir}")
        print("DEBUG: About to do file globbing...")

        # Find all figure files
        try:
            if self.r_only:
                print("DEBUG: r_only mode, getting R files...")
                r_files = list(self.figures_dir.glob("*.R"))
                mermaid_files = []
                python_files = []
            else:
                print("DEBUG: Getting mermaid files...")
                mermaid_files = list(self.figures_dir.glob("*.mmd"))
                print(f"DEBUG: Found {len(mermaid_files)} mermaid files")

                print("DEBUG: Getting python files...")
                python_files = list(self.figures_dir.glob("*.py"))
                print(f"DEBUG: Found {len(python_files)} python files")

                print("DEBUG: Getting R files...")
                r_files = list(self.figures_dir.glob("*.R"))
                print(f"DEBUG: Found {len(r_files)} R files")

            print("DEBUG: File globbing completed successfully!")

            # Process figures with optional parallelization
            if parallel and (len(mermaid_files) + len(python_files) + len(r_files)) > 1:
                self._generate_figures_parallel(
                    mermaid_files, python_files, r_files, max_workers
                )
            else:
                self._generate_figures_sequential(mermaid_files, python_files, r_files)

            print("DEBUG: All generation methods completed!")

        except Exception as e:
            print(f"DEBUG: Error in method: {e}")
            raise

    def _generate_figures_sequential(self, mermaid_files, python_files, r_files):
        """Generate figures sequentially (original behavior)."""
        # Mermaid generation
        print("DEBUG: About to test Mermaid generation...")
        if mermaid_files and not self.r_only:
            print(f"Found {len(mermaid_files)} Mermaid file(s):")
            for mmd_file in mermaid_files:
                print(f"  Processing: {mmd_file.name}")
                try:
                    self.generate_mermaid_figure(mmd_file)
                    print(f"  ✓ Completed: {mmd_file.name}")
                except Exception as e:
                    print(f"  ✗ Failed: {mmd_file.name} - {e}")

        # Python generation
        print("DEBUG: About to test Python generation...")
        if python_files and not self.r_only:
            print(f"Found {len(python_files)} Python file(s):")
            for py_file in python_files:
                print(f"  Processing: {py_file.name}")
                try:
                    self.generate_python_figure(py_file)
                    print(f"  ✓ Completed: {py_file.name}")
                except Exception as e:
                    print(f"  ✗ Failed: {py_file.name} - {e}")

        # R generation
        print("DEBUG: About to test R generation...")
        if r_files:
            print(f"Found {len(r_files)} R file(s):")
            for r_file in r_files:
                print(f"  Processing: {r_file.name}")
                try:
                    self.generate_r_figure(r_file)
                    print(f"  ✓ Completed: {r_file.name}")
                except Exception as e:
                    print(f"  ✗ Failed: {r_file.name} - {e}")

    def _generate_figures_parallel(
        self, mermaid_files, python_files, r_files, max_workers
    ):
        """Generate figures in parallel using ThreadPoolExecutor."""
        import concurrent.futures
        import threading

        print(f"Using parallel processing with {max_workers} workers")

        # Create thread-safe print function
        print_lock = threading.Lock()

        def safe_print(*args, **kwargs):
            with print_lock:
                print(*args, **kwargs)

        def process_figure(file_info):
            """Process a single figure file."""
            file_path, file_type = file_info
            try:
                safe_print(f"  [Parallel] Processing: {file_path.name}")

                if file_type == "mermaid":
                    self.generate_mermaid_figure(file_path)
                elif file_type == "python":
                    self.generate_python_figure(file_path)
                elif file_type == "r":
                    self.generate_r_figure(file_path)

                safe_print(f"  [Parallel] ✓ Completed: {file_path.name}")
                return True, file_path.name, None
            except Exception as e:
                safe_print(f"  [Parallel] ✗ Failed: {file_path.name} - {e}")
                return False, file_path.name, str(e)

        # Prepare work items
        work_items = []

        if mermaid_files and not self.r_only:
            work_items.extend([(f, "mermaid") for f in mermaid_files])

        if python_files and not self.r_only:
            work_items.extend([(f, "python") for f in python_files])

        if r_files:
            work_items.extend([(f, "r") for f in r_files])

        if not work_items:
            print("No figures to process")
            return

        safe_print(f"Processing {len(work_items)} figures in parallel...")

        # Process figures in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(process_figure, item): item[0] for item in work_items
            }

            # Collect results
            completed = 0
            failed = 0

            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    success, filename, error = future.result()
                    if success:
                        completed += 1
                    else:
                        failed += 1
                except Exception as exc:
                    safe_print(f"  [Parallel] ✗ Exception for {file_path.name}: {exc}")
                    failed += 1

            safe_print(
                f"Parallel processing completed: {completed} successful, {failed} failed"
            )

    def generate_mermaid_figure(self, mmd_file):
        """Generate figure from Mermaid diagram file using two-step SVG process."""
        try:
            # Create subdirectory for this figure
            figure_dir = self.output_dir / mmd_file.stem
            figure_dir.mkdir(parents=True, exist_ok=True)

            # --- Step 1: Generate SVG using Mermaid CLI ---
            svg_output_file = figure_dir / f"{mmd_file.stem}.svg"
            print(
                f"  🎨 Generating intermediate SVG: {figure_dir.name}/{svg_output_file.name}..."
            )

            if self.engine == "docker":
                # Use Docker for Mermaid processing
                result = self.docker_manager.run_mermaid_generation(
                    input_file=mmd_file.resolve(),
                    output_file=svg_output_file.resolve(),
                    background_color="transparent",
                )
            else:
                # Check if mmdc (Mermaid CLI) is available locally
                if not self._check_mermaid_cli():
                    print(f"  ⚠️  Skipping {mmd_file.name}: Mermaid CLI not available")
                    print("     Install with: npm install -g @mermaid-js/mermaid-cli")
                    return

                cmd_parts = [
                    "mmdc",
                    "-i",
                    str(mmd_file),
                    "-o",
                    str(svg_output_file),
                    "--backgroundColor",
                    "transparent",
                ]

                cmd = " ".join(cmd_parts)
                result = self.platform.run_command(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"  ❌ Error generating SVG for {mmd_file.name}:")
                print(f"     {result.stderr}")
                return

            print(
                f"  ✅ Successfully generated {figure_dir.name}/{svg_output_file.name}"
            )

            # --- Step 2: Convert SVG to PNG and PDF using CairoSVG ---
            if self.engine == "docker":
                # Use Docker for CairoSVG conversion (Docker image has CairoSVG pre-installed)
                cairosvg_available = True
                cairo_error = None
            else:
                # Check CairoSVG availability for local execution
                cairosvg_available, cairo_error = self._check_cairosvg_availability()

            if not cairosvg_available:
                print(
                    f"  ⚠️  CairoSVG not available for {mmd_file.name} - using SVG only"
                )
                print(f"     Reason: {cairo_error}")
                self._print_cairo_installation_help()
                print(
                    f"     SVG file generated: {figure_dir.name}/{svg_output_file.name}"
                )
                print("     LaTeX can use SVG files directly for PDF compilation")
                return

            # Convert SVG to raster formats
            formats_to_generate = ["png", "pdf"]
            generated_files = [f"{figure_dir.name}/{svg_output_file.name}"]

            if self.engine == "docker":
                # Use Docker for CairoSVG conversion
                for format_type in formats_to_generate:
                    output_file = figure_dir / f"{mmd_file.stem}.{format_type}"
                    print(
                        f"  🎨 Converting SVG to {format_type.upper()}: {figure_dir.name}/{output_file.name}..."
                    )
                    try:
                        result = self.docker_manager.run_cairo_conversion(
                            input_file=svg_output_file.resolve(),
                            output_file=output_file.resolve(),
                            output_format=format_type,
                            dpi=300 if format_type == "png" else None,
                        )

                        if result.returncode != 0:
                            print(
                                f"  ❌ Error converting SVG to {format_type.upper()} for {mmd_file.name}:"
                            )
                            print(f"     {result.stderr}")
                            continue

                        print(
                            f"  ✅ Successfully generated {figure_dir.name}/{output_file.name}"
                        )
                        generated_files.append(f"{figure_dir.name}/{output_file.name}")
                    except Exception as e:
                        print(
                            f"  ❌ Error converting SVG to {format_type.upper()} for {mmd_file.name}:"
                        )
                        print(f"     {str(e)}")
            else:
                # Use local CairoSVG
                import cairosvg

                for format_type in formats_to_generate:
                    output_file = figure_dir / f"{mmd_file.stem}.{format_type}"
                    print(
                        f"  🎨 Converting SVG to {format_type.upper()}: {figure_dir.name}/{output_file.name}..."
                    )
                    try:
                        if format_type == "png":
                            cairosvg.svg2png(
                                url=str(svg_output_file),
                                write_to=str(output_file),
                                dpi=300,
                            )
                        elif format_type == "pdf":
                            cairosvg.svg2pdf(
                                url=str(svg_output_file), write_to=str(output_file)
                            )

                        print(
                            f"  ✅ Successfully generated {figure_dir.name}/{output_file.name}"
                        )
                        generated_files.append(f"{figure_dir.name}/{output_file.name}")
                    except Exception as conversion_error:
                        print(
                            f"  ❌ Error converting SVG to {format_type.upper()} for {mmd_file.name}:"
                        )
                        print(f"     {conversion_error}")
                        if "cairo" in str(conversion_error).lower():
                            self._print_cairo_troubleshooting()

            if generated_files:
                print(f"     Total files generated: {', '.join(generated_files)}")

        except Exception as e:
            print(f"  ❌ Error processing {mmd_file.name}: {e}")

    def _check_cairosvg_availability(self):
        """Check if CairoSVG is available and working."""
        try:
            import cairosvg

            # Test basic functionality
            cairosvg.svg2png(bytestring=b'<svg><rect width="10" height="10"/></svg>')
            return True, None
        except ImportError:
            return False, "CairoSVG package not installed"
        except Exception as e:
            error_msg = str(e)
            if "cairo" in error_msg.lower():
                return False, f"Cairo system libraries not available: {error_msg}"
            else:
                return False, f"CairoSVG error: {error_msg}"

    def _print_cairo_installation_help(self):
        """Print platform-specific Cairo installation instructions."""
        import platform

        system = platform.system().lower()

        print("     💡 To enable PNG/PDF conversion, install Cairo libraries:")
        if system == "darwin":  # macOS
            print("     - macOS: brew install cairo pango pkg-config")
            print("     - Then restart your terminal to update environment variables")
        elif system == "linux":
            print(
                "     - Ubuntu/Debian: sudo apt-get install libcairo2-dev libpango1.0-dev"
            )
            print("     - RHEL/CentOS: sudo yum install cairo-devel pango-devel")
            print("     - Arch: sudo pacman -S cairo pango")
        elif system == "windows":
            print(
                "     - Windows: Install GTK libraries via msys2 or winget install GTK"
            )
        else:
            print(
                "     - Install Cairo and Pango development libraries for your system"
            )
        print("     - Then reinstall: pip install --force-reinstall cairosvg")

    def _print_cairo_troubleshooting(self):
        """Print Cairo-specific troubleshooting tips."""
        import platform

        system = platform.system().lower()

        print("     🔧 Cairo troubleshooting:")
        if system == "darwin":  # macOS
            print(
                "     - Try: export PKG_CONFIG_PATH=/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
            )
            print(
                "     - Try: export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
            )
            print("     - Run: rxiv setup --reinstall to reconfigure environment")
        else:
            print("     - Ensure Cairo libraries are in your system's library path")
            print("     - Try reinstalling: pip install --force-reinstall cairosvg")
        print("     - Alternative: Use SVG files directly (LaTeX supports SVG)")

    def generate_python_figure(self, py_file):
        """Generate figure from Python script."""
        try:
            # Create subdirectory for this figure
            figure_dir = self.output_dir / py_file.stem
            figure_dir.mkdir(parents=True, exist_ok=True)

            print(f"  🐍 Executing {py_file.name}...")

            # Execute the Python script - use Docker if engine="docker"
            import shlex

            if self.engine == "docker":
                # Use Docker execution with centralized manager
                env = {"RXIV_FIGURE_OUTPUT_DIR": str(figure_dir.absolute())}

                result = self.docker_manager.run_python_script(
                    script_file=py_file.resolve(),
                    working_dir=figure_dir.resolve(),
                    environment=env,
                )
            else:
                # Use local Python execution
                python_cmd = self.platform.python_cmd
                if "uv run" in python_cmd:
                    # For uv run, we need to run from the project root but change to the
                    # figure directory within the script execution
                    exec_code = (
                        f"import os; "
                        f"__file__ = '{py_file.absolute()}'; "
                        f"os.chdir('{figure_dir.absolute()}'); "
                        f"exec(open('{py_file.absolute()}').read())"
                    )
                    cmd_parts = ["uv", "run", "python", "-c", exec_code]
                    # Use manual shell escaping for compatibility
                    cmd = " ".join(shlex.quote(part) for part in cmd_parts)
                    # Run from current working directory (project root) not figure_dir
                    cwd = None
                else:
                    cmd_parts = [python_cmd, str(py_file.absolute())]
                    cmd = " ".join(shlex.quote(part) for part in cmd_parts)
                    # For other Python commands, run from figure directory
                    cwd = str(figure_dir.absolute())

                # Set environment variable to ensure script saves to correct location
                import os

                env = os.environ.copy()
                env["RXIV_FIGURE_OUTPUT_DIR"] = str(figure_dir.absolute())

                result = self.platform.run_command(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=cwd,
                    env=env,
                )

            if result.stdout:
                # Print any output from the script (like success messages)
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        print(f"     {line}")

            if result.returncode != 0:
                print(f"  ❌ Error executing {py_file.name}:")
                if result.stderr:
                    print(f"     {result.stderr}")
                return

            print("     Debug: Script executed successfully, now checking for files...")

            # Check for generated files by scanning the figure subdirectory
            # Add a small delay to ensure files are fully written in CI environments
            import time

            time.sleep(0.1)

            # Force filesystem sync
            import os

            os.sync() if hasattr(os, "sync") else None

            print(f"     Debug: About to scan directory: {figure_dir.absolute()}")
            print(f"     Debug: Directory exists: {figure_dir.exists()}")
            if figure_dir.exists():
                dir_contents = list(figure_dir.iterdir())
                print(f"     Debug: Directory contents: {dir_contents}")
            else:
                print("     Debug: Directory does not exist!")

            current_files = set()
            for ext in ["png", "pdf", "svg", "eps"]:
                # Use rglob to find files recursively in subdirectories
                found_files = list(figure_dir.rglob(f"*.{ext}"))
                current_files.update(found_files)
                file_names = [f.name for f in found_files]
                print(f"     Debug: Found {len(found_files)} {ext} files: {file_names}")

            # Look for files that might have been created by this script
            base_name = py_file.stem
            potential_files = []
            for file_path in current_files:
                # Check if filename contains the base name or is a common figure pattern
                if (
                    base_name.lower() in file_path.stem.lower()
                    or file_path.stem.lower().startswith("figure")
                    or file_path.stem.lower().startswith("fig")
                ):
                    potential_files.append(file_path)

            if potential_files:
                print("  ✅ Generated figures:")
                for gen_file in sorted(potential_files):
                    # Show relative path from figure_dir
                    rel_path = gen_file.relative_to(figure_dir)
                    print(f"     - {figure_dir.name}/{rel_path}")
            else:
                print(f"  ⚠️  No output files detected for {py_file.name}")
                print(f"     Debug: Checked {len(current_files)} total files")
                print(f"     Debug: Base name pattern: {base_name.lower()}")
                if current_files:
                    available_files = [f.name for f in current_files]
                    print(f"     Debug: Available files: {available_files}")

        except Exception as e:
            print(f"  ❌ Error executing {py_file.name}: {e}")

    def generate_r_figure(self, r_file):
        """Generate figure from R script."""
        try:
            # Check if Rscript is available (only for local execution)
            if self.engine != "docker" and not self._check_rscript():
                print(f"  ⚠️  Skipping {r_file.name}: Rscript not available")
                print("     Ensure R is installed and accessible in your PATH")
                print("Check https://www.r-project.org/ for installation instructions")
                return

            # Create subdirectory for this figure
            figure_dir = self.output_dir / r_file.stem
            figure_dir.mkdir(parents=True, exist_ok=True)

            print(f"  📊 Executing {r_file.name}...")

            # Execute the R script - use Docker if engine="docker"

            if self.engine == "docker":
                # Use Docker execution with centralized manager
                env = {"RXIV_FIGURE_OUTPUT_DIR": str(figure_dir.absolute())}

                result = self.docker_manager.run_r_script(
                    script_file=r_file.resolve(),
                    working_dir=figure_dir.resolve(),
                    environment=env,
                )
            else:
                # Use local R execution
                cmd = f"Rscript {str(r_file.absolute())}"

                # Set environment variable to ensure script saves to correct location
                import os

                env = os.environ.copy()
                env["RXIV_FIGURE_OUTPUT_DIR"] = str(figure_dir.absolute())

                result = self.platform.run_command(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(figure_dir.absolute()),
                    env=env,
                )

            if result.stdout:
                # Print any output from the script (like success messages)
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        print(f"     {line}")

            if result.returncode != 0:
                print(f"  ❌ Error executing {r_file.name}:")
                if result.stderr:
                    print(f"     {result.stderr}")
                return

            # Check for generated files by scanning the figure subdirectory
            current_files = set()
            for ext in ["png", "pdf", "svg", "eps"]:
                current_files.update(figure_dir.glob(f"*.{ext}"))

            # Look for files that might have been created by this script
            base_name = r_file.stem
            potential_files = []
            for file_path in current_files:
                # Check if filename contains the base name or is a common figure pattern
                if (
                    base_name.lower() in file_path.stem.lower()
                    or file_path.stem.lower().startswith("figure")
                    or file_path.stem.lower().startswith("fig")
                ):
                    potential_files.append(file_path)

            if potential_files:
                print("  ✅ Generated figures:")
                for gen_file in sorted(potential_files):
                    print(f"     - {figure_dir.name}/{gen_file.name}")
            else:
                print(f"  ⚠️  No output files detected for {r_file.name}")

        except Exception as e:
            print(f"  ❌ Error executing {r_file.name}: {e}")

    def _check_mermaid_cli(self):
        """Check if Mermaid CLI (mmdc) is available."""
        return self.platform.check_command_exists("mmdc")

    def _import_matplotlib(self):
        """Safely import matplotlib."""
        try:
            import matplotlib

            # Use non-interactive backend for headless operation
            matplotlib.use("Agg")
            return matplotlib
        except ImportError:
            print("  ⚠️  matplotlib not available for Python figures")
            return None

    def _import_seaborn(self):
        """Safely import seaborn."""
        try:
            import seaborn as sns

            return sns
        except ImportError:
            print("  ⚠️  seaborn not available")
            return None

    def _import_numpy(self):
        """Safely import numpy."""
        try:
            import numpy as np

            return np
        except ImportError:
            print("  ⚠️  numpy not available")
            return None

    def _import_pandas(self):
        """Safely import pandas."""
        try:
            import pandas as pd

            return pd
        except ImportError:
            print("  ⚠️  pandas not available")
            return None

    def _check_rscript(self):
        """Check if Rscript is available."""
        return self.platform.check_command_exists("Rscript")


# CLI integration
def main():
    """Main function for CLI integration."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Generate figures from source files")
    parser.add_argument(
        "--figures-dir", default="FIGURES", help="Directory with source figures"
    )
    parser.add_argument("--output-dir", default="FIGURES", help="Output directory")
    parser.add_argument(
        "--format", default="png", help="Output format (png, svg, pdf, eps)"
    )
    parser.add_argument("--r-only", action="store_true", help="Process only R files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Enable parallel processing (default: True)",
    )
    parser.add_argument(
        "--no-parallel", action="store_true", help="Disable parallel processing"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of parallel workers (default: 4)",
    )
    parser.add_argument(
        "--engine",
        default=os.environ.get("RXIV_ENGINE", "local"),
        choices=["local", "docker"],
        help="Execution engine (local or docker, can be set via RXIV_ENGINE env var)",
    )

    args = parser.parse_args()

    generator = FigureGenerator(
        figures_dir=args.figures_dir,
        output_dir=args.output_dir,
        output_format=args.format,
        r_only=args.r_only,
        engine=args.engine,
    )

    # Set verbose mode if specified
    if args.verbose:
        generator.verbose = args.verbose

    # Determine parallel processing settings
    use_parallel = args.parallel and not args.no_parallel
    max_workers = max(1, min(args.max_workers, 8))  # Limit to reasonable range

    generator.generate_all_figures(parallel=use_parallel, max_workers=max_workers)
    print("Figure generation complete!")


if __name__ == "__main__":
    main()
