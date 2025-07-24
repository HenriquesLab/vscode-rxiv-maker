#!/bin/bash

# CI Monitoring Script for homebrew-rxiv-maker
# Monitors GitHub Actions workflow runs and provides real-time status updates

set -euo pipefail

# Configuration
REPO_NAME="homebrew-rxiv-maker"
WORKFLOW_NAME="Test Homebrew Installation"
REFRESH_INTERVAL=30  # seconds
MAX_RUNTIME=3600     # 1 hour in seconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to format duration
format_duration() {
    local seconds=$1
    local hours=$((seconds / 3600))
    local minutes=$(((seconds % 3600) / 60))
    local secs=$((seconds % 60))

    if [ $hours -gt 0 ]; then
        printf "%dh %02dm %02ds" $hours $minutes $secs
    elif [ $minutes -gt 0 ]; then
        printf "%dm %02ds" $minutes $secs
    else
        printf "%ds" $secs
    fi
}

# Function to calculate runtime from start time
calculate_runtime() {
    local start_time=$1
    local current_time=$(date +%s)
    local start_timestamp=$(date -d "$start_time" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$start_time" +%s 2>/dev/null)
    echo $((current_time - start_timestamp))
}

# Function to get workflow runs
get_workflow_runs() {
    gh run list --limit 10 --json status,conclusion,startedAt,displayTitle,workflowName,databaseId,url 2>/dev/null || {
        print_status $RED "Error: Failed to fetch workflow runs. Make sure you're authenticated with 'gh auth login'"
        exit 1
    }
}

# Function to get job details for a specific run
get_job_details() {
    local run_id=$1
    gh run view "$run_id" --json jobs 2>/dev/null | jq -r '.jobs[] | "\(.name):\(.status):\(.conclusion // "N/A")"' 2>/dev/null || echo "Unable to fetch job details"
}

# Function to cancel hanging jobs
cancel_hanging_jobs() {
    local run_id=$1
    local runtime=$2

    if [ $runtime -gt $MAX_RUNTIME ]; then
        print_status $YELLOW "Job $run_id has been running for $(format_duration $runtime) (> 1 hour)"
        read -p "Cancel this job? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            gh run cancel "$run_id"
            print_status $YELLOW "✓ Cancelled job $run_id"
        fi
    fi
}

# Function to display run status
display_run_status() {
    local run_data=$1
    local status=$(echo "$run_data" | jq -r '.status')
    local conclusion=$(echo "$run_data" | jq -r '.conclusion // "N/A"')
    local title=$(echo "$run_data" | jq -r '.displayTitle')
    local workflow=$(echo "$run_data" | jq -r '.workflowName')
    local run_id=$(echo "$run_data" | jq -r '.databaseId')
    local url=$(echo "$run_data" | jq -r '.url')
    local start_time=$(echo "$run_data" | jq -r '.startedAt')

    # Calculate runtime
    local runtime=0
    if [ "$start_time" != "null" ]; then
        runtime=$(calculate_runtime "$start_time")
    fi

    # Status indicator
    case "$status" in
        "in_progress")
            if [ $runtime -gt $MAX_RUNTIME ]; then
                print_status $RED "🔴 HANGING"
            else
                print_status $BLUE "🔵 RUNNING"
            fi
            ;;
        "completed")
            case "$conclusion" in
                "success") print_status $GREEN "✅ SUCCESS" ;;
                "failure") print_status $RED "❌ FAILED" ;;
                "cancelled") print_status $YELLOW "⚠️  CANCELLED" ;;
                *) print_status $YELLOW "⚪ $conclusion" ;;
            esac
            ;;
        "queued") print_status $YELLOW "⏳ QUEUED" ;;
        *) print_status $YELLOW "⚪ $status" ;;
    esac

    # Run details
    echo "   ID: $run_id"
    echo "   Title: $title"
    echo "   Runtime: $(format_duration $runtime)"
    echo "   URL: $url"

    # Job details for running jobs
    if [ "$status" = "in_progress" ]; then
        echo "   Jobs:"
        get_job_details "$run_id" | while IFS=':' read -r job_name job_status job_conclusion; do
            case "$job_status" in
                "in_progress") echo "     🔵 $job_name (running)" ;;
                "completed")
                    case "$job_conclusion" in
                        "success") echo "     ✅ $job_name" ;;
                        "failure") echo "     ❌ $job_name" ;;
                        *) echo "     ⚪ $job_name ($job_conclusion)" ;;
                    esac
                    ;;
                "queued") echo "     ⏳ $job_name (queued)" ;;
                *) echo "     ⚪ $job_name ($job_status)" ;;
            esac
        done

        # Check if job should be cancelled
        if [ "$1" = "--interactive" ]; then
            cancel_hanging_jobs "$run_id" "$runtime"
        fi
    fi

    echo
}

# Function to show summary
show_summary() {
    local runs_data=$1
    local total_runs=$(echo "$runs_data" | jq length)
    local running_runs=$(echo "$runs_data" | jq '[.[] | select(.status == "in_progress")] | length')
    local queued_runs=$(echo "$runs_data" | jq '[.[] | select(.status == "queued")] | length')
    local success_runs=$(echo "$runs_data" | jq '[.[] | select(.status == "completed" and .conclusion == "success")] | length')
    local failed_runs=$(echo "$runs_data" | jq '[.[] | select(.status == "completed" and .conclusion == "failure")] | length')

    echo "════════════════════════════════════════════════════════════════"
    echo "CI MONITORING SUMMARY - $(date)"
    echo "════════════════════════════════════════════════════════════════"
    echo "🔵 Running: $running_runs  |  ⏳ Queued: $queued_runs  |  ✅ Success: $success_runs  |  ❌ Failed: $failed_runs"
    echo "Total runs shown: $total_runs"
    echo "════════════════════════════════════════════════════════════════"
    echo
}

# Function to monitor continuously
monitor_continuous() {
    local interactive_mode=$1

    while true; do
        clear
        local runs_data=$(get_workflow_runs)

        show_summary "$runs_data"

        echo "$runs_data" | jq -c '.[]' | while read -r run; do
            display_run_status "$run" "$interactive_mode"
        done

        if [ "$interactive_mode" = "--interactive" ]; then
            echo "Press Ctrl+C to exit, or wait ${REFRESH_INTERVAL}s for refresh..."
        else
            echo "Refreshing in ${REFRESH_INTERVAL}s... (Press Ctrl+C to exit)"
        fi

        sleep $REFRESH_INTERVAL
    done
}

# Function to show help
show_help() {
    echo "CI Monitoring Script for $REPO_NAME"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "OPTIONS:"
    echo "  --watch, -w       Monitor continuously (default)"
    echo "  --once, -o        Show status once and exit"
    echo "  --interactive, -i Monitor with interactive options (cancel hanging jobs)"
    echo "  --cancel-hanging  Cancel jobs running longer than 1 hour"
    echo "  --help, -h        Show this help message"
    echo
    echo "Examples:"
    echo "  $0                    # Monitor continuously"
    echo "  $0 --once            # Show current status"
    echo "  $0 --interactive     # Monitor with interactive options"
    echo "  $0 --cancel-hanging  # Cancel hanging jobs"
}

# Function to cancel hanging jobs
cancel_hanging_jobs_batch() {
    local runs_data=$(get_workflow_runs)

    echo "$runs_data" | jq -c '.[] | select(.status == "in_progress")' | while read -r run; do
        local run_id=$(echo "$run" | jq -r '.databaseId')
        local start_time=$(echo "$run" | jq -r '.startedAt')
        local title=$(echo "$run" | jq -r '.displayTitle')

        if [ "$start_time" != "null" ]; then
            local runtime=$(calculate_runtime "$start_time")

            if [ $runtime -gt $MAX_RUNTIME ]; then
                print_status $YELLOW "Cancelling hanging job: $title (ID: $run_id, Runtime: $(format_duration $runtime))"
                gh run cancel "$run_id"
                print_status $GREEN "✓ Cancelled job $run_id"
            fi
        fi
    done
}

# Main script logic
main() {
    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        print_status $RED "Error: GitHub CLI (gh) is not installed. Please install it first."
        exit 1
    fi

    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        print_status $RED "Error: jq is not installed. Please install it first."
        exit 1
    fi

    # Parse command line arguments
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --once|-o)
            local runs_data=$(get_workflow_runs)
            show_summary "$runs_data"
            echo "$runs_data" | jq -c '.[]' | while read -r run; do
                display_run_status "$run"
            done
            exit 0
            ;;
        --interactive|-i)
            monitor_continuous "--interactive"
            ;;
        --cancel-hanging)
            cancel_hanging_jobs_batch
            exit 0
            ;;
        --watch|-w|"")
            monitor_continuous ""
            ;;
        *)
            print_status $RED "Error: Unknown option '$1'"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
