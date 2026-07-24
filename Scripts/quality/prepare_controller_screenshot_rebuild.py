#!/usr/bin/env python3
"""Archive legacy exports and materialize current G5 native screenshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
ACTIVE_ROOT = ROOT / "Docs" / "报告" / "图" / "控制器"
ARCHIVE_ROOT = ROOT / "Docs" / "报告" / "图" / "归档" / "控制器旧导出资产_20260722"
ARCHIVE_MANIFEST = ARCHIVE_ROOT / "LEGACY_CONTROLLER_EXPORT_ARCHIVE_MANIFEST.json"
OUTPUT_ROOT = ROOT / "Docs" / "报告" / "审计" / "控制器原生截图归位"
OUTPUT_JSON = OUTPUT_ROOT / "CONTROLLER_SCREENSHOT_REBUILD_MANIFEST.json"
OUTPUT_MD = OUTPUT_ROOT / "CONTROLLER_SCREENSHOT_REBUILD_MANIFEST.md"
G5_REVIEW_ROOT = ROOT / "Results" / "control_platform" / "g5_graphical_structure_review_20260722" / "reviews"
MATERIALIZATION_JSON = OUTPUT_ROOT / "NATIVE_STRUCTURE_SCREENSHOT_MATERIALIZATION.json"
SLOT_GITKEEP_NAME = ".gitkeep"
SLOT_GITKEEP_CONTENT = "# Keeps this controller screenshot slot in version control until native evidence is captured.\n"

FAMILIES = {
    "pid_family": "01_PID族",
    "classic_robust": "02_线性与鲁棒",
    "sliding_mode": "03_滑模控制",
    "optimization": "04_MPC族",
    "geometric_flatness": "05_几何与平坦",
    "learning": "06_学习控制",
    "fixed_integrated": "07_固定集成链",
}
EXCLUSIONS = {
    "mu_synthesis": "当前工程缺少可运行的动态 mu-Synthesis 实现，不以静态图或邻近算法替代。",
    "neural_smc": "当前工程缺少冻结训练资产、定长推理与回退验证，不以其他学习或滑模路线替代。",
    "px4ctrl": "ROS1/PX4 运行时工程基线，不伪造 MWORKS 图形模型，也不进入本批控制器图审对比。",
}


class RebuildError(ValueError):
    pass


def rp(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise RebuildError(f"path escapes project root: {path}") from exc


def dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RebuildError(f"JSON root must be an object: {rp(path)}")
    return value


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise RebuildError(f"invalid PNG: {rp(path)}")
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        raise RebuildError(f"PNG has invalid dimensions: {rp(path)}")
    return width, height


def g5_structure_source(scheme_id: str) -> tuple[Path, dict[str, Any]]:
    packet_path = G5_REVIEW_ROOT / scheme_id / "G5_REVIEW_PACKET.json"
    if not packet_path.is_file():
        raise RebuildError(f"{scheme_id}: missing current G5 packet: {rp(packet_path)}")
    packet = read(packet_path)
    screenshots = packet.get("evidence", {}).get("mworks_phase_screenshots")
    if not isinstance(screenshots, list) or len(screenshots) != 1 or not isinstance(screenshots[0], str):
        raise RebuildError(f"{scheme_id}: current G5 packet must bind exactly one native structure screenshot")
    source = ROOT / screenshots[0]
    rp(source)
    if not source.is_file():
        raise RebuildError(f"{scheme_id}: native structure screenshot is missing: {screenshots[0]}")
    width, height = png_dimensions(source)
    source_sha256 = digest(source)
    capture_manifest = packet.get("evidence", {}).get("screenshot_manifest")
    capture_manifest_path = ROOT / str(capture_manifest) if isinstance(capture_manifest, str) else None
    if capture_manifest_path is None:
        raise RebuildError(f"{scheme_id}: current G5 packet has no screenshot manifest")
    rp(capture_manifest_path)
    if not capture_manifest_path.is_file():
        raise RebuildError(f"{scheme_id}: current G5 screenshot manifest is missing: {capture_manifest}")
    capture = read(capture_manifest_path)
    captures = capture.get("captures")
    if not isinstance(captures, list) or len(captures) != 1 or not isinstance(captures[0], dict):
        raise RebuildError(f"{scheme_id}: current G5 screenshot manifest must bind exactly one capture")
    manifest_capture = captures[0]
    manifest_path = manifest_capture.get("path")
    manifest_sha256 = manifest_capture.get("sha256")
    if not isinstance(manifest_path, str) or (ROOT / manifest_path).resolve() != source.resolve():
        raise RebuildError(f"{scheme_id}: packet and screenshot-manifest paths disagree")
    if not isinstance(manifest_sha256, str) or manifest_sha256.lower() != source_sha256.lower():
        raise RebuildError(f"{scheme_id}: packet capture hash does not match source screenshot")
    return source, {
        "g5_review_packet": rp(packet_path),
        "source_screenshot": rp(source),
        "source_sha256": source_sha256,
        "source_width": width,
        "source_height": height,
        "capture_manifest": rp(capture_manifest_path) if capture_manifest_path else None,
        "capture_manifest_sha256": manifest_sha256,
    }


def current_rows() -> list[dict[str, Any]]:
    value = read(MAP_PATH)
    rows = value.get("schemes")
    if value.get("schema") != "mosim.current_model_entry_map.v1":
        raise RebuildError("current model map schema is invalid")
    if not isinstance(rows, list) or len(rows) != 49 or not all(isinstance(row, dict) for row in rows):
        raise RebuildError("current model map must retain exactly 49 scheme rows")
    by_id = {str(row.get("scheme_id")): row for row in rows}
    expected = Counter(
        {
            "resolved_current_model": 46,
            "blocked_missing_current_model": 2,
            "not_applicable_runtime_baseline": 1,
        }
    )
    actual = Counter(str(row.get("mapping_state")) for row in rows)
    if len(by_id) != 49 or actual != expected:
        raise RebuildError(f"unexpected current-model distribution: {dict(actual)}")
    if by_id.get("px4ctrl", {}).get("mapping_state") != "not_applicable_runtime_baseline":
        raise RebuildError("px4ctrl must remain the runtime-only baseline")
    for scheme_id in ("mu_synthesis", "neural_smc"):
        if by_id.get(scheme_id, {}).get("mapping_state") != "blocked_missing_current_model":
            raise RebuildError(f"{scheme_id} must remain blocked")
    return rows


def archived_record(path: Path, origin: str) -> dict[str, Any]:
    record = {
        "origin_path": origin,
        "archived_path": rp(path),
        "kind": "png" if path.suffix.lower() == ".png" else "legacy_note",
        "sha256": digest(path),
        "bytes": path.stat().st_size,
    }
    if record["kind"] == "png":
        with path.open("rb") as stream:
            header = stream.read(24)
        if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
            raise RebuildError(f"invalid PNG: {rp(path)}")
        record["width"], record["height"] = struct.unpack(">II", header[16:24])
    return record


def archive_errors() -> list[str]:
    if not ARCHIVE_MANIFEST.is_file():
        return [f"missing archive manifest: {rp(ARCHIVE_MANIFEST)}"]
    try:
        manifest = read(ARCHIVE_MANIFEST)
    except Exception as exc:
        return [str(exc)]
    files = manifest.get("files")
    if manifest.get("schema") != "mosim.legacy_controller_export_archive.v1":
        return ["legacy archive schema is invalid"]
    if not isinstance(files, list) or not files:
        return ["legacy archive has no file records"]
    errors: list[str] = []
    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            errors.append("legacy archive row is not an object")
            continue
        target = item.get("archived_path")
        if not isinstance(target, str) or target in seen:
            errors.append("legacy archive paths must be unique")
            continue
        seen.add(target)
        path = ROOT / target
        if not path.is_file():
            errors.append(f"archived file is missing: {target}")
        elif item.get("sha256") != digest(path):
            errors.append(f"archived file hash drift: {target}")
    return errors


def write_readmes() -> None:
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    (ARCHIVE_ROOT / "README.md").write_text(
        "# 旧控制器导出资产归档\n\n"
        "本目录保存 2026-07-22 前报告树中的控制器导出图片和阻塞说明，只保留可追溯历史，不能作为当前图审或仿真证据。\n\n"
        "完整哈希和原路径见 LEGACY_CONTROLLER_EXPORT_ARCHIVE_MANIFEST.json。\n",
        encoding="utf-8",
        newline="\n",
    )
    ACTIVE_ROOT.mkdir(parents=True, exist_ok=True)
    (ACTIVE_ROOT / "README.md").write_text(
        "# 当前控制器原生窗口截图\n\n"
        "本目录保存 46 条当前 MWORKS 图审对象的 G5 packet 绑定原生整窗截图。每条路线的 01_图形模型.png 必须保持原生窗口宽高比，不得使用 MWORKS 导出画布、报告副本、历史结果图或裁切变形图。具体来源、冻结模型入口和哈希见 Docs/报告/审计/控制器原生截图归位/CONTROLLER_SCREENSHOT_REBUILD_MANIFEST.json。\n\n"
        "02_最小闭环结果原生窗口.png 只允许在 G6 正式仿真后写入；当前结构截图不代表仿真、代码生成或运行时通过。旧导出图片和旧阻塞说明已归档到同级归档目录，不能复制回本目录。\n",
        encoding="utf-8",
        newline="\n",
    )


def archive_legacy() -> dict[str, Any]:
    if ARCHIVE_ROOT.exists() and any(ARCHIVE_ROOT.iterdir()):
        raise RebuildError(f"archive destination is not empty: {rp(ARCHIVE_ROOT)}")
    if not ACTIVE_ROOT.is_dir():
        raise RebuildError(f"active controller directory is missing: {rp(ACTIVE_ROOT)}")
    files = sorted(path for path in ACTIVE_ROOT.rglob("*") if path.is_file())
    invalid = [path for path in files if path.suffix.lower() not in {".png", ".md"}]
    if invalid:
        raise RebuildError("unsupported legacy file type: " + ", ".join(rp(path) for path in invalid))
    if not files:
        raise RebuildError("legacy source contains no files")
    records: list[dict[str, Any]] = []
    for source in files:
        origin = rp(source)
        relative = source.relative_to(ACTIVE_ROOT)
        # Keep the archive's own README separate from the historic root README.
        # Otherwise write_readmes() would overwrite the latter after migration.
        target = (
            ARCHIVE_ROOT / "legacy_root_README.md"
            if relative == Path("README.md")
            else ARCHIVE_ROOT / relative
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        records.append(archived_record(target, origin))
    for directory in sorted((path for path in ACTIVE_ROOT.rglob("*") if path.is_dir()), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    manifest = {
        "schema": "mosim.legacy_controller_export_archive.v1",
        "scope": "Historical exported report images and state notes only; not current graphical-review or simulation evidence.",
        "source_root_before_archive": "Docs/报告/图/控制器",
        "archive_root": rp(ARCHIVE_ROOT),
        "file_count": len(records),
        "png_count": sum(record["kind"] == "png" for record in records),
        "legacy_note_count": sum(record["kind"] == "legacy_note" for record in records),
        "files": records,
    }
    ARCHIVE_MANIFEST.write_text(dump(manifest), encoding="utf-8", newline="\n")
    write_readmes()
    return {
        "file_count": manifest["file_count"],
        "png_count": manifest["png_count"],
        "legacy_note_count": manifest["legacy_note_count"],
    }


def screenshot_slot(row: dict[str, Any]) -> dict[str, Any]:
    scheme_id = str(row["scheme_id"])
    category = str(row["category"])
    role = str(row.get("current_model_role"))
    family = FAMILIES.get(category)
    if family is None:
        raise RebuildError(f"{scheme_id}: unsupported category {category}")
    if role == "graphical_controller_core":
        name, kind = "01_图形模型.png", "internal_control_law"
    elif role == "fixed_integrated_whole_aircraft_closed_loop":
        name, kind = "01_图形模型.png", "fixed_integrated_whole_aircraft"
    else:
        raise RebuildError(f"{scheme_id}: unsupported model role {role}")
    directory = ACTIVE_ROOT / family / scheme_id
    _, source_metadata = g5_structure_source(scheme_id)
    return {
        "scheme_id": scheme_id,
        "display_name_zh": row.get("display_name_zh"),
        "category": category,
        "family_directory": family,
        "review_kind": kind,
        "review_target": {
            "model_file": row.get("current_model_file"),
            "model_class": row.get("current_model_class"),
            "model_sha256": row.get("current_model_sha256"),
            "model_role": role,
        },
        "asset_directory": rp(directory),
        "directory_version_marker": rp(directory / SLOT_GITKEEP_NAME),
        "required_assets": {
            "structure_native_window": rp(directory / name),
            "minimum_closed_loop_result_native_window": rp(directory / "02_最小闭环结果原生窗口.png"),
            "capture_manifest": source_metadata["capture_manifest"],
            "g5_review_packet": source_metadata["g5_review_packet"],
        },
        "source_capture": source_metadata,
        "capture_rules": {
            "allowed_source": "windows_mcp_direct_whole_window_capture_only",
            "capture_surface": "Windows MCP direct whole-window or desktop capture of the rendered MWORKS window",
            "preserve_window_native_aspect_ratio": True,
            "forbidden_sources": [
                "exported_canvas",
                "report_copy",
                "historical_result_capture",
                "cropped_or_aspect_ratio_distorted_capture",
                "wrapper_only_port_shell",
            ],
        },
    }


def sync_slot_directories(slots: list[dict[str, Any]]) -> None:
    for slot in slots:
        directory = ROOT / str(slot["asset_directory"])
        directory.mkdir(parents=True, exist_ok=True)
        (directory / SLOT_GITKEEP_NAME).write_text(
            SLOT_GITKEEP_CONTENT,
            encoding="utf-8",
            newline="\n",
        )


def materialize_native_structure(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Copy the packet-bound native window capture into the report asset tree."""
    records: list[dict[str, Any]] = []
    for slot in slots:
        source = ROOT / str(slot["source_capture"]["source_screenshot"])
        target = ROOT / str(slot["required_assets"]["structure_native_window"])
        source_sha256 = str(slot["source_capture"]["source_sha256"])
        existed = target.exists()
        if existed:
            if digest(target).lower() != source_sha256.lower():
                raise RebuildError(
                    f"{slot['scheme_id']}: refusing to overwrite a different report screenshot: {rp(target)}"
                )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        target_width, target_height = png_dimensions(target)
        target_sha256 = digest(target)
        if target_sha256.lower() != source_sha256.lower():
            raise RebuildError(f"{slot['scheme_id']}: materialized screenshot hash drifted")
        if (target_width, target_height) != (
            slot["source_capture"]["source_width"],
            slot["source_capture"]["source_height"],
        ):
            raise RebuildError(f"{slot['scheme_id']}: materialized screenshot dimensions drifted")
        records.append(
            {
                "scheme_id": slot["scheme_id"],
                "source": slot["source_capture"]["source_screenshot"],
                "target": rp(target),
                "sha256": target_sha256,
                "width": target_width,
                "height": target_height,
                "copied": not existed,
            }
        )
    MATERIALIZATION_JSON.parent.mkdir(parents=True, exist_ok=True)
    MATERIALIZATION_JSON.write_text(
        dump(
            {
                "schema": "mosim.native_structure_screenshot_materialization.v1",
                "scope": "Current G5 packet-bound native structure screenshots only; no simulation result is claimed.",
                "source": "G5_REVIEW_PACKET.evidence.mworks_phase_screenshots[0]",
                "target_root": rp(ACTIVE_ROOT),
                "count": len(records),
                "records": records,
            }
        ),
        encoding="utf-8",
        newline="\n",
    )
    return records


def build_manifest() -> dict[str, Any]:
    rows = current_rows()
    slots = sorted(
        [screenshot_slot(row) for row in rows if row.get("mapping_state") == "resolved_current_model"],
        key=lambda item: (item["family_directory"], item["scheme_id"]),
    )
    active = {rp(path) for path in ACTIVE_ROOT.rglob("*.png") if path.is_file()}
    expected = {
        path
        for slot in slots
        for path in (
            slot["required_assets"]["structure_native_window"],
            slot["required_assets"]["minimum_closed_loop_result_native_window"],
        )
    }
    for slot in slots:
        assets = slot["required_assets"]
        slot["capture_status"] = {
            "structure_native_window": "present_unreviewed" if assets["structure_native_window"] in active else "not_captured",
            "minimum_closed_loop_result_native_window": "present_unreviewed" if assets["minimum_closed_loop_result_native_window"] in active else "not_captured",
        }
    excluded = sorted(
        [
            {
                "scheme_id": str(row["scheme_id"]),
                "mapping_state": row.get("mapping_state"),
                "reason_zh": EXCLUSIONS[str(row["scheme_id"])],
            }
            for row in rows
            if row.get("mapping_state") != "resolved_current_model"
        ],
        key=lambda item: item["scheme_id"],
    )
    errors = archive_errors()
    return {
        "schema": "mosim.controller_screenshot_rebuild_manifest.v1",
        "scope": "Static screenshot rebuild ledger only; no MWORKS review, simulation, code generation, runtime result, or report acceptance is claimed.",
        "source_model_map": rp(MAP_PATH),
        "active_asset_root": rp(ACTIVE_ROOT),
        "archive": {"root": rp(ARCHIVE_ROOT), "manifest": rp(ARCHIVE_MANIFEST), "validation_errors": errors},
        "summary": {
            "catalog_scheme_count": len(rows),
            "current_screenshot_scope_count": len(slots),
            "asset_directory_count": sum((ROOT / slot["asset_directory"]).is_dir() for slot in slots),
            "directory_version_marker_count": sum(
                (ROOT / slot["directory_version_marker"]).is_file() for slot in slots
            ),
            "excluded_from_current_screenshot_scope_count": len(excluded),
            "structure_capture_count": sum(slot["capture_status"]["structure_native_window"] == "present_unreviewed" for slot in slots),
            "minimum_result_capture_count": sum(slot["capture_status"]["minimum_closed_loop_result_native_window"] == "present_unreviewed" for slot in slots),
            "unexpected_active_png_count": len(active - expected),
            "legacy_archive_valid": not errors,
        },
        "excluded_routes": excluded,
        "slots": slots,
        "unexpected_active_pngs": sorted(active - expected),
    }


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    summary, slots, excluded = manifest.get("summary"), manifest.get("slots"), manifest.get("excluded_routes")
    if manifest.get("schema") != "mosim.controller_screenshot_rebuild_manifest.v1":
        return ["screenshot rebuild manifest schema is invalid"]
    if not isinstance(summary, dict) or not isinstance(slots, list) or not isinstance(excluded, list):
        return ["screenshot rebuild manifest is missing summary, slots, or exclusions"]
    errors: list[str] = []
    if summary.get("catalog_scheme_count") != 49:
        errors.append("catalog must retain 49 historical/project routes")
    if summary.get("current_screenshot_scope_count") != 46 or len(slots) != 46:
        errors.append("current screenshot scope must contain exactly 46 routes")
    if summary.get("asset_directory_count") != 46:
        errors.append("screenshot layout must contain exactly 46 initialized directories")
    if summary.get("directory_version_marker_count") != 46:
        errors.append("screenshot layout must contain exactly 46 versioned directory markers")
    if {row.get("scheme_id") for row in excluded if isinstance(row, dict)} != set(EXCLUSIONS):
        errors.append("exclusions must be mu_synthesis, neural_smc, and px4ctrl")
    if len({row.get("scheme_id") for row in slots if isinstance(row, dict)}) != 46:
        errors.append("screenshot slots must have 46 unique scheme IDs")
    if summary.get("unexpected_active_png_count") != 0:
        errors.append("active screenshot tree contains unexpected PNG files")
    if not summary.get("legacy_archive_valid"):
        errors.append("legacy archive integrity check failed")
    for slot in slots:
        if not isinstance(slot, dict):
            errors.append("screenshot slot is not an object")
            continue
        rules = slot.get("capture_rules")
        if not isinstance(rules, dict):
            errors.append("screenshot slot is missing capture rules")
            continue
        if rules.get("allowed_source") != "windows_mcp_direct_whole_window_capture_only":
            errors.append("screenshot slot must require a Windows MCP whole-window capture")
        if rules.get("preserve_window_native_aspect_ratio") is not True:
            errors.append("screenshot slot must preserve the native window aspect ratio")
        marker = ROOT / str(slot.get("directory_version_marker") or "")
        if not marker.is_file() or marker.name != SLOT_GITKEEP_NAME:
            errors.append(f"{slot.get('scheme_id')}: screenshot slot is missing its versioned directory marker")
        elif marker.read_text(encoding="utf-8") != SLOT_GITKEEP_CONTENT:
            errors.append(f"{slot.get('scheme_id')}: screenshot slot versioned directory marker drifted")
    return errors


def render_markdown(manifest: dict[str, Any]) -> str:
    summary = manifest["summary"]
    counts = Counter(slot["family_directory"] for slot in manifest["slots"])
    lines = [
        "# 控制器原生截图重建清单",
        "",
        "状态：native_structure_materialized。本清单记录当前 G5 packet 绑定的原生结构截图归位情况；它不代表任何路线已通过最小闭环仿真、代码生成、运行时或报告性能验收。"
        if summary["structure_capture_count"] == summary["current_screenshot_scope_count"]
        else "状态：static_rebuild_ready。本清单只定义截图槽位和来源边界，不代表任何路线已通过图审或仿真。",
        "",
        "| 项目 | 数量 |",
        "|---|---:|",
        f"| 历史/项目方案注册表 | {summary['catalog_scheme_count']} |",
        f"| 当前原生窗口截图范围 | {summary['current_screenshot_scope_count']} |",
        f"| 已初始化截图目录 | {summary['asset_directory_count']} |",
        f"| 已版本化目录占位符 | {summary['directory_version_marker_count']} |",
        f"| 已归档旧导出资产 | {'完整' if summary['legacy_archive_valid'] else '异常'} |",
        f"| 已采集内部结构原生图 | {summary['structure_capture_count']} |",
        f"| 已采集最小闭环结果原生图 | {summary['minimum_result_capture_count']} |",
        "",
        "六个名义控制族和一个固定集成链分别入库。导出画布、旧报告副本和历史结果截图不能写回当前目录。",
        "",
        "| 目录 | 路线数 |",
        "|---|---:|",
    ]
    lines.extend(f"| {directory} | {count} |" for directory, count in sorted(counts.items()))
    lines.extend(["", "## 不进入本批截图", ""])
    lines.extend(f"- {row['scheme_id']}：{row['reason_zh']}" for row in manifest["excluded_routes"])
    lines.extend(
        [
            "",
            "每个 01_图形模型.png 必须来自冻结模型入口的 Windows MCP 原生整窗/桌面采集，保持窗口原生宽高比，并与 G5 截图 manifest、图审 packet 绑定。02_最小闭环结果原生窗口.png 只能在 G6 正式仿真后写入，不能用结构图、历史结果或空白窗口代替。",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-legacy", action="store_true")
    parser.add_argument("--materialize-native-structure", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        archived = archive_legacy() if args.archive_legacy else None
        manifest = build_manifest()
        if not args.check:
            sync_slot_directories(manifest["slots"])
            if args.materialize_native_structure:
                materialize_native_structure(manifest["slots"])
            manifest = build_manifest()
        errors = validate_manifest(manifest)
        markdown = render_markdown(manifest)
        if args.check:
            if not OUTPUT_JSON.is_file() or read(OUTPUT_JSON) != manifest:
                errors.append("rebuild JSON is absent or stale")
            if not OUTPUT_MD.is_file() or OUTPUT_MD.read_text(encoding="utf-8") != markdown:
                errors.append("rebuild Markdown is absent or stale")
        else:
            OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
            OUTPUT_JSON.write_text(dump(manifest), encoding="utf-8", newline="\n")
            OUTPUT_MD.write_text(markdown, encoding="utf-8", newline="\n")
    except Exception as exc:
        errors = [str(exc)]
        archived = None
    print(dump({"ok": not errors, "archive": archived, "errors": errors}).rstrip())
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
