import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REQ = "PMO-MWORKS-R2-MOSIMQUAD-STATIC-CLASSIFICATION-LIVE-AUDIT-QUEUE-20260608-015"
EVID = ROOT / "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue"
RET = ROOT / "Results/agent_packets/returns/PMO-MWORKS-R2-MOSIMQUAD-STATIC-CLASSIFICATION-LIVE-AUDIT-QUEUE-20260608-015.json"
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def order_entries(path: str) -> list[str]:
    p = ROOT / path
    if not p.exists():
        return []
    return [line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def package_decls(text: str) -> list[str]:
    return re.findall(r"^\s*(?:package|model|block|function)\s+([A-Za-z_]\w*)\b", text, flags=re.M)


def extends_targets(text: str) -> list[str]:
    return re.findall(r"\bextends\s+([A-Za-z_][\w.]*)(?:\s*\(|\s*;)", text)


category_roles = {
    "Baseline": ("官方基线适配", "official_baseline_adapter", "QuadrotorModel", "formal wrapper aliases only"),
    "Dynamics": ("Sunray150动力学升级", "project_owned_dynamics_upgrade", "QuadrotorExperiments.DynamicsUpgrade", "formal wrapper aliases only"),
    "Missions": ("正式任务场景", "official_task_scenarios", "QuadrotorExperiments.OfficialScenarios", "formal wrapper aliases only"),
    "Controllers": ("控制器基线与对比", "controller_baselines_and_blocks", "QuadrotorExperiments.ControllerBaselines + QuadrotorControllerBlocks", "formal wrapper/category aliases only"),
    "Robustness": ("鲁棒、故障、安全与扰动", "robust_fault_safety_disturbance", "QuadrotorExperiments.RobustFaultScenarios", "formal wrapper aliases only"),
    "Planning": ("规划与地图场景", "planning_and_map_scenarios", "QuadrotorExperiments.PlanningScenarios", "formal wrapper aliases only"),
    "SceneTrace": ("UE场景trace与显示隔离", "scene_trace_and_isolation", "QuadrotorExperiments.SceneTraceScenarios + TraceIsolation", "aggregate package aliases"),
    "System": ("系统级图形和硬件抽象", "system_graphical_architecture_modules", "QuadrotorExperiments.SystemArchitecture + SystemModules", "aggregate package aliases"),
    "Formation": ("编队扩展", "formation_extension", "QuadrotorExperiments.FormationScenarios", "formal wrapper aliases only"),
    "Support": ("支撑/trace/MCP工具模型", "support_trace_mcp_helpers", "QuadrotorExperiments.SupportModels", "formal wrapper aliases only"),
    "LegacyCompatibility": ("旧入口兼容", "legacy_compatibility_pool", "QuadrotorExperiments", "compatibility aggregate only"),
}


def main() -> None:
    EVID.mkdir(parents=True, exist_ok=True)
    RET.parent.mkdir(parents=True, exist_ok=True)

    mosim_root_order = order_entries("Models/MoSimQuadrotorModel/package.order")
    formal_categories = []
    formal_surface_rows = []
    for cat in mosim_root_order:
        pmo = ROOT / "Models/MoSimQuadrotorModel" / cat / "package.mo"
        po = ROOT / "Models/MoSimQuadrotorModel" / cat / "package.order"
        txt = pmo.read_text(encoding="utf-8") if pmo.exists() else ""
        decls = [d for d in package_decls(txt) if d != cat]
        orders = order_entries(rel(po)) if po.exists() else []
        targets = extends_targets(txt)
        role_cn, role_key, source, state = category_roles.get(cat, ("", "", "", ""))
        formal_categories.append({
            "category": cat,
            "role_cn": role_cn,
            "role_key": role_key,
            "formal_package": f"MoSimQuadrotorModel.{cat}",
            "package_mo": rel(pmo),
            "package_order": rel(po) if po.exists() else None,
            "order_entries": orders,
            "order_count": len(orders),
            "declared_entries": decls,
            "declared_entry_count": len(decls),
            "source_or_dependency_surface": source,
            "implementation_state": state,
            "canonicality_state": "formal_entry_alias_surface_not_real_namespace_migration",
            "live_validation_state": "not_run_static_only_015",
        })
        formal_surface_rows.append({
            "formal_entry": f"MoSimQuadrotorModel.{cat}",
            "visible_order_index": mosim_root_order.index(cat) + 1,
            "category_role": role_cn,
            "source_surface": source,
            "package_order_entry_count": len(orders),
            "extends_targets": targets,
            "surface_kind": state,
            "recommended_next_gate": "package_browser_visibility_then_targeted_check_or_layout_queue",
        })

    qexp = ROOT / "Models/QuadrotorExperiments"
    legacy_dirs = []
    for d in sorted([x for x in qexp.iterdir() if x.is_dir()]):
        mo_files = sorted([x.name for x in d.glob("*.mo")])
        pkg_text = (d / "package.mo").read_text(encoding="utf-8") if (d / "package.mo").exists() else ""
        legacy_dirs.append({
            "legacy_category": d.name,
            "path": rel(d),
            "mo_file_count": len(mo_files),
            "sample_mo_files": mo_files[:8],
            "has_package_mo": (d / "package.mo").exists(),
            "has_package_order": (d / "package.order").exists(),
            "package_order_count": len(order_entries(rel(d / "package.order"))) if (d / "package.order").exists() else 0,
            "package_extends_target_count": len(extends_targets(pkg_text)),
            "role_in_015": "legacy_implementation_or_compatibility_source_preserved",
        })

    ctrl_root = ROOT / "Models/QuadrotorControllerBlocks"
    controller_mo_files = sorted([p.name for p in ctrl_root.glob("*.mo") if p.name != "package.mo"])
    controller_backup_dirs = sorted([p.name for p in ctrl_root.iterdir() if p.is_dir()])
    ctrl_pkg_text = read_text("Models/QuadrotorControllerBlocks/package.mo")
    controller_surface = {
        "package": "QuadrotorControllerBlocks",
        "path": "Models/QuadrotorControllerBlocks",
        "flat_controller_mo_count": len(controller_mo_files),
        "flat_controller_mo_files": controller_mo_files,
        "package_order_entries": order_entries("Models/QuadrotorControllerBlocks/package.order"),
        "package_order_count": len(order_entries("Models/QuadrotorControllerBlocks/package.order")),
        "backup_or_upgrade_dirs_preserved_count": len(controller_backup_dirs),
        "backup_or_upgrade_dirs_preserved": controller_backup_dirs,
        "extends_targets_count": len(extends_targets(ctrl_pkg_text)),
        "role_in_015": "controller_block_package_shell_and_legacy_flat_controller_library_preserved",
    }

    references_surface = {
        "package": "QuadrotorModel",
        "path": "References/MWORKS/QuadrotorModel/package.mo",
        "role_in_015": "official_upstream_baseline_and_regression_dependency_read_only",
        "resource_files_observed": len(list((ROOT / "References/MWORKS/QuadrotorModel/Resources").rglob("*"))),
        "do_not_edit_policy": True,
        "formal_adapter_entries": [
            "MoSimQuadrotorModel.Baseline.OfficialExample1",
            "MoSimQuadrotorModel.Baseline.OfficialExample2",
            "MoSimQuadrotorModel.Baseline.OfficialExample3",
            "MoSimQuadrotorModel.Baseline.OfficialQuadChassis",
        ],
    }

    classification = {
        "schema": "mosim.mworks_model_hygiene.model_ownership_classification.v1",
        "request_id": REQ,
        "generated_at": NOW,
        "task_scope": "static_only_no_mworks_gui_no_mcp_no_model_edits",
        "ownership_summary": [
            {
                "owner_surface": "References/MWORKS/QuadrotorModel",
                "classification": "official_upstream_baseline",
                "write_policy": "read_only_do_not_destructively_rewrite",
                "current_use": "baseline adapters under MoSimQuadrotorModel.Baseline and regression reference",
            },
            {
                "owner_surface": "Models/MoSimQuadrotorModel",
                "classification": "formal_project_package_surface",
                "write_policy": "formal wrapper/package surface; real migration requires later scoped task",
                "current_use": "11 top-level categories and package/order surfaces for user navigation and future audit",
            },
            {
                "owner_surface": "Models/QuadrotorExperiments",
                "classification": "legacy_experiment_pool_and_compatibility_source",
                "write_policy": "preserve old paths and flat compatibility aliases until migration batches pass live gates",
                "current_use": "actual legacy implementations and categorized source surfaces for experiments/smokes",
            },
            {
                "owner_surface": "Models/QuadrotorControllerBlocks",
                "classification": "controller_block_library_and_package_shell",
                "write_policy": "preserve flat controller implementations and backup dirs; formal controller surface via category package aliases",
                "current_use": "controller block categories consumed by MoSimQuadrotorModel.Controllers",
            },
        ],
        "formal_categories": formal_categories,
        "legacy_quadrotor_experiments_categories": legacy_dirs,
        "controller_blocks_surface": controller_surface,
        "official_quadrotor_model_surface": references_surface,
        "counts": {
            "mosim_formal_top_categories": len(mosim_root_order),
            "mosim_formal_ordered_child_entries": sum(c["order_count"] for c in formal_categories),
            "quadrotor_experiments_category_dirs": len(legacy_dirs),
            "quadrotor_experiments_category_mo_files_in_dirs": sum(d["mo_file_count"] for d in legacy_dirs),
            "quadrotor_controller_flat_mo_files": len(controller_mo_files),
            "quadrotor_controller_backup_dirs": len(controller_backup_dirs),
        },
        "claim_boundary": "Static ownership and classification only; no package-browser acceptance, graphical/layout/wiring acceptance, check_model, simulation, controller performance, planner_ready, runtime ack, mission success, or closed_loop.",
    }
    write_json(EVID / "model_ownership_classification.json", classification)

    md = [
        "# Model Ownership Classification",
        "",
        f"Request: `{REQ}`",
        "",
        "This is static-only evidence. It classifies current package ownership and future audit surfaces without opening MWORKS, calling MCP, or editing model implementation files.",
        "",
        "## Ownership Summary",
        "",
    ]
    for row in classification["ownership_summary"]:
        md.append(f"- `{row['owner_surface']}`: {row['classification']}; policy: {row['write_policy']}; use: {row['current_use']}.")
    md += ["", "## Formal MoSimQuadrotorModel Categories", "", "| Order | Category | Role | Source/dependency | Entries | State |", "|---:|---|---|---|---:|---|"]
    for i, c in enumerate(formal_categories, 1):
        md.append(f"| {i} | `{c['formal_package']}` | {c['role_cn']} | `{c['source_or_dependency_surface']}` | {c['order_count']} | {c['implementation_state']} |")
    md += [
        "",
        "## Legacy Pools",
        "",
        f"- `Models/QuadrotorExperiments`: {len(legacy_dirs)} category directories, {sum(d['mo_file_count'] for d in legacy_dirs)} category `.mo` files observed; root flat compatibility aliases remain in `package.mo`.",
        f"- `Models/QuadrotorControllerBlocks`: {len(controller_mo_files)} flat controller `.mo` files and {len(controller_backup_dirs)} backup directories preserved; category package shell remains the public controller surface.",
        "- `References/MWORKS/QuadrotorModel`: official upstream baseline remains read-only; formal adapters live under `MoSimQuadrotorModel.Baseline`.",
        "",
        "## Boundary",
        "",
        "No live package-browser, layout, wiring, check_model, simulation, controller performance, planner readiness, runtime ack, mission success, or closed_loop claim is made by this artifact.",
    ]
    write_text(EVID / "model_ownership_classification.md", "\n".join(md))

    surface_map = {
        "schema": "mosim.mworks_model_hygiene.formal_package_surface_map.v1",
        "request_id": REQ,
        "generated_at": NOW,
        "root_package": "MoSimQuadrotorModel",
        "root_order_entries": mosim_root_order,
        "root_order_count": len(mosim_root_order),
        "root_order_duplicates": sorted([x for x in set(mosim_root_order) if mosim_root_order.count(x) > 1]),
        "formal_surface_rows": formal_surface_rows,
        "compatibility_surfaces": [
            {"surface": "QuadrotorExperiments.package.mo", "role": "root hidden deprecated aliases preserve old flat load paths"},
            {"surface": "MoSimQuadrotorModel.LegacyCompatibility.LegacyExperimentPool", "role": "formal aggregate backstop, not preferred new entry"},
            {"surface": "QuadrotorControllerBlocks package shell", "role": "controller category aliases preserve flat controller classes"},
        ],
        "static_validation": {
            "no_mosim_implementation_mo_files_observed": len([p for p in (ROOT / "Models/MoSimQuadrotorModel").rglob("*.mo") if p.name != "package.mo"]) == 0,
            "mosim_package_order_has_11_entries": len(mosim_root_order) == 11,
            "mosim_package_order_duplicates": sorted([x for x in set(mosim_root_order) if mosim_root_order.count(x) > 1]),
            "controller_backup_dirs_not_in_public_order": not any(x in order_entries("Models/QuadrotorControllerBlocks/package.order") for x in controller_backup_dirs),
            "official_baseline_treated_read_only": True,
        },
    }
    write_json(EVID / "formal_package_surface_map.json", surface_map)

    recommendations = [
        ("P0_before_next_live_audit", "Package browser visibility", "Use MoSimQuadrotorModel root and the 11 ordered categories as the user-facing entry; keep QuadrotorExperiments visible only as legacy compatibility/reference pool.", "Requires live package-browser review, not a file move."),
        ("P0_next_static_or_live_batch", "QuadrotorExperiments old flat aliases", "Do not delete old flat aliases yet. After scenario YAML/scripts/docs migrate to MoSimQuadrotorModel names and live checks pass, mark selected aliases as permanent legacy or retire candidate.", "Retirement would break historical scripts/evidence without reference update and live gates."),
        ("P1_migration_batch", "Dynamics naming", "Treat MoSimQuadrotorModel.Dynamics.RotorActuatorCore and PhysicalWrenchAdapter as future canonical names; keep source labels linking to QuadrotorExperiments.DynamicsUpgrade until check_model/smoke evidence is rerun.", "Canonical implementation migration requires explicit .mo moves/renames and live checks."),
        ("P1_migration_batch", "Robustness nested grouping", "If users need browsable subfolder-style entries for PIDBaselines and RotorLoss, create real subpackage directories in a later task or accept embedded package declarations as current static surface.", "015 forbids creating/moving implementation directories."),
        ("P1_controller_library", "QuadrotorControllerBlocks backup directories", "Keep five *_backup directories out of package.order and public controller categories. Later decide archive/delete only with explicit permission and hash evidence.", "015 forbids move/delete/archive."),
        ("P1_graphical_review", "White/blank GUI surfaces reported by user", "Queue graphical/layout review for System.Architecture, SceneTrace.Isolation, Planning display/map, and controller graphical blocks with foreground/maximized evidence owned by PMO/CoAgentOps when live review is authorized.", "Needs live GUI screenshots and cannot be resolved statically."),
        ("P2_cleanup", "LegacyCompatibility naming", "Keep LegacyExperimentPool as a single aggregate until the project chooses permanent aliases. Avoid flattening all 100+ legacy names under formal package surface.", "Flattening would obscure canonical categories and may create duplicate names."),
    ]
    rec_md = [
        "# Naming Cleanup Recommendations",
        "",
        f"Request: `{REQ}`",
        "",
        "These are non-destructive recommendations only. 015 did not rename, move, delete, archive, or edit model implementation files.",
        "",
        "| Priority | Area | Recommendation | Why not done in 015 |",
        "|---|---|---|---|",
    ]
    for priority, area, recommendation, reason in recommendations:
        rec_md.append(f"| {priority} | {area} | {recommendation} | {reason} |")
    write_text(EVID / "naming_cleanup_recommendations.md", "\n".join(rec_md))

    base_names = [
        "MoSimQuadrotorModel",
        "MoSimQuadrotorModel.Baseline",
        "MoSimQuadrotorModel.Dynamics",
        "MoSimQuadrotorModel.Missions",
        "MoSimQuadrotorModel.Controllers",
        "MoSimQuadrotorModel.Robustness",
        "MoSimQuadrotorModel.Planning",
        "MoSimQuadrotorModel.SceneTrace",
        "MoSimQuadrotorModel.System",
        "MoSimQuadrotorModel.Formation",
        "MoSimQuadrotorModel.Support",
        "MoSimQuadrotorModel.Controllers.AWFFPidBlocks",
        "MoSimQuadrotorModel.Controllers.InnovationControllers",
        "MoSimQuadrotorModel.Controllers.FaultAllocationControllers",
        "MoSimQuadrotorModel.Planning.NavigationDisplay",
        "MoSimQuadrotorModel.Planning.OpenBlocksColorMapReview",
        "MoSimQuadrotorModel.System.Architecture",
        "MoSimQuadrotorModel.SceneTrace.Isolation",
        "MoSimQuadrotorModel.Robustness.RotorLoss",
        "MoSimQuadrotorModel.LegacyCompatibility.LegacyExperimentPool",
    ]
    queue = []
    for i, name in enumerate(base_names, 1):
        if name == "MoSimQuadrotorModel":
            batch = "package_browser_visibility"
            expected = ["root package visible with 11 ordered categories", "no unexpected flat implementation clutter under formal package root"]
        elif any(x in name for x in ["NavigationDisplay", "OpenBlocksColorMapReview"]):
            batch = "planning_display_or_map_visual_screen"
            expected = ["visible display/map model opens to meaningful diagram", "blank/white/proxy surface recorded as issue if present"]
        elif "System.Architecture" in name:
            batch = "system_graphical_layout_screen"
            expected = ["complete system graphical architecture opens", "missing wires, unreadable routing, blank panels listed"]
        elif "SceneTrace.Isolation" in name:
            batch = "factory_trace_wiring_isolation_screen"
            expected = ["trace isolation package and representative smoke diagrams visible", "wiring boundary labels readable"]
        elif "Controllers." in name:
            batch = "controller_category_package_browser_and_topology_screen"
            expected = ["controller category visible", "representative child graphical/equation bridge distinction recorded"]
        elif "Robustness.RotorLoss" in name:
            batch = "package_browser_visibility_then_r1_serialized_check_model_sample"
            expected = ["nested robustness group visible", "representative rotor-loss class selected for later check_model only by R1/R2 serialized live task"]
        else:
            batch = "package_browser_visibility"
            expected = ["package browser category visible", "order and child entries match static package.order"]
        queue.append({
            "queue_index": i,
            "target": name,
            "audit_batch": batch,
            "static_source_surface": "Models/MoSimQuadrotorModel",
            "resource_lock": "single_reusable_MWORKS_Sysplorer_window_serialized_with_R1_R2",
            "required_pre_live_gate": "latest CoAgentOps activation/window patrol or bounded current-turn check if live task packet permits it",
            "expected_live_evidence_later": expected,
            "stop_conditions_later": [
                "demo/login/authorization/gui-error/mixed/unknown MWORKS state",
                "new window required",
                "MCP session reuse violation",
                "check_model/layout requires model edits outside live audit scope",
            ],
            "015_status": "queued_not_executed_static_only",
        })

    next_queue = {
        "schema": "mosim.mworks_model_hygiene.next_live_audit_queue.v1",
        "request_id": REQ,
        "generated_at": NOW,
        "source_inputs": [
            "Results/mworks_model_hygiene/20260607_012_mosimquad_graphical_audit_queue_refinement/first_batch_live_audit_queue.json",
            "Results/mworks_model_hygiene/20260608_014_mosimquad_alias_category_migration_plan/category_order_coverage.json",
            "Current Models/MoSimQuadrotorModel package surfaces",
        ],
        "queue_count": len(queue),
        "max_first_batch_count": 20,
        "queue": queue,
        "serialization_plan": {
            "resource_lock": "one reusable MWORKS/Sysplorer session; no parallel R1/R2 live model operations",
            "phase_order": [
                "activation/window patrol reference",
                "package-browser visibility screenshot/observation",
                "representative graphical/layout/wiring screenshot/observation",
                "R1/R2 serialized check_model smoke only in a separate scoped task",
            ],
            "r2_scope": "package browser, diagram/layout/wiring readability observations",
            "r1_scope": "dynamics/control check_model/simulation behavior evidence where needed",
        },
        "claim_boundary": "Queue only; no live audit was executed in 015.",
    }
    write_json(EVID / "next_live_audit_queue.json", next_queue)

    blockers = {
        "schema": "mosim.mworks_model_hygiene.unresolved_classification_blockers.v1",
        "request_id": REQ,
        "generated_at": NOW,
        "blocking_for_015_completion": False,
        "blockers": [
            {
                "kind": "live_package_browser_not_run",
                "scope": "all formal MoSimQuadrotorModel categories",
                "reason": "015 is static-only and forbids MWORKS/Sysplorer/Syslab GUI, screenshots, MCP, check_model, simulation, and Smart Layout.",
                "follow_up": "Dispatch a separate live package/browser + graphical audit task using current patrol/session rules.",
            },
            {
                "kind": "implementation_migration_not_performed",
                "scope": "QuadrotorExperiments -> MoSimQuadrotorModel",
                "reason": "Formal package surfaces are wrappers/aliases; implementation files remain in legacy pools by design.",
                "follow_up": "For each migration batch, explicitly permit file moves/renames and update scenario YAML/scripts/docs plus compatibility aliases and live check_model evidence.",
            },
            {
                "kind": "official_baseline_read_only",
                "scope": "References/MWORKS/QuadrotorModel",
                "reason": "Official baseline must remain regression dependency and was not edited.",
                "follow_up": "Use MoSimQuadrotorModel.Baseline adapters for comparison; only change official reference with separate explicit approval.",
            },
            {
                "kind": "controller_backup_dirs_preserved",
                "scope": "Models/QuadrotorControllerBlocks/*_backup",
                "reason": "015 forbids archive/delete/rename; backups remain out of public package.order.",
                "follow_up": "Later hygiene task may hash and archive/delete backup dirs only if explicitly authorized.",
            },
            {
                "kind": "blank_or_white_gui_surfaces_require_live_review",
                "scope": "user-reported white GUI surfaces and graphical layout concerns",
                "reason": "Static files cannot prove what the live Qt/Sysplorer package browser or diagram canvas renders.",
                "follow_up": "Queue foreground/maximized live review with screenshot observations when PMO/CoAgentOps authorizes GUI audit.",
            },
            {
                "kind": "nested_package_order_real_subdir_not_created",
                "scope": "MoSimQuadrotorModel.Robustness.PIDBaselines and RotorLoss",
                "reason": "Nested packages are embedded declarations inside Robustness/package.mo; no real subdirectories were created in 014/015.",
                "follow_up": "If package browser needs true subfolder package.order, create a later package-surface task permitting subdirectories.",
            },
        ],
    }
    write_json(EVID / "unresolved_classification_blockers.json", blockers)

    scope_summary = f"""# Scope Diff Summary

Request: `{REQ}`

015 generated static classification and live-audit queue evidence only.

## Files Written

- `Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/model_ownership_classification.md`
- `Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/model_ownership_classification.json`
- `Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/formal_package_surface_map.json`
- `Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/naming_cleanup_recommendations.md`
- `Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/next_live_audit_queue.json`
- `Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/unresolved_classification_blockers.json`
- this `scope_diff_summary.md`
- the 015 return packet under `Results/agent_packets/returns/` after packet write

## Explicit Non-Actions

- No `.mo`, `package.mo`, or `package.order` files were edited.
- No implementation files were moved, deleted, renamed, or archived.
- `References/MWORKS/QuadrotorModel` was read-only.
- No ROS2, UE, FAST-LIO, planner, controller runtime/config, or Sunray asset files were touched.
- No MWORKS/Sysplorer/Syslab GUI, screenshot, MCP, `check_model`, `SimulateModel`, Smart Layout, `ClearAll`, or `ChangeDirectory` was used.
- No Git stage, unstage, revert, clean, commit, or push was performed.

## Claim Boundary

015 claims only static package ownership/classification, naming cleanup recommendations, unresolved blockers, and a future live audit queue. It is not package-browser acceptance, graphical/layout/wiring acceptance, `check_model`, simulation, controller performance, planner readiness, runtime ack, mission success, or closed_loop.
"""
    write_text(EVID / "scope_diff_summary.md", scope_summary)

    actual_outputs = [
        "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/model_ownership_classification.md and .json: static ownership/classification map covering official QuadrotorModel, formal MoSimQuadrotorModel, legacy QuadrotorExperiments, and QuadrotorControllerBlocks.",
        "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/formal_package_surface_map.json: formal package surface/order map for the 11 MoSimQuadrotorModel categories and compatibility surfaces.",
        "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/naming_cleanup_recommendations.md: non-destructive naming/category cleanup recommendations and deferred migration decisions.",
        "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/next_live_audit_queue.json: 20-target serialized future live package-browser/layout/wiring/check queue with resource locks and stop conditions.",
        "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/unresolved_classification_blockers.json: precise unresolved blockers for live review, real implementation migration, official baseline edits, controller backup handling, and nested real subpackages.",
        "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/scope_diff_summary.md: explicit allowed-scope diff and non-action summary.",
    ]

    packet = {
        "schema": "mosim.agent_packet.return.v1",
        "request_id": REQ,
        "status": "completed",
        "task_class": "static_inventory_only",
        "quality_status": "completed_static_classification_and_live_audit_queue",
        "source": "static_file_validation_no_gui_no_mcp_no_check_model_no_simulation",
        "completed_at": NOW,
        "origin_thread_id": "019e9868-83ea-70f0-92c5-a3a408bd78c6",
        "target_thread": "MoSim｜MWORKS动力学与控制验证部-R2",
        "target_thread_id": "019e9999-b0d3-7682-bccd-faef08fcf1df",
        "department_local_goal": "在 014 完成 MoSimQuadrotorModel 全分类 wrapper/package surface 后，静态整理当前正式包、旧实验池、控制器库和官方基线的 ownership/classification，并给出下一轮 live package-browser/图形审核队列。",
        "critical_path_steps": [
            "读取 015 task packet、AGENTS.md、new_conversation_context、MoSimQuadrotorModel 迁移设计文档、agent_task_ledger、mworks-model-context、mworks-sysblock-graphical-modeling、014 return/evidence、012 return/evidence 和当前模型包树。",
            "确认 015 是 static-only：live_mworks_touched=false，禁止 MWORKS/Sysplorer/Syslab GUI/MCP/check_model/SimulateModel/Smart Layout/截图/窗口操作。",
            "盘点 Models/MoSimQuadrotorModel 的 11 个正式分类 package.mo/package.order，识别正式 wrapper/category surface 和 extends source/dependency surface。",
            "盘点 Models/QuadrotorExperiments 旧实验池分类目录、.mo 数量、package.order 状态和兼容 alias 角色；保持旧 flat 入口不动。",
            "盘点 Models/QuadrotorControllerBlocks 控制器 flat .mo、7 个 public 分类入口和 5 个 backup 目录不进入 public surface 的状态。",
            "将 official QuadrotorModel、formal MoSimQuadrotorModel、legacy QuadrotorExperiments、controller blocks 和 future live graphical audit surfaces 分开生成工程证据。",
            "写 015 evidence artifacts 和 return packet，并运行 json/tool、department contract、MWORKS live gate、scoped diff checks。",
        ],
        "parallelizable_slices": [
            {"slice": "formal MoSimQuadrotorModel package surface inventory", "status": "completed", "evidence": "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/formal_package_surface_map.json"},
            {"slice": "legacy QuadrotorExperiments and controller block ownership classification", "status": "completed", "evidence": "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/model_ownership_classification.json"},
            {"slice": "naming cleanup recommendations and unresolved blockers", "status": "completed", "evidence": ["Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/naming_cleanup_recommendations.md", "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/unresolved_classification_blockers.json"]},
            {"slice": "future live package-browser/layout/wiring/check queue serialization", "status": "completed", "evidence": "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/next_live_audit_queue.json"},
        ],
        "subagent_plan": "available_but_not_useful",
        "subagent_plan_reason": "015 is deterministic static-only package/source inventory and evidence synthesis. The useful work is current checkout parsing plus 014/012 evidence consolidation; a disposable subagent would duplicate reads, cannot perform live GUI/MCP, and would add merge risk without independent resource benefit.",
        "subagents_used": [],
        "verification_gates": [
            {"gate": "required_read_first", "status": "pass", "evidence": ["AGENTS.md", "Docs/Workflows/new_conversation_context.md", "Docs/Design/12_MoSimQuadrotorModel模型归档与迁移计划.md", "Docs/Workflows/agent_task_ledger.md", "C:/Users/HP/.codex/skills/mworks-model-context/SKILL.md", "C:/Users/HP/.codex/skills/mworks-sysblock-graphical-modeling/SKILL.md", "014 return/evidence", "012 return/evidence", "current model package trees"]},
            {"gate": "static_only_boundary", "status": "pass", "details": "No MWORKS/Sysplorer/Syslab GUI/window/screenshot/MCP/check_model/SimulateModel/Smart Layout/ClearAll/ChangeDirectory was used."},
            {"gate": "package_surface_inventory", "status": "pass", "evidence": "formal_package_surface_map.json", "details": "MoSimQuadrotorModel root package.order has 11 entries and no duplicates; all category package.order surfaces were inventoried."},
            {"gate": "ownership_classification", "status": "pass", "evidence": "model_ownership_classification.json", "details": "Official baseline, formal package, legacy experiment pool, controller block library, and future live audit surfaces are separated."},
            {"gate": "next_live_queue_limit_and_serialization", "status": "pass", "evidence": "next_live_audit_queue.json", "details": "Queue has 20 targets, resource-lock and stop-condition fields, and no live acceptance claim."},
            {"gate": "forbidden_scope_preserved", "status": "pass", "details": "No implementation .mo/package/order, official baseline, ROS2/UE/planner/controller/runtime, or Git staging actions were performed."},
        ],
        "manual_review_or_blocker_triggers": [
            "If PMO wants package-browser or white/blank GUI surface diagnosis, dispatch a separate live task with current patrol/session gate and screenshot requirements.",
            "If a formal wrapper fails live loading/check_model, preserve legacy implementation files and return a precise live blocker rather than broad-editing in-place.",
            "If real namespace migration is requested, require an explicit task that permits moving/renaming implementation files and updates scenario YAML/scripts/docs/reports plus compatibility aliases.",
            "If controller backup/upgrade directories should be archived or removed, require explicit deletion/archive authorization and pre/post hash evidence.",
            "If official QuadrotorModel baseline must change, require explicit official-baseline edit approval and regression evidence.",
            "If nested Robustness packages need true subfolders/package.order surfaces, dispatch a later package-surface task permitting new subpackage directories.",
        ],
        "will_not_click_activation_login": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "mworks_activation_patrol_reference": {
            "mode": "not_required_for_static_file_only_015",
            "activation_patrol_owner": "CoAgentOps",
            "recent_patrol_required": False,
            "reason": "015 task packet marks live_mworks_touched=false and explicitly forbids opening, switching, maximizing, screenshotting, or operating MWORKS/Sysplorer/Syslab. No live surface/window evidence was touched.",
        },
        "engineering_output_mode": "static_inventory_only",
        "model_ownership_classification": {
            "evidence": "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/model_ownership_classification.json",
            "summary": classification["ownership_summary"],
            "counts": classification["counts"],
        },
        "classification_map_artifacts": [
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/model_ownership_classification.md",
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/model_ownership_classification.json",
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/formal_package_surface_map.json",
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/naming_cleanup_recommendations.md",
        ],
        "formal_package_surface_map": {
            "evidence": "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/formal_package_surface_map.json",
            "root_order_entries": mosim_root_order,
            "root_order_count": len(mosim_root_order),
            "root_order_duplicates": [],
            "formal_surface_count": len(formal_surface_rows),
        },
        "naming_cleanup_recommendations": {
            "evidence": "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/naming_cleanup_recommendations.md",
            "recommendation_count": len(recommendations),
            "destructive_changes_recommended_for_015": False,
        },
        "next_live_audit_queue": {
            "evidence": "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/next_live_audit_queue.json",
            "queue_count": len(queue),
            "max_first_batch_count": 20,
            "resource_lock": next_queue["serialization_plan"]["resource_lock"],
            "not_executed_in_015": True,
        },
        "unresolved_classification_blockers": {
            "evidence": "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/unresolved_classification_blockers.json",
            "blocking_for_015_completion": False,
            "blocker_count": len(blockers["blockers"]),
            "kinds": [b["kind"] for b in blockers["blockers"]],
        },
        "actual_engineering_outputs": actual_outputs,
        "evidence_paths": [
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/model_ownership_classification.md",
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/model_ownership_classification.json",
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/formal_package_surface_map.json",
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/naming_cleanup_recommendations.md",
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/next_live_audit_queue.json",
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/unresolved_classification_blockers.json",
            "Results/mworks_model_hygiene/20260608_015_mosimquad_static_classification_live_audit_queue/scope_diff_summary.md",
        ],
        "forbidden_actions_confirmed": {
            "edited_mo_package_or_package_order_files": False,
            "moved_deleted_renamed_or_archived_implementation_files": False,
            "edited_references_official_quadrotor_model": False,
            "edited_models_quadrotor_experiments_or_controller_blocks_implementation_files": False,
            "opened_closed_switched_maximized_restarted_or_screenshotted_mworks_sysplorer_syslab_window": False,
            "operated_mworks_sysplorer_syslab_gui": False,
            "called_sysplorer_syslab_mworks_mcp": False,
            "ran_check_model": False,
            "ran_simulate_model": False,
            "ran_smart_layout_or_diagram_writeback": False,
            "called_clearall_or_changedirectory": False,
            "edited_ros2_ue_fast_lio_planner_controller_runtime_or_configs_or_sunray_assets": False,
            "staged_unstaged_reverted_cleaned_committed_or_pushed_git": False,
            "claimed_package_browser_acceptance": False,
            "claimed_graphical_layout_or_wiring_acceptance": False,
            "claimed_controller_performance_planner_ready_runtime_ack_mission_success_simulation_success_closed_loop": False,
        },
        "checker_results": {},
        "claim_boundary": [
            "015 claims only static model ownership/classification evidence, formal package surface mapping, non-destructive naming cleanup recommendations, unresolved blocker rows, and a queued plan for future live MWORKS audits.",
            "015 does not claim live Sysplorer package-browser acceptance, graphical/layout acceptance, wiring acceptance, check_model, simulation, controller performance, planner readiness, runtime acknowledgement, mission success, or closed_loop.",
            "015 does not move, delete, rename, archive, or edit implementation files; real migration and live audits must be later separately scoped tasks serialized with MWORKS R1/R2 resource locks.",
        ],
    }
    write_json(RET, packet)


if __name__ == "__main__":
    main()
