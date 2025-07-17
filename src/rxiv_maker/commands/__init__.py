"""Command-line interface modules for Rxiv-Maker.

This package contains the main executable scripts for article and figure generation.
"""

from .generate_figures import FigureGenerator
from .generate_figures import main as figures_main
from .generate_preprint import generate_preprint
from .generate_preprint import main as preprint_main

__all__ = ["generate_preprint", "preprint_main", "FigureGenerator", "figures_main"]
