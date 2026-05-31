# 2026-05-24 — convert.go codegen (Phase 12)

## Context

After Phase 6 lifted `protoconv` helpers out of every connect handler's
`convert.go`, ~1741 LOC of hand-written `domain ↔ wire` mapping still lived
across 18 backend connect packages. Each `convert.go`:

* mechanically mirrors fields between a domain struct (GORM) and a proto
  message
* wraps non-trivial bridges (`time.Time → string`, `pq.StringArray →
  []string`, `int → int32`) via `protoconv` helpers
* leaves no programmatic contract — schema drift between proto and domain
  surfaces only at runtime ("field renamed but convert.go still maps the
  old name").

`/arch_check` flagged this as P2: mechanical, but the error class is
"silent wire-domain drift" which `bazel test` does not catch.

## Decision

Generate `<message>_convert.amesh.go` from the .proto schema using a
custom protoc plugin. proto is the wire SSOT; codegen reads
`(amesh.codegen.v1.go_domain)` message option + per-field `field_convert`
to emit `ToProto<Message>` / `FromProto<Message>` functions.

### Mechanism / Policy split

| Layer | Owner | Examples |
|---|---|---|
| **Mechanism** — Phase 6 `protoconv` | shared, public helper | `RFC3339`, `StringPtr`, `IntToInt32`, `StringSlice` |
| **Policy** — Phase 12 codegen | annotation in `.proto` | `field_convert = "rfc3339_ptr"` |
| **Exception** — hand-written `*_convert_custom.go` | per-domain | enum maps, derived fields, nested struct walks |

Annotation schema lives in `proto/codegen/v1/options.proto` (extension
fields on `MessageOptions`, `FieldOptions`, and `FileOptions`). Plugin
binary at `tools/protoc-gen-amesh-convert/`.

### Output location

Convert files land **in the backend connect handler tree**, not next to
the .pb.go. Required by Go's internal-package rule: the generated
function references `backend/internal/domain/<x>`, and proto/gen/go
packages cannot reach into `backend/internal/`.

File-level annotation:

```proto
option (amesh.codegen.v1.convert_target) = {
  output_dir: "backend/internal/api/connect/binding"
  output_package: "bindingconnect"
};
```

`protoconv` was relocated from `backend/internal/api/connect/internal/protoconv`
to `backend/pkg/protoconv` so the generated handler-side file can import it
without crossing an internal boundary.

### Build pipeline

```
proto/<svc>/v1/<file>.proto
        │
        ├── go_proto_library                        → bazel-bin/.../<file>.pb.go
        │   (//proto/<svc>/v1:<svc>_go_proto)
        │
        └── amesh_proto_convert                     → bazel-bin/backend/internal/api/connect/<svc>/<base>_convert.amesh.go
            (build_defs/protoconv/defs.bzl)           (consumed by handler go_library srcs;
                                                       NEVER lands in source tree —
                                                       .gitignore enforces this)
```

Generated `.amesh.go` files live only under `bazel-bin/`. The
`amesh_proto_convert` Bazel rule calls `@com_google_protobuf//:protoc` with
our plugin (`--amesh-convert_opt=flat=1`), declares the output file at
rule-evaluation time, and hands it to downstream `go_library` srcs as a
generated source. IDE workflows (gopls, golangci-lint) read the generated
files from `bazel-bin/` after a `bazel build`.

For multi-source `proto_library` targets (e.g., `proto/pod/v1` carries
both `pod.proto` and `agentpod_settings.proto`), the rule accepts a
`proto_file = "pod.proto"` attr to restrict codegen to one .proto per
invocation — Bazel requires output declarations to be statically
predictable, so N annotated protos in one `proto_library` → N
`amesh_proto_convert` rules.

### Annotation surface

Message-level:
* `(amesh.codegen.v1.go_domain) = { type: "...PodBinding" }` — required.
* `generate_to_proto`, `generate_from_proto` — default both on.

Field-level (all under `extend google.protobuf.FieldOptions`):
* `field_rename` — domain field name differs from proto Go-cased name
  (`org_id` → `OrganizationID`).
* `field_convert` — protoconv helper key (`rfc3339`, `rfc3339_ptr`,
  `rfc3339_nano`, `rfc3339_nano_ptr`, `string_ptr`, `string_slice_cast`,
  `int_to_int32`, `int_to_int64`, `int_ptr_to_int32`,
  `int_ptr_to_int64`).
* `field_skip` — omit from generated code.
* `field_custom` — call a hand-written helper in a sibling
  `_convert_custom.go` (the inverse direction's name is auto-derived by
  flipping the `ToProto`/`FromProto` suffix).

File-level:
* `(amesh.codegen.v1.convert_target) = { output_dir, output_package }`
  — required for every file that has at least one annotated message.

## Status (Phase 12 complete)

- **M1 schema** ✅ `proto/codegen/v1/options.proto` (5 field options + 1
  file option + 1 message option).
- **M2 plugin MVP** ✅ reads message option via typed extension API.
- **M3 type mapping** ✅ 10 conversion kinds (time/nullable/slice/int) +
  `protoconv` relocated to `backend/pkg/protoconv` + file-level
  `ConvertTarget` annotation to redirect output into backend connect
  handler tree.
- **M4 exceptions + errors** ✅ `field_skip` / `field_custom` (with
  auto `ToProto` ↔ `FromProto` suffix flip) / hard error on unknown
  `field_convert` kind with proto-message context.
- **M5 Bazel macro** ✅ COMPLETE. `build_defs/protoconv/defs.bzl`
  defines `amesh_proto_convert(name, proto, output, proto_file=None)`.
  Plugin accepts `flat=1` opt to emit a single-basename file under
  protoc's `out` (Bazel controls placement). 17/17 migrated domains use
  this macro; no committed `*_convert.amesh.go` in source tree
  (`.gitignore` rule enforces).
- **M6 PodBinding pilot** ✅ end-to-end. Generated convert produced
  byte-identical output to the hand-written version. All 17 binding
  tests pass.
- **M7 17-domain migration** ✅ COMPLETE. ~1830 LOC net handwritten
  reduction in source tree. All 27 connect handler tests pass; full
  `bazel test //backend/...` green (110/110).

  Each migrated handler now contains:
  * `<svc>_convert_custom.go` — only the `field_custom` helpers that
    the plugin can't synthesise (enum maps, nested struct walks,
    multi-source composites).
  * No more `convert.go` alias wrappers — call sites use the generated
    `ToProtoX` / `FromProtoX` names directly.
  * `BUILD.bazel` declares one `amesh_proto_convert` per annotated
    `.proto` (uses `proto_file = "..."` when the proto_library has
    multiple sources).

- **M8 exceptions** ✅ documented.
  - `admin/sso`: reverse proto-request → service-request mapping. Direction
    opposite to every other ToProto/FromProto pair; only one of its kind
    in the codebase. Stays hand-written.
  - `blockstore`: uses RFC3339Nano precision for audit-grade timestamp
    round-trip. Could be migrated via `field_convert = "rfc3339_nano"`,
    deferred for now because blockstore is a single-domain outlier where
    the conservative audit-precision policy is easier to read at the call
    site than as an annotation. May revisit if a second Nano-precision
    domain emerges.

## Consequences

* The wire-domain drift bug class moves from runtime to **compile time**.
  Adding a proto field without updating the domain struct → codegen
  emits an assignment that references a missing Go field → compile error.
  Adding a domain field without updating the proto → the field stays
  absent from wire (silent omission), but `bazel build` still passes;
  drift in this direction is the residual risk.
* `convert.go` files shrink to ~3 lines (thin aliases preserving
  in-package call-site names). Where complex defaulting was required
  (empty-shape on nil, post-decryption shells, etc.), the alias preserves
  it explicitly.
* The plugin is the new owner of "how do we wire `time.Time` to the
  RFC3339 wire format"; updating that rule means editing
  `tools/protoc-gen-amesh-convert/main.go::protoconvFuncName` and
  `backend/pkg/protoconv/*.go` once, not 18 times.
* `backend/pkg/protoconv` is now public (was `backend/internal/...`).
  This was necessary so `proto/gen/go` packages — which generate Go
  bindings outside `backend/internal/` — can import the helpers. The
  package surface is small (~10 functions) and stable, so the exposure
  cost is acceptable.
* Two exception domains (blockstore, admin/sso) remain hand-written.
  Each is a one-off shape; adding codegen knobs for either would cost
  more in plugin complexity than it saves in LOC.
