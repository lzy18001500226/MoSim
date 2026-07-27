#!/usr/bin/env python3
"""Materialize the current-root PID ATTITUDE_THRUST CFunction adapter source.

The P1 artifact is a verified source import, not evidence for the current G6
formal closure.  This builder moves the exact embedded C implementation into
the formal model root and records the source and generated hashes so the new
runner has no executable dependency on Results/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY_SOURCE = ROOT / (
    "Results/control_platform/p1_pid_attitude_thrust_mworks_20260716/models/"
    "MoSim_PID_AttitudeThrust_CFunction_Sysblock.mo"
)
OUTPUT = ROOT / (
    "Models/MoSimQuadrotorModel/Control/Bridges/"
    "PidAttitudeThrustCFunction.mo"
)
MANIFEST = ROOT / (
    "Results/control_platform/g6_formal_champion_promotion_20260725/"
    "cascade_pid/adapter_source_import.json"
)
BINDING = ROOT / "Config/control_platform/g6_champion_bindings/cascade_pid.json"
SOURCE_MODEL = "MoSim_PID_AttitudeThrust_CFunction_Sysblock"
TARGET_MODEL = "PidAttitudeThrustCFunction"
TARGET_WITHIN = "MoSimQuadrotorModel.Control.Bridges"
CURRENT_CODEGEN = ROOT / (
    "Results/control_platform/g6_formal_champion_promotion_20260725/"
    "cascade_pid/generated_c"
)

# Keep the PID-family formal closure on the same physical provenance chain as
# the other five promoted champions.  Binding only the thin assembly file
# would leave the actuator, sensor, parameter, and reference dependencies
# outside the hash-bound record.
SHARED_CLOSURE_SOURCES: tuple[tuple[str, str], ...] = (
    ("shared_sunray150_assembly", "Models/MoSimQuadrotorModel/Vehicle/Sunray150Assembly.mo"),
    ("physical_wrench_adapter", "Models/MoSimQuadrotorModel/Vehicle/Dynamics/PhysicalWrenchAdapter.mo"),
    ("wrapper_surface", "Models/MoSimQuadrotorModel/Vehicle/Dynamics/WrapperSurface.mo"),
    ("rotor_actuator_core", "Models/MoSimQuadrotorModel/Vehicle/Dynamics/RotorActuatorCore.mo"),
    ("plant_sensor_surface", "Models/MoSimQuadrotorModel/Vehicle/Sensors/package.mo"),
    ("virtual_px4_classic_profile", "Models/MoSimQuadrotorModel/Parameters/Sunray150VirtualPx4Classic.mo"),
    ("climb_path_reference", "Models/MoSimQuadrotorModel/Guidance/Trajectories/package.mo"),
)

REQUIRED_SOURCE_PATHS: tuple[tuple[str, str], ...] = (
    ("formal_runner", "Models/MoSimQuadrotorModel/Experiment/Runners/CascadePidFormalRunner.mo"),
    ("formal_adapter", "Models/MoSimQuadrotorModel/Control/Adapters/CascadePidAttitudeThrustAdapter.mo"),
    ("current_root_cfunction_core", "Models/MoSimQuadrotorModel/Control/Bridges/PidAttitudeThrustCFunction.mo"),
    ("shared_attitude_rate_allocator", "Models/MoSimQuadrotorModel/Control/Allocation/OfflineAttitudeRateAllocator.mo"),
    *SHARED_CLOSURE_SOURCES,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_native_text(text: str) -> str:
    """Remove only MWORKS-native line-end and trailing-whitespace churn.

    Sysplorer can strip the trailing spaces emitted by an older exported
    CFunction source.  Those bytes do not alter the Modelica model, its port
    list, its external function, or generated C binding.  Keep all line
    content intact so a substantive project-side modification is still
    rejected by the source-import gate.
    """

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip(" \t") for line in lines)


def native_serialization_equivalence(expected: str, current: str) -> str | None:
    """Classify the only accepted historical-import serialization variant."""

    if current == expected:
        return "exact_bytes"
    if canonical_native_text(current) == canonical_native_text(expected):
        return "mworks_line_end_and_trailing_whitespace_only"
    return None


def materialized_text() -> str:
    if not LEGACY_SOURCE.is_file():
        raise FileNotFoundError(f"PID ATTITUDE_THRUST source import is missing: {LEGACY_SOURCE}")
    text = LEGACY_SOURCE.read_text(encoding="utf-8")
    if text.lstrip().startswith("within "):
        raise RuntimeError("Expected the historical CFunction import to be a top-level model")
    if text.count(f"model {SOURCE_MODEL}") != 1 or text.count(f"end {SOURCE_MODEL};") != 1:
        raise RuntimeError("Historical CFunction model marker is not unique")

    text = text.replace(f"model {SOURCE_MODEL}", f"model {TARGET_MODEL}", 1)
    text = text.replace(f"end {SOURCE_MODEL};", f"end {TARGET_MODEL};", 1)

    legacy_codegen = (
        ROOT / "Results/control_platform/p1_pid_attitude_thrust_mworks_20260716/generated_c_v2"
    )
    legacy_literal = str(legacy_codegen).replace("\\", "\\\\")
    current_literal = str(CURRENT_CODEGEN).replace("\\", "\\\\")
    if legacy_literal not in text:
        raise RuntimeError("Historical CFunction code-generation path was not found for relocation")
    text = text.replace(legacy_literal, current_literal)
    return f"within {TARGET_WITHIN};\n{text.rstrip()}\n"


def manifest(
    current_hash: str,
    imported_source_hash: str,
    serialization_equivalence: str,
) -> dict[str, object]:
    return {
        "schema": "mosim.g6.cascade_pid_adapter_source_import.v1",
        "purpose": "Current-root formal adapter source materialization before MWORKS minimum closure.",
        "scheme_id": "cascade_pid",
        "source_role": "historical_behavior_reference_only",
        "legacy_source": str(LEGACY_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "legacy_source_sha256": sha256(LEGACY_SOURCE),
        "current_model_file": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "current_model_class": f"{TARGET_WITHIN}.{TARGET_MODEL}",
        "current_model_sha256": current_hash,
        "historical_materialized_source_sha256": imported_source_hash,
        "serialization_equivalence": serialization_equivalence,
        "embedded_external_function": "MosimPidAttitudeThrustStepScalar",
        "code_generation_output": str(CURRENT_CODEGEN.relative_to(ROOT)).replace("\\", "/"),
        "claim_boundary": (
            "This import only establishes source provenance. MWORKS CheckModel, "
            "current-run minimum closure, result metrics, and A/B validation are separate gates."
        ),
    }


def project_file(path_text: str, *, label: str) -> Path:
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} leaves the project root: {path_text}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"{label} is missing: {path_text}")
    return path


def current_binding() -> dict[str, object]:
    if not BINDING.is_file():
        raise FileNotFoundError(f"Cascade PID formal binding is missing: {BINDING}")
    value = json.loads(BINDING.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Cascade PID formal binding must be a JSON object")
    if value.get("schema") != "mosim.g6_formal_champion_binding.v1":
        raise ValueError("Cascade PID formal binding schema is unexpected")
    if value.get("controller_id") != "cascade_pid":
        raise ValueError("Cascade PID formal binding controller_id is unexpected")
    return value


def current_binding_with_source_hashes(binding: dict[str, object]) -> dict[str, object]:
    """Refresh the PID binding after deterministic formal-harness changes."""

    refreshed = json.loads(json.dumps(binding))
    boundary = refreshed.get("formal_harness_feedback_boundary")
    if not isinstance(boundary, dict):
        raise ValueError("Cascade PID formal binding feedback boundary is missing")
    boundary["kind"] = "sampled_controller_inputs"
    boundary["sample_period_s"] = 0.01
    boundary["initial_measurement"] = "zero"
    boundary["signals"] = [
        "reference.position_command -> controller.position_ref",
        "reference.velocity_command -> controller.velocity_ref",
        "reference.acceleration_command -> controller.acceleration_ref",
        "plant.position -> controller.position_mea",
        "plant.attitude -> controller.attitude_mea",
    ]
    boundary["continuous_inner_loop_signals"] = [
        "plant.attitude -> offline_inner_allocator.attitude_mea",
    ]
    boundary["reason"] = (
        "The discrete C-function cascade core receives explicit 100 Hz UnitDelay boundaries on position, "
        "velocity, and acceleration references plus plant measurements. The shared inner attitude-rate "
        "allocator keeps direct plant attitude feedback so its stabilizing loop is not delayed."
    )
    for section in ("target", "formal_adapter"):
        item = refreshed.get(section)
        if not isinstance(item, dict):
            raise ValueError(f"Cascade PID formal binding {section} is missing")
        model_file = item.get("model_file")
        if not isinstance(model_file, str):
            raise ValueError(f"Cascade PID formal binding {section}.model_file is missing")
        item["model_sha256"] = sha256(project_file(model_file, label=f"{section} model"))
    adapter = refreshed["formal_adapter"]
    if not isinstance(adapter, dict):
        raise ValueError("Cascade PID formal binding formal_adapter is invalid")
    adapter["implementation"] = {"kind": "direct_model_reference"}

    sources = refreshed.get("source_bindings")
    if not isinstance(sources, list) or not sources:
        raise ValueError("Cascade PID formal binding source_bindings is missing")
    source_by_role: dict[str, dict[str, object]] = {}
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Cascade PID formal binding source entry is invalid")
        role = source.get("role")
        path_text = source.get("path")
        if not isinstance(role, str) or not isinstance(path_text, str):
            raise ValueError("Cascade PID formal binding source role/path is invalid")
        if role in source_by_role:
            raise ValueError(f"Cascade PID formal binding source role repeats: {role}")
        source_by_role[role] = source

    normalized_sources: list[dict[str, object]] = []
    for role, path_text in REQUIRED_SOURCE_PATHS:
        existing = source_by_role.pop(role, None)
        if existing is not None and existing.get("path") != path_text:
            raise ValueError(
                f"Cascade PID formal binding {role} path differs from the shared closure contract: "
                f"{existing.get('path')} != {path_text}"
            )
        normalized_sources.append(
            {
                "role": role,
                "path": path_text,
                "expected_sha256": sha256(project_file(path_text, label=role)),
            }
        )

    # Preserve the source-import manifest after the physical chain.  Any
    # future extra provenance source remains bound, but cannot displace a
    # required physical dependency or evade hash refresh.
    for source in sources:
        role = source["role"]
        if role not in source_by_role:
            continue
        path_text = source["path"]
        if not isinstance(role, str) or not isinstance(path_text, str):
            raise ValueError("Cascade PID formal binding source role/path is invalid")
        normalized_sources.append(
            {
                "role": role,
                "path": path_text,
                "expected_sha256": sha256(project_file(path_text, label=role)),
            }
        )
    refreshed["source_bindings"] = normalized_sources
    return refreshed


def binding_hash_mismatches(binding: dict[str, object]) -> list[str]:
    refreshed = current_binding_with_source_hashes(binding)
    mismatches: list[str] = []
    for section in ("target", "formal_adapter"):
        expected = binding[section]
        actual = refreshed[section]
        if expected != actual:
            mismatches.append(section)
    expected_sources = binding["source_bindings"]
    actual_sources = refreshed["source_bindings"]
    if expected_sources != actual_sources:
        mismatches.append("source_bindings")
    for expected, actual in zip(expected_sources, actual_sources):
        if expected != actual:
            mismatches.append(str(expected.get("role", "unknown_source")))
    return mismatches


def write_binding(binding: dict[str, object]) -> None:
    BINDING.write_text(json.dumps(binding, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the current generated model and manifest")
    args = parser.parse_args()
    expected = materialized_text()
    imported_source_hash = hashlib.sha256(canonical_native_text(expected).encode("utf-8")).hexdigest()
    current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
    equivalence = native_serialization_equivalence(expected, current) if current else None

    if args.check:
        errors: list[str] = []
        if not OUTPUT.is_file() or equivalence is None:
            errors.append(
                "current formal CFunction model differs from the deterministic source import "
                "outside MWORKS-native line-end/trailing-whitespace serialization"
            )
        current_hash = sha256(OUTPUT) if OUTPUT.is_file() else ""
        expected_manifest = manifest(current_hash, imported_source_hash, equivalence or "unverified")
        if not MANIFEST.is_file():
            errors.append("adapter source-import manifest is missing")
        else:
            try:
                actual_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"adapter source-import manifest is invalid JSON: {exc}")
            else:
                if actual_manifest != expected_manifest:
                    errors.append("adapter source-import manifest differs from deterministic content")
        binding = current_binding()
        stale_binding_roles = binding_hash_mismatches(binding)
        if stale_binding_roles:
            errors.append(
                "Cascade PID formal binding source hashes are stale: "
                + ", ".join(stale_binding_roles)
            )
        print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        return 0 if not errors else 1

    if OUTPUT.is_file() and equivalence is None:
        raise RuntimeError(
            "Refusing to overwrite a current formal CFunction model whose content differs from "
            "the deterministic historical import outside native serialization whitespace."
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    if not OUTPUT.is_file():
        OUTPUT.write_text(expected, encoding="utf-8", newline="\n")
        current = OUTPUT.read_text(encoding="utf-8")
        equivalence = native_serialization_equivalence(expected, current)
    if equivalence is None:
        raise RuntimeError("Current formal CFunction model cannot be classified after materialization")
    expected_manifest = manifest(sha256(OUTPUT), imported_source_hash, equivalence)
    MANIFEST.write_text(json.dumps(expected_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    refreshed_binding = current_binding_with_source_hashes(current_binding())
    write_binding(refreshed_binding)
    print(
        json.dumps(
            {
                "adapter_source_import": expected_manifest,
                "formal_binding": str(BINDING.relative_to(ROOT)).replace("\\", "/"),
                "formal_binding_source_hashes": refreshed_binding["source_bindings"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
