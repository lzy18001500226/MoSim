module MoSimModelStudio

using Dates
using ObjectOriented
using TyAppDesigner
using TyPlot

const ACCEPTED_CONTROLLERS = [
    "px4ctrl",
    "cascade_pid",
    "gain_scheduled_pid",
    "fuzzy_pid",
    "neural_pid",
]

const CONTROLLER_OPTIONS = [
    ACCEPTED_CONTROLLERS...,
    "pid_indi [disabled: runtime evidence pending]",
    "nmpc_outer [disabled: runtime evidence pending]",
]

const UAV_OPTIONS = [
    "3",
    "4 [disabled: scale gate pending]",
    "5 [disabled: scale gate pending]",
    "6 [disabled: scale gate pending]",
    "7 [disabled: scale gate pending]",
    "8 [disabled: scale gate pending]",
    "9 [disabled: scale gate pending]",
]

@oodef mutable struct App
    UIFigure::TyAppDesigner.Figure = TyAppDesigner.create_figure()
    TitleLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    ControllerDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    VehicleDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    WindField::TyAppDesigner.NumericEditField = TyAppDesigner.create_numericeditfield()
    PreviewButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    SubmitButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    SysplorerButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    ResultButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    UIAxes::TyAppDesigner.UIAxes = TyAppDesigner.create_uiaxes()
    StatusLabel::TyAppDesigner.Label = TyAppDesigner.create_label()

    Appname::Module = @__MODULE__
    Appfile::String = @__FILE__
    ProjectRoot::String = normpath(joinpath(@__DIR__, "..", "..", ".."))
    function ControllerChanged(app, event)
        selected = app.ControllerDropDown.Value
        if selected in ACCEPTED_CONTROLLERS
            app.StatusLabel.Text = "Controller accepted: " * selected
        else
            app.StatusLabel.Text = "Controller unavailable. Select an accepted controller before creating a request."
        end
    end

    function VehicleChanged(app, event)
        selected = app.VehicleDropDown.Value
        if selected == "3"
            app.StatusLabel.Text = "Three-UAV profile is available."
        else
            app.StatusLabel.Text = "UAV count unavailable. Select 3 before creating a request."
        end
    end

    function PreviewPressed(app, event)
        wind = app.WindField.Value
        t = collect(0.0:0.1:10.0)
        response = @. exp(-0.15 * t) * sin(1.8 * t) + 0.02 * wind
        TyAppDesigner.plot(app.UIAxes, t, response)
        TyAppDesigner.title(app.UIAxes, "Bounded preview")
        TyAppDesigner.xlabel(app.UIAxes, "Time (s)")
        TyAppDesigner.ylabel(app.UIAxes, "Normalized response")
        app.StatusLabel.Text = "Preview updated. This is a UI capability plot, not controller evidence."
    end

    function create_request(app, action)
        controller = app.ControllerDropDown.Value
        vehicle_count = app.VehicleDropDown.Value
        if !(controller in ACCEPTED_CONTROLLERS)
            app.StatusLabel.Text = "Request blocked. The selected controller has no accepted runtime gate."
            return nothing
        end
        if vehicle_count != "3"
            app.StatusLabel.Text = "Request blocked. UAV counts 4-9 require an individual scale gate."
            return nothing
        end
        request_dir = joinpath(app.ProjectRoot, "Results", "ui_platform", "model_studio_requests")
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
        return request_path
    end

    function SubmitPressed(app, event)
        path = app.create_request("prepare_run")
        path === nothing && return
        app.StatusLabel.Text = "Orchestrator request created:\n" * path
    end

    function SysplorerPressed(app, event)
        path = app.create_request("open_model_context")
        path === nothing && return
        app.StatusLabel.Text = "Sysplorer request created:\n" * path
    end

    function ResultPressed(app, event)
        path = app.create_request("open_result_viewer")
        path === nothing && return
        app.StatusLabel.Text = "Result-viewer request created:\n" * path
    end

    function createComponents(app)
        app.UIFigure = TyAppDesigner.uifigure(Visible=false)
        app.UIFigure.Position = [100, 100, 980, 620]
        app.UIFigure.Name = "MoSim Model Studio"

        app.TitleLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.TitleLabel.Position = [30, 24, 920, 36]
        app.TitleLabel.Text = "MoSim Model Studio"
        app.TitleLabel.FontSize = 22
        app.TitleLabel.FontWeight = "bold"
        app.TitleLabel.HorizontalAlignment = "left"

        app.ControllerDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.ControllerDropDown.Position = [30, 90, 410, 32]
        app.ControllerDropDown.Label = "Controller"
        app.ControllerDropDown.Items = CONTROLLER_OPTIONS
        app.ControllerDropDown.Value = "px4ctrl"
        app.ControllerDropDown.ValueChangedFcn = "ControllerChanged"

        app.VehicleDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.VehicleDropDown.Position = [30, 145, 410, 32]
        app.VehicleDropDown.Label = "UAV count"
        app.VehicleDropDown.Items = UAV_OPTIONS
        app.VehicleDropDown.Value = "3"
        app.VehicleDropDown.ValueChangedFcn = "VehicleChanged"

        app.WindField = TyAppDesigner.uinumericeditfield(app.UIFigure)
        app.WindField.Position = [30, 200, 410, 32]
        app.WindField.Label = "Wind speed (m/s)"
        app.WindField.Value = 0.0
        app.WindField.Limits = [0.0, 20.0]

        app.PreviewButton = TyAppDesigner.uibutton(app.UIFigure)
        app.PreviewButton.Position = [30, 270, 190, 36]
        app.PreviewButton.Text = "Preview"
        app.PreviewButton.ButtonPushedFcn = "PreviewPressed"

        app.SubmitButton = TyAppDesigner.uibutton(app.UIFigure)
        app.SubmitButton.Position = [250, 270, 190, 36]
        app.SubmitButton.Text = "Prepare run"
        app.SubmitButton.ButtonPushedFcn = "SubmitPressed"

        app.SysplorerButton = TyAppDesigner.uibutton(app.UIFigure)
        app.SysplorerButton.Position = [30, 326, 190, 36]
        app.SysplorerButton.Text = "Open model"
        app.SysplorerButton.ButtonPushedFcn = "SysplorerPressed"

        app.ResultButton = TyAppDesigner.uibutton(app.UIFigure)
        app.ResultButton.Position = [250, 326, 190, 36]
        app.ResultButton.Text = "Open result"
        app.ResultButton.ButtonPushedFcn = "ResultPressed"

        app.StatusLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.StatusLabel.Position = [30, 405, 410, 165]
        app.StatusLabel.Text = "Ready. Disabled options remain visible and are rejected by the capability gate."
        app.StatusLabel.HorizontalAlignment = "left"
        app.StatusLabel.VerticalAlignment = "top"
        app.StatusLabel.WordWrap = true

        app.UIAxes = TyAppDesigner.uiaxes(app.UIFigure)
        app.UIAxes.Position = [485, 90, 455, 480]

        app.UIFigure.Visible = true
    end

    function initApp(app)
        app.createComponents()
        TyAppDesigner.registerApp(app, app.UIFigure)
        return app
    end

    function delete(app)
        TyAppDesigner.delete(app, app.UIFigure)
    end
end

Instance = App().initApp()

end
