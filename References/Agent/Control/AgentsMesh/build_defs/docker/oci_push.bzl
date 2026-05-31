"""Shared multi-registry push targets for OCI images.

Used by `go_oci_image` (Go services) and `next_oci_image` (Next.js
apps) to expose the same `:name_push_<key>` / `:name_push` shape from
both pipelines.

Each registry in `repositories` becomes a `:<name>_push_<key>` target.
A back-compat alias `:<name>_push` points at `default` if present,
otherwise the alphabetically first key.

Tag list is stamped from `build_defs/workspace_status.sh`: every push
publishes `latest` plus the CI-stamped `IMAGE_VERSION` and
`IMAGE_MINOR`. The stamp keys are referenced as `STABLE_*` so the
push is bound to the stable status file.
"""

load("@aspect_bazel_lib//lib:expand_template.bzl", "expand_template")
load("@rules_oci//oci:defs.bzl", "oci_push")

_DEFAULT_TAG_TEMPLATE = [
    "latest",
    "STAMP_VERSION",
    "STAMP_MINOR",
]

_DEFAULT_STAMP_SUBSTITUTIONS = {
    "STAMP_VERSION": "{{STABLE_IMAGE_VERSION}}",
    "STAMP_MINOR": "{{STABLE_IMAGE_MINOR}}",
}

def oci_push_targets(
        name,
        image,
        repositories = {},
        repository = None,
        tag_template = _DEFAULT_TAG_TEMPLATE,
        stamp_substitutions = _DEFAULT_STAMP_SUBSTITUTIONS,
        visibility = ["//visibility:public"]):
    """Emit per-registry oci_push targets + back-compat alias.

    Args:
        name: Base name. The image target is `:<name>` and the helper
            adds `:<name>_tags`, `:<name>_push_<reg_key>`, `:<name>_push`.
        image: Label of the `oci_image` to push.
        repositories: Dict mapping registry key → full repo URL.
            E.g. `{"dockerhub": "agentsmesh/backend"}`.
        repository: Back-compat single-registry shorthand; treated as
            `repositories = {"default": repository}`. Prefer the dict.
        tag_template: List of tag strings. Tokens listed in
            `stamp_substitutions` are replaced via `expand_template`'s
            stamping; everything else is literal.
        stamp_substitutions: Map of placeholder → `{{STABLE_*}}` key
            for `--stamp` substitution.
        visibility: Standard visibility for the generated targets.
    """
    repos = dict(repositories)
    if repository and not repos:
        repos["default"] = repository

    if not repos:
        return

    expand_template(
        name = name + "_tags",
        out = name + "_tags.txt",
        stamp_substitutions = stamp_substitutions,
        template = tag_template,
    )

    for reg_key in sorted(repos.keys()):
        oci_push(
            name = "{}_push_{}".format(name, reg_key),
            image = image,
            remote_tags = ":" + name + "_tags",
            repository = repos[reg_key],
            visibility = visibility,
        )

    # Back-compat alias: prefer "default", else first alphabetical key.
    back_compat_key = "default" if "default" in repos else sorted(repos.keys())[0]
    native.alias(
        name = name + "_push",
        actual = ":{}_push_{}".format(name, back_compat_key),
        visibility = visibility,
    )
