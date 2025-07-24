#!/bin/bash

# ======================================================================
# Safe Docker Build Wrapper for Rxiv-Maker
# ======================================================================
# This script provides a safe wrapper around Docker builds to prevent
# system crashes and handle resource constraints gracefully.
#
# Features:
# - Resource monitoring and limits
# - Progress reporting without overwhelming output
# - Graceful handling of build failures
# - Memory management for large builds
# ======================================================================

set -e

# Configuration
MAX_BUILD_TIME="${MAX_BUILD_TIME:-7200}"  # 2 hours maximum (multi-platform builds take longer)
PROGRESS_INTERVAL="${PROGRESS_INTERVAL:-60}" # Report progress every 60 seconds to reduce noise
LOG_FILE="build-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Function to check system resources
check_system_resources() {
    print_info "Checking system resources..."

    # Check available disk space (need at least 5GB)
    AVAILABLE_SPACE=$(df . | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 5242880 ]; then  # 5GB in KB
        print_warning "Low disk space detected. Docker build may fail."
        print_warning "Available: $(($AVAILABLE_SPACE / 1024))MB, Recommended: 5GB+"
    fi

    # Check if Docker daemon is responsive
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running or not accessible"
        exit 1
    fi

    print_success "System resources check passed"
}

# Function to clean up Docker resources before build
cleanup_docker_resources() {
    print_info "Cleaning up Docker resources to free space..."

    # Remove dangling images
    if docker images -f "dangling=true" -q | grep -q .; then
        docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true
        print_info "Removed dangling images"
    fi

    # Clean build cache (keep last 24h)
    docker builder prune -f --filter "until=24h" 2>/dev/null || true
    print_info "Cleaned old build cache"
}

# Function to run build with simplified monitoring
run_build_with_monitoring() {
    local build_cmd="$1"
    local log_file="$2"

    print_info "Starting Docker build..."
    print_info "Build log: $log_file"
    print_info "Maximum build time: $((MAX_BUILD_TIME / 60)) minutes"

    # Use a simpler approach to avoid process management issues
    local start_time=$(date +%s)

    # Execute build with timeout but simpler monitoring
    if timeout "$MAX_BUILD_TIME" bash -c "$build_cmd >> '$log_file' 2>&1"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_success "Build completed successfully in $((duration / 60))m $((duration % 60))s"
        return 0
    else
        local exit_code=$?
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        if [ $exit_code -eq 124 ]; then
            print_error "Build timed out after $((MAX_BUILD_TIME / 60)) minutes"
        else
            print_error "Build failed with exit code: $exit_code after $((duration / 60))m $((duration % 60))s"
        fi

        # Check for common error patterns in log
        if grep -q "No space left on device" "$log_file" 2>/dev/null; then
            print_error "Issue detected: No space left on device"
        elif grep -q "killed" "$log_file" 2>/dev/null; then
            print_error "Issue detected: Process was killed (likely out of memory)"
        fi

        return 1
    fi
}

# Function to show build summary
show_build_summary() {
    local log_file="$1"
    local success="$2"

    if [ "$success" = "true" ]; then
        # Extract build time from log
        if grep -q "Successfully tagged" "$log_file"; then
            print_success "Docker image built successfully!"
        fi

        # Show image size if available
        local image_name=$(grep -o "Successfully tagged .*" "$log_file" | cut -d' ' -f3 | head -1)
        if [ -n "$image_name" ]; then
            print_info "Image size:"
            docker images "$image_name" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 2>/dev/null || true
        fi
    else
        print_error "Build failed. Last 20 lines of build log:"
        echo "----------------------------------------"
        tail -20 "$log_file" 2>/dev/null || echo "No log available"
        echo "----------------------------------------"
        print_info "Full log available at: $log_file"
    fi
}

# Main execution
main() {
    print_info "Starting safe Docker build process..."

    # Check prerequisites
    check_system_resources
    cleanup_docker_resources

    # Build the actual build command
    BUILD_CMD="./build.sh $*"

    print_info "Build command: $BUILD_CMD"
    print_info "Working directory: $(pwd)"

    # Execute build with monitoring
    if run_build_with_monitoring "$BUILD_CMD" "$LOG_FILE"; then
        show_build_summary "$LOG_FILE" "true"
        print_success "Safe build process completed successfully!"

        # Clean up log file on success (optional)
        if [ "${KEEP_LOGS:-false}" != "true" ]; then
            rm -f "$LOG_FILE"
        fi

        exit 0
    else
        show_build_summary "$LOG_FILE" "false"
        print_error "Safe build process failed!"
        exit 1
    fi
}

# Show help if requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Safe Docker Build Wrapper for Rxiv-Maker"
    echo ""
    echo "Usage: $0 [build.sh options]"
    echo ""
    echo "Environment variables:"
    echo "  MAX_BUILD_TIME   - Maximum build time in seconds (default: 7200)"
    echo "  PROGRESS_INTERVAL - Progress report interval in seconds (default: 30)"
    echo "  KEEP_LOGS        - Keep log files on success (default: false)"
    echo ""
    echo "Examples:"
    echo "  $0 --local --tag test"
    echo "  $0 --tag latest --repo myuser/repo"
    echo "  MAX_BUILD_TIME=3600 $0 --local"
    echo ""
    exit 0
fi

# Run main function with all arguments
main "$@"
