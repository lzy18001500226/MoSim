# 文件树审核摘要

Request ID: `DOCSECRETARY-FILE-ORGANIZATION-REVIEW-20260608-001`

## Results 根目录整理后

```text
Results/
  README.md
  人工审核清单.csv
  tmp_agent_projects_list.txt
  agent_packets/
  coagent_gateway/
  coagent_transport/
  coagent_status/
  mworks_background_capture/
  mworks_gui_incidents/
  mworks_model_hygiene/
  mworks_window_management/
  ros2_runtime/
  unreal_experiment_console/
  unreal_scene_mapping/
  tmp/
  ... 其他按领域分类目录
```

根目录中原先平铺的旧 `tmp_*` 清单已归到：

```text
Results/tmp/git_reference_intake_20260601/
```

## Results 主要目录规模

```text
agent_packets                    3392 files, 8.17 MB
agent_runtime                    9635 files, 3024.45 MB
browser_captures                 2836 files, 250.89 MB
coagent_gateway                   464 files, 0.75 MB
coagent_status                    367 files, 6.77 MB
coagent_transport                5454 files, 41.56 MB
mworks_background_capture         383 files, 16.70 MB
mworks_gui_incidents               96 files, 19.76 MB
mworks_model_hygiene              243 files, 2.67 MB
mworks_window_management            39 files, 3.19 MB
native_result_cache                49 files, 8080.30 MB
official                          353 files, 4997.50 MB
ros2_runtime                     3060 files, 253.57 MB
tmp                              9808 files, 1263.22 MB
unreal_experiment_console         186 files, 2.62 MB
unreal_scene_mapping              559 files, 685.04 MB
```

## agent_packets 当前结构

```text
Results/agent_packets/
  <root task packets>        225 json, 25 yaml
  returns/                   282 files
  blockers/                  134 files
  notifications/              29 files
  reviews/                    22 files
  summaries/                  22 files
  closeouts/                   5 files
  manual/                      1 file
  archive/                     0 files
  maintenance/                 0 files
```

审核结论：`returns/`、`blockers/` 和根部 task packets 都是当前工作流引用面，本轮保持不动。

## Docs/Cache 当前结构

```text
Docs/Cache/
  session_memory_migration/                         26 md
  session_memory_migration/image/long_goal_plan_20260604/ 1 png
```

审核结论：结构清晰，保持不动。

## 本轮移动文件分类

```text
Results/tmp/git_reference_intake_20260601/
  docs_unreal                    8 files
  reference_control             27 files
  reference_domain              35 files
  rollout_tmp                    2 files
  other_tmp                      3 files
```

移动文件共 75 个，合计约 10.70 MB。

## 移动后的旧临时清单目录

```text
Results/tmp/git_reference_intake_20260601/
  tmp_batch012_sorted.txt
  tmp_cached_names_now.txt
  tmp_docs_unreal_nonvenv_ignored_paths_no_missing_lfs.txt
  tmp_docs_unreal_nonvenv_ignored_paths.txt
  tmp_docs_unreal_nonvenv_over100.txt
  tmp_docs_unreal_remaining_after_venv.txt
  tmp_docs_unreal_remaining_ignored.txt
  tmp_docs_unreal_venv_batch_00
  tmp_docs_unreal_venv_batch_01
  tmp_docs_unreal_venv_remaining.txt
  tmp_refs_agent_control_batch_000 ... tmp_refs_agent_control_batch_025
  tmp_refs_agent_control_files.txt
  tmp_refs_agent_domain_batch_000 ... tmp_refs_agent_domain_batch_031
  tmp_refs_agent_domain_batch_031_diffcheck_files
  tmp_refs_agent_domain_batch_031_normalize_files
  tmp_refs_agent_domain_files.txt
  tmp_refs_agent_key_ignored.txt
  tmp_win_rollouts.txt
  tmp_wsl_rollouts.txt
```

## 待审核整理建议

```text
Results/agent_packets/tasks/
  future only or migration with workflow/checker compatibility plan

Results/coagent_transport/archive/YYYYMMDD/
  only after confirming runtime/recovery tools do not require flat paths

Results/tmp/<source_or_task>/
  second pass classification for existing tmp evidence
```

本轮没有移动这些高风险候选。
