from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "prepare_controller_screenshot_rebuild.py"


def load_module():
    spec = importlib.util.spec_from_file_location("controller_screenshot_rebuild", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_controller_screenshot_rebuild_covers_48_route_scope_with_current_capture_bindings():
    module = load_module()
    manifest = module.build_manifest()

    assert module.rp(module.OUTPUT_ROOT) == "Docs/报告/审计/控制器原生截图归位"
    assert module.validate_manifest(manifest) == []
    assert manifest["summary"] == {
        "catalog_scheme_count": 48,
        "current_screenshot_scope_count": 48,
        "asset_directory_count": 48,
        "directory_version_marker_count": 48,
        "excluded_from_current_screenshot_scope_count": 0,
        "current_native_structure_capture_count": 4,
        "current_g5_structure_capture_count": 0,
        "user_reviewed_historical_structure_count": 44,
        "minimum_result_capture_count": 0,
        "unexpected_active_png_count": 0,
        "legacy_archive_valid": True,
    }
    assert manifest["excluded_routes"] == []
    assert {item["scheme_id"] for item in manifest["supplemental_current_capture_routes"]} == {
        "pid_awff_linear_eso",
        "px4ctrl",
    }
    assert len(manifest["slots"]) == 48
    assert all(
        item["capture_rules"]["allowed_source"] == "windows_mcp_direct_whole_window_capture_only"
        and item["capture_rules"]["preserve_window_native_aspect_ratio"] is True
        and item["directory_version_marker"].endswith("/.gitkeep")
        and item["required_assets"]["structure_native_window"].endswith("/01_图形模型.png")
        and item["capture_status"]["minimum_closed_loop_result_native_window"] == "not_captured"
        for item in manifest["slots"]
    )
    current = {
        item["scheme_id"]: item
        for item in manifest["slots"]
        if item["capture_status"]["structure_native_window"]
        == "present_current_native_window"
    }
    assert set(current) == {
        "smc_boundary_layer",
        "nmpc_outer",
        "px4ctrl",
        "pid_awff_linear_eso",
    }
    assert current["px4ctrl"]["review_kind"] == "graphical_outer_loop"
    assert (
        current["pid_awff_linear_eso"]["review_kind"]
        == "equation_core_formal_runner_interface"
    )
    assert all(
        item["source_capture"]["capture_binding_kind"]
        == "direct_current_native_window"
        and item["required_assets"]["capture_manifest"]
        == "Docs/报告/审计/控制器原生截图归位/CURRENT_NATIVE_STRUCTURE_CAPTURE_BINDINGS.json"
        and item["required_assets"]["g5_review_packet"] is None
        for item in current.values()
    )
    historical = [
        item
        for item in manifest["slots"]
        if item["capture_status"]["structure_native_window"]
        == "present_user_reviewed_historical_graphical"
    ]
    assert len(historical) == 44
    assert all(
        item["source_capture"] is None
        and item["user_reviewed_archive_source"]["review_status"] == "user_visual_reviewed"
        and item["required_assets"]["capture_manifest"] is None
        and item["required_assets"]["g5_review_packet"] is None
        for item in historical
    )
    archive_rows = module.read(module.ARCHIVE_MANIFEST)["files"]
    root_readme = next(
        row
        for row in archive_rows
        if row["origin_path"] == "Docs/报告/图/控制器/README.md"
    )
    assert root_readme["archived_path"].endswith("legacy_root_README.md")
