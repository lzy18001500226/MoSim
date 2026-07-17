#!/usr/bin/env python3
"""Fail-closed provenance check for the P3 generated px4ctrl backend."""

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
    "integral_smc": 1,
    "terminal_smc": 2,
    "nonsingular_terminal_smc": 3,
    "super_twisting_smc": 4,
    "adaptive_smc": 5,
    "fuzzy_smc": 6,
}
BASE.SCHEMA = "mosim.sliding_mode_generated_runtime_provenance.v1"
BASE.MODEL = "MoSim_P3_SlidingMode_CFunction_Sysblock"
BASE.BACKEND = "sliding_mode_attitude_thrust"
BASE.BACKEND_DEFINITION = "MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST"
BASE.GENERATED_DIR_CACHE_VAR = "MOSIM_PX4CTRL_SLIDING_MODE_ATTITUDE_THRUST_GENERATED_DIR"
BASE.RUNTIME_SYMBOL = f"{BASE.MODEL}::Step"
BASE.BINARY_SYMBOL = "MosimSlidingModeStepScalar"
BASE.REQUIRED_GENERATED_FILES = (
    f"{BASE.MODEL}.c", f"{BASE.MODEL}.h", f"{BASE.MODEL}_data.c",
    f"{BASE.MODEL}_private.h", "extern_inc/momodel_extern_ince1.c",
)


if __name__ == "__main__":
    raise SystemExit(BASE.main())
