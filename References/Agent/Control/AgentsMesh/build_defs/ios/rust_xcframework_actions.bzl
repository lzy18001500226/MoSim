"""Supporting Starlark rules for `rust_xcframework`.

- `pick_static_lib`: filters a platform_transition_filegroup's
  multi-file DefaultInfo down to a single `.a` file exposed as its own
  target (so downstream `allow_single_file` attrs resolve cleanly).
- `lipo_universal`: merges two same-name static libraries (arm64 +
  x86_64 simulator) into a fat static library.
- `uniffi_swift_bindings`: runs the uniffi-bindgen binary against a
  static library to emit the Swift glue + C header + modulemap, then
  renames the outputs to match a caller-provided module name.
"""

def _pick_static_lib_impl(ctx):
    files = ctx.attr.src[DefaultInfo].files.to_list()
    match = None
    for f in files:
        if f.basename == ctx.attr.lib_name:
            match = f
            break
    if match == None:
        fail("pick_static_lib: no `{}` in {}; got: {}".format(
            ctx.attr.lib_name,
            ctx.attr.src.label,
            [f.basename for f in files],
        ))

    # Declare under the rule's own subdir so multiple picks of the same
    # library in one package don't collide on output paths.
    out = ctx.actions.declare_file("{}/{}".format(ctx.label.name, ctx.attr.lib_name))
    ctx.actions.symlink(output = out, target_file = match)
    return [DefaultInfo(files = depset([out]))]

pick_static_lib = rule(
    implementation = _pick_static_lib_impl,
    attrs = {
        "src": attr.label(
            mandatory = True,
            doc = "Target whose DefaultInfo contains the wanted `.a`.",
        ),
        "lib_name": attr.string(
            mandatory = True,
            doc = "Filename of the static library (e.g. `libagentsmesh_ffi.a`).",
        ),
    },
    doc = "Expose a single `.a` from a multi-file target as its own single-file label.",
)

def _lipo_universal_impl(ctx):
    out = ctx.actions.declare_file("{}/{}".format(ctx.label.name, ctx.attr.lib_name))
    inputs = [f for t in ctx.attr.srcs for f in t[DefaultInfo].files.to_list()]
    args = ctx.actions.args()
    args.add("-create")
    for f in inputs:
        args.add(f.path)
    args.add("-output", out.path)
    ctx.actions.run(
        outputs = [out],
        inputs = inputs,
        executable = "/usr/bin/lipo",
        arguments = [args],
        mnemonic = "Lipo",
        progress_message = "lipo -create %s" % ctx.attr.lib_name,
    )
    return [DefaultInfo(files = depset([out]))]

lipo_universal = rule(
    implementation = _lipo_universal_impl,
    attrs = {
        "srcs": attr.label_list(
            mandatory = True,
            allow_files = [".a"],
            doc = "Static libraries to merge (typically arm64 + x86_64 simulator).",
        ),
        "lib_name": attr.string(
            mandatory = True,
            doc = "Output filename.",
        ),
    },
    doc = "Merge same-name static libraries into a universal binary via `lipo -create`.",
)

def _uniffi_swift_bindings_impl(ctx):
    mod = ctx.attr.module_name
    crate = ctx.attr.crate_name
    out_dir_name = ctx.label.name + "_out"

    # The modulemap's internal `module X { header "X.h" }` ties the
    # header filename to uniffi's module declaration, so `<crate>FFI.h`
    # and `<crate>FFI.modulemap` stay paired as emitted. Only the
    # caller-facing `.swift` glue is renamed to `<module>.swift` (which
    # is what SPM's Package.swift target imports).
    header = ctx.actions.declare_file("{}/{}FFI.h".format(out_dir_name, crate))
    modulemap = ctx.actions.declare_file("{}/{}FFI.modulemap".format(out_dir_name, crate))
    swift = ctx.actions.declare_file("{}/{}.swift".format(out_dir_name, mod))

    tool = ctx.executable.uniffi_bindgen
    lib = ctx.file.library

    # Stage a minimal Cargo.toml so uniffi-bindgen's `cargo metadata`
    # call succeeds inside the sandbox. The manifest only needs to be
    # parseable — uniffi doesn't read deps, just crate-level config
    # which we don't use. Writing it inline avoids dragging the real
    # workspace Cargo.toml (which has `workspace = true` path deps the
    # sandbox can't resolve) into the action.
    stub_manifest = ctx.actions.declare_file(ctx.label.name + "_stub_Cargo.toml")
    ctx.actions.write(
        output = stub_manifest,
        content = '[package]\nname = "%s-stub"\nversion = "0.0.0"\nedition = "2021"\n\n[lib]\npath = "lib.rs"\n' % crate,
    )

    script = """
set -euo pipefail
TOOL="$1"
LIB="$2"
OUT_DIR="$3"
MOD="$4"
CRATE="$5"
STUB_MANIFEST="$6"

# Resolve paths before cd-ing into the work dir.
case "$TOOL" in /*) ;; *) TOOL="$PWD/$TOOL" ;; esac
case "$LIB" in /*) ;; *) LIB="$PWD/$LIB" ;; esac
case "$STUB_MANIFEST" in /*) ;; *) STUB_MANIFEST="$PWD/$STUB_MANIFEST" ;; esac
case "$OUT_DIR" in /*) ;; *) OUT_DIR="$PWD/$OUT_DIR" ;; esac

mkdir -p "$OUT_DIR"
WORK="$(mktemp -d)"
cp "$STUB_MANIFEST" "$WORK/Cargo.toml"
touch "$WORK/lib.rs"
export PATH="$HOME/.cargo/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
cd "$WORK"

"$TOOL" generate --library "$LIB" --language swift --out-dir "$OUT_DIR" --crate "$CRATE" --metadata-no-deps --no-format

# Rename only the Swift glue. Header+modulemap keep the crate-derived
# `<crate>FFI.*` names so the modulemap's `header "<crate>FFI.h"`
# directive stays valid.
if [ "$CRATE" != "$MOD" ] && [ -f "$OUT_DIR/${CRATE}.swift" ]; then
  mv "$OUT_DIR/${CRATE}.swift" "$OUT_DIR/${MOD}.swift"
fi
"""

    out_dir = header.dirname
    ctx.actions.run_shell(
        outputs = [header, modulemap, swift],
        inputs = [lib, stub_manifest],
        tools = [tool],
        command = script,
        arguments = [tool.path, lib.path, out_dir, mod, crate, stub_manifest.path],
        mnemonic = "UniFFIBindgen",
        progress_message = "Generating %s Swift bindings" % mod,
        use_default_shell_env = True,
        execution_requirements = {"requires-darwin": ""},
    )

    return [
        DefaultInfo(files = depset([swift, header, modulemap])),
        OutputGroupInfo(
            swift = depset([swift]),
            header = depset([header]),
            modulemap = depset([modulemap]),
        ),
    ]

uniffi_swift_bindings = rule(
    implementation = _uniffi_swift_bindings_impl,
    attrs = {
        "library": attr.label(
            mandatory = True,
            allow_single_file = [".a"],
            doc = "Static library passed to `uniffi-bindgen --library`.",
        ),
        "module_name": attr.string(
            mandatory = True,
            doc = "Swift module name. The `.swift` glue is renamed to `<module>.swift`; header + modulemap keep their `<crate>FFI.*` names.",
        ),
        "crate_name": attr.string(
            mandatory = True,
            doc = "Rust crate name (e.g. `agentsmesh_ffi`). Passed to `uniffi-bindgen --crate`; baked into `<crate>FFI.{h,modulemap}`.",
        ),
        "uniffi_bindgen": attr.label(
            mandatory = True,
            executable = True,
            cfg = "exec",
            doc = "uniffi-bindgen binary target.",
        ),
    },
    doc = "Generate Swift glue + C header + modulemap from a uniffi-exporting static library.",
)
