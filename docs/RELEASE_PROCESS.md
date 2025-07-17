# Release Process Guide

This guide explains how to release new versions of rxiv-maker to both PyPI and Homebrew.

## Overview

The release process involves two separate workflows:
1. **PyPI Publishing** - Automated via GitHub Actions
2. **Homebrew Formula Update** - Manual trigger or scheduled update

## Prerequisites

### PyPI API Tokens

Set up PyPI API tokens for secure publishing:

#### 1. Production PyPI Token
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Create API token with scope limited to `rxiv-maker` project
3. Copy the token (starts with `pypi-`)

#### 2. Test PyPI Token (Optional)
1. Go to [Test PyPI Account Settings](https://test.pypi.org/manage/account/)
2. Create API token with scope limited to `rxiv-maker` project
3. Copy the token (starts with `pypi-`)

#### 3. Add Secrets to GitHub Repository
1. Go to repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `PYPI_API_TOKEN` - Production PyPI token
   - `TESTPYPI_API_TOKEN` - Test PyPI token (optional)

### GitHub Environments (Recommended)

Set up GitHub environments for additional security:

1. Go to repository Settings → Environments
2. Create environments:
   - `pypi` - For production releases
   - `testpypi` - For test releases
3. Configure protection rules:
   - Required reviewers (for production)
   - Deployment branches (only `main` for production)

## Release Workflow

### 1. Prepare Release

```bash
# 1. Ensure you're on main branch
git checkout main
git pull origin main

# 2. Update version in pyproject.toml (if needed)
# The version is automatically detected from git tags

# 3. Update CHANGELOG.md
# Add new version section with changes

# 4. Commit changes
git add .
git commit -m "Prepare for release v1.4.0"
git push origin main
```

### 2. Create Release

#### Option A: GitHub Web Interface (Recommended)
1. Go to [GitHub Releases](https://github.com/henriqueslab/rxiv-maker/releases)
2. Click "Create a new release"
3. Create new tag: `v1.4.0` (must start with `v`)
4. Release title: `v1.4.0`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

#### Option B: Command Line
```bash
# Create and push tag
git tag -a v1.4.0 -m "Release v1.4.0"
git push origin v1.4.0

# Create release via GitHub CLI
gh release create v1.4.0 --title "v1.4.0" --notes-file CHANGELOG.md
```

### 3. Monitor PyPI Publishing

The PyPI publishing workflow automatically triggers when a release is published:

1. Go to [Actions tab](https://github.com/henriqueslab/rxiv-maker/actions)
2. Find "Publish to PyPI" workflow
3. Monitor the build and publish jobs
4. Check for any failures and address them

### 4. Update Homebrew Formula

After PyPI publishing succeeds:

#### Option A: Manual Trigger
1. Go to [Actions tab](https://github.com/henriqueslab/rxiv-maker/actions)
2. Select "Update Homebrew Formula"
3. Click "Run workflow"
4. Enter version: `1.4.0`
5. Click "Run workflow"

#### Option B: Wait for Scheduled Update
- The workflow runs daily at 6 AM UTC
- It automatically checks for new PyPI versions
- Updates the formula if a new version is found

## Testing Releases

### Test PyPI Publishing

Test the release process without affecting production:

1. Go to [Actions tab](https://github.com/henriqueslab/rxiv-maker/actions)
2. Select "Publish to PyPI"
3. Click "Run workflow"
4. Select "testpypi" environment
5. Enter version to test
6. Click "Run workflow"

### Test Installation

After publishing to Test PyPI:

```bash
# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ rxiv-maker==1.4.0

# Test basic functionality
rxiv --version
rxiv --help
```

## Troubleshooting

### Common Issues

#### PyPI Publishing Failures

**Version already exists:**
```
ERROR: File already exists
```
- PyPI doesn't allow overwriting existing versions
- Create a new version (e.g., 1.4.1) or use Test PyPI

**Invalid credentials:**
```
ERROR: Invalid or expired token
```
- Check that `PYPI_API_TOKEN` secret is set correctly
- Regenerate token if expired

**Package validation failed:**
```
ERROR: Invalid distribution
```
- Check `pyproject.toml` configuration
- Ensure all required fields are present
- Test build locally: `python -m build`

#### Homebrew Formula Issues

**Formula syntax errors:**
```bash
# Test formula locally
brew audit --strict src/homebrew-rxiv-maker/Formula/rxiv-maker.rb
```

**Package not found on PyPI:**
- Ensure PyPI publishing completed successfully
- Wait a few minutes for PyPI propagation
- Check package exists: https://pypi.org/project/rxiv-maker/

**SHA256 mismatch:**
- The workflow automatically calculates SHA256
- If manual calculation needed:
```bash
curl -L https://files.pythonhosted.org/packages/.../rxiv_maker-1.4.0.tar.gz | shasum -a 256
```

### Manual Recovery

#### Rollback Release

If a release has issues:

1. **PyPI**: Cannot delete versions (contact PyPI support for serious issues)
2. **Homebrew**: Revert formula to previous version
3. **GitHub**: Delete release and tag if needed

#### Fix Broken Formula

```bash
# Clone repository
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker

# Fix formula
edit src/homebrew-rxiv-maker/Formula/rxiv-maker.rb

# Test changes
brew audit --strict src/homebrew-rxiv-maker/Formula/rxiv-maker.rb
brew install --build-from-source ./src/homebrew-rxiv-maker/Formula/rxiv-maker.rb

# Commit and push
git add src/homebrew-rxiv-maker/Formula/rxiv-maker.rb
git commit -m "Fix Homebrew formula"
git push origin main
```

## Security Considerations

### Token Management
- Use scoped tokens (project-specific)
- Rotate tokens regularly
- Use GitHub environments for additional protection
- Never commit tokens to repository

### Release Validation
- All releases are built from source
- SHA256 checksums are verified
- Packages are tested before publication
- Formula changes are reviewed before merge

### Monitoring
- Set up notifications for workflow failures
- Monitor PyPI download statistics
- Track Homebrew installation analytics
- Review security advisories regularly

## Automation Status

- ✅ **PyPI Publishing**: Fully automated on release
- ✅ **Homebrew Formula**: Manual trigger or scheduled
- ✅ **Testing**: Automated validation in both workflows
- ✅ **Security**: Token-based authentication
- ✅ **Monitoring**: Comprehensive logging and summaries

## Resources

- [PyPI API Token Guide](https://pypi.org/help/#apitoken)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Homebrew Formula Reference](https://docs.brew.sh/Formula-Cookbook)
- [Repository Actions](https://github.com/henriqueslab/rxiv-maker/actions)

---

**Last Updated**: 2025-01-17
**Maintainer**: rxiv-maker team