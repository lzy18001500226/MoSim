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


def test_controller_screenshot_rebuild_preserves_46_route_scope_and_archive_boundary():
    module = load_module()
    manifest = module.build_manifest()

    assert module.validate_manifest(manifest) == []
    assert manifest["summary"] == {
        "catalog_scheme_count": 49,
        "current_screenshot_scope_count": 46,
        "asset_directory_count": 46,
        "directory_version_marker_count": 46,
        "excluded_from_current_screenshot_scope_count": 3,
        "structure_capture_count": 0,
        "minimum_result_capture_count": 0,
        "unexpected_active_png_count": 0,
        "legacy_archive_valid": True,
    }
    assert {item["scheme_id"] for item in manifest["excluded_routes"]} == {
        "mu_synthesis",
        "neural_smc",
        "px4ctrl",
    }
    assert len(manifest["slots"]) == 46
    assert all(
        item["capture_rules"]["allowed_source"] == "windows_mcp_direct_whole_window_capture_only"
        and item["capture_rules"]["preserve_window_native_aspect_ratio"] is True
        and item["directory_version_marker"].endswith("/.gitkeep")
        for item in manifest["slots"]
    )
    archive_rows = module.read(module.ARCHIVE_MANIFEST)["files"]
    root_readme = next(
        row
        for row in archive_rows
        if row["origin_path"] == "Docs/报告/图/控制器/README.md"
    )
    assert root_readme["archived_path"].endswith("legacy_root_README.md")
