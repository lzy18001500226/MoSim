from Scripts.ui.export_model_studio_catalog import build_catalog, render_tsv
from apps.model_studio.tools.generate_slapp import build_project


def test_catalog_is_registry_and_profile_driven() -> None:
    catalog = build_catalog()
    profiles = {profile["profile_id"]: profile for profile in catalog["profiles"]}
    assert profiles["px4ctrl_figure8_baseline_v1"]["controller_id"] == "px4ctrl"
    assert profiles["px4ctrl_figure8_baseline_v1"]["vehicle_count"] == 1
    assert profiles["factory_l2_three_uav_swarm_formation_v1"]["vehicle_count"] == 3
    assert profiles["factory_l2_three_uav_swarm_formation_v1"]["enabled"] is True
    vehicles = {vehicle["vehicle_count"]: vehicle for vehicle in catalog["vehicles"]}
    assert vehicles[1]["enabled"] is True
    assert vehicles[3]["enabled"] is True
    assert all(not vehicles[count]["enabled"] for count in range(4, 10))
    assert "PROFILE\tpx4ctrl_figure8_baseline_v1\t" in render_tsv(catalog)


def test_generated_app_normalizes_julia_ui_strings_and_preserves_disabled_labels() -> None:
    project = build_project()
    callbacks = {callback["name"]: callback["code"] for callback in project["callbackFunctions"]}
    assert 'profile = String(split(profile_value' in callbacks["SubmitPressed"]
    assert 'app.StatusLabel.Text = String(strip(read(' in callbacks["SubmitPressed"]
    assert "Cmd(String.(args))" in callbacks["SubmitPressed"]
    assert "controller_option = findfirst" in callbacks["ProfileChanged"]
    assert "app.ControllerDropDown.Items[controller_option]" in callbacks["ProfileChanged"]
