"""Bibliography commands for rxiv-maker CLI."""

import os
import re
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def _is_doi_like(input_string: str) -> bool:
    """Check if a string looks like a DOI (in any supported format).

    Args:
        input_string: String to check

    Returns:
        True if the string looks like a DOI, False otherwise
    """
    if not input_string or not isinstance(input_string, str):
        return False

    input_string = input_string.strip()

    # Check for DOI URL patterns
    if input_string.startswith(("https://doi.org/", "http://doi.org/", "doi.org/")):
        return True

    # Check for direct DOI pattern (10.xxxx/yyyy)
    doi_pattern = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
    return bool(doi_pattern.match(input_string))


def _normalize_doi(doi_input: str) -> str | None:
    """Normalize DOI input to standard format.

    Accepts DOIs in formats:
    - 10.xxxx/yyyy
    - https://doi.org/10.xxxx/yyyy
    - http://doi.org/10.xxxx/yyyy
    - doi.org/10.xxxx/yyyy

    Returns:
        Normalized DOI string (10.xxxx/yyyy format) or None if invalid
    """
    # Remove whitespace
    doi_input = doi_input.strip()

    # Handle URL formats
    if doi_input.startswith(("https://doi.org/", "http://doi.org/")):
        doi_input = doi_input.replace("https://doi.org/", "").replace("http://doi.org/", "")
    elif doi_input.startswith("doi.org/"):
        doi_input = doi_input.replace("doi.org/", "")

    # Validate the final DOI format using CrossRef's pattern
    doi_pattern = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)

    if doi_pattern.match(doi_input):
        return doi_input

    return None


@click.group()
def bibliography():
    """Bibliography management commands."""
    pass


@bibliography.command()
@click.argument("manuscript_path", type=click.Path(exists=True, file_okay=False), required=False)
@click.option("--dry-run", "-d", is_flag=True, help="Preview fixes without applying them")
@click.pass_context
def fix(ctx: click.Context, manuscript_path: str | None, dry_run: bool) -> None:
    """Fix bibliography issues automatically.

    MANUSCRIPT_PATH: Path to manuscript directory (default: MANUSCRIPT)

    This command searches CrossRef to fix bibliography issues.
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
        sys.exit(1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Fixing bibliography...", total=None)

            # Import bibliography fixing command
            from ...commands.fix_bibliography import main as fix_bibliography_main

            # Prepare arguments
            args = [manuscript_path]
            if dry_run:
                args.append("--dry-run")
            if verbose:
                args.append("--verbose")

            # Save original argv and replace
            original_argv = sys.argv
            sys.argv = ["fix_bibliography"] + args

            try:
                fix_bibliography_main()
                progress.update(task, description="✅ Bibliography fixes completed")
                if dry_run:
                    console.print("✅ Bibliography fixes preview completed!", style="green")
                else:
                    console.print("✅ Bibliography fixes applied successfully!", style="green")

            except SystemExit as e:
                progress.update(task, description="❌ Bibliography fixing failed")
                if e.code != 0:
                    console.print("❌ Bibliography fixing failed. See details above.", style="red")
                    sys.exit(1)

            finally:
                sys.argv = original_argv

    except KeyboardInterrupt:
        console.print("\\n⏹️  Bibliography fixing interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error during bibliography fixing: {e}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(1)


@bibliography.command()
@click.argument("dois", nargs=-1, required=True)
@click.option(
    "--manuscript-path",
    "-m",
    type=str,
    default=None,
    help="Path to manuscript directory (default: MANUSCRIPT or $MANUSCRIPT_PATH)",
)
@click.option("--overwrite", "-o", is_flag=True, help="Overwrite existing entries")
@click.pass_context
def add(
    ctx: click.Context,
    dois: tuple[str, ...],
    manuscript_path: str | None,
    overwrite: bool,
) -> None:
    """Add bibliography entries from DOIs.

    DOIS: One or more DOIs to add

    Examples:
    rxiv bibliography add 10.1000/example.doi
    rxiv bibliography add https://doi.org/10.1038/d41586-022-00563-z
    rxiv bibliography add 10.1000/ex1 10.1000/ex2
    rxiv bibliography add -m ./my_manuscript https://doi.org/10.1000/example
    """
    verbose = ctx.obj.get("verbose", False)

    # Default to MANUSCRIPT if not specified
    actual_manuscript_path = manuscript_path
    if actual_manuscript_path is None:
        actual_manuscript_path = os.environ.get("MANUSCRIPT_PATH", "MANUSCRIPT")

    # Validate manuscript path exists and is a directory
    manuscript_path_obj = Path(actual_manuscript_path)
    if not manuscript_path_obj.exists():
        console.print(
            f"❌ Error: Manuscript directory '{actual_manuscript_path}' does not exist",
            style="red",
        )
        sys.exit(1)

    if not manuscript_path_obj.is_dir():
        console.print(
            f"❌ Error: '{actual_manuscript_path}' is not a directory",
            style="red",
        )
        sys.exit(1)

    # Validate and normalize DOIs
    normalized_dois = []
    for doi in dois:
        normalized_doi = _normalize_doi(doi)
        if not normalized_doi:
            console.print(
                f"❌ Error: Invalid DOI format '{doi}'. "
                f"DOIs should be in format '10.xxxx/yyyy' or 'https://doi.org/10.xxxx/yyyy'",
                style="red",
            )
            sys.exit(1)
        normalized_dois.append(normalized_doi)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(f"Adding {len(normalized_dois)} bibliography entries...", total=None)

            # Import bibliography adding command
            from ...commands.add_bibliography import main as add_bibliography_main

            # Prepare arguments
            args = [actual_manuscript_path] + normalized_dois
            if overwrite:
                args.append("--overwrite")
            if verbose:
                args.append("--verbose")

            # Save original argv and replace
            original_argv = sys.argv
            sys.argv = ["add_bibliography"] + args

            try:
                add_bibliography_main()
                progress.update(task, description="✅ Bibliography entries added")
                console.print(
                    f"✅ Added {len(normalized_dois)} entries successfully!",
                    style="green",
                )
                console.print(f"📚 DOIs added: {', '.join(normalized_dois)}", style="blue")

            except SystemExit as e:
                progress.update(task, description="❌ Bibliography adding failed")
                if e.code != 0:
                    console.print("❌ Bibliography adding failed. See details above.", style="red")
                    sys.exit(1)

            finally:
                sys.argv = original_argv

    except KeyboardInterrupt:
        console.print("\\n⏹️  Bibliography adding interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error during bibliography adding: {e}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(1)


@bibliography.command()
@click.argument("manuscript_path", type=click.Path(exists=True, file_okay=False), required=False)
@click.option("--no-doi", is_flag=True, help="Skip DOI validation")
@click.pass_context
def validate(ctx: click.Context, manuscript_path: str | None, no_doi: bool) -> None:
    """Validate bibliography entries.

    MANUSCRIPT_PATH: Path to manuscript directory (default: MANUSCRIPT)

    This command validates bibliography entries for:
    - Correct format
    - DOI validity
    - Required fields
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
        sys.exit(1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Validating bibliography...", total=None)

            # Import validation command (we'll use the main validate command)
            from ...commands.validate import main as validate_main

            # Prepare arguments
            args = [manuscript_path]
            if no_doi:
                args.append("--no-doi")
            if verbose:
                args.append("--verbose")

            # Save original argv and replace
            original_argv = sys.argv
            sys.argv = ["validate"] + args

            try:
                validate_main()
                progress.update(task, description="✅ Bibliography validation completed")
                console.print("✅ Bibliography validation passed!", style="green")

            except SystemExit as e:
                progress.update(task, description="❌ Bibliography validation failed")
                if e.code != 0:
                    console.print(
                        "❌ Bibliography validation failed. See details above.",
                        style="red",
                    )
                    sys.exit(1)

            finally:
                sys.argv = original_argv

    except KeyboardInterrupt:
        console.print("\\n⏹️  Bibliography validation interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error during bibliography validation: {e}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(1)
