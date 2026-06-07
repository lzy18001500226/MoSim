---
name: mworks-syslab-porting
description: Port MATLAB scripts, Simulink habits, MathWorks skills, numeric workflows, tests, plotting, metrics, or performance rules into this MWORKS.Syslab/Sysplorer quadrotor project. Use when translating material from Skills/Matlab, Skills/Simulink, MATLAB code, Simulink workflows, or MathWorks-style prompts into project-local MWORKS workflows.
---

# MWORKS Syslab Porting

Use project-local `Skills/Mworks/` first. Treat MathWorks/Simulink material as a second-level pattern library only when the MWORKS skills do not cover the task. After using an upstream pattern, translate it into MWORKS terms and update the relevant `Skills/Mworks/*/SKILL.md`, `workflows/`, or `docs/index/` artifact. Verify every executable API through MWORKS docs or MCP.

## Source Priority

Check in this order:

```text
Skills/Mworks/
docs/index/mathworks_to_mworks_migration.md
docs/mworks/converted/matlab_compat/
docs/mworks/converted/
docs/mworks/scan/relevant_index.md
Skills/Matlab/
Skills/Simulink/
```

## Translation Map

| MathWorks pattern | MWORKS project target |
|---|---|
| MATLAB script/function | Syslab Julia script or project Python script |
| MATLAB toolbox function | installed Syslab/Ty/Julia package after `detect_syslab_toolboxes` |
| Simulink current model/block | Sysplorer `model_manager` context query |
| Simulink `sim()` / `logsout` | Sysplorer `simulate_model` + `result_manager` |
| Simulink Test | scenario smoke/regression workflow and metrics threshold |
| MATLAB profiler/timeit | Python/Syslab timing plus saved metrics |
| MATLAB coding standards | project Python/Julia style: clear names, preallocation, deterministic tests |

## Required MCP Checks

For Syslab/Juila:

```text
read_syslab_skill
detect_syslab_toolboxes
map_matlab_functions_to_julia when porting MATLAB functions
search_syslab_docs / read_syslab_doc for unknown functions
evaluate_julia_code or run_julia_file for validation
```

For Sysplorer:

```text
activation sentinel / background screenshot for MWORKS department work
  -> if demo/login/activation/authorization/GUI blocker: stop and return blocker
get_api_document
resources_retrieval
check_model
simulate_model
result_manager
```

MWORKS department-owned Syslab/Sysplorer porting tasks must run
`Scripts/agent/check_mworks_gui_sentinel.py` and
`Scripts/tools/capture_window_background.ps1` before any Sysplorer MCP/model
work. Return or blocker packets must include `activation_sentinel_before`,
`gui_sentinel_before`, `background_screenshot_before`,
`activation_state_observation`, `license_state`,
`will_not_click_activation_login=true`, `mworks_window_evidence_touched=true`,
and `live_mworks_touched`. Do not treat demo, login, activation,
authorization, visible unknown window, unknown sentinel, or GUI-error-report states as porting or solver
bugs.
If the porting task proceeds into live Sysplorer/MWORKS model work, capture and
inspect phase screenshots after load/check/simulate/plot phases as applicable
and return `mworks_phase_screenshots` plus `mworks_phase_observations`. If
activation/license/login/authorization/GUI-error evidence appears at preflight
or mid-task, stop live work and return a P0 MWORKS infrastructure blocker so
PMO sends both sparse WeChat and sparse email alert.

## Output Rules

Every translation must produce a project artifact:

```text
workflow under workflows/
index under docs/index/
script under scripts/
scenario/controller config
test under tests/
result evidence under results/
```

Avoid creating broad new documents. Update existing index/workflow files when a concise change is enough.

## Coding Rules

1. Prefer existing project script style.
2. Use deterministic inputs and saved outputs.
3. Avoid hard-coded absolute paths.
4. Preallocate arrays or use vectorized operations for metrics and plotting.
5. Use tolerances for floating-point tests.
6. Keep generated reports and figures reproducible from raw results.
