module MoSimModelStudioApp
    # Default loaded module
    using TyAppDesigner
    using ObjectOriented

    # User loaded module and file
    using Dates
    using TyPlot

    @oodef mutable struct App

        # Properties that correspond to app components
        UIFigure::TyAppDesigner.Figure = TyAppDesigner.create_figure()
        TitleLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
        ControllerDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
        VehicleDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
        WindField::TyAppDesigner.NumericEditField = TyAppDesigner.create_numericeditfield()
        PreviewButton::TyAppDesigner.Button = TyAppDesigner.create_button()
        SubmitButton::TyAppDesigner.Button = TyAppDesigner.create_button()
        SysplorerButton::TyAppDesigner.Button = TyAppDesigner.create_button()
        ResultButton::TyAppDesigner.Button = TyAppDesigner.create_button()
        StatusLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
        UIAxes::TyAppDesigner.UIAxes = TyAppDesigner.create_uiaxes()

        # Appinfo
        Appname::Module = @__MODULE__
        Appfile::String = @__FILE__
        Environment::String = "designer"

        # Code that executes after component creation

        # User custom functions


        # User custom properties


        # Callbacks that handle component events

        # ControllerChanged function:ControllerDropDown
        function ControllerChanged(app,event)
            selected = app.ControllerDropDown.Value
            accepted = ["px4ctrl", "cascade_pid", "gain_scheduled_pid", "fuzzy_pid", "neural_pid"]
            if selected in accepted
                app.LastController = selected
                app.StatusLabel.Text = "Controller accepted: " * selected
            else
                app.StatusLabel.Text = "Controller unavailable. Select an accepted controller before creating a request."
            end
        end

        # VehicleChanged function:VehicleDropDown
        function VehicleChanged(app,event)
            selected = app.VehicleDropDown.Value
            if selected == "3"
                app.LastVehicleCount = selected
                app.StatusLabel.Text = "Three-UAV profile is available."
            else
                app.StatusLabel.Text = "UAV count unavailable. Select 3 before creating a request."
            end
        end

        # PreviewPressed function:PreviewButton
        function PreviewPressed(app,event)
            wind = app.WindField.Value
            t = collect(0.0:0.1:10.0)
            response = @. exp(-0.15 * t) * sin(1.8 * t) + 0.02 * wind
            TyAppDesigner.plot(app.UIAxes, t, response)
            TyAppDesigner.title(app.UIAxes, "Bounded preview")
            TyAppDesigner.xlabel(app.UIAxes, "Time (s)")
            TyAppDesigner.ylabel(app.UIAxes, "Normalized response")
            app.StatusLabel.Text = "Preview updated. This is a UI capability plot, not controller evidence."
        end

        # SubmitPressed function:SubmitButton
        function SubmitPressed(app,event)
            gate_open, gate_message = app.request_gate()
            if !gate_open
                app.StatusLabel.Text = gate_message
                return
            end
            path = app.write_request("prepare_run")
            app.StatusLabel.Text = "Orchestrator request created:\n" * path
        end

        # SysplorerPressed function:SysplorerButton
        function SysplorerPressed(app,event)
            gate_open, gate_message = app.request_gate()
            if !gate_open
                app.StatusLabel.Text = gate_message
                return
            end
            path = app.write_request("open_model_context")
            app.StatusLabel.Text = "Sysplorer request created:\n" * path
        end

        # ResultPressed function:ResultButton
        function ResultPressed(app,event)
            gate_open, gate_message = app.request_gate()
            if !gate_open
                app.StatusLabel.Text = gate_message
                return
            end
            path = app.write_request("open_result_viewer")
            app.StatusLabel.Text = "Result-viewer request created:\n" * path
        end

        # Create UIFigure and components
        function createComponents(app)
            # Create UIFigure
            app.UIFigure = TyAppDesigner.uifigure(Visible=false)
            app.UIFigure.Position = [100,100,980,620]
            app.UIFigure.Name = raw"MoSim Model Studio"

            # Create TitleLabel
            app.TitleLabel = TyAppDesigner.uilabel(app.UIFigure)
            app.TitleLabel.Position = [30,24,920,36]
            app.TitleLabel.FontSize = 22
            app.TitleLabel.FontWeight = raw"bold"
            app.TitleLabel.Text = raw"MoSim Model Studio"

            # Create ControllerDropDown
            app.ControllerDropDown = TyAppDesigner.uidropdown(app.UIFigure)
            app.ControllerDropDown.Position = [30,90,410,32]
            app.ControllerDropDown.Label = raw"Controller"
            app.ControllerDropDown.Items = [raw"px4ctrl",raw"cascade_pid",raw"gain_scheduled_pid",raw"fuzzy_pid",raw"neural_pid",raw"pid_indi [disabled: runtime evidence pending]",raw"nmpc_outer [disabled: runtime evidence pending]"]
            app.ControllerDropDown.Value = raw"px4ctrl"
            app.ControllerDropDown.ValueChangedFcn = raw"ControllerChanged"

            # Create VehicleDropDown
            app.VehicleDropDown = TyAppDesigner.uidropdown(app.UIFigure)
            app.VehicleDropDown.Position = [30,145,410,32]
            app.VehicleDropDown.Label = raw"UAV count"
            app.VehicleDropDown.Items = [raw"3",raw"4 [disabled: scale gate pending]",raw"5 [disabled: scale gate pending]",raw"6 [disabled: scale gate pending]",raw"7 [disabled: scale gate pending]",raw"8 [disabled: scale gate pending]",raw"9 [disabled: scale gate pending]"]
            app.VehicleDropDown.Value = raw"3"
            app.VehicleDropDown.ValueChangedFcn = raw"VehicleChanged"

            # Create WindField
            app.WindField = TyAppDesigner.uinumericeditfield(app.UIFigure)
            app.WindField.Position = [30,200,410,32]
            app.WindField.Limits = [0,20]
            app.WindField.Label = raw"Wind speed (m/s)"
            app.WindField.Value = 0

            # Create PreviewButton
            app.PreviewButton = TyAppDesigner.uibutton(app.UIFigure)
            app.PreviewButton.Position = [30,270,190,36]
            app.PreviewButton.Text = raw"Preview"
            app.PreviewButton.ButtonPushedFcn = raw"PreviewPressed"

            # Create SubmitButton
            app.SubmitButton = TyAppDesigner.uibutton(app.UIFigure)
            app.SubmitButton.Position = [250,270,190,36]
            app.SubmitButton.Text = raw"Prepare run"
            app.SubmitButton.ButtonPushedFcn = raw"SubmitPressed"

            # Create SysplorerButton
            app.SysplorerButton = TyAppDesigner.uibutton(app.UIFigure)
            app.SysplorerButton.Position = [30,326,190,36]
            app.SysplorerButton.Text = raw"Open model"
            app.SysplorerButton.ButtonPushedFcn = raw"SysplorerPressed"

            # Create ResultButton
            app.ResultButton = TyAppDesigner.uibutton(app.UIFigure)
            app.ResultButton.Position = [250,326,190,36]
            app.ResultButton.Text = raw"Open result"
            app.ResultButton.ButtonPushedFcn = raw"ResultPressed"

            # Create StatusLabel
            app.StatusLabel = TyAppDesigner.uilabel(app.UIFigure)
            app.StatusLabel.Position = [30,405,410,165]
            app.StatusLabel.WordWrap = true
            app.StatusLabel.Text = raw"Ready. Disabled options remain visible and are rejected by the capability gate."

            # Create UIAxes
            app.UIAxes = TyAppDesigner.uiaxes(app.UIFigure)
            app.UIAxes.Position = [485,90,455,480]

            # Show the figure after all components are created
            app.UIFigure.Visible= true
        end

        # App creation
        function initApp(app)
            # Create UIFigure and components
            app.createComponents()

            # Register the app with App Designer
            TyAppDesigner.registerApp(app, app.UIFigure)

            return app
        end

        # App deletion
        function delete(app)
            # Delete UIFigure when app is deleted
            TyAppDesigner.delete(app, app.UIFigure)
        end
    end

    # Create an APP instance
    Instance = App().initApp()
end