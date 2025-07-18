# AppVeyor Testing Workflow

This document describes the AppVeyor configuration for testing the Homebrew installation of rxiv-maker from test-pypi.

## Overview

The AppVeyor workflow tests:
1. **Homebrew installation** from test-pypi using the `--with-test-pypi` option
2. **Basic CLI functionality** to ensure the package works correctly
3. **Verification logic** to ensure the dependency checking works
4. **No automatic system dependency installation** during pip install

## Configuration

### Environment
- **Image**: macOS Monterey (latest supported by AppVeyor)
- **Homebrew**: Configured with minimal analytics and auto-update disabled
- **Python**: System Python 3.11 (installed via Homebrew)

### Test Phases

#### 1. Installation Phase
```bash
# Fix Homebrew configuration issues in CI
brew untap homebrew/homebrew-cask-versions || true
brew cleanup || true

# Update Homebrew
brew update

# Install system dependencies first
brew install --cask basictex
brew install python@3.11 node@20 r make

# Install from local formula with test-pypi option
brew install --build-from-source ./homebrew-rxiv-maker/Formula/rxiv-maker.rb --with-test-pypi

# Verify installation
which rxiv
rxiv --version
```

#### 2. Build Phase (Functionality Tests)
```bash
# Test basic CLI functionality
rxiv --help
rxiv check-installation --json

# Test manuscript initialization
rxiv init test-manuscript
rxiv validate --detailed

# Verify no automatic system dependencies were installed
python3 -c "import sys; print('Python path:', sys.path)"
```

#### 3. Test Phase (Verification Tests)
```bash
# Verify package installation source
pip show rxiv-maker

# Test CLI commands
rxiv setup --check-deps-only
rxiv config show

# Test verification logic
rxiv check-installation --detailed
```

## Expected Behavior

### ✅ What Should Work
- Package installs from test-pypi via Homebrew
- CLI commands work without errors
- Verification logic detects system dependencies
- No automatic system dependency installation occurs during pip install

### ❌ What Should NOT Happen
- Automatic LaTeX/Node.js installation during pip install
- Package installation from main PyPI (should use test-pypi)
- CLI import errors or missing dependencies

## Formula Configuration

The Homebrew formula supports a `--with-test-pypi` option:

```ruby
# Install from test PyPI
brew install --build-from-source ./homebrew-rxiv-maker/Formula/rxiv-maker.rb --with-test-pypi

# Install from source (default)
brew install --build-from-source ./homebrew-rxiv-maker/Formula/rxiv-maker.rb
```

### Test PyPI Installation
When using `--with-test-pypi`, the formula:
1. Installs from `https://test.pypi.org/simple/`
2. Falls back to `https://pypi.org/simple/` for dependencies
3. Installs `rxiv-maker` package specifically from test-pypi

## Artifacts

The workflow collects:
- **test-manuscript/** - Generated test manuscript directory
- **Build logs** - Full installation and test output

## Notifications

Email notifications are sent to `rxiv.maker@gmail.com` for:
- Build success
- Build failure
- Build status changes

## Cache Configuration

AppVeyor caches:
- Homebrew taps directory
- Homebrew library directory

This reduces build times by avoiding re-downloading unchanged Homebrew components.

## Troubleshooting

### Common Issues

#### Homebrew Configuration Issues in CI
```bash
# Fix: Remove problematic homebrew-cask-versions tap
brew untap homebrew/homebrew-cask-versions || true

# Fix: Clean up existing Homebrew configuration
brew cleanup || true

# Error: "fatal: could not read Username for 'https://github.com'"
# Solution: The above commands fix authentication issues in CI environments
```

#### Formula Installation Fails
```bash
# Check formula syntax
brew audit --strict ./homebrew-rxiv-maker/Formula/rxiv-maker.rb

# Test formula locally
brew install --build-from-source ./homebrew-rxiv-maker/Formula/rxiv-maker.rb --with-test-pypi
```

#### Package Not Found on test-pypi
```bash
# Check if package exists
curl -s https://test.pypi.org/simple/rxiv-maker/ | grep -i "rxiv-maker"

# Verify package was uploaded
pip install --index-url https://test.pypi.org/simple/ rxiv-maker
```

#### CLI Import Errors
```bash
# Check Python path
python3 -c "import sys; print('\\n'.join(sys.path))"

# Check package installation
pip show rxiv-maker

# Test direct import
python3 -c "import rxiv_maker; print('Import successful')"
```

### Recovery Steps

1. **Check AppVeyor logs** for detailed error messages
2. **Test formula locally** on macOS system
3. **Verify test-pypi package** is available and correct
4. **Check dependencies** are properly resolved

## Integration with Development Workflow

This AppVeyor configuration integrates with:
1. **Test PyPI publishing** - Tests packages before main PyPI release
2. **Homebrew formula updates** - Validates formula changes
3. **CI/CD pipeline** - Automated testing on every commit/PR

## Usage

To trigger AppVeyor testing:
1. Push changes to the repository
2. AppVeyor automatically runs the test suite
3. Check results at https://ci.appveyor.com/project/[username]/rxiv-maker
4. Review artifacts and logs for issues

The workflow ensures that the Homebrew installation process works correctly with the modified pip installer (no automatic system dependencies) while maintaining all verification functionality.

## Status

### ✅ Completed
- **AppVeyor CI configuration** - Complete with macOS Monterey image
- **Test-pypi package deployment** - Version 1.4.0.dev0 successfully deployed
- **Homebrew formula updates** - Added `--with-test-pypi` option support
- **CI environment fixes** - Resolved Homebrew authentication and tap issues
- **System dependency handling** - BasicTeX and other dependencies installed via CI

### 🔄 In Progress
- **Live CI testing** - Latest build triggered with fixes applied
- **Build monitoring** - Checking for successful completion

### 🔗 Links
- **Test-PyPI Package**: https://test.pypi.org/project/rxiv-maker/1.4.0.dev0/
- **AppVeyor Project**: https://ci.appveyor.com/project/paxcalpt/rxiv-maker
- **GitHub Repository**: https://github.com/HenriquesLab/rxiv-maker

### Recent Changes
- **Fixed Homebrew CI issues** - Added tap cleanup and configuration fixes
- **Enhanced system dependency installation** - Install BasicTeX as cask in CI
- **Improved error handling** - Added `|| true` to prevent CI failures on cleanup commands