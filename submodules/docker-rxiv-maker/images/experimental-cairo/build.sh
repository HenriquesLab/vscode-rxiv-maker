#!/bin/bash
# ======================================================================
# Rxiv-Maker Experimental Cairo Docker Image Build Script
# ======================================================================
# This script builds the experimental Cairo-enhanced Docker image with
# advanced SVG processing capabilities for post-Puppeteer workflows.
#
# Usage:
#   ./build.sh                    # Build and push to Docker Hub
#   ./build.sh --local            # Build locally only
#   ./build.sh --tag v1.0-cairo   # Use specific tag
#   ./build.sh --platform linux/amd64  # Single platform
# ======================================================================

set -euo pipefail

# Default configuration
REPO="henriqueslab/rxiv-maker-experimental"
TAG="latest-cairo"
PLATFORMS="linux/amd64,linux/arm64"
LOCAL_ONLY=false
PUSH_TO_HUB=true
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --local)
            LOCAL_ONLY=true
            PUSH_TO_HUB=false
            PLATFORMS="linux/$(uname -m | sed 's/x86_64/amd64/' | sed 's/aarch64/arm64/')"
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --platform)
            PLATFORMS="$2"
            shift 2
            ;;
        --repo)
            REPO="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Rxiv-Maker Experimental Cairo Docker Image Build Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --local              Build locally only (no push to Docker Hub)"
            echo "  --tag TAG            Use specific tag (default: latest-cairo)"
            echo "  --platform PLATFORMS Build for specific platforms (default: linux/amd64,linux/arm64)"
            echo "  --repo REPOSITORY    Use different repository (default: henriqueslab/rxiv-maker-experimental)"
            echo "  --verbose            Enable verbose output"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Build and push latest-cairo"
            echo "  $0 --local                          # Build locally only"
            echo "  $0 --tag v1.0-cairo                 # Build and push with specific tag"
            echo "  $0 --platform linux/amd64           # Build for AMD64 only"
            echo "  $0 --local --verbose                # Local build with verbose output"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Color output functions
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

# Validate prerequisites
validate_prerequisites() {
    print_info "Validating prerequisites..."

    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    # Check Docker Buildx for multi-platform builds
    if [[ "$PLATFORMS" == *","* ]] && ! docker buildx version >/dev/null 2>&1; then
        print_error "Docker Buildx is required for multi-platform builds"
        exit 1
    fi

    # Check Docker Hub login if pushing
    if [[ "$PUSH_TO_HUB" == "true" ]]; then
        if ! docker info >/dev/null 2>&1; then
            print_error "Docker daemon is not running"
            exit 1
        fi

        # Test Docker Hub access (will prompt for login if needed)
        if ! docker pull hello-world >/dev/null 2>&1; then
            print_warning "Unable to pull from Docker Hub. You may need to login with 'docker login'"
        fi
    fi

    print_success "Prerequisites validated"
}

# Display build configuration
display_config() {
    print_info "Build Configuration:"
    echo "  Repository: $REPO"
    echo "  Tag: $TAG"
    echo "  Platforms: $PLATFORMS"
    echo "  Local only: $LOCAL_ONLY"
    echo "  Push to Hub: $PUSH_TO_HUB"
    echo "  Verbose: $VERBOSE"
    echo ""
}

# Build the image
build_image() {
    print_info "Building experimental Cairo image..."

    # Prepare build command
    local build_cmd="docker buildx build"
    local build_args=""

    # Add verbose flag if requested
    if [[ "$VERBOSE" == "true" ]]; then
        build_args="$build_args --progress=plain"
    fi

    # Add platform specification
    build_args="$build_args --platform $PLATFORMS"

    # Add tags
    build_args="$build_args --tag $REPO:$TAG"

    # Add additional tags for latest-cairo
    if [[ "$TAG" == "latest-cairo" ]]; then
        build_args="$build_args --tag $REPO:experimental-cairo"
    fi

    # Add push flag if not local only
    if [[ "$PUSH_TO_HUB" == "true" ]]; then
        build_args="$build_args --push"
    else
        build_args="$build_args --load"
    fi

    # Add context (current directory)
    build_args="$build_args ."

    # Execute build
    print_info "Executing: $build_cmd $build_args"

    # Record start time
    local start_time=$(date +%s)

    # Execute build command
    if ! eval "$build_cmd $build_args"; then
        print_error "Docker build failed"
        exit 1
    fi

    # Calculate build time
    local end_time=$(date +%s)
    local build_time=$((end_time - start_time))

    print_success "Build completed in ${build_time} seconds"
}

# Test the built image
test_image() {
    print_info "Testing built image..."

    # Only test if built locally
    if [[ "$LOCAL_ONLY" == "true" ]]; then
        local image_name="$REPO:$TAG"

        print_info "Testing basic functionality..."
        if ! docker run --rm "$image_name" python3 --version; then
            print_error "Python test failed"
            return 1
        fi

        print_info "Testing Cairo functionality..."
        if ! docker run --rm "$image_name" /usr/local/bin/test-cairo.sh; then
            print_error "Cairo test failed"
            return 1
        fi

        print_info "Testing LaTeX functionality..."
        if ! docker run --rm "$image_name" pdflatex --version >/dev/null 2>&1; then
            print_error "LaTeX test failed"
            return 1
        fi

        print_info "Testing Node.js and Mermaid..."
        if ! docker run --rm "$image_name" mmdc --version >/dev/null 2>&1; then
            print_error "Mermaid test failed"
            return 1
        fi

        print_info "Testing R functionality..."
        if ! docker run --rm "$image_name" R --version >/dev/null 2>&1; then
            print_error "R test failed"
            return 1
        fi

        print_success "All tests passed!"
    else
        print_info "Skipping tests (image was pushed to registry)"
    fi
}

# Display summary
display_summary() {
    print_success "Build Summary:"
    echo "  Image: $REPO:$TAG"
    echo "  Platforms: $PLATFORMS"
    if [[ "$PUSH_TO_HUB" == "true" ]]; then
        echo "  Status: Pushed to Docker Hub"
        echo "  Pull command: docker pull $REPO:$TAG"
    else
        echo "  Status: Built locally"
        echo "  Run command: docker run -it --rm $REPO:$TAG"
    fi
    echo ""
    print_info "Experimental Cairo features include:"
    echo "  • Enhanced CairoSVG and pycairo libraries"
    echo "  • Advanced SVG processing capabilities"
    echo "  • Extended font support for better rendering"
    echo "  • Optimized SVG-to-PNG conversion workflows"
    echo ""
}

# Main execution
main() {
    print_info "Starting Rxiv-Maker Experimental Cairo Docker build..."
    echo ""

    validate_prerequisites
    display_config
    build_image
    test_image
    display_summary

    print_success "Experimental Cairo Docker image build completed successfully!"
}

# Execute main function
main "$@"
