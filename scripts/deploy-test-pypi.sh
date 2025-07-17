#!/bin/bash

# Deploy to Test PyPI Script
# This script deploys the rxiv-maker package to test-pypi for testing

set -e  # Exit on any error

echo "🚀 Deploying rxiv-maker to Test PyPI"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: This script must be run from the rxiv-maker root directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 Activating virtual environment..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo "❌ Error: Virtual environment not found. Run 'make setup' first."
        exit 1
    fi
fi

# Check authentication
if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
    echo "🔐 Authentication Setup Required"
    echo "Please set up authentication for Test PyPI:"
    echo ""
    echo "Option 1: API Token (recommended)"
    echo "  export TWINE_USERNAME=__token__"
    echo "  export TWINE_PASSWORD=pypi-your-test-pypi-token-here"
    echo ""
    echo "Option 2: Username/Password"
    echo "  export TWINE_USERNAME=your-username"
    echo "  export TWINE_PASSWORD=your-password"
    echo ""
    echo "Get your Test PyPI token at: https://test.pypi.org/manage/account/"
    echo ""
    read -p "Have you set up authentication? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Please set up authentication and run the script again."
        exit 1
    fi
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ src/rxiv_maker.egg-info/

# Build the package
echo "📦 Building package..."
hatch build

# List built files
echo "📁 Built files:"
ls -la dist/

# Verify the package
echo "🔍 Verifying package..."
if command -v twine &> /dev/null; then
    twine check dist/*
else
    echo "⚠️  twine not found, skipping verification"
fi

# Upload to Test PyPI
echo "🚀 Uploading to Test PyPI..."
echo "Repository: https://test.pypi.org/legacy/"

if hatch publish -r https://test.pypi.org/legacy/; then
    echo "✅ Successfully uploaded to Test PyPI!"
    echo ""
    echo "🎉 Package deployed successfully!"
    echo "📍 View at: https://test.pypi.org/project/rxiv-maker/"
    echo ""
    echo "🧪 Test installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rxiv-maker"
    echo ""
    echo "🍺 Test Homebrew installation with:"
    echo "  brew install --build-from-source ./src/homebrew-rxiv-maker/Formula/rxiv-maker.rb --with-test-pypi"
else
    echo "❌ Upload failed!"
    echo "Common issues:"
    echo "  - Package version already exists on Test PyPI"
    echo "  - Authentication credentials incorrect"
    echo "  - Network connectivity issues"
    echo ""
    echo "💡 To fix version conflicts, create a new version:"
    echo "  git tag v1.4.0.dev4"
    echo "  hatch build"
    echo "  hatch publish -r https://test.pypi.org/legacy/"
    exit 1
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Test the package installation from test-pypi"
echo "2. Run AppVeyor tests (if configured)"
echo "3. Test Homebrew formula with --with-test-pypi"
echo "4. If all tests pass, deploy to production PyPI"
echo ""
echo "🔧 Troubleshooting:"
echo "- Check package at: https://test.pypi.org/project/rxiv-maker/"
echo "- View logs at: https://test.pypi.org/project/rxiv-maker/#history"
echo "- Report issues at: https://github.com/henriqueslab/rxiv-maker/issues"
