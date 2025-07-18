# Installing rxiv-maker via Homebrew

This guide shows you how to install rxiv-maker using Homebrew on macOS, providing a complete local development environment with all dependencies.

## 🎯 Quick Start

```bash
# Add the rxiv-maker tap
brew tap henriqueslab/rxiv-maker https://github.com/henriqueslab/rxiv-maker

# Install rxiv-maker with all dependencies
brew install rxiv-maker

# Verify installation
rxiv --version
```

## 📋 What You Get

The Homebrew installation provides a complete scientific writing environment:

### Core Components
- **rxiv-maker CLI** - Main command-line interface
- **Python 3.11+** - With scientific computing stack
- **LaTeX (BasicTeX)** - For PDF generation
- **Node.js 20** - For Mermaid diagrams
- **R** - For statistical figures

### Pre-installed LaTeX Packages
- `latexdiff` - For change tracking
- `biber` - Modern bibliography processing
- `biblatex` - Advanced bibliography management
- `pgfplots` - High-quality plots
- `adjustbox` - Box manipulation utilities

## 🚀 Creating Your First Manuscript

After installation, create and build your first manuscript:

```bash
# Create a new manuscript
rxiv init my-paper/
cd my-paper/

# The following files are created:
# ├── 00_CONFIG.yml          # Metadata and configuration
# ├── 01_MAIN.md             # Main manuscript content
# ├── 02_SUPPLEMENTARY_INFO.md # Supplementary information
# ├── 03_REFERENCES.bib      # Bibliography
# └── FIGURES/               # Directory for figure scripts

# Edit your content files
# Then generate the PDF:
rxiv build
```

## 🔧 Environment Setup

### Verify Installation
Check that all dependencies are properly installed:

```bash
rxiv setup --check-all
```

This will verify:
- Python environment and packages
- LaTeX installation and packages
- Node.js and npm
- R installation
- System tools (make, git)

### Configure Environment Variables
Customize rxiv-maker behavior with environment variables:

```bash
# Set custom manuscript directory
export MANUSCRIPT_PATH="my-custom-path/"

# Force local engine (vs Docker)
export RXIV_ENGINE="LOCAL"

# Enable verbose output
export RXIV_VERBOSE="1"

# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export MANUSCRIPT_PATH="manuscripts/"' >> ~/.zshrc
```

## 📦 Managing Dependencies

### LaTeX Packages
Install additional LaTeX packages as needed:

```bash
# Update tlmgr first
sudo tlmgr update --self

# Install specific packages
sudo tlmgr install algorithm2e
sudo tlmgr install siunitx
sudo tlmgr install glossaries

# Search for packages
tlmgr search --global <package-name>
```

### R Packages
Install R packages for statistical figure generation:

```bash
# Open R console
R

# Install common packages
install.packages(c(
  "ggplot2",      # Grammar of graphics
  "dplyr",        # Data manipulation
  "readr",        # Data import
  "tidyr",        # Data tidying
  "scales",       # Scale functions for visualization
  "patchwork",    # Combine plots
  "cowplot"       # Publication-ready plots
))

# Or install from command line
R -e "install.packages(c('ggplot2', 'dplyr'))"
```

### Node.js Packages
Mermaid CLI is automatically installed when needed, but you can install it globally:

```bash
npm install -g @mermaid-js/mermaid-cli
```

## 🔄 Updates and Maintenance

### Updating rxiv-maker
Keep rxiv-maker up to date with standard Homebrew commands:

```bash
# Update Homebrew and all formulas
brew update && brew upgrade

# Update only rxiv-maker
brew upgrade rxiv-maker

# Check for available updates
brew outdated | grep rxiv-maker
```

### Reinstalling Dependencies
If you encounter issues, reinstall Python dependencies:

```bash
# Reinstall Python virtual environment
rxiv setup --reinstall

# Or manually via pip
pip install --upgrade rxiv-maker
```

## 🎨 Usage Examples

### Basic Workflow
```bash
# Create manuscript
rxiv init nature-paper/
cd nature-paper/

# Edit configuration
editor 00_CONFIG.yml

# Write content
editor 01_MAIN.md

# Add bibliography
editor 03_REFERENCES.bib

# Generate figures (if any)
rxiv figures

# Build PDF
rxiv build

# Validate before submission
rxiv validate
```

### Advanced Features
```bash
# Force regenerate all figures
rxiv build --force-figures

# Skip validation for debugging
rxiv build --skip-validation

# Generate specific figures only
rxiv figures --pattern "Figure_1*"

# Track changes against previous version
rxiv track-changes v1.0.0

# Prepare arXiv submission
rxiv arxiv

# Clean build artifacts
rxiv clean
```

## 🐛 Troubleshooting

### Common Installation Issues

**Formula not found:**
```bash
# Update Homebrew and retry
brew update
brew search rxiv-maker

# Re-add tap if needed
brew untap henriqueslab/rxiv-maker
brew tap henriqueslab/rxiv-maker https://github.com/henriqueslab/rxiv-maker
```

**Permission errors with LaTeX:**
```bash
# Fix LaTeX directory permissions
sudo chown -R $(whoami) /usr/local/texlive

# Or use tlmgr user mode
tlmgr init-usertree
```

**Python package conflicts:**
```bash
# Clean install
brew uninstall rxiv-maker
brew install rxiv-maker

# Or reset Python environment
rxiv setup --reinstall
```

### Build Issues

**Missing LaTeX packages:**
```bash
# Check what's missing
rxiv validate --detailed

# Install missing packages
sudo tlmgr install <package-name>
```

**Figure generation fails:**
```bash
# Check figure scripts
ls FIGURES/
rxiv figures --verbose

# Test individual scripts
python FIGURES/Figure_1.py
```

**Bibliography errors:**
```bash
# Validate DOIs
rxiv bibliography validate

# Fix bibliography formatting
rxiv bibliography fix
```

### Getting Help

1. **Run diagnostics**: `rxiv setup --check-all`
2. **Validate manuscript**: `rxiv validate --detailed`
3. **Check logs**: Look in `output/` directory for detailed error logs
4. **Community support**: 
   - [GitHub Issues](https://github.com/henriqueslab/rxiv-maker/issues)
   - [GitHub Discussions](https://github.com/henriqueslab/rxiv-maker/discussions)

## 🔍 Comparison with Other Installation Methods

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Homebrew** | Easy install, dependency management, automatic updates | macOS only, requires admin for LaTeX | Mac users wanting complete setup |
| **PyPI** | Cross-platform, latest versions | Manual dependency management | Python developers |
| **Docker** | Isolated environment, reproducible | Requires Docker, slower | CI/CD, isolated testing |
| **Google Colab** | Zero installation, cloud-based | Internet required, limited customization | Quick testing, tutorials |

## 📚 Next Steps

After installation, explore these resources:

- **[User Guide](../getting-started/user_guide.md)** - Comprehensive usage guide
- **[CLI Reference](../CLI_REFERENCE.md)** - Complete command reference
- **[Examples](../EXAMPLE_MANUSCRIPT/)** - Example manuscript to learn from
- **[Troubleshooting](../troubleshooting/)** - Common issues and solutions

---

**Questions?** Check our [FAQ](https://github.com/henriqueslab/rxiv-maker/discussions/categories/q-a) or [start a discussion](https://github.com/henriqueslab/rxiv-maker/discussions).