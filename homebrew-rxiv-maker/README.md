# Homebrew Tap for rxiv-maker

This is the official Homebrew tap for [rxiv-maker](https://github.com/henriqueslab/rxiv-maker), providing easy installation of rxiv-maker and all its dependencies on macOS.

## 🚀 Quick Install

```bash
# Add the tap
brew tap henriqueslab/rxiv-maker https://github.com/henriqueslab/rxiv-maker

# Install rxiv-maker with all dependencies
brew install rxiv-maker

# Verify installation
rxiv --version
```

## 📦 What Gets Installed

The formula installs a complete local development environment including:

- **Python 3.11+** - Core runtime environment
- **LaTeX (BasicTeX)** - PDF generation engine
- **Node.js 20** - For Mermaid diagram generation
- **R** - For statistical figure generation
- **Essential LaTeX packages** - Common packages for scientific writing

## 🎯 Getting Started

After installation, create your first manuscript:

```bash
# Initialize a new manuscript
rxiv init my-paper/
cd my-paper/

# Edit your manuscript files
# - 00_CONFIG.yml (metadata and authors)
# - 01_MAIN.md (main content)
# - 03_REFERENCES.bib (bibliography)

# Generate PDF
rxiv build
```

## 🔄 Updates

Keep rxiv-maker up to date with standard Homebrew commands:

```bash
# Update tap and upgrade rxiv-maker
brew update && brew upgrade rxiv-maker

# Check for available updates
brew outdated rxiv-maker
```

## 🛠 Additional Setup

### LaTeX Packages
BasicTeX is installed with essential packages. Install additional packages as needed:
```bash
sudo tlmgr install <package-name>
```

### R Packages
Install R packages for your figure scripts:
```bash
R -e "install.packages(c('ggplot2', 'dplyr', 'readr', 'tidyr'))"
```

### Environment Check
Verify your installation and check for missing dependencies:
```bash
rxiv setup --check-all
```

## 🐛 Troubleshooting

### Common Issues

**Formula not found after adding tap:**
```bash
brew update
brew search rxiv-maker
```

**Permission issues with LaTeX:**
```bash
sudo chown -R $(whoami) /usr/local/texlive
```

**Python dependencies missing:**
```bash
rxiv setup --reinstall
```

**R packages not found:**
```bash
# Check R library path
R -e ".libPaths()"

# Install packages with specific path if needed
R -e "install.packages('ggplot2', lib='/usr/local/lib/R/4.3/site-library')"
```

### Getting Help

1. **Check environment**: `rxiv setup --check-all`
2. **Validate manuscript**: `rxiv validate`
3. **View logs**: Check `output/` directory for LaTeX logs
4. **Report issues**: [GitHub Issues](https://github.com/henriqueslab/rxiv-maker/issues)

## 🔧 Development

### Testing the Formula

```bash
# Test formula syntax
brew audit --strict rxiv-maker

# Install from source
brew install --build-from-source rxiv-maker

# Run formula tests
brew test rxiv-maker
```

### Local Formula Development

```bash
# Edit formula
edit homebrew-rxiv-maker/Formula/rxiv-maker.rb

# Test changes
brew reinstall --build-from-source ./homebrew-rxiv-maker/Formula/rxiv-maker.rb
```

## 📋 Formula Information

- **Source**: PyPI package `rxiv-maker`
- **License**: MIT
- **Dependencies**: Managed automatically by Homebrew
- **Auto-updates**: Via GitHub Actions on new releases

## 🆘 Support

- **Documentation**: [rxiv-maker README](https://github.com/henriqueslab/rxiv-maker#readme)
- **Issues**: [GitHub Issues](https://github.com/henriqueslab/rxiv-maker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/henriqueslab/rxiv-maker/discussions)

## 📄 License

This tap is released under the same MIT license as rxiv-maker.

---

**Made with ❤️ by the rxiv-maker team**