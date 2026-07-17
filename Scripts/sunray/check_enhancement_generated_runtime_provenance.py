#!/usr/bin/env python3
"""Fail-closed provenance check for the P5 generated px4ctrl backend."""

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
    "l1_adaptive": 1,
    "awff": 2,
    "complete_adrc": 3,
    "standardized_indi": 4,
    "parameter_scheduling": 5,
    "ilc": 6,
}
BASE.SCHEMA = "mosim.enhancement_generated_runtime_provenance.v1"
BASE.MODEL = "MoSim_P5_Enhancement_CFunction_Sysblock"
BASE.BACKEND = "enhancement_attitude_thrust"
BASE.BACKEND_DEFINITION = "MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST"
BASE.GENERATED_DIR_CACHE_VAR = "MOSIM_PX4CTRL_ENHANCEMENT_ATTITUDE_THRUST_GENERATED_DIR"
BASE.RUNTIME_SYMBOL = f"{BASE.MODEL}::Step"
BASE.BINARY_SYMBOL = "MosimEnhancementStepScalar"
BASE.REQUIRED_GENERATED_FILES = (
    f"{BASE.MODEL}.c", f"{BASE.MODEL}.h", f"{BASE.MODEL}_data.c",
    f"{BASE.MODEL}_private.h", "extern_inc/momodel_extern_ince1.c",
)


if __name__ == "__main__":
    raise SystemExit(BASE.main())
