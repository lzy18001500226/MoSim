module MoSimModelStudio

using Dates
using ObjectOriented
using TyAppDesigner
using TyPlot

function discover_project_root()
    candidates = String[]
    haskey(ENV, "MOSIM_PROJECT_ROOT") && push!(candidates, ENV["MOSIM_PROJECT_ROOT"])
    push!(candidates, normpath(joinpath(@__DIR__, "..", "..", "..")))
    push!(candidates, pwd())
    for initial in candidates
        candidate = abspath(initial)
        while true
            isfile(joinpath(candidate, "AGENTS.md")) && return candidate
            parent = dirname(candidate)
            parent == candidate && break
            candidate = parent
        end
    end
    error("MoSim project root not found. Set MOSIM_PROJECT_ROOT before starting the APP.")
end

@oodef mutable struct App
    UIFigure::TyAppDesigner.Figure = TyAppDesigner.create_figure()
    TitleLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    ProfileDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    ControllerDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    VehicleDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    WindField::TyAppDesigner.NumericEditField = TyAppDesigner.create_numericeditfield()
    RefreshButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    PreviewButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    SubmitButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    SysplorerButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    ResultButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    UIAxes::TyAppDesigner.UIAxes = TyAppDesigner.create_uiaxes()
    StatusLabel::TyAppDesigner.Label = TyAppDesigner.create_label()

    Appname::Module = @__MODULE__
    Appfile::String = @__FILE__
    ProjectRoot::String = discover_project_root()

    function catalog_rows(app)
        exporter = joinpath(app.ProjectRoot, "Scripts", "ui", "export_model_studio_catalog.py")
        output = read(Cmd(["python", exporter, "--format", "tsv"]), String)
        return [split(line, '\t') for line in split(chomp(output), '\n') if !isempty(line)]
    end

    function clean_option(app, value)
        return String(split(value, " [disabled:"; limit=2)[1])
    end

    function refresh_catalog(app)
        rows = app.catalog_rows()
        profiles = String[]
        controllers = String[]
        vehicles = String[]
        for fields in rows
            if fields[1] == "PROFILE"
                push!(profiles, fields[6] == "true" ? fields[2] : fields[2] * " [disabled: " * fields[7] * "]")
            elseif fields[1] == "CONTROLLER"
                push!(controllers, fields[5] == "true" ? fields[2] : fields[2] * " [disabled: " * fields[6] * "]")
            elseif fields[1] == "VEHICLE"
                push!(vehicles, fields[3] == "true" ? fields[2] : fields[2] * " [disabled: " * fields[4] * "]")
            end
        end
        app.ProfileDropDown.Items = profiles
        app.ControllerDropDown.Items = controllers
        app.VehicleDropDown.Items = vehicles
        enabled_profiles = filter(item -> !occursin("[disabled:", item), profiles)
        if !isempty(enabled_profiles)
            app.ProfileDropDown.Value = enabled_profiles[1]
            app.ProfileChanged(nothing)
        end
        app.StatusLabel.Text = "Registry and Profile catalog refreshed."
    end

    function RefreshPressed(app, event)
        try
            app.refresh_catalog()
        catch err
            app.StatusLabel.Text = "Catalog refresh failed: " * sprint(showerror, err)
        end
    end

    function ProfileChanged(app, event)
        selected = app.clean_option(app.ProfileDropDown.Value)
        for fields in app.catalog_rows()
            if fields[1] == "PROFILE" && fields[2] == selected
                controller_option = findfirst(item -> app.clean_option(item) == fields[4], app.ControllerDropDown.Items)
                vehicle_option = findfirst(item -> app.clean_option(item) == fields[5], app.VehicleDropDown.Items)
                controller_option !== nothing && (app.ControllerDropDown.Value = app.ControllerDropDown.Items[controller_option])
                vehicle_option !== nothing && (app.VehicleDropDown.Value = app.VehicleDropDown.Items[vehicle_option])
                runtime = fields[8] == "true" ? "runtime ready" : "runtime gate pending"
                app.StatusLabel.Text = fields[6] == "true" ? "Profile accepted; " * runtime : "Profile unavailable: " * fields[7]
                return
            end
        end
        app.StatusLabel.Text = "Profile not found in current catalog."
    end

    function ControllerChanged(app, event)
        selected = app.ControllerDropDown.Value
        app.StatusLabel.Text = occursin("[disabled:", selected) ? "Controller unavailable." : "Controller selected: " * selected
    end

    function VehicleChanged(app, event)
        selected = app.VehicleDropDown.Value
        app.StatusLabel.Text = occursin("[disabled:", selected) ? "UAV count unavailable." : "UAV count selected: " * selected
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
        profile = app.clean_option(app.ProfileDropDown.Value)
        controller = app.clean_option(app.ControllerDropDown.Value)
        vehicle = app.clean_option(app.VehicleDropDown.Value)
        if occursin("[disabled:", app.ProfileDropDown.Value) || occursin("[disabled:", app.ControllerDropDown.Value) || occursin("[disabled:", app.VehicleDropDown.Value)
            return "false\tselection_gate_rejected"
        end
        client = joinpath(app.ProjectRoot, "Scripts", "ui", "orchestrator_client.py")
        if action == "prepare_run"
            profile_path = ""
            for fields in app.catalog_rows()
                if fields[1] == "PROFILE" && fields[2] == profile
                    profile_path = fields[3]
                    if fields[4] != controller || fields[5] != vehicle
                        return "false\tprofile_selection_mismatch"
                    end
                end
            end
            isempty(profile_path) && return "false\tprofile_not_found"
            args = [
                "python", client, "prepare_run",
                "--profile-path", profile_path,
                "--controller-id", controller,
                "--vehicle-count", vehicle,
                "--wind-speed-mps", string(app.WindField.Value),
                "--format", "tsv",
            ]
            return String(strip(read(ignorestatus(Cmd(String.(args))), String)))
        end
        return String(strip(read(ignorestatus(Cmd(["python", client, action, "--format", "tsv"])), String)))
    end

    function SubmitPressed(app, event)
        app.StatusLabel.Text = app.create_request("prepare_run")
    end

    function SysplorerPressed(app, event)
        app.StatusLabel.Text = app.create_request("open_model_context")
    end

    function ResultPressed(app, event)
        app.StatusLabel.Text = app.create_request("get_result_packet")
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

        app.ProfileDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.ProfileDropDown.Position = [30, 82, 410, 32]
        app.ProfileDropDown.Label = "Experiment profile"
        app.ProfileDropDown.Items = ["Loading catalog..."]
        app.ProfileDropDown.Value = "Loading catalog..."
        app.ProfileDropDown.ValueChangedFcn = "ProfileChanged"

        app.ControllerDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.ControllerDropDown.Position = [30, 130, 410, 32]
        app.ControllerDropDown.Label = "Controller"
        app.ControllerDropDown.Items = ["Loading catalog..."]
        app.ControllerDropDown.Value = "Loading catalog..."
        app.ControllerDropDown.ValueChangedFcn = "ControllerChanged"

        app.VehicleDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.VehicleDropDown.Position = [30, 178, 410, 32]
        app.VehicleDropDown.Label = "UAV count"
        app.VehicleDropDown.Items = ["Loading catalog..."]
        app.VehicleDropDown.Value = "Loading catalog..."
        app.VehicleDropDown.ValueChangedFcn = "VehicleChanged"

        app.WindField = TyAppDesigner.uinumericeditfield(app.UIFigure)
        app.WindField.Position = [30, 226, 410, 32]
        app.WindField.Label = "Wind speed (m/s)"
        app.WindField.Value = 0.0
        app.WindField.Limits = [0.0, 20.0]

        app.PreviewButton = TyAppDesigner.uibutton(app.UIFigure)
        app.RefreshButton = TyAppDesigner.uibutton(app.UIFigure)
        app.RefreshButton.Position = [30, 282, 190, 36]
        app.RefreshButton.Text = "Refresh capability"
        app.RefreshButton.ButtonPushedFcn = "RefreshPressed"

        app.PreviewButton.Position = [250, 282, 190, 36]
        app.PreviewButton.Text = "Preview"
        app.PreviewButton.ButtonPushedFcn = "PreviewPressed"

        app.SubmitButton = TyAppDesigner.uibutton(app.UIFigure)
        app.SubmitButton.Position = [30, 334, 190, 36]
        app.SubmitButton.Text = "Prepare run"
        app.SubmitButton.ButtonPushedFcn = "SubmitPressed"

        app.SysplorerButton = TyAppDesigner.uibutton(app.UIFigure)
        app.SysplorerButton.Position = [250, 334, 190, 36]
        app.SysplorerButton.Text = "Open model"
        app.SysplorerButton.ButtonPushedFcn = "SysplorerPressed"

        app.ResultButton = TyAppDesigner.uibutton(app.UIFigure)
        app.ResultButton.Position = [30, 386, 190, 36]
        app.ResultButton.Text = "Open result"
        app.ResultButton.ButtonPushedFcn = "ResultPressed"

        app.StatusLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.StatusLabel.Position = [30, 442, 410, 128]
        app.StatusLabel.Text = "Ready. Disabled options remain visible and are rejected by the capability gate."
        app.StatusLabel.HorizontalAlignment = "left"
        app.StatusLabel.VerticalAlignment = "top"
        app.StatusLabel.WordWrap = true

        app.UIAxes = TyAppDesigner.uiaxes(app.UIFigure)
        app.UIAxes.Position = [485, 90, 455, 480]

        app.refresh_catalog()
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
