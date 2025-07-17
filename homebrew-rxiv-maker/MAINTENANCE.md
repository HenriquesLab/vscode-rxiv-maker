# Homebrew Formula Maintenance Guide

This guide is for maintainers of the rxiv-maker Homebrew formula. It covers how to update the formula, handle dependencies, and troubleshoot issues.

## 🔄 Automated Updates

The formula is updated via GitHub Actions after PyPI publishing is complete.

### Workflow: `.github/workflows/update-homebrew-formula.yml`

**Triggers:**
- Manual workflow dispatch (recommended)
- Scheduled daily check (6 AM UTC)

**Process:**
1. Wait for PyPI package availability
2. Extract version from PyPI or user input
3. Calculate SHA256 checksum from PyPI
4. Update formula file
5. Test installation
6. Commit changes

### Update Process

#### After PyPI Publishing

1. **Wait for PyPI propagation** (usually 1-5 minutes)
2. **Trigger manually**:
   ```bash
   # Via GitHub CLI
   gh workflow run update-homebrew-formula.yml -f version=1.4.0
   
   # Or via GitHub web interface
   # Go to Actions → Update Homebrew Formula → Run workflow
   ```

#### Scheduled Updates

The workflow runs daily to check for new PyPI versions:
- Compares current formula version with latest PyPI version
- Updates automatically if new version found
- Skips if already up to date

### Manual Trigger Options

```bash
# Basic update
gh workflow run update-homebrew-formula.yml -f version=1.4.0

# Force update even if version exists
gh workflow run update-homebrew-formula.yml -f version=1.4.0 -f force_update=true

# Skip PyPI availability check
gh workflow run update-homebrew-formula.yml -f version=1.4.0 -f wait_for_pypi=false
```

## 🛠 Manual Formula Updates

### Prerequisites

```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login

# Clone repository
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker
```

### Update Process

1. **Get package information from PyPI:**
   ```bash
   VERSION="1.4.0"
   curl -s "https://pypi.org/pypi/rxiv-maker/$VERSION/json" > package_info.json
   
   # Extract download URL
   python3 -c "
   import json
   with open('package_info.json') as f:
       data = json.load(f)
   for file in data['urls']:
       if file['packagetype'] == 'sdist':
           print('URL:', file['url'])
           print('SHA256:', file['digests']['sha256'])
           break
   "
   ```

2. **Update formula file:**
   ```bash
   FORMULA_FILE="homebrew-rxiv-maker/Formula/rxiv-maker.rb"
   NEW_URL="https://files.pythonhosted.org/packages/.../rxiv_maker-1.4.0.tar.gz"
   NEW_SHA256="abc123..."
   
   # Update URL, SHA256, and version
   sed -i.bak "s|url \".*\"|url \"$NEW_URL\"|g" "$FORMULA_FILE"
   sed -i.bak "s|sha256 \".*\"|sha256 \"$NEW_SHA256\"|g" "$FORMULA_FILE"
   sed -i.bak "s|version \".*\"|version \"$VERSION\"|g" "$FORMULA_FILE"
   ```

3. **Test the updated formula:**
   ```bash
   cd homebrew-rxiv-maker
   ./test-formula.sh --verbose
   ```

4. **Commit and push:**
   ```bash
   git add Formula/rxiv-maker.rb
   git commit -m "Update Homebrew formula to version $VERSION"
   git push origin main
   ```

## 🔧 Adding New Dependencies

### System Dependencies

Add to the `depends_on` section:

```ruby
class RxivMaker < Formula
  # ... existing content ...
  
  depends_on "python@3.11"
  depends_on "node@20"
  depends_on "r"
  depends_on "basictex"
  depends_on "new-dependency"  # Add here
  
  # ... rest of formula ...
end
```

### LaTeX Packages

Add to the `install` method:

```ruby
def install
  # ... existing installation code ...
  
  # Install additional LaTeX packages
  system "sudo", "tlmgr", "update", "--self"
  system "sudo", "tlmgr", "install", "latexdiff", "biber", "biblatex", "pgfplots", "adjustbox", "collectbox", "new-package"
end
```

### Python Dependencies

Python dependencies are automatically handled via pip installation. No formula changes needed.

## 🧪 Testing

### Local Testing

```bash
# Test formula syntax
brew audit --strict Formula/rxiv-maker.rb

# Test installation
brew install --build-from-source ./Formula/rxiv-maker.rb

# Run comprehensive tests
./test-formula.sh --verbose

# Clean up
brew uninstall rxiv-maker
```

### CI Testing

The formula is automatically tested on:
- macOS latest (Intel)
- macOS latest (Apple Silicon)

View test results in GitHub Actions.

## 🐛 Troubleshooting

### Common Issues

**Formula syntax errors:**
```bash
# Check syntax
brew audit --strict Formula/rxiv-maker.rb

# Common issues:
# - Missing quotes around strings
# - Incorrect indentation
# - Invalid Ruby syntax
```

**Installation failures:**
```bash
# Check build logs
brew install --build-from-source --verbose ./Formula/rxiv-maker.rb

# Common causes:
# - Network issues downloading packages
# - Permission problems with LaTeX
# - Missing system dependencies
```

**PyPI package not found:**
```bash
# Verify version exists on PyPI
curl -s "https://pypi.org/pypi/rxiv-maker/json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Available versions:')
for v in sorted(data['releases'].keys(), reverse=True)[:10]:
    print(f'  {v}')
"
```

### Debugging Tools

```bash
# Check formula info
brew info rxiv-maker

# List formula dependencies
brew deps rxiv-maker

# Check for dependency conflicts
brew doctor

# View detailed logs
brew install --verbose --debug rxiv-maker
```

## 🔒 Security Considerations

### SHA256 Verification

Always verify SHA256 checksums match PyPI:

```bash
# Download and verify
curl -L -o package.tar.gz "$DOWNLOAD_URL"
shasum -a 256 package.tar.gz

# Should match SHA256 in formula
```

### Dependency Auditing

```bash
# Audit formula for security issues
brew audit --strict Formula/rxiv-maker.rb

# Check for vulnerable dependencies
brew audit --strict --formula Formula/rxiv-maker.rb
```

## 📊 Monitoring

### Installation Analytics

Homebrew provides anonymous usage analytics:

```bash
# View formula analytics (if available)
brew analytics --formula rxiv-maker
```

### Issue Tracking

Monitor for issues:
- GitHub Issues mentioning "homebrew" or "brew"
- Failed CI builds
- User reports in Discussions

## 🆘 Getting Help

### Homebrew Resources

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Homebrew Troubleshooting](https://docs.brew.sh/Troubleshooting)
- [Homebrew Community](https://github.com/Homebrew/discussions)

### rxiv-maker Specific

- [GitHub Issues](https://github.com/henriqueslab/rxiv-maker/issues)
- [GitHub Discussions](https://github.com/henriqueslab/rxiv-maker/discussions)
- Contact: rxiv.maker@gmail.com

## 📋 Checklist for New Versions

- [ ] Verify new version is available on PyPI
- [ ] Update formula with correct URL and SHA256
- [ ] Test installation locally
- [ ] Check all dependencies still work
- [ ] Update documentation if needed
- [ ] Commit and push changes
- [ ] Monitor for user feedback
- [ ] Update this guide if process changed

---

**Last updated:** $(date +"%Y-%m-%d")
**Maintainer:** rxiv-maker team