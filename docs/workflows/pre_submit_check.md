# Pre-Submit Check Workflow

> Purpose: verify that the project is ready for competition submission.

---

## 1. Goal

Before submission, check that the project contains required files, runnable models, reproducible experiments, valid metrics, report figures, and documentation.

---

## 2. Required Deliverables

The project should include:

```text
complete MWORKS model files
controller source files
scenario configuration files
planning / trajectory scripts if used
formation scripts or models if used
batch simulation scripts
raw simulation results
metrics tables
figures
user manual PDF
simulation analysis report PDF
demo video
README.md
AGENTS.md
```

---

## 3. MCP Check

Run `/mcp` in Codex.

Pass condition:

```text
syslab has tools
sysplorer_mcp has tools
```

Expected Syslab tools:

```text
detect_syslab_toolboxes
evaluate_julia_code
run_julia_file
search_syslab_docs
read_syslab_doc
```

Expected Sysplorer tools:

```text
session_manager
model_manager
check_model
simulate_model
result_manager
get_api_document
```

Notes:

```text
Auth: Unsupported is normal.
Tools: (none) is failure.
```

---

## 4. Directory Check

Required project entry points:

```text
scripts/
docs/
docs/index/
docs/mworks/converted/
QuadrotorModel/
workflows/
```

Implementation directories are created only when they contain real files:

```text
controllers/
planners/
scenarios/
tests/
results/{group}/{scene}/{experiment}/raw/
results/{group}/{scene}/{experiment}/metrics/
results/{group}/{scene}/{experiment}/figures/
docs/figures/
```

Run:

```bash
python scripts/qa_check.py
python scripts/check_reference_outputs.py
```

### Skill / Workflow Hygiene Check

Project-local skills and workflows must stay discoverable and credential-free:

```text
every `Skills/Mworks/*` skill has `SKILL.md`
each `SKILL.md` has YAML frontmatter with `name` and `description`
workflow links in `docs/index/workflow_index.md` resolve
no copied OAuth/provider configs, private `.env`, token, or key files are tracked
external skill/runtime repositories remain reference material unless explicitly promoted
```

### Reference / Large-File / Secret Check

Before staging or packaging, inspect newly added reference trees and generated
assets. This is mandatory when `Skills/`, `references/`, `unreal/`, `results/`,
or downloaded open-source repositories changed.

```bash
git status --short
find . -type f -size +100M -not -path './.git/*' -print
rg -n --hidden --glob '!.git/**' \
  '(API_KEY|SECRET|TOKEN|OAuth|oauth|Bearer |PRIVATE KEY|GITHUB_TOKEN|OPENAI_API_KEY|COMPOSIO_API_KEY)' \
  AGENTS.md README.md Design docs workflows scripts Skills controllers planners scenarios unreal
```

Rules:

1. Do not stage whole reference repositories only because they are useful for
   reading. Promote only selected project-owned files, manifests, or translated
   workflows.
2. External automation skills that require OAuth, SaaS accounts, browser
   profiles, or cross-workspace file organization are not submission assets.
3. Binary/fonts/media/reference payloads are allowed only when they are required
   project assets, under GitHub limits, and have clear license/source notes.
4. If a large or credential-like hit is intentional documentation, verify that
   it is an example placeholder, not a real token or private config.

---

## 5. Required Experiment Check

At minimum, the following experiments should be runnable or documented:

```text
PID hover baseline
PID step baseline
PID figure8 baseline
optimized controller figure8
optimized controller spiral
wind disturbance scenario
mass change or motor fault scenario
```

Recommended additional experiments:

```text
path planning obstacle avoidance
three-UAV formation
formation switching
motor efficiency degradation
```

---

## 6. Metrics Check

For every experiment used in the report, verify that metrics exist.

Required metrics:

```text
position_rmse
max_position_error
steady_state_error
attitude_rmse
control_energy
```

For step response:

```text
overshoot
settling_time
rise_time
```

For robustness:

```text
disturbance_recovery_time
performance_degradation
improvement_over_baseline
```

For path planning:

```text
path_length
planning_time
minimum_obstacle_distance
trajectory_smoothness
```

For formation:

```text
formation_error_rmse
formation_error_max
minimum_inter_uav_distance
formation_keeping_rate
```

---

## 7. Figure Check

Every report claim should have a figure or table.

Required figures:

```text
environment setup screenshot
MCP verification screenshot
official quadrotor model screenshot
official PID controller screenshot
system architecture diagram
NMPC-INDI-L1 controller diagram
PID vs optimized 8-shaped trajectory
wind disturbance error curve
metrics comparison table or bar chart
```

Recommended figures:

```text
spiral trajectory
motor fault response
path planning obstacle map
planned path vs actual trajectory
formation trajectory
formation error curve
MCP tool call result
Syslab metrics generation result
```

---

## 8. Report Check

User manual must include:

```text
system overview
environment configuration
software installation
MCP configuration
how to open model
how to run simulation
how to reproduce scenarios
parameter explanation
interface explanation
common troubleshooting
```

Simulation report must include:

```text
algorithm design
system architecture
baseline PID analysis
optimized control method
experiment settings
metrics definition
comparison results
robustness analysis
scenario validation
innovation summary
conclusion
```

---

## 9. Video Check

Demo video should include:

```text
project overview
system architecture
baseline PID problem
optimized controller result
disturbance or fault scenario
path planning or formation if implemented
metrics and comparison
innovation summary
```

Length:

```text
<= 7 minutes
```

Do not show features that are not implemented.

---

## 10. Code Review Check

Before final submission, review:

```text
no broken absolute paths
no missing source files
no missing model dependencies
no untracked generated result required by report
no report claim without figure/metric
no copied code without source note
no temporary debug-only file in final package
```

---

## 11. Final Pass Criteria

A submission is ready if:

```text
MCP tools are available
baseline PID runs
optimized controller runs
metrics are generated
figures are generated
report can reference saved figures and metrics
README and user manual explain how to reproduce results
video matches implemented features
```

If any item fails, either fix it or remove the corresponding claim from the report.
