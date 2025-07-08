# Rxiv-Maker VS Code Extension

A VS Code extension for scientific manuscript authoring with rxiv-maker framework.

## Features

- **Syntax Highlighting**: Custom syntax highlighting for rxiv-maker markdown files (.rxm)
- **Citation Completion**: IntelliSense for bibliography entries from 03_REFERENCES.bib
- **Cross-reference Completion**: Autocompletion for @fig:, @table:, @eq:, @snote: references
- **YAML Validation**: Schema validation for 00_CONFIG.yml configuration files
- **Project Commands**: Insert citations, figure references, and validate project structure

## Supported Syntax

- Cross-references: `@fig:label`, `@sfig:label`, `@table:label`, `@stable:label`, `@eq:label`, `@snote:label`
- Citations: `@citation`, `[@cite1;@cite2]`
- Math expressions: `$inline$`, `$$block$$`, `$$equation$$ {#eq:label}`
- Scientific notation: `~subscript~`, `^superscript^`
- Document control: `<newpage>`, `<clearpage>`
- Figure metadata: `{#fig:label width="50%" tex_position="t"}`

## Usage

1. Open a workspace containing rxiv-maker files
2. Files with `.rxm` extension will automatically use rxiv-markdown language mode
3. Use Ctrl+Space for autocompletion of citations and references
4. Use Command Palette commands for inserting citations and references

## Commands

- `Rxiv-Maker: Insert Citation` - Insert bibliography citation
- `Rxiv-Maker: Insert Figure Reference` - Insert figure reference
- `Rxiv-Maker: Validate Project Structure` - Check project files

## Requirements

This extension works with rxiv-maker project structure:
- `00_CONFIG.yml` - Project configuration
- `01_MAIN.rxm` - Main manuscript file
- `03_REFERENCES.bib` - Bibliography file
- `FIGURES/` - Figure directory (optional)