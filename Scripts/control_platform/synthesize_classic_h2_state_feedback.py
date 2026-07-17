#!/usr/bin/env python3
"""Reproduce the frozen hover H2 state-feedback gains used by the classic core."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.linalg import solve_continuous_are


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    ROOT / "Results/control_platform/classic_controller_closeout_20260717"
    / "h2_synthesis/H2_STATE_FEEDBACK_SYNTHESIS.json"
)
AXES = {
    "x": {"q_position": 54.76, "q_velocity": 9.21, "r_control": 1.0, "frozen_gain": [7.4, 4.9]},
    "y": {"q_position": 54.76, "q_velocity": 9.21, "r_control": 1.0, "frozen_gain": [7.4, 4.9]},
    "z": {"q_position": 28.09, "q_velocity": 7.04, "r_control": 1.0, "frozen_gain": [5.3, 4.2]},
}


def synthesize_axis(spec: dict[str, float | list[float]]) -> dict[str, object]:
    a = np.array([[0.0, 1.0], [0.0, 0.0]])
    b1 = np.eye(2)
    b2 = np.array([[0.0], [1.0]])
    q = np.diag([float(spec["q_position"]), float(spec["q_velocity"])])
    r = np.array([[float(spec["r_control"])]])
    c1 = np.vstack((np.diag(np.sqrt(np.diag(q))), np.zeros((1, 2))))
    d12 = np.array([[0.0], [0.0], [np.sqrt(r[0, 0])]])
    x = solve_continuous_are(a, b2, q, r)
    gain = np.linalg.solve(r, b2.T @ x)
    closed_loop = a - b2 @ gain
    residual = a.T @ x + x @ a - x @ b2 @ np.linalg.solve(r, b2.T) @ x + q
    frozen = np.array(spec["frozen_gain"], dtype=float)
    return {
        "generalized_plant": {
            "A": a.tolist(), "B1": b1.tolist(), "B2": b2.tolist(),
            "C1": c1.tolist(), "D12": d12.tolist(),
            "state": ["position_error", "velocity_error"],
            "control": "virtual_acceleration_correction",
            "disturbance": ["position_state_disturbance", "velocity_state_disturbance"],
            "performance_output": ["weighted_position_error", "weighted_velocity_error", "weighted_control"],
        },
        "Q": q.tolist(), "R": r.tolist(), "care_solution": x.tolist(),
        "synthesized_gain": gain.ravel().tolist(),
        "frozen_gain": frozen.tolist(),
        "gain_max_abs_difference": float(np.max(np.abs(gain.ravel() - frozen))),
        "care_residual_max_abs": float(np.max(np.abs(residual))),
        "closed_loop_eigenvalues": [
            {"real": float(value.real), "imag": float(value.imag)}
            for value in np.linalg.eigvals(closed_loop)
        ],
        "stable": bool(np.all(np.real(np.linalg.eigvals(closed_loop)) < 0.0)),
    }


def build_report(tolerance: float = 1.0e-10) -> dict[str, object]:
    axes = {name: synthesize_axis(spec) for name, spec in AXES.items()}
    passed = all(
        axis["stable"]
        and axis["gain_max_abs_difference"] <= tolerance
        and axis["care_residual_max_abs"] <= tolerance
        for axis in axes.values()
    )
    return {
        "schema": "mosim.classic_controller.h2_state_feedback_synthesis.v1",
        "status": "passed" if passed else "failed",
        "method": "continuous_time_full_state_H2_via_CARE",
        "interpretation": "For z=[Q^(1/2)x;R^(1/2)u] and full-state feedback, the H2-optimal gain is the CARE state-feedback gain.",
        "axes": axes,
        "tolerance": tolerance,
        "claim_boundary": "Reproducible generalized-plant synthesis and frozen-gain provenance only; not MWORKS, SIL, Gazebo, or performance acceptance.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
