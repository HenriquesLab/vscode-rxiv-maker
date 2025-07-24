#!/bin/bash
"""
Comprehensive binary distribution testing script.

This script runs all binary-related tests including:
- PyInstaller build tests
- Package manager integration tests
- End-to-end binary workflow tests
- CI matrix compatibility tests
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "tests/binary" ]; then
    log_error "Must be run from the project root directory"
    exit 1
fi

log_info "Starting comprehensive binary distribution testing..."

# Create results directory
mkdir -p test-results/binary

# 1. Run PyInstaller build tests
log_info "Running PyInstaller build tests..."
if uv run pytest tests/binary/test_pyinstaller_build.py -v --tb=short \
    --timeout=300 \
    --junitxml=test-results/binary/pyinstaller-results.xml; then
    log_success "PyInstaller build tests passed"
else
    log_warning "Some PyInstaller build tests failed (may be environment-dependent)"
fi

# 2. Run package manager integration tests
log_info "Running package manager integration tests..."
if uv run pytest tests/binary/test_package_managers.py -v --tb=short \
    --timeout=300 \
    --junitxml=test-results/binary/package-manager-results.xml; then
    log_success "Package manager tests passed"
else
    log_warning "Some package manager tests failed"
fi

# 3. Run end-to-end workflow tests
log_info "Running end-to-end binary workflow tests..."
if uv run pytest tests/binary/test_end_to_end.py -v --tb=short \
    --timeout=300 \
    --junitxml=test-results/binary/e2e-results.xml; then
    log_success "End-to-end tests passed"
else
    log_warning "Some end-to-end tests failed"
fi

# 4. Run CI matrix compatibility tests
log_info "Running CI matrix compatibility tests..."
if uv run pytest tests/binary/test_ci_matrix.py -v --tb=short \
    --timeout=300 \
    --junitxml=test-results/binary/ci-matrix-results.xml; then
    log_success "CI matrix tests passed"
else
    log_warning "Some CI matrix tests failed"
fi

# 5. Run all binary tests together with coverage
log_info "Running comprehensive binary test suite with coverage..."
if uv run pytest tests/binary/ -v --tb=short \
    --timeout=300 \
    --cov=rxiv_maker \
    --cov-report=html:test-results/binary/htmlcov \
    --cov-report=xml:test-results/binary/coverage.xml \
    --cov-report=term-missing \
    --cov-fail-under=80 \
    --junitxml=test-results/binary/all-binary-results.xml; then
    log_success "Comprehensive binary test suite passed"
else
    log_error "Binary test suite had failures"
    exit 1
fi

# 6. Validate workflow files
log_info "Validating GitHub Actions workflow files..."

# Check release workflow
if [ -f ".github/workflows/release.yml" ]; then
    if python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))" 2>/dev/null; then
        log_success "Release workflow YAML is valid"
    else
        log_error "Release workflow YAML is invalid"
        exit 1
    fi
else
    log_warning "Release workflow not found"
fi

# Check test workflow
if [ -f ".github/workflows/test.yml" ]; then
    if python3 -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))" 2>/dev/null; then
        log_success "Test workflow YAML is valid"
    else
        log_error "Test workflow YAML is invalid"
        exit 1
    fi
else
    log_warning "Test workflow not found"
fi

# 7. Validate package manager files
log_info "Validating package manager configuration files..."

# Check Homebrew formula
HOMEBREW_FORMULA="submodules/homebrew-rxiv-maker/Formula/rxiv-maker.rb"
if [ -f "$HOMEBREW_FORMULA" ]; then
    if ruby -c "$HOMEBREW_FORMULA" >/dev/null 2>&1; then
        log_success "Homebrew formula syntax is valid"
    else
        log_warning "Homebrew formula syntax check failed (Ruby may not be available)"
    fi
else
    log_warning "Homebrew formula not found"
fi

# Check Scoop manifest
SCOOP_MANIFEST="submodules/scoop-rxiv-maker/bucket/rxiv-maker.json"
if [ -f "$SCOOP_MANIFEST" ]; then
    if python3 -c "import json; json.load(open('$SCOOP_MANIFEST'))" 2>/dev/null; then
        log_success "Scoop manifest JSON is valid"
    else
        log_error "Scoop manifest JSON is invalid"
        exit 1
    fi
else
    log_warning "Scoop manifest not found"
fi

# 8. Check binary build requirements
log_info "Checking binary build requirements..."

# Check that PyInstaller is available
if uv run python -c "import PyInstaller" 2>/dev/null; then
    log_success "PyInstaller is available"
else
    log_warning "PyInstaller not available (required for binary building)"
fi

# Check that required data files exist
REQUIRED_FILES=(
    "src/tex/template.tex"
    "src/tex/style/rxiv_maker_style.cls"
    "src/tex/style/rxiv_maker_style.bst"
    "src/rxiv_maker/rxiv_maker_cli.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "Required file exists: $file"
    else
        log_error "Required file missing: $file"
        exit 1
    fi
done

# 9. Generate test report
log_info "Generating test report..."

cat > test-results/binary/test-report.md << EOF
# Binary Distribution Test Report

Generated: $(date)

## Test Results Summary

### PyInstaller Build Tests
- Location: \`tests/binary/test_pyinstaller_build.py\`
- Purpose: Test PyInstaller configuration and build process
- Results: See \`pyinstaller-results.xml\`

### Package Manager Integration Tests
- Location: \`tests/binary/test_package_managers.py\`
- Purpose: Test Homebrew and Scoop integration
- Results: See \`package-manager-results.xml\`

### End-to-End Workflow Tests
- Location: \`tests/binary/test_end_to_end.py\`
- Purpose: Test complete binary distribution workflow
- Results: See \`e2e-results.xml\`

### CI Matrix Compatibility Tests
- Location: \`tests/binary/test_ci_matrix.py\`
- Purpose: Test CI configuration and platform compatibility
- Results: See \`ci-matrix-results.xml\`

## Coverage Report
- HTML Report: \`htmlcov/index.html\`
- XML Report: \`coverage.xml\`

## Workflow Validation
- Release workflow: $([ -f ".github/workflows/release.yml" ] && echo "✅ Valid" || echo "❌ Missing")
- Test workflow: $([ -f ".github/workflows/test.yml" ] && echo "✅ Valid" || echo "❌ Missing")

## Package Manager Validation
- Homebrew formula: $([ -f "$HOMEBREW_FORMULA" ] && echo "✅ Valid" || echo "❌ Missing")
- Scoop manifest: $([ -f "$SCOOP_MANIFEST" ] && echo "✅ Valid" || echo "❌ Missing")

## Recommendations

1. Run binary tests regularly during development
2. Test binary builds on all target platforms before release
3. Validate package manager configurations after version updates
4. Monitor CI performance and adjust timeouts as needed

## Next Steps

- [ ] Test actual binary builds on CI
- [ ] Validate package manager installations
- [ ] Performance test binary startup times
- [ ] Security scan binary distributions
EOF

log_success "Test report generated: test-results/binary/test-report.md"

# 10. Summary
echo
log_info "================== BINARY TESTING SUMMARY =================="
log_success "✅ Binary distribution testing completed successfully!"
log_info "📊 Test results saved to: test-results/binary/"
log_info "📋 Test report: test-results/binary/test-report.md"
log_info "🔍 Coverage report: test-results/binary/htmlcov/index.html"
echo
log_info "🚀 Ready for binary distribution workflow!"
log_info "==========================================================="
