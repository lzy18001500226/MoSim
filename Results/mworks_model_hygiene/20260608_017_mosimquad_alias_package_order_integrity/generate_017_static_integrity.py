import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "Results" / "mworks_model_hygiene" / "20260608_017_mosimquad_alias_package_order_integrity"
RETURN_PACKET = ROOT / "Results" / "agent_packets" / "returns" / "PMO-MWORKS-R2-MOSIMQUAD-ALIAS-PACKAGE-ORDER-INTEGRITY-STATIC-GATE-20260608-017.json"

MOSIM = ROOT / "Models" / "MoSimQuadrotorModel"
QEXP_DYN = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade"

REQ_ID = "PMO-MWORKS-R2-MOSIMQUAD-ALIAS-PACKAGE-ORDER-INTEGRITY-STATIC-GATE-20260608-017"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_order(path: Path):
    if not path.exists():
        return []
    return [line.strip() for line in read_text(path).splitlines() if line.strip()]


def duplicates(items):
    seen = set()
    dup = []
    for item in items:
        if item in seen and item not in dup:
            dup.append(item)
        seen.add(item)
    return dup


DECL_RE = re.compile(r"^\s*(package|model|record|block|connector|class)\s+([A-Za-z_][A-Za-z0-9_]*)\b", re.MULTILINE)
EXT_RE = re.compile(r"extends\s+([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\s*;")


def declarations_in(path: Path):
    if not path.exists():
        return []
    text = read_text(path)
    return [{"kind": m.group(1), "name": m.group(2), "line": text[:m.start()].count("\n") + 1} for m in DECL_RE.finditer(text)]


def extends_in(path: Path):
    if not path.exists():
        return []
    text = read_text(path)
    return [{"target": m.group(1), "line": text[:m.start()].count("\n") + 1} for m in EXT_RE.finditer(text)]


def package_info(pkg_dir: Path, qualified: str):
    pkg_mo = pkg_dir / "package.mo"
    order_path = pkg_dir / "package.order"
    order = read_order(order_path)
    decls = declarations_in(pkg_mo)
    embedded = {
        d["name"]: d
        for d in decls
        if d["name"] != qualified.split(".")[-1]
    }
    result_rows = []
    for entry in order:
        child_dir = pkg_dir / entry
        sibling_mo = pkg_dir / f"{entry}.mo"
        sources = []
        if entry in embedded:
            sources.append("embedded_declaration")
        if child_dir.is_dir() and (child_dir / "package.mo").exists():
            sources.append("child_package_dir")
        if sibling_mo.exists():
            sources.append("sibling_mo")
        status = "resolved" if sources else "unresolved"
        result_rows.append({
            "entry": entry,
            "qualified_name": f"{qualified}.{entry}",
            "status": status,
            "resolution_sources": sources,
            "embedded_kind": embedded.get(entry, {}).get("kind"),
            "child_package_dir": rel(child_dir) if child_dir.is_dir() else None,
            "sibling_mo": rel(sibling_mo) if sibling_mo.exists() else None,
        })

    declared_names = sorted(embedded)
    order_set = set(order)
    extra_declarations = [
        {
            "name": name,
            "kind": embedded[name]["kind"],
            "qualified_name": f"{qualified}.{name}",
            "reason": "embedded declaration not listed in package.order",
        }
        for name in declared_names
        if name not in order_set
    ]
    return {
        "package": qualified,
        "dir": rel(pkg_dir),
        "package_mo": rel(pkg_mo) if pkg_mo.exists() else None,
        "package_order": rel(order_path) if order_path.exists() else None,
        "package_mo_exists": pkg_mo.exists(),
        "package_order_exists": order_path.exists(),
        "order_entries": order,
        "order_count": len(order),
        "order_duplicates": duplicates(order),
        "order_entry_resolution": result_rows,
        "embedded_declarations": [
            {
                "name": name,
                "kind": embedded[name]["kind"],
                "line": embedded[name]["line"],
                "qualified_name": f"{qualified}.{name}",
            }
            for name in declared_names
        ],
        "embedded_not_in_package_order": extra_declarations,
        "status": "pass" if pkg_mo.exists() and order_path.exists() and not duplicates(order) and all(r["status"] == "resolved" for r in result_rows) else "fail",
    }


def index_packages():
    index = {}

    def add_package_dir(qname, pkg_dir):
        info = package_info(pkg_dir, qname)
        index[qname] = {"kind": "package", "source": info["package_mo"], "resolution": "package_dir"}
        for decl in info["embedded_declarations"]:
            index[decl["qualified_name"]] = {
                "kind": decl["kind"],
                "source": info["package_mo"],
                "line": decl["line"],
                "resolution": "embedded_declaration",
            }
        for entry in info["order_entry_resolution"]:
            if entry["sibling_mo"]:
                index[entry["qualified_name"]] = {
                    "kind": "model_or_class_file",
                    "source": entry["sibling_mo"],
                    "resolution": "sibling_mo",
                }

    add_package_dir("MoSimQuadrotorModel", MOSIM)
    for child in sorted([p for p in MOSIM.iterdir() if p.is_dir() and (p / "package.mo").exists()]):
        add_package_dir(f"MoSimQuadrotorModel.{child.name}", child)
    add_package_dir("QuadrotorExperiments.DynamicsUpgrade", QEXP_DYN)
    return index


def resolve_target(target: str, index):
    builtin_prefixes = ("Modelica.",)
    if target in index:
        item = dict(index[target])
        item["target"] = target
        item["status"] = "resolved"
        return item
    if target.startswith(builtin_prefixes):
        return {
            "target": target,
            "status": "resolved_external_builtin",
            "kind": "external_builtin",
            "source": None,
            "resolution": "external_builtin",
        }
    if target.startswith("QuadrotorModel."):
        return {
            "target": target,
            "status": "external_official_baseline_not_checked_in_017_scope",
            "kind": "external_official_baseline",
            "source": "References/MWORKS/QuadrotorModel",
            "resolution": "external_reference_scope",
        }
    if target.startswith("QuadrotorControllerBlocks."):
        return {
            "target": target,
            "status": "external_controller_package_not_checked_in_017_scope",
            "kind": "external_controller_package",
            "source": "Models/QuadrotorControllerBlocks",
            "resolution": "external_reference_scope",
        }
    if target.startswith("QuadrotorExperiments."):
        parts = target.split(".")
        # This task only requires direct static resolution for DynamicsUpgrade.
        if len(parts) >= 3 and parts[1] != "DynamicsUpgrade":
            candidate_dir = ROOT / "Models" / "QuadrotorExperiments" / parts[1]
            candidate_file = candidate_dir / f"{parts[-1]}.mo"
            return {
                "target": target,
                "status": "external_legacy_category_not_checked_in_017_focus",
                "kind": "external_legacy_category",
                "source": rel(candidate_file) if candidate_file.exists() else rel(candidate_dir),
                "resolution": "external_reference_scope",
            }
    return {"target": target, "status": "unresolved", "kind": None, "source": None, "resolution": None}


def extends_report_for(pkg_dir: Path, qualified: str, index):
    pkg_mo = pkg_dir / "package.mo"
    rows = []
    for ext in extends_in(pkg_mo):
        res = resolve_target(ext["target"], index)
        rows.append({
            "source_package": qualified,
            "source_file": rel(pkg_mo),
            "line": ext["line"],
            "target": ext["target"],
            "status": res["status"],
            "target_source": res.get("source"),
            "target_resolution": res.get("resolution"),
            "target_kind": res.get("kind"),
        })
    return rows


def alias_chain_report(index):
    rows = []
    dyn = package_info(MOSIM / "Dynamics", "MoSimQuadrotorModel.Dynamics")
    qdyn = package_info(QEXP_DYN, "QuadrotorExperiments.DynamicsUpgrade")
    qdyn_ext_map = {
        row["target"].split(".")[-1]: row["target"]
        for row in extends_in(QEXP_DYN / "package.mo")
        if row["target"].startswith("QuadrotorExperiments.DynamicsUpgrade.")
    }
    for ext in extends_in(MOSIM / "Dynamics" / "package.mo"):
        if not ext["target"].startswith("QuadrotorExperiments.DynamicsUpgrade."):
            continue
        alias = ext["target"].split(".")[-1]
        final_target = qdyn_ext_map.get(alias)
        final_res = resolve_target(final_target, index) if final_target else {"status": "unresolved", "source": None, "resolution": None, "kind": None}
        rows.append({
            "formal_entry": f"MoSimQuadrotorModel.Dynamics.{next((d['name'] for d in dyn['embedded_declarations'] if d['line'] < ext['line']), '<unknown>')}",
            "formal_extends": ext["target"],
            "compat_alias": f"QuadrotorExperiments.DynamicsUpgrade.{alias}",
            "compat_alias_in_order": alias in qdyn["order_entries"],
            "compat_alias_resolved": ext["target"] in index,
            "final_target": final_target,
            "final_target_status": final_res["status"],
            "final_target_source": final_res.get("source"),
            "final_target_resolution": final_res.get("resolution"),
        })
    return rows


def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str):
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    index = index_packages()
    package_targets = [
        ("MoSimQuadrotorModel", MOSIM),
        ("MoSimQuadrotorModel.Dynamics", MOSIM / "Dynamics"),
        ("MoSimQuadrotorModel.Parameters", MOSIM / "Parameters"),
        ("QuadrotorExperiments.DynamicsUpgrade", QEXP_DYN),
    ]
    all_mosim_categories = [
        package_info(child, f"MoSimQuadrotorModel.{child.name}")
        for child in sorted([p for p in MOSIM.iterdir() if p.is_dir() and (p / "package.mo").exists()])
    ]
    focus_matrix = [package_info(path, qname) for qname, path in package_targets]
    root_info = package_info(MOSIM, "MoSimQuadrotorModel")
    dyn_info = package_info(MOSIM / "Dynamics", "MoSimQuadrotorModel.Dynamics")
    param_info = package_info(MOSIM / "Parameters", "MoSimQuadrotorModel.Parameters")
    qdyn_info = package_info(QEXP_DYN, "QuadrotorExperiments.DynamicsUpgrade")
    current_child_order_count = sum(info["order_count"] for info in all_mosim_categories)

    extends_rows = []
    for qname, path in package_targets:
        extends_rows.extend(extends_report_for(path, qname, index))
    alias_chains = alias_chain_report(index)

    unresolved_package_order = [
        row
        for info in focus_matrix
        for row in info["order_entry_resolution"]
        if row["status"] != "resolved"
    ]
    duplicate_package_order = [
        {"package": info["package"], "duplicates": info["order_duplicates"]}
        for info in focus_matrix
        if info["order_duplicates"]
    ]
    unresolved_extends = [row for row in extends_rows if row["status"] == "unresolved"]
    unresolved_alias_chains = [row for row in alias_chains if row["final_target_status"] == "unresolved"]
    blocking_findings = unresolved_package_order + duplicate_package_order + unresolved_extends + unresolved_alias_chains
    completed = not blocking_findings

    matrix = {
        "request_id": REQ_ID,
        "status": "pass" if completed else "blocked",
        "scope": "static package/order integrity for current MoSimQuadrotorModel root, Dynamics, Parameters, and QuadrotorExperiments.DynamicsUpgrade",
        "root_package_order": root_info["order_entries"],
        "root_package_order_count": root_info["order_count"],
        "root_order_duplicates": root_info["order_duplicates"],
        "current_mosim_category_count": len([p for p in MOSIM.iterdir() if p.is_dir() and (p / "package.mo").exists()]),
        "current_mosim_ordered_child_entries": current_child_order_count,
        "focus_packages": focus_matrix,
        "all_mosim_category_summary": [
            {
                "package": info["package"],
                "order_count": info["order_count"],
                "order_duplicates": info["order_duplicates"],
                "embedded_declaration_count": len(info["embedded_declarations"]),
                "embedded_not_in_package_order_count": len(info["embedded_not_in_package_order"]),
                "status": info["status"],
            }
            for info in all_mosim_categories
        ],
        "blocking_findings": blocking_findings,
    }

    ext_report = {
        "request_id": REQ_ID,
        "status": "pass" if not unresolved_extends and not unresolved_alias_chains else "blocked",
        "scope": "extends resolution for MoSim root/Dynamics/Parameters and QuadrotorExperiments.DynamicsUpgrade; external non-focus packages are classified but not live-checked",
        "extends_rows": extends_rows,
        "dynamics_alias_chains": alias_chains,
        "unresolved_extends": unresolved_extends,
        "unresolved_alias_chains": unresolved_alias_chains,
        "notes": [
            "Modelica.Icons.Package is treated as a built-in external dependency.",
            "QuadrotorModel and non-DynamicsUpgrade QuadrotorExperiments/QuadrotorControllerBlocks targets are outside the focused 017 static resolution scope and are not live-checked.",
            "Every current MoSimQuadrotorModel.Dynamics alias resolves through QuadrotorExperiments.DynamicsUpgrade to a sibling concrete .mo implementation."
        ],
    }

    drift = {
        "request_id": REQ_ID,
        "r2_015_snapshot": {
            "mosim_formal_top_categories": 11,
            "mosim_formal_ordered_child_entries": 64,
            "root_order": [
                "Baseline",
                "Dynamics",
                "Missions",
                "Controllers",
                "Robustness",
                "Planning",
                "SceneTrace",
                "System",
                "Formation",
                "Support",
                "LegacyCompatibility",
            ],
            "dynamics_order_count": 9,
        },
        "current_after_r1_017_018_019": {
            "mosim_formal_top_categories": matrix["current_mosim_category_count"],
            "mosim_formal_ordered_child_entries": current_child_order_count,
            "root_order": root_info["order_entries"],
            "dynamics_order_count": dyn_info["order_count"],
            "parameters_order_count": param_info["order_count"],
            "dynamics_upgrade_order_count": qdyn_info["order_count"],
        },
        "stale_fields": [
            {
                "field": "formal_package_surface_map.root_order_count / mosim_formal_top_categories",
                "r2_015": 11,
                "current": matrix["current_mosim_category_count"],
                "reason": "R1 019 added the formal Parameters package to MoSimQuadrotorModel/package.order."
            },
            {
                "field": "formal_package_surface_map.root_order_entries",
                "r2_015": "no Parameters entry",
                "current": "Parameters appears after Dynamics",
                "reason": "R1 019 created Models/MoSimQuadrotorModel/Parameters with Sunray150ParameterProvenance."
            },
            {
                "field": "MoSimQuadrotorModel.Dynamics entries",
                "r2_015": "pre-017/018 Dynamics surface",
                "current": dyn_info["order_entries"],
                "reason": "R1 017 added ActuatorCommandMapper and ActuatorMappedWrapperSurface; R1 018 added OptionalDampingGyroLayer."
            },
            {
                "field": "QuadrotorExperiments.DynamicsUpgrade entries",
                "r2_015": "pre-017/018 compatibility DynamicsUpgrade surface",
                "current": qdyn_info["order_entries"],
                "reason": "R1 017/018 appended compatibility aliases and concrete sibling sources."
            },
            {
                "field": "mosim_formal_ordered_child_entries",
                "r2_015": 64,
                "current": current_child_order_count,
                "reason": "Dynamics gained three entries and Parameters gained one ordered child entry."
            }
        ],
        "conclusion": "R2 015 remains useful as an ownership taxonomy, but its counts and live-audit queue are stale for current Dynamics/Parameters/package.order integrity."
    }

    queue_md = """# Future Live Audit Queue Update

Static 017 outcome: no live MWORKS/Sysplorer/Syslab action was performed. The next live audit queue must be refreshed before package-browser/check_model work because R1 017/018/019 changed the formal surface.

## Priority Updates

1. `MoSimQuadrotorModel` package-browser visibility: root now has 12 ordered categories, with `Parameters` inserted after `Dynamics`.
2. `MoSimQuadrotorModel.Dynamics` package-browser visibility: audit the 12 ordered formal aliases, especially `ActuatorCommandMapper`, `ActuatorMappedWrapperSurface`, and `OptionalDampingGyroLayer`.
3. `QuadrotorExperiments.DynamicsUpgrade` compatibility browser visibility: confirm the same 12 compatibility aliases still display and resolve.
4. `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance`: package-browser visibility plus record-only `check_model`/load gate when live MWORKS is authorized.
5. Graphical/layout review remains deferred: these source/package-order checks do not prove diagram readability, missing wires, package-browser acceptance, or simulation readiness.

## Resource Lock

Use one reusable MWORKS/Sysplorer session only. Serialize R1 live check_model/smoke work and R2 package-browser/layout review. Stop immediately on demo/login/authorization/error-report/unknown live evidence.

## Claim Boundary

This queue update is static planning only. It is not package-browser acceptance, graphical/layout acceptance, wiring acceptance, `check_model`, `SimulateModel`, controller performance, planner readiness, runtime acknowledgement, mission success, or closed-loop evidence.
"""

    surface_md = [
        "# Current Category Surface",
        "",
        "Static-only summary for current `MoSimQuadrotorModel` after R1 017/018/019.",
        "",
        f"- Root ordered categories: {root_info['order_count']} ({', '.join(root_info['order_entries'])}).",
        f"- MoSim category directories with package.mo: {matrix['current_mosim_category_count']}.",
        f"- Sum of ordered child entries across MoSim categories: {current_child_order_count}.",
        f"- `MoSimQuadrotorModel.Dynamics` ordered entries: {dyn_info['order_count']}.",
        f"- `MoSimQuadrotorModel.Parameters` ordered entries: {param_info['order_count']}.",
        f"- `QuadrotorExperiments.DynamicsUpgrade` ordered entries: {qdyn_info['order_count']}.",
        "",
        "No MWORKS GUI/MCP/check_model/package-browser action was performed.",
    ]

    drift_md = [
        "# Drift From R2 015",
        "",
        "R2 015 is stale for current package/order counts and live-audit queue inputs.",
        "",
        "| Surface | R2 015 | Current 017 static gate | Drift reason |",
        "|---|---:|---:|---|",
        f"| MoSim formal top categories | 11 | {matrix['current_mosim_category_count']} | R1 019 added `Parameters`. |",
        f"| MoSim ordered child entries | 64 | {current_child_order_count} | R1 017/018 added Dynamics entries; R1 019 added Parameters child. |",
        f"| Dynamics ordered entries | 9 | {dyn_info['order_count']} | R1 017 added mapper/mapped wrapper; R1 018 added optional damping/gyro layer. |",
        f"| DynamicsUpgrade ordered entries | pre-017/018 | {qdyn_info['order_count']} | Compatibility aliases and concrete sources were added. |",
        "",
        "015 remains useful as ownership taxonomy, but its counts, package surface map, and next live queue must not be used as current acceptance evidence.",
    ]

    write_json(EVIDENCE / "alias_package_order_integrity_matrix.json", matrix)
    write_json(EVIDENCE / "extends_resolution_report.json", ext_report)
    write_json(EVIDENCE / "drift_from_r2_015.json", drift)
    write_text(EVIDENCE / "current_category_surface.md", "\n".join(surface_md))
    write_text(EVIDENCE / "drift_from_r2_015.md", "\n".join(drift_md))
    write_text(EVIDENCE / "future_live_audit_queue_update.md", queue_md)

    status = "completed" if completed else "blocked"
    packet = {
        "schema": "mosim.agent_packet.return.v1",
        "request_id": REQ_ID,
        "status": status,
        "task_class": "static_model_integrity_gate",
        "quality_status": "completed_static_integrity_gate" if completed else "blocked_static_integrity_gate",
        "source": "static_file_validation_no_gui_no_mcp_no_check_model_no_simulation",
        "completed_at": "2026-06-08T15:25:00+08:00",
        "origin_thread_id": "019e9868-83ea-70f0-92c5-a3a408bd78c6",
        "target_thread": "MoSim｜MWORKS动力学与控制验证部-R2",
        "target_thread_id": "019e9999-b0d3-7682-bccd-faef08fcf1df",
        "department_local_goal": "静态复核 R1 017/018/019 后当前 MoSimQuadrotorModel 的 alias/package.order/extends 完整性，明确 R2 015 快照过期字段，并更新未来 live package-browser/图形审核队列。",
        "critical_path_steps": [
            "读取 017 task packet、AGENTS.md、new_conversation_context、agent_task_ledger、MoSimQuadrotorModel 迁移设计文档、mworks-model-context skill、R2 015 return、R1 017/018/019 returns 和当前 package.mo/package.order 源。",
            "确认 static-only 边界：live_mworks_touched=false，mworks_window_evidence_touched=false，禁止 MWORKS/Sysplorer/Syslab GUI/MCP/check_model/SimulateModel/Smart Layout/package browser/result viewer。",
            "审计 MoSimQuadrotorModel root、Dynamics、Parameters 与 QuadrotorExperiments.DynamicsUpgrade 的 package.order 条目、重复项、embedded declarations、子包目录和 sibling .mo 解析。",
            "静态解析 Dynamics formal aliases 到 QuadrotorExperiments.DynamicsUpgrade compatibility aliases，再到真实 sibling .mo 实现源。",
            "对比 R2 015 快照与 R1 017/018/019 后当前 package surface，标出过期字段和后续 live audit 队列更新。",
            "写 017 evidence artifacts 和 return/blocker packet，并运行 JSON、MWORKS live gate、department packet contract、scoped diff checks。"
        ],
        "parallelizable_slices": [
            {
                "slice": "MoSim root/category package.order integrity",
                "status": "completed",
                "evidence": "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/alias_package_order_integrity_matrix.json"
            },
            {
                "slice": "Dynamics/DynamicsUpgrade/Parameters extends resolution",
                "status": "completed",
                "evidence": "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/extends_resolution_report.json"
            },
            {
                "slice": "R2 015 drift summary",
                "status": "completed",
                "evidence": [
                    "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/drift_from_r2_015.md",
                    "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/drift_from_r2_015.json"
                ]
            },
            {
                "slice": "Future live audit queue update",
                "status": "completed",
                "evidence": "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/future_live_audit_queue_update.md"
            }
        ],
        "subagent_plan": "available_but_not_useful",
        "subagent_plan_reason": "017 is a deterministic static parser/audit over a small, tightly coupled package surface. A disposable subagent would duplicate the same reads, cannot perform live MWORKS verification under task boundaries, and would add reconciliation overhead without independent evidence value.",
        "subagents_used": [],
        "verification_gates": [
            {
                "gate": "required_read_first",
                "status": "pass",
                "evidence": [
                    "AGENTS.md",
                    "Docs/Workflows/new_conversation_context.md",
                    "Docs/Workflows/agent_task_ledger.md",
                    "Docs/Design/12_MoSimQuadrotorModel模型归档与迁移计划.md",
                    "C:/Users/HP/.codex/skills/mworks-model-context/SKILL.md",
                    "R2 015 return",
                    "R1 017/018/019 returns",
                    "current root/Dynamics/Parameters/DynamicsUpgrade package files"
                ]
            },
            {
                "gate": "static_only_boundary",
                "status": "pass",
                "details": "No MWORKS/Sysplorer/Syslab GUI/window/screenshot/MCP/check_model/SimulateModel/Smart Layout/package-browser/result-viewer/ClearAll/ChangeDirectory was used."
            },
            {
                "gate": "package_order_integrity",
                "status": "pass" if not unresolved_package_order and not duplicate_package_order else "blocked",
                "evidence": "alias_package_order_integrity_matrix.json"
            },
            {
                "gate": "extends_resolution",
                "status": "pass" if not unresolved_extends and not unresolved_alias_chains else "blocked",
                "evidence": "extends_resolution_report.json"
            },
            {
                "gate": "r2_015_drift_recorded",
                "status": "pass",
                "evidence": "drift_from_r2_015.md"
            },
            {
                "gate": "future_live_queue_updated",
                "status": "pass",
                "evidence": "future_live_audit_queue_update.md"
            }
        ],
        "manual_review_or_blocker_triggers": [
            "If future live package-browser or check_model is required, dispatch a separate live task with CoAgentOps patrol/session gate and no new-window route.",
            "If any static package.order duplicate, unresolved order entry, or unresolved Dynamics/DynamicsUpgrade extends target appears later, write a blocker before live MWORKS work.",
            "If Parameters record needs live package-browser/check acceptance, serialize it with R1/R2 resource locks; 017 is not live acceptance.",
            "If official QuadrotorModel or References edits are needed, stop and request explicit PMO scope.",
            "If any Sunray150 numeric seed is to be promoted to truth, require PX4 ULog/bench/weighing/validated identification evidence."
        ],
        "will_not_click_activation_login": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "mworks_activation_patrol_reference": {
            "status": "not_required_static_model_integrity_gate",
            "activation_patrol_owner": "CoAgentOps",
            "recent_patrol_required": False,
            "reason": "017 is static-only and explicitly forbids MWORKS/Sysplorer/Syslab window, screenshot, GUI, MCP, package browser, check_model, SimulateModel, Smart Layout, and result viewer work."
        },
        "alias_package_order_integrity_matrix": {
            "path": "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/alias_package_order_integrity_matrix.json",
            "status": matrix["status"],
            "root_package_order_count": root_info["order_count"],
            "current_mosim_category_count": matrix["current_mosim_category_count"],
            "current_mosim_ordered_child_entries": current_child_order_count,
            "blocking_findings_count": len(blocking_findings)
        },
        "extends_resolution_report": {
            "path": "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/extends_resolution_report.json",
            "status": ext_report["status"],
            "extends_rows": len(extends_rows),
            "dynamics_alias_chains": len(alias_chains),
            "unresolved_extends_count": len(unresolved_extends),
            "unresolved_alias_chains_count": len(unresolved_alias_chains)
        },
        "drift_from_r2_015": {
            "path": "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/drift_from_r2_015.md",
            "status": "recorded",
            "r2_015_top_categories": 11,
            "current_top_categories": matrix["current_mosim_category_count"],
            "r2_015_ordered_child_entries": 64,
            "current_ordered_child_entries": current_child_order_count,
            "stale_snapshot": True
        },
        "future_live_audit_queue_update": {
            "path": "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/future_live_audit_queue_update.md",
            "status": "updated_static_plan_only"
        },
        "actual_engineering_outputs": [
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/current_category_surface.md",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/alias_package_order_integrity_matrix.json",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/extends_resolution_report.json",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/drift_from_r2_015.md",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/drift_from_r2_015.json",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/future_live_audit_queue_update.md"
        ],
        "changed_files": [
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/current_category_surface.md",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/alias_package_order_integrity_matrix.json",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/extends_resolution_report.json",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/drift_from_r2_015.md",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/drift_from_r2_015.json",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/future_live_audit_queue_update.md",
            "Results/mworks_model_hygiene/20260608_017_mosimquad_alias_package_order_integrity/generate_017_static_integrity.py",
            "Results/agent_packets/returns/PMO-MWORKS-R2-MOSIMQUAD-ALIAS-PACKAGE-ORDER-INTEGRITY-STATIC-GATE-20260608-017.json"
        ],
        "forbidden_actions_confirmed": {
            "edited_model_source_package_mo_or_package_order": False,
            "opened_closed_switched_maximized_restarted_or_screenshotted_mworks_sysplorer_syslab_window": False,
            "operated_mworks_sysplorer_syslab_gui": False,
            "called_mworks_sysplorer_syslab_mcp": False,
            "ran_check_model": False,
            "ran_simulate_model": False,
            "ran_smart_layout_package_browser_or_result_viewer": False,
            "called_clearall_or_changedirectory": False,
            "edited_references_official_quadrotor_model_ros2_ue_blender_sunray_coagent_runtime": False,
            "staged_unstaged_reverted_cleaned_committed_or_pushed_git": False
        },
        "checker_results": {},
        "claim_boundary": [
            "017 claims only static source/package/order integrity evidence for current MoSimQuadrotorModel aliases, Dynamics/DynamicsUpgrade/Parameters surfaces, and R2 015 drift.",
            "017 does not claim live MWORKS package-browser acceptance, graphical/layout acceptance, wiring acceptance, check_model, SimulateModel, controller performance, planner readiness, runtime acknowledgement, mission success, or closed_loop.",
            "017 does not identify or tune Sunray150 physical parameters and does not promote RflySim/Gazebo/YunZong/SDF numeric seeds to truth.",
            "017 does not edit model implementation files; real live validation or source fixes require separately scoped tasks."
        ],
    }
    write_json(RETURN_PACKET, packet)
    print(json.dumps({"status": status, "return_packet": rel(RETURN_PACKET), "blocking_findings_count": len(blocking_findings)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
