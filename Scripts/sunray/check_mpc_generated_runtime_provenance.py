#!/usr/bin/env python3
"""Fail-closed provenance check for the P4 generated px4ctrl backend."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "Scripts/sunray/check_linear_robust_generated_runtime_provenance.py"
SPEC = importlib.util.spec_from_file_location("generated_runtime_provenance_base", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {BASE_PATH}")
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

BASE.CONTROLLERS = {
    "linear_mpc": 1,
    "robust_mpc": 2,
    "adaptive_mpc": 3,
    "tube_mpc": 4,
    "explicit_gain_scheduled_mpc": 5,
    "ilqr": 6,
    "mppi": 7,
}
BASE.SCHEMA = "mosim.mpc_generated_runtime_provenance.v1"
BASE.MODEL = "MoSim_P4_Mpc_CFunction_Sysblock"
BASE.BACKEND = "mpc_attitude_thrust"
BASE.BACKEND_DEFINITION = "MOSIM_PX4CTRL_GENERATED_BACKEND_MPC_ATTITUDE_THRUST"
BASE.GENERATED_DIR_CACHE_VAR = "MOSIM_PX4CTRL_MPC_ATTITUDE_THRUST_GENERATED_DIR"
BASE.RUNTIME_SYMBOL = f"{BASE.MODEL}::Step"
BASE.BINARY_SYMBOL = "MosimMpcStepScalar"
BASE.REQUIRED_GENERATED_FILES = (
    f"{BASE.MODEL}.c", f"{BASE.MODEL}.h", f"{BASE.MODEL}_data.c",
    f"{BASE.MODEL}_private.h", "extern_inc/momodel_extern_ince1.c",
)


if __name__ == "__main__":
    raise SystemExit(BASE.main())
