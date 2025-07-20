"""Track changes command for rxiv-maker CLI."""

import os

import click
from rich.console import Console

console = Console()


@click.command()
@click.argument(
    "manuscript_path", type=click.Path(exists=True, file_okay=False), required=False
)
@click.argument("tag", required=True)
@click.option(
    "--output-dir", "-o", default="output", help="Output directory for generated files"
)
@click.pass_context
def track_changes(
    ctx: click.Context, manuscript_path: str | None, tag: str, output_dir: str
) -> None:
    """Generate PDF with change tracking against a git tag.

    MANUSCRIPT_PATH: Path to manuscript directory (default: MANUSCRIPT)
    TAG: Git tag to track changes against
    """
    # Default to MANUSCRIPT if not specified
    if manuscript_path is None:
        manuscript_path = os.environ.get("MANUSCRIPT_PATH", "MANUSCRIPT")

    # Call build command with track-changes option
    from .build import build

    # Create new context with track-changes option
    new_ctx = click.Context(build, obj=ctx.obj)
    new_ctx.invoke(
        build,
        manuscript_path=manuscript_path,
        output_dir=output_dir,
        force_figures=False,
        skip_validation=False,
        track_changes=tag,
    )
