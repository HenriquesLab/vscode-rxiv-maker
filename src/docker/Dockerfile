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

# ======================================================================
# Node.js and Mermaid CLI Installation Stage
# ======================================================================

FROM python-deps AS nodejs-deps

# Install Node.js 18 (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Mermaid CLI globally
RUN npm install -g @mermaid-js/mermaid-cli

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
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# ======================================================================
# Final Optimized Stage
# ======================================================================

FROM r-deps AS final

# Create a non-root user for security
RUN groupadd -r rxivmaker && useradd -r -g rxivmaker -d /home/rxivmaker -s /bin/bash rxivmaker \
    && mkdir -p /home/rxivmaker \
    && chown rxivmaker:rxivmaker /home/rxivmaker

# Set up working directory
WORKDIR /workspace

# Create necessary directories with proper permissions
RUN mkdir -p /workspace/output /workspace/cache /tmp/texmf-var \
    && chown -R rxivmaker:rxivmaker /workspace /tmp/texmf-var

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
    && node --version \
    && npm --version \
    && mmdc --version \
    && R --version | head -1 \
    && pdflatex --version | head -1 \
    && biber --version | head -1 \
    && echo "=== All dependencies installed successfully ==="

# Add labels for metadata
LABEL maintainer="Rxiv-Maker Project"
LABEL description="Base image for Rxiv-Maker with system dependencies"
LABEL version="1.0"
LABEL org.opencontainers.image.source="https://github.com/paxcalpt/rxiv-maker"
LABEL org.opencontainers.image.description="Ubuntu-based image with LaTeX, Python, Node.js, R, and Mermaid CLI pre-installed"
LABEL org.opencontainers.image.licenses="MIT"

# Switch to non-root user
USER rxivmaker

# Set default command
CMD ["/bin/bash"]
