# Documentation Index

> Entry point for project documentation and converted MWORKS reference materials.

---

## 1. Purpose

This file tells Codex and project members where to find relevant documentation.

Do not paste all official documentation into `AGENTS.md`. Store converted Markdown files under `docs/mworks/` and summarize their location here.

---

## 2. Project Documents

| Topic | File | Purpose |
|---|---|---|
| Project rules | `AGENTS.md` | AI agent behavior, MCP usage, workflows, testing |
| User manual | `docs/user_manual.md` | How to install, configure, and run the project |
| Simulation report | `docs/simulation_report.md` | Algorithm design and experiment results |
| API index | `docs/index/api_index.md` | MCP and API lookup |
| Workflow index | `docs/index/workflow_index.md` | Common development workflows |

---

## 3. MWORKS Documentation

Recommended converted documentation structure:

```text
docs/mworks/
├── mcp/
│   ├── sysplorer_mcp.md
│   └── syslab_mcp.md
├── sysplorer/
│   ├── model_manager.md
│   ├── simulation.md
│   ├── result_manager.md
│   └── python_api.md
├── syslab/
│   ├── julia_env.md
│   ├── plotting.md
│   ├── script_execution.md
│   └── matlab_to_julia.md
└── sysblock/
    ├── block_modeling.md
    ├── controller_blocks.md
    └── script_building.md
```

Current generated scan outputs:

| Topic | File | Notes |
|---|---|---|
| MWORKS scan entry | `docs/mworks/README.md` | Entry point for scanned local resource package |
| Scan summary | `docs/mworks/scan/scan_summary.md` | Relevant file counts and next steps |
| Ranked relevant index | `docs/mworks/scan/relevant_index.md` | Top project-related files from the resource package |
| Machine-readable index | `docs/mworks/scan/relevant_files.csv` | CSV for later filtering and scripts |
| Sysplorer modeling category | `docs/mworks/scan/categories/sysplorer_modeling.md` | Sysplorer, Modelica, modeling examples |
| Syslab analysis category | `docs/mworks/scan/categories/syslab_analysis.md` | Syslab, Julia, control analysis and plotting |
| UAV/challenge category | `docs/mworks/scan/categories/quadrotor_uav.md` | Intelligent unmanned system challenge materials |
| Extracted snippets | `docs/mworks/extracted/` | Markdown snippets converted from text-like source files |

---

## 4. MCP Docs

| Topic | File | Notes |
|---|---|---|
| Sysplorer MCP installation | `docs/mworks/mcp/sysplorer_mcp.md` | Installation, wrapper, tools |
| Syslab MCP installation | `docs/mworks/mcp/syslab_mcp.md` | Julia, script execution, nodesktop mode |
| MCP troubleshooting | `workflows/debug_mcp.md` | Tools none, wrapper, conflict config |

---

## 5. Control Algorithm Docs

| Topic | File |
|---|---|
| PID baseline | `docs/algorithms/pid_baseline.md` |
| Improved PID | `docs/algorithms/improved_pid.md` |
| NMPC | `docs/algorithms/nmpc.md` |
| INDI | `docs/algorithms/indi.md` |
| L1-inspired compensation | `docs/algorithms/l1_adaptive.md` |
| Safety filter | `docs/algorithms/safety_filter.md` |
| Fault tolerance | `docs/algorithms/fault_tolerance.md` |

---

## 6. Planning and Formation Docs

| Topic | File |
|---|---|
| Path planning overview | `docs/algorithms/planning.md` |
| A* | `docs/algorithms/astar.md` |
| RRT* | `docs/algorithms/rrt_star.md` |
| Minimum Snap | `docs/algorithms/minimum_snap.md` |
| B-spline | `docs/algorithms/bspline.md` |
| EGO-inspired planning | `docs/algorithms/ego_inspired.md` |
| Formation control | `docs/algorithms/formation.md` |

---

## 7. How to Use This Index

When answering development questions:

1. Read `AGENTS.md` first.
2. If the question is about a workflow, check `docs/index/workflow_index.md`.
3. If the question is about a tool or API, check `docs/index/api_index.md`.
4. If the question is about official behavior, check converted docs under `docs/mworks/`.
5. If docs are missing or unclear, use MCP documentation tools:
   - Sysplorer: `get_api_document`, `get_lib_model_document`, `resources_retrieval`
   - Syslab: `search_syslab_docs`, `read_syslab_doc`

---

## 8. Documentation Maintenance Rules

When new documentation is added:

1. Put the full converted Markdown under `docs/mworks/` or `docs/algorithms/`.
2. Add an entry to this index.
3. Add API-specific entries to `docs/index/api_index.md`.
4. Add workflow-specific entries to `docs/index/workflow_index.md`.
5. Do not duplicate long text into `AGENTS.md`.
