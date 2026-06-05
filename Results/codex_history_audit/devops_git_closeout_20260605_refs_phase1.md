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

3. `f67db02745d029a9b5098ff79fd743a529a185c3`
   - Message: `refs: add daytona app runtime slices`
   - Scope:
     - `.gitignore`
     - `References/Agent/Gateway/daytona/apps/cli`
     - `References/Agent/Gateway/daytona/apps/daemon`
     - `References/Agent/Gateway/daytona/apps/runner`
     - `References/Agent/Gateway/daytona/apps/daytona-e2e`
     - `References/Agent/Gateway/daytona/apps/otel-collector`
     - `References/Agent/Gateway/daytona/apps/proxy`
     - `References/Agent/Gateway/daytona/apps/snapshot-manager`
     - `References/Agent/Gateway/daytona/apps/ssh-gateway`
   - Reason: drain the next reviewed Daytona application slice while keeping `.env` files and generated/runtime directories ignored.
   - Evidence: 519 staged paths; largest staged file was 162,922 bytes; no nested `.git` hits; no LFS pointer hits; `.env`, `node_modules`, `bin`, `build`, and `dist` were excluded; cached diff check passed in a temporary index.
   - Notes: real index was cleaned back to the pre-existing unrelated staged files after the temporary-index commit.

4. `12828b8681a39cb5dc5e2b71604716cc3acde8b2`
   - Message: `refs: add daytona dashboard and docs slices`
   - Scope:
     - `.gitignore`
     - `References/Agent/Gateway/daytona/apps/dashboard`
     - `References/Agent/Gateway/daytona/apps/docs`
   - Reason: drain the next Daytona UI/docs slice while keeping app `.env`, generated static output, dependency folders, and cache/runtime outputs ignored.
   - Evidence: 965 staged paths; largest staged file was 8,326,623 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; forbidden path filters for `.env`, `node_modules`, `bin`, `build`, `dist`, `.next`, `.cache`, and `.turbo` passed; cached diff check passed in a temporary index.
   - Notes: commit parent was `1ab64fa63d6653a587e39fd523d4d275d1681aae`, which was already `origin/main`; this DevOps commit did not overwrite the concurrently pushed upstream commit.

Current known residuals:

- Real index had unrelated staged files before DevOps write work:
  - `Docs/Workflows/debug_mcp.md`
  - `PROGRESS.md`
  - `Results/codex_history_audit/app_history_title_project_fix_20260605-2217_manifest.json`
- `References/Data` has 323 tracked deletes while matching directories exist under ignored `References/Log`. Do not commit bare deletes.
- `References/PX4/mavros-ros2/mavros/test/mavros_py/testdata/missionplanner.parm` appears to be line-ending noise and is deferred.
- `References/Agent/Gateway/daytona` remains partially drained; next suggested batch is grouped small apps under 1000 files.

Next safe batches:

1. Daytona examples/guides or libs split by package family, each kept under 1000 paths.
2. `References/Data -> References/Log` migration pilot: start with `px4_pid_tuner`, then proceed by source-only batches for pyulog/px4tools/data-driven projects.
3. `References/Blender/**` remains a temporary throttle and must not be removed wholesale; if needed, open only README/LICENSE/source slices after size and generated-artifact scans.
