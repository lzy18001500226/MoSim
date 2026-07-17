#!/usr/bin/env python3
"""Fail-closed provenance check for the P9 learning px4ctrl backend."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "Scripts/sunray/check_linear_robust_generated_runtime_provenance.py"
SPEC = importlib.util.spec_from_file_location("learning_runtime_provenance_base", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {BASE_PATH}")
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

ARTIFACT_SHA256 = "4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45"
BASE.CONTROLLERS = {"trained_neural_residual": 1, "rl_gain_scheduler": 2}
BASE.SCHEMA = "mosim.learning_generated_runtime_provenance.v1"
BASE.MODEL = "MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock"
BASE.BACKEND = "learning_attitude_thrust"
BASE.BACKEND_DEFINITION = "MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST"
BASE.GENERATED_DIR_CACHE_VAR = "MOSIM_PX4CTRL_LEARNING_ATTITUDE_THRUST_GENERATED_DIR"
BASE.RUNTIME_SYMBOL = f"{BASE.MODEL}::Step"
BASE.BINARY_SYMBOL = "MosimLearningAttitudeThrustStepScalar"
BASE.REQUIRED_GENERATED_FILES = (
    f"{BASE.MODEL}.c", f"{BASE.MODEL}.h", f"{BASE.MODEL}_data.c",
    f"{BASE.MODEL}_private.h", "extern_inc/momodel_extern_ince1.c",
)
BASE.SIL_LIST_KEY = "routes"
_base_build_payload = BASE.build_payload


def build_payload(args):
    payload = _base_build_payload(args)
    errors = payload["errors"]
    artifact_path = ROOT / "Config/control_platform/learning_control_artifact.json"
    try:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        artifact = {}
        errors.append(f"invalid learning artifact: {exc}")
    if artifact.get("artifact_sha256") != ARTIFACT_SHA256:
        errors.append("learning artifact hash mismatch")
    generated_extern = Path(args.generated_code_dir) / "extern_inc/momodel_extern_ince1.c"
    generated_text = generated_extern.read_text(encoding="utf-8", errors="replace") if generated_extern.is_file() else ""
    if ARTIFACT_SHA256 not in generated_text:
        errors.append("generated C does not embed the frozen learning artifact hash")
    if args.runtime_log:
        log_text = args.runtime_log.read_text(encoding="utf-8", errors="replace") if args.runtime_log.is_file() else ""
        if f"learning_artifact_sha256={ARTIFACT_SHA256}" not in log_text:
            errors.append("runtime learning artifact hash acknowledgement missing")
    payload["learning_artifact"] = str(artifact_path)
    payload["learning_artifact_sha256"] = ARTIFACT_SHA256 if not errors else None
    payload["status"] = "passed" if not errors else "failed"
    return payload


BASE.build_payload = build_payload


if __name__ == "__main__":
    raise SystemExit(BASE.main())
