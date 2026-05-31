"""release_archive — wrap a cross-compiled binary in tar.gz or zip.

Equivalent to GoReleaser's `archives:` block. Each archive contains:
  - the binary (e.g., `agentsmesh-runner` or `agentsmesh-runner.exe`)
  - README.md
  - LICENSE (best-effort — included if the file exists)

Usage:

    load("//build_defs/release:release_archive.bzl", "release_archive")

    release_archive(
        name = "runner_linux_amd64_archive",
        binary = ":runner_linux_amd64",
        archive_name = "agentsmesh-runner_1.2.3_linux_amd64",
        format = "tar.gz",
        extra_files = ["//:README.md", "//:LICENSE"],
    )
"""

load("@rules_pkg//pkg:tar.bzl", "pkg_tar")
load("@rules_pkg//pkg:zip.bzl", "pkg_zip")

def release_archive(name, binary, archive_name, format, extra_files = None, **kwargs):
    """Wrap a binary + extras in a tar.gz / zip release archive.

    Args:
        name: Target name. Convention: `<binary>_<goos>_<goarch>_archive`.
        binary: Label of the cross-compiled `go_binary`. The archive
            uses the binary's output filename as-is (e.g.,
            `agentsmesh-runner` or `agentsmesh-runner.exe`).
        archive_name: Archive base name (no extension).
            E.g. `agentsmesh-runner_1.2.3_linux_amd64`.
        format: `tar.gz` or `zip`.
        extra_files: List of supplementary file labels (README, LICENSE).
        **kwargs: Forwarded to `pkg_tar` / `pkg_zip`.
    """
    extras = list(extra_files or [])

    if format == "tar.gz":
        pkg_tar(
            name = name,
            srcs = [binary] + extras,
            extension = "tar.gz",
            package_file_name = archive_name + ".tar.gz",
            strip_prefix = ".",
            **kwargs
        )
    elif format == "zip":
        pkg_zip(
            name = name,
            srcs = [binary] + extras,
            package_file_name = archive_name + ".zip",
            **kwargs
        )
    else:
        fail("Unsupported archive format: %s (expected 'tar.gz' or 'zip')" % format)
