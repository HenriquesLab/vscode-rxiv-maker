#!/bin/bash

# ======================================================================
# Rxiv-Maker Local Docker Testing Script
# ======================================================================
# This script mirrors the GitHub Actions build-pdf workflow for local testing.
# It provides a complete local development environment that accurately reflects
# the CI/CD pipeline while optimizing for local development speed.
#
# Usage:
#   ./test-local.sh                         # Auto-detect manuscript, use EXAMPLE_MANUSCRIPT
#   ./test-local.sh --manuscript MANUSCRIPT # Use specific manuscript
#   ./test-local.sh --build-base            # Build base image locally
#   ./test-local.sh --interactive           # Drop into shell on failure
#   ./test-local.sh --clean                 # Clean up containers and volumes
#   ./test-local.sh --help                  # Show help
# ======================================================================

set -e  # Exit on any error

# Configuration
DOCKER_BASE_IMAGE="henriqueslab/rxiv-maker-base:latest"
DOCKER_TEST_IMAGE="rxiv-maker-test:local"
DOCKER_CONTAINER_NAME="rxiv-maker-test-container"
DOCKER_COMPOSE_FILE="docker-compose.test.yml"
DEFAULT_MANUSCRIPT="EXAMPLE_MANUSCRIPT"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Function to show help
show_help() {
    echo "Rxiv-Maker Local Docker Testing Script"
    echo ""
    echo "This script mirrors the GitHub Actions build-pdf workflow for local testing."
    echo ""
    echo "Usage: $0 [OPTIONS] [MANUSCRIPT_PATH]"
    echo ""
    echo "Options:"
    echo "  --manuscript PATH     Use specific manuscript directory (default: auto-detect)"
    echo "  --build-base          Build base Docker image locally instead of pulling"
    echo "  --interactive         Drop into container shell on failure for debugging"
    echo "  --clean               Clean up containers, volumes, and test images"
    echo "  --debug               Enable verbose debugging output"
    echo "  --no-cache            Disable dependency caching (slower but fresh)"
    echo "  --force-figures       Force regeneration of all figures"
    echo "  --compose             Use Docker Compose instead of raw Docker commands"
    echo "  --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                              # Test with EXAMPLE_MANUSCRIPT"
    echo "  $0 --manuscript MANUSCRIPT      # Test with custom manuscript"
    echo "  $0 --build-base                 # Build base image locally"
    echo "  $0 --interactive --debug        # Debug mode with interactive shell"
    echo "  $0 --clean                      # Clean up all test resources"
    echo ""
    echo "Manuscript Path Detection:"
    echo "  1. Command line argument (--manuscript PATH)"
    echo "  2. Environment variable (MANUSCRIPT_PATH)"
    echo "  3. .env file (MANUSCRIPT_PATH=...)"
    echo "  4. Default: EXAMPLE_MANUSCRIPT"
    echo ""
    echo "Prerequisites:"
    echo "  - Docker installed and running"
    echo "  - Docker Compose (optional, for --compose mode)"
    echo "  - Internet connection (for base image pull)"
    echo ""
}

# Parse command line arguments
MANUSCRIPT_PATH=""
BUILD_BASE=false
INTERACTIVE=false
CLEAN=false
DEBUG=false
NO_CACHE=false
FORCE_FIGURES=false
USE_COMPOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --manuscript)
            MANUSCRIPT_PATH="$2"
            shift 2
            ;;
        --build-base)
            BUILD_BASE=true
            shift
            ;;
        --interactive)
            INTERACTIVE=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --force-figures)
            FORCE_FIGURES=true
            shift
            ;;
        --compose)
            USE_COMPOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            # Treat unknown options as manuscript path
            if [[ -z "$MANUSCRIPT_PATH" ]]; then
                MANUSCRIPT_PATH="$1"
            else
                print_error "Unknown option: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Validate Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

# Check Docker Compose if using compose mode
if [[ "$USE_COMPOSE" == true ]] && ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed but --compose was specified"
    exit 1
fi

# Change to project root directory
cd "$PROJECT_ROOT"

# Function to clean up resources
cleanup_resources() {
    print_info "Cleaning up Docker resources..."

    # Stop and remove containers
    if docker ps -a --format '{{.Names}}' | grep -q "$DOCKER_CONTAINER_NAME"; then
        print_info "Stopping and removing container: $DOCKER_CONTAINER_NAME"
        docker stop "$DOCKER_CONTAINER_NAME" 2>/dev/null || true
        docker rm "$DOCKER_CONTAINER_NAME" 2>/dev/null || true
    fi

    # Remove test image
    if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "$DOCKER_TEST_IMAGE"; then
        print_info "Removing test image: $DOCKER_TEST_IMAGE"
        docker rmi "$DOCKER_TEST_IMAGE" 2>/dev/null || true
    fi

    # Clean up volumes
    if docker volume ls --format '{{.Name}}' | grep -q "rxiv-maker-test"; then
        print_info "Removing test volumes..."
        docker volume ls --format '{{.Name}}' | grep "rxiv-maker-test" | xargs -r docker volume rm 2>/dev/null || true
    fi

    # Docker system prune
    if [[ "$NO_CACHE" == true ]]; then
        print_info "Pruning Docker system (no cache mode)..."
        docker system prune -f
    fi

    print_success "Cleanup completed"
}

# Handle cleanup mode
if [[ "$CLEAN" == true ]]; then
    cleanup_resources
    exit 0
fi

# Function to determine manuscript path (mirrors GitHub Actions logic)
determine_manuscript_path() {
    local manuscript_path=""

    # 1. Command line argument takes precedence
    if [[ -n "$MANUSCRIPT_PATH" ]]; then
        manuscript_path="$MANUSCRIPT_PATH"
        print_info "Using manuscript path from command line: $manuscript_path" >&2
    # 2. Environment variable
    elif [[ -n "${MANUSCRIPT_PATH:-}" ]]; then
        manuscript_path="$MANUSCRIPT_PATH"
        print_info "Using manuscript path from environment: $manuscript_path" >&2
    # 3. .env file
    elif [[ -f ".env" ]] && grep -q "^MANUSCRIPT_PATH=" .env; then
        manuscript_path=$(grep "^MANUSCRIPT_PATH=" .env | cut -d'=' -f2 | head -1)
        print_info "Using manuscript path from .env file: $manuscript_path" >&2
    # 4. Default
    else
        manuscript_path="$DEFAULT_MANUSCRIPT"
        print_info "Using default manuscript path: $manuscript_path" >&2
    fi

    # Validate manuscript directory exists
    if [[ ! -d "$manuscript_path" ]]; then
        print_error "Manuscript directory not found: $manuscript_path" >&2
        print_info "Available directories:" >&2
        ls -la . | grep '^d' | sed 's/^/  /' >&2
        exit 1
    fi

    echo "$manuscript_path"
}

# Function to build or pull base image
setup_base_image() {
    if [[ "$BUILD_BASE" == true ]]; then
        print_step "Building base Docker image locally..."
        cd src/docker
        if [[ -f "build.sh" ]]; then
            ./build.sh --local --tag latest
        else
            print_error "build.sh not found in src/docker directory"
            exit 1
        fi
        cd "$PROJECT_ROOT"
    else
        print_step "Pulling base Docker image: $DOCKER_BASE_IMAGE"
        docker pull "$DOCKER_BASE_IMAGE"
    fi
}

# Function to build test image
build_test_image() {
    print_step "Building test Docker image: $DOCKER_TEST_IMAGE"

    # Build context is project root
    docker build \
        -f src/docker/test-dockerfile \
        -t "$DOCKER_TEST_IMAGE" \
        --build-arg BASE_IMAGE="$DOCKER_BASE_IMAGE" \
        $(if [[ "$NO_CACHE" == true ]]; then echo "--no-cache"; fi) \
        $(if [[ "$DEBUG" == true ]]; then echo "--progress=plain"; fi) \
        .
}

# Function to run Docker container (mirrors GitHub Actions steps)
run_test_container() {
    local manuscript_path="$1"

    print_step "Running test container with manuscript: $manuscript_path"

    # Prepare environment variables
    local env_args=(
        -e "MANUSCRIPT_PATH=$manuscript_path"
        -e "FORCE_FIGURES=$FORCE_FIGURES"
        -e "TEXMFVAR=/tmp/texmf-var"
        -e "R_LIBS_USER=/home/rxivmaker/.R/library"
    )

    # Add debug environment if enabled
    if [[ "$DEBUG" == true ]]; then
        env_args+=(
            -e "DEBUG=true"
            -e "VERBOSE=true"
        )
    fi

    # Volume mounts
    local volume_args=(
        -v "$PROJECT_ROOT:/workspace"
        -v "rxiv-maker-test-cache:/home/rxivmaker/.cache"
        -v "rxiv-maker-test-r-libs:/home/rxivmaker/.R/library"
    )

    # Run container
    local docker_args=(
        --name "$DOCKER_CONTAINER_NAME"
        --rm
        --platform linux/amd64
        -w /workspace
        "${env_args[@]}"
        "${volume_args[@]}"
    )

    # Add interactive mode if requested
    if [[ "$INTERACTIVE" == true ]]; then
        docker_args+=(-it)
    fi

    # Execute the container
    print_info "Docker command: docker run ${docker_args[*]} $DOCKER_TEST_IMAGE"

    if docker run "${docker_args[@]}" "$DOCKER_TEST_IMAGE" /usr/local/bin/test-script.sh; then
        print_success "Docker test completed successfully!"
        return 0
    else
        local exit_code=$?
        print_error "Docker test failed with exit code: $exit_code"

        if [[ "$INTERACTIVE" == true ]]; then
            print_info "Dropping into interactive shell for debugging..."
            docker run "${docker_args[@]}" -it "$DOCKER_TEST_IMAGE" /bin/bash
        fi

        return $exit_code
    fi
}

# Function to validate results
validate_results() {
    local manuscript_path="$1"
    local expected_pdf="output/${manuscript_path}.pdf"

    print_step "Validating results..."

    # Check if PDF was generated
    if [[ -f "$expected_pdf" ]]; then
        print_success "PDF generated successfully: $expected_pdf"
        print_info "PDF size: $(du -h "$expected_pdf" | cut -f1)"
        print_info "PDF info: $(file "$expected_pdf")"
    else
        print_error "PDF not found at expected location: $expected_pdf"

        # Search for any PDF files
        print_info "Searching for PDF files..."
        find . -name "*.pdf" -type f 2>/dev/null | head -10 | sed 's/^/  /' || print_info "No PDF files found"

        return 1
    fi

    # Check output directory
    if [[ -d "output" ]]; then
        print_info "Output directory contents:"
        ls -la output/ | sed 's/^/  /'
    fi

    return 0
}

# Function to collect debug information
collect_debug_info() {
    print_step "Collecting debug information..."

    echo "=== Docker Environment ==="
    docker --version
    docker info | head -20

    echo "=== System Information ==="
    uname -a
    df -h .

    echo "=== Project Structure ==="
    ls -la

    echo "=== Output Directory ==="
    if [[ -d "output" ]]; then
        find output/ -type f | head -20
    else
        echo "Output directory not found"
    fi

    echo "=== Docker Images ==="
    docker images | grep -E "(rxiv-maker|henriqueslab)"

    echo "=== Docker Containers ==="
    docker ps -a | grep "rxiv-maker"
}

# Main execution
main() {
    print_info "=================================================="
    print_info "🐳 Rxiv-Maker Local Docker Testing"
    print_info "=================================================="

    # Determine manuscript path
    local manuscript_path
    manuscript_path=$(determine_manuscript_path)

    print_info "Configuration:"
    echo "  - Manuscript Path: $manuscript_path"
    echo "  - Base Image: $DOCKER_BASE_IMAGE"
    echo "  - Test Image: $DOCKER_TEST_IMAGE"
    echo "  - Build Base: $BUILD_BASE"
    echo "  - Interactive: $INTERACTIVE"
    echo "  - Debug: $DEBUG"
    echo "  - No Cache: $NO_CACHE"
    echo "  - Force Figures: $FORCE_FIGURES"
    echo "  - Use Compose: $USE_COMPOSE"
    echo ""

    # Cleanup previous runs
    cleanup_resources

    # Setup base image
    setup_base_image

    # Build test image
    build_test_image

    # Run test container
    if run_test_container "$manuscript_path"; then
        # Validate results
        if validate_results "$manuscript_path"; then
            print_success "✅ All tests passed!"
            print_info "Generated PDF: output/${manuscript_path}.pdf"
        else
            print_error "❌ Result validation failed"
            exit 1
        fi
    else
        print_error "❌ Container execution failed"
        if [[ "$DEBUG" == true ]]; then
            collect_debug_info
        fi
        exit 1
    fi

    print_info "=================================================="
    print_success "🎉 Local Docker testing completed successfully!"
    print_info "=================================================="
}

# Trap cleanup on script exit
trap cleanup_resources EXIT

# Run main function
main "$@"
