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

5. `b820a7d50db818c905f44bf2f719c7fac12f0dc4`
   - Message: `refs: add daytona sdk and small lib slices`
   - Scope:
     - `.gitignore`
     - selected `References/Agent/Gateway/daytona/libs/*` SDK/API client and support packages
   - Reason: drain a reviewed Daytona library slice while keeping dependency folders, build outputs, object folders, caches, and `.env` files ignored.
   - Evidence: 685 staged paths; largest staged file was 52,697 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; forbidden path filters passed.
   - Correction needed: PowerShell did not stop after `git diff --cached --check` reported CRLF/trailing-whitespace warnings for `libs/sdk-java/gradlew.bat`; this commit was local-only at discovery time and must be followed by a narrow fix commit before push.

6. `7933953ef382650e5d6e927fdfcef7583cca47e9`
   - Message: `chore: fix daytona libs git gate evidence`
   - Scope:
     - `References/Agent/Gateway/daytona/libs/sdk-java/gradlew.bat`
     - `Docs/Workflows/agent_orchestration.md`
     - this progress record
   - Reason: fix the Daytona libs batch diff-check anomaly before push and document the reusable PowerShell gate rule.
   - Evidence: follow-up `git diff --check HEAD~1..HEAD` exited with `$LASTEXITCODE=0`; the workflow now requires checking `$LASTEXITCODE` after native Git gate commands before `git write-tree`, `git commit-tree`, or `git update-ref`.

7. `4a998ff3eb572d57fc2c9ef0da694e79847a2a9e`
   - Message: `refs: add daytona toolbox client slices`
   - Scope:
     - `.gitignore`
     - `References/Agent/Gateway/daytona/libs/toolbox-api-client`
     - `References/Agent/Gateway/daytona/libs/toolbox-api-client-go`
     - `References/Agent/Gateway/daytona/libs/toolbox-api-client-java`
     - `References/Agent/Gateway/daytona/libs/toolbox-api-client-python`
     - `References/Agent/Gateway/daytona/libs/toolbox-api-client-python-async`
     - `References/Agent/Gateway/daytona/libs/toolbox-api-client-ruby`
   - Reason: drain another reviewed Daytona library/API client slice while keeping dependency folders, generated build outputs, object folders, caches, and `.env` files ignored.
   - Evidence: 839 staged paths; largest staged file was 354,506 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; forbidden path filters passed; `git diff --cached --check` and follow-up `git diff --check HEAD~1..HEAD` both exited with `$LASTEXITCODE=0`.

8. `a4000426964a61923db4ffad89a5c6d5ca46ed56`
   - Message: `refs: add daytona api client slices`
   - Scope:
     - `.gitignore`
     - `References/Agent/Gateway/daytona/libs/api-client`
     - `References/Agent/Gateway/daytona/libs/api-client-go`
     - `References/Agent/Gateway/daytona/libs/api-client-ruby`
   - Reason: drain another reviewed Daytona API client slice while keeping dependency folders, generated build outputs, object folders, caches, and `.env` files ignored.
   - Evidence: 649 staged paths; largest staged file was 401,277 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; forbidden path filters passed; `git diff --cached --check` and follow-up `git diff --check HEAD~1..HEAD` both exited with `$LASTEXITCODE=0`.

9. `9eb96d0414ee2c49e28bb4d1f15350233027ce4b`
   - Message: `refs: add daytona generated api client slices`
   - Scope:
     - `.gitignore`
     - `References/Agent/Gateway/daytona/libs/api-client-java`
     - `References/Agent/Gateway/daytona/libs/api-client-python`
     - `References/Agent/Gateway/daytona/libs/api-client-python-async`
   - Reason: drain the remaining reviewed Daytona generated API client language packages while keeping dependency folders, generated build outputs, object folders, caches, and `.env` files ignored.
   - Evidence: 876 staged paths; largest staged file was 850,148 bytes; one Gradle wrapper `.jar` was 43,453 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; forbidden path filters passed; `git diff --cached --check` and follow-up `git diff --check HEAD~1..HEAD` both exited with `$LASTEXITCODE=0`.

10. `e4af598759b498acf2a01e25deb815071b9a3c18`
    - Message: `refs: add daytona examples and guides`
    - Scope:
      - `.gitignore`
      - `References/Agent/Gateway/daytona/examples`
      - `References/Agent/Gateway/daytona/guides`
    - Reason: drain Daytona examples and guide content while keeping dependency folders, build outputs, caches, and `.env` files ignored.
    - Evidence: 301 staged paths; largest staged file was 252,461 bytes; Gradle wrapper `.jar` files were 43,583 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; forbidden path filters passed; two Java example `gradlew.bat` files were normalized to LF after diff-check caught CRLF/trailing-whitespace warnings; follow-up `git diff --check HEAD~1..HEAD` exited with `$LASTEXITCODE=0`.

11. `a3cba6c3be0d2a0c47ebac090ec82a510cd6ca70`
    - Message: `refs: migrate px4 pid tuner logs`
    - Scope:
      - `.gitignore`
      - `References/Data/px4_pid_tuner`
      - `References/Log/px4_pid_tuner`
    - Reason: start the `References/Data -> References/Log` migration as a paired rename batch instead of committing bare tracked deletes.
    - Evidence: 4 `References/Data/px4_pid_tuner` tracked deletes matched 4 `References/Log/px4_pid_tuner` files; max file size was 34,465 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; `git show --summary --name-status --find-renames` reports four `R100` renames; follow-up `git diff --check HEAD~1..HEAD` exited with `$LASTEXITCODE=0`; remaining `References/Data` tracked deletes dropped from 323 to 319.

12. `7483009f1fcd08c78e71ec7dbeaee77181f87be7`
    - Message: `refs: migrate pyulog source logs`
    - Scope:
      - `.gitignore`
      - `References/Data/pyulog`
      - `References/Log/pyulog`
    - Reason: continue `References/Data -> References/Log` migration with a source-only pyulog batch while excluding `.ulg` log samples.
    - Evidence: 50 non-`.ulg` Data deletes matched 50 Log files; max staged file was 62,892 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; `.ulg` files were excluded by path list and `.gitignore`; `git show --summary --name-status --find-renames` reports `R100` renames for the source/doc/config files; follow-up `git diff --check HEAD~1..HEAD` exited with `$LASTEXITCODE=0`; remaining `References/Data` tracked deletes dropped from 319 to 269, with 6 pyulog `.ulg` deletes intentionally left open for manifest-only or explicit data policy.

13. `bf32f1a1073196cb4e019b91d373f1a1700e7032`
    - Message: `refs: migrate px4tools source logs`
    - Scope:
      - `.gitignore`
      - `References/Data/px4tools`
      - `References/Log/px4tools`
    - Reason: continue `References/Data -> References/Log` migration with a source-only px4tools batch while excluding CSV, ULG, and PX4LOG data files.
    - Evidence: 42 non-data Data deletes matched 42 Log files; max staged file was 734,707 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; `.csv`, `.ulg`, and `.px4log` files were excluded by path list and `.gitignore`; `git show --summary --name-status --find-renames` reports `R100` renames for the source/doc/config/notebook files; follow-up `git diff --check HEAD~1..HEAD` exited with `$LASTEXITCODE=0`; remaining `References/Data` tracked deletes dropped from 269 to 227, with 5 px4tools data-file deletes intentionally left open for manifest-only or explicit data policy.

14. `18d856b3356356e4d0bb870483ceb7b559871508`
    - Message: `refs: migrate airo control source logs`
    - Scope:
      - `.gitignore`
      - `References/Data/airo_control_interface`
      - `References/Log/airo_control_interface`
    - Reason: continue `References/Data -> References/Log` migration with a source/config/media-only airo control batch while excluding object/shared-library build products.
    - Evidence: 62 non-binary Data deletes matched 62 Log files; max staged file was 310,386 bytes; no high-confidence credential pattern hits; no nested `.git` hits; no LFS pointer hits; `.o` and `.so` files were excluded by path list and `.gitignore`; `git show --summary --name-status --find-renames` reports `R100` renames for the source/config/media files; follow-up `git diff --check HEAD~1..HEAD` exited with `$LASTEXITCODE=0`; remaining `References/Data` tracked deletes dropped from 227 to 165, with 13 airo `.o/.so` binary deletes intentionally left open for manifest-only or explicit binary policy.

Current known residuals:

- Real index had unrelated staged files before DevOps write work:
  - `Docs/Workflows/debug_mcp.md`
  - `PROGRESS.md`
  - `Results/codex_history_audit/app_history_title_project_fix_20260605-2217_manifest.json`
- `References/Data` has 323 tracked deletes while matching directories exist under ignored `References/Log`. Do not commit bare deletes.
- `References/PX4/mavros-ros2/mavros/test/mavros_py/testdata/missionplanner.parm` appears to be line-ending noise and is deferred.
- `References/Agent/Gateway/daytona` remains partially drained; next suggested batch is grouped small apps under 1000 files.
- `git diff --cached --check` must be treated as failed when `$LASTEXITCODE` is nonzero under PowerShell; this rule was added to `Docs/Workflows/agent_orchestration.md` after the Daytona libs gate anomaly and verified in commit `7933953ef382650e5d6e927fdfcef7583cca47e9`.

Next safe batches:

1. Daytona examples/guides or any remaining root/library slices, each kept under 1000 paths.
2. Continue `References/Data -> References/Log` migration by paired rename/source-only batches for pyulog/px4tools/data-driven projects; do not commit remaining tracked deletes naked.
3. `References/Blender/**` remains a temporary throttle and must not be removed wholesale; if needed, open only README/LICENSE/source slices after size and generated-artifact scans.

## 2026-06-06 DevOps visible closeout continuation

15. `dc95f30eb12fb28c6df285dd7271c4dc951629c8`
    - Message: `docs: record airo control source migration`
    - Scope:
      - `Results/codex_history_audit/devops_git_closeout_20260605_refs_phase1.md`
    - Reason: persist the airo source/config/media migration evidence before continuing the next Git split slices.
    - Evidence: committed with a temporary index so the real staged area preserved unrelated staged files (`Docs/Workflows/debug_mcp.md`, `PROGRESS.md`, and `Results/codex_history_audit/app_history_title_project_fix_20260605-2217_manifest.json`); `git diff --cached --check` exited with `$LASTEXITCODE=0`; pushed to `origin/main`.

16. `4920e84db0551baa1fb5d73f48364dff94839cde`
    - Message: `refs: migrate esc test logs`
    - Scope:
      - `References/Data/esc_test`
      - `References/Log/esc_test`
    - Reason: complete another paired `References/Data -> References/Log` migration batch instead of leaving old-location tracked deletes.
    - Evidence: 27 paths; no file >=100 MB; no high-confidence credential pattern hits; no nested runtime directory hits; `git diff --cached --check` exited with `$LASTEXITCODE=0`; path-limited status for the old/new esc_test locations was clean after commit.

17. `b73a5fdf491e8ffd0e6d0ef10bd1ec496653a088`
    - Message: `refs: migrate data-driven system identification logs`
    - Scope:
      - `References/Data/data-driven-system-identification`
      - `References/Log/data-driven-system-identification`
    - Reason: move the data-driven system identification reference project as a paired path-limited batch. User policy is single-file GitHub limit first: file categories such as `.ulg`, notebook, or small data files are not excluded merely because the folder is large.
    - Evidence: 29 paths; no file >=100 MB; no high-confidence credential pattern hits; no nested runtime directory hits; `git diff --cached --check` exited with `$LASTEXITCODE=0`; path-limited status for the old/new locations was clean after commit.

18. `f8b18917d0dff6811a351400711747bf6f9e512f`
    - Message: `refs: migrate data-driven dynamics logs`
    - Scope:
      - `References/Data/data-driven-dynamics`
      - `References/Log/data-driven-dynamics`
    - Reason: move the data-driven dynamics reference project as a paired path-limited batch. Small `.csv`, `.ulg`, and `.stl` reference assets were admitted because no single file exceeded 100 MB and no secret pattern was found.
    - Evidence: 85 paths; no file >=100 MB; no high-confidence credential pattern hits; no nested runtime directory hits; `git diff --cached --check` exited with `$LASTEXITCODE=0`; path-limited status for the old/new locations was clean after commit.

19. `07177560750c46ded2715df4967f8c0354f2a90f`
    - Message: `refs: remove old data artifact locations`
    - Scope:
      - `References/Data/airo_control_interface`
      - `References/Data/px4tools`
      - `References/Data/pyulog`
    - Reason: remove the remaining old `References/Data` tracked artifact/sample paths after their source batches were migrated. Log-side generated objects and log samples remain ignored rather than force-added.
    - Evidence: 24 paths; all remaining `References/Data` tracked deletes dropped to 0; `git diff --cached --check` exited with `$LASTEXITCODE=0`; pushed to `origin/main`.

Current continuation state:

- `References/Data` path-limited tracked deletes are now 0.
- `References/Log` has no visible path-limited status after the migration batches.
- Real index still preserves unrelated staged files:
  - `Docs/Workflows/debug_mcp.md`
  - `PROGRESS.md`
  - `Results/codex_history_audit/app_history_title_project_fix_20260605-2217_manifest.json`
- `Docs/Skills/Unreal` has four tracked `.venv` path changes plus untracked wrapper/skill files. Treat the `.venv` entries as environment cleanup and the wrapper/skill files as a separate source/docs batch.
- `Docs/Skills/Windows-MCP` has untracked wrapper files; its ignored `.venv`, `__pycache__`, and `*.egg-info` content should stay ignored.
- `References/Agent` still contains hundreds of thousands of ignored files. Do not remove its broad throttle; continue by sub-project unignore/stage batches under 1000 files.
- `References/Blender/**` remains a temporary throttle at the end of `.gitignore`. Do not remove it wholesale; narrow only after per-subtree inventory because `tests/` and `release/` would expose 1000+ files.

## Review cache rule for this Git closeout

Do not repeat full gates for batches already reviewed and committed in this
record unless their path status changes again. Treat the following as reviewed
checkpoint evidence:

- Each listed commit was created with a temporary index, path-limited staging,
  a sub-1000 path count, `$LASTEXITCODE`-checked `git diff --cached --check`,
  and a normal push when the branch was ahead of `origin/main`.
- The reviewed scope is exactly the paths recorded under each commit. Do not
  generalize a clean gate for one slice to a broad parent tree such as
  `References/Agent`, `References/Blender`, `Results/unreal_scene_mapping`, or
  `UE5`.
- For already-reviewed commits, future DevOps passes should only re-check if
  `git status --short -- <recorded-path>` shows a new change, if an ignored
  throttle is being narrowed for that path, or if a push/remote sync check
  contradicts the recorded commit.
- If a path is still only hidden by a temporary throttle, it is not complete.
  Review caching applies to committed slices, not to ignored backlog.

This rule was added after the user correction: reviewed work must be written
into project evidence so future DevOps passes do not burn time repeating the
same checks.
