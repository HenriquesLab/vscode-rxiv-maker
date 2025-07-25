#!/bin/bash

# ======================================================================
# Rxiv-Maker Docker Image Build Script
# ======================================================================
# This script builds and pushes the Rxiv-Maker base Docker image to
# Docker Hub. The image contains all system dependencies but NO
# rxiv-maker specific code.
#
# Usage:
#   ./build.sh                    # Build and push latest
#   ./build.sh --tag v1.0        # Build and push with specific tag
#   ./build.sh --local           # Build locally only (no push)
#   ./build.sh --help            # Show help
# ======================================================================

set -e  # Exit on any error

# Configuration
DOCKER_HUB_REPO="henriqueslab/rxiv-maker-base"
DEFAULT_TAG="latest"
PLATFORMS="linux/amd64,linux/arm64"
CONTEXT_DIR="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    echo "Rxiv-Maker Docker Image Build Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --tag TAG        Build with specific tag (default: latest)"
    echo "  --local          Build locally only (no push to Docker Hub)"
    echo "  --platform PLAT  Build for specific platform (default: linux/amd64,linux/arm64)"
    echo "  --repo REPO      Use different Docker Hub repository (default: rxivmaker/base)"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                              # Build and push latest"
    echo "  $0 --tag v1.0                  # Build and push with v1.0 tag"
    echo "  $0 --local                     # Build locally only"
    echo "  $0 --platform linux/amd64      # Build for x86_64 only"
    echo "  $0 --repo myuser/rxiv-base      # Use different repository"
    echo ""
    echo "Prerequisites:"
    echo "  - Docker with buildx plugin installed"
    echo "  - Docker Hub account with push permissions"
    echo "  - Logged in to Docker Hub (docker login)"
    echo ""
}

# Parse command line arguments
TAG="$DEFAULT_TAG"
LOCAL_ONLY=false
REPO="$DOCKER_HUB_REPO"
PLATFORM="$PLATFORMS"

while [[ $# -gt 0 ]]; do
    case $1 in
        --tag)
            TAG="$2"
            shift 2
            ;;
        --local)
            LOCAL_ONLY=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --repo)
            REPO="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Validate Docker buildx is available
if ! docker buildx version &> /dev/null; then
    print_error "Docker buildx is not available. Please install or enable it."
    exit 1
fi

# Check if we're in the correct directory
if [[ ! -f "Dockerfile" ]]; then
    print_error "Dockerfile not found. Are you in the src/docker directory?"
    exit 1
fi

# Show build configuration
print_info "Build Configuration:"
echo "  Repository: $REPO"
echo "  Tag: $TAG"
echo "  Platform(s): $PLATFORM"
echo "  Local only: $LOCAL_ONLY"
echo "  Context: $CONTEXT_DIR"
echo ""

# Create buildx builder if it doesn't exist
BUILDER_NAME="rxiv-maker-builder"
if ! docker buildx inspect "$BUILDER_NAME" &> /dev/null; then
    print_info "Creating Docker buildx builder: $BUILDER_NAME"
    docker buildx create --name "$BUILDER_NAME" --driver docker-container --use
else
    print_info "Using existing Docker buildx builder: $BUILDER_NAME"
    docker buildx use "$BUILDER_NAME"
fi

# Build the image
IMAGE_NAME="$REPO:$TAG"
print_info "Building Docker image: $IMAGE_NAME"

# Build arguments
BUILD_ARGS=(
    --platform "$PLATFORM"
    --tag "$IMAGE_NAME"
    --progress plain
    --pull
)

# Push logic moved to multi-platform handling section below

# Handle local builds and multi-platform constraints
if [[ "$LOCAL_ONLY" == true ]]; then
    # Check if this is a multi-platform build
    if [[ "$PLATFORM" == *","* ]]; then
        print_error "Multi-platform builds cannot be built locally"
        print_info "For multi-platform builds, use without --local flag to push to registry"
        print_info "Or specify a single platform like --platform linux/amd64"
        exit 1
    else
        BUILD_ARGS+=(--load)
        print_info "Building locally for platform: $PLATFORM"
    fi
else
    # For push builds, check if logged in
    if ! test -f ~/.docker/config.json || ! grep -q "auths" ~/.docker/config.json 2>/dev/null; then
        print_error "Not logged in to Docker Hub. Please run 'docker login' first"
        exit 1
    fi
    BUILD_ARGS+=(--push)
    print_info "Building for push to registry"
fi

# Execute the build
print_info "Starting Docker build..."
echo "Command: docker buildx build ${BUILD_ARGS[*]} $CONTEXT_DIR"
echo ""

# Record start time for build timing
START_TIME=$(date +%s)

if docker buildx build "${BUILD_ARGS[@]}" "$CONTEXT_DIR"; then
    # Calculate build time
    END_TIME=$(date +%s)
    BUILD_DURATION=$((END_TIME - START_TIME))
    DURATION_MIN=$((BUILD_DURATION / 60))
    DURATION_SEC=$((BUILD_DURATION % 60))
    print_success "Docker build completed successfully in ${DURATION_MIN}m ${DURATION_SEC}s!"

    if [[ "$LOCAL_ONLY" == true ]]; then
        print_info "Image built locally: $IMAGE_NAME"
        print_info "To push later, run: docker push $IMAGE_NAME"

        # Quick verification for local builds
        print_info "Verifying image functionality..."
        if docker run --rm "$IMAGE_NAME" python --version >/dev/null 2>&1; then
            print_success "✅ Image verification passed"
        else
            print_warning "⚠️  Image verification failed - Python not working"
        fi
    else
        print_success "Image pushed to Docker Hub: $IMAGE_NAME"
        print_info "Image is now available at: https://hub.docker.com/r/${REPO}/tags"
    fi

    # Show image size
    if [[ "$LOCAL_ONLY" == true ]]; then
        print_info "Image size information:"
        docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    fi

    echo ""
    print_info "Next steps:"
    echo "  1. Test the image: docker run -it $IMAGE_NAME"
    echo "  2. Update GitHub Actions workflow to use: $IMAGE_NAME"
    echo "  3. Verify all dependencies are working in the container"

else
    print_error "Docker build failed!"
    exit 1
fi

# Show usage instructions
echo ""
print_info "Usage in GitHub Actions:"
echo "  container: $IMAGE_NAME"
echo ""
print_info "Usage for local development:"
echo "  docker run -it --rm -v \$(pwd):/workspace $IMAGE_NAME"
echo ""
print_info "Usage with Rxiv-Maker Docker engine mode:"
echo "  make pdf RXIV_ENGINE=DOCKER"
echo "  make validate RXIV_ENGINE=DOCKER"
echo "  make test RXIV_ENGINE=DOCKER"
echo ""

print_success "Build script completed successfully!"
