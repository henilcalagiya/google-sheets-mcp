#!/bin/bash

# Publishing script for google-sheets-mcp
# This script helps prepare and publish the package

set -e

echo "🚀 Google Sheets MCP - Publishing Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Not in the project root directory"
    exit 1
fi

# Check for hardcoded credentials
echo "🔍 Checking for hardcoded credentials..."

# Check for actual API keys (not just the word in documentation)
if grep -r "AIza[A-Za-z0-9_-]\{35\}" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ --exclude=*.md --exclude=*.yml --exclude=*.yaml --exclude=*.sh > /dev/null 2>&1; then
    print_error "Found potential API keys in the codebase"
    exit 1
fi

# Check for private keys (not just the word in documentation)
if grep -r "-----BEGIN PRIVATE KEY-----" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ --exclude=*.md --exclude=*.yml --exclude=*.yaml --exclude=*.sh > /dev/null 2>&1; then
    print_error "Found hardcoded private keys in the codebase"
    exit 1
fi

# Check for secrets (not just the word in documentation)
if grep -r "sk-[A-Za-z0-9_-]\{20,}" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ --exclude=*.md --exclude=*.yml --exclude=*.yaml --exclude=*.sh > /dev/null 2>&1; then
    print_error "Found potential secrets in the codebase"
    exit 1
fi

print_status "No hardcoded credentials found"

# Check version consistency
echo "🔍 Checking version consistency..."

PYPROJECT_VERSION=$(grep '^version =' pyproject.toml | cut -d'"' -f2)
INIT_VERSION=$(grep '__version__' gsheet_mcp_server/__init__.py | cut -d'"' -f2)

if [ "$PYPROJECT_VERSION" != "$INIT_VERSION" ]; then
    print_error "Version mismatch: pyproject.toml ($PYPROJECT_VERSION) != __init__.py ($INIT_VERSION)"
    exit 1
fi

print_status "Version consistency verified: $PYPROJECT_VERSION"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build package
echo "🔨 Building package..."
uv build

# Check build results
if [ ! -f "dist/google_sheets_mcp-$PYPROJECT_VERSION-py3-none-any.whl" ]; then
    print_error "Wheel file not created"
    exit 1
fi

if [ ! -f "dist/google_sheets_mcp-$PYPROJECT_VERSION.tar.gz" ]; then
    print_error "Source distribution not created"
    exit 1
fi

print_status "Package built successfully"

# Check package contents
echo "📦 Checking package contents..."
PACKAGE_FILES=$(python -c "import tarfile; t = tarfile.open('dist/google_sheets_mcp-$PYPROJECT_VERSION.tar.gz'); print(len([f for f in t.getmembers() if f.name.endswith('.py')]))")
print_status "Package contains $PACKAGE_FILES Python files"

# Test package import
echo "🧪 Testing package import..."
python -c "import gsheet_mcp_server; print('✅ Package imports successfully')" || {
    print_error "Package import failed"
    exit 1
}

print_status "Package import test passed"

# Show package info
echo "📊 Package Information:"
echo "  - Name: google-sheets-mcp"
echo "  - Version: $PYPROJECT_VERSION"
echo "  - Wheel: dist/google_sheets_mcp-$PYPROJECT_VERSION-py3-none-any.whl"
echo "  - Source: dist/google_sheets_mcp-$PYPROJECT_VERSION.tar.gz"

# Check if we should publish
if [ "$1" = "--publish" ]; then
    echo "🚀 Publishing to PyPI..."
    
    # Check if twine is installed
    if ! command -v twine &> /dev/null; then
        print_error "twine not found. Install with: pip install twine"
        exit 1
    fi
    
    # Upload to PyPI
    twine upload dist/*
    print_status "Package published to PyPI"
    
    echo "🎉 Successfully published google-sheets-mcp v$PYPROJECT_VERSION"
    echo "📦 Available at: https://pypi.org/project/google-sheets-mcp/"
else
    echo ""
    print_warning "Package built successfully but not published"
    echo "To publish, run: $0 --publish"
    echo ""
    echo "Or use GitHub Actions:"
    echo "1. Commit and push your changes"
    echo "2. Create a GitHub release with tag v$PYPROJECT_VERSION"
    echo "3. GitHub Actions will automatically publish to PyPI"
fi

echo ""
echo "📋 Next steps:"
echo "1. Test the package: pip install google-sheets-mcp"
echo "2. Create GitHub release with tag v$PYPROJECT_VERSION"
echo "3. Monitor PyPI page: https://pypi.org/project/google-sheets-mcp/"
