#!/usr/bin/env python3
"""Audit the installed Syslab μ-analysis and μ-synthesis execution surface."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LAUNCHER = Path(r"C:\Users\Public\TongYuan\julia-1.10.10\bin\julia-ty.bat")


JULIA_AUDIT = r"""
using TyRobustControl
using Random
Random.seed!(929)
R = randn(5,5) + 1im*randn(5,5)
U = randn(5,2) + 1im*randn(5,2)
V = randn(2,5) + 1im*randn(2,5)
block_structure = [-1 0; -1 0; 1 1; 2 0]
Q, bound = cmsclsyn(R,U,V,block_structure)
println("musyn=" * string(isdefined(TyRobustControl, :musyn)))
println("MuSynthesis=" * string(isdefined(TyRobustControl, :MuSynthesis)))
println("cmsclsyn=" * string(isdefined(TyRobustControl, :cmsclsyn)))
println("mussv=" * string(isdefined(TyRobustControl, :mussv)))
println("bound=" * repr(bound))
println("q_rows=" * string(size(Q, 1)))
println("q_cols=" * string(size(Q, 2)))
"""


def parse_output(stdout: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in stdout.splitlines():
        if "=" in line:
            key, value = line.strip().split("=", 1)
            if key in {"musyn", "MuSynthesis", "cmsclsyn", "mussv", "bound", "q_rows", "q_cols"}:
                values[key] = value
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--launcher", type=Path, default=DEFAULT_LAUNCHER)
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=ROOT / "Results/control_platform/p2_mu_syslab_capability_20260716",
    )
    args = parser.parse_args()
    result_dir = args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    audit_file = result_dir / "syslab_mu_capability_audit.jl"
    audit_file.write_text(JULIA_AUDIT.strip() + "\n", encoding="utf-8")
    audit_expression = "; ".join(line.strip() for line in JULIA_AUDIT.splitlines() if line.strip())
    process = subprocess.run(
        [str(args.launcher), "-e", audit_expression],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    (result_dir / "syslab.stdout.txt").write_text(process.stdout, encoding="utf-8")
    (result_dir / "syslab.stderr.txt").write_text(process.stderr, encoding="utf-8")
    values = parse_output(process.stdout)
    constant_matrix_mu_available = (
        process.returncode == 0
        and values.get("cmsclsyn") == "true"
        and values.get("mussv") == "true"
        and float(values.get("bound", "nan")) > 0.0
    )
    dynamic_mu_controller_synthesis_available = (
        values.get("musyn") == "true" or values.get("MuSynthesis") == "true"
    )
    report = {
        "schema": "mosim.control_platform.syslab_mu_capability_audit.v1",
        "status": "passed_capability_audit" if constant_matrix_mu_available else "blocked",
        "launcher": str(args.launcher),
        "process_return_code": process.returncode,
        "symbols": {
            "musyn": values.get("musyn") == "true",
            "MuSynthesis": values.get("MuSynthesis") == "true",
            "cmsclsyn": values.get("cmsclsyn") == "true",
            "mussv": values.get("mussv") == "true",
        },
        "cmsclsyn_example": {
            "bound": float(values["bound"]) if "bound" in values else None,
            "q_size": [int(values["q_rows"]), int(values["q_cols"])] if "q_rows" in values and "q_cols" in values else None,
        },
        "constant_matrix_mu_available": constant_matrix_mu_available,
        "dynamic_mu_controller_synthesis_available": dynamic_mu_controller_synthesis_available,
        "decision": "deferred",
        "decision_reason": "Syslab executes cmsclsyn/mussv for constant-matrix mu analysis, but exposes no musyn or MuSynthesis dynamic controller synthesis entrypoint. MATLAB Robust Control Toolbox is not licensed on this machine.",
        "claim_ceiling": "tool_capability_audit_only_not_a_mu_synthesis_controller",
    }
    (result_dir / "SYSLAB_MU_CAPABILITY_AUDIT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed_capability_audit" else 1


if __name__ == "__main__":
    raise SystemExit(main())
