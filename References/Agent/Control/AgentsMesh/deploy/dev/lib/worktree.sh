# shellcheck shell=bash
# worktree.sh — git-worktree-aware naming + per-worktree port allocation.
#
# Worktrees share .env / docker-compose project namespace by name. Different
# worktrees get a deterministic port offset so they don't collide.
# `_runtime_dir` is the per-worktree mutable state root (pids, logs, certs);
# gitignored, lives next to dev.sh.

# Worktree name → docker-compose project name suffix.
# In a worktree the git-dir is `.git/worktrees/<name>`; in the main checkout
# it's plain `.git`, so we fall back to the current branch.
#
# `AGENTSMESH_WORKTREE_NAME` env override takes precedence. Required by CI
# shards: detached-HEAD checkouts (PR + push events) resolve to the literal
# string "HEAD" → slug "head", so every PR / every shard collapses onto the
# same compose project name and the same backend / DB / runner container.
# Two shards on the same self-hosted host then end up sharing the dev-org
# pod table — a `terminateAllPods()` cleanup hook in one shard wipes the
# in-flight pod of the other. The override is opt-in; local devs and the
# main worktree continue to use the git-derived name.
get_worktree_name() {
    if [[ -n "${AGENTSMESH_WORKTREE_NAME:-}" ]]; then
        echo "$AGENTSMESH_WORKTREE_NAME" | sed 's/[^a-zA-Z0-9-]/-/g' | tr '[:upper:]' '[:lower:]'
        return
    fi

    local git_dir
    git_dir=$(git rev-parse --git-dir 2>/dev/null)

    if [[ "$git_dir" == *".git/worktrees/"* ]]; then
        basename "$git_dir"
    else
        git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main"
    fi | sed 's/[^a-zA-Z0-9-]/-/g' | tr '[:upper:]' '[:lower:]'
}

# Port offset from worktree name. main/master always 0; everything else maps
# into [1, 500] via 6 hex chars of md5. 50-step window per offset → 25,000
# port range covered (10000-35000), 500 worktrees max before collision.
calculate_port_offset() {
    local name="$1"
    if [[ "$name" == "main" || "$name" == "master" ]]; then
        echo 0
    else
        local hash
        if command -v md5sum &>/dev/null; then
            hash=$(echo -n "$name" | md5sum | cut -c1-6)
        else
            hash=$(echo -n "$name" | md5 | cut -c1-6)
        fi
        echo $(( (16#$hash % 500) + 1 ))
    fi
}

# Mutable runtime state root: host service pids/logs, runner cert, isolated
# HOME for the runner container's CLI configs. Gitignored.
_runtime_dir() { echo "$SCRIPT_DIR/runtime"; }
