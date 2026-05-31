# shellcheck shell=bash
# doctor.sh — fail-fast prereq check.
#
# Why ibazel is mandatory: dev.sh's contract is "hot-reload dev environment".
# Without ibazel, host services can't pick up `.go` edits without manual
# restart, breaking the contract. CI installs ibazel explicitly (see
# .github/workflows/bazel.yml) — no fallback in this script.

check_ibazel_doctor() {
    local missing=()
    command -v bazel  >/dev/null 2>&1 || missing+=("bazel (bazelisk)")
    command -v ibazel >/dev/null 2>&1 || missing+=("ibazel (bazel-watcher)")
    if (( ${#missing[@]} > 0 )); then
        error "缺少必需工具：${missing[*]}"
        echo "  bazel:   brew install bazelisk (macOS) | bazelisk releases (Linux)"
        echo "  ibazel:  https://github.com/bazelbuild/bazel-watcher/releases"
        echo "           (no homebrew formula — grab the darwin-arm64 / linux-amd64 binary)"
        exit 1
    fi

    # AI CLIs are runner-pod prereqs — warn (don't fail) so backend / relay
    # come up for non-pod work even when CLIs aren't installed.
    local ai_missing=()
    command -v claude >/dev/null 2>&1 || ai_missing+=("claude")
    command -v codex  >/dev/null 2>&1 || ai_missing+=("codex")
    command -v gemini >/dev/null 2>&1 || ai_missing+=("gemini")
    if (( ${#ai_missing[@]} > 0 )); then
        warn "AI CLI 未全装（${ai_missing[*]}）— runner pod 创建会受限"
        echo "  npm i -g @anthropic-ai/claude-code @openai/codex @google/gemini-cli"
    fi
}
