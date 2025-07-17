"""Commands for the rxiv-maker CLI."""

from .arxiv import arxiv
from .bibliography import bibliography
from .build import build
from .check_installation import check_installation
from .clean import clean
from .figures import figures
from .init import init
from .setup import setup
from .track_changes import track_changes
from .validate import validate
from .version import version

__all__ = [
    "arxiv",
    "bibliography",
    "build",
    "check_installation",
    "clean",
    "figures",
    "init",
    "setup",
    "track_changes",
    "validate",
    "version",
]
