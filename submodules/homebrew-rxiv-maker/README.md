# Homebrew Formula for rxiv-maker

> **Status**: This repository contains the Homebrew formula for [rxiv-maker](https://github.com/HenriquesLab/rxiv-maker). The formula is being prepared for submission to [homebrew-core](https://github.com/Homebrew/homebrew-core) for easier installation.

A [Homebrew](https://brew.sh/) formula for installing [rxiv-maker](https://github.com/HenriquesLab/rxiv-maker), an automated LaTeX article generation system that transforms scientific writing from chaos to clarity.

Rxiv-Maker bridges the gap between **easy writing** (Markdown) and **beautiful output** (LaTeX), featuring automated figure generation from Python/R scripts and Mermaid diagrams, seamless citation management, and professional typesetting with zero LaTeX hassle.

## Repository Structure

This repository contains:
- `Formula/rxiv-maker.rb` - The main Homebrew formula for current use
- `rxiv-maker-core.rb` - Optimized formula for homebrew-core submission
- `HOMEBREW_CORE_SUBMISSION.md` - Guide for submitting to homebrew-core

## Installation

### Option 1: Using This Formula Repository
```bash
# Install directly from this repository
brew install HenriquesLab/rxiv-maker/rxiv-maker
```

### Option 2: Manual Formula Installation
```bash
# Clone this repository and install locally
git clone https://github.com/HenriquesLab/homebrew-rxiv-maker.git
brew install ./homebrew-rxiv-maker/Formula/rxiv-maker.rb
```

### Option 3: Future Direct Install (Coming Soon)
Once accepted into homebrew-core:
```bash
# Simple direct installation (future)
brew install rxiv-maker
```

### Alternative: PyPI Install
For immediate access to latest features:
```bash
pip install rxiv-maker
```

#### Prerequisites
- macOS 10.15+ or Linux
- [Homebrew](https://brew.sh/) package manager

### System Dependencies
rxiv-maker requires additional system dependencies for full functionality:

#### macOS
```bash
# Install LaTeX distribution (recommended)
brew install --cask mactex

# Or minimal LaTeX installation
brew install --cask basictex

# Git is usually pre-installed with Xcode Command Line Tools
# If not available:
xcode-select --install
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install texlive-full git make

# Fedora/CentOS/RHEL
sudo dnf install texlive-scheme-full git make

# Arch Linux
sudo pacman -S texlive-most git make
```

## Usage

After installation, the `rxiv` command will be available in your PATH:

```bash
# Initialize a new manuscript
rxiv init

# Generate PDF
rxiv pdf

# Show help
rxiv --help

# Check version
rxiv version
```

## Updating

```bash
# Update Homebrew and all packages
brew update && brew upgrade

# Update only rxiv-maker
brew upgrade rxiv-maker
```

## Uninstalling

```bash
# Remove rxiv-maker
brew uninstall rxiv-maker
```

## Troubleshooting

### Python Environment
rxiv-maker is installed in an isolated Python virtual environment to avoid conflicts with system Python packages. This follows Python PEP 668 best practices.

### LaTeX Issues
If you encounter LaTeX compilation errors:

#### macOS
1. Ensure MacTeX or BasicTeX is installed
2. Add LaTeX to PATH: `echo 'export PATH="/usr/local/texlive/2023/bin/universal-darwin:$PATH"' >> ~/.zshrc`
3. Reload shell: `source ~/.zshrc`
4. Verify: `which pdflatex`

#### Linux
1. Install full TeXLive distribution for best compatibility
2. Verify LaTeX installation: `pdflatex --version`
3. For Ubuntu/Debian: `sudo apt-get install texlive-latex-extra texlive-fonts-recommended`

### Permission Issues
If you encounter permission errors:
```bash
# Fix Homebrew permissions
sudo chown -R $(whoami) $(brew --prefix)/*

# Or reinstall Homebrew (if issues persist)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### PATH Issues
If `rxiv` command is not found:
```bash
# Check if Homebrew bin is in PATH
echo $PATH | grep $(brew --prefix)/bin

# Add to PATH if missing (zsh)
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Add to PATH if missing (bash)
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
```

## Development

This formula automatically tracks releases from the [official rxiv-maker PyPI package](https://pypi.org/project/rxiv-maker/).

### Manual Updates
To manually update the formula:
1. Check the latest version on PyPI
2. Update `Formula/rxiv-maker.rb`
3. Calculate new SHA256: `brew fetch --build-from-source ./Formula/rxiv-maker.rb`
4. Test the formula: `brew install --build-from-source ./Formula/rxiv-maker.rb`

### Testing
```bash
# Test formula syntax
brew audit --strict ./Formula/rxiv-maker.rb

# Test installation
brew install --verbose --debug ./Formula/rxiv-maker.rb

# Test functionality
rxiv --help
```

## Support

- **rxiv-maker Issues**: [GitHub Issues](https://github.com/HenriquesLab/rxiv-maker/issues)
- **Formula Issues**: [GitHub Issues](https://github.com/HenriquesLab/homebrew-rxiv-maker/issues)
- **Documentation**: [rxiv-maker README](https://github.com/HenriquesLab/rxiv-maker#readme)
- **Homebrew Docs**: [Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)

## License

This formula repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.

The rxiv-maker software is separately licensed. See the [rxiv-maker repository](https://github.com/HenriquesLab/rxiv-maker) for its license terms.

---

**© 2025 Jacquemet and Henriques Labs | Rxiv-Maker**  
*"Because science is hard enough without fighting with LaTeX."*