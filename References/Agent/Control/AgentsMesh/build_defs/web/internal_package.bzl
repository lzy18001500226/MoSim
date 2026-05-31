"""Internal npm package helpers — Bazel as the SSOT for package metadata.

Replaces source-tree `package.json` files for first-party `@agentsmesh/*`
packages. The package metadata (name, version, main, dependencies) is
declared in BUILD.bazel via `internal_npm_package(...)`; a synthetic
`package.json` is materialised into bazel-bin at build time and shipped
alongside the source files through aspect_rules_js's `npm_package` rule.

Downstream `npm_link_package` in the root BUILD.bazel registers the
result at `//:node_modules/@agentsmesh/<name>` — no `workspace:*` /
pnpm-workspace.yaml entry required.

Usage:
    load("//build_defs/web:internal_package.bzl", "internal_npm_package")

    internal_npm_package(
        name = "pkg",
        package_name = "@agentsmesh/electron-adapter",
        version = "0.1.0",
        main = "src/index.ts",
        dependencies = {"@agentsmesh/service-interface": "*"},
        srcs = glob(["src/**/*.ts"], exclude = ["src/**/*.test.ts"]),
    )
"""

load("@aspect_rules_js//npm:defs.bzl", "npm_package")
load("@bazel_skylib//rules:write_file.bzl", "write_file")

def generated_package_json(
        name,
        package_name,
        version = "0.1.0",
        main = None,
        types = None,
        dependencies = None,
        dev_dependencies = None,
        extra = None,
        **kwargs):
    """Generate a `package.json` file from BUILD.bazel attrs.

    Output is a tree-artifact-relative `package.json` written via
    `write_file`. Content is JSON encoded from a Starlark dict; key
    insertion order is preserved (deterministic across builds).

    Args:
        name: Bazel target name. The actual filename is always
            `package.json` (Node's resolver requires that).
        package_name: npm package name (e.g. `@agentsmesh/foo`).
            Must match downstream `npm_link_package(name = "...")`.
        version: Semver string. Internal packages all use `0.1.0`.
        main: Path to the entry point relative to package root.
        types: Path to TS declarations. Defaults to `main`.
        dependencies: Dict of runtime deps; values are version specs
            (use `*` for first-party links — npm_link_package overrides).
        dev_dependencies: Same shape as `dependencies`.
        extra: Dict merged into the final JSON. Use for tool-specific
            keys (`napi`, `scripts`, `files`, etc.).
        **kwargs: Forwarded to `write_file` (visibility, tags…).
    """
    pkg = {
        "name": package_name,
        "version": version,
        "private": True,
    }
    if main:
        pkg["main"] = main
    if types:
        pkg["types"] = types
    if dependencies:
        pkg["dependencies"] = dependencies
    if dev_dependencies:
        pkg["devDependencies"] = dev_dependencies
    if extra:
        pkg.update(extra)

    write_file(
        name = name,
        out = "package.json",
        content = [json.encode_indent(pkg, indent = "  ")],
        **kwargs
    )

def internal_npm_package(
        name,
        package_name,
        version = "0.1.0",
        main = "src/index.ts",
        types = None,
        dependencies = None,
        dev_dependencies = None,
        extra = None,
        srcs = [],
        visibility = None,
        **kwargs):
    """Define an internal npm package without source-tree `package.json`.

    Wraps `generated_package_json` + `npm_package`. The result is
    consumable by `npm_link_package(src = "//<pkg>:pkg")` from the
    root BUILD.bazel.

    Args:
        name: Target name; downstream consumers use `:<name>`.
        package_name: npm package name.
        version: Semver string.
        main: Entry point relative to the package root.
        types: TS declarations entry. Defaults to `main`.
        dependencies: Runtime deps dict. See generated_package_json.
        dev_dependencies: Dev deps dict. See generated_package_json.
        extra: Extra JSON fields. See generated_package_json.
        srcs: Files shipped alongside the generated package.json.
            Pass `ts_project` outputs and/or `glob(["src/**/*.ts"])`.
        visibility: Standard visibility. Defaults to public.
        **kwargs: Forwarded to `npm_package`.
    """
    generated_package_json(
        name = name + "_pkg_json",
        package_name = package_name,
        version = version,
        main = main,
        types = types or main,
        dependencies = dependencies,
        dev_dependencies = dev_dependencies,
        extra = extra,
    )

    npm_package(
        name = name,
        package = package_name,
        version = version,
        srcs = [":" + name + "_pkg_json"] + srcs,
        visibility = visibility or ["//visibility:public"],
        **kwargs
    )
