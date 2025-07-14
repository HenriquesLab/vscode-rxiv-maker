# ======================================================================
#  _____  __   __  _  __   __         __  __          _
# |  __ \ \ \ / / (_)\ \ / /         |  \/  |        | |
# | |__) | \ V /   _  \ V /   _____  | \  / |  __ _  | | __  ___  _ __
# |  _  /   > <   | |  > <   |_____| | |\/| | / _` | | |/ / / _ \| '__|
# | | \ \  / . \  | | / . \          | |  | || (_| | |   < |  __/| |
# |_|  \_\/_/ \_\ |_|/_/ \_\         |_|  |_| \__,_| |_|\_\ \___||_|
#
# ======================================================================
# Automated Scientific Article Generation and Publishing System
#
# 🚀 QUICK START:
#   make setup        # Install Python dependencies
#   make pdf          # Generate PDF (requires LaTeX)
#   make help         # Show all available commands
#
# Author: Rxiv-Maker Project
# Documentation: See README.md
# ======================================================================

# ======================================================================
# ⚙️  CONFIGURATION VARIABLES
# ======================================================================

# Export all variables but handle MANUSCRIPT_PATH specially
export
.EXPORT_ALL_VARIABLES:

# ======================================================================
# 🌐 CROSS-PLATFORM COMPATIBILITY
# ======================================================================

# Detect operating system with GitHub Actions override
ifdef MAKEFILE_FORCE_UNIX
    # GitHub Actions environment - force Unix-style even on Windows runners
    DETECTED_OS := GitHub-Actions-Unix
    PATH_SEP := /
    SHELL_NULL := /dev/null
    PYTHON_EXEC := python3
    VENV_PYTHON := .venv/bin/python
    VENV_ACTIVATE := .venv/bin/activate
    FORCE_UNIX_SHELL := true
else ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    PATH_SEP := \\
    SHELL_NULL := nul
    PYTHON_EXEC := python
    VENV_PYTHON := .venv\Scripts\python.exe
    VENV_ACTIVATE := .venv\Scripts\activate
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        DETECTED_OS := Linux
    endif
    ifeq ($(UNAME_S),Darwin)
        DETECTED_OS := macOS
    endif
    PATH_SEP := /
    SHELL_NULL := /dev/null
    PYTHON_EXEC := python3
    VENV_PYTHON := .venv/bin/python
    VENV_ACTIVATE := .venv/bin/activate
endif

# Check if .env file exists (cross-platform)
ifdef MAKEFILE_FORCE_UNIX
    ENV_FILE_EXISTS := $(shell [ -f ".env" ] && echo "true" || echo "false")
else ifeq ($(OS),Windows_NT)
    ENV_FILE_EXISTS := $(shell if exist ".env" (echo true) else (echo false))
else
    ENV_FILE_EXISTS := $(shell [ -f ".env" ] && echo "true" || echo "false")
endif

# Cross-platform Python command selection (prefer uv, then venv, then system python)
ifdef MAKEFILE_FORCE_UNIX
    PYTHON_CMD := $(shell if command -v uv >$(SHELL_NULL) 2>&1; then echo "uv run python"; elif [ -f "$(VENV_PYTHON)" ]; then echo "$(PWD)/$(VENV_PYTHON)"; else echo "$(PYTHON_EXEC)"; fi)
else ifeq ($(OS),Windows_NT)
    # Windows detection
    PYTHON_CMD := $(shell where uv >nul 2>&1 && echo uv run python || (if exist "$(VENV_PYTHON)" (echo $(PWD)\$(VENV_PYTHON)) else (echo $(PYTHON_EXEC))))
else
    # Unix-like systems (macOS, Linux)
    PYTHON_CMD := $(shell if command -v uv >$(SHELL_NULL) 2>&1; then echo "uv run python"; elif [ -f "$(VENV_PYTHON)" ]; then echo "$(PWD)/$(VENV_PYTHON)"; else echo "$(PYTHON_EXEC)"; fi)
endif

# ======================================================================
# 🐳 ENGINE MODE CONFIGURATION (DOCKER vs LOCAL)
# ======================================================================

# Engine mode: LOCAL (default) or DOCKER
# Override with: make pdf RXIV_ENGINE=DOCKER
RXIV_ENGINE ?= LOCAL

# Docker configuration
DOCKER_IMAGE ?= henriqueslab/rxiv-maker-base:latest
DOCKER_HUB_REPO ?= henriqueslab/rxiv-maker-base

# Platform detection for Docker 
# NOTE: rxiv-maker-base image is AMD64-only due to Chrome ARM64 Linux limitations
# ARM64 users run with Rosetta emulation for full compatibility
DOCKER_PLATFORM := linux/amd64

# Engine-specific command configuration
ifeq ($(RXIV_ENGINE),DOCKER)
    # Docker mode: Run all commands inside containers with platform-specific image
    DOCKER_RUN_CMD = docker run --rm --platform $(DOCKER_PLATFORM) -v $(PWD):/workspace -w /workspace
    PYTHON_CMD = $(DOCKER_RUN_CMD) $(DOCKER_IMAGE) python
    DOCKER_MODE_ACTIVE = true
    ENGINE_STATUS = 🐳 Docker ($(DOCKER_PLATFORM))
else
    # Local mode: Use local installations (existing behavior)
    DOCKER_MODE_ACTIVE = false
    ENGINE_STATUS = 💻 Local
endif

OUTPUT_DIR := output

# Handle MANUSCRIPT_PATH with proper precedence: command line > environment > .env > default
ifeq ($(origin MANUSCRIPT_PATH), command line)
    # Command line takes highest precedence - keep the value as is
else ifeq ($(origin MANUSCRIPT_PATH), environment)
    # Environment variable (like MANUSCRIPT_PATH=value make pdf) takes precedence
else
    # Load from .env file or use default
    -include .env
    MANUSCRIPT_PATH ?= $(shell \
        if [ -f ".env" ] && grep -q "^MANUSCRIPT_PATH=" .env 2>/dev/null; then \
            grep "^MANUSCRIPT_PATH=" .env | cut -d'=' -f2 | head -1; \
        else \
            echo "MANUSCRIPT"; \
        fi)
endif

# Export MANUSCRIPT_PATH explicitly after determining its value
export MANUSCRIPT_PATH

# Default manuscript path if not provided via environment or .env (cross-platform)
ifdef MAKEFILE_FORCE_UNIX
    DEFAULT_MANUSCRIPT_PATH := $(shell \
        if [ -f ".env" ] && grep -q "^MANUSCRIPT_PATH=" .env 2>/dev/null; then \
            grep "^MANUSCRIPT_PATH=" .env | cut -d'=' -f2 | head -1; \
        else \
            echo "MANUSCRIPT"; \
        fi)
else ifeq ($(OS),Windows_NT)
    DEFAULT_MANUSCRIPT_PATH := $(shell if exist ".env" (for /f "tokens=2 delims==" %i in ('findstr /b "MANUSCRIPT_PATH=" .env 2^>nul') do @echo %i) else (echo MANUSCRIPT))
else
    DEFAULT_MANUSCRIPT_PATH := $(shell \
        if [ -f ".env" ] && grep -q "^MANUSCRIPT_PATH=" .env 2>/dev/null; then \
            grep "^MANUSCRIPT_PATH=" .env | cut -d'=' -f2 | head -1; \
        else \
            echo "MANUSCRIPT"; \
        fi)
endif

# Simple variable precedence: Use MANUSCRIPT_PATH if defined, otherwise use default
# This handles both command-line (MANUSCRIPT_PATH=value make target) and environment variables
MANUSCRIPT_PATH ?= $(DEFAULT_MANUSCRIPT_PATH)

ARTICLE_DIR = $(MANUSCRIPT_PATH)
FIGURES_DIR = $(ARTICLE_DIR)/FIGURES
STYLE_DIR := src/tex/style
PYTHON_SCRIPT := src/py/commands/generate_preprint.py
FIGURE_SCRIPT := src/py/commands/generate_figures.py

# Testing configuration
TEMPLATE_FILE := src/tex/template.tex
ARTICLE_MD = $(ARTICLE_DIR)/01_MAIN.md
MANUSCRIPT_CONFIG = $(ARTICLE_DIR)/00_CONFIG.yml
SUPPLEMENTARY_MD = $(ARTICLE_DIR)/02_SUPPLEMENTARY_INFO.md
REFERENCES_BIB = $(ARTICLE_DIR)/03_REFERENCES.bib

# Output file names based on manuscript path
MANUSCRIPT_NAME = $(notdir $(MANUSCRIPT_PATH))
OUTPUT_TEX = $(MANUSCRIPT_NAME).tex
OUTPUT_PDF = $(MANUSCRIPT_NAME).pdf

# ======================================================================
# 📌 DEFAULT AND CONVENIENCE TARGETS
# ======================================================================

# Default target
.PHONY: all
all: pdf

# ======================================================================
# 🚀 QUICK START COMMANDS
# ======================================================================
# Main user-facing commands with simple names

# Install Python dependencies (cross-platform)
.PHONY: setup
setup:
	@$(PYTHON_CMD) src/py/commands/setup_environment.py

# Reinstall Python dependencies (removes .venv and creates new one) - cross-platform
.PHONY: setup-reinstall
setup-reinstall:
	@$(PYTHON_CMD) src/py/commands/setup_environment.py --reinstall

# Check system dependencies
.PHONY: check-deps
check-deps:
	@echo "🔍 Checking system dependencies..."
	@$(PYTHON_CMD) src/py/commands/setup_environment.py --check-deps-only

# Check system dependencies (verbose)
.PHONY: check-deps-verbose
check-deps-verbose:
	@echo "🔍 Checking system dependencies (verbose)..."
	@$(PYTHON_CMD) src/py/commands/setup_environment.py --check-deps-only --verbose

# Generate PDF with validation (requires LaTeX installation)
.PHONY: pdf
pdf:
	@MANUSCRIPT_PATH="$(MANUSCRIPT_PATH)" $(PYTHON_CMD) src/py/commands/build_manager.py --manuscript-path "$(MANUSCRIPT_PATH)" --output-dir $(OUTPUT_DIR) --verbose $(if $(FORCE_FIGURES),--force-figures)

# Generate PDF without validation (for debugging)
.PHONY: pdf-no-validate
pdf-no-validate:
	@MANUSCRIPT_PATH="$(MANUSCRIPT_PATH)" $(PYTHON_CMD) src/py/commands/build_manager.py --manuscript-path "$(MANUSCRIPT_PATH)" --output-dir $(OUTPUT_DIR) --skip-validation $(if $(FORCE_FIGURES),--force-figures)

# Prepare arXiv submission package
.PHONY: arxiv
arxiv: pdf
	@echo "Preparing arXiv submission package..."
	@$(PYTHON_CMD) src/py/commands/prepare_arxiv.py --output-dir $(OUTPUT_DIR) --arxiv-dir $(OUTPUT_DIR)/arxiv_submission --zip-filename $(OUTPUT_DIR)/for_arxiv.zip --manuscript-path "$(MANUSCRIPT_PATH)" --zip
	@echo "✅ arXiv package ready: $(OUTPUT_DIR)/for_arxiv.zip"
	@echo "Copying arXiv package to manuscript directory with naming convention..."
	@YEAR=$$($(PYTHON_CMD) -c "import yaml; import sys; sys.path.insert(0, 'src/py'); config = yaml.safe_load(open('$(MANUSCRIPT_CONFIG)', 'r')); print(config.get('date', '').split('-')[0] if config.get('date') else '$(shell date +%Y)')"); \
	FIRST_AUTHOR=$$($(PYTHON_CMD) -c "import yaml; import sys; sys.path.insert(0, 'src/py'); config = yaml.safe_load(open('$(MANUSCRIPT_CONFIG)', 'r')); authors = config.get('authors', []); name = authors[0]['name'] if authors and len(authors) > 0 else 'Unknown'; print(name.split()[-1] if ' ' in name else name)"); \
	ARXIV_FILENAME="$${YEAR}__$${FIRST_AUTHOR}_et_al__for_arxiv.zip"; \
	cp $(OUTPUT_DIR)/for_arxiv.zip $(MANUSCRIPT_PATH)/$${ARXIV_FILENAME}; \
	echo "✅ arXiv package copied to: $(MANUSCRIPT_PATH)/$${ARXIV_FILENAME}"
	@echo "📤 Upload the renamed file to arXiv for submission"

# ======================================================================
# 🔍 VALIDATION COMMANDS
# ======================================================================

# Validate manuscript structure and content (with detailed report)
.PHONY: validate
validate:
	@echo "🔍 Running manuscript validation..."
	@# Use command line variable or make variable with detailed and verbose output
	@$(PYTHON_CMD) src/py/commands/validate.py "$(MANUSCRIPT_PATH)" --detailed || { \
		echo ""; \
		echo "❌ Validation failed! Please fix the issues above before building PDF."; \
		echo "💡 Run 'make validate --help' for validation options"; \
		echo "💡 Use 'make pdf-no-validate' to skip validation and build anyway."; \
		exit 1; \
	}
	@echo "✅ Validation passed!"

# Internal validation target for PDF build (quiet mode)
.PHONY: _validate_quiet
_validate_quiet:
	@echo "🔍 Validating manuscript: $(MANUSCRIPT_PATH)"
	@$(PYTHON_CMD) src/py/commands/validate.py "$(MANUSCRIPT_PATH)" || { \
		echo ""; \
		echo "❌ Validation failed! Please fix the issues above before building PDF."; \
		echo "💡 Run 'make validate' for detailed error analysis"; \
		echo "💡 Use 'make pdf-no-validate' to skip validation and build anyway."; \
		exit 1; \
	}

# ======================================================================
# 🧪 TESTING AND CODE QUALITY
# ======================================================================

# Run all tests
.PHONY: test
test:
	@echo "🧪 Running all tests..."
	@$(PYTHON_CMD) -m pytest tests/ -v

# Run unit tests only
.PHONY: test-unit
test-unit:
	@echo "🧪 Running unit tests..."
	@$(PYTHON_CMD) -m pytest tests/unit/ -v

# Run integration tests only
.PHONY: test-integration
test-integration:
	@echo "🧪 Running integration tests..."
	@$(PYTHON_CMD) -m pytest tests/integration/ -v

# Lint code
.PHONY: lint
lint:
	@echo "🔍 Linting code..."
	@$(PYTHON_CMD) -m ruff check src/

# Format code
.PHONY: format
format:
	@echo "🎨 Formatting code..."
	@$(PYTHON_CMD) -m ruff format src/

# Type checking
.PHONY: typecheck
typecheck:
	@echo "🔍 Running type checking..."
	@$(PYTHON_CMD) -m mypy src/

# Run all code quality checks
.PHONY: check
check: lint typecheck
	@echo "✅ All code quality checks passed!"

# ======================================================================
# 📚 BIBLIOGRAPHY MANAGEMENT
# ======================================================================

# Fix bibliography issues automatically by searching CrossRef
.PHONY: fix-bibliography
fix-bibliography:
	@echo "🔧 Attempting to fix bibliography issues..."
	@$(PYTHON_CMD) src/py/commands/fix_bibliography.py "$(MANUSCRIPT_PATH)" || { \
		echo ""; \
		echo "❌ Bibliography fixing failed!"; \
		echo "💡 Run with --dry-run to see potential fixes first"; \
		echo "💡 Use --verbose for detailed logging"; \
		exit 1; \
	}

# Preview bibliography fixes without applying them
.PHONY: fix-bibliography-dry-run
fix-bibliography-dry-run:
	@echo "🔍 Checking potential bibliography fixes..."
	@$(PYTHON_CMD) src/py/commands/fix_bibliography.py "$(MANUSCRIPT_PATH)" --dry-run

# Add bibliography entries from DOI
.PHONY: add-bibliography
add-bibliography:
	@# Extract DOI arguments from command line
	@DOI_ARGS=""; \
	for arg in $(MAKECMDGOALS); do \
		if echo "$$arg" | grep -E '^10\.[0-9]{4}.*' >/dev/null 2>&1; then \
			DOI_ARGS="$$DOI_ARGS $$arg"; \
		fi; \
	done; \
	if [ -z "$$DOI_ARGS" ]; then \
		echo "❌ Error: No DOI(s) provided"; \
		echo "💡 Usage: make add-bibliography 10.1000/example"; \
		echo "💡 Multiple: make add-bibliography 10.1000/ex1 10.1000/ex2"; \
		exit 1; \
	fi; \
	echo "📚 Adding bibliography entries from DOI(s):$$DOI_ARGS"; \
	$(PYTHON_CMD) src/py/commands/add_bibliography.py "$(MANUSCRIPT_PATH)" $$DOI_ARGS $(if $(OVERWRITE),--overwrite) $(if $(VERBOSE),--verbose); \
	exit 0

# Allow DOI patterns as pseudo-targets
.PHONY: $(shell echo 10.*)
10.%: ;
	@# DOI patterns are handled by add-bibliography target

# ======================================================================
# 🔨 INTERNAL BUILD TARGETS (Deprecated - now handled by Python)
# ======================================================================
# These targets are kept for compatibility but delegate to Python commands

# ======================================================================
# 🧹 MAINTENANCE
# ======================================================================

# Clean output directory (cross-platform)
.PHONY: clean
clean:
	@MANUSCRIPT_PATH="$(MANUSCRIPT_PATH)" $(PYTHON_CMD) src/py/commands/cleanup.py --manuscript-path "$(MANUSCRIPT_PATH)" --output-dir $(OUTPUT_DIR)

# Clean only output directory
.PHONY: clean-output
clean-output:
	@$(PYTHON_CMD) src/py/commands/cleanup.py --output-only --output-dir $(OUTPUT_DIR)

# Clean only generated figures
.PHONY: clean-figures
clean-figures:
	@MANUSCRIPT_PATH="$(MANUSCRIPT_PATH)" $(PYTHON_CMD) src/py/commands/cleanup.py --figures-only --manuscript-path "$(MANUSCRIPT_PATH)"

# Clean only arXiv files
.PHONY: clean-arxiv
clean-arxiv:
	@$(PYTHON_CMD) src/py/commands/cleanup.py --arxiv-only

# Clean only temporary files
.PHONY: clean-temp
clean-temp:
	@$(PYTHON_CMD) src/py/commands/cleanup.py --temp-only

# Clean only cache files
.PHONY: clean-cache
clean-cache:
	@$(PYTHON_CMD) src/py/commands/cleanup.py --cache-only

# ======================================================================
# 🐳 DOCKER ENGINE MODE
# ======================================================================

# Note: Docker image management commands are in src/docker/Makefile for maintainers.
# End users can use RXIV_ENGINE=DOCKER with any command for containerized execution.

# Show help
.PHONY: help
help:
	@VERSION=$$($(PYTHON_CMD) -c "import sys; sys.path.insert(0, 'src/py'); from src.py import __version__; print(__version__)" 2>/dev/null || echo "unknown"); \
	echo "====================================="; \
	echo "Rxiv-Maker v$$VERSION - Makefile Commands"; \
	echo "Platform: $(DETECTED_OS)"; \
	echo "====================================="; \
	echo ""; \
	echo "🚀 ESSENTIAL COMMANDS:"; \
	echo "  make setup          - Install Python dependencies"; \
	echo "  make setup-reinstall - Reinstall dependencies (removes .venv and creates new one)"; \
	echo "  make check-deps     - Check system dependencies (LaTeX, Make, Node.js, R)"; \
	echo "  make pdf            - Generate PDF with validation (auto-runs Python figure scripts)"; \
	echo "  make validate       - Check manuscript for issues"; \
	echo "  make fix-bibliography - Automatically fix bibliography issues using CrossRef"; \
	echo "  make add-bibliography - Add bibliography entries from DOI(s)"; \
	echo "  make arxiv          - Prepare arXiv submission package"; \
	echo "  make clean          - Remove output directory and clean all files"; \
	echo "  make clean-output   - Remove only output directory"; \
	echo "  make clean-figures  - Remove only generated figures"; \
	echo "  make clean-arxiv    - Remove only ArXiv files"; \
	echo "  make clean-temp     - Remove only temporary files"; \
	echo "  make clean-cache    - Remove only cache files"; \
	echo "  make help           - Show this help message"; \
	echo ""; \
	echo "🐳 DOCKER ENGINE MODE:"; \
	echo "  Current engine: $(ENGINE_STATUS)"; \
	echo "  make pdf RXIV_ENGINE=DOCKER     - Generate PDF using Docker container"; \
	echo "  make validate RXIV_ENGINE=DOCKER - Validate manuscript using Docker"; \
	echo "  make test RXIV_ENGINE=DOCKER     - Run tests in Docker container"; \
	echo "  Note: Docker image management in src/docker/Makefile"; \
	echo ""; \
	echo "📁 DIRECTORIES:"; \
	echo "  - Manuscript files: $(ARTICLE_DIR)/"; \
	echo "  - Figures:          $(FIGURES_DIR)/"; \
	echo "  - Output:           $(OUTPUT_DIR)/"; \
	echo ""; \
	echo "�️  FIGURES SETUP:"; \
	echo "   - Create $(FIGURES_DIR)/ directory for figure content"; \
	echo "   - Add Python scripts (.py) to generate figures programmatically"; \
	echo "   - Add Mermaid diagrams (.mmd) for flowcharts/diagrams"; \
	echo "   - Or place static figures in subdirectories (e.g., Figure_1/Figure_1.svg)"; \
	echo "   - Build system creates FIGURES directory automatically if missing"; \
	echo ""; \
	echo "💡 TIP: New to Rxiv-Maker?"; \
	echo "   1. Run 'make check-deps' to see what you need to install"; \
	echo "   2. Run 'make setup' to install Python dependencies"; \
	echo "   3. Run 'make pdf' to generate your first PDF"; \
	echo "   4. Edit files in $(ARTICLE_DIR)/ and re-run 'make pdf'"; \
	echo ""; \
	echo "💡 ADVANCED OPTIONS:"; \
	echo "   - Skip validation: make pdf-no-validate"; \
	echo "   - Force figure regeneration: make pdf FORCE_FIGURES=true (re-runs all Python/Mermaid scripts)"; \
	echo "   - Use different manuscript folder: MANUSCRIPT_PATH=path/to/folder make -e pdf"; \
	echo "   - Docker engine mode: RXIV_ENGINE=DOCKER make pdf (uses containers)"; \
	echo "   - Custom Docker image: DOCKER_IMAGE=my/image:tag RXIV_ENGINE=DOCKER make pdf"; \
	echo "   - Verbose dependency check: make check-deps-verbose"; \
	echo "   - Skip system deps check: python src/py/commands/setup_environment.py --no-check-system-deps"; \
	echo "   - Preview bibliography fixes: make fix-bibliography-dry-run"; \
	echo "   - Add bibliography: make add-bibliography 10.1000/example"; \
	echo "   - Multiple DOIs: make add-bibliography 10.1000/ex1 10.1000/ex2"; \
	echo "   - Validation options: $(PYTHON_EXEC) src/py/commands/validate.py --help"; \
	echo "   - arXiv files created in: $(OUTPUT_DIR)/arxiv_submission/"; \
	echo "   - arXiv ZIP file: $(OUTPUT_DIR)/for_arxiv.zip"; \
	echo ""; \
	echo "🌐 PLATFORM NOTES:"; \
	echo "   - Platform detected: $(DETECTED_OS)"; \
	echo "   - Python command: $(PYTHON_CMD)"; \
	echo "   - Virtual environment: $(VENV_PYTHON)"; \
	echo ""; \
	echo "🔧 PLATFORM-AGNOSTIC IMPLEMENTATION:"; \
	echo "   - Cross-platform Python commands handle complex operations"; \
	echo "   - Simplified Makefile delegates to Python modules"; \
	echo "   - Better error handling and platform compatibility"
