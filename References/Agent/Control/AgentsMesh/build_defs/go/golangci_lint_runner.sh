#!/usr/bin/env bash
# golangci_lint_runner.sh — sh_binary entrypoint that runs the
# hermetic golangci-lint binary over a Go module rooted at the
# live workspace tree (BUILD_WORKSPACE_DIRECTORY).
#
# Args:
#   $1  rlocation path to the golangci-lint binary
#   $2  workspace-relative module dir (e.g., "backend")
#   $3  rlocation path to the module's .golangci.yml
#
# Extra positional args are forwarded to `golangci-lint run` (e.g.,
# `--fix`).

set -uo pipefail

# Bazel's bash runfiles bootstrap. RUNFILES_DIR is set by sh_binary
# when invoked via `bazel run`. Fall back to RUNFILES_MANIFEST_FILE
# if only the manifest is available (e.g., on platforms without
# directory-based runfiles).
if [[ -z "${RUNFILES_DIR:-}" && -z "${RUNFILES_MANIFEST_FILE:-}" ]]; then
    if [[ -d "${0}.runfiles" ]]; then
        export RUNFILES_DIR="${0}.runfiles"
    elif [[ -f "${0}.runfiles_manifest" ]]; then
        export RUNFILES_MANIFEST_FILE="${0}.runfiles_manifest"
    fi
fi

runfiles_lib=""
if [[ -n "${RUNFILES_DIR:-}" && -f "${RUNFILES_DIR}/bazel_tools/tools/bash/runfiles/runfiles.bash" ]]; then
    runfiles_lib="${RUNFILES_DIR}/bazel_tools/tools/bash/runfiles/runfiles.bash"
elif [[ -n "${RUNFILES_MANIFEST_FILE:-}" ]]; then
    # On manifest-only platforms, the bash helper is alongside the manifest.
    runfiles_lib="$(dirname "$RUNFILES_MANIFEST_FILE")/bazel_tools/tools/bash/runfiles/runfiles.bash"
fi

if [[ -z "$runfiles_lib" || ! -f "$runfiles_lib" ]]; then
    echo "ERROR: bash runfiles helper not found." >&2
    echo "  RUNFILES_DIR=${RUNFILES_DIR:-<unset>}" >&2
    echo "  RUNFILES_MANIFEST_FILE=${RUNFILES_MANIFEST_FILE:-<unset>}" >&2
    exit 1
fi

# shellcheck disable=SC1090
source "$runfiles_lib"

linter_rloc="$1"
module_dir="$2"
config_rloc="$3"
shift 3

linter="$(rlocation "$linter_rloc")"
config="$(rlocation "$config_rloc")"

if [[ -z "$linter" || ! -x "$linter" ]]; then
    echo "ERROR: golangci-lint binary not found at rlocation '$linter_rloc'" >&2
    exit 1
fi
if [[ -z "$config" || ! -f "$config" ]]; then
    echo "ERROR: .golangci.yml not found at rlocation '$config_rloc'" >&2
    exit 1
fi

# `bazel run` sets BUILD_WORKSPACE_DIRECTORY to the workspace root.
# Without it (e.g., direct invocation), bail with a clear message —
# we deliberately don't fall back to runfiles because golangci-lint
# needs the live Go module tree (vendored deps, GOMODCACHE).
if [[ -z "${BUILD_WORKSPACE_DIRECTORY:-}" ]]; then
    echo "ERROR: BUILD_WORKSPACE_DIRECTORY not set — invoke via 'bazel run', not direct exec." >&2
    exit 1
fi

cd "$BUILD_WORKSPACE_DIRECTORY"

# Single-module repo: no go.work. Worktrees nested under a parent repo
# can still pick up an ancestor go.work via Go's upward search; force it
# off so golangci-lint always resolves against //:go.mod alone.
export GOWORK=off

# golangci-lint's typecheck pass needs the generated proto stubs on the
# Go module path. We don't commit them (proto/gen/ is in .bazelignore +
# never tracked), so materialize the Bazel-built .pb.go files into the
# source tree before every lint run. Bazel's action graph caches the
# generation; on a warm tree the bazel build call is a no-op + the cp is
# idempotent.
#
# `go_proto_library` runs under a Go-toolchain configuration transition,
# so its outputs land in `bazel-out/<cpu>-fastbuild-ST-<hash>/bin/...`,
# not the default-cfg `bazel info bazel-bin` path. Listing
# `bazel-bin/proto/<svc>/v1/<svc>_go_proto_/...` therefore comes back
# empty even after a successful build. We `find` across every `bin/`
# under `bazel-out/` and take the first match — every ST variant
# generates byte-identical .pb.go output, so any one of them is a valid
# source for the source-tree mirror.
#
# We materialize EVERY go_proto_library target (not just runner) because
# the backend connect handlers reference 30+ proto packages — missing
# any one trips the lint typecheck with `no required module provides package`.
#
# Also build //backend/internal/api/connect/... so the amesh_proto_convert
# Bazel rule fires + produces `*_convert.amesh.go` outputs in bazel-bin
# (the materialization loop below copies them to source tree).
bazel build --noshow_progress //proto/... //backend/internal/api/connect/... >/dev/null 2>&1 || {
    echo "ERROR: failed to bazel build //proto/... //backend/internal/api/connect/... — codegen stubs unavailable for lint." >&2
    exit 1
}
bazel_out="$(bazel info output_path 2>/dev/null)"
if [[ -z "$bazel_out" || ! -d "$bazel_out" ]]; then
    echo "ERROR: bazel output_path not resolvable: '$bazel_out'" >&2
    exit 1
fi

# Mirror every *_go_proto_ output directory into proto/gen/go/<svc>/v1/.
# The Bazel-emitted layout under each go_proto_library is:
#   .../<svc>_go_proto_/github.com/anthropics/agentsmesh/proto/gen/go/<svc>/v1/*.pb.go
# We strip everything before `proto/gen/go/` and rebuild under the workspace.
while IFS= read -r pb_file; do
    rel="${pb_file#*github.com/anthropics/agentsmesh/}"
    dest="$BUILD_WORKSPACE_DIRECTORY/$rel"
    mkdir -p "$(dirname "$dest")"
    cp -f "$pb_file" "$dest"
done < <(find "$bazel_out" -type f -path "*_go_proto_/github.com/anthropics/agentsmesh/proto/gen/go/*/*.pb.go" 2>/dev/null)

# Phase 12 codegen: `<svc>_convert.amesh.go` files generated by the
# `amesh_proto_convert` Bazel rule (build_defs/protoconv/defs.bzl). These
# live alongside handler `<svc>_convert_custom.go` and are also kept out
# of the source tree (.gitignore enforces). golangci-lint's typecheck
# pass needs them visible — materialize from bazel-bin into the handler
# packages before linting, same logic as the .pb.go mirror above.
#
# Output filename matches the rule's `output =` attr, which is the proto
# basename suffixed `_convert.amesh.go` (e.g. binding_convert.amesh.go,
# agentpod_settings_convert.amesh.go). The Bazel rule declares the file
# in `bazel-out/<cpu>-fastbuild/bin/backend/internal/api/connect/<svc>/`
# — no extra path prefix to strip, just copy each into the matching
# source-tree dir.
while IFS= read -r amesh_file; do
    rel="${amesh_file#"$bazel_out"/}"
    # rel = "<cpu>-fastbuild/bin/backend/internal/api/connect/<svc>/<file>.amesh.go"
    # Strip the leading "<cpu>-<cfg>/bin/" prefix to get the source-tree path.
    rel="${rel#*/bin/}"
    dest="$BUILD_WORKSPACE_DIRECTORY/$rel"
    mkdir -p "$(dirname "$dest")"
    cp -f "$amesh_file" "$dest"
done < <(find "$bazel_out" -type f -path "*backend/internal/api/connect/*/*_convert.amesh.go" 2>/dev/null)

echo "::group::golangci-lint $($linter --version | head -1) on $module_dir/"
"$linter" run --config="$config" --timeout=5m "$@" "./$module_dir/..."
status=$?
echo "::endgroup::"
exit $status
