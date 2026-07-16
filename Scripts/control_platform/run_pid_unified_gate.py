#!/usr/bin/env python3
"""Compile and exercise the deterministic PID/Cascade PID C core."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "Scripts" / "control_platform"


def emit(report: dict, output_json: Path | None) -> int:
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if output_json is not None:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] in {"passed", "toolchain_blocked"} else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    compiler = shutil.which("gcc")
    required_sources = [CORE / "pid_unified_core.h", CORE / "pid_unified_core.c"]
    if not compiler:
        return emit({
            "status": "toolchain_blocked",
            "scope": "pid_unified_c_core_compile_and_golden_vector",
            "source_contract": "present" if all(path.is_file() for path in required_sources) else "missing",
            "blocker": "gcc is not available on the current Windows PATH",
            "runtime_claim": "none",
            "next_gate": "compile_and_execute_the_same_golden_vector_in_an_authorized_c_toolchain",
        }, args.output_json)
    with tempfile.TemporaryDirectory(prefix="mosim_pid_gate_") as temp:
        temp_path = Path(temp)
        runner = temp_path / "runner.c"
        binary = temp_path / "runner.exe"
        runner.write_text(
            '#include "pid_unified_core.h"\n'
            '#include <stdio.h>\n'
            'int main(void) {\n'
            '  MosimPidConfig c; MosimPidState s = {0}; MosimPidInput i = {0}; MosimPidOutput o;\n'
            '  mosim_pid_default_config(&c); c.kp=1.2; c.ki=0.8; c.kd=0.1; c.feedforward_gain=0.2;\n'
            '  c.output_min=-1.0; c.output_max=1.0; c.integral_min=-0.5; c.integral_max=0.5;\n'
            '  c.anti_windup_gain=0.4; c.derivative_filter_tau=0.05; c.schedule_gain=0.2;\n'
            '  c.fuzzy_gain=0.1; c.neural_gain=0.05; c.neural_residual_limit=0.2;\n'
            '  i.setpoint=0.8; i.measurement=0.1; i.feedforward=0.3; i.schedule=0.5;\n'
            '  i.fuzzy_error=0.4; i.neural_residual=0.1; i.dt=0.02; i.reset=1; i.enable=1;\n'
            '  if (mosim_pid_step(&c,&s,&i,&o)!=0) return 2;\n'
            '  printf("%.17g %.17g %.17g %.17g %d\\n",o.command,o.unsaturated_command,o.integral,o.scheduled_gain,o.saturated);\n'
            '  return 0; }\n', encoding="ascii"
        )
        compile_cmd = [compiler, "-std=c99", "-O2", "-I", str(CORE),
                       str(runner), str(CORE / "pid_unified_core.c"), "-lm", "-o", str(binary)]
        compiled = subprocess.run(compile_cmd, cwd=ROOT, capture_output=True, text=True)
        if compiled.returncode != 0:
            return emit({"status": "failed", "stage": "compile", "stderr": compiled.stderr}, args.output_json)
        executed = subprocess.run([str(binary)], cwd=ROOT, capture_output=True, text=True)
        if executed.returncode != 0:
            return emit({"status": "failed", "stage": "run", "stderr": executed.stderr}, args.output_json)
        values = executed.stdout.strip().split()
        if len(values) != 5:
            return emit({"status": "failed", "stage": "golden_vector", "stdout": executed.stdout}, args.output_json)
        command, unsaturated, integral, gain = map(float, values[:4])
        saturated = int(values[4])
        passed = (
            abs(command - 1.0) < 1e-12
            and unsaturated > command
            and -0.5 <= integral <= 0.5
            and 1.0 < gain < 1.2
            and saturated == 1
        )
        report = {
            "status": "passed" if passed else "failed",
            "scope": "deterministic_pid_core_and_cascade_contract",
            "runtime_claim": "none",
            "command": command,
            "unsaturated_command": unsaturated,
            "integral": integral,
            "scheduled_gain": gain,
            "saturated": saturated,
        }
        return emit(report, args.output_json)


if __name__ == "__main__":
    raise SystemExit(main())
