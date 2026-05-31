"""Bazel rule that exposes a Rust-backed Clang module as a `CcInfo` provider
that `swift_library` can depend on directly.

The motivation: `xcframework_assemble` produces an `.xcframework` directory
artifact, but `swift_library` cannot consume directories — it needs
`CcInfo` (compilation + linking context). This rule wraps the same inputs
(header, modulemap, static libs) that fed the xcframework into a proper
provider chain so Swift code can `import AgentsMeshCoreFFI` and link the
Rust .a transparently.

Platform selection — the rule takes BOTH the device-only static lib and
the simulator-universal lib, and uses `select()` at usage sites to pick
the right one based on the target Apple platform. Bazel's CcInfo merges
both linker inputs into the final binary; the linker then ignores the
slice that doesn't match the target arch.
"""

load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")

def _swift_clang_module_impl(ctx):
    cc_toolchain = find_cpp_toolchain(ctx)
    feature_configuration = cc_common.configure_features(
        ctx = ctx,
        cc_toolchain = cc_toolchain,
        requested_features = ctx.features,
        unsupported_features = ctx.disabled_features,
    )

    header = ctx.file.header
    modulemap = ctx.file.modulemap
    static_lib = ctx.file.static_lib

    # Stage the header + modulemap into a single include directory so
    # Clang sees `#include "AgentsMeshCoreFFI.h"` and the module map
    # together. Bazel's CcInfo wants a stable include prefix.
    include_dir = ctx.actions.declare_directory(ctx.label.name + "_include")
    ctx.actions.run_shell(
        outputs = [include_dir],
        inputs = [header, modulemap],
        command = """
        set -euo pipefail
        OUT=$1; HEADER=$2; MMAP=$3
        mkdir -p "$OUT"
        cp "$HEADER" "$OUT/"
        cp "$MMAP"   "$OUT/module.modulemap"
        """,
        arguments = [include_dir.path, header.path, modulemap.path],
        mnemonic = "StageClangModule",
    )

    compilation_context = cc_common.create_compilation_context(
        headers = depset([include_dir, header, modulemap]),
        includes = depset([include_dir.path]),
    )

    library_to_link = cc_common.create_library_to_link(
        actions = ctx.actions,
        feature_configuration = feature_configuration,
        cc_toolchain = cc_toolchain,
        static_library = static_lib,
    )
    linker_input = cc_common.create_linker_input(
        owner = ctx.label,
        libraries = depset([library_to_link]),
    )
    linking_context = cc_common.create_linking_context(
        linker_inputs = depset([linker_input]),
    )

    return [
        DefaultInfo(files = depset([include_dir, static_lib])),
        CcInfo(
            compilation_context = compilation_context,
            linking_context = linking_context,
        ),
    ]

swift_clang_module = rule(
    implementation = _swift_clang_module_impl,
    attrs = {
        "header": attr.label(
            mandatory = True,
            allow_single_file = [".h"],
            doc = "Generated Clang header (uniffi-bindgen output).",
        ),
        "modulemap": attr.label(
            mandatory = True,
            allow_single_file = [".modulemap"],
            doc = "Generated Clang module map.",
        ),
        "static_lib": attr.label(
            mandatory = True,
            allow_single_file = [".a"],
            doc = "Static library binary (.a) — must match target Apple platform.",
        ),
        "_cc_toolchain": attr.label(default = "@bazel_tools//tools/cpp:current_cc_toolchain"),
    },
    fragments = ["cpp"],
    toolchains = ["@bazel_tools//tools/cpp:toolchain_type"],
    doc = "Wrap a Rust XCFramework's headers + static lib into a CcInfo so swift_library can depend on it.",
)
