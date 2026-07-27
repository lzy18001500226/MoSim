#!/usr/bin/env python3
"""Materialize current-root CFunction sources for promoted G6 champions.

The selected SMC, MPC, and bounded-learning routes already have deterministic
project C cores.  Their earlier fixture exports live under ``Results/`` and
are useful evidence, but a whole-aircraft formal runner must not execute a
leaf model from a historical result directory.  This builder reproduces those
bridges from their current source builders, rewrites only the class namespace,
and records every generator input hash.

It intentionally does not run MWORKS.  CheckModel, simulation, native-window
capture, and code generation are later gates.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Bridges"
RESULT_ROOT = ROOT / "Results" / "control_platform" / "g6_formal_champion_promotion_20260725"
TARGET_WITHIN = "MoSimQuadrotorModel.Control.Bridges"


SPECS: tuple[dict[str, Any], ...] = (
    {
        "scheme_id": "super_twisting_smc",
        "builder": "Scripts/control_platform/build_sliding_mode_attitude_thrust_mworks_models.py",
        "builder_kind": "p2_family",
        "source_model": "MoSim_P3_SlidingMode_CFunction_Sysblock",
        "target_model": "SuperTwistingSmcCFunction",
        "external_function": "MosimSlidingModeStepScalar",
        "inputs": (
            "Scripts/control_platform/build_linear_robust_attitude_thrust_mworks_models.py",
            "Scripts/control_platform/sliding_mode_attitude_thrust_core.h",
            "Scripts/control_platform/sliding_mode_attitude_thrust_core.c",
            "Scripts/sunray/px4ctrl_golden_slice/build_g9_family_cfunction_sysblock.py",
        ),
    },
    {
        "scheme_id": "linear_mpc",
        "builder": "Scripts/control_platform/build_mpc_attitude_thrust_mworks_models.py",
        "builder_kind": "p2_family",
        "source_model": "MoSim_P4_Mpc_CFunction_Sysblock",
        "target_model": "LinearMpcCFunction",
        "external_function": "MosimMpcStepScalar",
        "inputs": (
            "Scripts/control_platform/build_linear_robust_attitude_thrust_mworks_models.py",
            "Scripts/control_platform/mpc_attitude_thrust_core.h",
            "Scripts/control_platform/mpc_attitude_thrust_core.c",
            "Scripts/sunray/px4ctrl_golden_slice/build_g9_family_cfunction_sysblock.py",
        ),
    },
    {
        "scheme_id": "trained_neural_residual",
        "builder": "Scripts/control_platform/build_learning_attitude_thrust_mworks_models.py",
        "builder_kind": "generic_family",
        "source_model": "MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock",
        "target_model": "TrainedNeuralResidualCFunction",
        "external_function": "MosimLearningAttitudeThrustStepScalar",
        "inputs": (
            "Scripts/control_platform/pid_unified_core.h",
            "Scripts/control_platform/pid_unified_core.c",
            "Scripts/control_platform/pid_attitude_thrust_core.h",
            "Scripts/control_platform/pid_attitude_thrust_core.c",
            "Scripts/control_platform/learning_control_weights.h",
            "Scripts/control_platform/learning_control_core.h",
            "Scripts/control_platform/learning_control_core.c",
            "Scripts/control_platform/learning_attitude_thrust_core.h",
            "Scripts/control_platform/learning_attitude_thrust_core.c",
            "Scripts/sunray/px4ctrl_golden_slice/build_g9_family_cfunction_sysblock.py",
        ),
    },
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def project_path(relative_path: str) -> Path:
    path = (ROOT / relative_path).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"path leaves project root: {relative_path}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"required generator input is missing: {relative_path}")
    return path


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def canonical_native_text(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip(" \t") for line in lines)


def native_serialization_equivalence(expected: str, current: str) -> str | None:
    if current == expected:
        return "exact_bytes"
    if canonical_native_text(current) == canonical_native_text(expected):
        return "mworks_line_end_and_trailing_whitespace_only"
    return None


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_spec(scheme_id: str) -> dict[str, Any]:
    for spec in SPECS:
        if spec["scheme_id"] == scheme_id:
            return spec
    raise ValueError(f"unknown promoted CFunction scheme: {scheme_id}")


def generated_bridge(spec: dict[str, Any]) -> str:
    module = load_module(project_path(str(spec["builder"])), f"g6_{spec['scheme_id']}_builder")
    codegen_dir = RESULT_ROOT / str(spec["scheme_id"]) / "generated_c"
    if spec["builder_kind"] == "p2_family":
        p2_builder = module.load_p2_builder()
        p2_builder.INPUTS = module.INPUTS
        p2_builder.OUTPUTS = module.OUTPUTS
        p2_builder.BASE_INPUTS = module.BASE_INPUTS
        generic_builder = p2_builder.load_generic_builder()
    elif spec["builder_kind"] == "generic_family":
        generic_builder = module.load_generic_builder()
    else:
        raise RuntimeError(f"unsupported builder kind: {spec['builder_kind']}")

    source_model = str(spec["source_model"])
    target_model = str(spec["target_model"])
    bridge = generic_builder.build_model(source_model, codegen_dir, module.embedded_c(), real_as_float=False)
    bridge = bridge.replace("MosimPx4ctrlG9FamilyCStepScalar", str(spec["external_function"]))
    if str(spec["external_function"]) not in bridge:
        raise RuntimeError(f"{spec['scheme_id']}: generated bridge lacks its expected external function")
    if bridge.count(f"model {source_model}") != 1 or bridge.count(f"end {source_model};") != 1:
        raise RuntimeError(f"{spec['scheme_id']}: source bridge model markers are not unique")
    bridge = bridge.replace(f"model {source_model}", f"model {target_model}", 1)
    bridge = bridge.replace(f"end {source_model};", f"end {target_model};", 1)
    return f"within {TARGET_WITHIN};\n{bridge.rstrip()}\n"


def target_path(spec: dict[str, Any]) -> Path:
    return BRIDGE_ROOT / f"{spec['target_model']}.mo"


def manifest_path(spec: dict[str, Any]) -> Path:
    return RESULT_ROOT / str(spec["scheme_id"]) / "adapter_source_import.json"


def generator_inputs(spec: dict[str, Any]) -> list[dict[str, str]]:
    paths = (str(spec["builder"]), *tuple(str(path) for path in spec["inputs"]))
    items: list[dict[str, str]] = []
    for raw_path in paths:
        path = project_path(raw_path)
        items.append({"path": relative(path), "sha256": sha256_file(path)})
    return items


def expected_manifest(spec: dict[str, Any], current_hash: str, equivalence: str) -> dict[str, Any]:
    target = target_path(spec)
    return {
        "schema": "mosim.g6.champion_cfunction_source_import.v1",
        "purpose": "Current-root CFunction materialization for separately bound formal whole-aircraft closure.",
        "scheme_id": spec["scheme_id"],
        "source_role": "deterministic_current_source_builder",
        "generator_inputs": generator_inputs(spec),
        "current_model_file": relative(target),
        "current_model_class": f"{TARGET_WITHIN}.{spec['target_model']}",
        "current_model_sha256": current_hash,
        "source_model_name": spec["source_model"],
        "embedded_external_function": spec["external_function"],
        "serialization_equivalence": equivalence,
        "code_generation_output": relative(RESULT_ROOT / str(spec["scheme_id"]) / "generated_c"),
        "claim_boundary": (
            "This deterministic source import establishes current-root CFunction provenance only. "
            "MWORKS CheckModel, current-run minimum closure, metrics, native window evidence, "
            "code generation, and Gazebo validation are separate gates."
        ),
    }


def materialize(spec: dict[str, Any], *, check: bool) -> list[str]:
    expected = generated_bridge(spec)
    target = target_path(spec)
    manifest = manifest_path(spec)
    current = target.read_text(encoding="utf-8") if target.is_file() else ""
    equivalence = native_serialization_equivalence(expected, current) if current else None
    errors: list[str] = []

    if check:
        if equivalence is None:
            errors.append(f"{spec['scheme_id']}: current CFunction differs from deterministic source import")
            return errors
        expected_value = expected_manifest(spec, sha256_file(target), equivalence)
        if not manifest.is_file():
            errors.append(f"{spec['scheme_id']}: source-import manifest is missing")
        else:
            try:
                actual_value = json.loads(manifest.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{spec['scheme_id']}: source-import manifest is invalid JSON: {exc}")
            else:
                if actual_value != expected_value:
                    errors.append(f"{spec['scheme_id']}: source-import manifest differs from deterministic content")
        return errors

    if target.is_file() and equivalence is None:
        errors.append(f"{spec['scheme_id']}: refusing to overwrite a divergent current CFunction")
        return errors
    target.parent.mkdir(parents=True, exist_ok=True)
    (RESULT_ROOT / str(spec["scheme_id"]) / "generated_c").mkdir(parents=True, exist_ok=True)
    if not target.is_file():
        target.write_text(expected, encoding="utf-8", newline="\n")
        current = target.read_text(encoding="utf-8")
        equivalence = native_serialization_equivalence(expected, current)
    if equivalence is None:
        errors.append(f"{spec['scheme_id']}: generated CFunction cannot be classified after materialization")
        return errors
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(expected_manifest(spec, sha256_file(target), equivalence), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", choices=[spec["scheme_id"] for spec in SPECS])
    parser.add_argument("--check", action="store_true", help="verify current imports and manifests without writing")
    args = parser.parse_args()
    selected = [find_spec(scheme_id) for scheme_id in args.only] if args.only else list(SPECS)
    errors: list[str] = []
    for spec in selected:
        errors.extend(materialize(spec, check=args.check))
    print(json.dumps({"ok": not errors, "checked": [spec["scheme_id"] for spec in selected], "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
