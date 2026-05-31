"""OCI image macro for AgentsMesh Go services.

Produces an OCI image (distroless-based), a local `_tarball` for
`docker load`, and one `_push_<key>` target per registry in
`repositories`. Tag stamping plugs into `build_defs/workspace_status.sh` via
Bazel's `--stamp --workspace_status_command=...` flags so the tag list
comes from the CI environment, not the BUILD file.

Usage:
    load("//build_defs/docker:go_oci_image.bzl", "go_oci_image")

    go_oci_image(
        name = "image",
        binary = ":server",
        exposed_ports = ["8080/tcp"],
        repositories = {
            "dockerhub":  "agentsmesh/backend",
            "agentsmesh": "registry.agentsmesh.ai/agentsmesh/backend",
        },
    )

    # Produces:
    #   :image                   — oci_image
    #   :image_tarball           — oci_load (docker load)
    #   :image_push_dockerhub    — oci_push to Docker Hub
    #   :image_push_agentsmesh   — oci_push to AgentsMesh registry

Used by backend/runner/relay to produce distroless images.
"""

load("@rules_oci//oci:defs.bzl", "oci_image", "oci_load")
load("@rules_pkg//pkg:mappings.bzl", "pkg_attributes", "pkg_mkdirs")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")
load(":oci_push.bzl", "oci_push_targets")

# uid/gid the container runs as. Pinned to 1000:1000 to match the
# legacy GoReleaser/Dockerfile-built images (`addgroup -g 1000 -S app
# && adduser -u 1000 -S app -G app`) so existing prod swarm volumes
# (e.g. `agentsmesh_backend_data`) — created by the GoReleaser image
# and already owned by uid 1000 on disk — keep working without a
# manual chown after the Bazel migration. Distroless's built-in
# `nonroot` user is uid 65532, which would otherwise force a one-shot
# `chown -R 65532:65532 …` on every prod node holding stateful volumes.
APP_UID = "1000"
APP_GID = "1000"

def go_oci_image(
        name,
        binary,
        base = "@distroless_static",
        env = {},
        exposed_ports = [],
        labels = {},
        repositories = {},
        repository = None,
        visibility = ["//visibility:public"]):
    """Bundle a Go binary into a distroless OCI image + push targets.

    Args:
        name: Target name.
        binary: Label of the `go_binary` to embed.
        base: OCI base image, defaults to distroless/static.
        env: Environment variables inside the container.
        exposed_ports: Ports to expose on the image.
        labels: OCI labels to add to the image.
        repositories: Dict mapping registry key → full repo URL. Every
            entry becomes a `:name_push_<key>` target. `bazel run` one
            of them with `--stamp --workspace_status_command=...` to
            push with the CI-provided version tag.
        repository: Back-compat single-registry shorthand; equivalent
            to `repositories = {"default": repository}`. Prefer the dict.
        visibility: Standard visibility.
    """
    binary_name = binary.split(":")[-1]

    # /app + binary owned by 1000:1000 — same ownership the GoReleaser
    # Dockerfile produced via `chown -R app:app /app`. Without this the
    # binary lands as root:root and the runtime user can't mkdir/write
    # under /app (e.g. logger's `logs/` subdir, ACME staging, etc.).
    pkg_tar(
        name = name + "_layer",
        srcs = [binary],
        package_dir = "/app",
        owner = APP_UID + "." + APP_GID,
        mode = "0755",
    )

    # Pre-create /data/acme (and therefore /data) owned by 1000:1000.
    # Docker swarm copies the image's view of a mountpoint into a
    # freshly-created volume — including ownership — so this lets new
    # `agentsmesh_backend_data` volumes inherit 1000:1000 from day
    # one. Existing prod volumes are already 1000:1000 (legacy
    # Dockerfile invariant) so this aligns the two paths.
    pkg_mkdirs(
        name = name + "_data_dirs",
        dirs = [
            "/data",
            "/data/acme",
        ],
        attributes = pkg_attributes(
            mode = "0755",
            user = APP_UID,
            group = APP_GID,
        ),
    )
    pkg_tar(
        name = name + "_data_layer",
        srcs = [":" + name + "_data_dirs"],
    )

    oci_image(
        name = name,
        base = base,
        entrypoint = ["/app/" + binary_name],
        env = env,
        exposed_ports = exposed_ports,
        labels = labels,
        tars = [
            ":" + name + "_layer",
            ":" + name + "_data_layer",
        ],
        # Numeric uid (not the distroless `nonroot` alias) so we don't
        # depend on the base image's /etc/passwd. 1000 matches the
        # `app` user the legacy GoReleaser image created.
        user = APP_UID,
        visibility = visibility,
        workdir = "/app",
    )

    oci_load(
        name = name + "_tarball",
        image = ":" + name,
        repo_tags = ["agentsmesh/" + binary_name + ":latest"],
        visibility = visibility,
    )

    oci_push_targets(
        name = name,
        image = ":" + name,
        repositories = repositories,
        repository = repository,
        visibility = visibility,
    )
