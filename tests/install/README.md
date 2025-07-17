# Universal Python Wheel Installer Tests

This directory contains comprehensive tests for the Universal Python Wheel Installer functionality in rxiv-maker.

## Overview

The test suite verifies that the Universal Python Wheel Installer works correctly across different scenarios, with a focus on Docker Ubuntu environments for consistent testing.

## Test Structure

```
tests/install/
├── README.md                          # This file
├── __init__.py                        # Package initialization
├── conftest.py                        # Docker fixtures and utilities
├── test_basic_installation.py         # Basic installation functionality
├── test_platform_detection.py         # Platform detection tests
├── test_dependency_installation.py    # System dependency installation
├── cli/
│   ├── __init__.py
│   └── test_check_installation.py     # CLI integration tests
├── docker/
│   ├── __init__.py
│   ├── test_docker_environment.py     # Docker environment detection
│   └── test_full_workflow.py          # End-to-end workflow tests
└── fixtures/
    ├── test_manuscripts/               # Test manuscript data
    └── expected_outputs/               # Expected test outputs
```

## Test Categories

### 1. Basic Installation Tests (`test_basic_installation.py`)
- **Purpose**: Verify core installation functionality
- **Tests**:
  - Clean Ubuntu container setup
  - Installation from PyPI (when available)
  - Installation from wheel files
  - Different installation modes (full, minimal, core)
  - Skip system dependencies flag
  - Import functionality after installation
  - Entry point verification
  - Dependency installation
  - Error handling scenarios
  - Installation idempotency

### 2. Platform Detection Tests (`test_platform_detection.py`)
- **Purpose**: Test platform detection and capabilities
- **Tests**:
  - Linux platform detection in containers
  - Architecture detection (x86_64/amd64)
  - Package manager detection (apt)
  - Distribution detection methods
  - Package manager capabilities
  - System requirements detection
  - Network connectivity testing
  - Compiler and development tools
  - Library dependencies
  - Environment variables

### 3. Dependency Installation Tests (`test_dependency_installation.py`)
- **Purpose**: Test system dependency installation
- **Tests**:
  - LaTeX installation and compilation
  - Node.js and npm installation
  - Mermaid CLI installation
  - R language installation
  - Python development libraries
  - Graphics libraries for matplotlib
  - System library compilation
  - Dependency integration
  - Error handling for missing dependencies

### 4. CLI Integration Tests (`cli/test_check_installation.py`)
- **Purpose**: Test check-installation command functionality
- **Tests**:
  - Basic check-installation command
  - JSON output format
  - Detailed output format
  - Help output
  - Missing dependencies detection
  - Fix functionality
  - Component checking
  - Error handling
  - Output formatting

### 5. Docker Environment Tests (`docker/test_docker_environment.py`)
- **Purpose**: Test Docker-specific functionality
- **Tests**:
  - Docker environment detection
  - Container ID detection
  - Docker socket availability
  - Container resource limits
  - Network configuration
  - Environment variables
  - Container capabilities
  - File system access
  - Installation behavior in containers

### 6. Full Workflow Tests (`docker/test_full_workflow.py`)
- **Purpose**: Test complete installation-to-usage workflows
- **Tests**:
  - Install → init workflow
  - Install → validate workflow
  - Install → figures workflow
  - Install → build workflow (simulation)
  - Install → check workflow
  - Error handling in workflows
  - Performance testing
  - Memory usage testing
  - Integration with system dependencies

## Running Tests

### Prerequisites

1. **Docker**: Tests require Docker to be installed and running
2. **Python 3.11+**: Required for test execution
3. **Environment Variable**: Set `DOCKER_AVAILABLE=true` to enable Docker tests

### Using Nox (Recommended)

```bash
# Run basic installation tests (fast)
nox -s install_tests

# Run complete installation tests (slow)
nox -s install_tests_full

# Run without Docker (unit tests only)
nox -s install_tests_basic
```

### Using pytest directly

```bash
# Set environment variable
export DOCKER_AVAILABLE=true

# Run all installation tests
pytest tests/install/ -v

# Run specific test categories
pytest tests/install/test_basic_installation.py -v
pytest tests/install/cli/ -v
pytest tests/install/docker/ -v

# Run with markers
pytest tests/install/ -m "not slow" -v              # Skip slow tests
pytest tests/install/ -m "docker" -v                # Only Docker tests
pytest tests/install/ -m "install and not docker" -v # Unit tests only
```

### Using Docker Compose

```bash
# Run tests in Docker environment
docker-compose -f tests/docker/docker-compose.install-test.yml up --build

# Interactive shell for debugging
docker-compose -f tests/docker/docker-compose.install-test.yml --profile shell up

# Clean Ubuntu environment
docker-compose -f tests/docker/docker-compose.install-test.yml --profile clean-ubuntu up
```

## Test Configuration

### Pytest Markers

- `@pytest.mark.install` - Installation-related tests
- `@pytest.mark.docker` - Docker-dependent tests
- `@pytest.mark.container` - Container-based tests
- `@pytest.mark.slow` - Slow tests (>30 seconds)
- `@pytest.mark.integration` - Integration tests

### Environment Variables

- `DOCKER_AVAILABLE=true` - Enable Docker tests
- `RXIV_INSTALL_MODE=full|minimal|core` - Installation mode
- `RXIV_SKIP_SYSTEM_DEPS=1` - Skip system dependencies
- `CI=true` - CI environment detection

## Test Fixtures

### Docker Fixtures (`conftest.py`)

- `docker_manager` - Docker test management
- `ubuntu_container` - Clean Ubuntu 22.04 container
- `test_package_wheel` - Built wheel package for testing
- `mock_install_manager` - Mock installation manager
- `test_manuscript_dir` - Test manuscript directory

### Utility Functions

- `run_in_container()` - Execute commands in containers
- `install_rxiv_maker_in_container()` - Install package in container
- `DockerTestManager` - Container lifecycle management

## Expected Behavior

### Success Criteria

✅ **Installation Modes**: All modes (full, minimal, core) work correctly
✅ **Platform Detection**: Linux/Ubuntu platform detected correctly
✅ **Dependency Installation**: System dependencies install properly
✅ **CLI Integration**: All CLI commands function after installation
✅ **Error Handling**: Graceful error handling and recovery
✅ **Environment Detection**: Docker/CI environments detected correctly
✅ **Performance**: Installation completes within reasonable time
✅ **Resource Usage**: Reasonable memory and disk usage

### Test Timeouts

- **Basic tests**: 60 seconds per test
- **Installation tests**: 300 seconds per test (5 minutes)
- **Full workflow tests**: 600 seconds per test (10 minutes)

## Troubleshooting

### Common Issues

1. **Docker not available**
   ```bash
   # Check Docker is running
   docker ps
   
   # Set environment variable
   export DOCKER_AVAILABLE=true
   ```

2. **Permission issues**
   ```bash
   # Ensure Docker daemon is accessible
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Network issues**
   ```bash
   # Test network connectivity
   docker run --rm ubuntu:22.04 ping -c 1 8.8.8.8
   ```

4. **Resource constraints**
   ```bash
   # Check available resources
   docker system df
   docker system prune  # Clean up if needed
   ```

### Debug Mode

```bash
# Run tests with verbose output
pytest tests/install/ -v -s --tb=long

# Run single test with debugging
pytest tests/install/test_basic_installation.py::TestBasicInstallation::test_install_from_wheel -v -s

# Use interactive debugging
pytest tests/install/ --pdb
```

## Test Data

### Test Manuscripts

The test suite includes minimal test manuscripts for workflow testing:
- Basic configuration files
- Simple Markdown content
- Test bibliography entries
- Python figure scripts

### Expected Outputs

Tests validate against expected outputs:
- JSON response formats
- Command exit codes
- File creation patterns
- Log message formats

## Integration with CI/CD

Tests are designed to run in CI environments:
- GitHub Actions integration
- Docker-based execution
- Parallel test execution
- Test result reporting
- Coverage reporting

## Contributing

When adding new tests:

1. Follow existing test patterns
2. Use appropriate pytest markers
3. Include Docker and non-Docker variants
4. Add comprehensive error testing
5. Update this README

## Performance Benchmarks

Target performance metrics:
- Installation: < 60 seconds
- Command response: < 10 seconds
- Test execution: < 10 minutes total
- Memory usage: < 2GB peak

## Security Considerations

Tests verify:
- No sensitive data in logs
- Proper permission handling
- Secure temporary file handling
- Container isolation
- Network security