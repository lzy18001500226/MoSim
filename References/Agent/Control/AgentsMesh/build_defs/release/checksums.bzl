"""checksums — emit a checksums.txt manifest with SHA-256 of every archive.

Equivalent to GoReleaser's `checksum:` block. Output format matches
`shasum -a 256` so users can verify with `shasum -a 256 -c checksums.txt`.

Usage:

    load("//build_defs/release:checksums.bzl", "release_checksums")

    release_checksums(
        name = "runner_checksums",
        archives = [
            ":runner_linux_amd64_archive",
            ":runner_linux_arm64_archive",
            ":runner_darwin_amd64_archive",
            # ...
        ],
    )

The output `checksums.txt` is a Bazel-buildable target that uploads
alongside the archives in the GitHub Release step.
"""

def _release_checksums_impl(ctx):
    out = ctx.actions.declare_file("checksums.txt")

    # `srcs` is a list of File objects (the actual archive outputs from
    # pkg_tar / pkg_zip). We compute sha256 over each and emit a line
    # `<sha256>  <basename>` — basename only, so the manifest is portable
    # across machines (matches GoReleaser output).
    args = ctx.actions.args()
    args.add(out)
    for src in ctx.files.archives:
        args.add(src)

    ctx.actions.run_shell(
        outputs = [out],
        inputs = ctx.files.archives,
        arguments = [args],
        command = """
set -euo pipefail
out="$1"; shift
: > "$out"
for f in "$@"; do
    name="$(basename "$f")"
    if command -v sha256sum >/dev/null 2>&1; then
        sum="$(sha256sum "$f" | awk '{print $1}')"
    else
        sum="$(shasum -a 256 "$f" | awk '{print $1}')"
    fi
    echo "${sum}  ${name}" >> "$out"
done
""",
        mnemonic = "ReleaseChecksums",
        progress_message = "Generating checksums.txt for %d archives" % len(ctx.files.archives),
    )

    return [DefaultInfo(files = depset([out]))]

release_checksums = rule(
    implementation = _release_checksums_impl,
    attrs = {
        "archives": attr.label_list(
            allow_files = True,
            mandatory = True,
            doc = "Archive targets (pkg_tar / pkg_zip outputs) to checksum.",
        ),
    },
    doc = "Emit a checksums.txt manifest (sha256) for the given archives.",
)
