#!/usr/bin/env python3
"""Validate frozen learning controllers, compiled C inference, and fallback behavior."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "Config/control_platform/learning_control_artifact.json"
CORE_DIR = ROOT / "Scripts/control_platform"


def canonical_json(data: Any) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def python_neural(artifact: dict[str, Any], observation: np.ndarray) -> np.ndarray:
    spec = artifact["neural_residual"]
    weights = spec["weights"]
    normalized = np.clip(observation / np.asarray(artifact["observation"]["scale"]), -1.0, 1.0)
    hidden = np.tanh(normalized @ np.asarray(weights["w1"]) + np.asarray(weights["b1"]))
    output = hidden @ np.asarray(weights["w2"]) + np.asarray(weights["b2"])
    return np.clip(output, -float(spec["output_limit_mps2"]), float(spec["output_limit_mps2"]))


def python_rl(artifact: dict[str, Any], observation: np.ndarray) -> np.ndarray:
    spec = artifact["rl_gain_scheduler"]
    weights = spec["weights"]
    normalized = np.clip(observation / np.asarray(artifact["observation"]["scale"]), -1.0, 1.0)
    hidden1 = np.tanh(normalized @ np.asarray(weights["w1"]) + np.asarray(weights["b1"]))
    hidden2 = np.tanh(hidden1 @ np.asarray(weights["w2"]) + np.asarray(weights["b2"]))
    output = hidden2 @ np.asarray(weights["w3"]) + np.asarray(weights["b3"])
    lower, upper = spec["action_bounds"]
    return np.clip(output, float(lower), float(upper))


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    if len(drive) != 1:
        raise ValueError(f"unsupported Windows path for WSL mapping: {resolved}")
    relative = resolved.as_posix().split(":", 1)[1].lstrip("/")
    return f"/mnt/{drive}/{relative}"


def build_runner(observations: np.ndarray) -> str:
    rows = []
    for index, observation in enumerate(observations):
        values = ", ".join(f"{value:.17g}" for value in observation)
        rows.append(f"    {{{{{values}}}, 1}},")
    return f'''#include "learning_control_core.h"
#include <math.h>
#include <stdio.h>

int main(void)
{{
    MosimLearningInput inputs[{len(observations)}] = {{
{chr(10).join(rows)}
    }};
    MosimLearningOutput output;
    int index;
    for (index = 0; index < {len(observations)}; ++index) {{
        mosim_neural_residual_step(&inputs[index], &output);
        printf("neural,%d,%d,%d,%.17g,%.17g,%.17g\\n", index, output.status_code,
               output.fallback_active, output.values[0], output.values[1], output.values[2]);
        mosim_rl_gain_scheduler_step(&inputs[index], &output);
        printf("rl,%d,%d,%d,%.17g,%.17g,%.17g\\n", index, output.status_code,
               output.fallback_active, output.values[0], output.values[1], output.values[2]);
    }}
    inputs[0].enable = 0;
    mosim_neural_residual_step(&inputs[0], &output);
    printf("disabled,0,%d,%d,%.17g,%.17g,%.17g\\n", output.status_code,
           output.fallback_active, output.values[0], output.values[1], output.values[2]);
    inputs[0].enable = 1;
    inputs[0].values[0] = NAN;
    mosim_rl_gain_scheduler_step(&inputs[0], &output);
    printf("nonfinite,0,%d,%d,%.17g,%.17g,%.17g\\n", output.status_code,
           output.fallback_active, output.values[0], output.values[1], output.values[2]);
    return 0;
}}
'''


def compiled_equivalence(result_dir: Path, artifact: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    rng = np.random.default_rng(20260719)
    observations = rng.uniform(-3.0, 3.0, size=(64, 12))
    build_dir = result_dir / "c_build"
    build_dir.mkdir(parents=True, exist_ok=True)
    runner = build_dir / "learning_control_runner.c"
    runner.write_text(build_runner(observations), encoding="utf-8", newline="\n")
    build_wsl = wsl_path(build_dir)
    core_wsl = wsl_path(CORE_DIR)
    command = (
        f"cd '{build_wsl}' && gcc -std=c99 -O2 -Wall -Wextra "
        f"-I'{core_wsl}' learning_control_runner.c '{core_wsl}/learning_control_core.c' "
        "-lm -o learning_control_runner && ./learning_control_runner"
    )
    completed = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "--", "bash", "-lc", command],
        check=True, capture_output=True, text=True,
    )
    max_error = 0.0
    compared = 0
    fallback_rows: dict[str, dict[str, Any]] = {}
    for line in completed.stdout.splitlines():
        mode, index_text, status_text, fallback_text, *values_text = line.split(",")
        values = np.asarray([float(item) for item in values_text])
        if mode in {"neural", "rl"}:
            index = int(index_text)
            expected = python_neural(artifact, observations[index]) if mode == "neural" else python_rl(artifact, observations[index])
            max_error = max(max_error, float(np.max(np.abs(values - expected))))
            compared += 3
            if int(status_text) != 0 or int(fallback_text) != 0:
                raise RuntimeError(f"unexpected fallback for {mode} row {index}")
        else:
            fallback_rows[mode] = {
                "status_code": int(status_text),
                "fallback_active": bool(int(fallback_text)),
                "values": values.tolist(),
            }
    equivalence = {
        "status": "passed" if max_error <= 1.0e-12 else "blocked",
        "compiled_with": "Ubuntu-20.04 gcc -std=c99 -O2",
        "observation_count": len(observations),
        "scalar_comparisons": compared,
        "max_abs_error": max_error,
    }
    fallback_ok = (
        fallback_rows.get("disabled", {}).get("fallback_active") is True
        and fallback_rows.get("nonfinite", {}).get("fallback_active") is True
        and all(abs(value) <= 1.0e-15 for row in fallback_rows.values() for value in row["values"])
    )
    fallback = {
        "status": "passed" if fallback_ok else "blocked",
        "cases": fallback_rows,
    }
    return equivalence, fallback


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default="Results/control_platform/p9_learning_offline_gate_20260717")
    args = parser.parse_args()
    result_dir = Path(args.result_dir)
    if not result_dir.is_absolute():
        result_dir = ROOT / result_dir
    result_dir.mkdir(parents=True, exist_ok=True)

    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    declared_hash = artifact["artifact_sha256"]
    hash_payload = dict(artifact)
    del hash_payload["artifact_sha256"]
    computed_hash = hashlib.sha256(canonical_json(hash_payload)).hexdigest()
    hash_ok = computed_hash == declared_hash
    equivalence, fallback = compiled_equivalence(result_dir, artifact)
    neural_metrics = artifact["neural_residual"]["metrics"]
    rl_metrics = artifact["rl_gain_scheduler"]["metrics"]
    neural_ab = {
        "status": "passed" if neural_metrics["rmse_improvement_fraction"] > 0.05 else "blocked",
        "baseline_rmse_mps2": neural_metrics["baseline_zero_residual_rmse_mps2"],
        "learned_rmse_mps2": neural_metrics["model_rmse_mps2"],
        "rmse_improvement_fraction": neural_metrics["rmse_improvement_fraction"],
    }
    rl_ab = {
        "status": "passed" if rl_metrics["cost_improvement_fraction"] > 0.02 else "blocked",
        "baseline_mean_cost": rl_metrics["baseline_mean_cost"],
        "learned_mean_cost": rl_metrics["learned_mean_cost"],
        "rmse_improvement_fraction": rl_metrics["cost_improvement_fraction"],
        "cost_improvement_fraction": rl_metrics["cost_improvement_fraction"],
    }
    checks = [hash_ok, equivalence["status"] == "passed", fallback["status"] == "passed",
              neural_ab["status"] == "passed", rl_ab["status"] == "passed"]
    report = {
        "schema": "mosim.learning_control.offline_gate.v1",
        "status": "passed" if all(checks) else "blocked",
        "artifact": str(ARTIFACT.relative_to(ROOT)).replace("\\", "/"),
        "artifact_hash_gate": {
            "status": "passed" if hash_ok else "blocked",
            "declared_sha256": declared_hash,
            "computed_sha256": computed_hash,
        },
        "compiled_c_equivalence": equivalence,
        "fallback_gate": fallback,
        "neural_residual_ab": neural_ab,
        "rl_gain_scheduler_ab": rl_ab,
        "gazebo_runtime_status": "pending_shared_runtime_release",
        "claim_boundary": "Trained frozen policies, compiled C equivalence, fallback, and held-out offline A/B only; no Gazebo/PX4 claim.",
    }
    output = result_dir / "P9_LEARNING_CONTROL_OFFLINE_GATE.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
