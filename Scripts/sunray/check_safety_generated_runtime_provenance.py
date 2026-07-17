#!/usr/bin/env python3
"""Fail-closed provenance and event check for the P6 SafetySupervisor backend."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "Scripts/sunray/check_linear_robust_generated_runtime_provenance.py"
SPEC = importlib.util.spec_from_file_location("generated_runtime_provenance_base", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {BASE_PATH}")
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

BASE.CONTROLLERS = {
    "safety_filter": 1,
    "cbf": 2,
    "reference_governor": 3,
    "geofence": 4,
    "emergency_stop": 5,
    "return_and_land": 6,
    "failsafe_state_machine": 7,
}
BASE.SCHEMA = "mosim.safety_generated_runtime_provenance.v1"
BASE.MODEL = "MoSim_P6_SafetySupervisor_CFunction_Sysblock"
BASE.BACKEND = "safety_supervisor"
BASE.BACKEND_DEFINITION = "MOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR"
BASE.GENERATED_DIR_CACHE_VAR = "MOSIM_PX4CTRL_SAFETY_SUPERVISOR_GENERATED_DIR"
BASE.RUNTIME_SYMBOL = f"{BASE.MODEL}::Step"
BASE.BINARY_SYMBOL = "MosimSafetySupervisorStepScalar"
BASE.SIL_LIST_KEY = "modes"
BASE.REQUIRED_GENERATED_FILES = (
    f"{BASE.MODEL}.c", f"{BASE.MODEL}.h", f"{BASE.MODEL}_data.c",
    f"{BASE.MODEL}_private.h", "extern_inc/momodel_extern_ince1.c",
)
EXPECTED_ACTIONS = {
    "safety_filter": 1, "cbf": 1, "reference_governor": 1, "geofence": 1,
    "emergency_stop": 5, "return_and_land": 3, "failsafe_state_machine": 2,
}

ORIGINAL_BUILD_PAYLOAD = BASE.build_payload


def build_payload(args):
    payload = ORIGINAL_BUILD_PAYLOAD(args)
    errors = payload["errors"]
    expected_action = EXPECTED_ACTIONS[args.controller_profile]
    event_match = None
    if args.runtime_log and args.runtime_log.is_file():
        log_text = args.runtime_log.read_text(encoding="utf-8", errors="replace")
        pattern = re.compile(
            rf"\[px4ctrl\] safety_event mode={re.escape(args.controller_profile)} "
            rf"action={expected_action} state=(\d+) active_constraints=(\d+) "
            rf"test_event=true safe_thrust=([-+0-9.eE]+)"
        )
        event_match = pattern.search(log_text)
    if event_match is None:
        errors.append("expected generated SafetySupervisor event acknowledgement missing")
    payload["expected_action"] = expected_action
    payload["event_acknowledged"] = event_match is not None
    payload["event_state"] = int(event_match.group(1)) if event_match else None
    payload["active_constraints"] = int(event_match.group(2)) if event_match else None
    payload["safe_thrust"] = float(event_match.group(3)) if event_match else None
    payload["status"] = "passed" if not errors else "failed"
    return payload


BASE.build_payload = build_payload


if __name__ == "__main__":
    raise SystemExit(BASE.main())
