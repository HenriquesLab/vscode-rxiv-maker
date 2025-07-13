# Complete Command Reference

This is the comprehensive command reference for Rxiv-Maker. All commands work with both local and Docker environments.

## 🚀 Quick Reference

| Task | Command | Docker Mode |
|------|---------|-------------|
| **Generate PDF** | `make pdf` | `make pdf RXIV_ENGINE=DOCKER` |
| **Validate manuscript** | `make validate` | `make validate RXIV_ENGINE=DOCKER` |
| **Setup environment** | `make setup` | `make setup RXIV_ENGINE=DOCKER` |
| **Run tests** | `pytest` | `make test RXIV_ENGINE=DOCKER` |
| **Clean outputs** | `make clean` | `make clean RXIV_ENGINE=DOCKER` |
| **Force figure regeneration** | `make pdf FORCE_FIGURES=true` | `make pdf FORCE_FIGURES=true RXIV_ENGINE=DOCKER` |

---

## 📋 Table of Contents

- [Environment Setup](#environment-setup)
- [PDF Generation](#pdf-generation)
- [Manuscript Validation](#manuscript-validation)
- [Figure Management](#figure-management)
- [Bibliography Management](#bibliography-management)
- [Testing Commands](#testing-commands)
- [Maintenance Commands](#maintenance-commands)
- [Docker Engine Mode](#docker-engine-mode)
- [Environment Variables](#environment-variables)
- [Troubleshooting Commands](#troubleshooting-commands)

---

## 🔧 Environment Setup

### Initial Setup

<details>
<summary><strong>Local Development Setup</strong></summary>

```bash
# Clone repository
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
make setup

# Alternative: reinstall dependencies (removes .venv and recreates)
make setup-reinstall
```

</details>

<details>
<summary><strong>Docker Development Setup</strong></summary>

```bash
# Clone repository
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker

# No additional setup needed - Docker handles dependencies
# Just verify Docker is running
docker --version

# Set Docker mode as default (optional)
export RXIV_ENGINE=DOCKER
echo 'export RXIV_ENGINE=DOCKER' >> ~/.bashrc  # Linux/macOS
```

</details>

### Platform Detection

```bash
# Check platform and show available commands
make help
```

---

## 📄 PDF Generation

### Basic PDF Generation

```bash
# Generate PDF from default manuscript (MANUSCRIPT/)
make pdf

# Generate PDF from specific manuscript directory
make pdf MANUSCRIPT_PATH=EXAMPLE_MANUSCRIPT
make pdf MANUSCRIPT_PATH=MY_PAPER

# Generate PDF with validation first (recommended)
make validate && make pdf
```

### Advanced PDF Generation

```bash
# Force regeneration of all figures
make pdf FORCE_FIGURES=true

# Generate PDF without validation (for debugging)
make pdf-no-validate

# Generate PDF with verbose output
make pdf VERBOSE=true

# Combine options
make pdf MANUSCRIPT_PATH=MY_PAPER FORCE_FIGURES=true VERBOSE=true
```

### Docker Mode PDF Generation

```bash
# Basic Docker PDF generation
make pdf RXIV_ENGINE=DOCKER

# Docker with specific manuscript
make pdf MANUSCRIPT_PATH=EXAMPLE_MANUSCRIPT RXIV_ENGINE=DOCKER

# Docker with all options
make pdf MANUSCRIPT_PATH=MY_PAPER FORCE_FIGURES=true RXIV_ENGINE=DOCKER
```

---

## ✅ Manuscript Validation

### Basic Validation

```bash
# Validate default manuscript
make validate

# Validate specific manuscript
make validate MANUSCRIPT_PATH=MY_PAPER

# Detailed validation with suggestions
python src/py/commands/validate.py MANUSCRIPT --detailed --verbose
```

### Advanced Validation

```bash
# Validate without DOI checking (for offline work)
python src/py/commands/validate.py MANUSCRIPT --no-doi

# Validate specific manuscript directly
python src/py/scripts/validate_manuscript.py MANUSCRIPT_PATH

# Validation with specific error analysis
python src/py/scripts/validate_manuscript.py MANUSCRIPT_PATH --detailed
```

### Docker Mode Validation

```bash
# Basic Docker validation
make validate RXIV_ENGINE=DOCKER

# Docker validation with specific manuscript
make validate MANUSCRIPT_PATH=MY_PAPER RXIV_ENGINE=DOCKER
```

---

## 🎨 Figure Management

### Figure Generation

```bash
# Generate all figures automatically (called by make pdf)
python src/py/commands/generate_figures.py --figures-dir MANUSCRIPT/FIGURES

# Generate figures with verbose output
python src/py/commands/generate_figures.py --figures-dir MANUSCRIPT/FIGURES --verbose

# Force regenerate all figures
make clean-figures && make pdf
```

### Figure Troubleshooting

```bash
# Clean generated figures
make clean-figures

# Test figure generation in isolation
cd MANUSCRIPT/FIGURES
source ../../.venv/bin/activate  # If using local development
python Figure_1.py              # Test specific figure script
```

### Docker Mode Figure Generation

```bash
# Force figure regeneration in Docker
make pdf FORCE_FIGURES=true RXIV_ENGINE=DOCKER

# Clean figures in Docker mode
make clean-figures RXIV_ENGINE=DOCKER
```

---

## 📚 Bibliography Management

### Bibliography Operations

```bash
# Fix bibliography issues automatically using CrossRef
make fix-bibliography

# Preview bibliography fixes without applying them
make fix-bibliography-dry-run

# Add bibliography entries from DOI(s)
make add-bibliography DOI=10.1000/example
```

### Bibliography Validation

```bash
# Test DOI validation specifically
python -c "from src.py.validators.doi_validator import DOIValidator; v = DOIValidator('MANUSCRIPT'); print(v.validate())"

# Check DOI cache status
python -c "from src.py.utils.doi_cache import DOICache; c = DOICache(); print(c.stats())"

# Clear DOI cache
rm .cache/doi_cache.json
```

---

## 🧪 Testing Commands

### Running Tests

<details>
<summary><strong>Local Development Testing</strong></summary>

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/py --cov-report=html

# Run specific test files
pytest tests/unit/test_md2tex.py
pytest tests/integration/

# Run tests for specific functionality
pytest tests/unit/test_figure_processor.py -v
pytest tests/unit/test_citation_processor.py -v
```

</details>

<details>
<summary><strong>Advanced Testing with Nox</strong></summary>

```bash
# Run tests across multiple Python versions
nox -s tests

# Run linting
nox -s lint

# Run type checking
nox -s type_check

# Run tests with coverage
nox -s coverage
```

</details>

<details>
<summary><strong>Direct Testing Commands</strong></summary>

```bash
# Lint code directly
ruff check src/
ruff format src/

# Type checking directly
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

</details>

### Docker Mode Testing

```bash
# Run all tests in Docker
make test RXIV_ENGINE=DOCKER

# Test specific manuscript in Docker
make test MANUSCRIPT_PATH=EXAMPLE_MANUSCRIPT RXIV_ENGINE=DOCKER
```

---

## 🧹 Maintenance Commands

### Cleaning Operations

```bash
# Clean output directory and generated figures
make clean

# Clean only figures
make clean-figures

# Clean only output directory
rm -rf output/
```

### Archive Operations

```bash
# Prepare arXiv submission package
make arxiv

# Prepare release package
make release
```

### System Information

```bash
# Show platform and system information
make help

# Check Python environment
python --version
which python

# Check LaTeX installation
pdflatex --version
which pdflatex
```

---

## 🐳 Docker Engine Mode

### Docker Setup

```bash
# Set Docker mode as default for session
export RXIV_ENGINE=DOCKER

# Use custom Docker image
export DOCKER_IMAGE=my/custom-image:tag
make pdf RXIV_ENGINE=DOCKER

# Check Docker status
docker --version
docker info
```

### Docker Commands

```bash
# All standard commands work with RXIV_ENGINE=DOCKER
make pdf RXIV_ENGINE=DOCKER
make validate RXIV_ENGINE=DOCKER
make test RXIV_ENGINE=DOCKER
make clean RXIV_ENGINE=DOCKER

# Docker-specific operations
docker images henriqueslab/rxiv-maker-base
docker run --rm henriqueslab/rxiv-maker-base:latest python --version
```

### Docker Image Management (Maintainers)

<details>
<summary><strong>Docker Image Build Commands</strong></summary>

```bash
cd src/docker

# Essential commands
make image-build      # Build multi-platform image locally (safe mode)
make image-push       # Build and push to DockerHub (safe mode)
make image-test       # Build and test image functionality
make login            # Login to Docker Hub

# Development commands  
make image-local      # Build for local testing only
make image-build-fast # Build without safe mode (faster, may crash)
make image-clean      # Clean up Docker resources
make info             # Show Docker system information
make help             # Show all available commands
```

</details>

---

## 🌍 Environment Variables

### Core Variables

```bash
# Manuscript path
export MANUSCRIPT_PATH=MY_PAPER

# Force figure regeneration
export FORCE_FIGURES=true

# Enable Docker mode
export RXIV_ENGINE=DOCKER

# Custom Docker image
export DOCKER_IMAGE=henriqueslab/rxiv-maker-base:latest

# Verbose output
export VERBOSE=true
```

### LaTeX Variables

```bash
# LaTeX temporary directory
export TEXMFVAR=/tmp/texmf-var

# Mermaid CLI options
export MERMAID_CLI_OPTIONS="--theme dark"
```

### Using .env File

```bash
# Create .env file in project root
cat > .env << EOF
MANUSCRIPT_PATH=MANUSCRIPT
FORCE_FIGURES=false
RXIV_ENGINE=LOCAL
EOF
```

---

## 🔍 Troubleshooting Commands

### Debugging PDF Generation

```bash
# Step-by-step debugging
make validate                    # Check for issues first
make clean-figures              # Clean figures
make pdf VERBOSE=true           # Generate with verbose output

# Manual LaTeX compilation
cd output
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

### Debugging Figure Generation

```bash
# Test figure generation in isolation
cd MANUSCRIPT/FIGURES
source ../../.venv/bin/activate
python Figure_1.py

# Check for missing dependencies
python -c "import matplotlib; print('matplotlib OK')"
python -c "import seaborn; print('seaborn OK')"
python -c "import pandas; print('pandas OK')"
```

### System Diagnostics

```bash
# Check all dependencies
make validate MANUSCRIPT_PATH=EXAMPLE_MANUSCRIPT

# Check Python environment
python -c "import sys; print(f'Python: {sys.executable}')"
python -c "import sys; print(f'Python path: {sys.path}')"

# Check LaTeX environment
which pdflatex
which bibtex
kpsewhich --var-value TEXMFHOME
```

### Docker Troubleshooting

```bash
# Test Docker setup
docker run --rm hello-world
docker run --rm henriqueslab/rxiv-maker-base:latest python --version

# Debug Docker container
docker run --rm -it henriqueslab/rxiv-maker-base:latest bash

# Check Docker resources
docker system df
docker images
docker ps -a
```

### Log Analysis

```bash
# Check output logs
ls -la output/*.log
tail -50 output/MANUSCRIPT.log

# Check for specific errors
grep -i error output/*.log
grep -i warning output/*.log

# Check figure generation logs
ls -la MANUSCRIPT/FIGURES/*/
```

---

## 📋 Command Combinations

### Recommended Workflows

```bash
# Full development workflow
make validate && make clean && make pdf

# Quick iteration during writing
make validate && make pdf

# Fresh build with new figures
make clean && make pdf FORCE_FIGURES=true

# Docker development workflow
make validate RXIV_ENGINE=DOCKER && make pdf RXIV_ENGINE=DOCKER
```

### Testing Workflows

```bash
# Pre-commit workflow
make validate && pytest && make pdf

# Full testing workflow
nox -s lint && nox -s type_check && nox -s tests

# Docker testing workflow
make test RXIV_ENGINE=DOCKER && make pdf RXIV_ENGINE=DOCKER
```

### Maintenance Workflows

```bash
# Clean rebuild
make clean && make setup && make pdf

# Docker clean rebuild
docker system prune -f && make pdf RXIV_ENGINE=DOCKER

# Environment refresh
make setup-reinstall && make pdf
```

---

## 🔗 Cross-Platform Notes

### Windows-Specific Commands

```powershell
# Windows PowerShell equivalents
.\.venv\Scripts\Activate.ps1     # Activate virtual environment
$env:RXIV_ENGINE="DOCKER"        # Set environment variable
```

### macOS/Linux-Specific Commands

```bash
source .venv/bin/activate         # Activate virtual environment
export RXIV_ENGINE=DOCKER        # Set environment variable
```

### Platform-Agnostic Commands

All `make` commands work identically across platforms:
- `make pdf`
- `make validate`
- `make setup`
- `make clean`

---

## 💡 Pro Tips

1. **Always validate first**: `make validate && make pdf`
2. **Use Docker for consistency**: `export RXIV_ENGINE=DOCKER`
3. **Test with example**: `make pdf MANUSCRIPT_PATH=EXAMPLE_MANUSCRIPT`
4. **Force figures when needed**: `make pdf FORCE_FIGURES=true`
5. **Clean before major changes**: `make clean && make pdf`
6. **Use verbose for debugging**: `make pdf VERBOSE=true`
7. **Combine commands efficiently**: `make validate && make pdf`

---

*This command reference serves as the authoritative source for all Rxiv-Maker commands. For installation help, see the [Installation Guide](../getting-started/installation.md). For workflows, see the [GitHub Actions Guide](../workflows/github-actions.md).*