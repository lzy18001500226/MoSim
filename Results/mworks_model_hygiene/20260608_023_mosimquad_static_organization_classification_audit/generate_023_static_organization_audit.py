#!/usr/bin/env python3
"""Generate R2 023 static organization/classification audit evidence."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REQUEST_ID = "PMO-MWORKS-R2-MOSIMQUAD-STATIC-ORGANIZATION-CLASSIFICATION-AUDIT-20260608-023"
EVIDENCE_DIR = ROOT / "Results" / "mworks_model_hygiene" / "20260608_023_mosimquad_static_organization_classification_audit"
RETURN_PACKET = ROOT / "Results" / "agent_packets" / "returns" / f"{REQUEST_ID}.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_order(dir_path: Path) -> list[str]:
    path = dir_path / "package.order"
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def package_dirs(root: Path) -> list[Path]:
    return sorted([p for p in root.rglob("*") if p.is_dir() and (p / "package.mo").exists()])


def package_order_report(root: Path) -> dict:
    reports = []
    for pkg_dir in [root] + package_dirs(root):
        if pkg_dir != root and pkg_dir == root:
            continue
        entries = read_order(pkg_dir)
        seen = set()
        duplicates = []
        for entry in entries:
            if entry in seen:
                duplicates.append(entry)
            seen.add(entry)
        embedded_declarations = []
        if (pkg_dir / "package.mo").exists():
            embedded_declarations = [
                name
                for name in find_model_declared_names(pkg_dir / "package.mo")
                if name != "package"
            ]
        mo_children = sorted(p.stem for p in pkg_dir.glob("*.mo") if p.name != "package.mo")
        child_packages = sorted(p.name for p in pkg_dir.iterdir() if p.is_dir() and (p / "package.mo").exists())
        resolved_public_sources = set(mo_children) | set(child_packages) | set(embedded_declarations)
        reports.append(
            {
                "package_dir": rel(pkg_dir),
                "package": ".".join(pkg_dir.relative_to(root.parent).parts),
                "order_entries": entries,
                "order_count": len(entries),
                "order_duplicates": duplicates,
                "embedded_declarations_in_package_mo": sorted(embedded_declarations),
                "sibling_mo_children": mo_children,
                "child_package_dirs": child_packages,
                "unordered_sibling_mo_children": sorted(set(mo_children) - set(entries)),
                "missing_order_entries_as_public_source": sorted(
                    entry
                    for entry in entries
                    if entry not in resolved_public_sources
                ),
            }
        )
    return {
        "root": rel(root),
        "package_count": len(reports),
        "root_order_entries": read_order(root),
        "reports": reports,
    }


def mo_files(root: Path) -> list[str]:
    return sorted(rel(p) for p in root.rglob("*.mo"))


def find_model_declared_names(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return re.findall(r"^\s*(?:model|block|package|function|record|connector|type)\s+([A-Za-z_][A-Za-z0-9_]*)\b", text, flags=re.M)


def current_tree_inventory() -> dict:
    mosim = ROOT / "Models" / "MoSimQuadrotorModel"
    legacy = ROOT / "Models" / "QuadrotorExperiments"
    controllers = ROOT / "Models" / "QuadrotorControllerBlocks"
    legacy_category_dirs = [p for p in legacy.iterdir() if p.is_dir() and (p / "package.mo").exists()]
    return {
        "mosim_quadrotor_model": {
            "package_order": package_order_report(mosim),
            "mo_files": mo_files(mosim),
            "top_category_count": len(read_order(mosim)),
            "ordered_child_entry_count_excluding_root": sum(len(read_order(p)) for p in package_dirs(mosim)),
        },
        "quadrotor_experiments": {
            "package_order": package_order_report(legacy),
            "mo_files": mo_files(legacy),
            "category_dirs": [rel(p) for p in sorted(legacy_category_dirs)],
            "category_dir_count": len(legacy_category_dirs),
            "implementation_mo_count_excluding_package_mo": len([p for p in legacy.rglob("*.mo") if p.name != "package.mo"]),
        },
        "quadrotor_controller_blocks": {
            "package_order": package_order_report(controllers),
            "mo_files": mo_files(controllers),
            "flat_controller_mo_count": len([p for p in controllers.glob("*.mo") if p.name != "package.mo"]),
            "backup_upgrade_mo_count": len(list(controllers.glob("*_backup/upgrade/*/*.mo"))),
        },
    }


MOSIM_CATEGORY_ROLES = [
    {
        "category": "Baseline",
        "chinese_annotation": "官方基线适配：只包装官方 Example1/2/3 和 QuadChassis，用于回归对照。",
        "source": "QuadrotorModel official package",
        "classification": "formal_project_surface_keep",
        "next_action": "保持正式入口；后续 live check_model/package-browser 只验证可加载性，不改官方基线。",
    },
    {
        "category": "Dynamics",
        "chinese_annotation": "Sunray150 动力学升级：旋翼/执行器/物理力矩接口与烟测入口。",
        "source": "QuadrotorExperiments.DynamicsUpgrade",
        "classification": "formal_project_surface_migrate_to_real_source_later",
        "next_action": "保留当前 wrapper；后续单独任务再决定是否把真实实现迁出旧实验池。",
    },
    {
        "category": "Parameters",
        "chinese_annotation": "参数来源与标定记录：记录 Sunray150 参数来源，不等同于参数验收。",
        "source": "MoSimQuadrotorModel.Parameters",
        "classification": "formal_project_surface_keep",
        "next_action": "后续 R1 参数/动力学验证后再补 live acceptance 证据。",
    },
    {
        "category": "Missions",
        "chinese_annotation": "正式任务场景：官方轨迹任务和主控制器闭环对比入口。",
        "source": "QuadrotorExperiments.OfficialScenarios",
        "classification": "migrate_to_mosim_formal",
        "next_action": "优先迁移 YAML/scripts/docs authoritative references 到 MoSimQuadrotorModel.Missions。",
    },
    {
        "category": "Controllers",
        "chinese_annotation": "控制器库入口：接入 QuadrotorControllerBlocks 的七个分类控制器包面。",
        "source": "QuadrotorControllerBlocks",
        "classification": "formal_project_surface_keep_controller_library_reference",
        "next_action": "保留控制器实现库所有权；MoSimQuadrotorModel.Controllers 只作为浏览入口。",
    },
    {
        "category": "Robustness",
        "chinese_annotation": "鲁棒/故障/安全：质量扰动、阵风、电机损失、故障分配和安全返航。",
        "source": "QuadrotorExperiments.RobustFaultScenarios",
        "classification": "migrate_to_mosim_formal_with_nested_batches",
        "next_action": "拆成 Mass20、WindGust、RotorLoss、Safety 四批；PIDBaselines 保留为对比基线。",
    },
    {
        "category": "Planning",
        "chinese_annotation": "规划与地图场景：轨迹参考、障碍场、走廊门控和地图审查辅助。",
        "source": "QuadrotorExperiments.PlanningScenarios",
        "classification": "mixed_migrate_and_review_helper",
        "next_action": "闭环规划场景迁入正式队列；NavigationDisplay/ColorMapReview 标为 review/support，不作为控制性能验收。",
    },
    {
        "category": "SceneTrace",
        "chinese_annotation": "UE 场景 trace 与显示隔离：已接入场景和逐层隔离诊断入口。",
        "source": "QuadrotorExperiments.SceneTraceScenarios + TraceIsolation",
        "classification": "mixed_migrate_and_diagnostic_ladder",
        "next_action": "AcceptedScenes 可进入正式 trace 队列；TraceIsolation 01-30 保留诊断梯，不作为用户任务目录。",
    },
    {
        "category": "System",
        "chinese_annotation": "系统级图形和硬件抽象：完整系统故障场景与模块化接口。",
        "source": "QuadrotorExperiments.SystemArchitecture + SystemModules",
        "classification": "migrate_as_alias_then_live_validate",
        "next_action": "后续 live 图形/走线审核优先检查 CompleteSystemGraphical 与模块 package-browser。",
    },
    {
        "category": "Formation",
        "chinese_annotation": "多机编队扩展：三角编队与 8 字任务。",
        "source": "QuadrotorExperiments.FormationScenarios",
        "classification": "migrate_to_mosim_formal_after_single_uav_gates",
        "next_action": "单机任务/鲁棒包面通过后再进入 live 审核；当前只保留正式入口。",
    },
    {
        "category": "Support",
        "chinese_annotation": "支撑工具模型：trace 表、内联引用、lookup smoke、MCP 状态烟测。",
        "source": "QuadrotorExperiments.SupportModels",
        "classification": "keep_as_support_not_user_mission",
        "next_action": "不混入 Missions/Planning；仅作为支撑包面和调试依赖。",
    },
    {
        "category": "LegacyCompatibility",
        "chinese_annotation": "旧入口兼容：保留历史脚本/证据路径，不作为新开发首选入口。",
        "source": "QuadrotorExperiments root hidden aliases",
        "classification": "keep_compatibility_until_references_migrated",
        "next_action": "待 YAML/scripts/docs/live gates 全部迁移后，再决定哪些旧 alias 长期保留。",
    },
]


LEGACY_DISPOSITION = [
    {
        "legacy_package": "QuadrotorExperiments.OfficialScenarios",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "OfficialScenarios"),
        "target_surface": "MoSimQuadrotorModel.Missions",
        "disposition": "migrate_to_mosim_formal",
        "reason": "这些是正式任务/控制器闭环对比入口，已经有 MoSimQuadrotorModel.Missions wrapper 和中文说明。",
        "keep_legacy": "保留旧路径作为 compatibility alias/source until YAML/scripts/docs and live checks migrate.",
    },
    {
        "legacy_package": "QuadrotorExperiments.ControllerBaselines",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "ControllerBaselines"),
        "target_surface": "MoSimQuadrotorModel.Controllers and legacy ControllerBaselines compatibility",
        "disposition": "keep_legacy_reference_or_baseline",
        "reason": "这些是 PID/AWFF 对比基线，不应被当作新主线任务；控制器正式库入口已经转到 QuadrotorControllerBlocks。",
        "keep_legacy": "长期保留对比/报告复现实验入口，后续只补清晰中文注释和旧入口说明。",
    },
    {
        "legacy_package": "QuadrotorExperiments.RobustFaultScenarios",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "RobustFaultScenarios"),
        "target_surface": "MoSimQuadrotorModel.Robustness",
        "disposition": "migrate_to_mosim_formal_with_nested_batches",
        "reason": "质量扰动、阵风、安全滤波和故障场景是工程价值主线，应分批归入 Robustness。",
        "keep_legacy": "旧路径保留，PIDBaselines 子包保持对比基线而非正式控制改进成果。",
    },
    {
        "legacy_package": "QuadrotorExperiments.RobustFaultScenarios.RotorLoss",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "RobustFaultScenarios" / "RotorLoss"),
        "target_surface": "MoSimQuadrotorModel.Robustness.RotorLoss",
        "disposition": "migrate_to_mosim_formal",
        "reason": "单/多电机损失、故障分配、阵风叠加是鲁棒控制核心场景。",
        "keep_legacy": "保留旧路径直到 live package-browser/check_model 和结果脚本完成迁移。",
    },
    {
        "legacy_package": "QuadrotorExperiments.RobustFaultScenarios.PIDBaselines",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "RobustFaultScenarios" / "PIDBaselines"),
        "target_surface": "MoSimQuadrotorModel.Robustness.PIDBaselines",
        "disposition": "keep_legacy_reference_or_baseline",
        "reason": "这些是扰动/故障下的 PID 对照，不应包装成新控制成果。",
        "keep_legacy": "保留为 baseline/reference，中文注释标明对比基线。",
    },
    {
        "legacy_package": "QuadrotorExperiments.PlanningScenarios",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "PlanningScenarios"),
        "target_surface": "MoSimQuadrotorModel.Planning",
        "disposition": "mixed_migrate_and_review_helper",
        "reason": "OpenBlocks/CorridorGate 闭环可迁入正式规划场景；NavigationDisplay/ColorMapReview 是审查辅助。",
        "keep_legacy": "保留旧路径；review helper 后续可放 Support/Planning.ReviewTools，不能声明控制验收。",
    },
    {
        "legacy_package": "QuadrotorExperiments.SceneTraceScenarios",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "SceneTraceScenarios"),
        "target_surface": "MoSimQuadrotorModel.SceneTrace.AcceptedScenes",
        "disposition": "migrate_to_mosim_formal_after_live_review",
        "reason": "UE Factory/Derelict trace smoke 有工程价值，但需 live 图形/trace 证据才能升级为 accepted scene。",
        "keep_legacy": "保留旧路径和 smoke 标签，避免误称 UE runtime acceptance。",
    },
    {
        "legacy_package": "QuadrotorExperiments.TraceIsolation",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "TraceIsolation"),
        "target_surface": "MoSimQuadrotorModel.SceneTrace.Isolation",
        "disposition": "diagnostic_ladder_keep_out_of_primary_user_surface",
        "reason": "FactoryTraceIso01-30 是逐层接线/显示隔离诊断梯，不是正式任务场景。",
        "keep_legacy": "保留为诊断工具；后续 package-browser 可折叠或中文标明诊断用途。",
    },
    {
        "legacy_package": "QuadrotorExperiments.DynamicsUpgrade",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade"),
        "target_surface": "MoSimQuadrotorModel.Dynamics",
        "disposition": "migrate_to_mosim_formal_source_later",
        "reason": "动力学升级是正式包核心，但 023 不移动真实实现；021 已修正隐藏 sibling .mo 静态解析边界。",
        "keep_legacy": "保留旧实现文件直到 R1/R2 live gates 和 source migration task 明确允许。",
    },
    {
        "legacy_package": "QuadrotorExperiments.SystemArchitecture",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "SystemArchitecture"),
        "target_surface": "MoSimQuadrotorModel.System.Architecture",
        "disposition": "migrate_as_alias_then_live_validate",
        "reason": "完整系统图形和故障场景需要 R2 live 图形/走线审核；当前仅可作为静态 alias surface。",
        "keep_legacy": "保留旧路径；CompleteSystemGraphical 是优先 live 审核对象。",
    },
    {
        "legacy_package": "QuadrotorExperiments.SystemModules",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "SystemModules"),
        "target_surface": "MoSimQuadrotorModel.System.Modules",
        "disposition": "migrate_as_alias_then_live_validate",
        "reason": "Perception/FlightController/MissionComputer 等模块是系统包面候选，但需要图形/端口 live 审核。",
        "keep_legacy": "保留模块旧路径和中文接口说明，禁止未经审核改连线。",
    },
    {
        "legacy_package": "QuadrotorExperiments.SupportModels",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "SupportModels"),
        "target_surface": "MoSimQuadrotorModel.Support",
        "disposition": "keep_as_support_not_user_mission",
        "reason": "trace/MCP/lookup helper 是工具依赖，不应显示为正式任务或控制结果。",
        "keep_legacy": "保留旧路径并标注工具/支撑用途。",
    },
    {
        "legacy_package": "QuadrotorExperiments.FormationScenarios",
        "current_entries": read_order(ROOT / "Models" / "QuadrotorExperiments" / "FormationScenarios"),
        "target_surface": "MoSimQuadrotorModel.Formation",
        "disposition": "migrate_to_mosim_formal_after_single_uav_gates",
        "reason": "编队场景有展示价值，但应排在单机动力学/鲁棒/规划 gates 之后。",
        "keep_legacy": "保留旧路径到 formation live audit 通过。",
    },
]


OBSOLETE_OR_REVIEW_HELPERS = [
    {
        "surface": "QuadrotorExperiments.TraceIsolation.FactoryTraceIso01..FactoryTraceIso30",
        "classification": "diagnostic_ladder_not_obsolete_but_not_primary_surface",
        "recommendation": "在中文说明中标为 trace/接线逐层诊断，后续 package browser 可放到 SceneTrace.Isolation 折叠入口，不进入 Missions/Planning 主线。",
    },
    {
        "surface": "QuadrotorExperiments.PlanningScenarios.PlanningNavigationDisplay",
        "classification": "review_display_helper",
        "recommendation": "保留为 Planning 支撑/显示审查对象；不能当作规划闭环性能验收。",
    },
    {
        "surface": "QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksColorMapReview",
        "classification": "review_display_helper",
        "recommendation": "保留为地图/颜色审查入口；下一步 live 图形审核只检查显示完整性，不声明控制性能。",
    },
    {
        "surface": "Any user-observed white/blank package/browser or diagram tiles",
        "classification": "live_graphical_review_required",
        "recommendation": "静态审查不能解释白色/空白 GUI；等待 approved no-start MWORKS route 后由 R2 做截图和 written observation。",
    },
    {
        "surface": "QuadrotorControllerBlocks *_backup/upgrade",
        "classification": "private_backup_not_public_package_surface",
        "recommendation": "继续排除在 public package.order 和 MoSimQuadrotorModel.Controllers 分类入口之外。",
    },
]


SAFE_MIGRATION_QUEUE = [
    {
        "batch": "023-A missions authority references",
        "scope": "YAML/scripts/docs/report references only after live package load/check succeeds",
        "targets": "MoSimQuadrotorModel.Missions.*",
        "action": "migrate authoritative references from QuadrotorExperiments.OfficialScenarios to MoSimQuadrotorModel.Missions; keep legacy aliases",
        "risk": "medium_requires_live_check_model",
    },
    {
        "batch": "023-B robustness nested review",
        "scope": "Robustness Mass20/WindGust/Safety/RotorLoss split",
        "targets": "MoSimQuadrotorModel.Robustness.*",
        "action": "create user-facing Chinese sub-buckets in future package surface if PMO approves source/package edits; keep PIDBaselines labeled as baseline",
        "risk": "medium_large_surface_requires_serialized_live",
    },
    {
        "batch": "023-C planning helper separation",
        "scope": "Planning closed-loop scenarios versus display/review helpers",
        "targets": "MoSimQuadrotorModel.Planning",
        "action": "mark NavigationDisplay and ColorMapReview as review/support; migrate OpenBlocks/CorridorGate closed-loop references after live review",
        "risk": "medium_user_visible_category_semantics",
    },
    {
        "batch": "023-D scene trace diagnostic folding",
        "scope": "SceneTrace AcceptedScenes and Isolation",
        "targets": "MoSimQuadrotorModel.SceneTrace",
        "action": "keep FactoryTraceIso01-30 as diagnostic ladder; live review only first/last and representative wiring stages before broader acceptance",
        "risk": "high_requires_graphical_evidence",
    },
    {
        "batch": "023-E system graphical audit",
        "scope": "SystemArchitecture and SystemModules",
        "targets": "MoSimQuadrotorModel.System",
        "action": "queue CompleteSystemGraphical, GPSDropout, BatteryLow, OffboardLoss, MissionFailure, GeofenceBreach and module diagrams for R2 live graphical review",
        "risk": "high_requires_no_start_route_and_layout_review",
    },
    {
        "batch": "023-F legacy compatibility cleanup",
        "scope": "QuadrotorExperiments root hidden aliases",
        "targets": "QuadrotorExperiments package.mo hidden aliases",
        "action": "after all references migrate, decide permanent report-reproducibility aliases versus deprecated hidden aliases; no deletion in static audit",
        "risk": "high_breaks_old_evidence_if_done_early",
    },
]


NEXT_LIVE_QUEUE = [
    {
        "order": 1,
        "target": "MoSimQuadrotorModel root package browser",
        "review": "12 top categories visible with Chinese package description; no unexpected flat legacy clutter.",
        "blocked_until": "approved attach-existing/no-start foreground route exists and reusable main MWORKS window is available",
    },
    {
        "order": 2,
        "target": "MoSimQuadrotorModel.Missions package browser",
        "review": "15 official mission wrappers visible; check labels separate Example1/2/3 and trajectory variants.",
        "blocked_until": "same live route gate",
    },
    {
        "order": 3,
        "target": "MoSimQuadrotorModel.Robustness package browser",
        "review": "PIDBaselines/RotorLoss nested packages plus Mass/Wind/Safety entries are not visually confusing.",
        "blocked_until": "same live route gate",
    },
    {
        "order": 4,
        "target": "MoSimQuadrotorModel.Planning package browser",
        "review": "Closed-loop planning entries are distinguishable from NavigationDisplay and ColorMapReview helpers.",
        "blocked_until": "same live route gate",
    },
    {
        "order": 5,
        "target": "MoSimQuadrotorModel.SceneTrace package browser",
        "review": "AcceptedScenes and Isolation are understandable; trace isolation ladder does not overwhelm primary package surface.",
        "blocked_until": "same live route gate",
    },
    {
        "order": 6,
        "target": "MoSimQuadrotorModel.System.Architecture.CompleteSystemGraphical",
        "review": "Diagram opens without blank/white surface; wiring, ports, subsystem layout, and labels are readable.",
        "blocked_until": "same live route gate; no Smart Layout writeback unless future task explicitly permits",
    },
    {
        "order": 7,
        "target": "QuadrotorExperiments legacy root",
        "review": "Legacy package surface shows category packages and hidden compatibility aliases do not clutter public browser.",
        "blocked_until": "same live route gate",
    },
]


def write_json(path: Path, data: dict | list) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown_table(path: Path, title: str, headers: list[str], rows: list[list[str]]) -> None:
    lines = [f"# {title}", ""]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", "<br>") for cell in row) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")

    inventory = current_tree_inventory()
    static_map = {
        "request_id": REQUEST_ID,
        "generated_at": now,
        "status": "completed_static_organization_classification",
        "source_boundary": "static file/package.order/package.mo inventory only; no MWORKS GUI/MCP/live validation",
        "formal_package_role": "Models/MoSimQuadrotorModel is the project-owned formal package surface.",
        "legacy_package_role": "Models/QuadrotorExperiments remains legacy implementation pool plus compatibility/source surface during migration.",
        "controller_package_role": "Models/QuadrotorControllerBlocks remains controller block library consumed through MoSimQuadrotorModel.Controllers.",
        "current_inventory": inventory,
        "mosim_category_roles": MOSIM_CATEGORY_ROLES,
    }
    write_json(EVIDENCE_DIR / "static_organization_classification_map.json", static_map)

    write_markdown_table(
        EVIDENCE_DIR / "static_organization_classification_map.md",
        "023 Static Organization Classification Map",
        ["Category", "Classification", "Chinese annotation", "Source", "Next action"],
        [
            [
                row["category"],
                row["classification"],
                row["chinese_annotation"],
                row["source"],
                row["next_action"],
            ]
            for row in MOSIM_CATEGORY_ROLES
        ],
    )

    disposition = {
        "request_id": REQUEST_ID,
        "generated_at": now,
        "summary": "Disposition matrix for legacy QuadrotorExperiments categories and their MoSimQuadrotorModel migration/keep/deprecate treatment.",
        "rows": LEGACY_DISPOSITION,
    }
    write_json(EVIDENCE_DIR / "quadrotor_experiments_migration_disposition_matrix.json", disposition)
    write_markdown_table(
        EVIDENCE_DIR / "quadrotor_experiments_migration_disposition_matrix.md",
        "QuadrotorExperiments Migration Disposition Matrix",
        ["Legacy package", "Target surface", "Disposition", "Reason", "Keep legacy policy"],
        [
            [
                row["legacy_package"],
                row["target_surface"],
                row["disposition"],
                row["reason"],
                row["keep_legacy"],
            ]
            for row in LEGACY_DISPOSITION
        ],
    )

    annotation_lines = [
        "# Chinese Annotation Recommendations",
        "",
        "## Package-level wording",
        "",
    ]
    for row in MOSIM_CATEGORY_ROLES:
        annotation_lines.append(f"- `{row['category']}`: {row['chinese_annotation']}")
    annotation_lines.extend(
        [
            "",
            "## Legacy wording rules",
            "",
            "- `QuadrotorExperiments` root: 标注为旧实验池与兼容入口，提醒新工作优先使用 `MoSimQuadrotorModel`。",
            "- PID baseline entries: 标注为对比基线，不写成新控制算法成果。",
            "- Trace isolation ladder: 标注为逐层诊断/接线隔离，不写成正式任务或仿真验收。",
            "- Display/review helpers: 标注为图形/地图审查支撑，不声明 controller performance。",
            "- Controller block backups: 标注为内部升级备份，不进入 public package.order。",
            "",
        ]
    )
    (EVIDENCE_DIR / "chinese_annotation_recommendations.md").write_text("\n".join(annotation_lines), encoding="utf-8")

    drift = {
        "request_id": REQUEST_ID,
        "generated_at": now,
        "drift_from_r2_015_and_021": [
            {
                "source": "R2 015",
                "status": "partially_stale",
                "details": "015 formal package map had older counts. Current root package.order has 12 categories including Parameters and current ordered child entries are regenerated from source.",
            },
            {
                "source": "R2 021",
                "status": "current_for_static_parser_boundary",
                "details": "021 corrected sibling .mo false positives and remains the boundary for static extends resolution, but 023 focuses on user-facing classification, not parser correction.",
            },
            {
                "source": "R2 022",
                "status": "still_blocks_live_audit",
                "details": "022 live route blocker remains: approved reusable attach-existing/no-start foreground route is missing.",
            },
        ],
        "duplicate_or_confusing_surfaces": [
            {
                "surface": "MoSimQuadrotorModel.Missions versus QuadrotorExperiments.OfficialScenarios",
                "status": "intentional_duplicate_alias_surface",
                "recommendation": "Use MoSimQuadrotorModel as user-facing formal surface; keep legacy for compatibility.",
            },
            {
                "surface": "MoSimQuadrotorModel.Robustness.PIDBaselines versus ControllerBaselines",
                "status": "baseline_overlap",
                "recommendation": "Keep both as baseline/reference; do not promote PID baseline variants as new control achievements.",
            },
            {
                "surface": "Planning display/review helpers mixed with closed-loop planning entries",
                "status": "classification_risk",
                "recommendation": "Future package-surface cleanup should separate review helpers from closed-loop planning models.",
            },
            {
                "surface": "SceneTrace AcceptedScenes and TraceIsolation",
                "status": "diagnostic_ladder_risk",
                "recommendation": "Keep Isolation visible only as diagnostic, and do not overpopulate the first live audit batch.",
            },
        ],
        "obsolete_or_review_helper_candidates": OBSOLETE_OR_REVIEW_HELPERS,
    }
    write_json(EVIDENCE_DIR / "drift_duplicate_obsolete_surface_report.json", drift)

    drift_md = [
        "# Drift, Duplicate, Obsolete Surface Report",
        "",
        "## Drift from prior evidence",
        "",
    ]
    for row in drift["drift_from_r2_015_and_021"]:
        drift_md.append(f"- `{row['source']}`: {row['status']} - {row['details']}")
    drift_md.extend(["", "## Duplicate or confusing surfaces", ""])
    for row in drift["duplicate_or_confusing_surfaces"]:
        drift_md.append(f"- `{row['surface']}`: {row['status']} - {row['recommendation']}")
    drift_md.extend(["", "## Rejected/obsolete/review helper candidates", ""])
    for row in OBSOLETE_OR_REVIEW_HELPERS:
        drift_md.append(f"- `{row['surface']}`: {row['classification']} - {row['recommendation']}")
    drift_md.append("")
    (EVIDENCE_DIR / "drift_duplicate_obsolete_surface_report.md").write_text("\n".join(drift_md), encoding="utf-8")

    write_json(EVIDENCE_DIR / "safe_migration_queue.json", {"request_id": REQUEST_ID, "generated_at": now, "rows": SAFE_MIGRATION_QUEUE})
    write_markdown_table(
        EVIDENCE_DIR / "safe_migration_queue.md",
        "Safe Migration Queue",
        ["Batch", "Scope", "Targets", "Action", "Risk"],
        [[row["batch"], row["scope"], row["targets"], row["action"], row["risk"]] for row in SAFE_MIGRATION_QUEUE],
    )

    write_json(EVIDENCE_DIR / "next_live_audit_queue_update.json", {"request_id": REQUEST_ID, "generated_at": now, "rows": NEXT_LIVE_QUEUE})
    write_markdown_table(
        EVIDENCE_DIR / "next_live_audit_queue_update.md",
        "Next Live Audit Queue Update",
        ["Order", "Target", "Review", "Blocked until"],
        [[row["order"], row["target"], row["review"], row["blocked_until"]] for row in NEXT_LIVE_QUEUE],
    )

    scope_summary = [
        "# Scope Diff Summary",
        "",
        "- Source `.mo`, `package.mo`, and `package.order` files changed by 023: none.",
        "- MWORKS/Sysplorer/Syslab GUI, screenshots, MCP, check_model, SimulateModel, Smart Layout, package browser, result viewer touched: no.",
        "- Official QuadrotorModel, References, UE/ROS2/Sunray/Blender/CoAgent runtime touched: no.",
        "- Git actions performed: no.",
        "- Files written by 023 are limited to this evidence directory plus the return packet.",
        "",
    ]
    (EVIDENCE_DIR / "scope_diff_summary.md").write_text("\n".join(scope_summary), encoding="utf-8")

    packet = {
        "schema": "mosim.agent_packet.return.v1",
        "request_id": REQUEST_ID,
        "status": "completed",
        "task_class": "static_model_organization_classification_audit",
        "engineering_output_mode": "static_model_organization_evidence",
        "created_at": now,
        "completed_at": now,
        "origin_thread": "MoSim｜主线 PMO",
        "origin_thread_id": "019e9868-83ea-70f0-92c5-a3a408bd78c6",
        "target_thread": "MoSim｜MWORKS动力学与控制验证部-R2",
        "target_thread_id": "019e9999-b0d3-7682-bccd-faef08fcf1df",
        "department_local_goal": "Produce a static organization/classification audit for MoSimQuadrotorModel versus legacy QuadrotorExperiments so old scattered experiment surfaces are converted into a clear migration, keep, or deprecate queue without touching live MWORKS or model source.",
        "critical_path_steps": [
            {"step": "Read 023 task packet and required governance/design/skill/prior-output sources.", "status": "completed"},
            {"step": "Keep strict static-only boundary: no MWORKS/Sysplorer/Syslab GUI/window/screenshot/MCP/check_model/SimulateModel/Smart Layout/package browser/result viewer.", "status": "completed"},
            {"step": "Inventory current MoSimQuadrotorModel, QuadrotorExperiments, and QuadrotorControllerBlocks package.order/package.mo/.mo surfaces.", "status": "completed"},
            {"step": "Classify formal categories, legacy experiment buckets, baseline/reference surfaces, diagnostic ladders, review helpers, and migration candidates.", "status": "completed"},
            {"step": "Write engineering evidence artifacts and return packet, then run JSON and department/static MWORKS validators.", "status": "completed"},
        ],
        "parallelizable_slices": [
            {"slice": "Current package tree inventory", "decision": "handled_locally", "reason": "The source tree is bounded and deterministic; local script regenerated counts directly from current files."},
            {"slice": "Legacy disposition matrix", "decision": "handled_locally", "reason": "Classification depends on R2 ownership judgement and migration design policy."},
            {"slice": "Disposable subagent independent review", "decision": "available_but_not_useful", "reason": "A subagent would duplicate small static reads and cannot add live evidence under the static-only boundary."},
            {"slice": "Live package/browser or graphical audit", "decision": "forbidden_not_parallelizable", "reason": "023 forbids live MWORKS and 022 still blocks live route until attach-only/no-start route is proven."},
        ],
        "subagent_plan": "available_but_not_useful",
        "subagent_plan_reason": "No disposable subagent was used. The audit is a bounded, deterministic static classification over current package/order/source inventory; live work is forbidden and the classification calls need single-owner R2 judgement.",
        "subagents_used": [],
        "verification_gates": [
            {"gate": "required_read_first", "status": "passed", "evidence": ["AGENTS.md", "Docs/Workflows/new_conversation_context.md", "Docs/Workflows/agent_task_ledger.md", "Docs/Design/12_MoSimQuadrotorModel模型归档与迁移计划.md", "C:/Users/HP/.codex/skills/mworks-model-context/SKILL.md", "R2 015 return", "R2 021 return", "R2 022 blocker", "current Models package trees"]},
            {"gate": "static_only_boundary", "status": "passed", "evidence": "live_mworks_touched=false; mworks_window_evidence_touched=false; no GUI/MCP/check/simulation/layout/window operation was used."},
            {"gate": "package_tree_inventory", "status": "passed_static", "evidence": rel(EVIDENCE_DIR / "static_organization_classification_map.json")},
            {"gate": "legacy_disposition_matrix", "status": "passed_static", "evidence": rel(EVIDENCE_DIR / "quadrotor_experiments_migration_disposition_matrix.json")},
            {"gate": "migration_queue_and_live_queue", "status": "passed_static", "evidence": [rel(EVIDENCE_DIR / "safe_migration_queue.md"), rel(EVIDENCE_DIR / "next_live_audit_queue_update.md")]},
            {"gate": "forbidden_scope_preserved", "status": "passed", "evidence": rel(EVIDENCE_DIR / "scope_diff_summary.md")},
        ],
        "manual_review_or_blocker_triggers": [
            "Need to inspect package browser, diagram layout, wiring, result window, Smart Layout output, screenshots, or white/blank GUI surfaces.",
            "Need to move/delete/rename implementation files or edit package.order/package.mo outside a separately approved source task.",
            "Need to change official QuadrotorModel, References, UE/ROS2/Sunray/Blender, controller/planner runtime, or CoAgent runtime.",
            "Need to declare check_model, simulation, controller performance, planner_ready, runtime ack, mission success, or closed_loop.",
            "Approved reusable attach-existing/no-start MWORKS route remains missing for live R2 graphical/package audit.",
        ],
        "mworks_activation_patrol_reference": {
            "status": "not_required_static_only_023",
            "activation_patrol_owner": "CoAgentOps",
            "recent_patrol_required": False,
            "reason": "023 is static-only and explicitly forbids opening, switching, maximizing, screenshotting, or operating MWORKS/Sysplorer/Syslab. No window evidence was touched.",
        },
        "will_not_click_activation_login": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "mworks_window_policy": "static_file_only_no_mworks_window_or_mcp_touch",
        "package_tree_audit": {
            "artifact": rel(EVIDENCE_DIR / "static_organization_classification_map.json"),
            "mosim_top_categories": inventory["mosim_quadrotor_model"]["package_order"]["root_order_entries"],
            "mosim_top_category_count": inventory["mosim_quadrotor_model"]["top_category_count"],
            "quadrotor_experiments_category_count": inventory["quadrotor_experiments"]["category_dir_count"],
            "quadrotor_experiments_implementation_mo_count_excluding_package_mo": inventory["quadrotor_experiments"]["implementation_mo_count_excluding_package_mo"],
            "quadrotor_controller_flat_mo_count": inventory["quadrotor_controller_blocks"]["flat_controller_mo_count"],
            "quadrotor_controller_backup_upgrade_mo_count": inventory["quadrotor_controller_blocks"]["backup_upgrade_mo_count"],
        },
        "classification_map": {
            "artifact_json": rel(EVIDENCE_DIR / "static_organization_classification_map.json"),
            "artifact_markdown": rel(EVIDENCE_DIR / "static_organization_classification_map.md"),
            "summary": "MoSimQuadrotorModel is the formal project package; QuadrotorExperiments is legacy implementation/compatibility source; QuadrotorControllerBlocks is a controller block library consumed through Controllers.",
        },
        "old_to_new_class_mapping": {
            "artifact_json": rel(EVIDENCE_DIR / "quadrotor_experiments_migration_disposition_matrix.json"),
            "artifact_markdown": rel(EVIDENCE_DIR / "quadrotor_experiments_migration_disposition_matrix.md"),
            "summary": "Legacy categories are split into migrate_to_mosim_formal, migrate_as_alias_then_live_validate, keep_legacy_reference_or_baseline, diagnostic ladder, and review helper dispositions.",
        },
        "rename_batches": {
            "artifact_json": rel(EVIDENCE_DIR / "safe_migration_queue.json"),
            "artifact_markdown": rel(EVIDENCE_DIR / "safe_migration_queue.md"),
            "summary": "023 proposes serialized non-destructive migration batches; no move/delete/rename/source edits were performed.",
        },
        "graphical_layout_review_plan": {
            "artifact_json": rel(EVIDENCE_DIR / "next_live_audit_queue_update.json"),
            "artifact_markdown": rel(EVIDENCE_DIR / "next_live_audit_queue_update.md"),
            "summary": "Future R2 live audit queue starts with package browser clarity and then representative graphical/system diagrams after the no-start live route is proven.",
        },
        "drift_duplicate_obsolete_surface_report": {
            "artifact_json": rel(EVIDENCE_DIR / "drift_duplicate_obsolete_surface_report.json"),
            "artifact_markdown": rel(EVIDENCE_DIR / "drift_duplicate_obsolete_surface_report.md"),
            "summary": "R2 015 counts are stale; 021 parser boundary remains current; TraceIsolation ladder and planning display/color-map helpers are not formal user-facing mission/control acceptance surfaces.",
        },
        "chinese_annotation_recommendations": {
            "artifact": rel(EVIDENCE_DIR / "chinese_annotation_recommendations.md"),
            "summary": "Category-level Chinese wording recommendations distinguish formal missions, baselines, support/review helpers, and diagnostic ladders.",
        },
        "actual_engineering_outputs": [
            {"type": "static_package_tree_classification_map", "path": rel(EVIDENCE_DIR / "static_organization_classification_map.md"), "summary": "Current package/order/source inventory plus MoSimQuadrotorModel category roles and Chinese annotation recommendations."},
            {"type": "legacy_migration_disposition_matrix", "path": rel(EVIDENCE_DIR / "quadrotor_experiments_migration_disposition_matrix.md"), "summary": "QuadrotorExperiments categories classified as formal migration, alias/live-validate, baseline/reference, support, diagnostic ladder, or review helper."},
            {"type": "safe_migration_queue", "path": rel(EVIDENCE_DIR / "safe_migration_queue.md"), "summary": "Serialized future migration batches that preserve old aliases and defer source moves/renames to scoped tasks."},
            {"type": "graphical_live_audit_queue_update", "path": rel(EVIDENCE_DIR / "next_live_audit_queue_update.md"), "summary": "Next R2 live package-browser/layout review targets and blockers after approved no-start MWORKS route proof."},
            {"type": "drift_duplicate_obsolete_surface_report", "path": rel(EVIDENCE_DIR / "drift_duplicate_obsolete_surface_report.md"), "summary": "Static drift, duplicate/confusing surface, obsolete/review-helper candidate report addressing user concern about messy categories."},
            {"type": "scope_diff_summary", "path": rel(EVIDENCE_DIR / "scope_diff_summary.md"), "summary": "Evidence that 023 wrote only allowed evidence/packet files and did not touch model source, GUI/MCP, runtime, or Git."},
        ],
        "changed_files": {
            "source_files_changed_by_023": [],
            "evidence_files_written_by_023": [
                rel(EVIDENCE_DIR / "generate_023_static_organization_audit.py"),
                rel(EVIDENCE_DIR / "static_organization_classification_map.json"),
                rel(EVIDENCE_DIR / "static_organization_classification_map.md"),
                rel(EVIDENCE_DIR / "quadrotor_experiments_migration_disposition_matrix.json"),
                rel(EVIDENCE_DIR / "quadrotor_experiments_migration_disposition_matrix.md"),
                rel(EVIDENCE_DIR / "chinese_annotation_recommendations.md"),
                rel(EVIDENCE_DIR / "drift_duplicate_obsolete_surface_report.json"),
                rel(EVIDENCE_DIR / "drift_duplicate_obsolete_surface_report.md"),
                rel(EVIDENCE_DIR / "safe_migration_queue.json"),
                rel(EVIDENCE_DIR / "safe_migration_queue.md"),
                rel(EVIDENCE_DIR / "next_live_audit_queue_update.json"),
                rel(EVIDENCE_DIR / "next_live_audit_queue_update.md"),
                rel(EVIDENCE_DIR / "scope_diff_summary.md"),
            ],
            "return_packet_written_by_023": rel(RETURN_PACKET),
        },
        "forbidden_actions_confirmed": {
            "edited_model_source_mo_package_mo_or_package_order": False,
            "moved_deleted_or_renamed_legacy_implementation_files": False,
            "edited_official_quadrotor_model_or_references": False,
            "opened_closed_switched_maximized_restarted_or_screenshotted_mworks_sysplorer_syslab_window": False,
            "operated_mworks_sysplorer_syslab_gui": False,
            "called_mworks_sysplorer_syslab_mcp": False,
            "ran_check_model": False,
            "ran_simulate_model": False,
            "ran_smart_layout_package_browser_or_result_viewer": False,
            "called_clearall_or_changedirectory": False,
            "edited_ros2_ue_sunray_blender_coagent_controller_planner_runtime": False,
            "staged_unstaged_reverted_cleaned_committed_or_pushed_git": False,
        },
        "quality_check_results": {"status": "pending_until_post_generation_checks", "checks": []},
        "claim_boundary": [
            "023 claims only static organization/classification readiness, package tree audit, migration disposition, Chinese annotation recommendations, and next live audit queue update.",
            "023 does not move, delete, rename, or edit `.mo`, `package.mo`, or `package.order` source files.",
            "023 does not prove live MWORKS activation, package-browser acceptance, graphical/layout/wiring acceptance, check_model, SimulateModel, controller performance, planner_ready, runtime acknowledgement, mission success, or closed_loop.",
            "023 does not supersede 022 live route blocker; live R2 package/browser/graphical audit remains blocked until an approved attach-existing/no-start route exists.",
        ],
        "next_action_for_pmo": "Use the 023 disposition matrix to approve the next narrow static source/package task or defer to a future live package-browser/layout audit after the MWORKS no-start route is proven.",
    }
    RETURN_PACKET.parent.mkdir(parents=True, exist_ok=True)
    write_json(RETURN_PACKET, packet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
