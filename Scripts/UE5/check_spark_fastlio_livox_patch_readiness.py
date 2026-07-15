#!/usr/bin/env python3
"""Check whether the local spark-fast-lio ROS2 candidate is Mid360-ready.

This is a static gate for the currently staged third-party candidate under
Results/tmp. It deliberately does not claim runtime localization. The only
claim is whether the source tree is internally consistent enough to build and
run the Livox CustomMsg path for MoSim Mid360-style input.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATE = ROOT / "Results/tmp/fastlio_ros2_candidates/spark-fast-lio/spark_fast_lio"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"


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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def check(candidate: Path) -> dict[str, Any]:
    files = {
        "cmake": candidate / "CMakeLists.txt",
        "package": candidate / "package.xml",
        "preprocess_h": candidate / "include/preprocess.h",
        "preprocess_cpp": candidate / "src/preprocess.cpp",
        "spark_h": candidate / "include/spark_fast_lio.h",
        "spark_cpp": candidate / "src/spark_fast_lio.cpp",
    }
    texts = {name: read_text(path) for name, path in files.items()}
    all_text = "\n".join(texts.values())

    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, why: str, evidence: list[str] | None = None) -> None:
        checks.append(
            {
                "name": name,
                "passed": bool(passed),
                "why": why,
                "evidence": evidence or [],
            }
        )

    add(
        "candidate_tree_exists",
        candidate.exists(),
        "spark-fast-lio candidate source tree must exist under the ignored Results/tmp workspace.",
        [rel(candidate)],
    )
    add(
        "uses_ros2_livox_driver2_package",
        "find_package(livox_ros_driver2" in texts["cmake"] or "livox_ros_driver2" in texts["package"],
        "ROS2 Humble Mid360 route should use livox_ros_driver2 package naming, not ROS1 livox_ros_driver.",
        [rel(files["cmake"]), rel(files["package"])],
    )
    add(
        "does_not_find_ros1_livox_driver",
        "find_package(livox_ros_driver QUIET)" not in texts["cmake"]
        and "find_package(livox_ros_driver REQUIRED)" not in texts["cmake"],
        "CMake must not gate the ROS2 CustomMsg path on ROS1 livox_ros_driver.",
        [rel(files["cmake"])],
    )
    add(
        "preprocess_uses_ros2_custommsg_header",
        "livox_ros_driver2/msg/custom_msg.hpp" in texts["preprocess_h"],
        "Preprocess header must include ROS2 livox_ros_driver2/msg/custom_msg.hpp.",
        [rel(files["preprocess_h"])],
    )
    add(
        "preprocess_drops_ros1_custommsg_header",
        "livox_ros_driver/CustomMsg.h" not in texts["preprocess_h"],
        "Preprocess header must not include ROS1 livox_ros_driver/CustomMsg.h in a ROS2 candidate.",
        [rel(files["preprocess_h"])],
    )
    add(
        "preprocess_signature_is_ros2_custommsg",
        "livox_ros_driver2::msg::CustomMsg" in texts["preprocess_h"]
        and "livox_ros_driver2::msg::CustomMsg" in texts["preprocess_cpp"],
        "Preprocess process()/avia_handler() overloads must accept livox_ros_driver2::msg::CustomMsg.",
        [rel(files["preprocess_h"]), rel(files["preprocess_cpp"])],
    )
    add(
        "livox_macro_consistent",
        "LIVOXROS_DRIVER_FOUND" not in all_text and "LIVOX_ROS_DRIVER_FOUND" in all_text,
        "The candidate currently has a typo-prone macro path; all guards should consistently use LIVOX_ROS_DRIVER_FOUND.",
        [rel(files["spark_cpp"]), rel(files["cmake"])],
    )
    add(
        "livox_callback_binding_consistent",
        "livoxLiDARCallback" in texts["spark_h"]
        and "SPARKFastLIO2::livoxLiDARCallback" in texts["spark_cpp"]
        and "livoxLidarCallback" not in texts["spark_cpp"],
        "Subscriber binding must match the declared livoxLiDARCallback symbol exactly.",
        [rel(files["spark_h"]), rel(files["spark_cpp"])],
    )
    add(
        "livox_callback_uses_member_imu_buffer",
        "imu_buffer.empty()" not in texts["spark_cpp"] and "imu_buffer_" in texts["spark_cpp"],
        "Livox callback must use the class member imu_buffer_, not an undeclared imu_buffer.",
        [rel(files["spark_cpp"])],
    )
    add(
        "livox_callback_uses_nanoseconds",
        "nanseconds()" not in texts["spark_cpp"] and "nanoseconds()" in texts["spark_cpp"],
        "rclcpp::Time exposes nanoseconds(); the typo nanseconds() blocks the CustomMsg path.",
        [rel(files["spark_cpp"])],
    )
    add(
        "pointcloud2_path_not_used_as_mid360_claim",
        "case AVIA:" in texts["preprocess_cpp"] or "livox_ros_driver2::msg::CustomMsg" in texts["preprocess_cpp"],
        "Mid360 evidence must go through a Livox-aware path, not only Ouster/Kimera/Velodyne PointCloud2 cases.",
        [rel(files["preprocess_cpp"])],
    )
    add(
        "mosim_startup_diagnostics_not_duplicated",
        texts["spark_cpp"].count("MoSim startup params:") == 1,
        "The generated startup diagnostics block must be idempotent; repeated patch runs must not duplicate it.",
        [rel(files["spark_cpp"])],
    )
    add(
        "mosim_runtime_diagnostics_not_duplicated",
        texts["spark_cpp"].count("Process LiDAR/IMU:") == 1
        and texts["preprocess_cpp"].count("Livox preprocess:") == 1
        and texts["preprocess_cpp"].count("Livox avia_handler entry:") == 1,
        "Generated runtime diagnostics must be inserted exactly once in the Livox preprocessing path.",
        [rel(files["spark_cpp"]), rel(files["preprocess_cpp"])],
    )

    blockers = [item["name"] for item in checks if not item["passed"]]
    return {
        "schema": "mosim.spark_fastlio_livox_patch_readiness.v1",
        "candidate": rel(candidate),
        "ready": not blockers,
        "blockers": blockers,
        "checks": checks,
        "decision": "ready_for_build_runtime_gate" if not blockers else "patch_required_before_mid360_runtime_claim",
        "next_action": (
            "Build the candidate and run headless MoSim Mid360 truth evaluation."
            if not blockers
            else "Patch ROS2 Livox CustomMsg package/header/signature/macro/callback consistency first."
        ),
        "claim_boundary": [
            "Passing this static gate is not FAST-LIO localization evidence.",
            "Runtime evidence still requires nonzero registered cloud, odometry, path, coherent timestamps, and truth-error metrics.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# spark-fast-lio Livox Patch Readiness",
        "",
        f"- candidate: `{report['candidate']}`",
        f"- ready: `{str(report['ready']).lower()}`",
        f"- decision: `{report['decision']}`",
        f"- next_action: {report['next_action']}",
        "",
        "## Checks",
        "",
        "| Status | Check | Reason |",
        "|---|---|---|",
    ]
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(f"| {status} | `{item['name']}` | {item['why']} |")
    lines.extend(["", "## Claim Boundary", ""])
    for item in report["claim_boundary"]:
        lines.append(f"- {item}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_json(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail if the candidate is not patch-ready")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidate = project_path(args.candidate)
    report = check(candidate)
    if args.write:
        output_root = project_path(args.output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        write_json(output_root / "SPARK_FASTLIO_LIVOX_PATCH_READINESS.json", report)
        write_markdown(output_root / "SPARK_FASTLIO_LIVOX_PATCH_READINESS.md", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.strict and not report["ready"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
