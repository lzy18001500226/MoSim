"""amesh_proto_convert — Bazel rule that invokes the
`protoc-gen-amesh-convert` plugin to generate Go domain↔wire converter
functions from .proto annotations.

Output: a single `<name>_convert.amesh.go` file under bazel-bin, ready to
be added to a `go_library`'s srcs.

Usage:

    load("//build_defs/protoconv:defs.bzl", "amesh_proto_convert")

    amesh_proto_convert(
        name = "binding_convert_amesh",
        proto = "//proto/binding/v1:binding_proto",
        output = "binding_convert.amesh.go",
    )

    go_library(
        name = "binding",
        srcs = [
            "binding.go",
            "convert_custom.go",   # hand-written field_custom helpers
            ":binding_convert_amesh",
        ],
        ...
    )

The rule:
  1. Reads `ProtoInfo.transitive_sources` from the `proto` dep
  2. Invokes `@com_google_protobuf//:protoc` with our plugin
  3. Passes `--amesh-convert_opt=flat=1` so the plugin emits the file at
     the protoc `out` root (rather than nested under the annotation's
     output_dir, which is buf-only)
  4. Declares the output file relative to the rule's package, so the
     generated `.go` is accessible to downstream `go_library` srcs

The annotation's `convert_target.output_package` is honoured by the plugin
when writing the `package <name>` line; `output_dir` is ignored under
`flat=1` (Bazel controls placement).
"""

load("@rules_proto//proto:defs.bzl", "ProtoInfo")

def _amesh_proto_convert_impl(ctx):
    proto_info = ctx.attr.proto[ProtoInfo]
    output = ctx.actions.declare_file(ctx.attr.output)

    args = ctx.actions.args()
    args.add("--plugin=protoc-gen-amesh-convert=" + ctx.executable._plugin.path)
    args.add("--amesh-convert_out=" + output.dirname)
    args.add("--amesh-convert_opt=flat=1")

    # Proto include paths — protoc needs each import root that any
    # transitive .proto resolves through. proto_source_root is the
    # per-target adjustment; transitive_proto_path includes deps.
    if proto_info.proto_source_root:
        args.add("-I", proto_info.proto_source_root)
    for path in proto_info.transitive_proto_path.to_list():
        args.add("-I", path)

    # The proto file(s) to compile — only the direct sources; transitives
    # are reachable via -I and consulted for annotation extension types
    # (e.g. codegen/v1/options.proto).
    #
    # When `proto_file` is set, restrict protoc to that single .proto so a
    # multi-srcs proto_library (e.g. pod has agentpod_settings.proto + pod.proto)
    # can produce one output per file via N parallel amesh_proto_convert rules
    # without Bazel hitting an undeclared-output failure.
    direct_sources = proto_info.direct_sources
    if ctx.attr.proto_file:
        filtered = [s for s in direct_sources if s.basename == ctx.attr.proto_file]
        if not filtered:
            fail("proto_file %s not found in direct_sources of %s" % (
                ctx.attr.proto_file,
                ctx.attr.proto.label,
            ))
        direct_sources = filtered
    for src in direct_sources:
        args.add(src.path)

    ctx.actions.run(
        executable = ctx.executable._protoc,
        arguments = [args],
        inputs = depset(
            direct = [ctx.executable._plugin],
            transitive = [proto_info.transitive_sources],
        ),
        outputs = [output],
        mnemonic = "AmeshConvert",
        progress_message = "AmeshConvert %s" % output.short_path,
    )

    return [DefaultInfo(files = depset([output]))]

amesh_proto_convert = rule(
    implementation = _amesh_proto_convert_impl,
    attrs = {
        "proto": attr.label(
            providers = [ProtoInfo],
            mandatory = True,
            doc = "proto_library carrying (amesh.codegen.v1.*) annotations.",
        ),
        "output": attr.string(
            mandatory = True,
            doc = "Output filename, e.g. 'binding_convert.amesh.go'. " +
                  "File is declared in the rule's package.",
        ),
        "proto_file": attr.string(
            doc = "Optional .proto basename (e.g. 'pod.proto') to restrict " +
                  "codegen to a single file inside a multi-srcs proto_library. " +
                  "Required when the proto_library contains >1 annotated .proto " +
                  "so each amesh_proto_convert rule produces exactly one output.",
        ),
        "_plugin": attr.label(
            default = "//tools/protoc-gen-amesh-convert",
            executable = True,
            cfg = "exec",
        ),
        "_protoc": attr.label(
            default = "@com_google_protobuf//:protoc",
            executable = True,
            cfg = "exec",
        ),
    },
)
