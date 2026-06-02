#!/usr/bin/env python3
"""Check whether MoSim LiDAR/IMU inputs are claimable for Mid360 FAST-LIO."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENE_DIR = ROOT / "Results" / "unreal_scene_mapping" / "factoryenvironmentcollect"
DEFAULT_CONFIG = ROOT / "Config" / "ros2" / "mosim_spark_fast_lio_mid360.yaml"
DEFAULT_SPARK_FASTLIO_ROOT = ROOT / "Results" / "tmp" / "fastlio_ros2_candidates" / "spark-fast-lio"


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def parse_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    try:
        if any(mark in value.lower() for mark in (".", "e")):
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"')


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, out)]
    pending_key: str | None = None
    pending_indent = 0
    pending_items: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if pending_key is not None:
            pending_items.append(line.strip())
            if "]" in line:
                parent = stack[-1][1]
                joined = " ".join(pending_items)
                parent[pending_key] = parse_scalar(joined)
                pending_key = None
                pending_items = []
            continue
        if ":" not in line:
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, value = line.strip().split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        value = value.strip()
        if value.startswith("[") and not value.endswith("]"):
            pending_key = key
            pending_indent = indent
            pending_items = [value]
            continue
        if not value:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(value)
    if pending_key is not None:
        raise ValueError(f"unterminated list in {path} near indent {pending_indent}")
    return out


def ros_params(config: dict[str, Any]) -> dict[str, Any]:
    root = config.get("/**", config.get("**", {}))
    return root.get("ros__parameters", {})


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl_sample(path: Path, *, max_frames: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
            if len(rows) >= max_frames:
                break
    return rows


def point_count(frame: dict[str, Any]) -> int:
    if isinstance(frame.get("points_m"), list):
        return len(frame["points_m"])
    if isinstance(frame.get("points_lidar_m"), list):
        return len(frame["points_lidar_m"])
    return 0


def summarize_frames(frames: list[dict[str, Any]]) -> dict[str, Any]:
    counts = [point_count(frame) for frame in frames]
    times = [float(frame.get("time", frame.get("time_s", 0.0))) for frame in frames]
    attrs = [frame.get("point_attributes", []) for frame in frames]
    attr_count_matches = [
        isinstance(attr, list) and len(attr) == point_count(frame)
        for frame, attr in zip(frames, attrs)
    ]
    attr_keys = set()
    line_values = set()
    for attr_list in attrs:
        if not isinstance(attr_list, list):
            continue
        for attr in attr_list[:2000]:
            if not isinstance(attr, dict):
                continue
            attr_keys.update(attr.keys())
            if "line" in attr:
                line_values.add(int(attr["line"]))
    deltas = [right - left for left, right in zip(times, times[1:])]
    return {
        "frames_sampled": len(frames),
        "points_per_frame_min": min(counts) if counts else 0,
        "points_per_frame_max": max(counts) if counts else 0,
        "points_per_frame_avg": round(sum(counts) / len(counts), 3) if counts else 0.0,
        "time_first_s": round(times[0], 6) if times else None,
        "time_last_s": round(times[-1], 6) if times else None,
        "nonmonotonic_time_pairs": sum(1 for delta in deltas if delta < 0.0),
        "duplicate_time_pairs": sum(1 for delta in deltas if abs(delta) < 1e-12),
        "point_attribute_keys": sorted(attr_keys),
        "point_attribute_count_matches_points": all(attr_count_matches) if attr_count_matches else False,
        "observed_lines": sorted(line_values),
    }


def summarize_fastlio_dataset(frames: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_frames(frames)
    synthetic_flags = []
    imu_sources = set()
    yaws = []
    for frame in frames:
        imu = frame.get("synthetic_imu", {})
        if isinstance(imu, dict):
            synthetic_flags.append(not bool(imu.get("is_measured_imu")))
            imu_sources.add(str(imu.get("source", "unknown")))
        rpy = frame.get("rpy_rad", [])
        if isinstance(rpy, list) and len(rpy) >= 3:
            yaws.append(float(rpy[2]))
    summary.update(
        {
            "synthetic_imu_frames_sampled": sum(1 for item in synthetic_flags if item),
            "measured_imu_frames_sampled": sum(1 for item in synthetic_flags if not item),
            "imu_sources": sorted(imu_sources),
            "yaw_span_rad_sampled": round(max(yaws) - min(yaws), 9) if yaws else 0.0,
        }
    )
    return summary


def add_finding(findings: list[dict[str, str]], severity: str, surface: str, detail: str, action: str) -> None:
    findings.append({"severity": severity, "surface": surface, "detail": detail, "action": action})


def inspect_spark_fastlio_support(root: Path) -> dict[str, Any]:
    preprocess_cpp = root / "spark_fast_lio" / "src" / "preprocess.cpp"
    preprocess_h = root / "spark_fast_lio" / "include" / "preprocess.h"
    cmake = root / "spark_fast_lio" / "CMakeLists.txt"
    package_xml = root / "spark_fast_lio" / "package.xml"
    result: dict[str, Any] = {
        "root": rel(root) if root.exists() else rel(root),
        "preprocess_cpp": rel(preprocess_cpp),
        "preprocess_h": rel(preprocess_h),
        "source_exists": preprocess_cpp.exists() and preprocess_h.exists(),
        "pointcloud2_supported_lidar_types": [],
        "livox_custommsg_guarded": False,
        "livox_ros2_custommsg_supported": False,
        "pointcloud2_livox_supported": False,
    }
    if not result["source_exists"]:
        return result
    cpp = preprocess_cpp.read_text(encoding="utf-8", errors="replace")
    header = preprocess_h.read_text(encoding="utf-8", errors="replace")
    cmake_text = cmake.read_text(encoding="utf-8", errors="replace") if cmake.exists() else ""
    package_text = package_xml.read_text(encoding="utf-8", errors="replace") if package_xml.exists() else ""
    supported = []
    for label in ("OUST64", "KMOUST64", "VELO16", "AVIA"):
        marker = f"case {label}:"
        if marker in cpp:
            supported.append(label)
    result["pointcloud2_supported_lidar_types"] = supported
    result["livox_custommsg_guarded"] = (
        "LIVOX_ROS_DRIVER_FOUND" in cpp
        and (
            ("livox_ros_driver::CustomMsg" in cpp and "livox_ros_driver::CustomMsg" in header)
            or (
                "livox_ros_driver2::msg::CustomMsg" in cpp
                and "livox_ros_driver2::msg::CustomMsg" in header
            )
        )
    )
    result["livox_ros2_custommsg_supported"] = (
        "livox_ros_driver2::msg::CustomMsg" in cpp
        and "livox_ros_driver2::msg::CustomMsg" in header
        and "find_package(livox_ros_driver2" in cmake_text
        and "livox_ros_driver2" in package_text
    )
    result["pointcloud2_livox_supported"] = "AVIA" in supported
    return result


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    scene_dir = project_path(args.scene_dir)
    config_path = project_path(args.config)
    manifest_path = project_path(args.manifest or scene_dir / "livox_like_lidar_manifest.json")
    livox_frames_path = project_path(args.livox_frames or scene_dir / "livox_like_lidar_frames.jsonl")
    fastlio_dataset_path = project_path(args.fastlio_dataset or scene_dir / "fastlio_replay_dataset.jsonl")

    params = ros_params(parse_simple_yaml(config_path))
    preprocess = params.get("preprocess", {})
    common = params.get("common", {})
    mapping = params.get("mapping", {})
    manifest = read_json(manifest_path) if manifest_path.exists() else {}
    livox_frames = read_jsonl_sample(livox_frames_path, max_frames=args.sample_frames) if livox_frames_path.exists() else []
    fastlio_frames = read_jsonl_sample(fastlio_dataset_path, max_frames=args.sample_frames) if fastlio_dataset_path.exists() else []
    livox_summary = summarize_frames(livox_frames)
    fastlio_summary = summarize_fastlio_dataset(fastlio_frames)
    spark_support = inspect_spark_fastlio_support(project_path(args.spark_fastlio_root))

    findings: list[dict[str, str]] = []
    if preprocess.get("lidar_type") != 1:
        add_finding(
            findings,
            "error",
            "FAST-LIO config",
            f"lidar_type={preprocess.get('lidar_type')} but Mid360/Livox requires Livox serial semantics.",
            "Use lidar_type=1 before claiming Mid360 FAST-LIO.",
        )
    if preprocess.get("scan_line") != 4:
        add_finding(
            findings,
            "error",
            "FAST-LIO config",
            f"scan_line={preprocess.get('scan_line')} but Mid360 references and MoSim dense replay emit lines 0-3.",
            "Use scan_line=4 and verify line attributes.",
        )
    if float(preprocess.get("blind", 0.0)) < 0.5:
        add_finding(
            findings,
            "warning",
            "FAST-LIO config",
            f"blind={preprocess.get('blind')} is below the current Mid360 baseline.",
            "Keep blind at 0.5m unless a calibrated sensor model says otherwise.",
        )
    if bool(mapping.get("extrinsic_est_en")):
        add_finding(
            findings,
            "warning",
            "extrinsic",
            "online extrinsic estimation is enabled for synthetic aligned frames.",
            "Use fixed documented extrinsics for deterministic replay until calibration exists.",
        )
    if manifest and float(manifest.get("points_per_frame_avg", 0.0)) < args.min_dense_points:
        add_finding(
            findings,
            "error",
            "dense LiDAR manifest",
            f"manifest avg points/frame={manifest.get('points_per_frame_avg')} below {args.min_dense_points}.",
            "Regenerate dense Mid360 replay before FAST-LIO runtime.",
        )
    if livox_summary["points_per_frame_avg"] < args.min_dense_points:
        add_finding(
            findings,
            "error",
            "dense LiDAR frames",
            f"sample avg points/frame={livox_summary['points_per_frame_avg']} below {args.min_dense_points}.",
            "Do not run localization on low-density toy scans.",
        )
    required_attrs = {"offset_time_ns", "line", "reflectivity", "tag"}
    observed_attrs = set(livox_summary["point_attribute_keys"])
    missing_attrs = sorted(required_attrs - observed_attrs)
    if missing_attrs:
        add_finding(
            findings,
            "error",
            "dense LiDAR attributes",
            f"missing point attributes: {', '.join(missing_attrs)}.",
            "Preserve Livox-like per-point timing, line, reflectivity, and tag fields.",
        )
    if livox_summary["observed_lines"] and livox_summary["observed_lines"] != [0, 1, 2, 3]:
        add_finding(
            findings,
            "error",
            "dense LiDAR scan lines",
            f"observed lines={livox_summary['observed_lines']}.",
            "Ensure dense replay emits exactly Mid360 line ids 0-3 for this config.",
        )
    if livox_summary["nonmonotonic_time_pairs"] > 0:
        add_finding(
            findings,
            "error",
            "dense LiDAR time",
            "frame timestamps are nonmonotonic.",
            "Fix sensor clocking before localization.",
        )
    livox_runtime_supported = bool(spark_support.get("livox_ros2_custommsg_supported"))
    if (
        fastlio_summary["points_per_frame_avg"]
        and fastlio_summary["points_per_frame_avg"] < args.min_fastlio_points
        and not livox_runtime_supported
    ):
        add_finding(
            findings,
            "error",
            "FAST-LIO replay dataset",
            f"legacy dataset avg points/frame={fastlio_summary['points_per_frame_avg']} below {args.min_fastlio_points}.",
            "Route FAST-LIO input through the dense Mid360 transport, not the old 512-point adapter.",
        )
    if (
        fastlio_summary["point_attribute_keys"] == []
        and fastlio_summary["points_per_frame_avg"] > 0
        and not livox_runtime_supported
    ):
        add_finding(
            findings,
            "error",
            "FAST-LIO replay dataset",
            "legacy dataset has no per-point Livox attributes.",
            "Do not use this file as the claimable FAST-LIO input.",
        )
    if fastlio_summary["synthetic_imu_frames_sampled"] > 0 and not livox_runtime_supported:
        add_finding(
            findings,
            "error",
            "IMU source",
            f"sample includes {fastlio_summary['synthetic_imu_frames_sampled']} synthetic IMU frames.",
            "Feed MWORKS/PX4-equivalent high-rate IMU into ROS2 before localization claims.",
        )
    if (
        preprocess.get("lidar_type") == 1
        and spark_support["source_exists"]
        and not spark_support["pointcloud2_livox_supported"]
        and not livox_runtime_supported
    ):
        add_finding(
            findings,
            "error",
            "FAST-LIO implementation",
            "spark-fast-lio PointCloud2 preprocessing handles only "
            + ", ".join(spark_support["pointcloud2_supported_lidar_types"])
            + "; lidar_type=1/Livox is compiled only through a guarded CustomMsg path.",
            "Use a Livox CustomMsg-capable runtime, add livox_ros_driver message support, or switch to a FAST-LIO variant that natively accepts Mid360/Livox input.",
        )
    if livox_runtime_supported and fastlio_summary["points_per_frame_avg"]:
        add_finding(
            findings,
            "warning",
            "legacy FAST-LIO dataset",
            "legacy fastlio_replay_dataset is present but is no longer the claimable Mid360 input path.",
            "Use dense Livox CustomMsg plus MWORKS/ROS2 IMU for runtime gates; keep legacy dataset only as a degraded historical reference.",
        )

    error_count = sum(1 for finding in findings if finding["severity"] == "error")
    warning_count = sum(1 for finding in findings if finding["severity"] == "warning")
    dense_lidar_ready = (
        preprocess.get("lidar_type") == 1
        and preprocess.get("scan_line") == 4
        and livox_summary["points_per_frame_avg"] >= args.min_dense_points
        and required_attrs <= observed_attrs
        and livox_summary["nonmonotonic_time_pairs"] == 0
    )
    status = "claimable_input_ready" if error_count == 0 else "not_claimable"
    if error_count > 0 and dense_lidar_ready:
        status = "dense_lidar_ready_but_fastlio_input_blocked"
    return {
        "schema": "mosim.fastlio_input_contract.v1",
        "status": status,
        "dense_lidar_ready": dense_lidar_ready,
        "error_count": error_count,
        "warning_count": warning_count,
        "paths": {
            "scene_dir": rel(scene_dir),
            "config": rel(config_path),
            "manifest": rel(manifest_path),
            "livox_frames": rel(livox_frames_path),
            "fastlio_dataset": rel(fastlio_dataset_path),
        },
        "config": {
            "common": {
                "lid_topic": common.get("lid_topic"),
                "imu_topic": common.get("imu_topic"),
                "time_sync_en": common.get("time_sync_en"),
                "time_offset_lidar_to_imu": common.get("time_offset_lidar_to_imu"),
            },
            "preprocess": {
                "lidar_type": preprocess.get("lidar_type"),
                "scan_line": preprocess.get("scan_line"),
                "scan_rate": preprocess.get("scan_rate"),
                "timestamp_unit": preprocess.get("timestamp_unit"),
                "blind": preprocess.get("blind"),
            },
            "mapping": {
                "extrinsic_est_en": mapping.get("extrinsic_est_en"),
                "extrinsic_T": mapping.get("extrinsic_T"),
                "extrinsic_R": mapping.get("extrinsic_R"),
            },
        },
        "manifest_summary": {
            "schema": manifest.get("schema"),
            "frame_count": manifest.get("frame_count"),
            "points_per_frame_avg": manifest.get("points_per_frame_avg"),
            "lidar_rate_hz": manifest.get("lidar_rate_hz"),
            "point_rate_hz": manifest.get("point_rate_hz"),
            "claim": manifest.get("claim"),
        },
        "livox_frame_sample": livox_summary,
        "fastlio_dataset_sample": fastlio_summary,
        "implementation_support": {
            "spark_fast_lio": spark_support,
        },
        "findings": findings,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# FAST-LIO Input Contract Check",
        "",
        f"- status: `{report['status']}`",
        f"- dense_lidar_ready: `{report['dense_lidar_ready']}`",
        f"- errors: `{report['error_count']}`",
        f"- warnings: `{report['warning_count']}`",
        "",
        "## Config",
        "",
        f"- path: `{report['paths']['config']}`",
        f"- lidar_type: `{report['config']['preprocess'].get('lidar_type')}`",
        f"- scan_line: `{report['config']['preprocess'].get('scan_line')}`",
        f"- scan_rate: `{report['config']['preprocess'].get('scan_rate')}`",
        f"- lidar topic: `{report['config']['common'].get('lid_topic')}`",
        f"- imu topic: `{report['config']['common'].get('imu_topic')}`",
        "",
        "## FAST-LIO Implementation Support",
        "",
        f"- spark-fast-lio root: `{report['implementation_support']['spark_fast_lio']['root']}`",
        f"- PointCloud2 supported lidar types: `{report['implementation_support']['spark_fast_lio']['pointcloud2_supported_lidar_types']}`",
        f"- PointCloud2 Livox supported: `{report['implementation_support']['spark_fast_lio']['pointcloud2_livox_supported']}`",
        f"- Livox CustomMsg path guarded: `{report['implementation_support']['spark_fast_lio']['livox_custommsg_guarded']}`",
        "",
        "## Dense LiDAR Sample",
        "",
        f"- avg points/frame: `{report['livox_frame_sample']['points_per_frame_avg']}`",
        f"- observed lines: `{report['livox_frame_sample']['observed_lines']}`",
        f"- attributes: `{report['livox_frame_sample']['point_attribute_keys']}`",
        "",
        "## Findings",
        "",
    ]
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['severity'].upper()} - {finding['surface']}",
                "",
                finding["detail"],
                "",
                f"Action: {finding['action']}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-dir", default=str(DEFAULT_SCENE_DIR))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default="")
    parser.add_argument("--livox-frames", default="")
    parser.add_argument("--fastlio-dataset", default="")
    parser.add_argument("--sample-frames", type=int, default=5)
    parser.add_argument("--min-dense-points", type=int, default=15000)
    parser.add_argument("--min-fastlio-points", type=int, default=15000)
    parser.add_argument("--spark-fastlio-root", default=str(DEFAULT_SPARK_FASTLIO_ROOT))
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--strict", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = evaluate(args)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_json:
        output_json = project_path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if args.output_md:
        write_markdown(project_path(args.output_md), report)
    if args.strict and report["status"] != "claimable_input_ready":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
