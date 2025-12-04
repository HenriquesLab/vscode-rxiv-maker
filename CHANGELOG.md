# Change Log

All notable changes to the "rxiv-maker" VS Code extension will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.3.13] - 2025-12-04

### Added
- **🌐 Open VSX Registry Support** - Extension now publishes to Open VSX Registry
  - **Multi-Platform**: Available for VSCodium, Code-OSS, and other VS Code alternatives
  - **Automated Publishing**: Release workflow automatically publishes to both VS Code Marketplace and Open VSX
  - **Easy Installation**: Users can install from either marketplace
  - **Documentation**: Updated README with Open VSX installation instructions

## [0.3.11] - 2025-10-23

### Fixed
- **🔧 LaTeX Validation** - Fixed false positive "Unmatched opening brace" errors in LaTeX blocks
  - **Apostrophe Handling**: Removed inappropriate string literal handling that treated apostrophes as string delimiters
  - **Accurate Brace Counting**: LaTeX validator now correctly counts braces in text containing quotes or apostrophes (e.g., "mAIcrobe's")
  - **LaTeX Comment Support**: Added proper handling for LaTeX comments (`%` until end of line)
  - **Better Validation**: More accurate syntax validation for complex LaTeX captions and text

### Improved
- **📦 Extension Packaging** - Optimized extension package size and distribution
  - **75% Smaller**: Reduced package size from 5.75 MB to 1.41 MB
  - **Fewer Files**: Reduced from 2,988 files to just 15 essential runtime files
  - **Added .vscodeignore**: Properly excludes development files, source code, and node_modules
  - **Faster Loading**: Leaner package improves extension loading and installation performance

## [0.3.10] - 2025-09-25

### Fixed
- **🔧 Cross-Reference Validation** - Fixed issue with cross-references not being found between manuscript files
  - **Dual Strategy Search**: Cross-reference validator now searches both project root and document directory
  - **Improved File Discovery**: Fixed issue where `@snote:getting_started` and other cross-references weren't found in supplementary files
  - **Robust Fallback**: Ensures cross-references work even when project root detection fails
  - **Better Error Handling**: More reliable validation for multi-file manuscript projects

## [0.3.9] - 2025-09-25

### Added
- **✨ Inline Code Syntax Highlighting** - Added support for `code` inline code blocks
  - **Backtick Support**: Added proper syntax highlighting for inline code using backticks
  - **Markdown Compatibility**: Enhanced markdown compatibility with standard inline code patterns
  - **Proper Scoping**: Uses standard TextMate scopes for better theme integration

### Enhanced
- **🔍 Improved Cross-Reference Detection** - Enhanced project structure awareness
  - **Project Root Detection**: Cross-reference validator now searches from the rxiv-maker project root
  - **Better File Discovery**: Automatically finds manuscript files by traversing up to find `00_CONFIG.yml`
  - **Reliable Validation**: More consistent cross-reference validation across complex project structures
  - **Fallback Support**: Gracefully falls back to current directory search when project root not found

## [0.3.8] - 2025-09-24

### Added
- **✨ Mathematical Expression Syntax Highlighting** - Enhanced support for LaTeX-style math notation
  - **Inline Math**: Added syntax highlighting for `$...$` expressions (e.g., `$E = mc^2$`, `$\alpha = \frac{\beta}{\gamma}$`)
  - **Display Math**: Added syntax highlighting for `$$...$$` expressions for centered equations
  - **Smart Detection**: Uses negative lookbehind/lookahead to properly distinguish between inline and display math
  - **Proper Scoping**: Math expressions are highlighted with dedicated TextMate scopes for extensibility

## [0.3.7] - 2025-09-24

### Fixed
- Ensure the PDF build runs in the correct manuscript folder by managing a dedicated terminal per manuscript path (cwd)
  - Prevents reusing a terminal from another workspace folder (e.g., mAIcrobebiorxivdraft) when building EXAMPLE_MANUSCRIPT
  - Names terminals like `rxiv-maker: <folder>` for clarity
  - Cleans up mapping when terminals close

### Internal
- Refactor terminal management in `src/extension.ts` to a Map keyed by cwd
- No API changes

## [0.3.5] - 2025-09-12

### Fixed
- **🐛 Citation Detection Logic Fix** - Resolved incorrect validation that excluded files with cross-references
  - **Improved Logic**: Fixed bug where presence of cross-references (`@fig:`, `@table:`, etc.) prevented citation detection
  - **Better Patterns**: Enhanced regex patterns to distinguish between citations and cross-references
  - **Bracketed Citations**: Improved detection of `[@citation]` and `[@ref1; @ref2]` formats
  - **Standalone Citations**: Better handling of standalone `@citation` patterns while excluding cross-refs

### Added
- **✨ Markdown Formatting Support** - Added bold and italic text highlighting
  - **Bold Text**: Added syntax highlighting for `**bold text**` patterns
  - **Italic Text**: Added syntax highlighting for `*italic text*` patterns
  - **Smart Patterns**: Regex patterns avoid conflicts between single and double asterisks

## [0.3.1] - 2025-09-11

### Fixed
- **🐛 LaTeX Brace Matching Fix** - Resolved false positive "Unmatched opening brace in LaTeX code" errors
  - **Block-level Validation**: LaTeX validator now processes entire TeX blocks instead of line-by-line validation
  - **Multi-line Support**: Properly handles braces that span multiple lines in complex LaTeX structures
  - **String Literal Handling**: Improved brace counting ignores braces inside quoted strings
  - **Escaped Brace Support**: Correctly handles escaped braces (`\{` and `\}`)
  - **Preserved Inline Validation**: Inline TeX expressions continue to be validated individually

### Technical Improvements
- **Enhanced Validator Architecture**: Added `validateTexBlock` method for comprehensive block validation
- **Improved Error Detection**: Better handling of unmatched closing braces with early detection
- **Maintained Compatibility**: All existing validation features preserved while fixing brace matching

## [0.2.6] - 2025-09-08

### Fixed
- **🐛 Critical Syntax Highlighting Fix** - Resolved complete syntax highlighting failure
  - **JSON Grammar Error**: Fixed malformed JSON in syntax grammar file that prevented extension loading
  - **Citation Highlighting**: Restored highlighting for complex citations like `[@izquierdo-martinez_chromosome_2025]`
  - **LaTeX Block Highlighting**: Fixed `{{tex: ...}}` block syntax highlighting
  - **Cross-Reference Highlighting**: Restored `@fig:label`, `@stable:data` reference highlighting
  - **Completion Providers**: Fixed broken citation and reference auto-completion
  - **Simplified Grammar**: Streamlined syntax patterns for better performance and reliability

### Improved
- **🔧 Enhanced Citation Support** - Better handling of complex citation patterns
  - **Multi-Citation Support**: Proper highlighting for `[@ref1; @ref2; @ref3]` patterns
  - **Complex Key Support**: Handles underscores, hyphens, and dots in citation keys
  - **Bracket Citation Support**: Full syntax highlighting for bracketed citation groups

## [0.2.5] - 2025-09-08

### Added
- **🎨 Enhanced Syntax Highlighting** - Comprehensive citation and LaTeX highlighting improvements
  - **Citation Highlighting**: Added support for `[@key]` and `[@key1; @key2]` patterns
  - **LaTeX Command Highlighting**: Inline LaTeX commands like `\textbf{}`, `\emph{}`
  - **Math Mode Highlighting**: Proper highlighting for `$...$` inline math expressions
  - **Table Syntax**: LaTeX table separators `&`, `\\`, `\hline` highlighting
  - **Cross-Reference Highlighting**: Enhanced `@fig:`, `@table:`, `@eq:` reference patterns

### Fixed
- **🔧 Completion Provider Issues** - Resolved missing completion provider classes
  - **Citation Completion**: Fixed missing `CitationCompletionProvider` implementation
  - **Reference Completion**: Fixed missing `ReferenceCompletionProvider` implementation
  - **Auto-completion**: Restored `@` trigger for citation and reference suggestions

## [0.2.3] - 2025-01-08

### Added
- **🔧 TeX Code Block Support** - Complete syntax highlighting and commands for LaTeX injection
  - **TeX Block Syntax**: `{{tex: LaTeX code}}` with proper syntax highlighting
  - **LaTeX Integration**: Full LaTeX syntax highlighting within `{{tex:}}` blocks
  - **Insert TeX Block**: Command palette option for inserting multi-line TeX blocks
  - **Insert Inline TeX**: Command palette option for inserting inline TeX code
  - **Smart Text Wrapping**: Automatically wraps selected LaTeX code in TeX blocks

- **⚡ Enhanced Reference Autocomplete** - Intelligent dropdown for cross-references
  - **Partial Typing Support**: Type `@f` to see figure options, `@t` for tables, etc.
  - **Smart Pattern Matching**: Enhanced detection of reference patterns during typing
  - **Comprehensive Coverage**: Supports `@fig:`, `@sfig:`, `@table:`, `@stable:`, `@eq:`, `@snote:`
  - **Context-Aware Filtering**: Shows only relevant references based on partial input
  - **Priority Sorting**: Reference type suggestions appear first in completion list

- **🎨 Enhanced Visual Experience** - Improved token coloring and syntax themes
  - **TeX Highlighting**: Coral orange (#FF7F50) styling for TeX command keywords
  - **LaTeX Content**: Proper syntax highlighting for LaTeX code within TeX blocks
  - **Consistent Theming**: TeX blocks integrate seamlessly with existing Python/blindtext themes

### Enhanced  
- **🔍 Improved Discoverability** - Enhanced marketplace presence
  - **Extended Keywords**: Added `tex`, `rxiv-maker`, `manuscript`, `references` for better search
  - **Command Integration**: All TeX commands properly integrated with VS Code command palette
  - **Language Support**: Enhanced language configuration for better TeX block editing

- **📝 Reference System Improvements** - More responsive and intelligent completion
  - **Better Trigger Detection**: Improved pattern matching for reference autocompletion  
  - **Enhanced Documentation**: Completion items now show reference type and line numbers
  - **Performance Optimization**: More efficient reference scanning and filtering

### Technical Improvements
- **TextMate Grammar**: Added comprehensive patterns for TeX block recognition
- **Completion Providers**: Enhanced `ReferenceCompletionProvider` with partial matching logic
- **Command Registration**: Proper registration of all TeX-related commands
- **Extension Activation**: TeX support activated automatically in rxiv-maker projects

## [0.2.2] - 2025-08-29

### Security
- **🛡️ Vulnerability Fixes** - Resolved all npm audit security issues
  - **Fixed @eslint/plugin-kit** Regular Expression DoS vulnerability (GHSA-xffm-g5w8-qvg7)  
  - **Fixed tmp package** arbitrary file write vulnerability (GHSA-52f5-9888-hmc6)
  - **Updated 3 critical packages** via npm audit fix

- **📦 Comprehensive Dependency Updates** - Enhanced security through package updates
  - **Updated TypeScript ecosystem**: @typescript-eslint/eslint-plugin, @typescript-eslint/parser
  - **Updated build tools**: esbuild 0.25.6 → 0.25.9, typescript 5.8.3 → 5.9.2
  - **Updated VS Code types**: @types/vscode 1.101.0 → 1.103.0, @types/node to latest
  - **Updated ESLint**: 9.30.1 → 9.34.0 for improved code quality

### Enhanced
- **🔧 Automated Marketplace Publishing** - VSCE_PAT integration for GitHub Actions
  - **Seamless releases**: Automated publishing to VS Code Marketplace via CI/CD
  - **Enhanced security**: All package vulnerabilities resolved (0 vulnerabilities)
  - **Build validation**: All tests pass with updated dependencies

## [0.2.1] - 2025-08-29

### Added
- **🔄 GitHub Actions Release Workflow** - Automated release pipeline for VS Code extension
  - **Tag-triggered releases** - Automatic releases when version tags are pushed
  - **GitHub Release creation** - Automatic release notes from changelog
  - **VS Code Marketplace publishing** - Automated extension publication
  - **Release asset upload** - .vsix file attached to GitHub releases
  - **Manual release trigger** - Workflow dispatch for manual releases

- **🧪 Continuous Integration Workflow** - Automated testing and validation
  - **Code quality checks** - Linting and type checking on every commit
  - **Build validation** - Ensure extension packages successfully
  - **Multi-branch testing** - CI runs on main and develop branches

### Enhanced
- **📦 Release Process** - Streamlined and automated release management
  - **Version verification** - Automatic validation that package.json matches git tag
  - **Changelog extraction** - Automatic release notes from CHANGELOG.md
  - **Marketplace integration** - Seamless publishing to VS Code Marketplace

### Technical Improvements
- **Repository structure** - Added .github/workflows for GitHub Actions
- **Build artifacts management** - .vsix files properly ignored and managed
- **Release documentation** - Comprehensive workflow documentation and summaries

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