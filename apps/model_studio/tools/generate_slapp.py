#!/usr/bin/env python3
"""Generate the native Syslab APP Designer project from the reviewed Julia source."""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "app.jl"
NATIVE_DIR = ROOT / "native_app"
NATIVE_SOURCE = NATIVE_DIR / "app.jl"
OUTPUT = NATIVE_DIR / "MoSimModelStudioApp.slapp"
FIGURE_ID = "mosim-model-studio-figure"
PROJECT_ROOT = ROOT.parents[1]
CATALOG_EXPORTER = PROJECT_ROOT / "Scripts" / "ui" / "export_model_studio_catalog.py"


def callback_body(source: str) -> str:
    return textwrap.indent(textwrap.dedent(source).strip(), "            ")


def function_block(source: str) -> str:
    return textwrap.indent(textwrap.dedent(source).strip(), "        ")


def load_catalog() -> dict:
    completed = subprocess.run(
        [sys.executable, str(CATALOG_EXPORTER), "--format", "json"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def julia_string(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def profile_bindings(catalog: dict) -> str:
    rows = []
    for profile in catalog["profiles"]:
        rows.append(
            "    "
            + julia_string(profile["profile_id"])
            + " => ("
            + ", ".join(
                [
                    julia_string(profile["profile_path"]),
                    julia_string(profile["controller_id"]),
                    julia_string(profile["vehicle_count"]),
                    "true" if profile["enabled"] else "false",
                    julia_string(profile["reason_code"]),
                    "true" if profile["runtime_ready"] else "false",
                ]
            )
            + "),"
        )
    return "Dict(\n" + "\n".join(rows) + "\n)"


def request_callback_body(action: str, catalog: dict) -> str:
    bindings = profile_bindings(catalog)
    template = r'''
    action = "__ACTION__"
    project_root = get(ENV, "MOSIM_PROJECT_ROOT", __PROJECT_ROOT__)
    client = joinpath(project_root, "Scripts", "ui", "orchestrator_client.py")
    try
    profile_value = app.ProfileDropDown.Value
    controller_value = app.ControllerDropDown.Value
    vehicle_value = app.VehicleDropDown.Value
    if occursin("[disabled:", profile_value) || occursin("[disabled:", controller_value) || occursin("[disabled:", vehicle_value)
        app.StatusLabel.Text = "false\tselection_gate_rejected"
        return
    end
    profile = String(split(profile_value, " [disabled:"; limit=2)[1])
    controller = String(split(controller_value, " [disabled:"; limit=2)[1])
    vehicle = String(split(vehicle_value, " [disabled:"; limit=2)[1])
    bindings = __BINDINGS__
    if action == "prepare_run"
        if !haskey(bindings, profile)
            app.StatusLabel.Text = "false\tprofile_not_found"
            return
        end
        profile_path, expected_controller, expected_vehicle, enabled, reason, runtime_ready = bindings[profile]
        if !enabled || controller != expected_controller || vehicle != expected_vehicle
            app.StatusLabel.Text = "false\tprofile_selection_mismatch"
            return
        end
        args = [
            "python", client, "prepare_run",
            "--profile-path", profile_path,
            "--controller-id", controller,
            "--vehicle-count", vehicle,
            "--wind-speed-mps", string(app.WindField.Value),
            "--format", "tsv",
        ]
    else
        args = ["python", client, action, "--format", "tsv"]
    end
    app.StatusLabel.Text = String(strip(read(ignorestatus(Cmd(args)), String)))
    catch err
        app.StatusLabel.Text = "false\tcallback_exception\t" * sprint(showerror, err)
    end
    '''
    source = (
        template.replace("__ACTION__", action)
        .replace("__BINDINGS__", bindings)
        .replace("__PROJECT_ROOT__", julia_string(PROJECT_ROOT))
    )
    return callback_body(source)


def common(component_id: str, component_type: str, variable: str, position: list[int]) -> dict:
    return {
        "id": component_id,
        "pid": FIGURE_ID,
        "state": {"position": position},
        "callbackFcns": {},
        "type": component_type,
        "visible": True,
        "enable": True,
        "tooltip": "",
        "contextMenu": [],
        "position": position,
        "interruptible": False,
        "busyAction": "queue",
        "tag": "",
        "variableName": variable,
    }


def label(component_id: str, variable: str, text: str, position: list[int], **overrides) -> dict:
    component = common(component_id, "label", variable, position)
    component.update(
        {
            "text": text,
            "interpreter": "none",
            "horizontalAlignment": "left",
            "verticalAlignment": "center",
            "wordWrap": False,
            "fontName": "Helvetica",
            "fontSize": 12,
            "fontWeight": "normal",
            "fontAngle": "normal",
            "fontColor": [0, 0, 0],
            "backgroundColor": [],
        }
    )
    component.update(overrides)
    component["state"].update(
        {key: value for key, value in overrides.items() if key in {"fontSize", "fontWeight", "wordWrap"}}
    )
    component["state"]["text"] = text
    return component


def dropdown(
    component_id: str,
    variable: str,
    display_label: str,
    items: list[str],
    value: str,
    callback: str,
    position: list[int],
) -> dict:
    component = common(component_id, "dropdown", variable, position)
    component.update(
        {
            "label": display_label,
            "value": value,
            "items": items,
            "itemsData": [],
            "placeholder": "",
            "fontName": "Helvetica",
            "fontSize": 12,
            "fontWeight": "normal",
            "fontAngle": "normal",
            "fontColor": [0, 0, 0],
            "backgroundColor": [1, 1, 1],
            "editable": False,
            "valueChangedFcn": callback,
        }
    )
    component["callbackFcns"] = {"valueChangedFcn": callback}
    component["state"].update(
        {"label": display_label, "items": items, "value": value, "valueChangedFcn": callback}
    )
    return component


def numeric_field(component_id: str, variable: str, display_label: str, position: list[int]) -> dict:
    component = common(component_id, "numericeditfield", variable, position)
    component.update(
        {
            "label": display_label,
            "value": 0.0,
            "limits": [0.0, 20.0],
            "placeholder": "",
            "horizontalAlignment": "right",
            "fontName": "Helvetica",
            "fontSize": 12,
            "fontWeight": "normal",
            "fontAngle": "normal",
            "fontColor": [0, 0, 0],
            "backgroundColor": [1, 1, 1],
            "editable": True,
            "valueChangedFcn": "",
        }
    )
    component["state"].update({"label": display_label, "value": 0.0})
    return component


def button(component_id: str, variable: str, text: str, callback: str, position: list[int]) -> dict:
    component = common(component_id, "button", variable, position)
    component.update(
        {
            "text": text,
            "wordWrap": False,
            "horizontalAlignment": "center",
            "verticalAlignment": "center",
            "icon": "",
            "iconAlignment": "left",
            "fontName": "Helvetica",
            "fontSize": 12,
            "fontWeight": "normal",
            "fontAngle": "normal",
            "fontColor": [0, 0, 0],
            "backgroundColor": [0.94, 0.94, 0.94],
            "buttonPushedFcn": callback,
        }
    )
    component["callbackFcns"] = {"buttonPushedFcn": callback}
    component["state"].update({"text": text, "buttonPushedFcn": callback})
    return component


def axes() -> dict:
    position = [485, 90, 455, 480]
    component = common("preview-axes", "uiaxes", "UIAxes", position)
    component.update(
        {
            "title": "Preview",
            "data": [],
            "xLabel": "Time (s)",
            "yLabel": "Normalized response",
            "legend": False,
            "grid": False,
            "hold": False,
            "xLim": [0, 1],
            "xLimMode": "auto",
            "yLim": [0, 1],
            "yLimMode": "auto",
            "buttonDownFcn": "",
        }
    )
    return component


def build_project() -> dict:
    catalog = load_catalog()
    profiles = [
        profile["profile_id"]
        if profile["enabled"]
        else f'{profile["profile_id"]} [disabled: {profile["reason_code"]}]'
        for profile in catalog["profiles"]
    ]
    controllers = [
        controller["controller_id"]
        if controller["enabled"]
        else f'{controller["controller_id"]} [disabled: {controller["reason_code"]}]'
        for controller in catalog["controllers"]
    ]
    vehicles = [
        str(vehicle["vehicle_count"])
        if vehicle["enabled"]
        else f'{vehicle["vehicle_count"]} [disabled: {vehicle["reason_code"]}]'
        for vehicle in catalog["vehicles"]
    ]
    preferred_profile = next(
        (
            profile["profile_id"]
            for profile in catalog["profiles"]
            if profile["profile_id"] == "px4ctrl_figure8_baseline_v1" and profile["enabled"]
        ),
        next(profile["profile_id"] for profile in catalog["profiles"] if profile["enabled"]),
    )
    selected = next(profile for profile in catalog["profiles"] if profile["profile_id"] == preferred_profile)
    source = SOURCE.read_text(encoding="utf-8")
    children = [
        label("title-label", "TitleLabel", "MoSim Model Studio", [30, 24, 920, 36], fontSize=22, fontWeight="bold"),
        dropdown("profile-dropdown", "ProfileDropDown", "Experiment profile", profiles, preferred_profile, "ProfileChanged", [30, 82, 410, 32]),
        dropdown("controller-dropdown", "ControllerDropDown", "Controller", controllers, selected["controller_id"], "ControllerChanged", [30, 130, 410, 32]),
        dropdown("vehicle-dropdown", "VehicleDropDown", "UAV count", vehicles, str(selected["vehicle_count"]), "VehicleChanged", [30, 178, 410, 32]),
        numeric_field("wind-field", "WindField", "Wind speed (m/s)", [30, 226, 410, 32]),
        button("refresh-button", "RefreshButton", "Refresh capability", "RefreshPressed", [30, 282, 190, 36]),
        button("preview-button", "PreviewButton", "Preview", "PreviewPressed", [250, 282, 190, 36]),
        button("submit-button", "SubmitButton", "Prepare run", "SubmitPressed", [30, 334, 190, 36]),
        button("model-button", "SysplorerButton", "Open model", "SysplorerPressed", [250, 334, 190, 36]),
        button("result-button", "ResultButton", "Open result", "ResultPressed", [30, 386, 190, 36]),
        label(
            "status-label",
            "StatusLabel",
            "Ready. Disabled options remain visible and are rejected by the capability gate.",
            [30, 442, 410, 128],
            verticalAlignment="top",
            wordWrap=True,
        ),
        axes(),
    ]
    callbacks = [
        {
            "name": "ProfileChanged",
            "code": callback_body(
                f"""
                selected = split(app.ProfileDropDown.Value, " [disabled:"; limit=2)[1]
                bindings = {profile_bindings(catalog)}
                if !haskey(bindings, selected)
                    app.StatusLabel.Text = "Profile not found in current catalog."
                    return
                end
                profile_path, controller, vehicle, enabled, reason, runtime_ready = bindings[selected]
                clean(item) = String(split(item, " [disabled:"; limit=2)[1])
                controller_option = findfirst(item -> clean(item) == controller, app.ControllerDropDown.Items)
                vehicle_option = findfirst(item -> clean(item) == vehicle, app.VehicleDropDown.Items)
                controller_option !== nothing && (app.ControllerDropDown.Value = app.ControllerDropDown.Items[controller_option])
                vehicle_option !== nothing && (app.VehicleDropDown.Value = app.VehicleDropDown.Items[vehicle_option])
                app.StatusLabel.Text = enabled ? "Profile accepted; " * (runtime_ready ? "runtime ready" : "runtime gate pending") : "Profile unavailable: " * reason
                """
            ),
        },
        {
            "name": "ControllerChanged",
            "code": callback_body(
                """
                selected = app.ControllerDropDown.Value
                app.StatusLabel.Text = occursin("[disabled:", selected) ? "Controller unavailable." : "Controller selected: " * selected
                """
            ),
        },
        {
            "name": "VehicleChanged",
            "code": callback_body(
                """
                selected = app.VehicleDropDown.Value
                app.StatusLabel.Text = occursin("[disabled:", selected) ? "UAV count unavailable." : "UAV count selected: " * selected
                """
            ),
        },
        {
            "name": "RefreshPressed",
            "code": callback_body(
                """
                app.StatusLabel.Text = "Capability catalog is frozen into this APP package. Rebuild the APP to refresh it."
                """
            ),
        },
        {
            "name": "PreviewPressed",
            "code": callback_body(
                """
                wind = app.WindField.Value
                t = collect(0.0:0.1:10.0)
                response = @. exp(-0.15 * t) * sin(1.8 * t) + 0.02 * wind
                TyAppDesigner.plot(app.UIAxes, t, response)
                TyAppDesigner.title(app.UIAxes, "Bounded preview")
                TyAppDesigner.xlabel(app.UIAxes, "Time (s)")
                TyAppDesigner.ylabel(app.UIAxes, "Normalized response")
                app.StatusLabel.Text = "Preview updated. This is a UI capability plot, not controller evidence."
                """
            ),
        },
        {
            "name": "SubmitPressed",
            "code": request_callback_body("prepare_run", catalog),
        },
        {
            "name": "SysplorerPressed",
            "code": request_callback_body("open_model_context", catalog),
        },
        {
            "name": "ResultPressed",
            "code": request_callback_body("get_result_packet", catalog),
        },
    ]
    return {
        "name": "MoSimModelStudioApp",
        "callbackFunctions": callbacks,
        "customPrivateFunctions": [],
        "customPublicFunctions": [],
        "customPrivateProperties": [],
        "customPublicProperties": [],
        "userLoadedModule": "    using Dates\n    using TyPlot",
        "figure": {
            "id": FIGURE_ID,
            "state": {},
            "callbackFcns": {},
            "type": "figure",
            "position": [100, 100, 980, 620],
            "name": "MoSim Model Studio",
            "color": [0.94, 0.94, 0.94],
            "tag": "",
            "children": children,
            "visible": True,
            "variableName": "UIFigure",
        },
        "info": {
            "type": "app",
            "name": "MoSim Model Studio",
            "version": "0.1.0",
            "author": "MoSim",
            "description": "Native experiment selection and audited orchestration request surface.",
            "icon": "",
            "startupFcn": "",
        },
        "code": source,
    }


def main() -> None:
    NATIVE_DIR.mkdir(parents=True, exist_ok=True)
    NATIVE_SOURCE.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    OUTPUT.write_text(
        json.dumps(build_project(), ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
