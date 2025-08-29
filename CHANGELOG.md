# Change Log

All notable changes to the "rxiv-maker" VS Code extension will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2025-08-29

### Added
- **🎨 Enhanced Python Inline Syntax Highlighting** - Consistent styling for all `{py:...}` commands
  - **Fixed TextMate Grammar Patterns** - Added proper capture groups for all Python inline commands
  - **Unified Token Coloring** - All `py:` commands now use consistent teal highlighting (#4EC9B0)
  - **Comprehensive Command Support** - Proper highlighting for import, set, get, global, context, format, and conditional commands

- **⚡ 8 New Command Palette Options** - Quick insertion commands for Python inline syntax
  - **Insert Python module import** - Smart module selection with common suggestions
  - **Insert Python from-import statement** - Template with placeholders for module and items
  - **Insert Python variable assignment** - Variable name and value placeholders
  - **Insert Python variable retrieval** - Variable name completion
  - **Insert Python context execution** - Context name and code placeholders
  - **Insert Python formatted output** - Format type suggestions (.2f, .0%, etc.)
  - **Insert Python global variable** - Global variable assignment template
  - **Insert Python conditional statement** - If-else condition template

### Fixed
- **Inconsistent syntax highlighting** - `{py:get}`, `{py:set}`, and other Python commands now have proper coloring
- **Missing capture groups** in regex patterns that prevented keyword highlighting from working
- **Token scope issues** - beginCaptures now properly reference existing capture groups
- **Command registration** - All new Python inline commands properly registered in VS Code

### Enhanced
- **User Experience** - Intelligent snippets with contextual suggestions for common use cases
- **Visual Consistency** - All Python inline commands now share the same bold teal styling
- **Command Palette Integration** - Easy access to all Python inline syntax through VS Code commands

## [0.1.0] - 2025-08-19

### Added
- **🐍 Python Code Execution Support** - Full syntax highlighting for Python execution commands
  - **Block Execution**: `{{py: code}}` with multi-line Python syntax highlighting
  - **Inline Execution**: `{py: expression}` with embedded Python expression support
  - **Smart Commands**: Insert Python block/inline commands with automatic code wrapping
  - **Snippet Support**: Template insertion with cursor placeholders for new code blocks

- **📝 Blindtext Placeholder Support** - Enhanced support for LaTeX blindtext commands  
  - **Blindtext Commands**: `{{blindtext}}` and `{{Blindtext}}` with dedicated syntax highlighting
  - **Quick Insert**: Command palette options for inserting placeholder text
  - **Custom Styling**: Purple theme highlighting for blindtext commands

- **🎨 Enhanced Syntax Highlighting** - Comprehensive theming for new semantic features
  - **Python Code**: Full Python syntax highlighting within embedded blocks
  - **Command Brackets**: Distinctive styling for `{{}}` and `{}` command delimiters
  - **Function Names**: Proper highlighting for command functions like `blindtext` and `py`
  - **Error-Safe**: Syntax highlighting works regardless of Python language server availability

- **⚡ Improved Editor Experience**
  - **Auto-Closing Pairs**: `{{` automatically closes with `}}`  
  - **Smart Selection**: Commands properly handle selected text for wrapping workflows
  - **Language Integration**: Enhanced language configuration for better code editing

### Enhanced
- **📦 Updated Extension Metadata**
  - **Keywords**: Added `python`, `dynamic-content`, and `blindtext` for better discoverability
  - **Description**: Updated to reflect Python execution and blindtext capabilities
  - **Version**: Bumped to 0.1.0 for major feature release

## [0.0.3] - 2025-08-06

### Added
- **Insert Table Reference command** - Find and insert references to tables with `@table:` or `@stable:` syntax
- **Insert Equation Reference command** - Find and insert references to equations with `@eq:` syntax  
- **Install rxiv-maker framework command** - Automated installation with dependency checking for git, make, python, and LaTeX
- **Cross-platform dependency validation** - Platform-specific installation instructions for Windows, macOS, and Linux
- **Workspace-aware installation** - Smart directory picker showing open workspace folders and common locations
- **Automatic directory creation** - Creates installation directories if they don't exist
- **Enhanced error handling** - Clear guidance when dependencies are missing with platform-specific solutions

### Changed
- **Improved figure reference detection** - Now searches both `01_MAIN.md` and `02_SUPPLEMENTARY_INFO.md` files instead of just current document
- **Enhanced label parsing** - Fixed regex to handle figure labels with additional attributes (e.g., `{#fig:label width="100%" tex_position="t"}`)
- **Corrected file naming** - Fixed search for `02_SUPPLEMENTARY_INFO.md` (was incorrectly looking for `02_SUPPLEMENTARY_INFORMATION.md`)
- **Better reference filtering** - Table and equation references now properly distinguish between regular and supplementary items

### Fixed
- **"No figure labels found" error** - Figure reference command now correctly finds all figures across manuscript files
- **Label attribute parsing** - Fixed regex pattern to handle labels with LaTeX positioning and sizing attributes
- **Cross-document reference detection** - All reference commands now search both main and supplementary files consistently

### Technical Improvements
- **Unified reference detection system** - Single `getDocumentReferences()` function handles all reference types
- **Enhanced command registration** - All new commands properly registered in package.json and extension context
- **Improved search logic** - Robust file discovery with fallback paths for different project structures
- **Better error messaging** - User-friendly error messages with specific guidance for resolution

## [0.0.2] - 2025-08-05

### Added
- Comprehensive README with detailed extension features and usage instructions
- Cross-references to main [Rxiv-Maker](https://github.com/HenriquesLab/rxiv-maker) repository
- Complete documentation of rxiv-markdown syntax support
- Installation and usage guides for different user types (beginners, teams, advanced users)
- Clear citation instructions for academic use with BibTeX and APA formats
- Related projects section linking to main framework and documentation
- Support badges showing extension capabilities (syntax highlighting, IntelliSense, etc.)

### Changed
- Updated package description to "Toolkit for scientific manuscript authoring with rxiv-maker"
- Enhanced README with professional academic styling consistent with main project
- Improved documentation structure with better organization and navigation

### Fixed
- Extension icon now has proper black background, eliminating white edges
- README badges converted from SVG to PNG-compatible format for VS Code marketplace compliance

### Removed
- Color theme functionality (themes directory and theme configuration)
- Unused theme files and related package.json entries

## [0.0.1] - 2025-08-05

### Added
- Initial release of Rxiv-Maker VS Code extension
- Syntax highlighting for rxiv-markdown files (.rxm, 01_MAIN.md, 02_SUPPLEMENTARY_INFO.md)
- Language configuration for rxiv-markdown
- Token colors for subscript, superscript, and document control elements
- IntelliSense support for citations and cross-references
- JSON schema validation for 00_CONFIG.yml files
- Commands for project management:
  - Insert Citation
  - Insert Figure Reference
  - Validate project structure
  - Build PDF
  - Clean build artifacts
  - Add bibliography entry by DOI
- Automatic workspace detection for rxiv-maker projects
- Configuration defaults for word wrapping in rxiv-markdown files

### Technical Details
- Built with TypeScript and esbuild
- Supports VS Code 1.101.0 and later
- MIT License
- Published by HenriquesLab