#!/usr/bin/env python3
"""Run generated MWORKS position outer-loop C code on a PX4/Gazebo trace.

This checker is intentionally shadow-only. It validates that the exported
position outer-loop interface produces finite, bounded pitch/roll/thrust
commands from the same tracking-error inputs used by the PX4-native gate.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics
import subprocess
import tempfile
from datetime import datetime, timezone


def read_jsonl(path: pathlib.Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def parse_wall_time(value: str | None) -> float:
    if not value:
        return math.nan
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return math.nan


def ned_to_enu(row: dict) -> dict:
    return {
        "wall_ts_s": parse_wall_time(row.get("recorded_wall_time_utc")),
        "x_east": float(row.get("y", math.nan)),
        "y_north": float(row.get("x", math.nan)),
        "z_up": -float(row.get("z", math.nan)),
        "valid": bool(row.get("xy_valid")) and bool(row.get("z_valid")),
    }


def nearest_by_time(rows: list[dict], times: list[float], target: float, start_index: int) -> tuple[dict | None, int, float]:
    import bisect

    if not rows:
        return None, start_index, math.nan
    insert_at = bisect.bisect_left(times, target, lo=max(0, start_index - 4))
    candidates: list[tuple[float, int]] = []
    for idx in (insert_at - 1, insert_at, insert_at + 1):
        if 0 <= idx < len(rows):
            candidates.append((abs(times[idx] - target), idx))
    if not candidates:
        return None, start_index, math.nan
    best_dt, best_idx = min(candidates, key=lambda item: item[0])
    return rows[best_idx], best_idx, best_dt


def build_samples(result_dir: pathlib.Path, phase: str) -> list[dict]:
    setpoints = read_jsonl(result_dir / "planner_setpoint_trace.jsonl")
    positions = [ned_to_enu(row) for row in read_jsonl(result_dir / "vehicle_local_position.jsonl")]
    setpoints = [row for row in setpoints if row.get("phase") == phase and math.isfinite(parse_wall_time(row.get("wall_time_utc")))]
    positions = [row for row in positions if row["valid"] and math.isfinite(row["wall_ts_s"])]
    position_times = [row["wall_ts_s"] for row in positions]

    samples: list[dict] = []
    cursor = 0
    for sp in setpoints:
        target_ts = parse_wall_time(sp.get("wall_time_utc"))
        pos, cursor, dt = nearest_by_time(positions, position_times, target_ts, cursor)
        if pos is None or dt > 0.30:
            continue
        ref = sp.get("position_m") or [math.nan, math.nan, math.nan]
        vel = sp.get("velocity_mps") or [0.0, 0.0, 0.0]
        samples.append(
            {
                "sequence": int(sp.get("sequence", len(samples))),
                "elapsed_s": float(sp.get("elapsed_s", len(samples) * 0.01)),
                "x_error": float(ref[0]) - pos["x_east"],
                "y_error": float(ref[1]) - pos["y_north"],
                "z_error": float(ref[2]) - pos["z_up"],
                "z_ref_rate": float(vel[2]),
                "alignment_dt_s": dt,
            }
        )
    return samples


def write_samples_csv(samples: list[dict], path: pathlib.Path) -> None:
    fields = ("sequence", "elapsed_s", "x_error", "y_error", "z_error", "z_ref_rate")
    path.write_text(
        ",".join(fields)
        + "\n"
        + "\n".join(",".join(str(row[field]) for field in fields) for row in samples)
        + "\n",
        encoding="utf-8",
    )


def run_generated_code(code_dir: pathlib.Path, samples_csv: pathlib.Path, out_jsonl: pathlib.Path) -> tuple[str, str]:
    with tempfile.TemporaryDirectory(prefix="mosim_position_outer_shadow_") as tmp:
        work_dir = pathlib.Path(tmp)
        harness_c = work_dir / "position_outer_loop_shadow_harness.c"
        harness_c.write_text(
            r'''
#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "AWFF_PositionOuterLoop_Sysblock.h"
#include "AWFF_PositionOuterLoop_Sysblock_private.h"

static int all_finite(double a, double b, double c) {
  return isfinite(a) && isfinite(b) && isfinite(c);
}

int main(int argc, char **argv) {
  if (argc != 3) {
    fprintf(stderr, "usage: %s samples.csv output.jsonl\n", argv[0]);
    return 2;
  }
  FILE *input = fopen(argv[1], "r");
  if (!input) {
    fprintf(stderr, "failed to open input: %s\n", strerror(errno));
    return 2;
  }
  FILE *output = fopen(argv[2], "w");
  if (!output) {
    fprintf(stderr, "failed to open output: %s\n", strerror(errno));
    fclose(input);
    return 2;
  }

  Init();
  char line[512];
  if (!fgets(line, sizeof(line), input)) {
    fclose(input);
    fclose(output);
    return 2;
  }

  while (fgets(line, sizeof(line), input)) {
    unsigned long sequence = 0;
    double elapsed_s = 0.0, x_error = 0.0, y_error = 0.0, z_error = 0.0, z_ref_rate = 0.0;
    int parsed = sscanf(line, "%lu,%lf,%lf,%lf,%lf,%lf", &sequence, &elapsed_s, &x_error, &y_error, &z_error, &z_ref_rate);
    if (parsed != 6) {
      continue;
    }

    lockGbIn.x_error = x_error;
    lockGbIn.y_error = y_error;
    lockGbIn.z_error = z_error;
    lockGbIn.z_ref_rate = z_ref_rate;
    Step();

    fprintf(
      output,
      "{\"sequence\":%lu,\"elapsed_s\":%.9f,\"input\":{\"x_error\":%.9f,\"y_error\":%.9f,\"z_error\":%.9f,\"z_ref_rate\":%.9f},\"output\":{\"pitch_ref\":%.9f,\"roll_ref\":%.9f,\"thrust_ref\":%.9f},\"finite\":%s}\n",
      sequence,
      elapsed_s,
      x_error,
      y_error,
      z_error,
      z_ref_rate,
      (double)blockGbOut.pitch_ref,
      (double)blockGbOut.roll_ref,
      (double)blockGbOut.thrust_ref,
      all_finite(blockGbOut.pitch_ref, blockGbOut.roll_ref, blockGbOut.thrust_ref) ? "true" : "false");
  }
  fclose(input);
  fclose(output);
  return 0;
}
''',
            encoding="utf-8",
        )
        executable = work_dir / "position_outer_loop_shadow_harness"
        command = [
            "gcc",
            "-std=c99",
            "-O2",
            "-Wall",
            "-Wextra",
            "-I",
            str(code_dir),
            str(harness_c),
            str(code_dir / "AWFF_PositionOuterLoop_Sysblock.c"),
            str(code_dir / "AWFF_PositionOuterLoop_Sysblock_data.c"),
            "-lm",
            "-o",
            str(executable),
        ]
        build = subprocess.run(command, cwd=work_dir, text=True, capture_output=True)
        if build.returncode != 0:
            return "failed", (build.stdout or "") + "\n" + (build.stderr or "")
        run = subprocess.run([str(executable), str(samples_csv), str(out_jsonl)], cwd=work_dir, text=True, capture_output=True)
        if run.returncode != 0:
            return "failed", (run.stdout or "") + "\n" + (run.stderr or "")
    return "passed", ""


def summarize_vectors(rows: list[dict]) -> dict:
    vectors = [
        [float(row["output"][field]) for field in ("pitch_ref", "roll_ref", "thrust_ref")]
        for row in rows
        if row.get("finite")
    ]
    flat = [value for vector in vectors for value in vector]
    max_step_delta = 0.0
    for prev, cur in zip(vectors, vectors[1:]):
        max_step_delta = max(max_step_delta, max(abs(a - b) for a, b in zip(prev, cur)))

    def axis(index: int) -> dict:
        values = [vector[index] for vector in vectors]
        return {
            "min": min(values) if values else math.nan,
            "max": max(values) if values else math.nan,
            "mean": statistics.fmean(values) if values else math.nan,
        }

    return {
        "finite_vectors": len(vectors),
        "max_abs_output": max((abs(value) for value in flat), default=math.nan),
        "max_step_output_delta": max_step_delta,
        "pitch_ref": axis(0),
        "roll_ref": axis(1),
        "thrust_ref": axis(2),
    }


def compare_reference(outputs: list[dict], reference_jsonl: pathlib.Path | None) -> dict:
    if not reference_jsonl:
        return {"enabled": False}
    refs = read_jsonl(reference_jsonl)
    ref_by_sequence = {int(row["sequence"]): row.get("position_loop", {}) for row in refs if "sequence" in row}
    errors: list[float] = []
    matched = 0
    for row in outputs:
        seq = int(row.get("sequence", -1))
        ref = ref_by_sequence.get(seq)
        if not ref:
            continue
        matched += 1
        for field in ("pitch_ref", "roll_ref", "thrust_ref"):
            errors.append(abs(float(row["output"][field]) - float(ref[field])))
    return {
        "enabled": True,
        "reference_jsonl": str(reference_jsonl),
        "matched_sequences": matched,
        "max_abs_error": max(errors, default=math.nan),
        "mean_abs_error": statistics.fmean(errors) if errors else math.nan,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True, type=pathlib.Path)
    parser.add_argument("--code-dir", required=True, type=pathlib.Path)
    parser.add_argument("--json-out", required=True, type=pathlib.Path)
    parser.add_argument("--phase", default="figure8")
    parser.add_argument("--reference-jsonl", type=pathlib.Path)
    parser.add_argument("--max-abs-output", type=float, default=1.0)
    parser.add_argument("--max-step-output-delta", type=float, default=1.0)
    parser.add_argument("--max-reference-error", type=float, default=1e-5)
    args = parser.parse_args()

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    samples = build_samples(args.result_dir, args.phase)
    samples_csv = args.json_out.parent / "position_outer_loop_shadow_inputs.csv"
    outputs_jsonl = args.json_out.parent / "position_outer_loop_shadow_outputs.jsonl"
    write_samples_csv(samples, samples_csv)

    compile_status, compile_error = run_generated_code(args.code_dir, samples_csv, outputs_jsonl)
    outputs = read_jsonl(outputs_jsonl)
    output_summary = summarize_vectors(outputs)
    reference_compare = compare_reference(outputs, args.reference_jsonl)

    checks = {
        "has_shadow_samples": len(samples) >= 100,
        "compile_and_run_passed": compile_status == "passed",
        "all_outputs_finite": output_summary["finite_vectors"] == len(samples) and len(samples) > 0,
        "output_bounded": math.isfinite(output_summary["max_abs_output"]) and output_summary["max_abs_output"] <= args.max_abs_output,
        "output_continuity_ok": math.isfinite(output_summary["max_step_output_delta"]) and output_summary["max_step_output_delta"] <= args.max_step_output_delta,
        "reference_compare_ok": (
            not reference_compare.get("enabled")
            or (
                reference_compare.get("matched_sequences", 0) >= 100
                and math.isfinite(reference_compare.get("max_abs_error", math.nan))
                and reference_compare["max_abs_error"] <= args.max_reference_error
            )
        ),
    }
    passed = all(checks.values())
    payload = {
        "schema": "mosim.mworks_position_outer_loop_codegen_px4_shadow_gate.v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed_position_outer_loop_shadow" if passed else "failed_metrics",
        "semantic_boundary": "shadow_only_no_px4_setpoint_or_gazebo_actuator_publication",
        "source_px4_result_dir": str(args.result_dir),
        "generated_code_dir": str(args.code_dir),
        "phase": args.phase,
        "counts": {
            "matched_shadow_inputs": len(samples),
            "shadow_outputs": len(outputs),
        },
        "compile_status": compile_status,
        "compile_error_tail": compile_error[-2000:],
        "metrics": {
            **output_summary,
            "alignment_dt_max_s": max((row["alignment_dt_s"] for row in samples), default=math.nan),
        },
        "reference_compare": reference_compare,
        "checks": checks,
        "integration_decision": {
            "position_loop_pitch_roll_thrust": "candidate_for_attitude_thrust_offboard_or_px4_module_gate" if passed else "not_ready",
            "not_for_trajectory_setpoint": True,
        },
        "claim_boundary": [
            "This gate executes generated MWORKS position outer-loop C code against PX4/Gazebo trace inputs.",
            "It is shadow-only: it does not publish PX4 Offboard setpoints and does not write Gazebo actuator topics.",
            "Passing this gate supports attitude/thrust Offboard or PX4 module integration design only; it is not deployed controller performance.",
        ],
        "files": {
            "shadow_inputs_csv": str(samples_csv),
            "shadow_outputs_jsonl": str(outputs_jsonl),
        },
    }
    args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
