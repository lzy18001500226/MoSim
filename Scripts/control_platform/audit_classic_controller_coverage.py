#!/usr/bin/env python3
"""Audit canonical classic-controller registry and final-matrix coverage."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "Config/control_platform/control_module_registry.json"
DEFAULT_MATRIX = (
    ROOT
    / "Results/control_platform/classic_controller_closeout_20260717"
    / "CLASSIC_CONTROLLER_FINAL_MATRIX.json"
)


@dataclass(frozen=True)
class CanonicalController:
    module_id: str
    family: str
    expected_kind: str
    addition: bool = False


CANONICAL_CONTROLLERS = (
    CanonicalController("lqr_baseline", "linear_optimal", "nominal_controller"),
    CanonicalController("lqi_baseline", "linear_optimal_integral", "nominal_controller"),
    CanonicalController("lqg", "linear_quadratic_gaussian", "nominal_controller"),
    CanonicalController("hinf_hover_wrench", "h_infinity", "nominal_controller"),
    CanonicalController("mu_synthesis", "mu_synthesis", "nominal_controller"),
    CanonicalController("so3_attitude", "so3_geometric", "attitude_rate_inner"),
    CanonicalController("backstepping_baseline", "backstepping", "nominal_controller"),
    CanonicalController("feedback_linearization", "feedback_linearization", "nominal_controller"),
    CanonicalController("adaptive_backstepping", "adaptive_backstepping", "nominal_controller"),
    CanonicalController("dfbc_high_order_attitude", "differential_flatness_high_order", "nominal_controller"),
    CanonicalController("dfbc_high_order_bodyrate", "differential_flatness_high_order", "nominal_controller"),
    CanonicalController("dfbc_smooth_robust_attitude", "differential_flatness_smooth_robust", "nominal_controller"),
    CanonicalController("dfbc_smooth_robust_bodyrate", "differential_flatness_smooth_robust", "nominal_controller"),
    CanonicalController("l1_awff_minimal", "l1_awff", "augmentation"),
    CanonicalController("dfbc_dob_eso_disabled", "dob_eso", "augmentation"),
    CanonicalController("dfbc_dob_eso", "dob_eso", "augmentation"),
    CanonicalController("neural_smc", "sliding_mode_neural", "nominal_controller"),
    CanonicalController("pole_placement_luenberger", "pole_placement_observer", "nominal_controller", True),
    CanonicalController("mrac", "model_reference_adaptive_control", "nominal_controller", True),
    CanonicalController("ndi", "nonlinear_dynamic_inversion", "nominal_controller", True),
    CanonicalController("fopid", "fractional_order_pid", "nominal_controller", True),
    CanonicalController("h2_state_feedback", "h2_optimal", "nominal_controller", True),
)


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def duplicates(values: list[str]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})


def evidence_paths(module: dict[str, Any]) -> list[str]:
    return [
        str(value)
        for key, value in module.items()
        if key.startswith("latest_") and key.endswith("_evidence") and value
    ]


def build_audit(registry: dict[str, Any], matrix: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    modules = registry.get("modules", [])
    rows = matrix.get("rows", [])
    if not isinstance(modules, list) or not isinstance(rows, list):
        raise ValueError("registry.modules and matrix.rows must be arrays")

    module_ids = [str(module.get("module_id", "")) for module in modules]
    matrix_ids = [str(row.get("controller", "")) for row in rows]
    by_module = {str(module.get("module_id", "")): module for module in modules}
    findings: list[dict[str, str]] = []
    coverage: list[dict[str, Any]] = []

    for expected in CANONICAL_CONTROLLERS:
        module = by_module.get(expected.module_id)
        in_matrix = expected.module_id in matrix_ids
        item: dict[str, Any] = {
            "module_id": expected.module_id,
            "family": expected.family,
            "expected_kind": expected.expected_kind,
            "new_addition": expected.addition,
            "registered": module is not None,
            "in_final_matrix": in_matrix,
        }
        if module is None:
            findings.append({"code": "missing_registry", "module_id": expected.module_id})
        else:
            item["status"] = module.get("status", "")
            item["selectable"] = bool(module.get("selectable", False))
            item["claim_ceiling"] = module.get("claim_ceiling", "")
            if module.get("family") != expected.family:
                findings.append({"code": "family_mismatch", "module_id": expected.module_id})
            if module.get("kind") != expected.expected_kind:
                findings.append({"code": "kind_mismatch", "module_id": expected.module_id})
            paths = evidence_paths(module)
            item["declared_evidence_paths"] = paths
            item["existing_evidence_paths"] = [path for path in paths if (root / path).exists()]
            if module.get("status") in {"accepted", "implemented"} and not paths:
                findings.append({"code": "missing_declared_evidence", "module_id": expected.module_id})
            for path in paths:
                if not (root / path).exists():
                    findings.append({"code": "missing_evidence_path", "module_id": expected.module_id, "path": path})
        if not in_matrix:
            findings.append({"code": "missing_final_matrix_row", "module_id": expected.module_id})
        coverage.append(item)

    for module_id in duplicates(module_ids):
        findings.append({"code": "duplicate_registry_id", "module_id": module_id})
    for module_id in duplicates(matrix_ids):
        findings.append({"code": "duplicate_matrix_id", "module_id": module_id})

    counts = {
        "canonical": len(CANONICAL_CONTROLLERS),
        "registered": sum(item["registered"] for item in coverage),
        "in_final_matrix": sum(item["in_final_matrix"] for item in coverage),
        "new_additions_registered": sum(item["registered"] for item in coverage if item["new_addition"]),
        "findings": len(findings),
    }
    return {
        "schema": "mosim.classic_controller_coverage_audit.v1",
        "status": "passed" if not findings else "blocked",
        "counts": counts,
        "coverage": coverage,
        "findings": findings,
        "claim_boundary": "Coverage audit only; no implementation, MWORKS, generated-C, SIL or Gazebo acceptance claim.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_audit(read_json(args.registry), read_json(args.matrix))
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
