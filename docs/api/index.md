# Rxiv-Maker API Documentation

This section provides comprehensive API documentation for the rxiv-maker Python package.

## Package Structure

The rxiv-maker package is organized into several key modules:

### Core Modules

- **[CLI](cli.md)** - Command-line interface and argument parsing
- **[Commands](commands.md)** - High-level command implementations
- **[Converters](converters.md)** - Markdown to LaTeX conversion pipeline
- **[Processors](processors.md)** - Document processing utilities
- **[Validators](validators.md)** - Content validation and error checking

### Supporting Modules

- **[Utils](utils.md)** - Utility functions and helpers
- **[Docker](docker.md)** - Docker container management
- **[Install](install.md)** - Dependency installation system

## Quick Start

```python
import rxiv_maker
from rxiv_maker.commands.build_manager import BuildManager
from rxiv_maker.converters.md2tex import MarkdownToLatexConverter

# Basic usage
build_manager = BuildManager()
result = build_manager.build_manuscript("path/to/manuscript")
```

## Key Classes and Functions

### BuildManager
The main orchestrator for manuscript building.

```python
from rxiv_maker.commands.build_manager import BuildManager

manager = BuildManager(
    output_dir="output",
    engine="local",  # or "docker"
    verbose=True
)
```

### MarkdownToLatexConverter
Converts Enhanced Markdown to LaTeX with content protection.

```python
from rxiv_maker.converters.md2tex import MarkdownToLatexConverter

converter = MarkdownToLatexConverter()
latex_content = converter.convert(markdown_content)
```

### Validation System
Comprehensive manuscript validation.

```python
from rxiv_maker.validators.citation_validator import CitationValidator
from rxiv_maker.validators.figure_validator import FigureValidator

citation_validator = CitationValidator()
figure_validator = FigureValidator()
```

## Module Details

Click on any module below for detailed API documentation:

- [CLI Module](cli.md) - Command-line interface implementation
- [Commands Module](commands.md) - High-level command implementations  
- [Converters Module](converters.md) - Content conversion pipeline
- [Processors Module](processors.md) - Document processing
- [Validators Module](validators.md) - Content validation
- [Utils Module](utils.md) - Utility functions
- [Docker Module](docker.md) - Container management
- [Install Module](install.md) - Dependency management

## Development

For development information, see:
- [Architecture Overview](../reference/architecture.md)
- [Contributing Guide](../../CONTRIBUTING.md)
- [Local Development Setup](../platforms/LOCAL_DEVELOPMENT.md)