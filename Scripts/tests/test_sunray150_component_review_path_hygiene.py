from pathlib import Path

from Scripts.UE5.assets.check_sunray150_component_review_path_hygiene import (
    PROJECT_ROOT,
    build_report,
    resolve_project_path,
)


def test_component_review_path_hygiene_keeps_required_gap_fill_outputs() -> None:
    report = build_report()

    assert report["required_components"]["battery_present"] is True
    assert report["required_components"]["guard_landing_gear_present"] is True
    assert report["path_policy"]["source_manifest_all_outputs_have_project_relative_path"] is True
    assert report["quality_boundary"]["manual_visual_review_required"] is True
    assert report["quality_boundary"]["final_material_acceptance"] is False


def test_component_review_path_hygiene_routes_all_images_by_project_relative_path() -> None:
    report = build_report()

    for item in report["component_index"]:
        rel = item["project_relative_path"]
        assert not Path(rel).is_absolute()
        assert resolve_project_path(rel).is_file()
        assert item["bytes"] > 0
        assert item["non_flat"] is True


def test_component_review_path_hygiene_rejects_paths_outside_project() -> None:
    outside = PROJECT_ROOT.parent / "OtherProject" / "battery.png"

    try:
        resolve_project_path(str(outside))
    except AssertionError as exc:
        assert "path outside project" in str(exc)
    else:
        raise AssertionError("outside path was accepted")
