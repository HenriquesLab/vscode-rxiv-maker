"""PDF command for rxiv-maker CLI."""

import os
import sys
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ...commands.build_manager import BuildManager

console = Console()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "manuscript_path",
    type=click.Path(exists=True, file_okay=False),
    required=False,
    metavar="[MANUSCRIPT_PATH]",
)
@click.option(
    "--output-dir",
    "-o",
    default="output",
    help="Output directory for generated files",
    metavar="DIR",
)
@click.option(
    "--force-figures", "-f", is_flag=True, help="Force regeneration of all figures"
)
@click.option("--skip-validation", "-s", is_flag=True, help="Skip validation step")
@click.option(
    "--track-changes",
    "-t",
    help="Track changes against specified git tag",
    metavar="TAG",
)
@click.pass_context
def build(
    ctx: click.Context,
    manuscript_path: str | None,
    output_dir: str,
    force_figures: bool,
    skip_validation: bool,
    track_changes: str | None,
) -> None:
    """Generate a publication-ready PDF from your Markdown manuscript with automated
    figure generation, professional typesetting, and bibliography management.

    **MANUSCRIPT_PATH**: Directory containing your manuscript files. Defaults to MANUSCRIPT/

    ## Examples

    **Build from default directory:**
    ```
    $ rxiv pdf
    ```

    **Build from custom directory:**
    ```
    $ rxiv pdf MY_PAPER/
    ```

    **Force regenerate all figures:**
    ```
    $ rxiv pdf --force-figures
    ```

    **Skip validation for debugging:**
    ```
    $ rxiv pdf --skip-validation
    ```

    **Track changes against git tag:**
    ```
    $ rxiv pdf --track-changes v1.0.0
    ```
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

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            # Create build manager
            task = progress.add_task("Initializing build manager...", total=None)
            build_manager = BuildManager(
                manuscript_path=manuscript_path,
                output_dir=output_dir,
                force_figures=force_figures,
                skip_validation=skip_validation,
                track_changes_tag=track_changes,
                verbose=verbose,
            )

            # Build the PDF
            progress.update(task, description="Generating PDF...")
            success = build_manager.run_full_build()

            if success:
                progress.update(task, description="✅ PDF generated successfully!")
                console.print(
                    f"📄 PDF generated: {output_dir}/{Path(manuscript_path).name}.pdf",
                    style="green",
                )

                # Show additional info
                if track_changes:
                    console.print(
                        f"🔍 Change tracking enabled against tag: {track_changes}",
                        style="blue",
                    )
                if force_figures:
                    console.print("🎨 All figures regenerated", style="blue")

            else:
                progress.update(task, description="❌ PDF generation failed")
                console.print(
                    "❌ PDF generation failed. Check output above for errors.",
                    style="red",
                )
                console.print("💡 Run with --verbose for more details", style="yellow")
                console.print(
                    "💡 Run 'rxiv validate' to check for issues", style="yellow"
                )
                sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n⏹️  PDF generation interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(1)
