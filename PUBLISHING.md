# Publishing to PyPI from GitHub

This guide explains how to publish the `google-sheets-mcp` package to PyPI using GitHub Actions.

## 🚀 Quick Start

### 1. Set up PyPI API Token

1. **Create PyPI Account** (if you don't have one):
   - Go to [PyPI](https://pypi.org/account/register/)
   - Create an account

2. **Generate API Token**:
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/)
   - Click "Add API token"
   - Choose "Entire account (all projects)"
   - Copy the token (it starts with `pypi-`)

3. **Add to GitHub Secrets**:
   - Go to your GitHub repository
   - Click "Settings" → "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token

### 2. Create a Release

1. **Update Version** (if needed):
   ```bash
   # Update version in pyproject.toml
   version = "0.1.1"  # or whatever new version
   
   # Update version in gsheet_mcp_server/__init__.py
   __version__ = "0.1.1"
   ```

2. **Commit and Push**:
   ```bash
   git add .
   git commit -m "Bump version to 0.1.1"
   git push origin main
   ```

3. **Create GitHub Release**:
   - Go to your GitHub repository
   - Click "Releases" → "Create a new release"
   - Tag: `v0.1.1` (must match version)
   - Title: `Release v0.1.1`
   - Description: Add release notes
   - Click "Publish release"

### 3. Automatic Publishing

Once you publish the release, GitHub Actions will automatically:
- ✅ Build the package
- ✅ Run security checks
- ✅ Publish to PyPI
- ✅ Verify the upload

## 📋 Workflow Details

### Test Workflow (`.github/workflows/test.yml`)
- **Triggers**: Push to main/develop, Pull requests
- **Tests**: Package builds on Python 3.10, 3.11, 3.12
- **Checks**: Package import, contents verification

### Security Workflow (`.github/workflows/security.yml`)
- **Triggers**: Push to main/develop, Pull requests
- **Checks**: 
  - No hardcoded API keys
  - No private keys in code
  - No sensitive files committed
  - Package security verification

### Publish Workflow (`.github/workflows/publish.yml`)
- **Triggers**: Release published
- **Actions**:
  - Builds package with `uv build`
  - Publishes to PyPI using API token
  - Uses `pypa/gh-action-pypi-publish` action

### Version Check (`.github/workflows/version-bump.yml`)
- **Triggers**: Changes to Python files or pyproject.toml
- **Checks**: Version consistency between files

## 🔧 Manual Publishing (Alternative)

If you prefer manual publishing:

### 1. Build Locally
```bash
uv build
```

### 2. Upload to PyPI
```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/*
```

### 3. Verify Upload
```bash
# Check package on PyPI
pip install google-sheets-mcp
python -c "import gsheet_mcp_server; print('✅ Successfully installed')"
```

## 🛡️ Security Best Practices

### Before Publishing:
1. ✅ **Run security checks**:
   ```bash
   # Check for hardcoded credentials
   grep -r "AIza" . --exclude-dir=.git
   grep -r "-----BEGIN PRIVATE KEY-----" . --exclude-dir=.git
   ```

2. ✅ **Verify package contents**:
    # Check package contents
    python -c "
    import tarfile
    import os
    import re
    
    # Read version from pyproject.toml using regex
    with open('pyproject.toml', 'r') as f:
        content = f.read()
        match = re.search(r'version = \"([^\"]+)\"', content)
        version = match.group(1) if match else '0.1.3'
    
    package_file = f'dist/google_sheets_mcp-{version}.tar.gz'
    t = tarfile.open(package_file)
    [print(f.name) for f in t.getmembers() if f.name.endswith('.py')]
    "

    # Test wheel installation
    python -c "
    import os
    import re
    
    # Read version from pyproject.toml using regex
    with open('pyproject.toml', 'r') as f:
        content = f.read()
        match = re.search(r'version = \"([^\"]+)\"', content)
        version = match.group(1) if match else '0.1.3'
    
    wheel_file = f'dist/google_sheets_mcp-{version}-py3-none-any.whl'
    import subprocess
    subprocess.run(['pip', 'install', wheel_file], check=True)
    print('✅ Wheel installation successful')
    "
   ```

### Security Checklist:
- [ ] No API keys in code
- [ ] No private keys in code
- [ ] No passwords in code
- [ ] No sensitive files in package
- [ ] All credentials use environment variables
- [ ] Documentation uses placeholder values

## 📈 Version Management

### Semantic Versioning:
- **MAJOR.MINOR.PATCH**
- **0.1.0** - Initial release
- **0.1.1** - Bug fixes
- **0.2.0** - New features
- **1.0.0** - Stable release

### Version Update Process:
1. Update `pyproject.toml` version
2. Update `gsheet_mcp_server/__init__.py` version
3. Commit changes
4. Create GitHub release
5. GitHub Actions publishes automatically

## 🚨 Troubleshooting

### Common Issues:

#### 1. PyPI Upload Fails
```bash
# Check if package already exists
pip search google-sheets-mcp

# Use --repository testpypi for testing
twine upload --repository testpypi dist/*
```

#### 2. Security Check Fails
```bash
# Check for credentials
grep -r "AIza\|sk-\|-----BEGIN" . --exclude-dir=.git

# Remove any found credentials
# Update .gitignore to exclude sensitive files
```

#### 3. Build Fails
```bash
# Clean and rebuild
rm -rf dist/ build/
uv build

# Check for missing files
find gsheet_mcp_server -name "*.py" | wc -l
```

## 📊 Monitoring

### After Publishing:
1. **Check PyPI**: https://pypi.org/project/google-sheets-mcp/
2. **Test Installation**: `pip install google-sheets-mcp`
3. **Verify Functionality**: Run the MCP server
4. **Monitor Downloads**: Check PyPI statistics

### GitHub Actions Monitoring:
- Go to "Actions" tab in your repository
- Check workflow runs for any failures
- Review security check results

## 🎯 Success Checklist

Before publishing, ensure:
- [ ] All tests pass
- [ ] Security checks pass
- [ ] Version numbers match
- [ ] Package builds successfully
- [ ] No credentials in code
- [ ] Documentation is complete
- [ ] PyPI API token is configured
- [ ] GitHub release is ready

## 🚀 Next Steps

After successful publication:
1. **Update documentation** with PyPI link
2. **Share on social media** about the release
3. **Monitor for issues** and user feedback
4. **Plan next release** with new features

---

**Happy Publishing! 🎉**
