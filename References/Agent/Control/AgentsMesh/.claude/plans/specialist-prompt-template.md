# Specialist Agent Prompt Template V2 (Reference Implementation)

Lessons captured from the `skill_registry` reference implementation —
the first service migrated end-to-end on `feat/proto-migration`. Use
this template **verbatim** for the remaining 25 services; the placeholders
in `{curly_braces}` are the per-service variables.

The V1 template (in `proto-migration-runbook.md` §"Specialist Agent
Prompt Template") was authored before the reference implementation
existed. V2 supersedes it for orchestrator dispatch.

---

## Template

```
# Migrate `{service_name}` service to Connect-RPC + protobuf

## Inputs
- service_name: {service_name}                       # e.g. promocode
- rest_handler_paths: {rest_handler_paths}           # backend/internal/api/rest/v1/*{service}*.go
- rust_dto_path: {rust_dto_path}                     # clients/core/crates/types/src/{service}.rs
- rust_api_client_path: {rust_api_client_path}       # clients/core/crates/api-client/src/modules/{service}.rs
- rust_wasm_service_path: {rust_wasm_service_path}   # clients/core/crates/wasm/src/service_{service}.rs
- ts_types_path: {ts_types_path}                     # clients/web/src/lib/api/{service}Types.ts (may not exist)
- ui_call_sites: {ui_call_sites}                     # grep -r "{service}Service" clients/web/src/
- historical_drift_prs: {historical_drift_prs}       # comma-separated PR numbers

## Reference implementation
The skill_registry service is the first to be migrated. **Read those 8 commits
before starting** — they are the closest thing to a working example:

    git log --oneline origin/feat/proto-migration -- proto/extension \
        backend/internal/api/connect/extension \
        clients/core/crates/types/src/extension_proto.rs \
        clients/web/src/lib/api/skillRegistry.ts

When the runbook and the reference diverge, **follow the reference**. The
runbook predates this PR.

## Must read first (in order)
1. .claude/plans/proto-migration-adr.md
2. .claude/plans/proto-naming-conventions.md  — every SHALL rule (especially §2.5 codec)
3. .claude/plans/proto-watch-list.md          — 8 known hazards (especially #5 auth, #6 field accumulation, #8 tag-number drift)
4. .claude/plans/proto-migration-runbook.md   — THIS document
5. .claude/plans/specialist-prompt-template.md (you are here)

## Working environment
You are spawned into an isolated worktree, base reset to origin/feat/proto-migration latest.

    git fetch origin feat/proto-migration
    git checkout -b proto-migration/service-{service_name} origin/feat/proto-migration

## Steps
Execute runbook §1 through §8. Each step's Bazel verification must pass
before proceeding. DO NOT skip §7.1 (round-trip test).

## Hard constraints (UNCHANGED from V1)
- PR target = feat/proto-migration (NEVER main).
- Do NOT merge the PR. Push, wait CI green, return to caller.
- Do NOT delete the existing Gin REST handler. Dual-track.
- Do NOT bump connectrpc.com/connect (locked at v1.19.1).
- Do NOT introduce google.protobuf.Timestamp — use string ISO-8601.
- Do NOT use json_name annotations in .proto.
- Do NOT add `Serialize` / `Deserialize` derives on migrated Rust DTOs.
- Do NOT use `application/json` content-type in any client-side code.
- Do NOT return `JsValue` from `serde_wasm_bindgen::to_value(&resp)`.

## NEW hard constraints (V2)
- **Reuse the org_scope helper.** Every org-scoped handler calls
  `interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)`. Do not
  re-implement the slug→tenant resolution; the helper IS the contract.
- **Run validate_prost_tags.** Every `proto_library(...)` target MUST
  be paired with a `validate_prost_tags(name, proto, rust)` test target.
  Failing to wire this is the single most likely source of the wire
  drift the migration set out to eliminate.
- **Generate the TS message classes.** Run
  `pnpm proto:gen-ts` after editing the .proto. Commit the output under
  `proto/gen/ts/{service}/v1/{service}_pb.ts`. Do not import from
  hand-authored TS for migrated services.
- **Keep adapters in `clients/web/src/lib/api/{service}.ts`.** Map
  proto camelCase + BigInt → web snake_case + number inside the
  adapter so call-sites don't need to change. Diverging the web type
  surface across all 26 services in one PR is out of scope.

## Done means
- All Bazel targets green: //proto/{service_name}/...,
  //backend/internal/api/connect/{service_name}/..., //backend/cmd/server:server,
  //clients/core/..., //clients/web:unit, //clients/web:lint,
  //clients/web:src, //tools/validate_prost_tags:validate_prost_tags_smoke,
  //proto/{service_name}/v1:{service_name}_validate.
- PR open against feat/proto-migration with the body template from
  runbook §8.2 filled in.
- CI green on the PR.
- Round-trip test exists for every response message.
- Three-way drift diff (runbook §1.5) is in the PR description.
- New e2e spec (or augmented existing one) marks the Connect path
  explicitly (see clients/web/e2e-playwright/tests/extensions/skill-registry-wasm-roundtrip.spec.ts
  for the pattern).

## Return when complete
- PR URL
- CI status
- Any deviations from conventions.md you had to make (if none, say "none")
- Any drift you discovered and fixed inline
- Wasm bundle delta (run `ls -la bazel-bin/.../wasm_pkg_bg.wasm` before/after)
```

---

## Per-service variables (filled by orchestrator)

The orchestrator dispatches one specialist agent per row, each running
in its own worktree. Estimated 4-6 hours per service after the reference
implementation. (Reference took ~5 hr including all 10 infra deliverables;
follow-on services do not re-pay the infrastructure cost.)

| Service | service_name | historical_drift_prs |
|---|---|---|
| Pod | pod | #340, 986a38ca6 |
| Promo code | promocode | 986a38ca6 |
| Billing | billing | #334 |
| Ticket | ticket | 986a38ca6 |
| Ticket comments | ticket_comments | 986a38ca6 |
| Channel | channel | — |
| Repository | repository | — |
| Runner | runner | — |
| Autopilot | autopilot | — |
| Mesh | mesh | — |
| Binding | binding | — |
| Invitation | invitation | — |
| Notification | notification | — |
| File | file | — |
| Support ticket | support_ticket | — |
| API key | apikey | #345 |
| User credential | user_credential | #329 (RepositoryProvider) |
| Grant | grant | — |
| SSO | sso | — |
| Token usage | token_usage | — |
| Blockstore | blockstore | — |
| Message | message | — |
| Loop | loop | — |
| Agent | agent | — |
| User | user | — |
| Org | org | — |

(26 services — `extension` was the reference, leaving 25 for the
parallel dispatch.)

---

## Decisions made by the reference implementation (carry forward)

These are decisions the reference resolved that subsequent specialists
should **not** re-litigate:

### TS proto codegen path — **committed mirror via `pnpm proto:gen-ts`**

The Bazel-native `ts_proto_library` macro is deferred to a follow-up
infra PR. Until it lands, every per-service PR commits the generated
`proto/gen/ts/{service}/v1/{service}_pb.ts` into the source tree. The
runbook §"TS proto codegen toolchain" describes the Bazel-macro endgame;
ignore it for now.

The Bazel macro is **non-trivial** to implement correctly — wiring
`@bufbuild/buf` through `js_run_binary` with descriptor sets, handling
output path normalization, generating the per-service ` _pb.ts` plus
the optional `_connect.ts`. Estimate 6-8 hrs of focused work, larger
than a single specialist's slot. The follow-up infra PR can land it as
a sweep across all 26 services once they are migrated.

### TS path alias — **`@proto/*` → `proto/gen/ts/*`**

Set in both `clients/web/tsconfig.json` (for tsc / Next.js / IDE) and
`clients/web/vitest.config.ts` (Vite uses its own resolver). Specialist
agents inherit; no per-service adjustment needed.

### `validate_prost_tags` impl language — **Python regex**

Not Rust syn, not protoc-based. The script lives at
`tools/validate_prost_tags/validate_prost_tags.py` and is invoked via a
thin sh_binary. Total ~200 LoC, zero pip deps, zero new Bazel
toolchains. Specialist agents do not modify the validator — they only
pair their service's `.proto` and Rust `*_proto.rs` via
`validate_prost_tags(name, proto, rust)` in the per-service
`BUILD.bazel`.

### Rust DTO file naming — **`{service}_proto.rs`**

`clients/core/crates/types/src/extension_proto.rs` is the reference.
Keep the legacy `clients/core/crates/types/src/extension.rs` (serde
types, REST path) untouched during the migration window. The two files
coexist under separate `pub mod` re-exports in `types/src/lib.rs`:

    pub use extension::*;            // legacy serde types
    pub mod proto_extension_v1 {     // prost types
        pub use super::extension_proto::*;
    }

This keeps the dual-track separation visible at the type-name level.

### Backend Connect handler layout

`backend/internal/api/connect/{service}/` with two files:

- `{service}.go` — RPCs + `Mount(mux, srv, opts...)`
- `{service}_convert.go` — domain ↔ proto field translation

Splitting `_convert.go` out keeps each file under the 200-line limit
(CLAUDE.md hard rule). The reference's `skill_registry.go` is 230 lines
and `skill_registry_convert.go` is 85 lines — split was necessary.

### `requireOrgAdmin` reuse

For services where the REST handler had an admin check (extension,
promocode, …), copy the `requireOrgAdmin(ctx)` helper from the
reference and call it after `ResolveOrgScope` in every method. Don't
re-implement role-checking — `tenant.UserRole` is the contract.

---

## Pitfalls the reference hit (avoid on follow-on services)

### Pitfall 1: `ResolveOrgScope` generic signature

Go generics can't reach through `*connect.Request[T]` to constrain
`GetOrgSlug()` on `*T`. **Pass `req.Msg` (the raw `*T`)** directly:

    ResolveOrgScope(ctx, req.Msg, s.orgSvc)

Not `ResolveOrgScope(ctx, req, s.orgSvc)`. The reference experimented
with the generic-constraint form and abandoned it.

### Pitfall 2: protoc-gen-es output path

`buf generate` with `directory: proto/{service}/v1` strips the path
prefix and dumps into `proto/gen/ts/`. Use `directory: proto` with
`excludes: ["proto/runner", "proto/gen"]` instead — that preserves the
`extension/v1/` subdirectory. The reference's `buf.yaml` is the working
shape.

### Pitfall 3: ApiError needs a new variant

`prost::Message::decode` errors don't map to `serde_json::Error`. The
reference added `ApiError::Decode(String)` plus a `ServiceError::InvalidJson`
projection. **You do not need to repeat this** — the variant is in
place. Just use `connect_call(...)` from `api-client`.

### Pitfall 4: Bazel test rule `_test` suffix

Native `rule(test = True)` enforces a `_test` suffix on the rule name.
The reference's `validate_prost_tags` macro wraps an internal
`_validate_prost_tags_test` rule. **You do not write rules** — you call
`validate_prost_tags(name, proto, rust)` from the per-service BUILD.

### Pitfall 5: Bazel runfiles path resolution

When wrapping a `sh_binary` from a custom rule, `runfiles_root =
${TEST_SRCDIR}/${TEST_WORKSPACE:-_main}` is the path you prepend to
short_path. Plain `$(dirname "$0")` doesn't work — the script lives in
a different runfiles subtree from the binary it invokes. The reference
captures the right pattern in `tools/validate_prost_tags/rule.bzl`.

### Pitfall 6: Stay under 200 / 400 line limits

`CLAUDE.md` is strict. The reference's `extension.rs` already had 240
lines of legacy serde types — adding ~200 lines of prost mirrors
broke the limit, so the prost mirrors moved to `extension_proto.rs`.
**Plan the same split for every service** with a non-trivial legacy
DTO file.

### Pitfall 7: Web SkillRegistry type lives in `@/lib/api`

Don't try to re-type `SkillRegistry` as the proto-generated camelCase
type at every UI call site — that's a 30+ file refactor. Map inside
the adapter (`lib/api/{service}.ts`), return the existing web type
shape. Diverging the type surface is a follow-up cleanup PR.

---

## Cost of the reference implementation

Reference work breakdown (5 hr):

| Deliverable | Hours |
|---|---|
| .proto file + Bazel proto_library/go_proto_library | 0.5 |
| interceptors/org_scope helper + tests | 0.5 |
| Backend Connect handler + convert + tests | 1.0 |
| Rust prost DTOs + api-client connect_call + wasm bridge | 1.5 |
| TS proto codegen tooling (buf.yaml, deps, alias, adapter) | 1.0 |
| validate_prost_tags Bazel rule + smoke test | 0.3 |
| E2E spec augmentation | 0.1 |
| Specialist prompt template V2 (this doc) | 0.1 |

Of these, **5 deliverables (org_scope, connect_call helper, ts_proto
infra, validate_prost_tags rule, adapter pattern) are one-shot
infrastructure**. Subsequent services reuse them — estimated 4 hr per
service, mostly mechanical proto authoring + handler implementation.
