#!/bin/bash
# dev_runner.sh — `bazel run //deploy/dev:up` (and siblings) entrypoint.
#
# `bazel run` sets BUILD_WORKSPACE_DIRECTORY to the workspace root. We cd
# into the live source tree's deploy/dev/ before exec-ing dev.sh, so dev.sh's
# SCRIPT_DIR resolves to the real path — required because dev.sh writes
# `.env`, runs `docker compose`, references `runner.Dockerfile` build context,
# and copies the bazel-built runner binary to `deploy/dev/runner-binary`. All
# of that needs to land in the source tree, not the bazel runfiles tree.
#
# The sh_binary `args` attribute in BUILD.bazel pins each target to one
# dev.sh flag (e.g. `:clean` → `--clean`), so `bazel run //deploy/dev:clean`
# is unambiguous; users can still pass extra args after `--`.

set -euo pipefail

if [[ -z "${BUILD_WORKSPACE_DIRECTORY:-}" ]]; then
    echo "ERROR: BUILD_WORKSPACE_DIRECTORY not set — invoke via 'bazel run', not direct exec." >&2
    exit 1
fi

cd "$BUILD_WORKSPACE_DIRECTORY/deploy/dev"
exec bash dev.sh "$@"
