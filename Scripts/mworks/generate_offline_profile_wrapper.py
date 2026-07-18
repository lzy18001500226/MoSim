#!/usr/bin/env python3
"""Generate one validated thin MWORKS wrapper under Results/."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
OUTPUT_ROOT = ROOT / "Results" / "mworks_generated_profiles"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
MODELICA_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def finite_vector(value: Any, size: int, name: str) -> list[float]:
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f"{name}_must_have_{size}_values")
    result = [float(item) for item in value]
    if any(item != item or abs(item) == float("inf") for item in result):
        raise ValueError(f"{name}_must_be_finite")
    return result


def modelica_vector(values: list[float]) -> str:
    return "{" + ", ".join(format(value, ".12g") for value in values) + "}"


def certified_request(catalog: dict[str, Any], profile_id: str, run_id: str) -> dict[str, Any]:
    for profile in catalog["certified_profiles"]:
        if profile["profile_id"] == profile_id:
            if profile["vehicle_count"] != 1:
                raise ValueError("direct_multi_uav_profile_does_not_use_generated_wrapper")
            if profile.get("execution_kind") == "direct_model":
                raise ValueError("direct_certified_profile_does_not_use_generated_wrapper")
            return {**profile, "run_id": run_id, "profile_kind": "certified"}
    raise ValueError("certified_profile_not_found")


def validate_request(catalog: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    run_id = str(request.get("run_id", ""))
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError("invalid_run_id")
    controller_id = str(request.get("controller_id", ""))
    module = catalog["modules"].get(controller_id)
    if not module or module.get("status") not in {"available", "fixture"}:
        raise ValueError("controller_not_available_offline")
    output_variant = str(request.get("output_variant", ""))
    if output_variant != module["output_variant"]:
        raise ValueError("output_variant_incompatible")
    default_runner = catalog["runners"].get(output_variant)
    if not default_runner:
        raise ValueError("runner_not_found")
    runner_model = module.get("runner_model", default_runner["model"])
    rotor_effectiveness = finite_vector(request.get("rotor_effectiveness", [1, 1, 1, 1]), 4, "rotor_effectiveness")
    if any(value < 0 or value > 1 for value in rotor_effectiveness):
        raise ValueError("rotor_effectiveness_out_of_range")
    gust_force = finite_vector(request.get("gust_force", [0, 0, 0]), 3, "gust_force")
    if any(abs(value) > 20 for value in gust_force):
        raise ValueError("gust_force_out_of_range")
    model_name = "MoSimGenerated_" + re.sub(r"[^A-Za-z0-9_]", "_", run_id)
    if not MODELICA_NAME_PATTERN.fullmatch(model_name):
        raise ValueError("invalid_generated_model_name")
    return {
        **request,
        "run_id": run_id,
        "controller_id": controller_id,
        "output_variant": output_variant,
        "runner_model": runner_model,
        "adapter_model": module["adapter_model"],
        "rotor_effectiveness": rotor_effectiveness,
        "gust_force": gust_force,
        "generated_model_name": model_name,
    }


def render_wrapper(profile: dict[str, Any]) -> str:
    modifications = [f"redeclare model Controller = {profile['adapter_model']}"]
    if profile["output_variant"] == "ROTOR_COMMAND":
        modifications.extend([
            f"rotor_effectiveness = {modelica_vector(profile['rotor_effectiveness'])}",
            f"gust_force = {modelica_vector(profile['gust_force'])}",
        ])
    joined = ",\n    ".join(modifications)
    return (
        f"model {profile['generated_model_name']}\n"
        f"  \"Generated thin offline profile wrapper; source remains in project packages\"\n"
        f"  extends {profile['runner_model']}(\n    {joined});\n"
        "  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, "
        "Tolerance = 0.0001, Interval = 0.01));\n"
        f"end {profile['generated_model_name']};\n"
    )


def generate(request: dict[str, Any]) -> dict[str, Any]:
    catalog = read_json(CATALOG_PATH)
    profile = validate_request(catalog, request)
    output_dir = (OUTPUT_ROOT / profile["run_id"]).resolve()
    if not output_dir.is_relative_to(OUTPUT_ROOT.resolve()):
        raise ValueError("generated_output_outside_results")
    output_dir.mkdir(parents=True, exist_ok=False)
    wrapper_path = output_dir / "GeneratedProfile.mo"
    wrapper_path.write_text(render_wrapper(profile), encoding="utf-8", newline="\n")
    profile_record = {
        "schema": "mosim.offline_generated_profile.v1",
        **profile,
        "wrapper_path": wrapper_path.relative_to(ROOT).as_posix(),
        "wrapper_sha256": hashlib.sha256(wrapper_path.read_bytes()).hexdigest(),
        "certification_state": "generated_unchecked",
        "claim_boundary": "Generated and compatibility-checked only; MWORKS check, simulation, Result.msr and animation remain pending."
    }
    write_json(output_dir / "PROFILE.json", profile_record)
    return profile_record


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--request-json", type=Path)
    source.add_argument("--certified-profile-id")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    catalog = read_json(CATALOG_PATH)
    request = read_json(args.request_json) if args.request_json else certified_request(catalog, args.certified_profile_id, args.run_id)
    request["run_id"] = args.run_id
    print(json.dumps(generate(request), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
