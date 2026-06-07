# COAGENT-DEVOPS-GIT-REFERENCES-SKILLS-CLOSEOUT-20260606 stage 20260607-c

Status: running

Scope: `References` and `Docs/Skills`, path-limited Git drain.

Pushed batches this stage:

- `c28a2b54cb` `devops: add sdk typescript reference subset` - 675 files.
- `84b2a2fe8b` `devops: add plandex reference subset` - 577 files.
- `07a4b6bc3f` `devops: add superagi reference subset` - 604 files.
- `14fb1dbb26` `devops: add playwright mcp gateway tail` - 28 files.
- `725c4521d8` `devops: add openai cookbook image assets` - 381 files.
- `eb387dd7f8` `devops: add openai cookbook examples subset` - 733 files.
- `6f871481c5` `devops: add openai cookbook partners voice examples` - 474 files.
- `c55ab487a8` `devops: add openai cookbook data subset` - 261 files.
- `5b2a8c7f79` `devops: add openai cookbook sample clothes part 1` - 600 files.
- `14eb33de44` `devops: add openai cookbook sample clothes part 2` - 402 files.
- `4c3520e54e` `devops: add codex platform reference subset` - 337 files.
- `6a8c03067a` `devops: add openai agents python core docs tests` - 958 files.
- `cc65d0be32` `devops: add haystack framework reference subset` - 621 files.
- `4616b8bdb9` `devops: add dify workflow toolchain subset` - 530 files.
- `7d7e8e46f1` `devops: add mastra small framework modules` - 659 files.
- `ec02d80cc3` `devops: add aisoc small security ops subset` - 439 files.
- `a0107c0198` `devops: add small agent reference tail` - 13 files.
- `95fff98aa8` `devops: add gateway residual clean tail` - 14 files.

Checks:

- Each submitted batch stayed under 1000 staged files.
- Each submitted batch passed `git diff --cached --check`.
- No submitted batch had a staged file at or above 100 MB.
- Each submitted batch was pushed to `main`.
- Closeout probe: cached index `0`, `.git/index.lock` absent, upstream ahead/behind `0 0`.
- `openai-cookbook/examples/data` has 8 remaining ignored CSV data files, all deferred because the upstream third-party files fail the whitespace gate; they are recorded in `Results/agent_runtime/openai_cookbook_data_nonsample_diffcheck_failed_paths_20260607.txt`.
- GitHub accepted the pushed batches but warned about two files above the 50 MB recommendation and below the 100 MB hard limit: `recommendations_embeddings_cache.pkl` at 53.54 MB and `sample_styles_with_embeddings.csv` at 65.78 MB.
- `Docs/Skills` source-tail probe found no remaining source/docs batch under `Blender-MCP/src`, `Windows-MCP/src`, or `ROS-MCP/ros_mcp`; the 107 candidate files were generated `__pycache__` or `*.egg-info` output and were unstaged.
- A read-only explorer recommended next safe slices: `openai-agents-python`, `haystack`, `dify` toolchain subset, `mastra` small modules, and `AiSOC` operations/plugins subset.

Deferred:

- Third-party upstream whitespace-gate files are recorded under `Results/agent_runtime/*diffcheck_failed*20260607.txt`.
- Local config fixtures, generated outputs, dependency folders, missing-object assets, pointer-only assets, and very large UE/AirSim content remain excluded from normal Git batches.
- `Docs/Skills` remaining ignored inventories are mostly local environments, generated UE intermediate files, or missing-object asset pointers.
- `openai-cookbook/examples/voice_solutions/one_way_translation_using_realtime_api/src/lib/wavtools/dist/` remains skipped as generated dist output.
- `References/Agent/Platforms/codex/codex-rs` remains deferred for later Rust sub-slices; 29 non-Rust codex files that failed the whitespace gate are recorded in `Results/agent_runtime/codex_platform_non_rust_diffcheck_failed_paths_20260607.txt`.
- `References/Agent/Frameworks/openai-agents-python/src/agents/extensions/memory/encrypt_session.py` remains deferred because the upstream file fails the whitespace gate.
- `References/Agent/Workflow/dify` has 27 deferred third-party files recorded in `Results/agent_runtime/dify_toolchain_subset_diffcheck_failed_paths_20260607.txt`; the clean 530-file toolchain subset was committed and pushed.
- `References/Agent/Frameworks/mastra` has 5 deferred third-party whitespace-gate files recorded in `Results/agent_runtime/mastra_small_modules_diffcheck_failed_paths_20260607.txt`; only `client-sdks`, `server-adapters`, `templates`, and `workflows` were unthrottled and submitted.
- `References/Agent/Security/AiSOC` has 4 deferred third-party whitespace-gate files recorded in `Results/agent_runtime/aisoc_small_ops_diffcheck_failed_paths_20260607.txt`; `detections` and `services` remain throttled. One extensionless Mach-O test artifact `plugins/mttr-widget/go/mttr-widget-test` was removed from the unpushed commit index, kept on disk, precisely ignored, and verified absent from `HEAD` before push.
- `References/Agent/ReviewLater/ChatGPT-Exporter-main` had a clean 9-file subset committed; 12 whitespace-gate files remain deferred. `References/Agent/Domain/terminal-velocity` has two files with leftover conflict markers, recorded in `Results/agent_runtime/agent_small_tail_domain_reviewlater_diffcheck_failed_paths_20260607.txt` and not submitted.
- `References/Agent/Gateway` residual audit found 756 ignored files: 680 generated/binary/runtime outputs, 59 initially clean candidates after env/key/build filtering, and 48 upstream whitespace-gate failures. The remaining 11 clean reference files were committed; failures are recorded in `Results/agent_runtime/gateway_residual_clean_tail_diffcheck_failed_paths_20260607.txt`.

Next:

- Continue with small `References/Agent` project groups under 1000 files after filtering generated/local-only outputs.
- Good next target: continue small-tail inventory, then inspect larger `References/Agent` groups by project slices. Keep env/key/materialized build outputs ignored instead of reopening them.

Additional pushed batch:

- `6516295196` `devops: add docs mcp server memory reference` - 696 files.

Additional deferred/current notes:

- `References/Agent/Memory/docs-mcp-server` had 694 ignored candidates; all passed risk and cached checks after a narrow whitelist and were committed with path evidence in `Results/agent_runtime/docs_mcp_server_paths_20260607.txt`.

Next addendum:

- Continue Memory small residuals such as `git-mcp`, `graphify-8`, `GraphRAG`, `khoj`, and `zep`, then larger Memory/UI/Workflow projects by subdirectory.
