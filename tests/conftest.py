"""Pytest configuration and fixtures for Rxiv-Maker tests."""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """---
title: "Test Article"
authors:
  - name: "John Doe"
    affiliation: "Test University"
    email: "john@test.com"
keywords: ["test", "article"]
---

# Introduction

This is a test article with **bold** and *italic* text.

## Methods

We used @testcitation2023 for our methodology.

## Results

See @fig:test for results.

![Test Figure](FIGURES/test.png){#fig:test width="0.8"}
"""


@pytest.fixture
def sample_yaml_metadata():
    """Sample YAML metadata for testing."""
    return {
        "title": "Test Article",
        "authors": [
            {
                "name": "John Doe",
                "affiliation": "Test University",
                "email": "john@test.com",
            }
        ],
        "keywords": ["test", "article"],
    }


@pytest.fixture
def sample_tex_template():
    """Sample LaTeX template for testing."""
    return """\\documentclass{article}
\\title{<PY-RPL:LONG-TITLE-STR>}
\\author{<PY-RPL:AUTHORS-AND-AFFILIATIONS>}
\\begin{document}
\\maketitle
\\begin{abstract}
<PY-RPL:ABSTRACT>
\\end{abstract}
<PY-RPL:MAIN-CONTENT>
\\end{document}
"""


def check_latex_available():
    """Check if LaTeX is available in the system."""
    try:
        result = subprocess.run(
            ["pdflatex", "--version"], capture_output=True, text=True
        )
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def check_r_available():
    """Check if R is available in the system."""
    try:
        result = subprocess.run(["R", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


# Markers for conditional test execution
requires_latex = pytest.mark.skipif(
    not check_latex_available(), reason="LaTeX not available"
)

requires_r = pytest.mark.skipif(not check_r_available(), reason="R not available")
