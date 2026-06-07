---
name: ty-sysplorer-modeling-rules
description: >-
  Sysplorer 建模总规则。用户要新建/搭建/修复/仿真模型，或任务可能属于 Modelica 物理、Sysblock 框图、Modelica+Sysblock 混合建模时使用。负责范式分流、七门闸、工作路径、MCP 工具边界和布局闭环：Modelica 物理模型写文本 `.mo`，Sysblock 只用官方 API，混合模型先完成 Sysblock 再嵌入物理顶层；路径只用 Agent CWD 或 `GetDirectory`；`check_model` 后、翻译/长仿真前按 Gate 6 完成图解语义/`smart_layout`。
---

# Sysplorer modeling rules (mandatory)

## MoSim project overlay

When this skill is used inside `C:\Users\HP\Desktop\MoSim`, project rules in
`AGENTS.md` and the MoSim MWORKS live gate take priority over generic modeling
guidance. Any MWORKS/Sysplorer/Syslab visible-department task, including static
model organization, must first run the department-owned activation sentinel and
background screenshot against the existing reusable window. If the sentinel or
background screenshot tooling is unavailable, return `status=blocked` with
`license_state=sentinel_unavailable_blocked`, set
`live_mworks_touched=false`, and do not enter MCP/model/check/simulate/layout
work. Completed MoSim model/simulation/layout work must produce real
engineering evidence such as `.mo`/`package.mo`, `check_model`,
`SimulateModel`, native result/`.msr`, metrics, diagram/layout screenshots, or
wiring observations. JSON packets, ledgers, and `PROGRESS.md` are only
control-plane evidence except for tasks explicitly scoped as
`diagnostic_only`, `rule_sync_only`, `preflight_drill_only`,
`dispatch_surface_diagnostic`, or `static_inventory_only`.

## When this skill must be followed

- The user will **author or edit models** and you must **comply** with paradigm choice, **seven gates**, path conventions, and the **MCP tool split** before deep execution. **Work paths** (see **Work paths for all modeling** below) may use **only** the agent CWD or **`GetDirectory`**—**never** the MCP server’s `main.py` / entry tree.
- The paradigm is unclear (Modelica physical vs Sysblock vs hybrid Modelica + Sysblock): you **must** resolve it using the rules in **`references/modeling_path_router.md`**, then follow the path-specific material under **`references/`** in this skill.
- **Modelica physical, text-only modeling**: diagram-side metadata in `.mo` (**`Placement`**, `connect` annotations such as **`Line`**, `Icon` / `Diagram` primitives) **must** follow the syntax/semantics in **`references/modelica_diagram_connect_semantics.md`** and **`modelica_style_guide.md` Part 3** so it can become input to `graph_json` / `smart_layout` for automated layout and routing. Do **not** leave topology as bare `connect` with no well-formed graphics layer.
- **After `check_model` succeeds (Modelica physical)**: before `translate` / first long `simulate` and before treating diagram work as “done,” **assess** whether the current `.mo` text already encodes the **graphical layer** per **`references/modelica_diagram_connect_semantics.md`** (components have usable **`Placement`**, and `connect` statements have diagram semantics such as **`Line`** / routing hooks where the pipeline expects them—not only bare `connect` with no layout input). **If that layer is missing or insufficient**, **first** run **`smart_layout`** (Gate 6: e.g. `mode=writeback_mo`, `auto_layout=true`, with `modelica_code` + `graph_json` / `graph_json_path` and `model_output_path` per **`references/seven_gates_workflow.md`**) to materialize or repair diagram annotations, **`check_model` again** if `.mo` changed, **then** proceed with translation/simulation and downstream gates. Do not skip this assessment-and-layout step when the source text was authored minimal-topology-first.

## Decision flow (summary)

1. **Hybrid Modelica + Sysblock path** (混合建模/混合仿真, physical plant + Sysblock controller, physical top model embeds a Sysblock model): follow **`modeling_path_router.md` §4** and **`references/hybrid_modeling_workflow.md`**. Build/edit the Sysblock controller with official APIs, then embed the completed Sysblock model as a SEC instance in a Modelica physical top-level `.mo`; if ordinary same-layer `AddComponent` mixing is rejected, treat that as an insertion-path limit, not as proof that hybrid models are unsupported.
2. **Strong Sysblock signals** (Sysblock, block diagram, Embedded Coder, `NewModel(..., restriction="Sysblock")`, programmatic block wiring) with no physical top-level/plant integration: **skip commercial-library-first §0** for physical TY libraries; go to the **Sysblock branch** and follow **`modeling_path_router.md` §3** with **`sysblock_style_guide.md`**. **Do not** author physical `connect()` hydraulic/mechanical graphs for these tasks.
3. **Modelica physical path**: run **library-first / domain mapping** (see `references/modeling_path_router.md` §0), then **`modelica_style_guide.md`**, **`modelica_diagram_connect_semantics.md`**, and **`seven_gates_workflow.md`**.
4. **If uncertain**: ask one clarifying question—Sysblock, traditional Modelica physical, or hybrid physical + Sysblock.

## Work paths for all modeling (mandatory)

**Every** path used to read or write user models, scripts, exports, imports, or any filesystem-dependent step **must** be taken **only** from the sources below. No other default (especially not the MCP server’s own tree) is allowed.

| Priority | Source | Use |
|----------|--------|-----|
| **1 — highest** | **Agent current working directory** | Base path for the active task: relative paths, new files, and “current project” resolution **when** the agent/session reports a CWD. Prefer this as the default workspace for modeling work. |
| **2** | **`GetDirectory`** (MCP) | When a Sysplorer- or project-aligned directory is required and it must come from the tool chain, use **only** the path returned by **`GetDirectory`** (or the server’s equivalent directory tool). **Do not** treat the MCP install tree as a substitute. |
| **Forbidden** | **MCP program / entry path** | **Do not** use the directory where the MCP server runs from as the modeling workspace: e.g. paths containing or rooted at **`main.py`**, the server’s Python entry package, a `site-packages` install used solely to run the server, or the repo clone **used only to launch** the server. **Never** read/write user models or project outputs there by default. |

Rationale: user artifacts must stay in the user or agent workspace; the server’s code tree is for the tool, not the user’s project.

## Global prohibitions (must match platform rules)

### Mandatory implementation modality

- **Modelica physical models**: **Must** author by **writing `.mo` as plain text** (direct file/source text). **Do not** use **call code** / programmatic API as the way to construct the physical Modelica model (no API-first or API-only physical modeling).
- **Sysblock block-diagram models**: **Must** build and wire topology using **call code** APIs (`run_script` / ModelingPy, etc.) per **`references/sysblock_style_guide.md`**. **Do not** author Sysblock block diagrams by **writing or editing `.mo` text** (including `SetModelText` or hand-written diagram `.mo`).
- **Hybrid Modelica + Sysblock models**: the Sysblock submodel still follows the Sysblock rule above; the physical wrapper/top-level still follows the Modelica text rule above. It is allowed to instantiate an already built/checked Sysblock model from the Modelica top-level `.mo` and connect its exposed `Inport` / `Outport` boundary ports. This is **not** permission to hand-write Sysblock internal topology or to embed physical components inside a Sysblock model.
- **Hybrid platform boundary**: do **not** summarize API insertion failures as "Sysplorer does not support hybrid models." The practical boundary is narrower: ordinary same-layer `AddComponent` mixing of `SysplorerEmbeddedCoder` base blocks and physical TY/Modelica components can be rejected, while a completed Sysblock model can be embedded in a physical Modelica top model as a Sysplorer-recognized SEC instance, typically preserved as `annotation(...,__MWORKS(SECInstance=true))`. If that SEC instance already exists, continue by inspecting its exposed ports and connecting/parametrizing/checking the hybrid top model. If it does not exist, do not force ordinary `AddComponent` mixing; use the supported Sysplorer hybrid insertion path or ask for/provide an existing SEC instance before top-level wiring.

- **Never** `ClearAll`, **`ChangeDirectory`**, or otherwise change Sysplorer CWD semantics that conflict with MCP workspace rules.
- Sysblock: **no `SetModelText` / text modeling** for topology; use official APIs (`run_script` / ModelingPy) per **`references/sysblock_style_guide.md`** (same requirement as **Mandatory implementation modality** above).
- Prefer **`get_lib_model_document`** for installed class docs; use **`resources_retrieval`** for large corpora (e.g. `modeling_rules`, `sysblock_model_library`) instead of dumping whole trees into context.

## Tool and corpus cheat sheet

| Goal | Primary tool / corpus |
|------|------------------------|
| Class doc from Sysplorer | `get_lib_model_document` |
| Sysblock block manuals | `resources_retrieval` + **`sysblock_model_library`** (explicit `sources` / index); see `references/sysblock-library-index.md` |
| Hybrid Modelica + Sysblock workflow | `references/hybrid_modeling_workflow.md`; examples under local Sysplorer docs: `HybridSimulation`, `Demo_BuckCircuit`, `Demo_RobotArm` |
| Mandatory rules / gates / style full text | `references/*.md` in this skill |
| Layout / diagram QA | After **`check_model` ok**, confirm `.mo` has diagram semantics per **`modelica_diagram_connect_semantics.md`**; if not, **`smart_layout`** first (then re-`check` if needed), **before** translate/first long simulate (`seven_gates_workflow.md` Gate 6). Also `model_manager(export_model_diagram)` for inspection. |

## Canonical references

Authoritative copies ship under **`references/`** (`modeling_path_router.md`, `modelica_style_guide.md`, `modelica_diagram_connect_semantics.md`, `sysblock_style_guide.md`, `hybrid_modeling_workflow.md`, `seven_gates_workflow.md`). RAG **`corpus_id=modeling_rules`** points at this directory; if a workspace ships different copies under **`resources/`**, prefer **`resources_retrieval`** for RAG, but keep **behavior** consistent with this skill.
