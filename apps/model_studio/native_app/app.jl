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
        ProfileDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
        ControllerDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
        VehicleDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
        WindField::TyAppDesigner.NumericEditField = TyAppDesigner.create_numericeditfield()
        RefreshButton::TyAppDesigner.Button = TyAppDesigner.create_button()
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

        # ProfileChanged function:ProfileDropDown
        function ProfileChanged(app,event)
            selected = split(app.ProfileDropDown.Value, " [disabled:"; limit=2)[1]
                            bindings = Dict(
                "factory_l2_three_uav_swarm_formation_v1" => ("Config/profiles/experiments/factory_l2_three_uav_swarm_formation_v1.json", "px4ctrl", "3", true, "enabled", false),
                "fastlio_hybrid_z_figure8_v1" => ("Config/profiles/experiments/fastlio_hybrid_z_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "fastlio_independent_eval_figure8_v1" => ("Config/profiles/experiments/fastlio_independent_eval_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "fastlio_px4_ekf_ab_figure8_v1" => ("Config/profiles/experiments/fastlio_px4_ekf_ab_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "g10a_dfbc_smooth_robust_dob_figure8_v1" => ("Config/profiles/experiments/g10a_dfbc_smooth_robust_dob_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10a_dfbc_smooth_robust_no_dob_figure8_v1" => ("Config/profiles/experiments/g10a_dfbc_smooth_robust_no_dob_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_dfbc_smooth_robust_indi_figure8_v1" => ("Config/profiles/experiments/g10c_dfbc_smooth_robust_indi_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_dfbc_smooth_robust_no_indi_figure8_v1" => ("Config/profiles/experiments/g10c_dfbc_smooth_robust_no_indi_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_official_pid_indi_figure8_v1" => ("Config/profiles/experiments/g10c_official_pid_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g10c_official_pid_no_indi_figure8_v1" => ("Config/profiles/experiments/g10c_official_pid_no_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_bodyrate_figure8_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_bodyrate_figure8_v1.json", "dfbc_high_order_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1.json", "dfbc_high_order_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_figure8_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_figure8_v1.json", "dfbc_high_order_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_takeoff_hover_land_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_takeoff_hover_land_v1.json", "dfbc_high_order_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_bodyrate_figure8_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_bodyrate_figure8_v1.json", "dfbc_smooth_robust_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1.json", "dfbc_smooth_robust_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_figure8_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_takeoff_hover_land_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_takeoff_hover_land_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g9_dfbc_basic_figure8_v1" => ("Config/profiles/experiments/g9_dfbc_basic_figure8_v1.json", "dfbc_basic", "1", false, "controller_runtime_gate_pending", false),
                "g9_nmpc_outer_figure8_v1" => ("Config/profiles/experiments/g9_nmpc_outer_figure8_v1.json", "nmpc_outer", "1", false, "controller_runtime_gate_pending", false),
                "g9_official_pid_figure8_v1" => ("Config/profiles/experiments/g9_official_pid_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g9_pid_indi_figure8_v1" => ("Config/profiles/experiments/g9_pid_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g9_se3_basic_figure8_v1" => ("Config/profiles/experiments/g9_se3_basic_figure8_v1.json", "se3_basic", "1", false, "controller_runtime_gate_pending", false),
                "g9_smc_boundary_layer_figure8_v1" => ("Config/profiles/experiments/g9_smc_boundary_layer_figure8_v1.json", "smc_boundary_layer", "1", false, "controller_runtime_gate_pending", false),
                "px4ctrl_figure8_baseline_v1" => ("Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json", "px4ctrl", "1", true, "enabled", true),
                "px4ctrl_spiral_baseline_v1" => ("Config/profiles/experiments/px4ctrl_spiral_baseline_v1.json", "px4ctrl", "1", true, "enabled", false),
                "px4ctrl_step_baseline_v1" => ("Config/profiles/experiments/px4ctrl_step_baseline_v1.json", "px4ctrl", "1", true, "enabled", false),
                "px4ctrl_takeoff_hover_land_v1" => ("Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json", "px4ctrl", "1", true, "enabled", false),
            )
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
        end

        # ControllerChanged function:ControllerDropDown
        function ControllerChanged(app,event)
            selected = app.ControllerDropDown.Value
            app.StatusLabel.Text = occursin("[disabled:", selected) ? "Controller unavailable." : "Controller selected: " * selected
        end

        # VehicleChanged function:VehicleDropDown
        function VehicleChanged(app,event)
            selected = app.VehicleDropDown.Value
            app.StatusLabel.Text = occursin("[disabled:", selected) ? "UAV count unavailable." : "UAV count selected: " * selected
        end

        # RefreshPressed function:RefreshButton
        function RefreshPressed(app,event)
            app.StatusLabel.Text = "Capability catalog is frozen into this APP package. Rebuild the APP to refresh it."
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
            action = "prepare_run"
                project_root = get(ENV, "MOSIM_PROJECT_ROOT", "C:\\Users\\HP\\Desktop\\MoSim")
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
                bindings = Dict(
                "factory_l2_three_uav_swarm_formation_v1" => ("Config/profiles/experiments/factory_l2_three_uav_swarm_formation_v1.json", "px4ctrl", "3", true, "enabled", false),
                "fastlio_hybrid_z_figure8_v1" => ("Config/profiles/experiments/fastlio_hybrid_z_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "fastlio_independent_eval_figure8_v1" => ("Config/profiles/experiments/fastlio_independent_eval_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "fastlio_px4_ekf_ab_figure8_v1" => ("Config/profiles/experiments/fastlio_px4_ekf_ab_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "g10a_dfbc_smooth_robust_dob_figure8_v1" => ("Config/profiles/experiments/g10a_dfbc_smooth_robust_dob_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10a_dfbc_smooth_robust_no_dob_figure8_v1" => ("Config/profiles/experiments/g10a_dfbc_smooth_robust_no_dob_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_dfbc_smooth_robust_indi_figure8_v1" => ("Config/profiles/experiments/g10c_dfbc_smooth_robust_indi_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_dfbc_smooth_robust_no_indi_figure8_v1" => ("Config/profiles/experiments/g10c_dfbc_smooth_robust_no_indi_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_official_pid_indi_figure8_v1" => ("Config/profiles/experiments/g10c_official_pid_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g10c_official_pid_no_indi_figure8_v1" => ("Config/profiles/experiments/g10c_official_pid_no_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_bodyrate_figure8_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_bodyrate_figure8_v1.json", "dfbc_high_order_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1.json", "dfbc_high_order_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_figure8_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_figure8_v1.json", "dfbc_high_order_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_takeoff_hover_land_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_takeoff_hover_land_v1.json", "dfbc_high_order_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_bodyrate_figure8_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_bodyrate_figure8_v1.json", "dfbc_smooth_robust_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1.json", "dfbc_smooth_robust_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_figure8_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_takeoff_hover_land_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_takeoff_hover_land_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g9_dfbc_basic_figure8_v1" => ("Config/profiles/experiments/g9_dfbc_basic_figure8_v1.json", "dfbc_basic", "1", false, "controller_runtime_gate_pending", false),
                "g9_nmpc_outer_figure8_v1" => ("Config/profiles/experiments/g9_nmpc_outer_figure8_v1.json", "nmpc_outer", "1", false, "controller_runtime_gate_pending", false),
                "g9_official_pid_figure8_v1" => ("Config/profiles/experiments/g9_official_pid_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g9_pid_indi_figure8_v1" => ("Config/profiles/experiments/g9_pid_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g9_se3_basic_figure8_v1" => ("Config/profiles/experiments/g9_se3_basic_figure8_v1.json", "se3_basic", "1", false, "controller_runtime_gate_pending", false),
                "g9_smc_boundary_layer_figure8_v1" => ("Config/profiles/experiments/g9_smc_boundary_layer_figure8_v1.json", "smc_boundary_layer", "1", false, "controller_runtime_gate_pending", false),
                "px4ctrl_figure8_baseline_v1" => ("Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json", "px4ctrl", "1", true, "enabled", true),
                "px4ctrl_spiral_baseline_v1" => ("Config/profiles/experiments/px4ctrl_spiral_baseline_v1.json", "px4ctrl", "1", true, "enabled", false),
                "px4ctrl_step_baseline_v1" => ("Config/profiles/experiments/px4ctrl_step_baseline_v1.json", "px4ctrl", "1", true, "enabled", false),
                "px4ctrl_takeoff_hover_land_v1" => ("Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json", "px4ctrl", "1", true, "enabled", false),
            )
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
        end

        # SysplorerPressed function:SysplorerButton
        function SysplorerPressed(app,event)
            action = "open_model_context"
                project_root = get(ENV, "MOSIM_PROJECT_ROOT", "C:\\Users\\HP\\Desktop\\MoSim")
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
                bindings = Dict(
                "factory_l2_three_uav_swarm_formation_v1" => ("Config/profiles/experiments/factory_l2_three_uav_swarm_formation_v1.json", "px4ctrl", "3", true, "enabled", false),
                "fastlio_hybrid_z_figure8_v1" => ("Config/profiles/experiments/fastlio_hybrid_z_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "fastlio_independent_eval_figure8_v1" => ("Config/profiles/experiments/fastlio_independent_eval_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "fastlio_px4_ekf_ab_figure8_v1" => ("Config/profiles/experiments/fastlio_px4_ekf_ab_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "g10a_dfbc_smooth_robust_dob_figure8_v1" => ("Config/profiles/experiments/g10a_dfbc_smooth_robust_dob_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10a_dfbc_smooth_robust_no_dob_figure8_v1" => ("Config/profiles/experiments/g10a_dfbc_smooth_robust_no_dob_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_dfbc_smooth_robust_indi_figure8_v1" => ("Config/profiles/experiments/g10c_dfbc_smooth_robust_indi_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_dfbc_smooth_robust_no_indi_figure8_v1" => ("Config/profiles/experiments/g10c_dfbc_smooth_robust_no_indi_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_official_pid_indi_figure8_v1" => ("Config/profiles/experiments/g10c_official_pid_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g10c_official_pid_no_indi_figure8_v1" => ("Config/profiles/experiments/g10c_official_pid_no_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_bodyrate_figure8_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_bodyrate_figure8_v1.json", "dfbc_high_order_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1.json", "dfbc_high_order_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_figure8_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_figure8_v1.json", "dfbc_high_order_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_takeoff_hover_land_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_takeoff_hover_land_v1.json", "dfbc_high_order_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_bodyrate_figure8_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_bodyrate_figure8_v1.json", "dfbc_smooth_robust_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1.json", "dfbc_smooth_robust_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_figure8_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_takeoff_hover_land_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_takeoff_hover_land_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g9_dfbc_basic_figure8_v1" => ("Config/profiles/experiments/g9_dfbc_basic_figure8_v1.json", "dfbc_basic", "1", false, "controller_runtime_gate_pending", false),
                "g9_nmpc_outer_figure8_v1" => ("Config/profiles/experiments/g9_nmpc_outer_figure8_v1.json", "nmpc_outer", "1", false, "controller_runtime_gate_pending", false),
                "g9_official_pid_figure8_v1" => ("Config/profiles/experiments/g9_official_pid_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g9_pid_indi_figure8_v1" => ("Config/profiles/experiments/g9_pid_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g9_se3_basic_figure8_v1" => ("Config/profiles/experiments/g9_se3_basic_figure8_v1.json", "se3_basic", "1", false, "controller_runtime_gate_pending", false),
                "g9_smc_boundary_layer_figure8_v1" => ("Config/profiles/experiments/g9_smc_boundary_layer_figure8_v1.json", "smc_boundary_layer", "1", false, "controller_runtime_gate_pending", false),
                "px4ctrl_figure8_baseline_v1" => ("Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json", "px4ctrl", "1", true, "enabled", true),
                "px4ctrl_spiral_baseline_v1" => ("Config/profiles/experiments/px4ctrl_spiral_baseline_v1.json", "px4ctrl", "1", true, "enabled", false),
                "px4ctrl_step_baseline_v1" => ("Config/profiles/experiments/px4ctrl_step_baseline_v1.json", "px4ctrl", "1", true, "enabled", false),
                "px4ctrl_takeoff_hover_land_v1" => ("Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json", "px4ctrl", "1", true, "enabled", false),
            )
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
        end

        # ResultPressed function:ResultButton
        function ResultPressed(app,event)
            action = "get_result_packet"
                project_root = get(ENV, "MOSIM_PROJECT_ROOT", "C:\\Users\\HP\\Desktop\\MoSim")
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
                bindings = Dict(
                "factory_l2_three_uav_swarm_formation_v1" => ("Config/profiles/experiments/factory_l2_three_uav_swarm_formation_v1.json", "px4ctrl", "3", true, "enabled", false),
                "fastlio_hybrid_z_figure8_v1" => ("Config/profiles/experiments/fastlio_hybrid_z_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "fastlio_independent_eval_figure8_v1" => ("Config/profiles/experiments/fastlio_independent_eval_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "fastlio_px4_ekf_ab_figure8_v1" => ("Config/profiles/experiments/fastlio_px4_ekf_ab_figure8_v1.json", "px4ctrl", "1", true, "enabled", false),
                "g10a_dfbc_smooth_robust_dob_figure8_v1" => ("Config/profiles/experiments/g10a_dfbc_smooth_robust_dob_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10a_dfbc_smooth_robust_no_dob_figure8_v1" => ("Config/profiles/experiments/g10a_dfbc_smooth_robust_no_dob_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_dfbc_smooth_robust_indi_figure8_v1" => ("Config/profiles/experiments/g10c_dfbc_smooth_robust_indi_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_dfbc_smooth_robust_no_indi_figure8_v1" => ("Config/profiles/experiments/g10c_dfbc_smooth_robust_no_indi_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g10c_official_pid_indi_figure8_v1" => ("Config/profiles/experiments/g10c_official_pid_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g10c_official_pid_no_indi_figure8_v1" => ("Config/profiles/experiments/g10c_official_pid_no_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_bodyrate_figure8_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_bodyrate_figure8_v1.json", "dfbc_high_order_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1.json", "dfbc_high_order_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_figure8_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_figure8_v1.json", "dfbc_high_order_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g95_dfbc_high_order_takeoff_hover_land_v1" => ("Config/profiles/experiments/g95_dfbc_high_order_takeoff_hover_land_v1.json", "dfbc_high_order_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_bodyrate_figure8_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_bodyrate_figure8_v1.json", "dfbc_smooth_robust_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1.json", "dfbc_smooth_robust_bodyrate", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_figure8_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_figure8_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g96_dfbc_smooth_robust_takeoff_hover_land_v1" => ("Config/profiles/experiments/g96_dfbc_smooth_robust_takeoff_hover_land_v1.json", "dfbc_smooth_robust_attitude", "1", false, "controller_runtime_gate_pending", false),
                "g9_dfbc_basic_figure8_v1" => ("Config/profiles/experiments/g9_dfbc_basic_figure8_v1.json", "dfbc_basic", "1", false, "controller_runtime_gate_pending", false),
                "g9_nmpc_outer_figure8_v1" => ("Config/profiles/experiments/g9_nmpc_outer_figure8_v1.json", "nmpc_outer", "1", false, "controller_runtime_gate_pending", false),
                "g9_official_pid_figure8_v1" => ("Config/profiles/experiments/g9_official_pid_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g9_pid_indi_figure8_v1" => ("Config/profiles/experiments/g9_pid_indi_figure8_v1.json", "official_pid", "1", false, "controller_runtime_gate_pending", false),
                "g9_se3_basic_figure8_v1" => ("Config/profiles/experiments/g9_se3_basic_figure8_v1.json", "se3_basic", "1", false, "controller_runtime_gate_pending", false),
                "g9_smc_boundary_layer_figure8_v1" => ("Config/profiles/experiments/g9_smc_boundary_layer_figure8_v1.json", "smc_boundary_layer", "1", false, "controller_runtime_gate_pending", false),
                "px4ctrl_figure8_baseline_v1" => ("Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json", "px4ctrl", "1", true, "enabled", true),
                "px4ctrl_spiral_baseline_v1" => ("Config/profiles/experiments/px4ctrl_spiral_baseline_v1.json", "px4ctrl", "1", true, "enabled", false),
                "px4ctrl_step_baseline_v1" => ("Config/profiles/experiments/px4ctrl_step_baseline_v1.json", "px4ctrl", "1", true, "enabled", false),
                "px4ctrl_takeoff_hover_land_v1" => ("Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json", "px4ctrl", "1", true, "enabled", false),
            )
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

            # Create ProfileDropDown
            app.ProfileDropDown = TyAppDesigner.uidropdown(app.UIFigure)
            app.ProfileDropDown.Position = [30,82,410,32]
            app.ProfileDropDown.Label = raw"Experiment profile"
            app.ProfileDropDown.Items = [raw"factory_l2_three_uav_swarm_formation_v1",raw"fastlio_hybrid_z_figure8_v1",raw"fastlio_independent_eval_figure8_v1",raw"fastlio_px4_ekf_ab_figure8_v1",raw"g10a_dfbc_smooth_robust_dob_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g10a_dfbc_smooth_robust_no_dob_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g10c_dfbc_smooth_robust_indi_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g10c_dfbc_smooth_robust_no_indi_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g10c_official_pid_indi_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g10c_official_pid_no_indi_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g95_dfbc_high_order_bodyrate_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1 [disabled: controller_runtime_gate_pending]",raw"g95_dfbc_high_order_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g95_dfbc_high_order_takeoff_hover_land_v1 [disabled: controller_runtime_gate_pending]",raw"g96_dfbc_smooth_robust_bodyrate_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1 [disabled: controller_runtime_gate_pending]",raw"g96_dfbc_smooth_robust_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g96_dfbc_smooth_robust_takeoff_hover_land_v1 [disabled: controller_runtime_gate_pending]",raw"g9_dfbc_basic_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g9_nmpc_outer_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g9_official_pid_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g9_pid_indi_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g9_se3_basic_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"g9_smc_boundary_layer_figure8_v1 [disabled: controller_runtime_gate_pending]",raw"px4ctrl_figure8_baseline_v1",raw"px4ctrl_spiral_baseline_v1",raw"px4ctrl_step_baseline_v1",raw"px4ctrl_takeoff_hover_land_v1"]
            app.ProfileDropDown.Value = raw"px4ctrl_figure8_baseline_v1"
            app.ProfileDropDown.ValueChangedFcn = raw"ProfileChanged"

            # Create ControllerDropDown
            app.ControllerDropDown = TyAppDesigner.uidropdown(app.UIFigure)
            app.ControllerDropDown.Position = [30,130,410,32]
            app.ControllerDropDown.Label = raw"Controller"
            app.ControllerDropDown.Items = [raw"px4ctrl",raw"official_pid [disabled: runtime_evidence_pending]",raw"cascade_pid",raw"gain_scheduled_pid",raw"fuzzy_pid",raw"neural_pid",raw"lqr_baseline [disabled: runtime_evidence_pending]",raw"lqi_baseline [disabled: runtime_evidence_pending]",raw"lqg [disabled: runtime_evidence_pending]",raw"mu_synthesis [disabled: runtime_evidence_pending]",raw"feedback_linearization [disabled: runtime_evidence_pending]",raw"passivity_based_control [disabled: runtime_evidence_pending]",raw"adaptive_backstepping [disabled: runtime_evidence_pending]",raw"backstepping_baseline [disabled: runtime_evidence_pending]",raw"se3_basic [disabled: runtime_evidence_pending]",raw"dfbc_basic [disabled: runtime_evidence_pending]",raw"smc_boundary_layer [disabled: runtime_evidence_pending]",raw"integral_smc [disabled: runtime_evidence_pending]",raw"terminal_smc [disabled: runtime_evidence_pending]",raw"nonsingular_terminal_smc [disabled: runtime_evidence_pending]",raw"super_twisting_smc [disabled: runtime_evidence_pending]",raw"adaptive_smc [disabled: runtime_evidence_pending]",raw"fuzzy_smc [disabled: runtime_evidence_pending]",raw"neural_smc [disabled: runtime_evidence_pending]",raw"hinf_hover_wrench [disabled: runtime_evidence_pending]",raw"nmpc_outer [disabled: runtime_evidence_pending]",raw"dfbc_high_order_attitude [disabled: runtime_evidence_pending]",raw"dfbc_high_order_bodyrate [disabled: runtime_evidence_pending]",raw"dfbc_smooth_robust_attitude [disabled: runtime_evidence_pending]",raw"dfbc_smooth_robust_bodyrate [disabled: runtime_evidence_pending]"]
            app.ControllerDropDown.Value = raw"px4ctrl"
            app.ControllerDropDown.ValueChangedFcn = raw"ControllerChanged"

            # Create VehicleDropDown
            app.VehicleDropDown = TyAppDesigner.uidropdown(app.UIFigure)
            app.VehicleDropDown.Position = [30,178,410,32]
            app.VehicleDropDown.Label = raw"UAV count"
            app.VehicleDropDown.Items = [raw"1",raw"2 [disabled: scale_gate_pending]",raw"3",raw"4 [disabled: scale_gate_pending]",raw"5 [disabled: scale_gate_pending]",raw"6 [disabled: scale_gate_pending]",raw"7 [disabled: scale_gate_pending]",raw"8 [disabled: scale_gate_pending]",raw"9 [disabled: scale_gate_pending]"]
            app.VehicleDropDown.Value = raw"1"
            app.VehicleDropDown.ValueChangedFcn = raw"VehicleChanged"

            # Create WindField
            app.WindField = TyAppDesigner.uinumericeditfield(app.UIFigure)
            app.WindField.Position = [30,226,410,32]
            app.WindField.Limits = [0,20]
            app.WindField.Label = raw"Wind speed (m/s)"
            app.WindField.Value = 0

            # Create RefreshButton
            app.RefreshButton = TyAppDesigner.uibutton(app.UIFigure)
            app.RefreshButton.Position = [30,282,190,36]
            app.RefreshButton.Text = raw"Refresh capability"
            app.RefreshButton.ButtonPushedFcn = raw"RefreshPressed"

            # Create PreviewButton
            app.PreviewButton = TyAppDesigner.uibutton(app.UIFigure)
            app.PreviewButton.Position = [250,282,190,36]
            app.PreviewButton.Text = raw"Preview"
            app.PreviewButton.ButtonPushedFcn = raw"PreviewPressed"

            # Create SubmitButton
            app.SubmitButton = TyAppDesigner.uibutton(app.UIFigure)
            app.SubmitButton.Position = [30,334,190,36]
            app.SubmitButton.Text = raw"Prepare run"
            app.SubmitButton.ButtonPushedFcn = raw"SubmitPressed"

            # Create SysplorerButton
            app.SysplorerButton = TyAppDesigner.uibutton(app.UIFigure)
            app.SysplorerButton.Position = [250,334,190,36]
            app.SysplorerButton.Text = raw"Open model"
            app.SysplorerButton.ButtonPushedFcn = raw"SysplorerPressed"

            # Create ResultButton
            app.ResultButton = TyAppDesigner.uibutton(app.UIFigure)
            app.ResultButton.Position = [30,386,190,36]
            app.ResultButton.Text = raw"Open result"
            app.ResultButton.ButtonPushedFcn = raw"ResultPressed"

            # Create StatusLabel
            app.StatusLabel = TyAppDesigner.uilabel(app.UIFigure)
            app.StatusLabel.Position = [30,442,410,128]
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