# ======================================================================
# Rxiv-Maker Base Docker Image (Multi-Architecture)
# ======================================================================
# This Docker image contains all system dependencies for Rxiv-Maker
# but NO Python code or rxiv-maker specific logic.
#
# ARCHITECTURE SUPPORT: AMD64 and ARM64
# - Uses CairoSVG for Mermaid diagram raster conversion (Cairo-only)
# - Full cross-platform compatibility with no browser dependencies
# - Enhanced Cairo libraries for optimal SVG processing
# - Significantly smaller image size without Chrome/Chromium
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

FROM base AS systemdeps

# Update package lists and install essential system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential system tools
    curl \
    wget \
    unzip \
    ca-certificates \
    software-properties-common \
    gnupg \
    lsb-release \
    # Build tools (enhanced for Cairo compilation)
    build-essential \
    make \
    pkg-config \
    cmake \
    meson \
    ninja-build \
    # Enhanced Cairo and graphics libraries
    libcairo2-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-dev \
    libgirepository1.0-dev \
    git1.2-gobject-2.0 \
    git1.2-glib-2.0 \
    gobject-introspection \
    libglib2.0-dev \
    # Advanced SVG processing libraries
    librsvg2-dev \
    librsvg2-bin \
    libxml2-dev \
    libxslt1-dev \
    # Font rendering enhancements
    libfontconfig1-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    # Additional graphics libraries for scientific plots
    libjpeg-dev \
    libgif-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    # Python development headers for Cairo compilation
    python3-dev \
    libffi-dev \
    # Git for version control
    git \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Enhanced Cairo/CairoSVG environment variables for optimal performance
ENV PKG_CONFIG_PATH="/usr/lib/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig:/usr/lib/aarch64-linux-gnu/pkgconfig"
ENV LD_LIBRARY_PATH="/usr/lib:/usr/lib/x86_64-linux-gnu:/usr/lib/aarch64-linux-gnu"
ENV CAIRO_FC_CONFIG_DIR="/etc/fonts"
ENV XDG_CACHE_HOME="/tmp/.cache"

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# ======================================================================
# R Installation Stage (MOVED UP FOR BETTER CACHING)
# ======================================================================

FROM systemdeps AS rdeps

# Install R with enhanced graphics support
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    # Enhanced R system dependencies for graphics
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libudunits2-dev \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    # Additional R graphics packages (system versions)
    r-cran-ggplot2 \
    r-cran-dplyr \
    r-cran-scales \
    r-cran-readr \
    r-cran-tidyr \
    r-cran-cairo \
    r-cran-svglite \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Configure R for optimal performance
RUN echo 'options(repos = c(CRAN = "https://packagemanager.rstudio.com/cran/__linux__/jammy/latest"))' >> /usr/lib/R/etc/Rprofile.site \
    && echo 'options(Ncpus = parallel::detectCores())' >> /usr/lib/R/etc/Rprofile.site \
    && echo 'options(bitmapType = "cairo")' >> /usr/lib/R/etc/Rprofile.site

# Pre-install additional R graphics packages
RUN R -e "install.packages(c('optparse', 'svglite', 'Cairo', 'magick', 'rsvg'), repos='https://packagemanager.rstudio.com/cran/__linux__/jammy/latest', dependencies=TRUE, Ncpus=parallel::detectCores())"

# ======================================================================
# Node.js and Mermaid CLI Installation Stage (Minimal for SVG Generation)
# ======================================================================

FROM rdeps AS nodejsdeps

# Install Node.js 18 (LTS) using NodeSource repository
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs=18.* \
    && rm -rf /var/lib/apt/lists/*

# Install comprehensive font collection for better SVG rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core font packages
    fonts-liberation \
    fonts-liberation2 \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    # Scientific and mathematical fonts
    fonts-lmodern \
    fonts-texgyre \
    fonts-stix \
    # Unicode and emoji support
    fonts-noto-core \
    fonts-noto-ui-core \
    fonts-noto-color-emoji \
    fonts-emojione \
    # Additional font families
    fonts-roboto \
    fonts-open-sans \
    fonts-firacode \
    # Font configuration
    fontconfig \
    && rm -rf /var/lib/apt/lists/* \
    # Update font cache with verbose output
    && fc-cache -fv \
    # Create font configuration for Cairo
    && mkdir -p /etc/fonts/conf.d

# Install Mermaid CLI with enhanced configuration for SVG output
RUN npm install -g @mermaid-js/mermaid-cli@10.6.1

# Create optimized Mermaid configuration for SVG output
RUN mkdir -p /opt/mermaid && cat > /opt/mermaid/config.json << 'EOF'
{
  "theme": "default",
  "themeVariables": {
    "fontFamily": "Liberation Sans, DejaVu Sans, Arial, sans-serif",
    "fontSize": "16px"
  },
  "flowchart": {
    "useMaxWidth": false,
    "htmlLabels": true
  },
  "sequence": {
    "useMaxWidth": false
  },
  "gantt": {
    "useMaxWidth": false
  }
}
EOF

# ======================================================================
# LaTeX Installation Stage
# ======================================================================

FROM nodejsdeps AS latexdeps

# Configure debconf to avoid interactive prompts for TeX packages
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install comprehensive LaTeX distribution with proper error handling
RUN apt-get update && \
    # Set environment to avoid interactive prompts during installation
    DEBIAN_FRONTEND=noninteractive \
    # Install packages in smaller groups to avoid memory issues
    apt-get install -y --no-install-recommends \
    # Core LaTeX packages first
    texlive-latex-base \
    texlive-latex-recommended \
    && apt-get install -y --no-install-recommends \
    # Font packages
    texlive-fonts-recommended \
    texlive-fonts-extra \
    && apt-get install -y --no-install-recommends \
    # Additional packages
    texlive-latex-extra \
    texlive-science \
    texlive-pictures \
    && apt-get install -y --no-install-recommends \
    # Bibliography and language packages
    texlive-bibtex-extra \
    biber \
    texlive-lang-english \
    && apt-get install -y --no-install-recommends \
    # Advanced TeX engines and utilities
    texlive-plain-generic \
    texlive-xetex \
    texlive-luatex \
    texlive-extra-utils \
    latexdiff \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    # Fix tex-common configuration issues
    && dpkg --configure -a || true
# ======================================================================
# Python Installation Stage (MOVED TO END FOR FREQUENT CHANGES)
# ======================================================================
FROM latexdeps AS pybase
# Add deadsnakes PPA for Python 3.11 on Ubuntu 22.04
RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.11 and essential Python tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    # Additional tools for Cairo Python bindings
    cython3 \
    file \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    # Fix any remaining configuration issues
    && dpkg --configure -a || true

# Set Python 3.11 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Upgrade pip to latest version
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install uv (modern Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Make uv available globally for all users
RUN cp /root/.local/bin/uv /usr/local/bin/uv && chmod +x /usr/local/bin/uv

# Install Python packages in stages for better error handling and caching
# Stage 1: Core scientific libraries
RUN uv pip install --system --no-cache-dir \
    "numpy>=1.24.0,<2.0.0" \
    "scipy>=1.10.0,<2.0.0" \
    "matplotlib>=3.7.0,<3.9.0" \
    "seaborn>=0.12.0,<0.14.0" \
    "pandas>=2.0.0,<3.0.0" \
    "Pillow>=9.0.0,<11.0.0"

# Stage 2: Core utility libraries
RUN uv pip install --system --no-cache-dir \
    "pypdf>=3.0.0,<5.0.0" \
    "PyYAML>=6.0.0,<7.0.0" \
    "python-dotenv>=1.0.0,<2.0.0" \
    "crossref-commons>=0.0.7,<1.0.0" \
    "lazydocs>=0.4.8,<1.0.0" \
    "types-requests>=2.32.4.20250611"

# Stage 3: Cairo and graphics libraries (most problematic ones)
RUN uv pip install --system --no-cache-dir \
    "pycairo>=1.25.0,<2.0.0" \
    "cairocffi>=1.6.0,<2.0.0" \
    "pygobject>=3.40.0,<3.50.0"

# Stage 4: SVG and document processing libraries
RUN uv pip install --system --no-cache-dir \
    "cairosvg>=2.7.0,<3.0.0" \
    "svglib>=1.5.0,<2.0.0" \
    "reportlab>=4.0.0,<5.0.0" \
    "tinycss2>=1.2.0,<2.0.0" \
    "cssselect2>=0.7.0,<1.0.0" \
    "defusedxml>=0.7.0,<1.0.0" \
    "lxml>=4.9.0,<6.0.0"

# Stage 5: Development and testing dependencies
RUN uv pip install --system --no-cache-dir \
    "pytest>=7.4,<8.0" \
    "py>=1.11.0,<2.0.0" \
    "ruff>=0.8.0,<1.0.0" \
    "mypy>=1.0,<2.0" \
    "types-PyYAML>=6.0.0,<7.0.0" \
    "nox>=2023.0.0,<2025.0.0" \
    "pytest-cov>=4.0,<5.0" \
    "coverage[toml]>=7.0,<8.0" \
    "pytest-notebook>=0.10.0,<1.0.0" \
    "nbstripout>=0.7.1,<1.0.0" \
    "pre-commit>=4.0.0,<5.0.0"
# ======================================================================
# Final Optimized Stage
# ======================================================================
FROM pybase AS final
# Create a non-root user for security (but allow GitHub Actions to work)
RUN groupadd -r rxivmaker && useradd -r -g rxivmaker -d /home/rxivmaker -s /bin/bash rxivmaker \
    && mkdir -p /home/rxivmaker \
    && chown rxivmaker:rxivmaker /home/rxivmaker

# Set up working directory
WORKDIR /workspace

# Create necessary directories with proper permissions
RUN mkdir -p /workspace/output /workspace/cache /tmp/texmf-var /tmp/cairo-cache \
    && chown -R rxivmaker:rxivmaker /workspace /tmp/texmf-var /tmp/cairo-cache \
    && chmod -R 777 /workspace /tmp/texmf-var /tmp/cairo-cache

# Set environment variables for LaTeX
ENV TEXMFVAR=/tmp/texmf-var
ENV TEXMFHOME=/tmp/texmf-home
ENV TEXMFCACHE=/tmp/texmf-cache

# Cairo-specific environment variables for optimal performance
ENV CAIRO_CACHE_DIR=/tmp/cairo-cache
ENV FONTCONFIG_FILE=/etc/fonts/fonts.conf
ENV FC_CACHE_DIR=/tmp/fontconfig-cache

# Set environment variables for R
ENV R_LIBS_USER=/home/rxivmaker/.R/library

# Create additional directories for Cairo and font caching
RUN mkdir -p /home/rxivmaker/.R/library /home/rxivmaker/.cache /tmp/fontconfig-cache \
    && chown -R rxivmaker:rxivmaker /home/rxivmaker/.R /home/rxivmaker/.cache /tmp/fontconfig-cache \
    && chmod -R 777 /tmp/fontconfig-cache

# Create Cairo test script for validation
RUN cat > /usr/local/bin/test-cairo.sh << 'EOF'
#!/bin/bash
echo "Testing Cairo SVG to PNG conversion..."
python3 -c "
import cairosvg
import io
from pathlib import Path

# Create test SVG
svg_content = '''<?xml version='1.0' encoding='UTF-8'?>
<svg width='200' height='100' xmlns='http://www.w3.org/2000/svg'>
  <rect width='200' height='100' fill='lightblue' stroke='navy' stroke-width='2'/>
  <text x='100' y='50' text-anchor='middle' font-family='Liberation Sans' font-size='16'>Cairo Test</text>
</svg>'''

# Convert to PNG
png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
print(f'Successfully converted SVG to PNG ({len(png_data)} bytes)')
print('Cairo functionality verified!')
"
EOF
RUN chmod +x /usr/local/bin/test-cairo.sh

# Add labels for metadata
LABEL maintainer="Rxiv-Maker Project"
LABEL description="Base image for Rxiv-Maker with Cairo-only SVG processing (no browser dependencies)"
LABEL version="1.8-cairo-only"
LABEL org.opencontainers.image.source="https://github.com/henriqueslab/rxiv-maker"
LABEL org.opencontainers.image.description="Ubuntu-based image with LaTeX, Python, Node.js, R, Mermaid CLI, and enhanced Cairo SVG processing (no browser dependencies)"
LABEL org.opencontainers.image.licenses="MIT"

# For GitHub Actions, we need to stay as root to allow workspace access
# USER rxivmaker

# Set default command
CMD ["/bin/bash"]
