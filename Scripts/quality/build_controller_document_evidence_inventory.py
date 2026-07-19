#!/usr/bin/env python3
"""Inventory document evidence for the authoritative 67 controller routes.

This is a static audit. It does not launch MWORKS and it does not promote a
diagram, CSV, or JSON file into native Result.msr or result-viewer evidence.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MATRIX = (
    ROOT
    / "Results/control_platform/classic_controller_closeout_20260717"
    / "CLASSIC_CONTROLLER_FINAL_MATRIX.json"
)
DEFAULT_OUTPUT_DIR = (
    ROOT / "Results/control_platform/controller_document_evidence_20260720"
)

COHORT_ROOTS = {
    "P1_PID": ["Results/control_platform/p1_pid_mworks_20260716"],
    "P2_LINEAR_ROBUST": ["Results/control_platform/p2_linear_robust_mworks_20260716"],
    "P3_SLIDING_MODE": ["Results/control_platform/p3_sliding_mode_mworks_20260716"],
    "P4_MPC": ["Results/control_platform/p4_mpc_mworks_20260716"],
    "P5_ENHANCEMENT": ["Results/control_platform/p5_enhancement_mworks_20260717"],
    "G9_CORE_COMPARISON": ["Results/control_platform/g5_mworks_closeout_20260716"],
    "P6_SAFETY": ["Results/control_platform/p6_safety_mworks_20260717"],
    "P7_FTC": ["Results/control_platform/p7_ftc_mworks_20260717"],
    "P8_FORMATION": ["Results/control_platform/p8_formation_mworks_20260717"],
    "P9_LEARNING": ["Results/control_platform/p9_learning_mworks_20260717"],
    "P10_CLASSIC_RECONCILIATION": [
        "Results/control_platform/p10_mworks_gap_closeout_20260718",
        "Results/control_platform/g5_mworks_closeout_20260716/wave_a",
    ],
    "P11_CLASSIC_ADDITIONS": [
        "Results/control_platform/classic_controller_closeout_20260717/mworks"
    ],
}

# Family rows intentionally bind to their shared family fixture. They do not
# imply that every submode has an independent screenshot.
ALIASES = {
    "official_pid": ["official_pid", "awff_pid_sysblock_demo"],
    "se3_basic": ["se3_basic", "se3"],
    "dfbc_basic": ["dfbc_basic"],
    "smc_boundary_layer": ["smc_boundary_layer", "boundary_layer_smc"],
    "pid_indi": ["pid_indi"],
    "nmpc_outer": ["nmpc_outer", "nmpc"],
    "safety_supervisor_family": ["safety_supervisor", "safety_filter"],
    "fdi_ftc_family": ["multi_fault_estimation_reconfiguration", "fdi", "ftc"],
    "lqr_baseline": ["wavea_lqr", "wave_a_lqr", "lqr_baseline"],
    "lqi_baseline": ["wavea_lqi", "wave_a_lqi", "lqi_baseline"],
    "so3_attitude": ["wavea_so3", "wave_a_so3", "so3_attitude"],
    "backstepping_baseline": [
        "wavea_backstepping",
        "wave_a_backstepping",
        "backstepping_baseline",
    ],
}

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
NUMERIC_SUFFIXES = {".csv", ".json"}
MODEL_SUFFIXES = {".mo"}
NATIVE_RESULT_SUFFIXES = {".msr"}
BLOCKED_IMPLEMENTATIONS = {"mu_synthesis", "neural_smc"}

EXACT_MODEL_SOURCES = {
    "official_pid": ["Models/QuadrotorControllerBlocks/AWFF_PID_Sysblock_Demo.mo"],
}

# These are exact controller/profile bindings from the offline composition
# catalog. Similar-looking legacy bundles are deliberately excluded.
EXACT_NATIVE_RESULT_ROOTS = {
    "official_pid": [
        "Results/mworks_generated_profiles/cert-official-pid-20260719-v2/native_result"
    ],
    "pid_indi": [
        "Results/mworks_generated_profiles/cert-pid-indi-20260719-v1/native_result"
    ],
    "linear_mpc": [
        "Results/mworks_generated_profiles/cert-linear-mpc-20260719-v1/native_result"
    ],
    "awff": ["Results/mworks_generated_profiles/cert-awff-20260719-v1/native_result"],
}


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_text_lf(path: Path, content: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def route_aliases(controller: str) -> list[str]:
    values = [controller, *ALIASES.get(controller, [])]
    return sorted({normalize(value) for value in values if value})


@lru_cache(maxsize=None)
def files_under(roots: tuple[Path, ...]) -> tuple[Path, ...]:
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(path for path in root.rglob("*") if path.is_file())
    return tuple(sorted(set(files), key=lambda path: rel(path).lower()))


def matches_route(path: Path, aliases: list[str]) -> bool:
    value = normalize(path.stem)
    return any(alias in value for alias in aliases)


def pick(files: list[Path], aliases: list[str], suffixes: set[str]) -> list[Path]:
    return [
        path
        for path in files
        if path.suffix.lower() in suffixes and matches_route(path, aliases)
    ]


def is_result_viewer(path: Path) -> bool:
    value = normalize(str(path))
    return "result_viewer" in value or "result_plot" in value or "结果查看器" in str(path)


def is_graphical_model_image(path: Path) -> bool:
    value = normalize(str(path))
    return any(
        token in value
        for token in ("graphical", "diagram", "diagrams", "live_gui", "sysplorer")
    ) and not is_result_viewer(path)


def evidence_paths_from_matrix(row: dict[str, Any]) -> list[Path]:
    return [repo_path(value) for value in row.get("evidence_paths", []) if isinstance(value, str)]


def inventory_row(row: dict[str, Any]) -> dict[str, Any]:
    controller = str(row["controller"])
    cohort = str(row["cohort"])
    roots = [repo_path(path) for path in COHORT_ROOTS[cohort]]
    files = list(files_under(tuple(roots)))
    aliases = route_aliases(controller)

    models = pick(files, aliases, MODEL_SUFFIXES)
    models.extend(
        path
        for path in (repo_path(value) for value in EXACT_MODEL_SOURCES.get(controller, []))
        if path.is_file()
    )
    models = sorted(set(models), key=lambda path: rel(path).lower())
    images = pick(files, aliases, IMAGE_SUFFIXES)
    graphical = [path for path in images if is_graphical_model_image(path)]
    result_images = [path for path in images if is_result_viewer(path)]
    native_results = pick(files, aliases, NATIVE_RESULT_SUFFIXES)
    for native_root_value in EXACT_NATIVE_RESULT_ROOTS.get(controller, []):
        native_root = repo_path(native_root_value)
        if native_root.is_dir():
            native_results.extend(native_root.rglob("*.msr"))
    native_results = sorted(set(native_results), key=lambda path: rel(path).lower())
    numeric = pick(files, aliases, NUMERIC_SUFFIXES)

    matrix_evidence = evidence_paths_from_matrix(row)
    existing_matrix_evidence = [path for path in matrix_evidence if path.exists()]
    numeric.extend(
        path
        for path in existing_matrix_evidence
        if path.suffix.lower() in NUMERIC_SUFFIXES
    )
    numeric = sorted(set(numeric), key=lambda path: rel(path).lower())

    implementation_blocked = controller in BLOCKED_IMPLEMENTATIONS
    missing: list[str] = []
    if not models:
        missing.append("model_source")
    if not graphical:
        missing.append("graphical_model_screenshot")
    if not result_images:
        missing.append("result_viewer_screenshot")
    if not numeric:
        missing.append("numeric_result_or_metrics")
    if not native_results:
        missing.append("native_result_msr_live_confirmation")

    if implementation_blocked:
        next_action = "bounded_implementation_gap_review"
    elif not models or not numeric:
        next_action = "repair_or_rerun_required"
    elif not graphical or not result_images:
        next_action = "capture_missing_mworks_screenshots"
    elif not native_results:
        next_action = "confirm_native_result_msr_in_live_session"
    else:
        next_action = "document_ready_static_audit"

    return {
        "cohort": cohort,
        "controller": controller,
        "matrix_status": row.get("status"),
        "implementation_state": row.get("implementation_state"),
        "claim_ceiling": row.get("claim_ceiling"),
        "aliases": aliases,
        "search_roots": [rel(path) for path in roots],
        "model_sources": [rel(path) for path in models],
        "graphical_model_screenshots": [rel(path) for path in graphical],
        "result_viewer_screenshots": [rel(path) for path in result_images],
        "numeric_results_or_metrics": [rel(path) for path in numeric],
        "native_result_msr": [rel(path) for path in native_results],
        "matrix_evidence_existing": [rel(path) for path in existing_matrix_evidence],
        "missing_evidence": missing,
        "implementation_blocked": implementation_blocked,
        "next_action": next_action,
    }


def build_inventory(matrix_path: Path) -> dict[str, Any]:
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    rows = matrix.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("matrix rows must be a list")
    inventory_rows = [inventory_row(row) for row in rows]
    status_counts = Counter(str(row.get("status")) for row in rows)
    action_counts = Counter(row["next_action"] for row in inventory_rows)

    return {
        "schema": "mosim.controller_document_evidence_inventory.v1",
        "status": "static_audit_not_live_mworks_acceptance",
        "source_matrix": rel(matrix_path),
        "claim_boundary": [
            "This inventory is a static file-presence audit and does not run MWORKS.",
            "Graphical model screenshots and result-viewer screenshots are separate evidence classes.",
            "CSV or JSON evidence is not promoted to native Result.msr evidence.",
            "A blocked or negative result remains valid report evidence when its provenance is preserved.",
        ],
        "summary": {
            "row_count": len(inventory_rows),
            "unique_controller_count": len({row["controller"] for row in inventory_rows}),
            "matrix_status_counts": dict(sorted(status_counts.items())),
            "model_source_present_count": sum(bool(row["model_sources"]) for row in inventory_rows),
            "graphical_screenshot_present_count": sum(
                bool(row["graphical_model_screenshots"]) for row in inventory_rows
            ),
            "result_screenshot_present_count": sum(
                bool(row["result_viewer_screenshots"]) for row in inventory_rows
            ),
            "numeric_result_present_count": sum(
                bool(row["numeric_results_or_metrics"]) for row in inventory_rows
            ),
            "native_result_msr_present_count": sum(
                bool(row["native_result_msr"]) for row in inventory_rows
            ),
            "implementation_blocked_count": sum(
                row["implementation_blocked"] for row in inventory_rows
            ),
            "next_action_counts": dict(sorted(action_counts.items())),
        },
        "rows": inventory_rows,
    }


def write_markdown(inventory: dict[str, Any], path: Path) -> None:
    summary = inventory["summary"]
    lines = [
        "# 控制器文档证据静态盘点（67项）",
        "",
        "状态：静态文件盘点，不代表MWORKS现场验收。",
        "",
        f"- 权威矩阵：`{inventory['source_matrix']}`",
        f"- 路线数：`{summary['row_count']}`",
        f"- 状态计数：`{json.dumps(summary['matrix_status_counts'], ensure_ascii=False)}`",
        f"- 已有模型源码：`{summary['model_source_present_count']}`",
        f"- 已有图形模型截图：`{summary['graphical_screenshot_present_count']}`",
        f"- 已有结果查看器截图：`{summary['result_screenshot_present_count']}`",
        f"- 已有数值结果或指标：`{summary['numeric_result_present_count']}`",
        f"- 仓库内可见Result.msr：`{summary['native_result_msr_present_count']}`",
        f"- 实现阻塞：`{summary['implementation_blocked_count']}`",
        "",
        "## 边界",
        "",
    ]
    lines.extend(f"- {item}" for item in inventory["claim_boundary"])
    lines.extend(
        [
            "",
            "## 逐项状态",
            "",
            "| 家族 | 路线 | 矩阵状态 | 模型 | 图形截图 | 结果截图 | 数值结果 | MSR | 下一步 |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in inventory["rows"]:
        lines.append(
            "| {cohort} | {controller} | {status} | {model} | {diagram} | {result} | "
            "{numeric} | {msr} | {action} |".format(
                cohort=row["cohort"],
                controller=row["controller"],
                status=row["matrix_status"],
                model="有" if row["model_sources"] else "缺",
                diagram="有" if row["graphical_model_screenshots"] else "缺",
                result="有" if row["result_viewer_screenshots"] else "缺",
                numeric="有" if row["numeric_results_or_metrics"] else "缺",
                msr="有" if row["native_result_msr"] else "待确认",
                action=row["next_action"],
            )
        )
    lines.extend(["", "## 下一批", ""])
    lines.append(
        "- 优先补齐已有模型和数值结果、但缺少图形或结果查看器截图的路线；不先重跑七场景。"
    )
    lines.append("- `mu_synthesis`与`neural_smc`保持实现阻塞，不阻塞其余65项证据整理。")
    write_text_lf(path, "\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", default=str(DEFAULT_MATRIX.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    matrix_path = repo_path(args.matrix)
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory(matrix_path)
    json_path = output_dir / "CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.json"
    md_path = output_dir / "CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.md"
    write_text_lf(json_path, json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    write_markdown(inventory, md_path)

    result = {
        "ok": inventory["summary"]["row_count"] == 67,
        "inventory_json": rel(json_path),
        "inventory_markdown": rel(md_path),
        **inventory["summary"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
