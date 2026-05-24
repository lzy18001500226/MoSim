#!/bin/bash

# Codex Loopback Wrapper
# Manages the iterative loopback process for Codex CLI
#
# This script coordinates multiple Codex CLI invocations,
# checking for completion conditions between iterations.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGER_SCRIPT="${SCRIPT_DIR}/loopback-manager.py"
EXTRACTOR_SCRIPT="${SCRIPT_DIR}/extract_codex_json.py"
STATE_FILE=".codex/loopback.local.md"
PYTHON_BIN="${LOOPBACK_PYTHON:-python3}"
REUSE_SESSION_DEFAULT="${CODEX_LOOPBACK_REUSE_SESSION:-1}"

# Colors for output (if terminal supports it)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if state file exists
check_state() {
    if [[ ! -f "${STATE_FILE}" ]]; then
        echo -e "${RED}Error: No active Loopback found.${NC}"
        echo "Start a new loopback with: /loopback <prompt>"
        exit 1
    fi
}

json_get() {
    local key="$1"
    "${PYTHON_BIN}" -c '
import json, sys
key = sys.argv[1]
raw = sys.stdin.read()
try:
    data = json.loads(raw) if raw.strip() else {}
except Exception:
    data = {}
val = data
for part in key.split("."):
    if isinstance(val, dict):
        val = val.get(part)
    else:
        val = None
        break
if val is None:
    sys.stdout.write("")
elif isinstance(val, bool):
    sys.stdout.write("true" if val else "false")
else:
    sys.stdout.write(str(val))
' "$key"
}

read_info_json() {
    "${PYTHON_BIN}" "${MANAGER_SCRIPT}" info --json 2>/dev/null || true
}

read_prompt() {
    local info_json="$1"
    printf "%s" "${info_json}" | json_get "prompt"
}

read_iteration() {
    local info_json="$1"
    printf "%s" "${info_json}" | json_get "iteration"
}

read_max_iterations() {
    local info_json="$1"
    printf "%s" "${info_json}" | json_get "max_iterations"
}

read_completion_promise() {
    local info_json="$1"
    printf "%s" "${info_json}" | json_get "completion_promise"
}

read_session_id() {
    local info_json="$1"
    printf "%s" "${info_json}" | json_get "session_id"
}

read_reuse_session() {
    local info_json="$1"
    printf "%s" "${info_json}" | json_get "reuse_session"
}

read_stop_flag() {
    local info_json="$1"
    printf "%s" "${info_json}" | json_get "stop"
}

read_stop_reason() {
    local info_json="$1"
    printf "%s" "${info_json}" | json_get "reason"
}

# Run a single iteration of the loopback
run_iteration() {
    local info_json iteration max_iterations completion_promise prompt session_id reuse_session
    info_json="$(read_info_json)"
    iteration="$(read_iteration "${info_json}")"
    max_iterations="$(read_max_iterations "${info_json}")"
    completion_promise="$(read_completion_promise "${info_json}")"
    session_id="$(read_session_id "${info_json}")"
    reuse_session="$(read_reuse_session "${info_json}")"
    prompt="$(read_prompt "${info_json}")"

    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Loopback Status:${NC}"
    echo "Active: true"
    if [[ -n "${max_iterations}" ]] && [[ "${max_iterations}" != "0" ]]; then
        echo "Iteration: ${iteration}/${max_iterations}"
    else
        echo "Iteration: ${iteration} (unlimited)"
    fi
    if [[ -n "${completion_promise}" ]] && [[ "${completion_promise}" != "null" ]]; then
        echo "Completion Promise: ${completion_promise}"
    else
        echo "Completion Promise: none"
    fi
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    if [[ -z "$prompt" ]]; then
        echo -e "${RED}Error: Could not retrieve prompt from state file.${NC}"
        exit 1
    fi

    echo -e "${GREEN}Running Codex with prompt:${NC}"
    echo "  $prompt"
    echo ""

    mkdir -p .codex/loopback.outputs
    local out_file=".codex/loopback.outputs/iteration-${iteration}.log"
    local extra_args=()
    if [[ -n "${CODEX_LOOPBACK_CODEX_ARGS:-}" ]]; then
        # shellcheck disable=SC2206
        extra_args=(${CODEX_LOOPBACK_CODEX_ARGS})
    fi

    # IMPORTANT: macOS ships bash 3.2, and with `set -u` an empty array expansion like
    # "${extra_args[@]}" can throw "unbound variable". Always gate expansions by length.
    local extra_args_len
    extra_args_len="${#extra_args[@]}"

    # Codex CLI refuses to run outside a git repo unless `--skip-git-repo-check` is set.
    # Make Loopback usable from directories like ~/Documents/GitHub (a folder-of-repos).
    local need_skip_git_repo_check=0
    if [[ "${extra_args_len}" -gt 0 ]]; then
        for a in "${extra_args[@]}"; do
            if [[ "${a}" == "--skip-git-repo-check" ]]; then
                need_skip_git_repo_check=0
                break
            fi
            need_skip_git_repo_check=1
        done
    else
        need_skip_git_repo_check=1
    fi
    if [[ "${need_skip_git_repo_check}" == "1" ]]; then
        if command -v git >/dev/null 2>&1; then
            if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
                need_skip_git_repo_check=0
            fi
        fi
    fi
    local skip_git_repo_arg=""
    if [[ "${need_skip_git_repo_check}" == "1" ]]; then
        skip_git_repo_arg="--skip-git-repo-check"
    fi

    local reuse_flag="${REUSE_SESSION_DEFAULT}"
    if [[ -n "${reuse_session}" ]]; then
        # reuse_session may be "true"/"false" or empty
        if [[ "${reuse_session}" == "false" ]]; then
            reuse_flag=0
        else
            reuse_flag=1
        fi
    fi

    # Run Codex with the prompt
    if command -v codex &> /dev/null; then
        # Prefer non-interactive execution so the wrapper can capture output and detect promises.
        #
        # You can pass extra flags via CODEX_LOOPBACK_CODEX_ARGS, e.g.:
        #   export CODEX_LOOPBACK_CODEX_ARGS="--full-auto"
        #
        # If you want maximum automation (DANGEROUS), you could use:
        #   export CODEX_LOOPBACK_CODEX_ARGS="--dangerously-bypass-approvals-and-sandbox"
        #
        # Ralph-loop-like behavior: reuse the SAME Codex session across iterations.
        # - First run uses `codex exec` (creates a new session)
        # - Subsequent runs use `codex exec resume <session_id>`
        if [[ "${reuse_flag}" == "1" ]]; then
            local thread_id_file=".codex/loopback.outputs/iteration-${iteration}.thread_id"
            local json_file=".codex/loopback.outputs/iteration-${iteration}.jsonl"
            local codex_cmd=()

            if [[ -z "${session_id}" ]]; then
                : > "${thread_id_file}"
                codex_cmd=(codex exec --json)
                if [[ -n "${skip_git_repo_arg}" ]]; then
                    codex_cmd+=("${skip_git_repo_arg}")
                fi
                if [[ "${extra_args_len}" -gt 0 ]]; then
                    codex_cmd+=("${extra_args[@]}")
                fi
                codex_cmd+=(-)

                printf "%s" "$prompt" | "${codex_cmd[@]}" 2>&1 \
                    | tee "${json_file}" \
                    | "${PYTHON_BIN}" "${EXTRACTOR_SCRIPT}" --thread-id-file "${thread_id_file}" \
                    | tee "${out_file}"

                local derived_id
                derived_id="$(cat "${thread_id_file}" 2>/dev/null || true)"
                if [[ -n "${derived_id}" ]]; then
                    "${PYTHON_BIN}" "${MANAGER_SCRIPT}" set-session --session-id "${derived_id}" --reuse-session true >/dev/null 2>&1 || true
                    session_id="${derived_id}"
                fi
            else
                : > "${thread_id_file}"
                codex_cmd=(codex exec resume --json)
                if [[ -n "${skip_git_repo_arg}" ]]; then
                    codex_cmd+=("${skip_git_repo_arg}")
                fi
                if [[ "${extra_args_len}" -gt 0 ]]; then
                    codex_cmd+=("${extra_args[@]}")
                fi
                codex_cmd+=("${session_id}" -)

                printf "%s" "$prompt" | "${codex_cmd[@]}" 2>&1 \
                    | tee "${json_file}" \
                    | "${PYTHON_BIN}" "${EXTRACTOR_SCRIPT}" --thread-id-file "${thread_id_file}" \
                    | tee "${out_file}"
            fi
        else
            local codex_cmd=(codex exec)
            if [[ -n "${skip_git_repo_arg}" ]]; then
                codex_cmd+=("${skip_git_repo_arg}")
            fi
            if [[ "${extra_args_len}" -gt 0 ]]; then
                codex_cmd+=("${extra_args[@]}")
            fi
            codex_cmd+=(-)
            printf "%s" "$prompt" | "${codex_cmd[@]}" 2>&1 | tee "${out_file}"
        fi
    else
        echo -e "${YELLOW}Warning: 'codex' command not found in PATH.${NC}"
        echo "Please ensure Codex CLI is installed and available."
        echo ""
        echo "Simulating Codex execution with prompt:"
        echo "  $prompt" | tee "${out_file}"
    fi

    # After Codex completes, check if we should continue
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo "Codex execution completed."
    echo ""

    "${PYTHON_BIN}" "${MANAGER_SCRIPT}" advance --output-file "${out_file}" >/dev/null 2>&1 || true
}

# Check if the loop should continue
check_should_continue() {
    if [[ ! -f "${STATE_FILE}" ]]; then
        echo -e "${YELLOW}Loopback state file removed. Assuming cancelled.${NC}"
        return 1
    fi

    local info_json stop_flag reason
    info_json="$(read_info_json)"
    stop_flag="$(read_stop_flag "${info_json}")"
    reason="$(read_stop_reason "${info_json}")"

    if [[ "${stop_flag}" == "true" ]]; then
        echo -e "${GREEN}Loopback stopping: ${reason:-done}${NC}"
        return 1
    fi

    return 0
}

# Main loop
main() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Loopback - Iterative Development Loop for Codex${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    check_state

    if ! "${PYTHON_BIN}" -c "import yaml" >/dev/null 2>&1; then
        echo -e "${RED}Error: Python cannot import 'yaml' (PyYAML).${NC}"
        echo "Loopback requires PyYAML for parsing the state file."
        echo ""
        echo "Fix options:"
        echo "  1) Install PyYAML into your python:  pip3 install pyyaml"
        echo "  2) Point LOOPBACK_PYTHON to a python that has PyYAML:"
        echo "     export LOOPBACK_PYTHON=/path/to/python3"
        exit 1
    fi

    # Check if we should continue from current state
    if ! check_should_continue; then
        echo ""
        echo -e "${GREEN}Loopback has already completed.${NC}"
        echo "Start a new loopback with: /loopback <prompt>"
        exit 0
    fi

    # Main iteration loop
    while true; do
        run_iteration

        if ! check_should_continue; then
            break
        fi

        echo ""
        echo -e "${YELLOW}Continuing to next iteration...${NC}"
        echo ""
        sleep 1
    done

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Loopback completed!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    # Show final status
    "${PYTHON_BIN}" "${MANAGER_SCRIPT}" status 2>/dev/null || true
}

# Handle interrupts
trap 'echo; echo -e "${RED}Loopback interrupted by user.${NC}"; exit 130' INT

main "$@"
