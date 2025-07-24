# Docker Images for Rxiv-Maker

Docker images and build infrastructure for rxiv-maker with experimental Cairo support.

## Overview

This repository contains Docker image definitions and build infrastructure for [rxiv-maker](https://github.com/HenriquesLab/rxiv-maker), an automated LaTeX article generation system. It provides both production-ready base images and experimental Cairo-optimized variants.

## Image Variants

### Base Images (`images/base/`)
- **Repository**: `henriqueslab/rxiv-maker-base`
- **Tags**: `latest`, `v1.x`
- **Architecture**: AMD64, ARM64
- **Purpose**: Production-ready images with complete LaTeX, Python, Node.js, and R environments

### Experimental Cairo Images (`images/experimental-cairo/`)
- **Repository**: `henriqueslab/rxiv-maker-experimental`
- **Tags**: `latest-cairo`, `experimental-cairo`
- **Architecture**: AMD64, ARM64
- **Purpose**: Enhanced Cairo/SVG processing capabilities for post-Puppeteer workflows

## Quick Start

### Using Pre-built Images

```bash
# Production base image
docker run -it --rm -v $(pwd):/workspace henriqueslab/rxiv-maker-base:latest

# Experimental Cairo image
docker run -it --rm -v $(pwd):/workspace henriqueslab/rxiv-maker-experimental:latest-cairo
```

### Building Images Locally

```bash
# Build base image
cd images/base
./build.sh --local

# Build experimental Cairo image
cd images/experimental-cairo
./build.sh --local
```

## Image Contents

Both image variants include:
- **Ubuntu 22.04** LTS base
- **Complete LaTeX distribution** (texlive-full)
- **Python 3.11** with scientific libraries
- **Node.js 18 LTS** with Mermaid CLI
- **R base** with common packages
- **System dependencies** for graphics and fonts

### Cairo-Specific Enhancements

The experimental Cairo images additionally include:
- Enhanced Cairo/SVG processing libraries
- CairoSVG, pycairo, cairocffi packages
- Additional font support for better rendering
- Optimized SVG-to-PNG conversion workflows

## Usage with Rxiv-Maker

### CLI Integration
```bash
# Use base image
rxiv pdf --engine docker

# Use experimental Cairo image
RXIV_DOCKER_VARIANT=experimental-cairo rxiv pdf --engine docker
```

### Makefile Integration
```bash
# Use base image
make pdf RXIV_ENGINE=DOCKER

# Use experimental Cairo image
make pdf RXIV_ENGINE=DOCKER RXIV_DOCKER_VARIANT=experimental-cairo
```

## Repository Structure

```
docker-rxiv-maker/
├── images/                        # Different image variants
│   ├── base/                     # Production base images
│   │   ├── Dockerfile            # Multi-stage build configuration
│   │   ├── build.sh              # Build and deployment script
│   │   ├── build-safe.sh         # Safe build wrapper
│   │   └── Makefile              # Management commands
│   └── experimental-cairo/       # Cairo-optimized experimental images
│       ├── Dockerfile            # Cairo-enhanced build configuration
│       ├── build.sh              # Cairo build script
│       └── test-cairo.sh         # Cairo functionality tests
├── scripts/                       # Shared utility scripts
├── docs/                         # Documentation
├── tests/                        # Integration tests
└── .github/workflows/            # CI/CD workflows
```

## Development

### Building Images

```bash
# Build and push base image
cd images/base
./build.sh --tag v1.0

# Build experimental Cairo image locally
cd images/experimental-cairo
./build.sh --local
```

### Testing Images

```bash
# Test base image functionality
cd tests
./base-image-tests.sh

# Test Cairo functionality
./cairo-tests.sh
```

## Performance

Docker images provide significant performance improvements for CI/CD:

| Environment | Build Time | Dependency Install | Size |
|-------------|------------|-------------------|------|
| Local Install | 8-15 min | 5-10 min | N/A |
| Base Image | 2-3 min | 30s | ~2.5GB |
| Cairo Image | 2-4 min | 45s | ~2.8GB |

## Documentation

- [Architecture Guide](docs/architecture.md) - How images are structured
- [Cairo Migration Guide](docs/cairo-migration.md) - Benefits of Cairo approach
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [Development Guide](docs/development.md) - Contributing to images

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `./build.sh --local`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [Rxiv-Maker Main Repository](https://github.com/HenriquesLab/rxiv-maker)
- [Docker Hub Base Images](https://hub.docker.com/r/henriqueslab/rxiv-maker-base)
- [Docker Hub Experimental Images](https://hub.docker.com/r/henriqueslab/rxiv-maker-experimental)