# Docker Infrastructure for Rxiv-Maker

Docker images and build infrastructure for rxiv-maker with mermaid.ink API integration.

## Overview

This directory contains Docker image definitions and build infrastructure for rxiv-maker. All images use the mermaid.ink API for diagram generation, eliminating browser dependencies.

## Directory Structure

```
src/docker/
├── images/
│   └── base/                     # Production base images
│       ├── Dockerfile            # Multi-stage build configuration
│       ├── build.sh              # Build and deployment script
│       ├── build-safe.sh         # Safe build wrapper
│       └── Makefile              # Management commands
└── docs/                         # Documentation
    ├── architecture.md           # How images are structured
    ├── base-images.md           # Base image documentation
    └── local-testing.md         # Local testing guide
```

## Image Details

### Base Images (`images/base/`)
- **Repository**: `henriqueslab/rxiv-maker-base`
- **Tags**: `latest`, `v1.x`
- **Architecture**: AMD64, ARM64 (native performance)
- **Purpose**: Production-ready images with complete LaTeX, Python, Node.js, and R environments
- **Features**: Mermaid.ink API integration, no browser dependencies, optimized image size

## Quick Start

### Using Pre-built Images

```bash
# Production base image
docker run -it --rm -v $(pwd):/workspace henriqueslab/rxiv-maker-base:latest
```

### Building Images Locally

```bash
# Build base image locally
cd src/docker/images/base
./build.sh --local

# Build and push to Docker Hub (requires login)
./build.sh --tag latest
```

## Image Contents

Base images include:
- **Ubuntu 22.04** LTS base
- **Complete LaTeX distribution** (texlive-full)
- **Python 3.11** with scientific libraries (NumPy, Matplotlib, etc.)
- **Node.js 18 LTS** (no mermaid-cli needed)
- **R base** with common packages and graphics support
- **SVG processing libraries**
- **Extended font collection** for better rendering
- **System dependencies** for graphics and multimedia processing

## Usage with Rxiv-Maker

### CLI Integration
```bash
# Use Docker engine mode
RXIV_ENGINE=docker rxiv pdf
```

### Manual Docker Usage
```bash
# Run with current directory as workspace
docker run -it --rm -v $(pwd):/workspace henriqueslab/rxiv-maker-base:latest
```

## Development

### Building Images

```bash
# Build and test locally
cd src/docker/images/base
make image-build

# Build and push to Docker Hub (requires Docker Hub login)
make image-push

# Build specific version
make image-version VERSION=v1.2.3
```

### Testing Images

```bash
# Test image functionality
make image-test

# Check build status
make build-status
```

## Performance

Docker images provide significant performance improvements for CI/CD:

| Environment | Build Time | Dependency Install | Size |
|-------------|------------|-------------------|------|
| Local Install | 8-15 min | 5-10 min | N/A |
| Docker Image | 2-3 min | 30s | ~2.5GB |

## Integration with GitHub Actions

Images are automatically built and pushed to Docker Hub when:
- Version changes in `src/rxiv_maker/__version__.py`
- Changes are made to Docker files in `src/docker/`
- Manual workflow dispatch is triggered

See `.github/workflows/build-docker-base.yml` for the complete CI/CD pipeline.

## License

MIT License - see main repository LICENSE file for details.