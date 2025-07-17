"""Main CLI entry point for rxiv-maker."""

import os
import sys
from pathlib import Path

import rich_click as click
from rich.console import Console

# Configure rich-click for better help formatting
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.SHOW_METAVARS_COLUMN = True
click.rich_click.APPEND_METAVARS_HELP = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
click.rich_click.ERRORS_SUGGESTION = "Try '{command} --help' for more information."
click.rich_click.STYLE_HELPTEXT_FIRST_LINE = "bold"
click.rich_click.STYLE_HELPTEXT = "dim"
click.rich_click.STYLE_OPTION = "bold cyan"
click.rich_click.STYLE_ARGUMENT = "bold yellow"
click.rich_click.STYLE_COMMAND = "bold green"
click.rich_click.STYLE_SWITCH = "bold red"
click.rich_click.STYLE_METAVAR = "bold blue"
click.rich_click.STYLE_USAGE = "bold"
click.rich_click.STYLE_USAGE_COMMAND = "bold green"
click.rich_click.STYLE_USAGE_ARGS = "bold yellow"
click.rich_click.STYLE_HELP_PANEL_BORDER = "blue"
click.rich_click.STYLE_HELP_PANEL_TITLE = "bold blue"

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .. import __version__
from ..utils.update_checker import check_for_updates_async, show_update_notification
from . import commands
from .commands.check_installation import check_installation
from .config import config_cmd

console = Console()


class UpdateCheckGroup(click.Group):
    """Custom Click group that handles update checking."""

    def invoke(self, ctx):
        """Invoke command and handle update checking."""
        try:
            # Start update check in background (non-blocking)
            check_for_updates_async()

            # Invoke the actual command
            result = super().invoke(ctx)

            # Show update notification after command completes
            # Only if command was successful and not disabled
            if not ctx.obj.get("no_update_check", False):
                show_update_notification()

            return result
        except Exception:
            # Always re-raise exceptions from commands
            raise


@click.group(cls=UpdateCheckGroup)
@click.version_option(version=__version__, prog_name="rxiv")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--engine",
    type=click.Choice(["local", "docker"]),
    default="local",
    help="Engine to use for processing (local or docker)",
)
@click.option(
    "--install-completion",
    type=click.Choice(["bash", "zsh", "fish"]),
    help="Install shell completion for the specified shell",
)
@click.option(
    "--no-update-check", is_flag=True, help="Skip update check for this command"
)
@click.pass_context
def main(
    ctx: click.Context,
    verbose: bool,
    engine: str,
    install_completion: str | None,
    no_update_check: bool,
) -> None:
    """**Rxiv-Maker**: Automated LaTeX article generation from Markdown.

    Transform your Markdown manuscripts into publication-ready PDFs with:

    - ✨ **Automated figure generation** from Python/R scripts
    - 📄 **Professional LaTeX typesetting** with zero LaTeX knowledge required
    - 📚 **Bibliography management** with automatic DOI validation
    - 🔗 **Cross-reference resolution** for figures, tables, and equations
    - 🐳 **Docker support** for reproducible builds
    - 🔄 **Change tracking** against git tags

    **Quick Start:**
    ```bash
    rxiv init MY_PAPER/          # Initialize new manuscript
    rxiv build                   # Generate PDF
    rxiv build --force-figures   # Force regenerate figures
    rxiv arxiv                   # Prepare arXiv submission
    ```

    **Examples:**
    ```bash
    rxiv build MANUSCRIPT/       # Build from specific directory
    rxiv build --engine docker   # Use Docker engine
    rxiv validate --no-doi       # Validate without DOI checks
    rxiv bibliography fix        # Fix bibliography issues
    ```
    """
    # Handle completion installation
    if install_completion:
        install_shell_completion(install_completion)
        return

    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["engine"] = engine
    ctx.obj["no_update_check"] = no_update_check

    # Set environment variables
    os.environ["RXIV_ENGINE"] = engine.upper()
    if verbose:
        os.environ["RXIV_VERBOSE"] = "1"
    if no_update_check:
        os.environ["RXIV_NO_UPDATE_CHECK"] = "1"


def install_shell_completion(shell: str) -> None:
    """Install shell completion for the specified shell."""
    console.print(f"Installing {shell} completion...", style="blue")

    try:
        if shell == "bash":
            completion_script = "_RXIV_COMPLETE=bash_source rxiv"
            install_path = Path.home() / ".bashrc"

        elif shell == "zsh":
            completion_script = "_RXIV_COMPLETE=zsh_source rxiv"
            install_path = Path.home() / ".zshrc"

        elif shell == "fish":
            completion_script = "_RXIV_COMPLETE=fish_source rxiv"
            install_path = Path.home() / ".config/fish/config.fish"

        # Add completion to shell config
        completion_line = f'eval "$({completion_script})"'

        # Check if already installed
        if install_path.exists():
            content = install_path.read_text()
            if completion_line in content:
                console.print(f"✅ {shell} completion already installed", style="green")
                return

        # Add completion
        with open(install_path, "a") as f:
            f.write(f"\n# Rxiv-Maker completion\n{completion_line}\n")

        console.print(
            f"✅ {shell} completion installed to {install_path}", style="green"
        )
        console.print(
            f"💡 Restart your shell or run: source {install_path}", style="yellow"
        )

    except Exception as e:
        console.print(f"❌ Error installing completion: {e}", style="red")


# Register command groups
main.add_command(commands.build)
main.add_command(commands.validate)
main.add_command(commands.clean)
main.add_command(commands.figures)
main.add_command(commands.arxiv)
main.add_command(commands.init)
main.add_command(commands.bibliography)
main.add_command(commands.track_changes)
main.add_command(commands.setup)
main.add_command(commands.version)
main.add_command(config_cmd, name="config")
main.add_command(check_installation, name="check-installation")

if __name__ == "__main__":
    main()
