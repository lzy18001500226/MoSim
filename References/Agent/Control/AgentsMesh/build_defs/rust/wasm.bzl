"""Rust → WASM ESM package for browser consumption.

Wraps the community `rules_rust_wasm_bindgen` ruleset with an opinionated
default: always target `web`, always invoke `wasm-opt` in release, and
expose a single `<name>_pkg` that downstream TypeScript targets can
`npm.link_packages()` against.

Usage:
    load("//build_defs/rust:wasm.bzl", "rust_wasm_library")

    rust_wasm_library(
        name = "wasm",
        crate = "//clients/core/crates/wasm:wasm_lib",
        visibility = ["//clients/web:__subpackages__"],
    )

    # In clients/web/BUILD.bazel:
    npm_link_package(
        name = "agentsmesh-wasm",
        src = "//clients/core/crates/wasm:wasm_pkg",
    )
"""

load("@rules_rust_wasm_bindgen//:defs.bzl", "rust_wasm_bindgen")

def rust_wasm_library(
        name,
        crate,
        target = "web",
        tags = None,
        visibility = None):
    """Compile a Rust crate to wasm + JS glue + TypeScript .d.ts.

    The wasm-bindgen CLI runs against the Rust cdylib output, produces
    `<name>_bg.wasm`, `<name>.js`, and `<name>.d.ts`. Downstream
    `aspect_rules_js` packages consume the bundle as a regular npm
    package via `npm_link_package`.

    Args:
        name: Package name (also used as module prefix).
        crate: Label of the `rust_library(crate_type = "cdylib")` target.
        target: wasm-bindgen target, "web" (default) | "bundler" | "nodejs".
        tags: Optional tags forwarded to the underlying rule (e.g. ["manual"]
            to keep the target out of `bazel build //...` until upstream
            crate manifests support per-triple cfg-gating; see
            `clients/core/crates/wasm/BUILD.bazel` for the diagnosis).
        visibility: Standard visibility attribute.
    """
    rust_wasm_bindgen(
        name = name,
        target = target,
        tags = tags,
        wasm_file = crate,
        visibility = visibility or ["//visibility:public"],
    )
