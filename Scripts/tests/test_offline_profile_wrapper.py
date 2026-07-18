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
    assert "extends MoSimQuadrotorModel.ExperimentRunner.Runners.RotorCommandRunner" in source
    assert "redeclare model Controller = MoSimQuadrotorModel.ExperimentRunner.Adapters.OfficialPIDRotorAdapter" in source
    assert "rotor_effectiveness = {1, 1, 1, 1}" in source


def test_cross_boundary_composition_is_rejected() -> None:
    with pytest.raises(ValueError, match="output_variant_incompatible"):
        generator.validate_request(catalog(), request(output_variant="ATTITUDE_THRUST"))


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
