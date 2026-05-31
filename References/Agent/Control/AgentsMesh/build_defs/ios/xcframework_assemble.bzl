"""Starlark rule that assembles an Apple XCFramework tree artifact.

`xcframework_assemble` takes a pair of iOS slices (device + simulator-
universal) plus the uniffi-bindgen-emitted header + modulemap and
produces a directory matching Apple's xcframework layout:

    <name>.xcframework/
      Info.plist
      ios-arm64/
        <libname>.a
        Headers/
          <module>FFI.h
          module.modulemap
      ios-arm64_x86_64-simulator/
        <libname>.a
        Headers/ (same two files)

This mirrors what `xcodebuild -create-xcframework` emits, minus the
dSYM companions we don't produce. The Info.plist is templated inline
so we don't need xcodebuild on the critical path.
"""

_INFO_PLIST = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
  <key>AvailableLibraries</key>
  <array>
    <dict>
      <key>BinaryPath</key><string>{lib}</string>
      <key>HeadersPath</key><string>Headers</string>
      <key>LibraryIdentifier</key><string>ios-arm64</string>
      <key>LibraryPath</key><string>{lib}</string>
      <key>SupportedArchitectures</key><array><string>arm64</string></array>
      <key>SupportedPlatform</key><string>ios</string>
    </dict>
    <dict>
      <key>BinaryPath</key><string>{lib}</string>
      <key>HeadersPath</key><string>Headers</string>
      <key>LibraryIdentifier</key><string>ios-arm64_x86_64-simulator</string>
      <key>LibraryPath</key><string>{lib}</string>
      <key>SupportedArchitectures</key>
      <array><string>arm64</string><string>x86_64</string></array>
      <key>SupportedPlatform</key><string>ios</string>
      <key>SupportedPlatformVariant</key><string>simulator</string>
    </dict>
  </array>
  <key>CFBundlePackageType</key><string>XFWK</string>
  <key>XCFrameworkFormatVersion</key><string>1.0</string>
</dict>
</plist>
"""

def _xcframework_assemble_impl(ctx):
    out = ctx.actions.declare_directory(ctx.attr.framework_name + ".xcframework")
    lib_name = ctx.attr.lib_name
    plist = _INFO_PLIST.format(lib = lib_name)
    plist_file = ctx.actions.declare_file(ctx.label.name + ".Info.plist")
    ctx.actions.write(output = plist_file, content = plist)

    device_lib = ctx.file.device_lib
    sim_lib = ctx.file.sim_lib
    header = ctx.file.header
    modulemap = ctx.file.modulemap

    script = """
set -euo pipefail
OUT="$1"
LIB_NAME="$2"
DEVICE_LIB="$3"
SIM_LIB="$4"
HEADER="$5"
MODULEMAP="$6"
PLIST="$7"

mkdir -p "$OUT/ios-arm64/Headers"
mkdir -p "$OUT/ios-arm64_x86_64-simulator/Headers"

cp "$DEVICE_LIB" "$OUT/ios-arm64/$LIB_NAME"
cp "$HEADER"    "$OUT/ios-arm64/Headers/"
cp "$MODULEMAP" "$OUT/ios-arm64/Headers/module.modulemap"

cp "$SIM_LIB"   "$OUT/ios-arm64_x86_64-simulator/$LIB_NAME"
cp "$HEADER"    "$OUT/ios-arm64_x86_64-simulator/Headers/"
cp "$MODULEMAP" "$OUT/ios-arm64_x86_64-simulator/Headers/module.modulemap"

cp "$PLIST" "$OUT/Info.plist"
"""

    ctx.actions.run_shell(
        outputs = [out],
        inputs = [device_lib, sim_lib, header, modulemap, plist_file],
        command = script,
        arguments = [
            out.path,
            lib_name,
            device_lib.path,
            sim_lib.path,
            header.path,
            modulemap.path,
            plist_file.path,
        ],
        mnemonic = "XCFrameworkAssemble",
        progress_message = "Assembling %s.xcframework" % ctx.attr.framework_name,
    )

    return [DefaultInfo(files = depset([out]))]

xcframework_assemble = rule(
    implementation = _xcframework_assemble_impl,
    attrs = {
        "framework_name": attr.string(
            mandatory = True,
            doc = "XCFramework basename, e.g. `AgentsMeshCore`.",
        ),
        "lib_name": attr.string(
            mandatory = True,
            doc = "Static library filename copied into each slice (e.g. `libagentsmesh_ffi.a`).",
        ),
        "device_lib": attr.label(
            mandatory = True,
            allow_single_file = [".a"],
            doc = "Device (aarch64-apple-ios) static library.",
        ),
        "sim_lib": attr.label(
            mandatory = True,
            allow_single_file = [".a"],
            doc = "Simulator universal (arm64+x86_64) static library.",
        ),
        "header": attr.label(
            mandatory = True,
            allow_single_file = [".h"],
            doc = "uniffi-bindgen FFI header.",
        ),
        "modulemap": attr.label(
            mandatory = True,
            allow_single_file = [".modulemap"],
            doc = "Clang module map. Gets renamed to module.modulemap inside the xcframework.",
        ),
    },
    doc = "Assemble device + simulator-universal slices + headers into an XCFramework directory artifact.",
)
