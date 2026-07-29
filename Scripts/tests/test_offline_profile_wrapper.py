from __future__ import annotations

import json
from pathlib import Path

import pytest

from Scripts.mworks import generate_offline_profile_wrapper as generator


def catalog() -> dict:
    return json.loads(generator.CATALOG_PATH.read_text(encoding="utf-8"))


def request(**overrides) -> dict:
    value = {
        "run_id": "custom-test-v1",
        "profile_id": "custom_test_v1",
        "profile_kind": "custom",
        "controller_id": "official_pid",
        "output_variant": "ROTOR_COMMAND",
        "scenario_id": "climb",
        "rotor_effectiveness": [1, 1, 1, 1],
        "gust_force": [0, 0, 0],
    }
    value.update(overrides)
    return value


def test_validate_and_render_wrapper_keeps_explicit_boundary() -> None:
    profile = generator.validate_request(catalog(), request())
    source = generator.render_wrapper(profile)
    assert "extends MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner" in source
    assert "redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter" in source
    assert "rotor_effectiveness = {1, 1, 1, 1}" in source


def test_all_generated_single_uav_certified_profiles_keep_legacy_compatibility() -> None:
    authority = catalog()
    profiles = [
        profile
        for profile in authority["certified_profiles"]
        if profile["vehicle_count"] == 1
    ]
    validated = [
        generator.validate_request(
            authority,
            generator.certified_request(authority, profile["profile_id"], "legacy-regression-v1"),
        )
        for profile in profiles
    ]
    assert len(validated) == 8
    assert all(profile["composition_mode"] == "legacy_bundle_v1" for profile in validated)


def test_cross_boundary_composition_is_rejected() -> None:
    with pytest.raises(ValueError, match="output_variant_incompatible"):
        generator.validate_request(catalog(), request(output_variant="ATTITUDE_THRUST"))


def test_exact_resolved_layered_composition_is_accepted() -> None:
    composition = {
        "formation_controller": None,
        "nominal_controller": "official_pid",
        "augmentations": ["awff"],
        "safety_filter": None,
        "fault_manager": None,
    }
    profile = generator.validate_request(
        catalog(),
        request(controller_id="awff", composition=composition),
    )
    assert profile["composition_mode"] == "layered_exact_v2"
    assert profile["composition"] == composition


def test_unimplemented_extra_layer_is_rejected() -> None:
    composition = {
        "formation_controller": None,
        "nominal_controller": "official_pid",
        "augmentations": ["awff", "anti_windup"],
        "safety_filter": None,
        "fault_manager": None,
    }
    with pytest.raises(ValueError, match="composition_not_implemented_by_adapter"):
        generator.validate_request(
            catalog(),
            request(controller_id="awff", composition=composition),
        )


def test_unresolved_legacy_alias_cannot_claim_layered_composition() -> None:
    composition = {
        "formation_controller": None,
        "nominal_controller": "nmpc_outer",
        "augmentations": [],
        "safety_filter": None,
        "fault_manager": None,
    }
    with pytest.raises(ValueError, match="layered_composition_mapping_unresolved"):
        generator.validate_request(
            catalog(),
            request(controller_id="linear_mpc", composition=composition),
        )


def test_blocked_safety_profile_cannot_generate_wrapper() -> None:
    with pytest.raises(ValueError, match="controller_not_available_offline"):
        generator.validate_request(
            catalog(),
            request(controller_id="qp_nmpc_safety"),
        )


def test_invalid_run_id_cannot_escape_results_root() -> None:
    with pytest.raises(ValueError, match="invalid_run_id"):
        generator.validate_request(catalog(), request(run_id="../outside"))


def test_generate_writes_only_thin_wrapper_and_profile(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    monkeypatch.setattr(generator, "OUTPUT_ROOT", tmp_path)
    result = generator.generate(request(run_id="custom-output-v1"))
    output = tmp_path / "custom-output-v1"
    assert sorted(path.name for path in output.iterdir()) == ["GeneratedProfile.mo", "PROFILE.json"]
    assert result["certification_state"] == "generated_unchecked"
