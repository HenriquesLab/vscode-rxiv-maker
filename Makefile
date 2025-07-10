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

# Detect operating system
ifeq ($(OS),Windows_NT)
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
ifeq ($(OS),Windows_NT)
    ENV_FILE_EXISTS := $(shell if exist ".env" (echo true) else (echo false))
else
    ENV_FILE_EXISTS := $(shell [ -f ".env" ] && echo "true" || echo "false")
endif

# Cross-platform Python command selection (prefer uv, then venv, then system python)
ifeq ($(OS),Windows_NT)
    # Windows detection
    PYTHON_CMD := $(shell where uv >nul 2>&1 && echo uv run python || (if exist "$(VENV_PYTHON)" (echo $(PWD)\$(VENV_PYTHON)) else (echo $(PYTHON_EXEC))))
else
    # Unix-like systems (macOS, Linux)
    PYTHON_CMD := $(shell if command -v uv >$(SHELL_NULL) 2>&1; then echo "uv run python"; elif [ -f "$(VENV_PYTHON)" ]; then echo "$(PWD)/$(VENV_PYTHON)"; else echo "$(PYTHON_EXEC)"; fi)
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
ifeq ($(OS),Windows_NT)
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
	@echo "🔧 Setting up Python environment with uv on $(DETECTED_OS)..."
ifeq ($(OS),Windows_NT)
	@where uv >nul 2>&1 && ( \
		echo "✅ Found uv, using it for environment management" && \
		echo "📦 Installing dependencies with uv..." && \
		uv sync --dev \
	) || ( \
		echo "⚠️  uv not found, installing it first..." && \
		powershell -Command "irm https://astral.sh/uv/install.ps1 | iex" && \
		echo "✅ uv installed, setting up project..." && \
		uv sync --dev \
	)
else
	@if command -v uv >$(SHELL_NULL) 2>&1; then \
		echo "✅ Found uv, using it for environment management"; \
		echo "📦 Installing dependencies with uv..."; \
		uv sync --dev; \
	else \
		echo "⚠️  uv not found, installing it first..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed, setting up project..."; \
		uv sync --dev; \
	fi
endif
	@echo "✅ Setup complete! Now you can run 'make pdf' to create your document."
	@echo "Note: You'll also need LaTeX installed on your system."
	@echo "💡 Virtual environment is available at .venv/ (automatically used by make commands)"

# Reinstall Python dependencies (removes .venv and creates new one) - cross-platform
.PHONY: setup-reinstall
setup-reinstall:
	@echo "🔄 Reinstalling Python environment with uv on $(DETECTED_OS)..."
ifeq ($(OS),Windows_NT)
	@if exist ".venv" ( \
		echo "🗑️  Removing existing virtual environment..." && \
		rmdir /s /q .venv \
	)
	@where uv >nul 2>&1 && ( \
		echo "✅ Found uv, using it for environment management" && \
		echo "📦 Installing dependencies with uv..." && \
		uv sync --dev \
	) || ( \
		echo "⚠️  uv not found, installing it first..." && \
		powershell -Command "irm https://astral.sh/uv/install.ps1 | iex" && \
		echo "✅ uv installed, setting up project..." && \
		uv sync --dev \
	)
else
	@if [ -d ".venv" ]; then \
		echo "🗑️  Removing existing virtual environment..."; \
		rm -rf .venv; \
	fi
	@if command -v uv >$(SHELL_NULL) 2>&1; then \
		echo "✅ Found uv, using it for environment management"; \
		echo "📦 Installing dependencies with uv..."; \
		uv sync --dev; \
	else \
		echo "⚠️  uv not found, installing it first..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed, setting up project..."; \
		uv sync --dev; \
	fi
endif
	@echo "✅ Reinstall complete! Now you can run 'make pdf' to create your document."
	@echo "Note: You'll also need LaTeX installed on your system."
	@echo "💡 Virtual environment is available at .venv/ (automatically used by make commands)"

# Generate PDF with validation (requires LaTeX installation)
.PHONY: pdf
pdf: _generate_figures _validate_quiet _build_pdf
	@MANUSCRIPT_PATH="$(MANUSCRIPT_PATH)" MERMAID_CLI_OPTIONS="$(MERMAID_CLI_OPTIONS)" $(PYTHON_CMD) src/py/commands/copy_pdf.py --output-dir $(OUTPUT_DIR)
	@if [ -f "$(OUTPUT_DIR)/$(OUTPUT_PDF)" ]; then \
		echo "✅ PDF compilation complete: $(OUTPUT_DIR)/$(OUTPUT_PDF)"; \
	else \
		echo "❌ Error: PDF file was not created"; \
		echo "💡 Run 'make validate-detailed' for comprehensive error analysis"; \
		exit 1; \
	fi

# Generate PDF without validation (for debugging)
.PHONY: pdf-no-validate
pdf-no-validate: _build_pdf
	@MANUSCRIPT_PATH="$(MANUSCRIPT_PATH)" $(PYTHON_CMD) src/py/commands/copy_pdf.py --output-dir $(OUTPUT_DIR)
	@if [ -f "$(OUTPUT_DIR)/$(OUTPUT_PDF)" ]; then \
		echo "✅ PDF compilation complete: $(OUTPUT_DIR)/$(OUTPUT_PDF)"; \
	else \
		echo "❌ Error: PDF file was not created"; \
		echo "💡 Run 'make validate-detailed' for comprehensive error analysis"; \
		exit 1; \
	fi

# Prepare arXiv submission package
.PHONY: arxiv
arxiv: _generate_files
	@echo "Preparing arXiv submission package..."
	@$(PYTHON_CMD) prepare_arxiv.py --output-dir $(OUTPUT_DIR) --arxiv-dir $(OUTPUT_DIR)/arxiv_submission --zip-filename $(OUTPUT_DIR)/for_arxiv.zip --zip
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
# 🔨 INTERNAL BUILD TARGETS
# ======================================================================

# Internal target for generating figures only
.PHONY: _generate_figures
_generate_figures:
	@echo "Checking manuscript directory structure..."
	@if [ ! -d "$(FIGURES_DIR)" ]; then \
		echo "⚠️  WARNING: FIGURES directory not found: $(FIGURES_DIR)"; \
		echo "   Creating FIGURES directory..."; \
		mkdir -p $(FIGURES_DIR); \
		echo "   ✅ Created $(FIGURES_DIR)"; \
		echo "   💡 Add figure generation scripts (.py) or Mermaid diagrams (.mmd) to this directory"; \
		echo "   💡 Or manually place figure files in subdirectories (e.g., Figure_1/Figure_1.svg)"; \
	fi

	@echo "Checking if figures need to be generated..."
	@NEED_FIGURES=false; \
	if [ -d "$(FIGURES_DIR)" ]; then \
		for mmd_file in $(FIGURES_DIR)/*.mmd; do \
			if [ -f "$$mmd_file" ]; then \
				base_name=$$(basename "$$mmd_file" .mmd); \
				if [ ! -f "$(FIGURES_DIR)/$$base_name/$$base_name.pdf" ]; then \
					NEED_FIGURES=true; \
					break; \
				fi; \
			fi; \
		done; \
	fi; \
	if [ "$$NEED_FIGURES" = "true" ] || [ "$(FORCE_FIGURES)" = "true" ]; then \
		echo "Generating figures from $(FIGURES_DIR)..."; \
		MANUSCRIPT_PATH="$(MANUSCRIPT_PATH)" MERMAID_CLI_OPTIONS="$(MERMAID_CLI_OPTIONS)" $(PYTHON_CMD) $(FIGURE_SCRIPT) --figures-dir $(FIGURES_DIR) --output-dir $(FIGURES_DIR) --format pdf; \
	fi

	@echo "Checking if Python figure scripts need to be executed..."
	@NEED_PYTHON_FIGURES=false; \
	if [ -d "$(FIGURES_DIR)" ]; then \
		for py_file in $(FIGURES_DIR)/*.py; do \
			if [ -f "$$py_file" ]; then \
				base_name=$$(basename "$$py_file" .py); \
				if [ ! -f "$(FIGURES_DIR)/$$base_name/$$base_name.png" ] || [ ! -f "$(FIGURES_DIR)/$$base_name/$$base_name.pdf" ]; then \
					NEED_PYTHON_FIGURES=true; \
					break; \
				fi; \
			fi; \
		done; \
	fi; \
	if [ "$$NEED_PYTHON_FIGURES" = "true" ] || [ "$(FORCE_FIGURES)" = "true" ]; then \
		echo "Executing Python figure generation scripts..."; \
		CURRENT_DIR=$$(pwd); \
		cd $(FIGURES_DIR) && \
		for py_file in *.py; do \
			if [ -f "$$py_file" ]; then \
				echo "  Running $$py_file..."; \
				$(PYTHON_CMD) "$$py_file" || { echo "Error running $$py_file"; exit 1; }; \
			fi; \
		done; \
		cd $$CURRENT_DIR; \
	fi

# Internal target for building PDF (used by both pdf and local targets)
.PHONY: _build_pdf
_build_pdf: _generate_files
	@echo "Compiling LaTeX to PDF..."
	@COMPILATION_SUCCESS=true; \
	cd $(OUTPUT_DIR) && \
	 pdflatex -interaction=nonstopmode $(OUTPUT_TEX) || COMPILATION_SUCCESS=false; \
	 bibtex $(MANUSCRIPT_NAME) || true; \
	 pdflatex -interaction=nonstopmode $(OUTPUT_TEX) || COMPILATION_SUCCESS=false; \
	 pdflatex -interaction=nonstopmode $(OUTPUT_TEX) || COMPILATION_SUCCESS=false; \
	if [ "$$COMPILATION_SUCCESS" = "false" ] && [ -f "$(OUTPUT_DIR)/$(MANUSCRIPT_NAME).log" ]; then \
		echo ""; \
		echo "⚠️  LaTeX compilation encountered errors. Analyzing..."; \
		$(PYTHON_CMD) src/py/commands/validate.py "$(MANUSCRIPT_PATH)" --no-latex=false --detailed 2>/dev/null || true; \
		echo ""; \
		echo "💡 Run 'make validate-latex' for detailed LaTeX error analysis"; \
	fi
	@echo "PDF compilation complete: $(OUTPUT_DIR)/$(OUTPUT_PDF)"
	@MANUSCRIPT_PATH="$(MANUSCRIPT_PATH)" $(PYTHON_CMD) src/py/commands/analyze_word_count.py

# Internal target for generating all necessary files
.PHONY: _generate_files
_generate_files:
	@echo "Setting up output directory..."
	@mkdir -p $(OUTPUT_DIR)
	@mkdir -p $(OUTPUT_DIR)/Figures

	@echo "Generating $(OUTPUT_TEX) from $(ARTICLE_MD)..."
	@MANUSCRIPT_PATH="$(MANUSCRIPT_PATH)" $(PYTHON_CMD) $(PYTHON_SCRIPT) --output-dir $(OUTPUT_DIR)

	@echo "Copying necessary files to $(OUTPUT_DIR)..."
	@cp $(STYLE_DIR)/*.cls $(OUTPUT_DIR)/ 2>/dev/null || echo "No .cls files found"
	@cp $(STYLE_DIR)/*.bst $(OUTPUT_DIR)/ 2>/dev/null || echo "No .bst files found"
	@cp $(STYLE_DIR)/*.sty $(OUTPUT_DIR)/ 2>/dev/null || echo "No .sty files found"

	@if [ -f $(REFERENCES_BIB) ]; then \
		cp $(REFERENCES_BIB) $(OUTPUT_DIR)/; \
	fi

	@if [ -d $(FIGURES_DIR) ]; then \
		mkdir -p $(OUTPUT_DIR)/Figures; \
		cp -r $(FIGURES_DIR)/* $(OUTPUT_DIR)/Figures/ 2>/dev/null || true; \
	fi

	@find src/tex -name "*.tex" -not -name "template.tex" -exec cp {} $(OUTPUT_DIR)/ \; 2>/dev/null || true
	@find src/tex -name "*.cls" -exec cp {} $(OUTPUT_DIR)/ \; 2>/dev/null || true
	@find src/tex -name "*.sty" -exec cp {} $(OUTPUT_DIR)/ \; 2>/dev/null || true

# ======================================================================
# 🧹 MAINTENANCE
# ======================================================================

# Clean output directory (cross-platform)
.PHONY: clean
clean:
	@echo "Cleaning output directory..."
ifeq ($(OS),Windows_NT)
	@if exist "$(OUTPUT_DIR)" rmdir /s /q "$(OUTPUT_DIR)" 2>nul || echo Output directory already clean
	@echo "Cleaning generated figures..."
	@if exist "$(FIGURES_DIR)" ( \
		for /r "$(FIGURES_DIR)" %%f in (*.pdf *.png *.svg *.eps) do del "%%f" 2>nul || echo No figures to clean \
	)
	@echo "Cleaning any leftover arXiv files..."
	@if exist "for_arxiv.zip" del "for_arxiv.zip" 2>nul || echo No arXiv files to clean
	@if exist "arxiv_submission" rmdir /s /q "arxiv_submission" 2>nul || echo No arXiv submission directory to clean
else
	@rm -rf $(OUTPUT_DIR)
	@echo "Cleaning generated figures..."
	@if [ -d "$(FIGURES_DIR)" ]; then \
		find "$(FIGURES_DIR)" -name "*.pdf" -o -name "*.png" -o -name "*.svg" -o -name "*.eps" | xargs rm -f 2>/dev/null || true; \
	fi
	@echo "Cleaning any leftover arXiv files..."
	@rm -f for_arxiv.zip arxiv_submission 2>/dev/null || true
endif
	@echo "Clean complete"

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
	echo "  make pdf            - Generate PDF with validation (auto-runs Python figure scripts)"; \
	echo "  make validate       - Check manuscript for issues"; \
	echo "  make fix-bibliography - Automatically fix bibliography issues using CrossRef"; \
	echo "  make add-bibliography - Add bibliography entries from DOI(s)"; \
	echo "  make arxiv          - Prepare arXiv submission package"; \
	echo "  make clean          - Remove output directory"; \
	echo "  make help           - Show this help message"; \
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
	echo "�💡 TIP: New to Rxiv-Maker?"; \
	echo "   1. Install LaTeX on your system"; \
	echo "   2. Run 'make setup' to install Python dependencies"; \
	echo "   3. Run 'make pdf' to generate your first PDF"; \
	echo "   4. Edit files in $(ARTICLE_DIR)/ and re-run 'make pdf'"; \
	echo ""; \
	echo "💡 ADVANCED OPTIONS:"; \
	echo "   - Skip validation: make pdf-no-validate"; \
	echo "   - Force figure regeneration: make pdf FORCE_FIGURES=true (re-runs all Python/Mermaid scripts)"; \
	echo "   - Use different manuscript folder: MANUSCRIPT_PATH=path/to/folder make -e pdf"; \
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
	echo "   - Virtual environment: $(VENV_PYTHON)"
