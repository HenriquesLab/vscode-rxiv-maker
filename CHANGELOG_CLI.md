# Rxiv-Maker CLI Modernization Changelog

## 🚀 Major Release: Modern CLI Interface

### ✨ New Features

#### 🎯 Modern Command-Line Interface
- **New `rxiv` command**: Beautiful, intuitive CLI built with Click framework
- **Rich output**: Colors, progress bars, formatted tables, and emoji indicators
- **Auto-completion**: Support for bash, zsh, and fish shells
- **Configuration system**: Persistent settings in `~/.rxiv/config.toml`
- **Comprehensive help**: Context-sensitive help with examples

#### 📦 Modern Python Packaging
- **Hatch build system**: Migrated from setuptools to modern hatch + hatch-vcs
- **Git-based versioning**: Automatic version management from git tags
- **Pip installable**: `pip install rxiv-maker` for easy installation
- **Console scripts**: `rxiv` command available system-wide after installation

#### 🔧 Enhanced Developer Experience
- **Hybrid Make interface**: Updated Makefile tries CLI first, falls back to legacy
- **Backward compatibility**: All existing Make commands still work
- **Better error handling**: Clear error messages with helpful suggestions
- **Docker integration**: Full Docker support with `--engine docker`

### 🎨 CLI Commands

#### Core Commands
- `rxiv build [PATH]` - Generate PDF from manuscript
- `rxiv validate [PATH]` - Validate manuscript structure and content
- `rxiv clean [PATH]` - Clean generated files
- `rxiv figures [PATH]` - Generate figures only
- `rxiv arxiv [PATH]` - Prepare arXiv submission package

#### Manuscript Management
- `rxiv init [PATH]` - Initialize new manuscript directory
- `rxiv track-changes [PATH] [TAG]` - Generate change tracking PDF

#### Bibliography Management
- `rxiv bibliography add [DOI...]` - Add bibliography entries
- `rxiv bibliography fix` - Fix bibliography issues
- `rxiv bibliography validate` - Validate bibliography entries

#### System & Configuration
- `rxiv setup` - Setup development environment
- `rxiv config show/get/set/reset` - Configuration management
- `rxiv version` - Show version information

### 🎯 CLI Features

#### Rich Output
- **Progress bars** during long operations
- **Colored output** for better readability
- **Formatted tables** for structured information
- **Emoji indicators** for quick status recognition
- **Detailed error messages** with resolution suggestions

#### Auto-completion
```bash
# Install completion
rxiv --install-completion bash  # or zsh, fish

# Use Tab completion
rxiv b<TAB>          # Completes to "build"
rxiv build --f<TAB>  # Completes to "--force-figures"
```

#### Configuration System
```bash
# Persistent settings
rxiv config set general.default_engine docker
rxiv config set figures.default_dpi 600
rxiv config show  # Display all settings
```

#### Global Options
- `--verbose, -v` - Enable verbose output
- `--engine {local,docker}` - Choose execution engine
- `--help` - Context-sensitive help

### 🔄 Migration & Compatibility

#### Backward Compatibility
- **All Make commands still work** - Zero breaking changes
- **Environment variables preserved** - Existing workflows unchanged
- **Docker mode support** - Both interfaces support Docker

#### Migration Path
| Make Command | CLI Command | Status |
|-------------|-------------|---------|
| `make setup` | `rxiv setup` | ✅ Available |
| `make pdf` | `rxiv build` | ✅ Available |
| `make validate` | `rxiv validate` | ✅ Available |
| `make clean` | `rxiv clean` | ✅ Available |
| `make arxiv` | `rxiv arxiv` | ✅ Available |

#### Hybrid Makefile
- **Tries CLI first** - If `rxiv` is installed, uses modern interface
- **Falls back to legacy** - If CLI unavailable, uses original commands
- **Seamless transition** - Users can migrate gradually

### 📚 Enhanced Documentation

#### New Documentation Files
- **CLI_REFERENCE.md** - Complete CLI command reference
- **MIGRATION.md** - Migration guide from Make to CLI
- **Updated README.md** - Modern CLI examples and quickstart
- **Enhanced CLAUDE.md** - Developer documentation with CLI workflows

#### Installation Documentation
```bash
# Quick install
pip install rxiv-maker

# Development install
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker
pip install -e .

# Enable completion
rxiv --install-completion bash
```

### 🧪 Testing & Quality

#### Comprehensive Test Suite
- **CLI unit tests** - Test individual command functionality
- **Integration tests** - Test complete workflows
- **Configuration tests** - Test settings management
- **Error handling tests** - Test edge cases and failures

#### Test Coverage
- **Main CLI functionality** - Command parsing and execution
- **Auto-completion** - Shell completion installation
- **Configuration system** - Settings persistence and validation
- **Error scenarios** - Graceful failure handling

### 🔧 Technical Details

#### Build System Migration
- **From**: setuptools + versioneer
- **To**: hatch + hatch-vcs
- **Benefits**: Modern packaging, git-based versioning, better dependency management

#### Version Management
- **Git-based**: Version automatically derived from git tags
- **PEP 440 compliant**: Proper Python version semantics
- **Development versions**: Automatic dev versions between tags

#### Dependencies
- **Click >= 8.0.0** - Modern CLI framework
- **Rich >= 13.0.0** - Beautiful terminal output
- **Existing dependencies** - All preserved for compatibility

### 🎯 Usage Examples

#### Quick Start
```bash
# Install and setup
pip install rxiv-maker
rxiv --install-completion bash

# Initialize manuscript
rxiv init MY_PAPER/

# Build PDF
rxiv build MY_PAPER/

# Validate
rxiv validate MY_PAPER/ --detailed

# Configure defaults
rxiv config set general.default_manuscript_path MY_PAPER/
rxiv config set figures.default_dpi 600

# Build with Docker
rxiv build --engine docker

# Bibliography management
rxiv bibliography add 10.1000/example.doi
rxiv bibliography fix

# Prepare for arXiv
rxiv arxiv MY_PAPER/

# Clean up
rxiv clean MY_PAPER/
```

#### Development Workflow
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
rxiv validate PAPER/ --detailed

# Track changes
git tag v1.0.0
# ... make changes ...
rxiv track-changes PAPER/ v1.0.0
```

### 🔮 Future Enhancements

This modernization provides a foundation for future enhancements:

- **Plugin system** - Extensible command architecture
- **Configuration profiles** - Multiple configuration sets
- **Enhanced templates** - More manuscript templates
- **Interactive mode** - Guided manuscript creation
- **API integration** - Integration with external services

### 🎉 Benefits Summary

#### For Users
- **Intuitive interface** - Easy to learn and use
- **Better feedback** - Rich output and progress indication
- **Faster workflow** - Auto-completion and smart defaults
- **Flexible installation** - Multiple installation options
- **Comprehensive help** - Context-sensitive documentation

#### For Developers
- **Modern architecture** - Clean, extensible codebase
- **Better testing** - Comprehensive test coverage
- **Easier maintenance** - Modern packaging and tooling
- **Enhanced debugging** - Better error messages and logging
- **Future-ready** - Foundation for new features

#### For Teams
- **Consistent interface** - Same commands across environments
- **Docker support** - Reproducible builds
- **Configuration management** - Team-wide settings
- **Backward compatibility** - Gradual migration path
- **Documentation** - Complete reference and guides

This modernization transforms rxiv-maker from a traditional Make-based tool into a modern, professional Python package with a beautiful command-line interface while maintaining complete backward compatibility.