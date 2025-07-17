# Migration Guide: Make Commands → Modern CLI

This guide helps existing rxiv-maker users transition from the traditional Make interface to the modern CLI.

## Overview

Rxiv-Maker now includes a modern command-line interface (`rxiv`) alongside the traditional Make commands. Both interfaces are fully supported, but the CLI offers enhanced features:

- **Rich output** with colors, progress bars, and formatted tables
- **Better error handling** with helpful suggestions
- **Auto-completion** for bash, zsh, and fish shells
- **Configuration management** with persistent settings
- **Improved user experience** with intuitive commands

## Quick Migration Reference

### Essential Commands

| Make Command | CLI Command | Notes |
|-------------|-------------|-------|
| `make setup` | `rxiv setup` | Install dependencies |
| `make pdf` | `rxiv build` | Generate PDF |
| `make validate` | `rxiv validate` | Validate manuscript |
| `make clean` | `rxiv clean` | Clean generated files |
| `make arxiv` | `rxiv arxiv` | Prepare arXiv package |

### Advanced Commands

| Make Command | CLI Command | Notes |
|-------------|-------------|-------|
| `make pdf FORCE_FIGURES=true` | `rxiv build --force-figures` | Force figure regeneration |
| `make pdf-no-validate` | `rxiv build --skip-validation` | Skip validation |
| `make pdf-track-changes TAG=v1.0.0` | `rxiv track-changes MANUSCRIPT/ v1.0.0` | Track changes |
| `make fix-bibliography` | `rxiv bibliography fix` | Fix bibliography |
| `make add-bibliography 10.1000/doi` | `rxiv bibliography add 10.1000/doi` | Add DOI |
| `make clean-figures` | `rxiv clean --figures-only` | Clean only figures |

### Environment Variables

| Make Variable | CLI Option | CLI Config | Notes |
|--------------|------------|------------|-------|
| `MANUSCRIPT_PATH=path/` | `rxiv build path/` | `general.default_manuscript_path` | Manuscript directory |
| `FORCE_FIGURES=true` | `--force-figures` | `build.force_figures` | Force figure regeneration |
| `RXIV_ENGINE=DOCKER` | `--engine docker` | `general.default_engine` | Execution engine |

## Step-by-Step Migration

### 1. Install the CLI

If you're using an existing rxiv-maker installation:

```bash
# Navigate to your rxiv-maker directory
cd /path/to/rxiv-maker

# Install in development mode to get the CLI
pip install -e .

# Verify installation
rxiv --version
```

### 2. Enable Auto-completion (Optional)

```bash
# For bash users
rxiv --install-completion bash

# For zsh users
rxiv --install-completion zsh

# For fish users
rxiv --install-completion fish
```

### 3. Configure Defaults (Optional)

Set up your preferred defaults:

```bash
# Show current configuration
rxiv config show

# Set default manuscript path
rxiv config set general.default_manuscript_path MY_PAPERS/

# Set default engine
rxiv config set general.default_engine docker

# Enable verbose output by default
rxiv config set general.verbose true
```

### 4. Try Basic Commands

Test the CLI with your existing manuscripts:

```bash
# Validate your manuscript
rxiv validate

# Build PDF
rxiv build

# Clean generated files
rxiv clean
```

## Common Migration Scenarios

### Scenario 1: Regular PDF Generation

**Old workflow:**
```bash
make setup
make pdf
```

**New workflow:**
```bash
rxiv setup
rxiv build
```

### Scenario 2: Custom Manuscript Directory

**Old workflow:**
```bash
MANUSCRIPT_PATH=MY_PAPER make pdf
```

**New workflow:**
```bash
rxiv build MY_PAPER/
```

**Or set as default:**
```bash
rxiv config set general.default_manuscript_path MY_PAPER/
rxiv build
```

### Scenario 3: Docker Mode

**Old workflow:**
```bash
make pdf RXIV_ENGINE=DOCKER
```

**New workflow:**
```bash
rxiv build --engine docker
```

**Or set as default:**
```bash
rxiv config set general.default_engine docker
rxiv build
```

### Scenario 4: Bibliography Management

**Old workflow:**
```bash
make fix-bibliography
make add-bibliography 10.1000/example.doi
```

**New workflow:**
```bash
rxiv bibliography fix
rxiv bibliography add 10.1000/example.doi
```

### Scenario 5: Manuscript Initialization

**Old workflow:**
```bash
# Manual creation of MANUSCRIPT/ directory and files
mkdir MANUSCRIPT
mkdir MANUSCRIPT/FIGURES
# ... manual file creation
```

**New workflow:**
```bash
rxiv init MY_PAPER/
```

## Advanced CLI Features

### Configuration Management

The CLI includes a comprehensive configuration system:

```bash
# Show all configuration options
rxiv config show

# Get specific setting
rxiv config get general.default_engine

# Set specific setting
rxiv config set build.force_figures true

# Reset to defaults
rxiv config reset

# Edit config file directly
rxiv config edit
```

### Rich Output

The CLI provides enhanced visual feedback:

- **Progress bars** during long operations
- **Colored output** for better readability
- **Formatted tables** for structured information
- **Emoji indicators** for quick status recognition
- **Detailed error messages** with suggestions

### Auto-completion

Enable shell auto-completion for faster command entry:

```bash
# Install for your shell
rxiv --install-completion bash  # or zsh, fish

# Then use Tab completion
rxiv b<TAB>          # Completes to "build"
rxiv build --f<TAB>  # Completes to "--force-figures"
```

## Troubleshooting

### CLI Command Not Found

If `rxiv` command is not found:

```bash
# Ensure you've installed in development mode
pip install -e .

# Or check if it's in your PATH
which rxiv

# Alternative: use as module
python -m rxiv_maker.cli --help
```

### Make Commands Still Work

All existing Make commands continue to work:

```bash
# These still work exactly as before
make setup
make pdf
make validate
make clean
```

The CLI commands are additions, not replacements.

### Configuration Issues

If you encounter configuration problems:

```bash
# Reset configuration to defaults
rxiv config reset

# Check configuration location
rxiv config show  # Shows config file path at bottom

# Edit manually if needed
rxiv config edit
```

## Best Practices

### For New Users

- Start with the CLI interface (`rxiv`) for the best experience
- Use `rxiv init` to create new manuscripts
- Enable auto-completion for your shell
- Set up configuration defaults for your workflow

### For Existing Users

- Keep using Make commands if you prefer them
- Try CLI commands gradually for new workflows
- Use both interfaces as needed - they're fully compatible
- Consider migrating scripts to use CLI commands for better output

### For Teams

- Document which interface your team prefers
- Both interfaces work identically with Docker mode
- CLI provides better error messages for debugging
- Make commands may be more familiar to some users

## Getting Help

### CLI Help

```bash
# General help
rxiv --help

# Command-specific help
rxiv build --help
rxiv bibliography --help

# Show version and system info
rxiv version --detailed
```

### Make Help

```bash
# Traditional help
make help
```

### Documentation

- **README.md**: Updated with both interfaces
- **CLAUDE.md**: Developer documentation with both interfaces
- **This file**: Migration guide

## Feedback

The CLI is designed to be intuitive and powerful. If you encounter issues or have suggestions:

1. Try the equivalent Make command to isolate the issue
2. Use `rxiv --verbose` for more detailed output
3. Check configuration with `rxiv config show`
4. Report issues following the project's contribution guidelines

Both interfaces will continue to be supported, so you can use whichever fits your workflow better!