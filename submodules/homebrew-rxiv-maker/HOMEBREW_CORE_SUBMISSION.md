# Homebrew Core Submission Guide

This document outlines the process for submitting rxiv-maker to homebrew-core.

## Preparation

### Formula File: `rxiv-maker-core.rb`

The file `rxiv-maker-core.rb` contains the optimized formula ready for homebrew-core submission. Key features:

- **Dependencies**: 
  - `python@3.11` - Compatible Python version
  - `texlive` - LaTeX distribution for PDF generation
- **Installation**: Uses `virtualenv_install_with_resources` (homebrew-core standard)
- **Testing**: Comprehensive test suite verifying CLI functionality
- **Wrapper Script**: Proper executable wrapper for the CLI

### Submission Requirements Met

✅ **Stable Release**: Version 1.4.11 available on PyPI  
✅ **License**: MIT license clearly specified  
✅ **Homepage**: Valid GitHub repository URL  
✅ **Dependencies**: All system dependencies properly declared  
✅ **Tests**: Comprehensive test suite  
✅ **Description**: Clear, concise description under 80 characters  

## Submission Process

### 1. Fork homebrew-core
```bash
gh repo fork Homebrew/homebrew-core
cd homebrew-core
```

### 2. Create Formula
```bash
# Copy the optimized formula
cp /path/to/rxiv-maker-core.rb Formula/rxiv-maker.rb
```

### 3. Test Formula
```bash
# Install and test locally
brew install --build-from-source ./Formula/rxiv-maker.rb
brew test rxiv-maker
brew audit --strict rxiv-maker
```

### 4. Submit Pull Request
```bash
git checkout -b rxiv-maker
git add Formula/rxiv-maker.rb
git commit -m "rxiv-maker: new formula

Automated LaTeX article generation system with modern CLI and figure support.
Transforms scientific manuscripts from Markdown to publication-ready PDFs."
git push origin rxiv-maker
gh pr create --title "rxiv-maker: new formula" --body "..."
```

## Benefits After Acceptance

- **Simpler Installation**: `brew install rxiv-maker` (no tap needed)
- **Automatic Updates**: Updates managed by homebrew-core maintainers
- **Better Discoverability**: Listed in main Homebrew repository
- **Quality Assurance**: Tested by Homebrew's CI system

## Maintenance

Once accepted:
- Updates are handled through PR to homebrew-core
- Version bumps submitted by maintainers or automated tools
- This tap repository can be archived or redirected

## Current Status

- ✅ Formula optimized for homebrew-core
- ✅ Documentation updated
- ⏳ Awaiting submission
- ⏳ PR review process
- ⏳ Acceptance into homebrew-core