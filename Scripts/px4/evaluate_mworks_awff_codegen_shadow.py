#!/usr/bin/env python3
"""Run generated MWORKS AWFF C code as a shadow controller on a PX4 flight trace.

This checker does not publish setpoints or actuator commands. It feeds the
generated controller with PX4/Gazebo trajectory tracking errors and records
whether generated outputs are finite, bounded, and continuous enough to be a
candidate for the next PX4 integration level.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import shutil
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
        "heading": float(row.get("heading", math.nan)),
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


def build_shadow_harness(code_dir: pathlib.Path, samples_csv: pathlib.Path, out_jsonl: pathlib.Path, work_dir: pathlib.Path) -> pathlib.Path:
    harness_c = work_dir / "awff_shadow_harness.c"
    harness_c.write_text(
        r'''
#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "AWFF_FullController_Sysblock.h"
#include "AWFF_FullController_Sysblock_private.h"

static int is_finite4(double a, double b, double c, double d) {
  return isfinite(a) && isfinite(b) && isfinite(c) && isfinite(d);
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
  char line[1024];
  if (!fgets(line, sizeof(line), input)) {
    fclose(input);
    fclose(output);
    return 2;
  }

  while (fgets(line, sizeof(line), input)) {
    unsigned long sequence = 0;
    double elapsed_s = 0.0, x_error = 0.0, y_error = 0.0, z_error = 0.0;
    double z_ref_rate = 0.0, roll_mea = 0.0, pitch_mea = 0.0, yaw_mea = 0.0, yaw_ref = 0.0;
    int parsed = sscanf(
        line,
        "%lu,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf",
        &sequence,
        &elapsed_s,
        &x_error,
        &y_error,
        &z_error,
        &z_ref_rate,
        &roll_mea,
        &pitch_mea,
        &yaw_mea,
        &yaw_ref);
    if (parsed != 10) {
      continue;
    }

    GbIn.x_error = x_error;
    GbIn.y_error = y_error;
    GbIn.z_error = z_error;
    GbIn.z_ref_rate = z_ref_rate;
    GbIn.roll_mea = roll_mea;
    GbIn.pitch_mea = pitch_mea;
    GbIn.yaw_mea = yaw_mea;
    GbIn.yaw_ref = yaw_ref;
    Step();

    fprintf(
        output,
        "{\"sequence\":%lu,\"elapsed_s\":%.9f,\"input\":{\"x_error\":%.9f,\"y_error\":%.9f,\"z_error\":%.9f,\"z_ref_rate\":%.9f,\"roll_mea\":%.9f,\"pitch_mea\":%.9f,\"yaw_mea\":%.9f,\"yaw_ref\":%.9f},\"position_loop\":{\"pitch_ref\":%.9f,\"roll_ref\":%.9f,\"thrust_ref\":%.9f},\"output\":{\"y\":%.9f,\"y1\":%.9f,\"y2\":%.9f,\"y3\":%.9f},\"finite\":%s}\n",
        sequence,
        elapsed_s,
        x_error,
        y_error,
        z_error,
        z_ref_rate,
        roll_mea,
        pitch_mea,
        yaw_mea,
        yaw_ref,
        (double)awff_fullcontroller_sysblockGbB.temp,
        (double)awff_fullcontroller_sysblockGbB.temp1,
        (double)awff_fullcontroller_sysblockGbB.temp2,
        (double)kGbOut.y,
        (double)kGbOut.y1,
        (double)kGbOut.y2,
        (double)kGbOut.y3,
        is_finite4(kGbOut.y, kGbOut.y1, kGbOut.y2, kGbOut.y3) ? "true" : "false");
  }
  fclose(input);
  fclose(output);
  return 0;
}
''',
        encoding="utf-8",
    )
    executable = work_dir / "awff_shadow_harness"
    sources = [
        harness_c,
        code_dir / "AWFF_FullController_Sysblock.c",
        code_dir / "AWFF_FullController_Sysblock_data.c",
    ]
    command = [
        "gcc",
        "-std=c99",
        "-O2",
        "-Wall",
        "-Wextra",
        "-I",
        str(code_dir),
        *[str(path) for path in sources],
        "-lm",
        "-o",
        str(executable),
    ]
    subprocess.run(command, cwd=work_dir, check=True, text=True, capture_output=True)
    subprocess.run([str(executable), str(samples_csv), str(out_jsonl)], cwd=work_dir, check=True, text=True, capture_output=True)
    return executable


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True, type=pathlib.Path)
    parser.add_argument("--code-dir", required=True, type=pathlib.Path)
    parser.add_argument("--json-out", required=True, type=pathlib.Path)
    parser.add_argument("--phase", default="figure8")
    parser.add_argument("--max-abs-output", type=float, default=5.0)
    parser.add_argument("--max-step-output-delta", type=float, default=1.0)
    args = parser.parse_args()
    args.result_dir = args.result_dir.resolve()
    args.code_dir = args.code_dir.resolve()
    args.json_out = args.json_out.resolve()

    setpoints = read_jsonl(args.result_dir / "planner_setpoint_trace.jsonl")
    positions = [ned_to_enu(row) for row in read_jsonl(args.result_dir / "vehicle_local_position.jsonl")]
    setpoints = [row for row in setpoints if row.get("phase") == args.phase and math.isfinite(parse_wall_time(row.get("wall_time_utc")))]
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
                "roll_mea": 0.0,
                "pitch_mea": 0.0,
                "yaw_mea": pos["heading"] if math.isfinite(pos["heading"]) else 0.0,
                "yaw_ref": float(sp.get("yaw_rad", 0.0)),
                "alignment_dt_s": dt,
            }
        )

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    shadow_jsonl = args.json_out.parent / "awff_codegen_shadow_outputs.jsonl"
    samples_csv = args.json_out.parent / "awff_codegen_shadow_inputs.csv"
    samples_csv.write_text(
        "sequence,elapsed_s,x_error,y_error,z_error,z_ref_rate,roll_mea,pitch_mea,yaw_mea,yaw_ref\n"
        + "\n".join(
            ",".join(
                str(row[field])
                for field in (
                    "sequence",
                    "elapsed_s",
                    "x_error",
                    "y_error",
                    "z_error",
                    "z_ref_rate",
                    "roll_mea",
                    "pitch_mea",
                    "yaw_mea",
                    "yaw_ref",
                )
            )
            for row in samples
        )
        + "\n",
        encoding="utf-8",
    )

    compile_status = "not_run"
    compile_error = ""
    with tempfile.TemporaryDirectory(prefix="mosim_awff_shadow_") as tmp:
        try:
            build_shadow_harness(args.code_dir, samples_csv, shadow_jsonl, pathlib.Path(tmp))
            compile_status = "passed"
        except subprocess.CalledProcessError as exc:
            compile_status = "failed"
            compile_error = (exc.stdout or "") + "\n" + (exc.stderr or "")

    outputs = read_jsonl(shadow_jsonl)
    output_vectors = [
        [float(row["output"][field]) for field in ("y", "y1", "y2", "y3")]
        for row in outputs
        if row.get("finite")
    ]
    position_loop_vectors = [
        [float(row["position_loop"][field]) for field in ("pitch_ref", "roll_ref", "thrust_ref")]
        for row in outputs
        if row.get("finite") and "position_loop" in row
    ]
    flat_outputs = [value for vector in output_vectors for value in vector]
    flat_position_loop = [value for vector in position_loop_vectors for value in vector]
    max_abs_output = max((abs(value) for value in flat_outputs), default=math.nan)
    max_abs_position_loop = max((abs(value) for value in flat_position_loop), default=math.nan)
    max_step_delta = 0.0
    for prev, cur in zip(output_vectors, output_vectors[1:]):
        max_step_delta = max(max_step_delta, max(abs(a - b) for a, b in zip(prev, cur)))
    max_position_loop_step_delta = 0.0
    for prev, cur in zip(position_loop_vectors, position_loop_vectors[1:]):
        max_position_loop_step_delta = max(max_position_loop_step_delta, max(abs(a - b) for a, b in zip(prev, cur)))

    def min_max_mean(index: int) -> dict:
        vals = [vector[index] for vector in position_loop_vectors]
        return {
            "min": min(vals) if vals else math.nan,
            "max": max(vals) if vals else math.nan,
            "mean": statistics.fmean(vals) if vals else math.nan,
        }

    z_errors = [row["z_error"] for row in samples]
    x_errors = [row["x_error"] for row in samples]
    y_errors = [row["y_error"] for row in samples]
    root_output_directly_usable = math.isfinite(max_abs_output) and max_abs_output <= args.max_abs_output
    position_loop_candidate_ready = (
        len(position_loop_vectors) == len(samples)
        and len(samples) > 0
        and math.isfinite(max_abs_position_loop)
        and max_abs_position_loop <= 1.0
        and math.isfinite(max_position_loop_step_delta)
        and max_position_loop_step_delta <= args.max_step_output_delta
    )
    checks = {
        "has_shadow_samples": len(samples) >= 100,
        "compile_and_run_passed": compile_status == "passed",
        "all_outputs_finite": len(output_vectors) == len(samples) and len(samples) > 0,
        "root_output_direct_l1_usable": root_output_directly_usable,
        "max_step_output_delta_ok": math.isfinite(max_step_delta) and max_step_delta <= args.max_step_output_delta,
        "position_loop_available": len(position_loop_vectors) == len(samples) and len(samples) > 0,
        "position_loop_continuity_ok": math.isfinite(max_position_loop_step_delta) and max_position_loop_step_delta <= args.max_step_output_delta,
        "position_loop_candidate_ready": position_loop_candidate_ready,
    }
    overall_ready = (
        checks["has_shadow_samples"]
        and checks["compile_and_run_passed"]
        and checks["all_outputs_finite"]
        and checks["position_loop_candidate_ready"]
    )
    payload = {
        "schema": "mosim.mworks_awff_codegen_px4_shadow_gate.v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed_position_loop_shadow" if overall_ready else "failed_metrics",
        "semantic_boundary": "shadow_only_no_px4_setpoint_or_gazebo_actuator_publication",
        "source_px4_result_dir": str(args.result_dir),
        "generated_code_dir": str(args.code_dir),
        "phase": args.phase,
        "counts": {
            "setpoints_in_phase": len(setpoints),
            "matched_shadow_inputs": len(samples),
            "shadow_outputs": len(outputs),
        },
        "compile_status": compile_status,
        "compile_error_tail": compile_error[-2000:],
        "metrics": {
            "x_error_rmse_m": math.sqrt(statistics.fmean([v * v for v in x_errors])) if x_errors else math.nan,
            "y_error_rmse_m": math.sqrt(statistics.fmean([v * v for v in y_errors])) if y_errors else math.nan,
            "z_error_rmse_m": math.sqrt(statistics.fmean([v * v for v in z_errors])) if z_errors else math.nan,
            "max_abs_output": max_abs_output,
            "max_step_output_delta": max_step_delta,
            "max_abs_position_loop": max_abs_position_loop,
            "max_position_loop_step_delta": max_position_loop_step_delta,
            "position_loop_pitch_ref": min_max_mean(0),
            "position_loop_roll_ref": min_max_mean(1),
            "position_loop_thrust_ref": min_max_mean(2),
            "alignment_dt_max_s": max((row["alignment_dt_s"] for row in samples), default=math.nan),
        },
        "checks": checks,
        "integration_decision": {
            "root_outports_y_y1_y2_y3": "not_l1_setpoint_ready" if not root_output_directly_usable else "bounded_but_still_motor_mixer_semantics",
            "position_loop_pitch_roll_thrust": "candidate_for_next_export_or_adapter_gate" if position_loop_candidate_ready else "not_ready",
            "recommended_next_step": "export_or_wrap_position_outer_loop_interface_for_px4_adapter_shadow_then_closed_loop",
        },
        "claim_boundary": [
            "This gate executes generated MWORKS C code against PX4/Gazebo trace inputs.",
            "It is shadow-only: it does not publish PX4 Offboard setpoints and does not write Gazebo actuator topics.",
            "Passing this gate supports L1/L2 integration readiness only; it is not deployed controller performance.",
        ],
        "files": {
            "shadow_inputs_csv": str(samples_csv),
            "shadow_outputs_jsonl": str(shadow_jsonl),
        },
    }
    args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"].startswith("passed") else 2


if __name__ == "__main__":
    raise SystemExit(main())
