# AgentsMesh iOS

SwiftUI + TCA app, Rust core via UniFFI, fully built by Bazel.

## Build

```bash
bazel build //clients/core/crates/ffi:AgentsMeshCore   # Rust → XCFramework
bazel build //clients/ios:AgentsMesh                   # signed .ipa
```

## Run on Simulator

```bash
bazel run //clients/ios:AgentsMesh_sim                 # install + launch on booted sim
```

If no simulator is booted, the runner auto-boots iPhone 17 Pro. The wrapper
unzips the `.ipa`, calls `simctl install` + `simctl launch`, then opens
Simulator.app.

## Develop in Xcode

```bash
bazel run //clients/ios:AgentsMesh_xcodeproj           # generate AgentsMesh.xcodeproj
open AgentsMesh.xcodeproj
```

The project is regenerable — never commit the `.xcodeproj`.

## Layout

| Path | Purpose |
|------|---------|
| `App/` | `@main` entry + `Info.plist` |
| `Packages/AgentsMeshCore/` | Swift facade over the Rust XCFramework (CoreBridge singleton, KeychainStorage, EventStream, PodOutputDispatcher) |
| `Packages/AgentsMeshFeatures/Sources/AppFeature/` | Root reducer + 5-tab dashboard + drawer overlay |
| `Packages/AgentsMeshFeatures/Sources/AuthFeature/` | Login + `CoreClient` (TCA `DependencyKey` wrapping the FFI) |
| `Packages/AgentsMeshFeatures/Sources/WorkspaceFeature/` | Pods list/grid/create-sheet |
| `Packages/AgentsMeshFeatures/Sources/TerminalFeature/` | SwiftTerm + Relay WebSocket client |
| `Packages/AgentsMeshFeatures/Sources/ChannelsFeature/` | Channel list + detail (8 message bubble variants) |
| `Packages/AgentsMeshFeatures/Sources/TicketsFeature/` | List + Kanban board + detail |
| `Packages/AgentsMeshFeatures/Sources/BlocksFeature/` | Page tree + block detail |
| `Packages/AgentsMeshFeatures/Sources/MoreFeature/` | More-tab sheet (feature grid) |
| `Packages/AgentsMeshFeatures/Sources/OrgDrawerFeature/` | Left-edge drawer (rail + account + menu) |
| `Packages/AgentsMeshFeatures/Sources/DesignSystem/` | Tokens + atomic components (Avatar, Chip, ListCell, …) |

## Build pipeline

```
//clients/ios:AgentsMesh                       (ios_application)
  └─ //clients/ios/App:AgentsMesh_entry        (swift_library, @main)
       ├─ //clients/ios/Packages/AgentsMeshCore  (Swift facade)
       │    └─ //clients/core/crates/ffi:AgentsMeshCore_cc  (CcInfo)
       │         └─ //clients/core/crates/ffi:AgentsMeshCore  (rust_xcframework macro)
       │              ├─ rust_static_library  [3 iOS triples via platform_transition]
       │              └─ uniffi-bindgen → Swift glue + .h + .modulemap
       │
       └─ //clients/ios/Packages/AgentsMeshFeatures/Sources/AppFeature
            └─ {Auth, Workspace, Terminal, Channels, Tickets, Blocks, More, OrgDrawer, DesignSystem}
```

Macros live in `build_defs/ios/`:
- `ios_product.bzl` — `ios_app()` produces app + sim runner + xcodeproj
- `rust_xcframework.bzl` — Rust → XCFramework pipeline
- `swift_clang_module.bzl` — wraps `.h`/`.modulemap`/`.a` into `CcInfo` so `swift_library` can link Rust
- `xcframework_assemble.bzl` — assembles the final `.xcframework` tree
- `sim_runner.sh` — wrapper used by `:_sim` to install + launch on a booted simulator

## CI

`.github/workflows/bazel.yml` `ios-xcframework` job:
1. Builds `//clients/core/crates/ffi:AgentsMeshCore` + Swift glue
2. Builds `//clients/ios:AgentsMesh` (full app)
3. Uploads `dist/AgentsMeshCore-xcframework.zip` as artifact

Runs on `macos-14`, requires Xcode 15+.

## Connect to local dev backend

The default `AGENTSMESH_API_URL` in `App/Info.plist` is `http://localhost:25350`
(the worktree-local `deploy/dev` backend). Replace with your environment's URL
for staging/production. Test creds for the local stack:
`dev@agentsmesh.local` / `devpass123`.
