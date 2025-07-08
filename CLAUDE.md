# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Build and Development
- `npm run compile` - Full build with type checking, linting, and bundling
- `npm run watch` - Watch mode for development (runs both esbuild and TypeScript watchers)
- `npm run package` - Production build with minification
- `npm run check-types` - Type checking only (no emit)
- `npm run lint` - Run ESLint on source files

### Testing
- `npm run test` - Run all tests (compiles tests, builds extension, lints, then runs tests)
- `npm run compile-tests` - Compile test files to `out/` directory
- `npm run watch-tests` - Watch and compile test files
- `npm run pretest` - Prepare for testing (compile tests, build extension, lint)

### VS Code Extension Development
- Press `F5` to launch extension in new VS Code window
- `Ctrl+Shift+P` / `Cmd+Shift+P` then type "Hello World" to run the sample command
- Use `Ctrl+R` / `Cmd+R` to reload the extension host window after changes

## Architecture

### VS Code Extension for Rxiv-Maker
This is a specialized VS Code extension built with TypeScript that provides comprehensive support for scientific manuscript authoring using the rxiv-maker framework.

**Key Files:**
- `src/extension.ts` - Main extension with language support, autocompletion, and commands
- `package.json` - Extension manifest with language definitions, commands, and activation events
- `syntaxes/rxiv-markdown.tmLanguage.json` - TextMate grammar for rxiv-maker syntax highlighting
- `language-configuration.json` - Language configuration for bracket matching and auto-closing
- `schemas/config-schema.json` - JSON schema for 00_CONFIG.yml validation
- `esbuild.js` - Custom build script for bundling the extension

**Extension Features:**
- **Language Support**: Custom `rxiv-markdown` language with specialized syntax highlighting
- **Auto-detection**: Automatically detects rxiv-maker projects and sets language mode
- **Citation Completion**: IntelliSense for bibliography entries from 03_REFERENCES.bib
- **Cross-reference Completion**: Autocompletion for @fig:, @table:, @eq:, @snote: references
- **Commands**: Insert citations, insert figure references, validate project structure
- **YAML Validation**: Schema validation for 00_CONFIG.yml configuration files

**Syntax Highlighting Support:**
- Cross-references: `@fig:label`, `@sfig:label`, `@table:label`, `@stable:label`, `@eq:label`, `@snote:label`
- Citations: `@citation`, `[@cite1;@cite2]`
- Math expressions: `$inline$`, `$$block$$`, `$$equation$$ {#eq:label}`
- Scientific notation: `~subscript~`, `^superscript^`
- Document control: `<newpage>`, `<clearpage>`
- Figure metadata: `{#fig:label width="50%" tex_position="t"}`

**Activation Events:**
- When rxiv-markdown language is used
- When workspace contains 00_CONFIG.yml, 01_MAIN.md, or 03_REFERENCES.bib files

### Build System
- **Bundler**: esbuild with custom configuration
- **TypeScript**: Strict mode enabled, targeting ES2022 with Node16 modules
- **Linting**: ESLint with TypeScript plugin, enforcing naming conventions and code quality
- **Testing**: VS Code Test CLI with Mocha-style tests

### Development Workflow
1. Source code in `src/` directory
2. Language definitions in `syntaxes/` and root directory
3. Schema files in `schemas/` directory
4. Build outputs to `dist/` directory
5. Extension loads from `dist/extension.js`

## Project Structure
```
src/
├── extension.ts                          # Main extension code with completion providers
└── test/
    └── extension.test.ts                 # Test suite
syntaxes/
└── rxiv-markdown.tmLanguage.json        # TextMate grammar for syntax highlighting
schemas/
└── config-schema.json                   # JSON schema for config validation
language-configuration.json              # Language configuration
```

The extension provides a complete authoring environment for rxiv-maker scientific manuscripts with intelligent autocompletion, syntax highlighting, and project validation.