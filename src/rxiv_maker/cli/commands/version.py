"""Version command for rxiv-maker CLI."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ... import __version__
from ...utils.platform import platform_detector
from ...utils.update_checker import force_update_check

console = Console()


@click.command()
@click.option(
    "--detailed", "-d", is_flag=True, help="Show detailed version information"
)
@click.option("--check-updates", "-u", is_flag=True, help="Check for available updates")
@click.pass_context
def version(ctx: click.Context, detailed: bool, check_updates: bool) -> None:
    """Show version information."""
    # Check for updates if requested
    if check_updates:
        console.print("🔍 Checking for updates...", style="blue")
        try:
            update_available, latest_version = force_update_check()
            if update_available:
                console.print(
                    f"📦 Update available: {__version__} → {latest_version}",
                    style="green",
                )
                console.print("   Run: pip install --upgrade rxiv-maker", style="blue")
                console.print(
                    f"   Release notes: https://github.com/henriqueslab/rxiv-maker/releases/tag/v{latest_version}",
                    style="blue",
                )
            else:
                console.print(
                    f"✅ You have the latest version ({__version__})", style="green"
                )
        except Exception as e:
            console.print(f"❌ Could not check for updates: {e}", style="red")
        console.print()  # Add spacing

    if detailed:
        # Create detailed version table
        table = Table(title="Rxiv-Maker Version Information")
        table.add_column("Component", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Status", style="yellow")

        # Add version info
        table.add_row("Rxiv-Maker", __version__, "✅ Installed")

        # Add platform info
        table.add_row("Platform", platform_detector.platform, "✅ Detected")
        table.add_row("Python", f"{sys.version.split()[0]}", "✅ Compatible")

        # Add dependency info
        try:
            import click

            table.add_row("Click", click.__version__, "✅ Available")
        except ImportError:
            table.add_row("Click", "Not found", "❌ Missing")

        try:
            # Rich doesn't have __version__, try getting it from __init__
            try:
                from rich import __version__ as rich_version

                table.add_row("Rich", rich_version, "✅ Available")
            except ImportError:
                table.add_row("Rich", "Available", "✅ Available")
        except ImportError:
            table.add_row("Rich", "Not found", "❌ Missing")

        try:
            import matplotlib

            table.add_row("Matplotlib", matplotlib.__version__, "✅ Available")
        except ImportError:
            table.add_row("Matplotlib", "Not found", "❌ Missing")

        console.print(table)

        # Show additional info
        console.print(
            f"\n📁 Installation path: {Path(__file__).parent.parent.parent.absolute()}",
            style="blue",
        )
        console.print(f"🐍 Python executable: {sys.executable}", style="blue")

    else:
        # Simple version output
        console.print(f"rxiv-maker {__version__}", style="green")
