# Testing Documentation

This document outlines the comprehensive testing strategy for rxiv-maker, with special focus on binary distribution testing.

## Testing Overview

rxiv-maker has a multi-layered testing approach:

1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test component interactions
3. **Binary Distribution Tests** - Test PyInstaller builds and package managers
4. **End-to-End Tests** - Test complete workflows
5. **CI/CD Tests** - Test automation and deployment

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
├── integration/             # Integration tests for workflows
├── cli/                     # CLI-specific tests
├── binary/                  # Binary distribution tests (NEW)
│   ├── test_pyinstaller_build.py    # PyInstaller configuration tests
│   ├── test_package_managers.py     # Homebrew/Scoop integration tests  
│   ├── test_end_to_end.py          # Complete binary workflow tests
│   └── test_ci_matrix.py           # CI matrix and compatibility tests
└── notebooks/               # Jupyter notebook tests
```

## Running Tests

### All Tests
```bash
# Run complete test suite
uv run pytest

# Run with coverage
uv run pytest --cov=rxiv_maker --cov-report=html
```

### Specific Test Categories

#### Unit Tests
```bash
uv run pytest tests/unit/ -v
```

#### Integration Tests  
```bash
uv run pytest tests/integration/ -v
```

#### Binary Distribution Tests
```bash
# Run all binary tests
uv run pytest tests/binary/ -v

# Run specific binary test categories
uv run pytest tests/binary/test_pyinstaller_build.py -v
uv run pytest tests/binary/test_package_managers.py -v
uv run pytest tests/binary/test_end_to_end.py -v
uv run pytest tests/binary/test_ci_matrix.py -v

# Run comprehensive binary testing script
./scripts/test-binary.sh
```

#### CLI Tests
```bash
uv run pytest tests/cli/ -v
```

## Binary Distribution Testing

### Purpose
Binary distribution testing ensures that:
- PyInstaller can build working executables
- Package managers (Homebrew, Scoop) work correctly
- CI/CD workflows function properly
- Binaries work across platforms

### Test Categories

#### 1. PyInstaller Build Tests (`test_pyinstaller_build.py`)
- **PyInstaller spec file validation**
- **Required data files inclusion**
- **Hidden imports completeness**
- **Binary compatibility checks**
- **Cross-platform build testing**

```bash
# Run PyInstaller tests
uv run pytest tests/binary/test_pyinstaller_build.py -v

# Run with markers
uv run pytest tests/binary/ -m pyinstaller -v
```

#### 2. Package Manager Integration Tests (`test_package_managers.py`)
- **Homebrew formula validation**
- **Scoop manifest validation**  
- **Version synchronization**
- **Workflow automation**
- **Binary URL correctness**

```bash
# Run package manager tests
uv run pytest tests/binary/test_package_managers.py -v

# Run specific platform tests
uv run pytest tests/binary/ -m homebrew -v
uv run pytest tests/binary/ -m scoop -v
```

#### 3. End-to-End Workflow Tests (`test_end_to_end.py`)
- **Complete release workflow**
- **Binary functionality testing**
- **GitHub release integration**
- **Multi-platform compatibility**
- **Performance considerations**

```bash
# Run end-to-end tests
uv run pytest tests/binary/test_end_to_end.py -v

# Run with slow tests
uv run pytest tests/binary/ -m "end_to_end or slow" -v
```

#### 4. CI Matrix Compatibility Tests (`test_ci_matrix.py`)  
- **CI workflow configuration**
- **Platform matrix coverage**
- **Performance optimization**
- **Security considerations**
- **Quality assurance**

```bash
# Run CI matrix tests
uv run pytest tests/binary/test_ci_matrix.py -v
```

## Test Markers

Use pytest markers to run specific test categories:

```bash
# Binary-related tests
uv run pytest -m binary -v

# Platform-specific tests  
uv run pytest -m platform_specific -v

# Slow tests (require special setup)
uv run pytest -m slow -v

# Package manager tests
uv run pytest -m "homebrew or scoop" -v
```

## Continuous Integration

### GitHub Actions Workflows

#### Test Workflow (`.github/workflows/test.yml`)
- Runs on: Push, PR, scheduled
- Matrix: Python 3.11-3.12, Ubuntu/Windows/macOS
- Includes: Unit tests, integration tests, CLI tests
- Coverage: Codecov integration

#### Release Workflow (`.github/workflows/release.yml`)
- Runs on: Git tags, manual trigger
- Builds: Multi-platform binaries
- Tests: Binary functionality
- Publishes: GitHub releases, PyPI, package managers
- **Submodule Integration**: Uses `submodules: recursive` for checkout
- **Package Manager Updates**: Triggers automated updates in submodule repositories

### Submodule Workflow Integration

The binary distribution system relies on Git submodules for package manager repositories:

#### Submodule Structure
- `submodules/homebrew-rxiv-maker/` - Homebrew formula repository
- `submodules/scoop-rxiv-maker/` - Scoop manifest repository  
- `submodules/vscode-rxiv-maker/` - VS Code extension repository
- `submodules/docker-rxiv-maker/` - Docker image repository

#### Automated Package Manager Updates
1. **Release Trigger**: Main release workflow publishes binaries
2. **Repository Dispatch**: Sends events to package manager submodules
3. **Formula/Manifest Update**: Submodule workflows update configurations
4. **Validation**: Package managers test updated configurations
5. **Commit**: Changes are automatically committed to submodule repositories

#### Submodule Workflow Files
- **Homebrew**: `submodules/homebrew-rxiv-maker/.github/workflows/update-formula.yml`
- **Scoop**: `submodules/scoop-rxiv-maker/.github/workflows/update-manifest.yml`

### Platform Coverage

| Platform | Python | Architecture | Status |
|----------|--------|--------------|--------|
| Ubuntu Latest | 3.11, 3.12 | x64 | ✅ |
| Windows Latest | 3.11, 3.12 | x64 | ✅ |
| macOS Latest | 3.11, 3.12 | ARM64 | ✅ |
| macOS 13 | 3.11, 3.12 | x64 | ✅ |

## Testing Best Practices

### Writing Tests

1. **Use descriptive test names**
   ```python
   def test_pyinstaller_can_build_executable_with_all_dependencies(self):
   ```

2. **Test both success and failure cases**
   ```python
   def test_homebrew_formula_handles_missing_binaries(self):
   ```

3. **Use appropriate fixtures**
   ```python
   @pytest.fixture
   def temp_build_dir(self):
       # Setup and teardown
   ```

4. **Mark tests appropriately**
   ```python
   @pytest.mark.slow
   @pytest.mark.binary
   def test_full_binary_build_process(self):
   ```

### Test Organization

- **One test class per component**
- **Group related tests together**
- **Use descriptive class names**
- **Separate fast and slow tests**

### Debugging Tests

```bash
# Run with verbose output
uv run pytest tests/binary/ -v -s

# Run specific test with debugging
uv run pytest tests/binary/test_pyinstaller_build.py::TestPyInstallerBuild::test_pyinstaller_spec_file_creation -v -s --tb=long

# Run with coverage and HTML report
uv run pytest tests/binary/ --cov=rxiv_maker --cov-report=html --cov-report=term-missing
```

## Test Environments

### Local Development
```bash
# Quick test run
uv run pytest tests/binary/test_ci_matrix.py -v

# Full binary test suite
./scripts/test-binary.sh
```

### CI Environment
- Automated on every push/PR
- Full platform matrix
- Binary build testing
- Package manager validation

### Release Environment
- Triggered on git tags
- Comprehensive binary testing
- Multi-platform builds
- Automated deployment

## Coverage Requirements

- **Minimum Coverage**: 80% for binary components
- **Target Coverage**: 90% overall
- **Critical Paths**: 100% coverage for CLI entry points

## Performance Benchmarks

### Test Execution Times
- Unit tests: < 30 seconds
- Integration tests: < 2 minutes  
- Binary tests: < 5 minutes
- Full suite: < 10 minutes

### Binary Sizes (Target)
- Linux x64: < 100MB
- Windows x64: < 120MB
- macOS ARM64: < 110MB
- macOS x64: < 110MB

## Troubleshooting

### Common Issues

#### PyInstaller Tests Failing
```bash
# Check Python environment
uv run python -c "import sys; print(sys.path)"

# Verify dependencies
uv run pytest tests/binary/test_pyinstaller_build.py::TestBinaryCompatibility::test_dependency_availability_matrix -v
```

#### Package Manager Tests Failing
```bash
# Check file existence
ls -la submodules/homebrew-rxiv-maker/Formula/rxiv-maker.rb
ls -la submodules/scoop-rxiv-maker/bucket/rxiv-maker.json

# Validate JSON/Ruby syntax
python3 -c "import json; print(json.load(open('submodules/scoop-rxiv-maker/bucket/rxiv-maker.json')))"
ruby -c submodules/homebrew-rxiv-maker/Formula/rxiv-maker.rb
```

#### CI Tests Failing
```bash
# Check workflow syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml')))"

# Validate test matrix
uv run pytest tests/binary/test_ci_matrix.py::TestCITestingMatrix::test_os_matrix_coverage -v
```

### Getting Help

1. Check test logs in `test-results/binary/`
2. Review coverage reports in `htmlcov/`
3. Run individual test files with `-v -s` flags
4. Check GitHub Actions workflow runs

## Contributing

When adding new features:

1. **Add unit tests** for new components
2. **Add integration tests** for new workflows  
3. **Update binary tests** if affecting distribution
4. **Test on multiple platforms** before submitting PR
5. **Update documentation** for new test procedures

For binary distribution changes:
1. Update `test_pyinstaller_build.py` for build changes
2. Update `test_package_managers.py` for Homebrew/Scoop changes
3. Update `test_end_to_end.py` for workflow changes
4. Run `./scripts/test-binary.sh` before submitting

### Submodule-Specific Testing

When working with submodules:

1. **Initialize submodules**: `git submodule update --init --recursive`
2. **Test submodule integration**: `uv run pytest tests/binary/test_package_managers.py::TestPackageManagerWorkflows -v`
3. **Verify workflow triggers**: `uv run pytest tests/binary/test_end_to_end.py::TestBinaryDistributionWorkflow::test_package_manager_trigger_configuration -v`
4. **Check submodule status**: `git submodule status`

#### Common Submodule Issues

- **Missing workflows**: If tests fail due to missing workflow files, ensure submodules are properly initialized
- **YAML parsing**: Some tests handle the YAML quirk where `on:` is parsed as boolean `True`
- **Path resolution**: Tests use relative paths to locate submodule files from the main repository

---

This comprehensive testing approach ensures rxiv-maker works reliably across all platforms and distribution methods.