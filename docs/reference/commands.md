# Command Reference

Essential commands for Rxiv-Maker. All commands work with both local and Docker environments.

## Quick Reference

| Task | Local Command | Docker Command |
|------|---------------|----------------|
| **Generate PDF** | `make pdf` | `make pdf RXIV_ENGINE=DOCKER` |
| **Validate manuscript** | `make validate` | `make validate RXIV_ENGINE=DOCKER` |
| **Setup environment** | `make setup` | Not needed (dependencies in container) |
| **Force figure regeneration** | `make pdf FORCE_FIGURES=true` | `make pdf FORCE_FIGURES=true RXIV_ENGINE=DOCKER` |
| **Track changes vs git tag** | `make pdf-track-changes TAG=v1.0.0` | `make pdf-track-changes TAG=v1.0.0 RXIV_ENGINE=DOCKER` |
| **Clean outputs** | `make clean` | `make clean RXIV_ENGINE=DOCKER` |

## Environment Setup

### Local Development
```bash
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker
make setup && make pdf
```

### Docker Development  
```bash
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker
make pdf RXIV_ENGINE=DOCKER
```

## PDF Generation

### Basic Commands
```bash
# Generate PDF from default manuscript
make pdf

# Generate PDF from specific manuscript directory
make pdf MANUSCRIPT_PATH=MY_PAPER
# Force regeneration of all figures
make pdf FORCE_FIGURES=true

# Generate PDF without validation (for debugging)
make pdf-no-validate
```

## Change Tracking

Generate PDFs highlighting differences against git tags:

```bash
# Track changes against a git tag
make pdf-track-changes TAG=v1.0.0

# Track changes for specific manuscript
make pdf-track-changes TAG=v1.2.0 MANUSCRIPT_PATH=MY_PAPER

# Track changes using Docker mode
make pdf-track-changes TAG=v1.0.0 RXIV_ENGINE=DOCKER
```

## Validation and Testing

```bash
# Validate manuscript before building
make validate

# Skip DOI validation
python src/py/commands/validate.py MANUSCRIPT --no-doi

# Run tests
pytest tests/
nox -s tests                       # Multiple Python versions
```

## Bibliography Management

```bash
# Fix bibliography issues automatically
make fix-bibliography

# Preview fixes without applying
make fix-bibliography-dry-run

# Add bibliography entry from DOI
make add-bibliography 10.1000/doi
```

## Maintenance

```bash
# Clean output directory and figures
make clean

# Clean specific components
make clean-output                  # Output directory only
make clean-figures                 # Generated figures only
make clean-cache                   # Cache files only

# Prepare arXiv submission
make arxiv
```

## Environment Variables

```bash
# Key variables (can be set in .env file)
MANUSCRIPT_PATH=MY_PAPER          # Manuscript directory
FORCE_FIGURES=true                # Force figure regeneration
RXIV_ENGINE=DOCKER                # Use Docker mode
```

## Troubleshooting

```bash
# Detailed validation with error analysis
python src/py/scripts/validate_manuscript.py MANUSCRIPT_PATH --detailed

# Test figure generation in isolation
python src/py/commands/generate_figures.py --figures-dir MANUSCRIPT/FIGURES --verbose

# Manual LaTeX compilation
cd output && pdflatex manuscript.tex
```

For complete documentation, see:
- [User Guide](../getting-started/user_guide.md) for detailed usage
- [Docker Guide](../workflows/docker-engine-mode.md) for containerized builds
- [GitHub Actions Guide](../workflows/github-actions.md) for automated builds