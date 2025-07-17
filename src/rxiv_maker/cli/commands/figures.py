"""Figures command for rxiv-maker CLI."""

import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

console = Console()


@click.command()
@click.argument(
    "manuscript_path", type=click.Path(exists=True, file_okay=False), required=False
)
@click.option("--force", "-f", is_flag=True, help="Force regeneration of all figures")
@click.option("--figures-dir", "-d", help="Custom figures directory path")
@click.pass_context
def figures(
    ctx: click.Context,
    manuscript_path: str | None,
    force: bool,
    figures_dir: str | None,
) -> None:
    """Generate figures from scripts.

    MANUSCRIPT_PATH: Path to manuscript directory (default: MANUSCRIPT)

    This command generates figures from:
    - Python scripts (*.py)
    - R scripts (*.R)
    - Mermaid diagrams (*.mmd)
    """
    verbose = ctx.obj.get("verbose", False)

    # Default to MANUSCRIPT if not specified
    if manuscript_path is None:
        manuscript_path = os.environ.get("MANUSCRIPT_PATH", "MANUSCRIPT")

    # Validate manuscript path exists
    if not Path(manuscript_path).exists():
        console.print(
            f"❌ Error: Manuscript directory '{manuscript_path}' does not exist",
            style="red",
        )
        console.print(
            f"💡 Run 'rxiv init {manuscript_path}' to create a new manuscript",
            style="yellow",
        )
        sys.exit(1)

    # Set figures directory
    if figures_dir is None:
        figures_dir = str(Path(manuscript_path) / "FIGURES")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Generating figures...", total=None)

            # Import figure generation command
            from ...commands.generate_figures import main as generate_figures_main

            # Prepare arguments
            args = ["--figures-dir", figures_dir]
            if force:
                args.append("--force")
            if verbose:
                args.append("--verbose")

            # Save original argv and replace
            original_argv = sys.argv
            sys.argv = ["generate_figures"] + args

            try:
                generate_figures_main()
                progress.update(task, description="✅ Figure generation completed")
                console.print("✅ Figures generated successfully!", style="green")
                console.print(f"📁 Figures directory: {figures_dir}", style="blue")

            except SystemExit as e:
                progress.update(task, description="❌ Figure generation failed")
                if e.code != 0:
                    console.print(
                        "❌ Figure generation failed. See details above.", style="red"
                    )
                    console.print(
                        "💡 Check your figure scripts for errors", style="yellow"
                    )
                    sys.exit(1)

            finally:
                sys.argv = original_argv

    except KeyboardInterrupt:
        console.print("\n⏹️  Figure generation interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error during figure generation: {e}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(1)
