# Rxiv-Maker CLI Reference

Complete reference for the modern `rxiv` command-line interface.

## Installation

```bash
# Install from PyPI
pip install rxiv-maker

# Development install
pip install -e .

# Verify installation
rxiv --version
```

## Global Options

All commands support these global options:

```bash
rxiv [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options

- `--version`: Show version and exit
- `--verbose, -v`: Enable verbose output
- `--engine {local,docker}`: Choose execution engine (default: local)
- `--install-completion {bash,zsh,fish}`: Install shell completion
- `--no-update-check`: Skip update check for this command
- `--help`: Show help and exit

### Examples

```bash
rxiv --verbose build MY_PAPER/          # Verbose build
rxiv --engine docker build              # Use Docker engine
rxiv --install-completion bash          # Install bash completion
rxiv --no-update-check build            # Skip update check
```

## Commands

### `rxiv build`

Build PDF from manuscript directory.

```bash
rxiv build [OPTIONS] [MANUSCRIPT_PATH]
```

#### Options

- `--output-dir, -o TEXT`: Output directory (default: output)
- `--force-figures, -f`: Force regeneration of all figures
- `--skip-validation, -s`: Skip validation step
- `--track-changes, -t TEXT`: Track changes against git tag
- `--help`: Show help

#### Examples

```bash
rxiv build                              # Build from MANUSCRIPT/
rxiv build MY_PAPER/                    # Build from custom directory
rxiv build --force-figures              # Force regenerate figures
rxiv build --skip-validation            # Skip validation
rxiv build --track-changes v1.0.0       # Track changes vs tag
rxiv build --output-dir custom_output   # Custom output directory
```

### `rxiv validate`

Validate manuscript structure and content.

```bash
rxiv validate [OPTIONS] [MANUSCRIPT_PATH]
```

#### Options

- `--detailed, -d`: Show detailed validation report
- `--no-doi`: Skip DOI validation
- `--help`: Show help

#### Examples

```bash
rxiv validate                           # Validate MANUSCRIPT/
rxiv validate MY_PAPER/                 # Validate custom directory
rxiv validate --detailed               # Show detailed report
rxiv validate --no-doi                 # Skip DOI validation
```

### `rxiv clean`

Clean generated files and directories.

```bash
rxiv clean [OPTIONS] [MANUSCRIPT_PATH]
```

#### Options

- `--output-dir, -o TEXT`: Output directory (default: output)
- `--figures-only, -f`: Clean only generated figures
- `--output-only, -O`: Clean only output directory
- `--arxiv-only, -a`: Clean only arXiv files
- `--temp-only, -t`: Clean only temporary files
- `--cache-only, -c`: Clean only cache files
- `--all, -A`: Clean all generated files
- `--help`: Show help

#### Examples

```bash
rxiv clean                              # Clean all generated files
rxiv clean MY_PAPER/                    # Clean custom directory
rxiv clean --figures-only               # Clean only figures
rxiv clean --cache-only                 # Clean only cache
```

### `rxiv figures`

Generate figures from scripts.

```bash
rxiv figures [OPTIONS] [MANUSCRIPT_PATH]
```

#### Options

- `--force, -f`: Force regeneration of all figures
- `--figures-dir, -d TEXT`: Custom figures directory path
- `--help`: Show help

#### Examples

```bash
rxiv figures                            # Generate from MANUSCRIPT/FIGURES/
rxiv figures MY_PAPER/                  # Generate from custom directory
rxiv figures --force                    # Force regeneration
rxiv figures --figures-dir custom/path  # Custom figures directory
```

### `rxiv arxiv`

Prepare arXiv submission package.

```bash
rxiv arxiv [OPTIONS] [MANUSCRIPT_PATH]
```

#### Options

- `--output-dir, -o TEXT`: Output directory (default: output)
- `--arxiv-dir, -a TEXT`: Custom arXiv directory path
- `--zip-filename, -z TEXT`: Custom zip filename
- `--no-zip`: Don't create zip file
- `--help`: Show help

#### Examples

```bash
rxiv arxiv                              # Prepare arXiv package
rxiv arxiv MY_PAPER/                    # Prepare from custom directory
rxiv arxiv --no-zip                     # Don't create zip file
rxiv arxiv --zip-filename custom.zip    # Custom zip filename
```

### `rxiv init`

Initialize a new manuscript directory.

```bash
rxiv init [OPTIONS] [MANUSCRIPT_PATH]
```

#### Options

- `--template, -t {basic,research,preprint}`: Template to use (default: basic)
- `--force, -f`: Force overwrite existing files
- `--help`: Show help

#### Examples

```bash
rxiv init                               # Initialize MANUSCRIPT/
rxiv init MY_PAPER/                     # Initialize custom directory
rxiv init --template research           # Use research template
rxiv init --force                       # Overwrite existing files
```

### `rxiv bibliography`

Bibliography management commands.

```bash
rxiv bibliography COMMAND [OPTIONS]
```

#### Subcommands

##### `rxiv bibliography fix`

Fix bibliography issues automatically.

```bash
rxiv bibliography fix [OPTIONS] [MANUSCRIPT_PATH]
```

**Options:**
- `--dry-run, -d`: Preview fixes without applying
- `--help`: Show help

**Examples:**
```bash
rxiv bibliography fix                   # Fix bibliography issues
rxiv bibliography fix MY_PAPER/         # Fix in custom directory
rxiv bibliography fix --dry-run         # Preview fixes
```

##### `rxiv bibliography add`

Add bibliography entries from DOIs.

```bash
rxiv bibliography add [OPTIONS] [MANUSCRIPT_PATH] DOIS...
```

**Options:**
- `--overwrite, -o`: Overwrite existing entries
- `--help`: Show help

**Examples:**
```bash
rxiv bibliography add 10.1000/doi       # Add single DOI
rxiv bibliography add 10.1000/doi1 10.1000/doi2  # Add multiple DOIs
rxiv bibliography add MY_PAPER/ 10.1000/doi       # Add to custom directory
rxiv bibliography add --overwrite 10.1000/doi     # Overwrite existing
```

##### `rxiv bibliography validate`

Validate bibliography entries.

```bash
rxiv bibliography validate [OPTIONS] [MANUSCRIPT_PATH]
```

**Options:**
- `--no-doi`: Skip DOI validation
- `--help`: Show help

**Examples:**
```bash
rxiv bibliography validate              # Validate bibliography
rxiv bibliography validate MY_PAPER/    # Validate in custom directory
rxiv bibliography validate --no-doi     # Skip DOI validation
```

### `rxiv track-changes`

Generate PDF with change tracking.

```bash
rxiv track-changes [OPTIONS] [MANUSCRIPT_PATH] TAG
```

#### Options

- `--output-dir, -o TEXT`: Output directory (default: output)
- `--help`: Show help

#### Examples

```bash
rxiv track-changes MY_PAPER/ v1.0.0     # Track changes vs tag
rxiv track-changes MANUSCRIPT/ v1.0.0   # Track changes in MANUSCRIPT/
```

### `rxiv setup`

Setup development environment.

```bash
rxiv setup [OPTIONS]
```

#### Options

- `--reinstall, -r`: Reinstall dependencies
- `--check-deps-only, -c`: Only check system dependencies
- `--help`: Show help

#### Examples

```bash
rxiv setup                              # Setup environment
rxiv setup --reinstall                  # Reinstall dependencies
rxiv setup --check-deps-only            # Check dependencies only
```

### `rxiv version`

Show version information.

```bash
rxiv version [OPTIONS]
```

#### Options

- `--detailed, -d`: Show detailed version information
- `--check-updates, -u`: Check for available updates
- `--help`: Show help

#### Examples

```bash
rxiv version                            # Show version
rxiv version --detailed                 # Show detailed system info
rxiv version --check-updates            # Check for updates
```

### `rxiv config`

Configuration management commands.

```bash
rxiv config COMMAND [OPTIONS]
```

#### Subcommands

##### `rxiv config show`

Show current configuration.

```bash
rxiv config show
```

##### `rxiv config get`

Get configuration value.

```bash
rxiv config get KEY
```

**Examples:**
```bash
rxiv config get general.default_engine
rxiv config get figures.default_dpi
```

##### `rxiv config set`

Set configuration value.

```bash
rxiv config set KEY VALUE
```

**Examples:**
```bash
rxiv config set general.default_engine docker
rxiv config set figures.default_dpi 600
rxiv config set general.verbose true
```

##### `rxiv config reset`

Reset configuration to defaults.

```bash
rxiv config reset
```

##### `rxiv config edit`

Edit configuration file in default editor.

```bash
rxiv config edit
```

## Configuration

Configuration is stored in `~/.rxiv/config.toml`.

### Configuration Keys

#### General Settings

- `general.default_engine`: Default execution engine (`local` or `docker`)
- `general.default_manuscript_path`: Default manuscript directory
- `general.default_output_dir`: Default output directory
- `general.verbose`: Enable verbose output by default
- `general.check_updates`: Check for package updates automatically

#### Build Settings

- `build.force_figures`: Force figure regeneration by default
- `build.skip_validation`: Skip validation by default
- `build.auto_clean`: Auto-clean before building

#### Validation Settings

- `validation.skip_doi`: Skip DOI validation by default
- `validation.detailed`: Show detailed validation by default

#### Figure Settings

- `figures.default_format`: Default figure format (`png`, `pdf`, `svg`)
- `figures.default_dpi`: Default figure DPI
- `figures.force_regeneration`: Force regeneration by default

#### Bibliography Settings

- `bibliography.auto_fix`: Auto-fix bibliography issues
- `bibliography.cache_timeout`: Cache timeout in days

#### Output Settings

- `output.colors`: Enable colored output
- `output.progress_bars`: Show progress bars
- `output.emoji`: Show emoji in output

### Configuration Examples

```bash
# Set Docker as default engine
rxiv config set general.default_engine docker

# Set custom manuscript path
rxiv config set general.default_manuscript_path MY_PAPERS/

# Enable verbose output by default
rxiv config set general.verbose true

# Disable update checking
rxiv config set general.check_updates false

# Set high-DPI figures
rxiv config set figures.default_dpi 600

# Skip DOI validation by default
rxiv config set validation.skip_doi true
```

## Auto-completion

Enable shell auto-completion for faster command entry.

### Installation

```bash
# For bash
rxiv --install-completion bash

# For zsh
rxiv --install-completion zsh

# For fish
rxiv --install-completion fish
```

### Usage

After installation, restart your shell and use Tab completion:

```bash
rxiv b<TAB>                    # Completes to "build"
rxiv build --f<TAB>            # Completes to "--force-figures"
rxiv config s<TAB>             # Completes to "set" and "show"
```

## Integration with Make

The CLI is designed to work alongside existing Make commands:

```bash
# Both interfaces work
make pdf                       # Legacy interface
rxiv build                     # Modern interface

# Makefile tries CLI first, falls back to legacy
make setup                     # Tries 'rxiv setup', falls back to legacy
```

## Update Notifications

Rxiv-Maker automatically checks for updates to provide the latest features and fixes.

### Automatic Update Checking

By default, the CLI checks for updates once per day:

```bash
rxiv build                              # Checks for updates in background
# 📦 Update available: 1.2.0 → 1.3.0
# Run: pip install --upgrade rxiv-maker
# Release notes: https://github.com/henriqueslab/rxiv-maker/releases/tag/v1.3.0
```

### Manual Update Checking

Check for updates manually:

```bash
rxiv version --check-updates            # Force check for updates
```

### Disabling Update Checks

Disable automatic update checks:

```bash
# Globally via configuration
rxiv config set general.check_updates false

# Per-command via flag
rxiv --no-update-check build

# Via environment variables
export RXIV_NO_UPDATE_CHECK=1          # Rxiv-specific
export NO_UPDATE_NOTIFIER=1            # Universal standard
```

### Update Cache

Update information is cached in `~/.rxiv/update_cache.json` for 24 hours to avoid excessive API calls.

## Docker Support

All CLI commands support Docker execution:

```bash
# Use Docker for specific command
rxiv build --engine docker

# Set Docker as default
rxiv config set general.default_engine docker

# All commands now use Docker by default
rxiv build
rxiv validate
rxiv clean
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid command line arguments

## Environment Variables

The CLI respects these environment variables:

- `MANUSCRIPT_PATH`: Default manuscript directory
- `RXIV_ENGINE`: Default execution engine
- `RXIV_VERBOSE`: Enable verbose output
- `RXIV_NO_UPDATE_CHECK`: Disable update checking
- `NO_UPDATE_NOTIFIER`: Disable update checking (alternative)
- `EDITOR`: Editor for `rxiv config edit`

## Examples

### Complete Workflow

```bash
# Setup
pip install rxiv-maker
rxiv --install-completion bash

# Initialize new manuscript
rxiv init MY_RESEARCH/

# Configure defaults
rxiv config set general.default_manuscript_path MY_RESEARCH/
rxiv config set figures.default_dpi 300

# Build PDF
rxiv build

# Validate
rxiv validate --detailed

# Add bibliography
rxiv bibliography add 10.1000/example.doi

# Build with fresh figures
rxiv build --force-figures

# Prepare for arXiv
rxiv arxiv

# Clean up
rxiv clean
```

### Development Workflow

```bash
# Clone and setup
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker
pip install -e .

# Enable completion
rxiv --install-completion zsh

# Work on manuscript
rxiv init PAPER/
rxiv build PAPER/

# Track changes
git tag v1.0.0
# ... make changes ...
rxiv track-changes PAPER/ v1.0.0
```

## Troubleshooting

### Command Not Found

```bash
# Solution 1: Install package
pip install -e .

# Solution 2: Use as module
python -m rxiv_maker.cli --help

# Solution 3: Use Make fallback
make pdf
```

### Configuration Issues

```bash
# Reset configuration
rxiv config reset

# Check configuration
rxiv config show

# Edit manually
rxiv config edit
```

### Auto-completion Not Working

```bash
# Reinstall completion
rxiv --install-completion bash

# Restart shell
exec $SHELL

# Check shell configuration
cat ~/.bashrc | grep rxiv
```

## Migration from Make

See [MIGRATION.md](MIGRATION.md) for detailed migration guidance.

## Further Reading

- [README.md](README.md): General overview and quickstart
- [CLAUDE.md](CLAUDE.md): Developer documentation
- [MIGRATION.md](MIGRATION.md): Migration guide from Make commands