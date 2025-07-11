# ======================================================================
# Rxiv-Maker Base Docker Image
# ======================================================================
# This Docker image contains all system dependencies for Rxiv-Maker
# but NO Python code or rxiv-maker specific logic.
#
# This base image is designed to accelerate GitHub Actions workflows
# by pre-installing time-consuming system dependencies.
# ======================================================================

FROM ubuntu:22.04 AS base

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Set locale to avoid locale warnings
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# ======================================================================
# System Dependencies Stage
# ======================================================================

FROM base AS system-deps

# Update package lists and install essential system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential system tools
    curl \
    wget \
    ca-certificates \
    software-properties-common \
    gnupg \
    lsb-release \
    # Build tools
    build-essential \
    make \
    pkg-config \
    # Font and graphics libraries (for matplotlib, seaborn, etc.)
    libfontconfig1-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    # Additional graphics libraries
    libcairo2-dev \
    libpango1.0-dev \
    libjpeg-dev \
    libgif-dev \
    libpng-dev \
    # Git for version control
    git \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# ======================================================================
# LaTeX Installation Stage
# ======================================================================

FROM system-deps AS latex-deps

# Install comprehensive LaTeX distribution
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core LaTeX packages
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    # Font packages
    texlive-fonts-recommended \
    texlive-fonts-extra \
    # Science and math packages
    texlive-science \
    texlive-pictures \
    # Bibliography tools
    texlive-bibtex-extra \
    biber \
    # Language support
    texlive-lang-english \
    # Additional utilities
    texlive-plain-generic \
    texlive-xetex \
    texlive-luatex \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# ======================================================================
# Python Installation Stage
# ======================================================================

FROM latex-deps AS python-deps

# Install Python 3.11 and essential Python tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Upgrade pip to latest version
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install uv (modern Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Pre-install core Python libraries for rxiv-maker
RUN uv pip install --system --no-cache-dir \
    "matplotlib>=3.7.0" \
    "seaborn>=0.12.0" \
    "numpy>=1.24.0" \
    "pandas>=2.0.0" \
    "scipy>=1.10.0" \
    "Pillow>=9.0.0" \
    "pypdf>=3.0.0" \
    "PyYAML>=6.0.0" \
    "python-dotenv>=1.0.0" \
    "crossref-commons>=0.0.7" \
    "lazydocs>=0.4.8" \
    "types-requests>=2.32.4.20250611"

# Pre-install common development dependencies
RUN uv pip install --system --no-cache-dir \
    "pytest>=7.4,<8.0" \
    "py>=1.11.0" \
    "ruff>=0.8.0" \
    "mypy>=1.0" \
    "types-PyYAML>=6.0.0" \
    "nox>=2023.0.0" \
    "pytest-cov>=4.0" \
    "coverage[toml]>=7.0" \
    "pytest-notebook>=0.10.0" \
    "nbstripout>=0.7.1" \
    "pre-commit>=4.0.0"

# ======================================================================
# Node.js and Mermaid CLI Installation Stage
# ======================================================================

FROM python-deps AS nodejs-deps

# Install Node.js 18 (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium for Puppeteer (required by Mermaid CLI)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium-browser \
    && rm -rf /var/lib/apt/lists/*

# Install Mermaid CLI globally
RUN npm install -g @mermaid-js/mermaid-cli

# Install chrome-headless-shell for Puppeteer (used by Mermaid CLI)
RUN npx puppeteer browsers install chrome-headless-shell

# Set environment variables for Puppeteer to use system Chromium
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# ======================================================================
# R Installation Stage
# ======================================================================

FROM nodejs-deps AS r-deps

# Install R and required system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    # Additional R system dependencies
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    # Graphics and font libraries for R plots
    libfontconfig1-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Pre-install common R packages for faster figure generation
RUN R -e "install.packages(c('ggplot2', 'dplyr', 'scales', 'readr', 'tidyr', 'optparse', 'svglite'), repos='https://cloud.r-project.org/', dependencies=TRUE)"

# ======================================================================
# Final Optimized Stage
# ======================================================================

FROM r-deps AS final

# Create a non-root user for security (but allow GitHub Actions to work)
RUN groupadd -r rxivmaker && useradd -r -g rxivmaker -d /home/rxivmaker -s /bin/bash rxivmaker \
    && mkdir -p /home/rxivmaker \
    && chown rxivmaker:rxivmaker /home/rxivmaker

# Set up working directory
WORKDIR /workspace

# Create necessary directories with proper permissions
RUN mkdir -p /workspace/output /workspace/cache /tmp/texmf-var \
    && chown -R rxivmaker:rxivmaker /workspace /tmp/texmf-var \
    && chmod -R 777 /workspace /tmp/texmf-var

# Set environment variables for LaTeX
ENV TEXMFVAR=/tmp/texmf-var
ENV TEXMFHOME=/tmp/texmf-home
ENV TEXMFCACHE=/tmp/texmf-cache

# Set environment variables for R
ENV R_LIBS_USER=/home/rxivmaker/.R/library

# Create R library directory
RUN mkdir -p /home/rxivmaker/.R/library \
    && chown -R rxivmaker:rxivmaker /home/rxivmaker/.R

# Verify installations
RUN echo "=== Verification ===" \
    && python3 --version \
    && uv --version \
    && gh --version \
    && node --version \
    && npm --version \
    && mmdc --version \
    && R --version | head -1 \
    && pdflatex --version | head -1 \
    && biber --version | head -1 \
    && echo "=== Python packages verification ===" \
    && python3 -c "import matplotlib; print(f'matplotlib: {matplotlib.__version__}')" \
    && python3 -c "import numpy; print(f'numpy: {numpy.__version__}')" \
    && python3 -c "import pandas; print(f'pandas: {pandas.__version__}')" \
    && python3 -c "import yaml; print('PyYAML: OK')" \
    && python3 -c "import pytest; print(f'pytest: {pytest.__version__}')" \
    && python3 -c "import ruff; print('ruff: OK')" \
    && echo "=== All dependencies installed successfully ==="

# Add labels for metadata
LABEL maintainer="Rxiv-Maker Project"
LABEL description="Base image for Rxiv-Maker with system dependencies"
LABEL version="1.2"
LABEL org.opencontainers.image.source="https://github.com/henriqueslab/rxiv-maker"
LABEL org.opencontainers.image.description="Ubuntu-based image with LaTeX, Python, Node.js, R, and Mermaid CLI pre-installed"
LABEL org.opencontainers.image.licenses="MIT"

# For GitHub Actions, we need to stay as root to allow workspace access
# USER rxivmaker

# Set default command
CMD ["/bin/bash"]
