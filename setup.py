"""Setup script for rxiv-maker with automatic system dependency installation."""

from pathlib import Path

from setuptools import find_packages, setup


def get_long_description():
    """Get long description from README."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return ""


def get_version():
    """Get version from _version.py."""
    try:
        # Try to import version from installed package
        from rxiv_maker._version import __version__

        return __version__
    except ImportError:
        # Fallback version for development
        return "1.4.0.dev0"


# Define requirements
requirements = [
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "scipy>=1.10.0",
    "Pillow>=9.0.0",
    "pypdf>=3.0.0",
    "PyYAML>=6.0.0",
    "python-dotenv>=1.0.0",
    "crossref-commons>=0.0.7",
    "lazydocs>=0.4.8",
    "types-requests>=2.32.4.20250611",
    "pytest>=7.4.4",
    "ruff>=0.12.2",
    "pre-commit>=4.2.0",
    "folder2md4llms>=0.3.0",
    "click>=8.0.0",
    "rich>=13.0.0",
    "rich-click>=1.6.0",
    "typing-extensions>=4.0.0",
    "packaging>=21.0.0",
]

# Define optional requirements
extras_require = {
    "dev": [
        "pytest>=7.4,<8.0",
        "py>=1.11.0",
        "ruff>=0.8.0",
        "mypy>=1.0",
        "types-PyYAML>=6.0.0",
        "nox>=2023.0.0",
        "pytest-cov>=4.0",
        "coverage[toml]>=7.0",
        "pytest-notebook>=0.10.0",
        "nbstripout>=0.7.1",
        "pre-commit>=4.0.0",
        "lazydocs>=0.4.8",
    ],
    "minimal": requirements,  # Same as base requirements
    "full": requirements,  # Same as base requirements (system deps handled separately)
}

setup(
    name="rxiv-maker",
    version=get_version(),
    author="Rxiv-Maker Contributors",
    author_email="rxiv.maker@gmail.com",
    description="Automated LaTeX article generation with universal system dependency installation",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/henriqueslab/rxiv-maker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing :: Markup :: LaTeX",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "rxiv=rxiv_maker.cli:main",
            "rxiv-install-deps=rxiv_maker.install.manager:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "latex",
        "markdown",
        "scientific-writing",
        "publishing",
        "automation",
        "cli",
        "command-line",
        "system-dependencies",
    ],
    project_urls={
        "Bug Reports": "https://github.com/henriqueslab/rxiv-maker/issues",
        "Source": "https://github.com/henriqueslab/rxiv-maker",
        "Documentation": "https://github.com/henriqueslab/rxiv-maker#readme",
    },
)
