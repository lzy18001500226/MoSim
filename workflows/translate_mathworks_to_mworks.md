# Translate MathWorks / Simulink Patterns to MWORKS

> Purpose: convert MATLAB/Simulink agent skills, prompts, or workflows into project-specific MWORKS.Syslab / Sysplorer / Sysblock procedures.

## Success Criteria

A translation is complete only when it produces at least one project-local artifact:

```text
docs/index/*.md
workflows/*.md
controllers/*/*.yaml
scenarios/**/*.yaml
scripts/*.py or scripts/*.jl
models/**/*.mo
results/raw/*.csv
results/metrics/*.json
```

Do not stop at a conceptual comparison.

## Step 1: Classify the Source Material

| Source Type | Example | Translate To |
|---|---|---|
| MATLAB coding rule | preallocation, vectorization, naming | Syslab/Python coding rule |
| MATLAB MCP wrapper | function description, tool metadata, request discipline | MWORKS MCP workflow discipline |
| Simulink model interaction | current model, selected blocks, block params | Sysplorer model/component/port introspection |
| Simulink simulation workflow | sim, logsout, signal logging | Sysplorer simulation + result_manager export |
| Simulink debugging workflow | sldebug, solver profiler | MWORKS check/translate/simulate/result probe workflow |
| Simulink project structure | models/data/doc/test separation | Quadrotor project directory conventions |

## Step 2: Check Official MWORKS Equivalence

Before writing a workflow, check these sources in order:

```text
docs/index/mathworks_to_mworks_migration.md
docs/mworks/converted/
docs/mworks/scan/relevant_index.md
references/MWORKS高校星火计划资料包/MWORKS与MATLAB功能对照/
```

If MCP is available, prefer targeted queries:

```text
syslab.detect_syslab_toolboxes
syslab.search_syslab_docs
sysplorer_mcp.get_api_document
sysplorer_mcp.get_lib_model_document
sysplorer_mcp.resources_retrieval
```

## Step 3: Choose the MWORKS Target

| Need | Preferred Target |
|---|---|
| numerical analysis, metrics, plots | Syslab Julia or project Python |
| Modelica model/component operations | Sysplorer MCP |
| block-level control subsystem design | Sysblock or Modelica class |
| scenario configuration | YAML under `scenarios/` |
| repeatable agent procedure | Markdown under `workflows/` |
| long-term rule/index | Markdown under `docs/index/` |

## Step 4: Write the Translation as an Action Workflow

A good MWORKS workflow contains:

```text
goal
inputs
MCP tools or scripts
output paths
validation checks
failure handling
evidence rules
```

Avoid vague rules like:

```text
use Simulink-style debugging
```

Prefer concrete rules:

```text
Use model_manager.get_components to locate the component, check_model before simulate_model, then read the exact result variables with result_manager.get_vars_values.
```

## Step 5: Verify with This Project

For control/simulation workflows:

```bash
python3 scripts/qa_check.py
python3 -m py_compile scripts/*.py tests/*.py
python3 scripts/check_reference_outputs.py
git diff --check
```

For MWORKS model evidence:

```text
MCP JSONL log exists
raw CSV exists
metrics JSON exists
scenario or report references the output
```

## Step 6: Keep the Repository Lean

Do not commit large raw upstream repositories or repeated generated logs just because they helped design a workflow.

Keep:

```text
compact indexes
converted high-value Markdown
small summaries
reproducible scripts
official result artifacts needed by reports
```

Avoid:

```text
duplicate upstream docs
temporary extraction folders
one-off raw conversion dumps
large videos/PDFs unless explicitly required
```

## Current Recommended Translation Queue

1. Use `Skills/Mworks/mworks-model-context/SKILL.md` for Simulink-style model/block context requests.
2. Use `Skills/Mworks/mworks-simulation-evidence/SKILL.md` for simulation/logging/result evidence requests.
3. Use `Skills/Mworks/mworks-syslab-porting/SKILL.md` for MATLAB coding, Syslab, plotting, and performance migration.
4. Use `Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` for debug/profiler/solver-style tasks.
5. Use `Skills/Mworks/mworks-test-quality/SKILL.md` for testing, review, and regression tasks.
6. Use `Skills/Mworks/mworks-report-visualization/SKILL.md` for report, replay, and video material.
7. Use `Skills/Mworks/mworks-mcp-operations/SKILL.md` for wrapper, session, and MCP minimal-impact behavior.
