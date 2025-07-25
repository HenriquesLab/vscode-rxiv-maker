#!/bin/bash

# pull-gha-logs.sh - GitHub Actions Log Puller for rxiv-maker and submodules
# Pulls the latest GitHub Actions logs for the main repository and all submodules

set -eo pipefail

# Check if we're running in bash
if [ -z "${BASH_VERSION:-}" ]; then
    echo "Error: This script requires bash" >&2
    exit 1
fi

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly GITHUB_API_BASE="https://api.github.com"
readonly LOG_DIR="$PROJECT_ROOT/gha-logs"

# Repository configurations
REPO_CONFIGS=(
    "main:HenriquesLab/rxiv-maker:main"
    "homebrew:HenriquesLab/homebrew-rxiv-maker:main"
    "scoop:HenriquesLab/scoop-rxiv-maker:main"
    "vscode:HenriquesLab/vscode-rxiv-maker:main"
)

# GitHub API token (optional, for higher rate limits)
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# Default values
DEFAULT_LIMIT=5
DEFAULT_STATUS="all"
VERBOSE=false
DOWNLOAD_ARTIFACTS=false
CLEAN_OLD=false

# Function to print colored output
print_status() {
    local status="$1"
    local message="$2"
    local color=""

    case "$status" in
        "SUCCESS"|"PASS") color="$GREEN" ;;
        "FAILURE"|"FAIL") color="$RED" ;;
        "PENDING"|"RUNNING") color="$YELLOW" ;;
        "INFO") color="$BLUE" ;;
        "DEBUG") color="$CYAN" ;;
        *) color="$NC" ;;
    esac

    echo -e "${color}[$status]${NC} $message"
}

# Function to make GitHub API request
github_api_request() {
    local endpoint="$1"
    local headers=()

    if [[ -n "$GITHUB_TOKEN" ]]; then
        headers=("-H" "Authorization: token $GITHUB_TOKEN")
        headers+=("-H" "Accept: application/vnd.github.v3+json")
    fi

    if [[ "$VERBOSE" == true ]]; then
        print_status "DEBUG" "API Request: $GITHUB_API_BASE/$endpoint"
    fi

    curl -s "${headers[@]}" "$GITHUB_API_BASE/$endpoint" 2>/dev/null || echo "{}"
}

# Function to download log file
download_log() {
    local log_url="$1"
    local output_file="$2"
    local headers=()

    if [[ -n "$GITHUB_TOKEN" ]]; then
        headers=("-H" "Authorization: token $GITHUB_TOKEN")
    fi

    if curl -s -L "${headers[@]}" "$log_url" -o "$output_file" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to get workflow runs and download logs
get_repo_logs() {
    local repo_key="$1"
    local repo_name="$2"
    local branch="$3"
    local limit="${4:-$DEFAULT_LIMIT}"
    local status_filter="${5:-$DEFAULT_STATUS}"

    print_status "INFO" "Processing $repo_key: $repo_name (branch: $branch)"

    # Create repo-specific log directory
    local repo_log_dir="$LOG_DIR/$repo_key"
    mkdir -p "$repo_log_dir"

    # Get workflow runs
    local api_endpoint="repos/$repo_name/actions/runs?branch=$branch&per_page=$limit"
    if [[ "$status_filter" != "all" ]]; then
        api_endpoint="${api_endpoint}&status=$status_filter"
    fi

    local workflow_runs
    workflow_runs=$(github_api_request "$api_endpoint")

    # Debug: Show what we received
    echo "DEBUG: Received data: '$workflow_runs'" >&2
    echo "DEBUG: Data length: ${#workflow_runs}" >&2

    if [[ "$workflow_runs" == "{}" ]]; then
        print_status "FAIL" "Failed to fetch workflow runs for $repo_name"
        return 1
    fi

    # Parse and process workflow runs
    echo "$workflow_runs" | python3 -c "
import json
import sys
import os

try:
    data = json.load(sys.stdin)
    runs = data.get('workflow_runs', [])

    if not runs:
        print('No workflow runs found')
        sys.exit(0)

    print(f'Found {len(runs)} workflow runs')

    for i, run in enumerate(runs):
        run_id = run['id']
        workflow_name = run['name']
        status = run['status']
        conclusion = run.get('conclusion', 'N/A')
        run_number = run['run_number']
        created_at = run['created_at']

        print(f'{run_id}|{workflow_name}|{status}|{conclusion}|{run_number}|{created_at}')

except Exception as e:
    print(f'Error parsing workflow data: {e}', file=sys.stderr)
    sys.exit(1)
" | while IFS='|' read -r run_id workflow_name status conclusion run_number created_at; do
        if [[ -z "$run_id" ]]; then
            continue
        fi

        local safe_workflow_name=$(echo "$workflow_name" | tr ' /' '_-' | tr -d '()[]{}')
        local timestamp=$(echo "$created_at" | cut -d'T' -f1)
        local log_filename="${timestamp}_${safe_workflow_name}_${run_number}_${status}"

        if [[ "$conclusion" != "N/A" && "$conclusion" != "null" ]]; then
            log_filename="${log_filename}_${conclusion}"
        fi

        log_filename="${log_filename}.log"
        local output_path="$repo_log_dir/$log_filename"

        print_status "INFO" "  Run #$run_number: $workflow_name ($status/$conclusion)"

        # Get logs download URL
        local logs_url
        logs_url=$(github_api_request "repos/$repo_name/actions/runs/$run_id/logs" | head -c 0 && echo "repos/$repo_name/actions/runs/$run_id/logs")

        if [[ "$VERBOSE" == true ]]; then
            print_status "DEBUG" "    Downloading logs to: $output_path"
        fi

        # Download logs
        if download_log "$GITHUB_API_BASE/$logs_url" "$output_path.zip"; then
            # Extract if it's a zip file
            if file "$output_path.zip" | grep -q "Zip archive"; then
                if command -v unzip >/dev/null 2>&1; then
                    local extract_dir="$repo_log_dir/${log_filename%.log}"
                    mkdir -p "$extract_dir"
                    if unzip -q "$output_path.zip" -d "$extract_dir" 2>/dev/null; then
                        rm "$output_path.zip"
                        print_status "SUCCESS" "    Downloaded and extracted: $log_filename"
                    else
                        mv "$output_path.zip" "$output_path"
                        print_status "SUCCESS" "    Downloaded (zip): $log_filename"
                    fi
                else
                    mv "$output_path.zip" "$output_path"
                    print_status "SUCCESS" "    Downloaded (zip): $log_filename"
                fi
            else
                mv "$output_path.zip" "$output_path"
                print_status "SUCCESS" "    Downloaded: $log_filename"
            fi
        else
            print_status "FAIL" "    Failed to download logs for run #$run_number"
            rm -f "$output_path.zip"
        fi

        # Download artifacts if requested
        if [[ "$DOWNLOAD_ARTIFACTS" == true ]]; then
            local artifacts_data
            artifacts_data=$(github_api_request "repos/$repo_name/actions/runs/$run_id/artifacts")

            local artifact_count
            artifact_count=$(echo "$artifacts_data" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    print(len(data.get('artifacts', [])))
except:
    print(0)
" 2>/dev/null)

            if [[ "$artifact_count" -gt 0 ]]; then
                print_status "INFO" "    Found $artifact_count artifacts"
                # Note: Artifact download requires additional API calls and authentication
                # This is a placeholder for artifact download functionality
            fi
        fi
    done

    print_status "SUCCESS" "Completed processing $repo_key"
    echo
}

# Function to clean old logs
clean_old_logs() {
    if [[ -d "$LOG_DIR" ]]; then
        print_status "INFO" "Cleaning old logs from $LOG_DIR"
        find "$LOG_DIR" -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
        find "$LOG_DIR" -type d -empty -delete 2>/dev/null || true
        print_status "SUCCESS" "Cleaned old logs (older than 7 days)"
    fi
}

# Function to show help
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Pull GitHub Actions logs for rxiv-maker and its submodules.

OPTIONS:
    -h, --help              Show this help message
    -t, --token TOKEN       GitHub API token (or set GITHUB_TOKEN env var)
    -l, --limit NUMBER      Limit number of workflow runs per repo (default: $DEFAULT_LIMIT)
    -s, --status STATUS     Filter by status: all, completed, in_progress, queued (default: $DEFAULT_STATUS)
    -r, --repo REPO         Pull logs for specific repo only (main|docker|homebrew|scoop|vscode)
    -v, --verbose           Verbose output
    -a, --artifacts         Download artifacts (requires authentication)
    -c, --clean             Clean old logs before downloading new ones
    --clean-only            Only clean old logs, don't download new ones

EXAMPLES:
    $0                                      # Pull logs for all repositories
    $0 -l 10 -s completed                  # Pull 10 completed runs for all repos
    $0 -r main -v                          # Pull logs for main repo only with verbose output
    $0 -t ghp_xxxx -a                      # Use specific token and download artifacts
    $0 --clean-only                        # Clean old logs only

ENVIRONMENT:
    GITHUB_TOKEN           GitHub API token for higher rate limits and private repos

OUTPUT:
    Logs are saved to: $LOG_DIR/
    ├── main/              # Main repository logs
    ├── docker/            # Docker submodule logs
    ├── homebrew/          # Homebrew submodule logs
    ├── scoop/             # Scoop submodule logs
    └── vscode/            # VS Code extension logs

EOF
}

# Parse command line arguments
LIMIT="$DEFAULT_LIMIT"
STATUS_FILTER="$DEFAULT_STATUS"
REPO_FILTER=""
CLEAN_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--token)
            GITHUB_TOKEN="$2"
            shift 2
            ;;
        -l|--limit)
            LIMIT="$2"
            shift 2
            ;;
        -s|--status)
            STATUS_FILTER="$2"
            shift 2
            ;;
        -r|--repo)
            REPO_FILTER="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -a|--artifacts)
            DOWNLOAD_ARTIFACTS=true
            shift
            ;;
        -c|--clean)
            CLEAN_OLD=true
            shift
            ;;
        --clean-only)
            CLEAN_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            show_help
            exit 1
            ;;
    esac
done

# Validate arguments
if ! [[ "$LIMIT" =~ ^[0-9]+$ ]] || [[ "$LIMIT" -lt 1 ]]; then
    echo "Error: Limit must be a positive integer" >&2
    exit 1
fi

if [[ "$STATUS_FILTER" != "all" && "$STATUS_FILTER" != "completed" && "$STATUS_FILTER" != "in_progress" && "$STATUS_FILTER" != "queued" ]]; then
    echo "Error: Status must be one of: all, completed, in_progress, queued" >&2
    exit 1
fi

if [[ -n "$REPO_FILTER" ]]; then
    # Validate repo filter
    valid_repos=("main" "docker" "homebrew" "scoop" "vscode")
    if [[ ! " ${valid_repos[@]} " =~ " ${REPO_FILTER} " ]]; then
        echo "Error: Repository must be one of: ${valid_repos[*]}" >&2
        exit 1
    fi
fi

# Main execution
main() {
    print_status "INFO" "Starting GitHub Actions log pull for rxiv-maker"
    echo "Configuration:"
    echo "  Log directory: $LOG_DIR"
    echo "  Limit per repo: $LIMIT"
    echo "  Status filter: $STATUS_FILTER"
    echo "  Repository filter: ${REPO_FILTER:-all}"
    echo "  Verbose: $VERBOSE"
    echo "  Download artifacts: $DOWNLOAD_ARTIFACTS"
    echo "  GitHub token: ${GITHUB_TOKEN:+set}"
    echo

    # Clean old logs if requested
    if [[ "$CLEAN_OLD" == true || "$CLEAN_ONLY" == true ]]; then
        clean_old_logs
        if [[ "$CLEAN_ONLY" == true ]]; then
            print_status "SUCCESS" "Clean-only operation completed"
            exit 0
        fi
    fi

    # Create log directory
    mkdir -p "$LOG_DIR"

    # Process repositories
    local processed_count=0
    local failed_count=0

    for config in "${REPO_CONFIGS[@]}"; do
        IFS=':' read -r repo_key repo_name branch <<< "$config"

        # Skip if repo filter is set and doesn't match
        if [[ -n "$REPO_FILTER" && "$repo_key" != "$REPO_FILTER" ]]; then
            continue
        fi

        if get_repo_logs "$repo_key" "$repo_name" "$branch" "$LIMIT" "$STATUS_FILTER"; then
            ((processed_count++))
        else
            ((failed_count++))
        fi
    done

    # Summary
    echo "=========================================="
    print_status "INFO" "Pull operation completed"
    echo "  Repositories processed: $processed_count"
    echo "  Repositories failed: $failed_count"
    echo "  Logs saved to: $LOG_DIR"

    if [[ -d "$LOG_DIR" ]]; then
        local total_files
        total_files=$(find "$LOG_DIR" -type f -name "*.log" | wc -l)
        echo "  Total log files: $total_files"
    fi

    if [[ "$failed_count" -gt 0 ]]; then
        print_status "FAIL" "Some repositories failed to process"
        exit 1
    else
        print_status "SUCCESS" "All repositories processed successfully"
    fi
}

# Run main function
main "$@"
