# Architecture Overview

Rxiv-Maker converts Markdown manuscripts into publication-ready PDFs through a multi-stage processing pipeline.

## Processing Pipeline

1. **Configuration Loading** - Parse YAML metadata (`00_CONFIG.yml`)
2. **Figure Generation** - Execute Python/Mermaid scripts  
3. **Markdown to LaTeX** - Convert Enhanced Markdown (rxiv-markdown) with content protection
4. **LaTeX Compilation** - Generate final PDF with bibliography

## Key Components

- **Converters** (`src/py/converters/`) - Markdown element processors with content protection
- **Processors** (`src/py/processors/`) - High-level document processing
- **Commands** (`src/py/commands/`) - CLI entry points and utilities

## Content Protection System

The conversion pipeline uses a sophisticated protection system to prevent processor interference:

1. Protect mathematical expressions and code blocks
2. Process document elements in specific order
3. Restore protected content at appropriate stages

See [CLAUDE.md](../CLAUDE.md) for detailed architecture documentation.
