"""Pure-Bazel Rust → iOS XCFramework macro.

`rust_xcframework(name, crate, module_name, lib_name)` wires a
`rust_static_library` target into three iOS-targeted slices (device,
simulator arm64, simulator x86_64), lipos the simulator pair, runs
uniffi-bindgen to produce Swift glue + headers + modulemap, then
assembles everything into an Apple XCFramework directory. No
xcodebuild, no shell script — the pipeline is purely Bazel actions.

Usage:
    load("//build_defs/ios:rust_xcframework.bzl", "rust_xcframework")

    rust_xcframework(
        name = "AgentsMeshCore",
        crate = ":ffi",
        module_name = "AgentsMeshCore",
        lib_name = "libagentsmesh_ffi.a",
        visibility = ["//clients/ios:__subpackages__"],
    )

The rule that backs `crate` must be a `rust_static_library` emitting
`lib<crate_name>.a`. The three iOS rustc triples must be registered
(`extra_target_triples` in MODULE.bazel).
"""

load("@aspect_bazel_lib//lib:transitions.bzl", "platform_transition_filegroup")
load(":rust_xcframework_actions.bzl", "lipo_universal", "pick_static_lib", "uniffi_swift_bindings")
load(":swift_clang_module.bzl", "swift_clang_module")
load(":xcframework_assemble.bzl", "xcframework_assemble")

def rust_xcframework(
        name,
        crate,
        module_name,
        lib_name,
        uniffi_bindgen = "//clients/core/crates/uniffi-bindgen:uniffi-bindgen",
        visibility = None):
    """Build a Rust-backed iOS XCFramework.

    Args:
        name: Target name. Also the xcframework directory basename
            (`<name>.xcframework`).
        crate: Label of a `rust_static_library` target with
            `crate_features = ["staticlib"]`. Must compile on the
            three iOS triples registered in MODULE.bazel.
        module_name: Swift module name exposed to consumers. Drives the
            generated `.swift`/`FFI.h`/`FFI.modulemap` filenames.
        lib_name: Static library filename on disk — e.g.
            `libagentsmesh_ffi.a`. Must match the rust_static_library's
            crate name (crate_name `agentsmesh_ffi` → `libagentsmesh_ffi.a`).
        uniffi_bindgen: Label of the uniffi-bindgen rust_binary.
        visibility: Standard visibility.

    The framework only builds on macOS hosts; the iOS rustc std slices
    rules_rust registers are not available on Linux runners, so every
    target is tagged `manual` + `requires-darwin`.
    """
    tags = ["manual", "requires-darwin", "ios"]

    device_fg = name + "_device_slice"
    sim_arm_fg = name + "_sim_arm64_slice"
    sim_x86_fg = name + "_sim_x86_64_slice"

    platform_transition_filegroup(
        name = device_fg,
        srcs = [crate],
        target_platform = "//build_defs/ios:ios_arm64",
        tags = tags,
    )
    platform_transition_filegroup(
        name = sim_arm_fg,
        srcs = [crate],
        target_platform = "//build_defs/ios:ios_sim_arm64",
        tags = tags,
    )
    platform_transition_filegroup(
        name = sim_x86_fg,
        srcs = [crate],
        target_platform = "//build_defs/ios:ios_x86_64",
        tags = tags,
    )

    device_lib = name + "_device_lib"
    sim_arm_lib = name + "_sim_arm64_lib"
    sim_x86_lib = name + "_sim_x86_64_lib"
    pick_static_lib(
        name = device_lib,
        src = ":" + device_fg,
        lib_name = lib_name,
        tags = tags,
    )
    pick_static_lib(
        name = sim_arm_lib,
        src = ":" + sim_arm_fg,
        lib_name = lib_name,
        tags = tags,
    )
    pick_static_lib(
        name = sim_x86_lib,
        src = ":" + sim_x86_fg,
        lib_name = lib_name,
        tags = tags,
    )

    sim_lib = name + "_sim_universal"
    lipo_universal(
        name = sim_lib,
        srcs = [":" + sim_arm_lib, ":" + sim_x86_lib],
        lib_name = lib_name,
        tags = tags,
    )

    bindings = name + "_bindings"

    # Derive the Rust crate name from the library filename: the usual
    # convention is `lib<crate_name>.a` so stripping those prefixes/
    # suffixes gives us the identifier uniffi-bindgen's `--crate`
    # expects.
    crate_id = lib_name.replace("lib", "", 1).replace(".a", "")
    uniffi_swift_bindings(
        name = bindings,
        library = ":" + device_lib,
        module_name = module_name,
        crate_name = crate_id,
        uniffi_bindgen = uniffi_bindgen,
        tags = tags,
    )

    header_fg = bindings + "_header"
    modulemap_fg = bindings + "_modulemap"
    swift_fg = bindings + "_swift"
    native.filegroup(
        name = header_fg,
        srcs = [":" + bindings],
        output_group = "header",
        tags = tags,
    )
    native.filegroup(
        name = modulemap_fg,
        srcs = [":" + bindings],
        output_group = "modulemap",
        tags = tags,
    )
    native.filegroup(
        name = swift_fg,
        srcs = [":" + bindings],
        output_group = "swift",
        tags = tags,
    )

    xcframework_assemble(
        name = name,
        framework_name = module_name,
        lib_name = lib_name,
        device_lib = ":" + device_lib,
        sim_lib = ":" + sim_lib,
        header = ":" + header_fg,
        modulemap = ":" + modulemap_fg,
        tags = tags,
        visibility = visibility,
    )

    # Swift glue exposed alongside the xcframework so SPM/consumers can
    # stage it next to the binary target without re-running bindgen.
    native.alias(
        name = name + "_swift",
        actual = ":" + swift_fg,
        tags = ["manual"],
        visibility = visibility,
    )

    # CcInfo-providing wrapper so `swift_library` can depend on it
    # directly. Per-platform `_cc_device` and `_cc_sim` targets pair the
    # Clang module (header + modulemap) with the matching .a slice; the
    # public `_cc` alias selects the right one based on the target Apple
    # platform so simulator builds get the simulator-universal lib and
    # device builds get the device .a.
    swift_clang_module(
        name = name + "_cc_device",
        header = ":" + header_fg,
        modulemap = ":" + modulemap_fg,
        static_lib = ":" + device_lib,
        tags = tags,
        visibility = ["//visibility:private"],
    )
    swift_clang_module(
        name = name + "_cc_sim",
        header = ":" + header_fg,
        modulemap = ":" + modulemap_fg,
        static_lib = ":" + sim_lib,
        tags = tags,
        visibility = ["//visibility:private"],
    )
    native.alias(
        name = name + "_cc",
        actual = select({
            "@build_bazel_apple_support//constraints:simulator": ":" + name + "_cc_sim",
            "@build_bazel_apple_support//constraints:device": ":" + name + "_cc_device",
            "//conditions:default": ":" + name + "_cc_device",
        }),
        visibility = visibility,
    )
