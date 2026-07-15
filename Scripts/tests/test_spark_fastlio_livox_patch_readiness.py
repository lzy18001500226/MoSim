#!/usr/bin/env python3
"""Regression checks for the spark-fast-lio Livox patch-readiness gate."""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts/UE5/check_spark_fastlio_livox_patch_readiness.py"
    spec = importlib.util.spec_from_file_location("check_spark_fastlio_livox_patch_readiness", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_spark_fastlio_livox_patch_readiness"] = module
    spec.loader.exec_module(module)
    return module


def load_patch_module():
    path = ROOT / "Scripts/UE5/patch_spark_fastlio_livox_ros2.py"
    spec = importlib.util.spec_from_file_location("patch_spark_fastlio_livox_ros2", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["patch_spark_fastlio_livox_ros2"] = module
    spec.loader.exec_module(module)
    return module


def test_patched_candidate_is_ready_for_build_gate() -> None:
    patch_module = load_patch_module()
    module = load_module()
    patch_module.patch_candidate(module.DEFAULT_CANDIDATE)
    report = module.check(module.DEFAULT_CANDIDATE)
    if report["schema"] != "mosim.spark_fastlio_livox_patch_readiness.v1":
        raise AssertionError(report)
    if not report["ready"]:
        raise AssertionError(report)
    if report["decision"] != "ready_for_build_runtime_gate":
        raise AssertionError(report)

    expected_checks = {
        "uses_ros2_livox_driver2_package",
        "does_not_find_ros1_livox_driver",
        "preprocess_uses_ros2_custommsg_header",
        "preprocess_drops_ros1_custommsg_header",
        "preprocess_signature_is_ros2_custommsg",
        "livox_macro_consistent",
        "livox_callback_binding_consistent",
        "livox_callback_uses_member_imu_buffer",
        "livox_callback_uses_nanoseconds",
    }
    checks = {item["name"]: item for item in report["checks"]}
    missing = expected_checks.difference(checks)
    if missing:
        raise AssertionError((missing, checks))
    failed = [name for name in expected_checks if not checks[name]["passed"]]
    if failed:
        raise AssertionError((failed, report))

    temp_root = ROOT / "Results/tmp/spark_fastlio_livox_patch_readiness_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        temp_root.mkdir(parents=True)
        md_path = temp_root / "SPARK_FASTLIO_LIVOX_PATCH_READINESS.md"
        json_path = temp_root / "SPARK_FASTLIO_LIVOX_PATCH_READINESS.json"
        module.write_markdown(md_path, report)
        module.write_json(json_path, report)
        text = md_path.read_text(encoding="utf-8")
        for phrase in (
            "ready_for_build_runtime_gate",
            "livox_callback_uses_nanoseconds",
            "Runtime evidence still requires",
        ):
            if phrase not in text:
                raise AssertionError(text)
        if b"\r\n" in md_path.read_bytes() or b"\r\n" in json_path.read_bytes():
            raise AssertionError("readiness outputs must use LF line endings")
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_patched_candidate_is_ready_for_build_gate()
    print("[OK] spark-fast-lio Livox patch-readiness regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
