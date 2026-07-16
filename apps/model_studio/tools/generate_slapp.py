#!/usr/bin/env python3
"""Generate the native Syslab APP Designer project from the reviewed Julia source."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "app.jl"
NATIVE_DIR = ROOT / "native_app"
NATIVE_SOURCE = NATIVE_DIR / "app.jl"
OUTPUT = NATIVE_DIR / "MoSimModelStudioApp.slapp"
FIGURE_ID = "mosim-model-studio-figure"


def callback_body(source: str) -> str:
    return textwrap.indent(textwrap.dedent(source).strip(), "            ")


def function_block(source: str) -> str:
    return textwrap.indent(textwrap.dedent(source).strip(), "        ")


def request_callback_body(action: str, success_prefix: str) -> str:
    template = r'''
    controller = app.ControllerDropDown.Value
    vehicle_count = app.VehicleDropDown.Value
    accepted = ["px4ctrl", "cascade_pid", "gain_scheduled_pid", "fuzzy_pid", "neural_pid"]
    if !(controller in accepted)
        app.StatusLabel.Text = "Request blocked. The selected controller has no accepted runtime gate."
        return
    end
    if vehicle_count != "3"
        app.StatusLabel.Text = "Request blocked. UAV counts 4-9 require an individual scale gate."
        return
    end
    action = "__ACTION__"
    project_root = normpath(joinpath(@__DIR__, "..", "..", ".."))
    request_dir = joinpath(project_root, "Results", "ui_platform", "model_studio_requests")
    mkpath(request_dir)
    stamp = Dates.format(now(), "yyyymmdd_HHMMSS_sss")
    created_at = Dates.format(now(), "yyyy-mm-ddTHH:MM:SS.sss")
    request_path = joinpath(request_dir, stamp * "_" * action * ".json")
    payload = """{
      \"schema\": \"mosim.model_studio.request.v1\",
      \"action\": \"$action\",
      \"controller_id\": \"$controller\",
      \"vehicle_count\": 3,
      \"wind_speed_mps\": $(app.WindField.Value),
      \"created_at_local\": \"$created_at\",
      \"status\": \"requested\"
    }
    """
    open(request_path, "w") do io
        write(io, payload)
    end
    app.StatusLabel.Text = "__SUCCESS__:\n" * request_path
    '''
    source = template.replace("__ACTION__", action).replace("__SUCCESS__", success_prefix)
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
    accepted = ["px4ctrl", "cascade_pid", "gain_scheduled_pid", "fuzzy_pid", "neural_pid"]
    controllers = accepted + [
        "pid_indi [disabled: runtime evidence pending]",
        "nmpc_outer [disabled: runtime evidence pending]",
    ]
    vehicles = ["3"] + [f"{count} [disabled: scale gate pending]" for count in range(4, 10)]
    source = SOURCE.read_text(encoding="utf-8")
    children = [
        label("title-label", "TitleLabel", "MoSim Model Studio", [30, 24, 920, 36], fontSize=22, fontWeight="bold"),
        dropdown("controller-dropdown", "ControllerDropDown", "Controller", controllers, "px4ctrl", "ControllerChanged", [30, 90, 410, 32]),
        dropdown("vehicle-dropdown", "VehicleDropDown", "UAV count", vehicles, "3", "VehicleChanged", [30, 145, 410, 32]),
        numeric_field("wind-field", "WindField", "Wind speed (m/s)", [30, 200, 410, 32]),
        button("preview-button", "PreviewButton", "Preview", "PreviewPressed", [30, 270, 190, 36]),
        button("submit-button", "SubmitButton", "Prepare run", "SubmitPressed", [250, 270, 190, 36]),
        button("model-button", "SysplorerButton", "Open model", "SysplorerPressed", [30, 326, 190, 36]),
        button("result-button", "ResultButton", "Open result", "ResultPressed", [250, 326, 190, 36]),
        label(
            "status-label",
            "StatusLabel",
            "Ready. Disabled options remain visible and are rejected by the capability gate.",
            [30, 405, 410, 165],
            verticalAlignment="top",
            wordWrap=True,
        ),
        axes(),
    ]
    callbacks = [
        {
            "name": "ControllerChanged",
            "code": callback_body(
                """
                selected = app.ControllerDropDown.Value
                accepted = ["px4ctrl", "cascade_pid", "gain_scheduled_pid", "fuzzy_pid", "neural_pid"]
                if selected in accepted
                    app.StatusLabel.Text = "Controller accepted: " * selected
                else
                    app.StatusLabel.Text = "Controller unavailable. Select an accepted controller before creating a request."
                end
                """
            ),
        },
        {
            "name": "VehicleChanged",
            "code": callback_body(
                """
                selected = app.VehicleDropDown.Value
                if selected == "3"
                    app.StatusLabel.Text = "Three-UAV profile is available."
                else
                    app.StatusLabel.Text = "UAV count unavailable. Select 3 before creating a request."
                end
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
            "code": request_callback_body("prepare_run", "Orchestrator request created"),
        },
        {
            "name": "SysplorerPressed",
            "code": request_callback_body("open_model_context", "Sysplorer request created"),
        },
        {
            "name": "ResultPressed",
            "code": request_callback_body("open_result_viewer", "Result-viewer request created"),
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
    NATIVE_SOURCE.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    OUTPUT.write_text(json.dumps(build_project(), ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
