# DevOps Git Closeout 2026-06-05 References Phase 1

Task: `COAGENT-DEVOPS-GIT-CLOSEOUT-20260605`

Scope: main worktree only, path-level Git split for open-source reference projects.

Rules applied:

- no `git add -A`
- no force push
- no `reset --hard`
- no delete/clean of user files
- no direct commit of >100 MB files, credentials, `.venv`, `node_modules`, `bin/cache/runtime` outputs
- use path-limited review and temporary indexes when the real index already has unrelated staged files

Completed batches:

1. `6bebce1e527408002394486dbbb1cacc5d647310`
   - Message: `chore: ignore firecrawl dotnet build outputs`
   - Scope: `.gitignore`
   - Reason: ignore `References/Agent/Gateway/firecrawl/apps/dot-net-sdk/**/bin/` so dotnet test coverage/build output is not submitted.
   - Evidence: previously visible untracked file was `References/Agent/Gateway/firecrawl/apps/dot-net-sdk/Firecrawl.Tests/bin/Debug/net8.0/.msCoverageSourceRootsMapping_Firecrawl.Tests`.

2. `d24fb51d2539c0b341a2288ec273de71edeaf87f`
   - Message: `refs: sync Sunray150 geometry references`
   - Scope:
     - `References/MWORKS/QuadrotorModel/package.mo`
     - `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/sunray150_with_mid360.sdf`
     - `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/sunray150_with_mid360.sdf.jinja`
   - Reason: sync reviewed Sunray150 rotor, camera, and collision geometry into MWORKS and Sunray SDF references.
   - Evidence: text-only files; no secret-pattern hits in reviewed diff; cached diff check passed in a temporary index.

Current known residuals:

- Real index had unrelated staged files before DevOps write work:
  - `Docs/Workflows/debug_mcp.md`
  - `PROGRESS.md`
  - `Results/codex_history_audit/app_history_title_project_fix_20260605-2217_manifest.json`
- `References/Data` has 323 tracked deletes while matching directories exist under ignored `References/Log`. Do not commit bare deletes.
- `References/PX4/mavros-ros2/mavros/test/mavros_py/testdata/missionplanner.parm` appears to be line-ending noise and is deferred.
- `References/Agent/Gateway/daytona` remains partially drained; next suggested batch is grouped small apps under 1000 files.

Next safe batches:

1. Daytona grouped apps: `apps/cli`, `apps/daemon`, `apps/runner`, `apps/daytona-e2e`, `apps/otel-collector`, `apps/proxy`, `apps/snapshot-manager`, `apps/ssh-gateway`, excluding `.env` files.
2. `References/Data -> References/Log` migration pilot: start with `px4_pid_tuner`, then proceed by source-only batches for pyulog/px4tools/data-driven projects.
