"""runner_release_bundle — fan out a single go_library into release assets.

Replaces GoReleaser's `builds:` + `archives:` + `checksum:` blocks
with one Bazel call. For a (binary_name) input it generates:

  - 6 cross-compiled binaries (linux/darwin/windows × amd64/arm64)
  - 6 archives (tar.gz for unix, zip for Windows) named
    `<binary>_<goos>_<goarch>.{tar.gz,zip}`
  - 1 checksums.txt with sha256 of every archive
  - 1 `:assets` filegroup that aggregates everything for `gh release upload`

Versioning: Bazel can't include stamp data in output filenames
(filenames must be known at analysis time). The Bazel-emitted
archives use a static `<binary>_<goos>_<goarch>.{tar.gz,zip}` name;
CI is responsible for inserting the version segment when uploading
to GitHub Release (see release.yml — it copies + renames artifacts
to `<binary>_v<TAG>_<goos>_<goarch>.{tar.gz,zip}` before `gh release
upload`). This mirrors how `rules_oci` handles image tags: stamp
goes into metadata, not into the build artifact path.

Usage:

    load("//build_defs/release:release_bundle.bzl", "runner_release_bundle")

    runner_release_bundle(
        name = "release",
        embed = [":runner_lib"],
        binary_name = "agentsmesh-runner",
        archive_basename = "agentsmesh-runner",
        extra_files = ["//:README.md", "//:LICENSE"],
    )
"""

load("//build_defs/release:checksums.bzl", "release_checksums")
load("//build_defs/release:cross_binary.bzl", "SUPPORTED_PLATFORMS", "cross_binary")
load("//build_defs/release:release_archive.bzl", "release_archive")

def runner_release_bundle(
        name,
        embed,
        binary_name,
        archive_basename,
        extra_files = None,
        **kwargs):
    """Generate a full release bundle (binaries + archives + checksums).

    Args:
        name: Top-level macro target prefix. Creates `<name>_assets`
            filegroup as the entry point for CI uploads.
        embed: `go_library` targets the binary embeds.
        binary_name: Binary filename inside the archive
            (e.g., `agentsmesh-runner`). Windows builds get `.exe`
            appended automatically by rules_go.
        archive_basename: Archive name prefix (e.g., `agentsmesh-runner`).
            The macro appends `_<goos>_<goarch>.{tar.gz,zip}`.
        extra_files: Files included alongside the binary in each archive
            (README, LICENSE, etc.).
        **kwargs: Forwarded to `cross_binary` (e.g., `gc_linkopts`).
    """
    archive_targets = []
    binary_targets = []

    for goos, goarch, archive_format in SUPPORTED_PLATFORMS:
        bin_target = "{}_bin_{}_{}".format(name, goos, goarch)

        out_filename = binary_name + (".exe" if goos == "windows" else "")
        cross_binary(
            name = bin_target,
            embed = embed,
            goos = goos,
            goarch = goarch,
            out = out_filename,
            visibility = ["//visibility:private"],
            **kwargs
        )
        binary_targets.append(":" + bin_target)

        archive_target = "{}_archive_{}_{}".format(name, goos, goarch)
        archive_name = "{}_{}_{}".format(archive_basename, goos, goarch)
        release_archive(
            name = archive_target,
            binary = ":" + bin_target,
            archive_name = archive_name,
            format = archive_format,
            extra_files = extra_files,
            visibility = ["//visibility:private"],
        )
        archive_targets.append(":" + archive_target)

    checksums_target = "{}_checksums".format(name)
    release_checksums(
        name = checksums_target,
        archives = archive_targets,
        visibility = ["//visibility:private"],
    )

    native.filegroup(
        name = "{}_assets".format(name),
        srcs = archive_targets + [":" + checksums_target],
        visibility = ["//visibility:public"],
    )
