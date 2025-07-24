#!/bin/bash

# GitHub Actions Auto-Fix Monitor Script
# This script monitors GHA workflows in the main repo and submodules
# and attempts to fix issues automatically using Claude Code

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$SCRIPT_DIR/gha-autofix.log"
LOCK_FILE="/tmp/gha-autofix.lock"
CLAUDE_CMD="claude"

# Claude process timeout (30 minutes = 1800 seconds)
CLAUDE_TIMEOUT=1800

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    cleanup
    exit 1
}

# Cleanup function
cleanup() {
    if [[ -f "$LOCK_FILE" ]]; then
        rm -f "$LOCK_FILE"
    fi
}

# Trap cleanup on exit
trap cleanup EXIT

# Check if script is already running
check_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        local pid
        pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            log "Script is already running (PID: $pid). Exiting."
            exit 0
        else
            log "Removing stale lock file"
            rm -f "$LOCK_FILE"
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

# Check if Claude CLI is available
check_claude() {
    if ! command -v "$CLAUDE_CMD" &> /dev/null; then
        error_exit "Claude CLI not found. Please install it first."
    fi

    # Test Claude CLI with a simple command
    if ! "$CLAUDE_CMD" --help &> /dev/null; then
        error_exit "Claude CLI is not working properly"
    fi

    log "Claude CLI is available and working"
}

# Check GitHub CLI availability
check_github_cli() {
    if ! command -v gh &> /dev/null; then
        error_exit "GitHub CLI (gh) not found. Please install it first."
    fi

    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        error_exit "GitHub CLI is not authenticated. Run 'gh auth login' first."
    fi

    log "GitHub CLI is available and authenticated"
}

# Get current branch
get_current_branch() {
    git rev-parse --abbrev-ref HEAD
}

# Check if there are uncommitted changes
check_git_status() {
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log "WARNING: Repository has uncommitted changes"
        git status --porcelain
        return 1
    fi
    return 0
}





# Send notification (optional)
send_notification() {
    local message="$1"

    # You can customize this to send notifications via:
    # - Slack webhook
    # - Discord webhook
    # - Email
    # - GitHub issue creation
    # - etc.

    log "NOTIFICATION: $message"

    # Example: Create a GitHub issue for critical failures
    # gh issue create --title "GHA Monitor Alert" --body "$message" --label "automation,gha-monitor" || true
}

# Run Claude session for all repositories
run_claude_session() {
    log "Starting Claude auto-fix session"

    # Change to repo root
    cd "$REPO_ROOT"

    # Check git status
    if ! check_git_status; then
        log "Repository has uncommitted changes, skipping this session"
        return 0
    fi

    # Update repository
    log "Updating repository..."
    git fetch origin || log "Failed to fetch from origin"

    # Start Claude with 30-minute timeout for entire session
    log "Starting Claude session with ${CLAUDE_TIMEOUT}s timeout"

    local claude_pid
    (
        cd "$REPO_ROOT"
        exec "$CLAUDE_CMD" resume --dangerously-skip-permission 2>&1 | tee -a "$LOG_FILE"
    ) &
    claude_pid=$!

    log "Started Claude process (PID: $claude_pid)"

    # Wait for timeout period
    local elapsed=0
    while [[ $elapsed -lt $CLAUDE_TIMEOUT ]]; do
        if ! kill -0 "$claude_pid" 2>/dev/null; then
            log "Claude process completed naturally"
            wait "$claude_pid"
            return $?
        fi

        sleep 30
        elapsed=$((elapsed + 30))

        if [[ $((elapsed % 300)) -eq 0 ]]; then  # Log every 5 minutes
            log "Claude session running (${elapsed}s elapsed)"
        fi
    done

    # Timeout reached, kill Claude process
    log "Timeout reached, killing Claude process (PID: $claude_pid)"

    # Try graceful termination first
    if kill -TERM "$claude_pid" 2>/dev/null; then
        sleep 5
        # Force kill if still running
        if kill -0 "$claude_pid" 2>/dev/null; then
            kill -KILL "$claude_pid" 2>/dev/null
        fi
    fi

    log "Claude session terminated after timeout"
    return 0
}

# Main execution
main() {
    log "=== GHA Auto-Fix Monitor Starting ==="

    # Check prerequisites
    check_lock
    check_claude
    check_github_cli

    # Validate we're in the right directory
    if [[ ! -f "$REPO_ROOT/pyproject.toml" ]] || [[ ! -d "$REPO_ROOT/submodules" ]]; then
        error_exit "Script must be run from rxiv-maker repository root or scripts directory"
    fi

    log "Starting continuous Claude auto-fix sessions (${CLAUDE_TIMEOUT}s per session)"

    # Continuous kill-and-restart loop
    local session_count=0
    while true; do
        session_count=$((session_count + 1))
        log "=== Starting Claude session #$session_count ==="

        run_claude_session

        log "Session #$session_count completed, restarting immediately..."
        sleep 5  # Brief pause between sessions
    done
}

# Script usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

GitHub Actions Auto-Fix Monitor Script

OPTIONS:
    --once          Run once and exit (don't loop)
    --help          Show this help message
    --dry-run       Check status only, don't fix issues
    --verbose       Enable verbose logging

ENVIRONMENT VARIABLES:
    CLAUDE_CMD      Claude command (default: claude)
    CLAUDE_TIMEOUT  Claude session timeout in seconds (default: 1800)

EXAMPLES:
    $0              # Run continuous auto-fix sessions
    $0 --once       # Run single Claude session and exit
    $0 --dry-run    # Simulate Claude sessions without actual execution

EOF
}

# Parse command line arguments
DRY_RUN=false
RUN_ONCE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --once)
            RUN_ONCE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            set -x
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Override run_claude_session for dry-run mode
if $DRY_RUN; then
    run_claude_session() {
        log "DRY RUN: Would run Claude auto-fix session"
        sleep 10  # Simulate some processing time
        return 0
    }
fi

# Run once or continuously
if $RUN_ONCE; then
    log "Running single Claude auto-fix session"
    check_lock
    check_claude
    check_github_cli

    # Validate we're in the right directory
    if [[ ! -f "$REPO_ROOT/pyproject.toml" ]] || [[ ! -d "$REPO_ROOT/submodules" ]]; then
        error_exit "Script must be run from rxiv-maker repository root or scripts directory"
    fi

    run_claude_session
    log "Single Claude auto-fix session completed"
else
    main
fi
