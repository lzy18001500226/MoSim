#!/usr/bin/env python3
"""Index controller graphical screenshots without overstating simulation evidence."""

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
REVIEWED_ARCHIVE_ROOT = ROOT / "Docs" / "报告" / "图" / "归档" / "控制器未绑定截图候选_20260727"
REVIEWED_ARCHIVE_MANIFEST = REVIEWED_ARCHIVE_ROOT / "UNBOUND_SCREENSHOT_ARCHIVE_MANIFEST.json"
REVIEWED_ARCHIVE_ROLE = "pre_v2_unbound_structure_candidate"
REVIEWED_ARCHIVE_REVIEW_DATE = "2026-07-28"
OUTPUT_ROOT = ROOT / "Docs" / "报告" / "审计" / "控制器原生截图归位"
OUTPUT_JSON = OUTPUT_ROOT / "CONTROLLER_SCREENSHOT_REBUILD_MANIFEST.json"
OUTPUT_MD = OUTPUT_ROOT / "CONTROLLER_SCREENSHOT_REBUILD_MANIFEST.md"
G5_REVIEW_ROOT = ROOT / "Results" / "control_platform" / "g5_graphical_structure_review_20260722" / "reviews"
MATERIALIZATION_JSON = OUTPUT_ROOT / "NATIVE_STRUCTURE_SCREENSHOT_MATERIALIZATION.json"
SLOT_GITKEEP_NAME = ".gitkeep"
SLOT_GITKEEP_CONTENT = "# Keeps this controller screenshot slot in version control until native evidence is captured.\n"

FAMILIES = {
    "pid_family": "01_PID族",
    "linear_robust_state_feedback": "02_线性与鲁棒状态反馈",
    "nonlinear_adaptive": "03_非线性与自适应",
    "sliding_mode": "04_滑模控制",
    "optimization_predictive": "05_最优与预测控制",
    "geometric_flatness": "06_几何与微分平坦",
    "learning": "07_智能与学习",
}
EXCLUSIONS = {
    "pid_awff_linear_eso": "已批准的 MWORKS Profile 设计项；尚无模型、Adapter、Runner 或图审对象。",
    "px4ctrl": "工程/部署基线；已有独立 MWORKS 图形化闭环证据，但不纳入本批 46 条 MWORKS 控制器图审/对比范围。",
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


def available_g5_structure_source(scheme_id: str) -> dict[str, Any] | None:
    """Return current-packet metadata only after genuine G5 evidence exists.

    Empty slots are intentional before native review.  Once a packet is present,
    its binding must pass the strict validation in :func:`g5_structure_source`;
    this helper never treats an old export or an incomplete packet as evidence.
    """

    packet_path = G5_REVIEW_ROOT / scheme_id / "G5_REVIEW_PACKET.json"
    if not packet_path.is_file():
        return None
    _, metadata = g5_structure_source(scheme_id)
    return metadata


def reviewed_archive_structure_sources() -> dict[str, dict[str, Any]]:
    """Return user-reviewed historical graphical candidates keyed by controller ID.

    These assets are allowed to illustrate controller internals after the user's
    visual review. They remain distinct from current G5 packet-bound captures
    and cannot establish a current-source simulation result.
    """

    if not REVIEWED_ARCHIVE_MANIFEST.is_file():
        raise RebuildError(f"missing reviewed screenshot archive: {rp(REVIEWED_ARCHIVE_MANIFEST)}")
    manifest = read(REVIEWED_ARCHIVE_MANIFEST)
    if manifest.get("schema") != "mosim.unbound_controller_screenshot_archive.v1":
        raise RebuildError("reviewed screenshot archive schema is invalid")
    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise RebuildError("reviewed screenshot archive has no file rows")

    sources: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("role") != REVIEWED_ARCHIVE_ROLE:
            continue
        archived_path = row.get("archived_path")
        source_sha256 = row.get("sha256")
        if not isinstance(archived_path, str) or not isinstance(source_sha256, str):
            raise RebuildError("reviewed screenshot archive row is incomplete")
        source = ROOT / archived_path
        if source.name != "01_图形模型.png" or not source.is_file():
            raise RebuildError(f"reviewed structure screenshot is missing: {archived_path}")
        if digest(source).lower() != source_sha256.lower():
            raise RebuildError(f"reviewed structure screenshot hash drifted: {archived_path}")
        scheme_id = source.parent.name
        if scheme_id in sources:
            raise RebuildError(f"duplicate reviewed structure screenshot: {scheme_id}")
        width, height = png_dimensions(source)
        sources[scheme_id] = {
            "review_status": "user_visual_reviewed",
            "review_date": REVIEWED_ARCHIVE_REVIEW_DATE,
            "archive_manifest": rp(REVIEWED_ARCHIVE_MANIFEST),
            "source_screenshot": rp(source),
            "source_sha256": source_sha256,
            "source_width": width,
            "source_height": height,
        }
    return sources


def current_rows() -> list[dict[str, Any]]:
    value = read(MAP_PATH)
    rows = value.get("schemes")
    if value.get("schema") != "mosim.current_model_entry_map.v1":
        raise RebuildError("current model map schema is invalid")
    if not isinstance(rows, list) or len(rows) != 48 or not all(isinstance(row, dict) for row in rows):
        raise RebuildError("current model map must retain exactly 48 active profile rows")
    by_id = {str(row.get("scheme_id")): row for row in rows}
    expected = Counter(
        {
            "resolved_current_model": 46,
            "planned_profile_no_model": 1,
            "pending_mworks_equivalent_core": 1,
        }
    )
    actual = Counter(str(row.get("mapping_state")) for row in rows)
    if len(by_id) != 48 or actual != expected:
        raise RebuildError(f"unexpected current-model distribution: {dict(actual)}")
    if by_id.get("px4ctrl", {}).get("mapping_state") != "pending_mworks_equivalent_core":
        raise RebuildError("px4ctrl catalog row must remain excluded from the 46-controller screenshot scope")
    if by_id.get("pid_awff_linear_eso", {}).get("mapping_state") != "planned_profile_no_model":
        raise RebuildError("pid_awff_linear_eso must remain a planned profile without a model")
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
        "# 控制器图形模型截图\n\n"
        "本目录按当前七个语义控制族收纳 46 条 MWORKS 图审对象。2026-07-28 经用户视觉审核后，01_图形模型.png 从可追溯候选归档按控制器 ID 复制归位；它们用于展示控制器内部结构和连线，不等价于当前源的仿真、性能、代码生成或运行时通过。来源哈希和当前模型入口见 Docs/报告/审计/控制器原生截图归位/CONTROLLER_SCREENSHOT_REBUILD_MANIFEST.json。\n\n"
        "02_最小闭环结果原生窗口.png 仍只允许在后续当前源正式仿真后写入。历史结果图继续留在归档中，不得作为当前 RMSE、排名或七场景结论。\n",
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


def screenshot_slot(row: dict[str, Any], reviewed_sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    scheme_id = str(row["scheme_id"])
    category = str(row["category"])
    role = str(row.get("current_model_role"))
    family = FAMILIES.get(category)
    if family is None:
        raise RebuildError(f"{scheme_id}: unsupported category {category}")
    if role == "graphical_controller_core":
        name, kind = "01_图形模型.png", "internal_control_law"
    elif role == "full_profile_whole_aircraft_closed_loop":
        name, kind = "01_图形模型.png", "named_whole_aircraft_profile"
    else:
        raise RebuildError(f"{scheme_id}: unsupported model role {role}")
    directory = ACTIVE_ROOT / family / scheme_id
    source_metadata = available_g5_structure_source(scheme_id)
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
            "capture_manifest": source_metadata["capture_manifest"] if source_metadata else None,
            "g5_review_packet": source_metadata["g5_review_packet"] if source_metadata else None,
        },
        "source_capture": source_metadata,
        "user_reviewed_archive_source": reviewed_sources.get(scheme_id),
        "capture_rules": {
            "allowed_source": "windows_mcp_direct_whole_window_capture_only",
            "approved_historical_structure_source": "user_visual_reviewed_archive_candidate_only",
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
    expected_directories = {ROOT / str(slot["asset_directory"]) for slot in slots}
    for slot in slots:
        directory = ROOT / str(slot["asset_directory"])
        directory.mkdir(parents=True, exist_ok=True)
        (directory / SLOT_GITKEEP_NAME).write_text(
            SLOT_GITKEEP_CONTENT,
            encoding="utf-8",
            newline="\n",
        )

    # The former layout used a separate fixed-integrated-chain directory.  It
    # is no longer an active family, so remove only its stale generated slots.
    # Refuse to delete anything that is not this script's untouched marker.
    stale_markers = sorted(
        ACTIVE_ROOT.rglob(SLOT_GITKEEP_NAME),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for marker in stale_markers:
        if marker.parent in expected_directories:
            continue
        if marker.read_text(encoding="utf-8") != SLOT_GITKEEP_CONTENT:
            raise RebuildError(f"refusing to remove non-generated screenshot slot: {rp(marker)}")
        siblings = [path for path in marker.parent.iterdir() if path != marker]
        if siblings:
            raise RebuildError(f"refusing to remove populated stale screenshot slot: {rp(marker.parent)}")
        marker.unlink()
        marker.parent.rmdir()

    # Remove now-empty former family directories while retaining the active
    # root and every declared current family directory.
    for directory in sorted(
        (path for path in ACTIVE_ROOT.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        if directory == ACTIVE_ROOT or directory in expected_directories:
            continue
        try:
            directory.rmdir()
        except OSError:
            pass


def materialize_native_structure(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Copy the packet-bound native window capture into the report asset tree."""
    records: list[dict[str, Any]] = []
    for slot in slots:
        source, source_metadata = g5_structure_source(str(slot["scheme_id"]))
        target = ROOT / str(slot["required_assets"]["structure_native_window"])
        source_sha256 = str(source_metadata["source_sha256"])
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
            source_metadata["source_width"],
            source_metadata["source_height"],
        ):
            raise RebuildError(f"{slot['scheme_id']}: materialized screenshot dimensions drifted")
        records.append(
            {
                "scheme_id": slot["scheme_id"],
                "source": source_metadata["source_screenshot"],
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
    reviewed_sources = reviewed_archive_structure_sources()
    slots = sorted(
        [
            screenshot_slot(row, reviewed_sources)
            for row in rows
            if row.get("mapping_state") == "resolved_current_model"
        ],
        key=lambda item: (item["family_directory"], item["scheme_id"]),
    )
    if set(reviewed_sources) != {str(slot["scheme_id"]) for slot in slots}:
        raise RebuildError("reviewed graphical screenshot IDs do not match the 46 current screenshot slots")
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
        source_capture = slot["source_capture"]
        reviewed_source = slot["user_reviewed_archive_source"]
        structure_path = ROOT / assets["structure_native_window"]
        if not structure_path.is_file():
            structure_status = "not_captured"
        elif isinstance(source_capture, dict) and digest(structure_path).lower() == str(source_capture["source_sha256"]).lower():
            structure_status = "present_unreviewed"
        elif isinstance(reviewed_source, dict) and digest(structure_path).lower() == str(reviewed_source["source_sha256"]).lower():
            structure_status = "present_user_reviewed_historical_graphical"
        elif isinstance(source_capture, dict):
            structure_status = "source_hash_mismatch"
        else:
            structure_status = "unbound_active_asset"
        slot["capture_status"] = {
            "structure_native_window": structure_status,
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
        "schema": "mosim.controller_screenshot_rebuild_manifest.v2",
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
            "current_native_structure_capture_count": sum(
                slot["capture_status"]["structure_native_window"] == "present_unreviewed" for slot in slots
            ),
            "user_reviewed_historical_structure_count": sum(
                slot["capture_status"]["structure_native_window"] == "present_user_reviewed_historical_graphical"
                for slot in slots
            ),
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
    if manifest.get("schema") != "mosim.controller_screenshot_rebuild_manifest.v2":
        return ["screenshot rebuild manifest schema is invalid"]
    if not isinstance(summary, dict) or not isinstance(slots, list) or not isinstance(excluded, list):
        return ["screenshot rebuild manifest is missing summary, slots, or exclusions"]
    errors: list[str] = []
    if summary.get("catalog_scheme_count") != 48:
        errors.append("catalog must retain 48 active entries")
    if summary.get("current_screenshot_scope_count") != 46 or len(slots) != 46:
        errors.append("current screenshot scope must contain exactly 46 routes")
    if summary.get("asset_directory_count") != 46:
        errors.append("screenshot layout must contain exactly 46 initialized directories")
    if summary.get("directory_version_marker_count") != 46:
        errors.append("screenshot layout must contain exactly 46 versioned directory markers")
    expected_markers = {
        ROOT / str(slot.get("directory_version_marker") or "")
        for slot in slots
        if isinstance(slot, dict)
    }
    actual_markers = set(ACTIVE_ROOT.rglob(SLOT_GITKEEP_NAME))
    if actual_markers != expected_markers:
        errors.append("screenshot layout contains stale or missing versioned directory markers")
    if {row.get("scheme_id") for row in excluded if isinstance(row, dict)} != set(EXCLUSIONS):
        errors.append("exclusions must be pid_awff_linear_eso and px4ctrl")
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
        if rules.get("approved_historical_structure_source") != "user_visual_reviewed_archive_candidate_only":
            errors.append("screenshot slot must define the approved historical graphical source")
        if rules.get("preserve_window_native_aspect_ratio") is not True:
            errors.append("screenshot slot must preserve the native window aspect ratio")
        marker = ROOT / str(slot.get("directory_version_marker") or "")
        if not marker.is_file() or marker.name != SLOT_GITKEEP_NAME:
            errors.append(f"{slot.get('scheme_id')}: screenshot slot is missing its versioned directory marker")
        elif marker.read_text(encoding="utf-8") != SLOT_GITKEEP_CONTENT:
            errors.append(f"{slot.get('scheme_id')}: screenshot slot versioned directory marker drifted")
        capture_status = slot.get("capture_status") if isinstance(slot.get("capture_status"), dict) else {}
        structure_status = capture_status.get("structure_native_window")
        source_capture = slot.get("source_capture")
        reviewed_source = slot.get("user_reviewed_archive_source")
        assets = slot.get("required_assets") if isinstance(slot.get("required_assets"), dict) else {}
        if structure_status == "present_unreviewed":
            if not isinstance(source_capture, dict):
                errors.append(f"{slot.get('scheme_id')}: captured structure image lacks a current G5 packet binding")
            elif assets.get("capture_manifest") != source_capture.get("capture_manifest") or assets.get("g5_review_packet") != source_capture.get("g5_review_packet"):
                errors.append(f"{slot.get('scheme_id')}: captured structure image packet binding drifted")
        elif structure_status == "present_user_reviewed_historical_graphical":
            structure_path = ROOT / str(assets.get("structure_native_window") or "")
            if not isinstance(reviewed_source, dict):
                errors.append(f"{slot.get('scheme_id')}: reviewed graphical image lacks archive provenance")
            elif reviewed_source.get("review_status") != "user_visual_reviewed" or reviewed_source.get("review_date") != REVIEWED_ARCHIVE_REVIEW_DATE:
                errors.append(f"{slot.get('scheme_id')}: reviewed graphical image has invalid review metadata")
            elif not structure_path.is_file() or digest(structure_path).lower() != str(reviewed_source.get("source_sha256")).lower():
                errors.append(f"{slot.get('scheme_id')}: reviewed graphical image hash drifted")
        elif structure_status != "not_captured":
            errors.append(f"{slot.get('scheme_id')}: active structure image has no approved provenance")
    return errors


def render_markdown(manifest: dict[str, Any]) -> str:
    summary = manifest["summary"]
    counts = Counter(slot["family_directory"] for slot in manifest["slots"])
    lines = [
        "# 控制器原生截图重建清单",
        "",
        "状态：user_reviewed_graphical_assets。46 张历史图形结构候选已在 2026-07-28 经用户视觉审核并按当前族类归位；它们不等价于当前源最小闭环、性能、代码生成或运行时通过。"
        if summary["user_reviewed_historical_structure_count"] == summary["current_screenshot_scope_count"]
        else "状态：screenshot_slots_prepared。本清单只定义截图槽位和来源边界，不代表任何路线已通过图审或仿真。",
        "",
        "| 项目 | 数量 |",
        "|---|---:|",
        f"| 历史/项目方案注册表 | {summary['catalog_scheme_count']} |",
        f"| 当前原生窗口截图范围 | {summary['current_screenshot_scope_count']} |",
        f"| 已初始化截图目录 | {summary['asset_directory_count']} |",
        f"| 已版本化目录占位符 | {summary['directory_version_marker_count']} |",
        f"| 已归档旧导出资产 | {'完整' if summary['legacy_archive_valid'] else '异常'} |",
        f"| 当前 G5 绑定原生结构图 | {summary['current_native_structure_capture_count']} |",
        f"| 用户审核历史图形结构图 | {summary['user_reviewed_historical_structure_count']} |",
        f"| 已采集最小闭环结果原生图 | {summary['minimum_result_capture_count']} |",
        "",
        "七个语义控制族分别入库；五条命名整机 Profile 按其 PID 或最优/预测归属入库，不另设控制器族。用户审核通过的历史图形结构候选可按本清单归位；旧结果截图继续归档，不能作为当前性能结论。",
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
            "当前新采集的 01_图形模型.png 必须来自冻结模型入口的 Windows MCP 原生整窗/桌面采集，保持窗口原生宽高比，并与当前 G5 截图 manifest、图审 packet 绑定。本批用户审核的历史图形结构候选仅用于结构展示。02_最小闭环结果原生窗口.png 只能在后续当前源正式仿真后写入，不能用结构图、历史结果或空白窗口代替。",
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
            write_readmes()
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
