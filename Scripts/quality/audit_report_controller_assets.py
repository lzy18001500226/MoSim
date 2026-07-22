#!/usr/bin/env python3
"""Audit archived controller exports from MoSim's former report asset tree.

This is deliberately a static audit. It verifies the archived report-copy asset pair,
cross-references the authoritative controller inventory, and detects byte-level
duplicate PNG files. It cannot judge Sysplorer wiring readability, confirm the
opened submodel, or turn a screenshot into a passed simulation result. Those
decisions remain explicit human/MWORKS review gates in the generated ledger.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPORT_ASSET_ROOT = ROOT / "Docs" / "报告" / "图" / "归档" / "控制器旧导出资产_20260722"
CONTROLLER_MATRIX = (
    ROOT
    / "Results"
    / "control_platform"
    / "classic_controller_closeout_20260717"
    / "CLASSIC_CONTROLLER_FINAL_MATRIX.json"
)
EVIDENCE_INVENTORY = (
    ROOT
    / "Results"
    / "control_platform"
    / "controller_document_evidence_20260720"
    / "CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Docs" / "报告" / "审计" / "归档" / "控制器旧导出资产_20260722"

MODEL_IMAGE = "01_图形模型.png"
RESULT_IMAGE = "02_仿真结果.png"
BLOCKED_ROUTES = {"mu_synthesis", "neural_smc"}
CORE_BODY_ROUTES = {
    "official_pid",
    "cascade_pid",
    "gain_scheduled_pid",
    "smc_boundary_layer",
    "super_twisting_smc",
    "lqr_baseline",
    "lqi_baseline",
    "standardized_indi",
    "pid_indi",
    "linear_mpc",
    "nmpc_outer",
    "awff",
    "safety_supervisor_family",
    "fdi_ftc_family",
    "leader_follower",
    "distributed_mpc_formation",
}


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {rel(path)}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Not a valid PNG IHDR: {rel(path)}")
    return struct.unpack(">II", header[16:24])


def image_record(path: Path) -> dict[str, Any]:
    width, height = png_dimensions(path)
    return {
        "path": rel(path),
        "sha256": sha256(path),
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
        "vertical_long_capture": height / width >= 2.0,
    }


def report_assets() -> dict[str, dict[str, Any]]:
    assets: dict[str, dict[str, Any]] = {}
    for model in sorted(REPORT_ASSET_ROOT.glob(f"*/*/{MODEL_IMAGE}")):
        route = model.parent.name
        if route in assets:
            raise ValueError(f"Duplicate report route directory: {route}")
        result = model.parent / RESULT_IMAGE
        assets[route] = {
            "family": model.parent.parent.name,
            "graphical_model": image_record(model),
            "simulation_result": image_record(result) if result.is_file() else None,
        }
    return assets


def duplicate_groups(
    assets: dict[str, dict[str, Any]], image_key: str
) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for route, item in assets.items():
        image = item.get(image_key)
        if image:
            grouped[str(image["sha256"])].append(route)
    return {
        digest: sorted(routes)
        for digest, routes in grouped.items()
        if len(routes) > 1
    }


def static_image_action(
    image: dict[str, Any] | None,
    duplicate_routes: list[str] | None,
    image_kind: str,
) -> str:
    if image is None:
        return "missing_report_copy"
    if duplicate_routes:
        return f"duplicate_{image_kind}_review_or_recapture"
    if bool(image["vertical_long_capture"]):
        return "capture_readable_internal_submodel"
    if image_kind == "model":
        return "manual_mworks_internal_wiring_review_required"
    return "manual_result_title_curve_and_run_binding_review_required"


def report_use(row: dict[str, Any]) -> str:
    route = str(row["controller"])
    if route in BLOCKED_ROUTES:
        return "blocked_route_not_in_body"
    if route in CORE_BODY_ROUTES:
        return "core_candidate_after_manual_review"
    return "coverage_matrix_or_appendix_evidence_only"


def non_backup_source_records(inventory_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return source metadata without treating crash backups as alternatives."""
    records: list[dict[str, Any]] = []
    for raw_path in inventory_row.get("model_sources", []):
        if not isinstance(raw_path, str):
            continue
        normalized = raw_path.replace("\\", "/")
        if any("backup" in segment.lower() for segment in normalized.split("/")):
            continue
        path = ROOT / raw_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        model_match = re.search(r"(?m)^\s*model\s+([A-Za-z_]\w*)\b", text)
        has_atomic_cfunction = any(
            re.match(
                r"\s*[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*CFunction\w*\s+[A-Za-z_]\w*\b",
                line,
            )
            for line in text.splitlines()
        )
        graphical_block_count = sum(
            1
            for line in text.splitlines()
            if line.lstrip().startswith("SysplorerEmbeddedCoder.")
            and ".Port." not in line
            and "ModelWorkspace" not in line
        )
        connection_count = sum(
            1 for line in text.splitlines() if line.lstrip().startswith("connect(")
        )
        records.append(
            {
                "path": rel(path),
                "model_name": model_match.group(1) if model_match else None,
                "has_atomic_cfunction": has_atomic_cfunction,
                "graphical_block_count": graphical_block_count,
                "connection_count": connection_count,
            }
        )
    return records


def classify_model_source(inventory_row: dict[str, Any]) -> dict[str, Any]:
    """Classify the actual internal-model candidate, not merely file presence."""
    records = non_backup_source_records(inventory_row)
    if bool(inventory_row.get("implementation_blocked")) or not records:
        return {
            "classification": "implementation_blocked",
            "selected_internal_source": None,
            "source_records": records,
        }

    native_records = [record for record in records if not record["has_atomic_cfunction"]]
    if not native_records:
        return {
            "classification": "atomic_cfunction_wrapper",
            "selected_internal_source": None,
            "source_records": records,
        }
    if len(native_records) != 1:
        top_score = max(
            (record["graphical_block_count"], record["connection_count"])
            for record in native_records
        )
        strongest_records = [
            record
            for record in native_records
            if (record["graphical_block_count"], record["connection_count"])
            == top_score
        ]
        if len(strongest_records) == 1:
            return {
                "classification": "native_graphical_candidate",
                "selected_internal_source": strongest_records[0]["path"],
                "source_records": records,
            }
        return {
            "classification": "source_mapping_ambiguous",
            "selected_internal_source": None,
            "source_records": records,
        }
    return {
        "classification": "native_graphical_candidate",
        "selected_internal_source": native_records[0]["path"],
        "source_records": records,
    }


def result_title_binding_status(
    inventory_row: dict[str, Any],
    source_records: list[dict[str, Any]],
    known_model_routes: dict[str, set[str]],
) -> str:
    """Catch copied Result Viewer screenshots whose displayed model is another route."""
    screenshot_paths = inventory_row.get("result_viewer_screenshots", [])
    if not screenshot_paths:
        return "missing_result_viewer_screenshot"
    expected_names = {
        str(record["model_name"]).upper()
        for record in source_records
        if record.get("model_name")
    }
    displayed_names: set[str] = set()
    for raw_path in screenshot_paths:
        if not isinstance(raw_path, str):
            continue
        displayed_names.update(
            name.upper()
            for name in re.findall(r"(MoSim_[A-Za-z0-9_]+)", Path(raw_path).stem)
        )
    if not displayed_names:
        return "result_title_not_machine_readable_review_required"
    if expected_names.intersection(displayed_names):
        return "machine_title_matches_source_review_required"
    displayed_routes = {
        route
        for name in displayed_names
        for route in known_model_routes.get(name, set())
    }
    if displayed_routes:
        return "result_title_route_mismatch"
    return "result_title_unresolved_review_required"


def source_layout_status(
    source_classification: str,
    image: dict[str, Any] | None,
    duplicate_routes: list[str] | None,
) -> str:
    if source_classification == "implementation_blocked":
        return "implementation_blocked_not_a_graphical_model"
    if source_classification == "atomic_cfunction_wrapper":
        return "atomic_cfunction_wrapper_not_report_internal_diagram"
    if source_classification == "source_mapping_ambiguous":
        return "source_mapping_ambiguous_select_internal_model_first"
    return static_image_action(image, duplicate_routes, "model")


def build_audit() -> dict[str, Any]:
    matrix = read_json(CONTROLLER_MATRIX)
    inventory = read_json(EVIDENCE_INVENTORY)
    matrix_rows = matrix.get("rows", [])
    inventory_rows = inventory.get("rows", [])
    if not isinstance(matrix_rows, list) or not isinstance(inventory_rows, list):
        raise ValueError("controller matrix and inventory rows must be lists")
    inventory_by_route = {
        str(row["controller"]): row for row in inventory_rows if isinstance(row, dict)
    }
    assets = report_assets()
    model_duplicates = duplicate_groups(assets, "graphical_model")
    result_duplicates = duplicate_groups(assets, "simulation_result")
    source_by_route = {
        str(row["controller"]): classify_model_source(row)
        for row in inventory_rows
        if isinstance(row, dict) and "controller" in row
    }
    known_model_routes: dict[str, set[str]] = defaultdict(set)
    for route, source in source_by_route.items():
        for record in source["source_records"]:
            model_name = record.get("model_name")
            if model_name:
                known_model_routes[str(model_name).upper()].add(route)

    rows: list[dict[str, Any]] = []
    for matrix_row in matrix_rows:
        if not isinstance(matrix_row, dict):
            raise ValueError("controller matrix contains a non-object row")
        route = str(matrix_row["controller"])
        asset = assets.get(route)
        inventory_row = inventory_by_route.get(route, {})
        model = asset["graphical_model"] if asset else None
        result = asset["simulation_result"] if asset else None
        model_duplicate_routes = model_duplicates.get(str(model["sha256"])) if model else None
        result_duplicate_routes = result_duplicates.get(str(result["sha256"])) if result else None
        source = source_by_route.get(route, classify_model_source(inventory_row))
        source_classification = str(source["classification"])
        result_binding = result_title_binding_status(
            inventory_row, source["source_records"], known_model_routes
        )
        route_report_use = report_use(matrix_row)
        if source_classification == "atomic_cfunction_wrapper":
            route_report_use = "interface_integration_evidence_only"
        elif source_classification == "source_mapping_ambiguous":
            route_report_use = "source_mapping_required_before_report_use"
        elif source_classification == "implementation_blocked":
            route_report_use = "blocked_route_not_in_body"
        result_report_use = "eligible_after_manual_result_review"
        if result_binding == "result_title_route_mismatch":
            result_report_use = "recapture_required_before_report_result_use"
        elif result_binding != "machine_title_matches_source_review_required":
            result_report_use = "live_result_binding_required_before_report_result_use"
        rows.append(
            {
                "family": asset["family"] if asset else "未归档视觉资产",
                "controller": route,
                "matrix_status": matrix_row.get("status"),
                "claim_ceiling": matrix_row.get("claim_ceiling"),
                "report_asset_present": asset is not None and result is not None,
                "graphical_model": model,
                "simulation_result": result,
                "model_duplicate_routes": model_duplicate_routes or [],
                "result_duplicate_routes": result_duplicate_routes or [],
                "model_source_present": bool(inventory_row.get("model_sources")),
                "source_classification": source_classification,
                "selected_internal_source": source["selected_internal_source"],
                "source_records": source["source_records"],
                "numeric_result_present": bool(
                    inventory_row.get("numeric_results_or_metrics")
                ),
                "native_result_msr_present": bool(inventory_row.get("native_result_msr")),
                "graphical_layout_status": source_layout_status(
                    source_classification, model, model_duplicate_routes
                ),
                "simulation_evidence_status": static_image_action(
                    result, result_duplicate_routes, "result"
                ),
                "result_title_binding_status": result_binding,
                "result_report_use": result_report_use,
                "manual_review_required": source_classification
                == "native_graphical_candidate",
                "report_use": route_report_use,
            }
        )

    status_counts = Counter(str(row.get("status")) for row in matrix_rows)
    report_assets_present = sum(row["report_asset_present"] for row in rows)
    model_duplicate_replacements = sum(len(routes) - 1 for routes in model_duplicates.values())
    result_duplicate_replacements = sum(len(routes) - 1 for routes in result_duplicates.values())
    vertical_models = [
        row["controller"]
        for row in rows
        if row["graphical_model"] and row["graphical_model"]["vertical_long_capture"]
    ]
    source_classification_counts = Counter(
        str(row["source_classification"]) for row in rows
    )
    title_mismatch_routes = sorted(
        row["controller"]
        for row in rows
        if row["result_title_binding_status"] == "result_title_route_mismatch"
    )
    title_unresolved_routes = sorted(
        row["controller"]
        for row in rows
        if row["result_title_binding_status"]
        == "result_title_unresolved_review_required"
    )

    return {
        "schema": "mosim.report_controller_asset_audit.v1",
        "status": "static_audit_pending_manual_mworks_review",
        "authorities": {
            "controller_matrix": rel(CONTROLLER_MATRIX),
            "document_evidence_inventory": rel(EVIDENCE_INVENTORY),
        },
        "claim_boundary": [
            "This audit checks report-copy files and static provenance only; it does not open MWORKS or run a simulation.",
            "A nonduplicate PNG is not automatically a readable internal controller diagram.",
            "A result-viewer screenshot and metrics file do not replace a route-bound native Result.msr or live-session verification.",
            "Only a review that opens the actual internal control-law submodel may mark wiring/layout as passed.",
        ],
        "summary": {
            "controller_matrix_rows": len(rows),
            "matrix_status_counts": dict(sorted(status_counts.items())),
            "report_asset_pair_count": report_assets_present,
            "missing_visual_asset_routes": sorted(
                row["controller"] for row in rows if not row["report_asset_present"]
            ),
            "model_duplicate_group_count": len(model_duplicates),
            "model_duplicate_replacement_count": model_duplicate_replacements,
            "result_duplicate_group_count": len(result_duplicates),
            "result_duplicate_replacement_count": result_duplicate_replacements,
            "vertical_model_capture_routes": sorted(vertical_models),
            "model_source_present_count": sum(row["model_source_present"] for row in rows),
            "source_classification_counts": dict(
                sorted(source_classification_counts.items())
            ),
            "atomic_cfunction_wrapper_routes": sorted(
                row["controller"]
                for row in rows
                if row["source_classification"] == "atomic_cfunction_wrapper"
            ),
            "source_mapping_ambiguous_routes": sorted(
                row["controller"]
                for row in rows
                if row["source_classification"] == "source_mapping_ambiguous"
            ),
            "numeric_result_present_count": sum(row["numeric_result_present"] for row in rows),
            "native_result_msr_present_count": sum(
                row["native_result_msr_present"] for row in rows
            ),
            "manual_layout_reviews_required": sum(
                row["manual_review_required"] for row in rows
            ),
            "result_title_mismatch_routes": title_mismatch_routes,
            "result_title_unresolved_routes": title_unresolved_routes,
        },
        "duplicate_groups": {
            "graphical_model": [
                {"sha256": digest, "routes": routes}
                for digest, routes in sorted(model_duplicates.items())
            ],
            "simulation_result": [
                {"sha256": digest, "routes": routes}
                for digest, routes in sorted(result_duplicates.items())
            ],
        },
        "rows": rows,
    }


def markdown_path(image: dict[str, Any] | None) -> str:
    return f"`{image['path']}`" if image else "缺"


def write_markdown(data: dict[str, Any], path: Path) -> None:
    summary = data["summary"]
    lines = [
        "# 控制器报告资产审计",
        "",
        "状态：`static_audit_pending_manual_mworks_review`。这是一张正式交付前的审计台账，不是第三份参赛交付物。",
        "",
        "## 结论",
        "",
        f"- 报告资产：`{summary['report_asset_pair_count']}/67` 条路线已有模型图和结果图；缺少的两条为 `{', '.join(summary['missing_visual_asset_routes'])}`，且均必须维持实现阻塞口径。",
        f"- 模型图存在 `{summary['model_duplicate_group_count']}` 组字节级复用；若要求每条路线具有独立截图，至少需替换 `{summary['model_duplicate_replacement_count']}` 张重复副本。",
        f"- 结果图存在 `{summary['result_duplicate_group_count']}` 组字节级复用；至少需替换 `{summary['result_duplicate_replacement_count']}` 张重复副本。",
        f"- `{len(summary['vertical_model_capture_routes'])}` 条模型图是纵向长图，不能直接缩放插入正文：`{', '.join(summary['vertical_model_capture_routes'])}`。",
        f"- 静态证据中 `{summary['model_source_present_count']}/67` 有模型源码、`{summary['numeric_result_present_count']}/67` 有数值结果或指标、`{summary['native_result_msr_present_count']}/67` 可定位到原生 `Result.msr`。未找到 MSR 不等于结果无效，但正文不能把它描述为已复核的原生结果。",
        f"- 仍需逐项打开并确认内部走线的路线数：`{summary['manual_layout_reviews_required']}`。",
        "- 源码类别：`{}`。其中原子 CFunction 包装器只能保留接口接入/部署证据，不能作为正文内部控制律图：`{}`。".format(
            ", ".join(
                f"{name}={count}"
                for name, count in summary["source_classification_counts"].items()
            ),
            ", ".join(summary["atomic_cfunction_wrapper_routes"]) or "无",
        ),
        "- 源码映射不唯一，必须先选择实际内部模型：`{}`。".format(
            ", ".join(summary["source_mapping_ambiguous_routes"]) or "无"
        ),
        "- 结果窗口标题与该路线源码不匹配，不能写入报告结论：`{}`。".format(
            ", ".join(summary["result_title_mismatch_routes"]) or "无"
        ),
        "- 结果窗口标题无法由文件名机器绑定到当前源码，仍需在 MWORKS 现场确认：`{}`。".format(
            ", ".join(summary["result_title_unresolved_routes"]) or "无"
        ),
        "",
        "## 审计边界",
        "",
    ]
    lines.extend(f"- {item}" for item in data["claim_boundary"])
    lines.extend(
        [
            "",
            "## 固定复核顺序",
            "",
            "1. 先处理重复图和纵向长图：打开每条路线的实际内部控制律子模型，而不是 `ExperimentRunner` 或只有左右端口的接口壳。",
            "2. 依次确认输入误差、控制律、关键增益/积分/观测/预测/约束环节、输出分配和反馈闭环的走线；只有结构可读才可记为 `layout_passed`。",
            "3. 结果窗口必须同时确认窗口标题、结果树、曲线名称、场景/Run ID 与当前路线一致；固定输入响应不能单独写成闭环性能结论。",
            "4. 每条核心路线完成后回填本表对应状态；只有 `core_candidate_after_manual_review` 才允许进入技术报告正文。其他路线保留为覆盖矩阵或证据库，不再批量缩放插图。",
            "",
            "## 重复图组",
            "",
            "### 图形模型",
            "",
        ]
    )
    for group in data["duplicate_groups"]["graphical_model"]:
        lines.append(f"- `{', '.join(group['routes'])}`")
    lines.extend(["", "### 仿真结果", ""])
    for group in data["duplicate_groups"]["simulation_result"]:
        lines.append(f"- `{', '.join(group['routes'])}`")
    lines.extend(
        [
            "",
            "## 逐路线台账",
            "",
            "| 家族 | 路线 | 模型图 | 结果图 | 源码 | 源码类别 | 数值 | MSR | 布局动作 | 结果标题 | 结果正文使用 | 结果动作 | 报告用途 |",
            "|---|---|---|---|---:|---|---:|---:|---|---|---|---|---|",
        ]
    )
    for row in data["rows"]:
        lines.append(
            "| {family} | `{controller}` | {model} | {result} | {source} | `{classification}` | {numeric} | {msr} | `{layout}` | `{binding}` | `{result_use}` | `{evidence}` | `{use}` |".format(
                family=row["family"],
                controller=row["controller"],
                model=markdown_path(row["graphical_model"]),
                result=markdown_path(row["simulation_result"]),
                source="有" if row["model_source_present"] else "缺",
                classification=row["source_classification"],
                numeric="有" if row["numeric_result_present"] else "缺",
                msr="有" if row["native_result_msr_present"] else "待现场确认",
                layout=row["graphical_layout_status"],
                binding=row["result_title_binding_status"],
                result_use=row["result_report_use"],
                evidence=row["simulation_evidence_status"],
                use=row["report_use"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT))
    )
    args = parser.parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    data = build_audit()
    json_path = output_dir / "控制器证据审计.json"
    markdown_file = output_dir / "控制器证据审计.md"
    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_markdown(data, markdown_file)
    print(
        json.dumps(
            {
                "ok": len(data["rows"]) == 67,
                "json": rel(json_path),
                "markdown": rel(markdown_file),
                **data["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if len(data["rows"]) == 67 else 1


if __name__ == "__main__":
    raise SystemExit(main())
