from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "Config" / "control_platform" / "mworks_app_entrypoints.json"


def load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8-sig"))


def test_mworks_app_entrypoints_reference_existing_formal_assets() -> None:
    contract = load_contract()

    assert contract["schema"] == "mosim.mworks_app_entrypoints.v1"
    assert (ROOT / contract["canonical_package"]["package_file"]).is_file()
    for path in contract["source_authorities"].values():
        assert (ROOT / path).exists(), path

    entries = {entry["entry_id"]: entry for entry in contract["review_entrypoints"]}
    assert set(entries) == {
        "sunray150_assembly",
        "px4ctrl_primary",
        "official_pid_baseline",
    }

    assembly = entries["sunray150_assembly"]
    assert (ROOT / assembly["model_file"]).is_file()
    assert (ROOT / assembly["thumbnail_asset"]).is_file()
    assert (ROOT / assembly["existing_evidence_root"]).is_dir()

    for entry_id in ("px4ctrl_primary", "official_pid_baseline"):
        entry = entries[entry_id]
        assert (ROOT / entry["runner_file"]).is_file()
        assert (ROOT / entry["controller_review_file"]).is_file()
        assert all((ROOT / path).is_dir() for path in entry["existing_result_roots"])

    assert (ROOT / entries["official_pid_baseline"]["negative_evidence_root"]).is_dir()


def test_mworks_app_entrypoints_preserve_g3_and_result_boundaries() -> None:
    contract = load_contract()

    boundary = contract["app_boundary"]
    assert boundary["app_source_change"] == "deferred_until_g3_review"
    assert boundary["mworks_launch"] == "not_app_managed"
    assert boundary["simulation_execution"] == "not_app_managed"
    assert boundary["native_result_msr"]["usage"] == "manual_optional"
    assert boundary["native_result_msr"]["rerun_to_create_replay"] == "not_authorized"

    g3 = contract["g3_deferred_population"]
    assert g3["tier2_route_target_count"] == 45
    assert g3["historical_g2_record_count"] == 48
    assert g3["app_binding_status"] == "deferred_until_g3_review"
    assert (ROOT / g3["historical_g2_result_root"]).is_dir()
    assert set(g3["tier1_review_only_scheme_ids"]) == {
        "pid_awff_linear_eso",
        "smc_boundary_layer",
        "nmpc_outer",
    }
