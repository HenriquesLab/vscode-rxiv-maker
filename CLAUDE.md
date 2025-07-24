# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rxiv-Maker is an automated LaTeX article generation system that converts scientific manuscripts from Markdown to publication-ready PDFs. It bridges the gap between easy writing (Markdown) and beautiful output (LaTeX) with automated figure generation, citations, and cross-references.

## Essential Commands

### CLI Commands (Modern Interface)
```bash
# Development Setup
rxiv setup                          # Install Python dependencies
rxiv setup --reinstall              # Reinstall dependencies (removes .venv and creates new one)

# PDF Generation
rxiv pdf                            # Generate PDF with validation (default: MANUSCRIPT/)
rxiv pdf MY_PAPER/                  # Use custom manuscript directory
rxiv pdf --force-figures            # Force regeneration of all figures
rxiv pdf --skip-validation          # Skip validation (for debugging)

# Manuscript Management
rxiv init                           # Initialize new manuscript (creates MANUSCRIPT/)
rxiv init MY_PAPER/                 # Initialize in custom directory
rxiv validate                       # Validate manuscript before building
rxiv validate --no-doi              # Skip DOI validation

# Figure Generation
rxiv figures                        # Generate figures only
rxiv figures --force                # Force regeneration of all figures

# Bibliography Management
rxiv bibliography fix               # Fix bibliography issues using CrossRef
rxiv bibliography fix --dry-run     # Preview fixes without applying
rxiv bibliography add 10.1000/doi   # Add bibliography entry from DOI
rxiv bibliography validate          # Validate bibliography entries

# Change Tracking
rxiv track-changes MANUSCRIPT/ v1.0.0  # Track changes against git tag

# Maintenance
rxiv clean                          # Clean output directory and generated figures
rxiv clean --figures-only           # Clean only generated figures
rxiv clean --cache-only             # Clean only cache files
rxiv arxiv                          # Prepare arXiv submission package

# Utility Commands
rxiv version                        # Show version information
rxiv version --detailed             # Show detailed version and system info
rxiv version --check-updates        # Check for package updates
rxiv config show                    # Show current configuration
rxiv config set general.check_updates false  # Disable update notifications
```

### Make Commands (Legacy Interface - Still Supported)
```bash
# Development Setup
make setup                           # Install Python dependencies (auto-detects platform)
make setup-reinstall                 # Reinstall dependencies (removes .venv and creates new one)

# PDF Generation
make pdf                            # Generate PDF with validation
MANUSCRIPT_PATH=path/to/manuscript make pdf  # Use custom manuscript directory  
make pdf FORCE_FIGURES=true         # Force regeneration of all figures
make pdf-no-validate               # Skip validation (for debugging)

# Change Tracking (requires latexdiff)
make pdf-track-changes TAG=v1.0.0   # Track changes against git tag
make pdf-track-changes TAG=v1.0.0 RXIV_ENGINE=DOCKER  # Docker mode

# Validation and Testing
make validate                       # Validate manuscript before building

# Bibliography Management
make fix-bibliography               # Fix bibliography issues using CrossRef
make fix-bibliography-dry-run       # Preview fixes without applying
make add-bibliography 10.1000/doi   # Add bibliography entry from DOI

# Testing and Code Quality
nox -s tests                       # Run tests across multiple Python versions
nox -s lint                        # Run linting
nox -s type_check                  # Run type checking
nox -s format                      # Format code with ruff
nox -s coverage                    # Run tests with coverage
nox -s integration                 # Run integration tests only
pytest tests/unit/                 # Run unit tests only
pytest tests/cli/                  # Run CLI tests only
pytest -m "not slow"               # Skip slow tests
pytest -k "test_specific"          # Run specific test
ruff check src/                    # Lint code directly
ruff format src/                   # Format code directly
mypy src/                         # Type checking directly

# Maintenance
make clean                         # Clean output directory and generated figures
make arxiv                        # Prepare arXiv submission package
```

## Architecture Overview

### Core Processing Pipeline
1. **Configuration Loading** - Parse YAML metadata from `00_CONFIG.yml`
2. **Figure Generation** - Execute Python/R scripts and Mermaid diagrams
3. **Markdown to LaTeX** - Convert enhanced Markdown with content protection
4. **LaTeX Compilation** - Generate final PDF with bibliography

### Key Components
- **CLI Module** (`src/rxiv_maker/cli/`) - Modern command-line interface with Click framework and update notifications
- **Converters** (`src/rxiv_maker/converters/`) - Process Markdown to LaTeX (figures, citations, math, tables)
- **Processors** (`src/rxiv_maker/processors/`) - Handle templates, YAML config, and author data
- **Commands** (`src/rxiv_maker/commands/`) - Main entry points (generate_preprint.py, validate.py, track_changes.py)
- **Validators** (`src/rxiv_maker/validators/`) - Validate citations, DOIs, figures, math, references

## Manuscript Structure

```
MANUSCRIPT/
├── 00_CONFIG.yml          # Metadata, authors, affiliations
├── 01_MAIN.md             # Main manuscript content
├── 02_SUPPLEMENTARY_INFO.md # Supplementary information
├── 03_REFERENCES.bib      # Bibliography
└── FIGURES/               # Figure generation scripts
    ├── Figure_1.py        # Python scripts
    ├── Figure_2.mmd       # Mermaid diagrams
    └── Figure_3.R         # R scripts
```

## rxiv-markdown Features

Enhanced Markdown with 20+ scientific features:
- Cross-references: `@fig:label`, `@table:label`, `@eq:label`, `@snote:label`
- Citations: `@citation`, `[@cite1;@cite2]`
- Text formatting: `~subscript~`, `^superscript^`
- Document control: `<newpage>`, `<clearpage>`

## Development Guidelines

### Code Style
- Use `ruff` for linting and formatting (configured in pyproject.toml)
- Follow Google-style docstrings, type hints for public APIs
- Line length: 88 characters, Python 3.11+ required

### Testing Strategy
- Unit tests (`tests/unit/`) for individual components
- Integration tests (`tests/integration/`) for full workflows
- CLI tests (`tests/cli/`) for command-line interface
- Use pytest fixtures for common test data
- Nox for cross-version testing (`nox -s tests`)
- Test markers: `unit`, `integration`, `cli`, `slow`, `validation`

### Common Development Patterns
- **Adding CLI Commands**: Create new command in `src/rxiv_maker/cli/commands/`, add to `__init__.py`, register in `main.py`
- **Adding Markdown Features**: Create processor in `src/rxiv_maker/converters/`, add to `md2tex.py` pipeline, add validation, write tests
- **Extending Figures**: Modify `generate_figures.py` and `figure_validator.py`
- **LaTeX Changes**: Update templates in `src/tex/` and `template_processor.py`

### Key Environment Variables
- `MANUSCRIPT_PATH` - Path to manuscript directory (default: MANUSCRIPT)
- `FORCE_FIGURES` - Force regeneration of figures (true/false)
- `RXIV_ENGINE` - Use Docker mode (DOCKER) or local mode (LOCAL)
- `PYTHONPATH` - Python path for development (set to src/ for local development)

## DOI Validation

The system includes DOI validation that verifies bibliography entries against the CrossRef API:
- **Format validation** using CrossRef regex patterns
- **Metadata verification** comparing title, journal, year, authors
- **Intelligent caching** in `.cache/doi_cache.json` (30 days)
- **Offline mode** via `--no-doi` flag

Example usage:
```bash
# Modern CLI
rxiv validate --no-doi              # Skip DOI validation

# Legacy command (still supported)
python src/rxiv_maker/commands/validate.py MANUSCRIPT --no-doi  # Skip DOI validation
```

## Cross-Platform Compatibility

Rxiv-Maker supports **Windows**, **macOS**, and **Linux** with automatic platform detection:
- **Windows**: Make (via chocolatey/scoop), LaTeX (MiKTeX/TeX Live)
- **macOS**: Make (via Xcode tools), LaTeX (MacTeX)  
- **Linux**: Make (via package manager), LaTeX (TeX Live with latexdiff)

## Troubleshooting

### Common Issues
- **LaTeX errors**: Run `make validate` for detailed error analysis
- **Figure failures**: Check scripts in FIGURES/ directory
- **Missing dependencies**: Run `make setup`
- **DOI validation failures**: Use `--no-doi` flag or check internet connection

### Debug Commands
```bash
# Modern CLI
rxiv validate --detailed            # Detailed validation report
rxiv figures --verbose              # Verbose figure generation
rxiv pdf --skip-validation          # Skip validation for debugging

# Legacy commands (still supported)
python src/rxiv_maker/scripts/validate_manuscript.py MANUSCRIPT_PATH --detailed
python src/rxiv_maker/commands/generate_figures.py --figures-dir MANUSCRIPT/FIGURES --verbose
cd output && pdflatex manuscript.tex  # Manual LaTeX compilation
```

## Docker Engine Mode

Rxiv-Maker supports Docker mode for containerised builds requiring only Docker and Make locally.

**⚠️ AMD64 only** due to Google Chrome ARM64 Linux limitations. ARM64 users should use local installation.

### Usage
```bash
# Use Docker for any command
make pdf RXIV_ENGINE=DOCKER              # Generate PDF in container
make validate RXIV_ENGINE=DOCKER         # Validate in container
make test RXIV_ENGINE=DOCKER             # Run tests in container

# Benefits: Minimal dependencies, reproducible builds, CI/CD ready
# Limitations: AMD64 only, slower on ARM64 via emulation
```

### Docker Image Management (Maintainers)
```bash
cd src/docker
make image-build      # Build image locally
make image-push       # Build and push to DockerHub
make image-test       # Test image functionality
```

## Modern CLI Interface

Rxiv-Maker now includes a modern command-line interface built with Click and Rich:

### Installation & Usage
```bash
# Install in development mode
pip install -e .

# Basic usage
rxiv --help                         # Show help
rxiv pdf                            # Build PDF from MANUSCRIPT/
rxiv pdf MY_PAPER/                  # Build from custom directory
rxiv init MY_PROJECT/               # Initialize new manuscript
```

### CLI Features
- **Rich output** with colors, progress bars, and formatted tables
- **Comprehensive help** with examples and usage tips
- **Auto-completion** support for bash/zsh/fish
- **Flexible arguments** supporting both positional and named parameters
- **Error handling** with helpful suggestions
- **Backward compatibility** with existing Make commands

### Engine Support
All CLI commands support both local and Docker execution:
```bash
rxiv pdf --engine docker            # Use Docker engine
rxiv pdf --engine local             # Use local engine (default)
```

### Migration from Make
The CLI provides equivalent functionality to Make commands:
```bash
# Old Make command      →   New CLI command
make setup              →   rxiv setup
make pdf                →   rxiv pdf
make validate           →   rxiv validate
make clean              →   rxiv clean
make arxiv              →   rxiv arxiv
```

## CLI Troubleshooting

### Common Issues and Solutions

#### CLI Command Not Found
```bash
# Problem: 'rxiv' command not found
# Solution: Install in development mode
pip install -e .

# Alternative: Use as module
python -m rxiv_maker.cli --help
```

#### Import Errors
```bash
# Problem: Module import errors
# Solution: Check Python path and dependencies
pip install -e . --force-reinstall

# Alternative: Use legacy commands
make setup && make pdf
```

#### Configuration Issues
```bash
# Problem: Configuration not working
# Solution: Reset configuration
rxiv config reset

# Check config file location
rxiv config show
```

#### Auto-completion Not Working
```bash
# Problem: Tab completion not working
# Solution: Reinstall completion
rxiv --install-completion bash  # or zsh, fish

# Restart shell
exec $SHELL
```

#### Legacy vs Modern Commands
```bash
# Both interfaces work simultaneously
make pdf                    # Legacy (always works)
rxiv pdf                    # Modern (after pip install -e .)

# Use whichever you prefer
```

### Development Environment Setup

```bash
# Recommended development setup
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker
pip install -e .                    # Install CLI in development mode
rxiv --install-completion bash      # Enable completion
rxiv config show                    # Check configuration

# Alternative: Use hatch for development
pip install hatch
hatch shell                         # Activate development environment
hatch run test                      # Run tests
hatch run lint                      # Run linting
hatch run type-check                # Run type checking
```

### CLI vs Make Integration

The CLI and Make commands are designed to work together:

- **CLI**: Modern interface with rich output and configuration
- **Make**: Traditional interface, always available as fallback
- **Makefile**: Updated to try CLI first, fall back to legacy
- **Docker**: Both interfaces support Docker mode
- **Environment**: Both respect the same environment variables

### Best Practices

1. **New Users**: Start with `rxiv` CLI for best experience
2. **Existing Users**: Continue with Make or gradually migrate
3. **Teams**: Document which interface you prefer
4. **CI/CD**: Both work identically in automation
5. **Debugging**: CLI provides better error messages

## Repository Structure

### Package Manager Repositories
Package manager repositories are maintained as separate GitHub repositories and included as git submodules:

- **Homebrew**: `submodules/homebrew-rxiv-maker/` → https://github.com/henriqueslab/homebrew-rxiv-maker.git
- **Scoop**: `submodules/scoop-rxiv-maker/` → https://github.com/henriqueslab/scoop-rxiv-maker.git
- **VS Code**: `submodules/vscode-rxiv-maker/` → https://github.com/HenriquesLab/vscode-rxiv-maker

### Directory Structure
```
rxiv-maker/
├── src/                     # Main source code
├── tests/                   # Test suites
├── docs/                    # Documentation
├── submodules/              # Git submodules for package managers
│   ├── homebrew-rxiv-maker/ # Homebrew tap (git submodule)
│   ├── scoop-rxiv-maker/    # Scoop bucket (git submodule)
│   └── vscode-rxiv-maker/   # VS Code extension (git submodule)
└── ...
```

## Package Management & Build System

Rxiv-Maker uses **hatch** for package management and versioning:

### Version Management
- Version is automatically managed by `hatch-vcs` from git tags
- Version file: `src/rxiv_maker/_version.py` (auto-generated)
- Fallback version: `1.4.0` (in pyproject.toml)

### Build Commands
```bash
# Build package
hatch build                         # Build wheel and sdist
hatch build --target wheel          # Build wheel only
hatch build --target sdist          # Build source distribution only

# Version info
hatch version                       # Show current version
git tag v1.5.0                      # Tag new version
hatch build                         # Build with new version
```

### Entry Points
- `rxiv` - Main CLI entry point (`rxiv_maker.cli:main`)
- `rxiv-install-deps` - System dependency installer (`rxiv_maker.install.manager:main`)

## Working with Git Submodules

### Initial Setup
```bash
# Clone repository with submodules
git clone --recurse-submodules https://github.com/henriqueslab/rxiv-maker.git

# Or initialize submodules after cloning
git submodule update --init --recursive
```

### Updating Submodules
```bash
# Update all submodules to latest commit
git submodule update --remote

# Update specific submodule
git submodule update --remote submodules/homebrew-rxiv-maker

# Commit submodule updates
git add .gitmodules submodules/
git commit -m "Update submodules to latest versions"
```

### Working with Submodules
```bash
# Work inside a submodule
cd submodules/homebrew-rxiv-maker
git checkout main
# Make changes, commit, push to submodule repository

# Update main repository to use new submodule commit
cd ../..
git add submodules/homebrew-rxiv-maker
git commit -m "Update homebrew submodule"
```

## Development Reminders

- Always activate virtual environment: `source .venv/bin/activate` or use `hatch shell`
- Do not acknowledge Claude when committing or doing PRs
- Write in UK English
- Use the modern CLI interface for new features
- Both CLI and Make commands are fully supported
- CLI provides better user experience and error handling
- Package manager repositories are managed as git submodules
- Use `hatch` for package management and `nox` for testing across Python versions