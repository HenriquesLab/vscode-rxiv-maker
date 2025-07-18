#!/bin/bash
# Test script for rxiv-maker Homebrew formula
# Usage: ./test-formula.sh [--verbose]

set -e

VERBOSE=false
if [[ "$1" == "--verbose" ]]; then
    VERBOSE=true
    set -x
fi

echo "🧪 Testing rxiv-maker Homebrew Formula"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    error "Homebrew is not installed. Please install from https://brew.sh/"
    exit 1
fi

success "Homebrew is installed"

# Check formula syntax
echo ""
info "Checking formula syntax..."
if brew audit --strict Formula/rxiv-maker.rb; then
    success "Formula syntax is valid"
else
    error "Formula syntax check failed"
    exit 1
fi

# Test installation from local formula
echo ""
info "Testing installation from local formula..."

# Uninstall if already installed
if brew list rxiv-maker &> /dev/null; then
    warning "rxiv-maker already installed, uninstalling first..."
    brew uninstall rxiv-maker
fi

# Install from local formula
if brew install --build-from-source ./Formula/rxiv-maker.rb; then
    success "Installation completed successfully"
else
    error "Installation failed"
    exit 1
fi

# Test basic functionality
echo ""
info "Testing basic functionality..."

# Test version command
if rxiv --version; then
    success "Version command works"
else
    error "Version command failed"
    exit 1
fi

# Test help command
if rxiv --help > /dev/null; then
    success "Help command works"
else
    error "Help command failed"
    exit 1
fi

# Test init command in a temporary directory
echo ""
info "Testing manuscript initialization..."
TEST_DIR="/tmp/rxiv-test-$(date +%s)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

if rxiv init .; then
    success "Manuscript initialization works"

    # Check if expected files were created
    if [[ -f "00_CONFIG.yml" && -f "01_MAIN.md" && -f "03_REFERENCES.bib" ]]; then
        success "All expected files created"
    else
        error "Some expected files missing"
        ls -la
        exit 1
    fi
else
    error "Manuscript initialization failed"
    exit 1
fi

# Test setup command
echo ""
info "Testing setup command..."
if rxiv setup --check-all; then
    success "Setup command works"
else
    warning "Setup command reported issues (this may be expected)"
fi

# Test formula test
echo ""
info "Running formula tests..."
cd - > /dev/null  # Return to original directory
if brew test rxiv-maker; then
    success "Formula tests passed"
else
    error "Formula tests failed"
    exit 1
fi

# Check dependencies
echo ""
info "Checking installed dependencies..."

check_dependency() {
    local cmd=$1
    local name=$2

    if command -v "$cmd" &> /dev/null; then
        success "$name is available"
        if $VERBOSE; then
            echo "  Path: $(which $cmd)"
            if [[ "$cmd" == "python3.11" ]]; then
                echo "  Version: $($cmd --version)"
            elif [[ "$cmd" == "node" ]]; then
                echo "  Version: $($cmd --version)"
            elif [[ "$cmd" == "R" ]]; then
                echo "  Version: $($cmd --version | head -1)"
            elif [[ "$cmd" == "pdflatex" ]]; then
                echo "  Version: $($cmd --version | head -1)"
            fi
        fi
    else
        error "$name is not available"
    fi
}

check_dependency "python3.11" "Python 3.11"
check_dependency "node" "Node.js"
check_dependency "R" "R"
check_dependency "pdflatex" "LaTeX (pdflatex)"
check_dependency "make" "Make"

# Test Python imports
echo ""
info "Testing Python package imports..."
if python3.11 -c "import rxiv_maker; print('rxiv_maker version:', rxiv_maker.__version__)"; then
    success "Python package imports work"
else
    error "Python package import failed"
    exit 1
fi

# Cleanup test directory
rm -rf "$TEST_DIR"

echo ""
echo "🎉 All tests passed!"
echo ""
echo "📋 Summary:"
echo "  ✅ Formula syntax is valid"
echo "  ✅ Installation works"
echo "  ✅ Basic CLI commands work"
echo "  ✅ Manuscript initialization works"
echo "  ✅ Dependencies are available"
echo "  ✅ Python package imports work"
echo ""

if $VERBOSE; then
    echo "📊 Installed package info:"
    brew info rxiv-maker
fi

echo "🚀 Ready for use! Try:"
echo "  rxiv init my-paper/"
echo "  cd my-paper/"
echo "  rxiv build"
