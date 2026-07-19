module MoSimModelStudio

using ObjectOriented
using TyAppDesigner
using Dates
include(joinpath(@__DIR__, "live_cosim_backend.jl"))
using .LiveCosimBackend

const ACTIVE_COLOR = [0.08, 0.36, 0.43]
const INACTIVE_COLOR = [0.88, 0.91, 0.92]
const SECTION_COLOR = [0.12, 0.25, 0.32]
const READY_COLOR = [0.86, 0.95, 0.89]
const WAIT_COLOR = [0.98, 0.93, 0.80]
const MUTED_COLOR = [0.93, 0.94, 0.94]
const CONSOLE_COLOR = [0.07, 0.10, 0.12]
const CONSOLE_TEXT_COLOR = [0.82, 0.91, 0.86]
const PROJECT_ROOT = normpath(joinpath(@__DIR__, "..", "..", ".."))
const OFFLINE_BATCH_RUNNER = joinpath(PROJECT_ROOT, "Scripts", "mworks", "run_offline_profile_batch.py")
const OFFLINE_ANIMATION_RESUMER = joinpath(PROJECT_ROOT, "Scripts", "mworks", "resume_offline_profile_animation.py")
const OFFLINE_BATCH_INDEX = joinpath(PROJECT_ROOT, "Results", "control_platform", "offline_batches", "BATCH_INDEX.json")

const CUSTOM_PROFILE_LABEL = "自定义组合"
const VEHICLE_COUNT_OPTIONS = string.(1:9)
const MAP_OPTIONS = ["空白地图", "Factory 避障地图"]
const LIVE_PROFILE_OPTIONS = [
    "official_pid_attitude_thrust_v1 [候选]",
    "official_pid + awff_v1 [候选]",
]
const SINGLE_UAV_MISSION_OPTIONS = ["起飞-悬停-降落", "爬升", "八字轨迹", "螺旋轨迹"]
const THREE_UAV_MISSION_OPTIONS = ["三机三角编队 8 字"]
const MODEL_MISSION_OPTIONS = vcat(SINGLE_UAV_MISSION_OPTIONS, THREE_UAV_MISSION_OPTIONS)
const MODEL_POSITION_OPTIONS = [
    "official_pid [已认证]", "improved_pid [已认证]", "linear_mpc [已认证]",
    "fault_compensation [已认证]", "px4ctrl [待接入]", "cascade_pid [待接入]",
    "gain_scheduled_pid [待接入]", "fuzzy_pid [待接入]", "neural_pid [待接入]",
    "trained_neural_residual [待接入]", "rl_gain_scheduler [待接入]", "lqr_baseline [待接入]",
    "lqi_baseline [待接入]", "lqg [待接入]", "mu_synthesis [待接入]",
    "feedback_linearization [待接入]", "passivity_based_control [待接入]",
    "adaptive_backstepping [待接入]", "pole_placement_luenberger [待接入]",
    "mrac [待接入]", "ndi [待接入]", "fopid [待接入]", "h2_state_feedback [待接入]",
    "backstepping_baseline [待接入]", "se3_basic [待接入]", "dfbc_basic [待接入]",
    "smc_boundary_layer [待接入]", "integral_smc [待接入]", "terminal_smc [待接入]",
    "nonsingular_terminal_smc [待接入]", "super_twisting_smc [待接入]",
    "adaptive_smc [待接入]", "fuzzy_smc [待接入]", "neural_smc [待接入]",
    "hinf_hover_wrench [待接入]", "nmpc_outer [待接入]",
    "dfbc_high_order_attitude [待接入]", "dfbc_high_order_bodyrate [待接入]",
    "dfbc_smooth_robust_attitude [待接入]", "dfbc_smooth_robust_bodyrate [待接入]",
]
const MODEL_ATTITUDE_OPTIONS = ["模型内部姿态/角速度环 [已认证]", "so3_attitude [待接入]", "px4_attitude_rate_inner [在线专用]"]
const MODEL_AUGMENTATION_OPTIONS = [
    "无", "pid_indi [已认证]", "awff [已认证]", "l1_adaptive [已认证]",
    "anti_windup [待接入]", "feedforward_profile [待接入]", "l1_awff_minimal [待接入]",
    "complete_adrc [待接入]", "standardized_indi [待接入]", "parameter_scheduling [待接入]",
    "ilc [待接入]", "dfbc_dob_eso_disabled [不可执行]", "dfbc_dob_eso [待接入]",
]
const MODEL_SAFETY_OPTIONS = [
    "basic_limiter [已认证]", "safety_filter [待接入]", "cbf [待接入]",
    "reference_governor [待接入]", "geofence [待接入]", "emergency_stop [待接入]",
    "return_and_land [待接入]", "failsafe_state_machine [待接入]",
]
const MODEL_FAULT_OPTIONS = [
    "无", "风扰", "电机效率下降", "风扰 + 电机效率下降", "fdi [待接入]",
    "passive_ftc [待接入]", "active_ftc [待接入]", "fault_aware_control_allocation [待接入]",
    "single_motor_fault_safe_land [待接入]", "multiple_fault_estimation_and_reconstruction [待接入]",
]
const MODEL_FORMATION_OPTIONS = [
    "无", "leader_follower [已认证]", "virtual_structure [待接入]", "consensus [待接入]",
    "containment [待接入]", "formation_tracking [待接入]", "formation_reconfiguration [待接入]",
    "fault_tolerant_formation [待接入]", "formation_cbf [待接入]",
    "distributed_mpc_formation [待接入]",
]
const MODEL_OUTPUT_OPTIONS = [
    "ROTOR_COMMAND / px4_control_allocator [已认证]",
    "ATTITUDE_THRUST / mavros_attitude_thrust [平台已验证]",
    "BODY_RATE_THRUST / mavros_bodyrate_thrust [平台已验证]",
    "WRENCH [平台已验证]",
]

const OFFLINE_PROFILE_ORDER = [
    "Official PID 爬升 [已认证]",
    "改进 PID 爬升 [已认证]",
    "AWFF 爬升 [已认证]",
    "PID-INDI 爬升 [已认证]",
    "Linear MPC 爬升 [已认证]",
    "L1/AWFF 爬升 [已认证]",
    "L1/AWFF 风扰 [已认证]",
    "故障补偿：电机 1 效率 85% [已认证]",
    "三机 Linear MPC 三角编队 8 字 [已认证]",
    "Custom：改进 PID + 轻风扰 [已验证]",
    "Custom：故障补偿 + 轻风扰 [已验证]",
    "QP/NMPC Safety [当前禁用]",
]

const OFFLINE_PROFILES = Dict(
    "Official PID 爬升 [已认证]" => (profile="offline_official_pid_climb_v1", mission="爬升", controller="official_pid [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="无", safety="basic_limiter [已认证]", fault="无", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/cert-official-pid-20260719-v2", available=true),
    "改进 PID 爬升 [已认证]" => (profile="offline_improved_pid_climb_v1", mission="爬升", controller="improved_pid [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="无", safety="basic_limiter [已认证]", fault="无", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/cert-improved-pid-20260719-v1", available=true),
    "AWFF 爬升 [已认证]" => (profile="offline_awff_climb_v1", mission="爬升", controller="official_pid [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="awff [已认证]", safety="basic_limiter [已认证]", fault="无", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/cert-awff-20260719-v1", available=true),
    "PID-INDI 爬升 [已认证]" => (profile="offline_pid_indi_climb_v1", mission="爬升", controller="official_pid [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="pid_indi [已认证]", safety="basic_limiter [已认证]", fault="无", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/cert-pid-indi-20260719-v1", available=true),
    "Linear MPC 爬升 [已认证]" => (profile="offline_linear_mpc_climb_v1", mission="爬升", controller="linear_mpc [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="无", safety="basic_limiter [已认证]", fault="无", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/cert-linear-mpc-20260719-v1", available=true),
    "L1/AWFF 爬升 [已认证]" => (profile="offline_l1_awff_climb_v1", mission="爬升", controller="official_pid [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="l1_adaptive [已认证]", safety="basic_limiter [已认证]", fault="无", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/cert-l1-awff-climb-20260719-v1", available=true),
    "L1/AWFF 风扰 [已认证]" => (profile="offline_l1_awff_wind_v1", mission="爬升", controller="official_pid [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="l1_adaptive [已认证]", safety="basic_limiter [已认证]", fault="风扰", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/cert-l1-awff-wind-20260719-v1", available=true),
    "故障补偿：电机 1 效率 85% [已认证]" => (profile="offline_fault_comp_rotor1_85_v1", mission="爬升", controller="fault_compensation [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="无", safety="basic_limiter [已认证]", fault="电机效率下降", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/cert-fault-comp-rotor1-85-20260719-v1", available=true),
    "三机 Linear MPC 三角编队 8 字 [已认证]" => (profile="offline_three_uav_linear_mpc_figure8_v1", mission="三机三角编队 8 字", controller="linear_mpc [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="无", safety="basic_limiter [已认证]", fault="无", formation="leader_follower [已认证]", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/cert-three-uav-linear-mpc-figure8-20260719-v2", available=true),
    "Custom：改进 PID + 轻风扰 [已验证]" => (profile="custom_improved_pid_mild_wind_v1", mission="爬升", controller="improved_pid [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="无", safety="basic_limiter [已认证]", fault="风扰", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/p7-custom-improved-pid-mild-wind-20260719-v2", available=true),
    "Custom：故障补偿 + 轻风扰 [已验证]" => (profile="custom_fault_comp_mixed_v1", mission="爬升", controller="fault_compensation [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="无", safety="basic_limiter [已认证]", fault="风扰 + 电机效率下降", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="Results/mworks_generated_profiles/p7-custom-fault-comp-mixed-20260719-v2", available=true),
    "QP/NMPC Safety [当前禁用]" => (profile="offline_qp_nmpc_safety_climb_v1", mission="爬升", controller="linear_mpc [已认证]", attitude="模型内部姿态/角速度环 [已认证]", augmentation="无", safety="safety_filter [待接入]", fault="无", formation="无", output="ROTOR_COMMAND / px4_control_allocator [已认证]", evidence="当前共用 Runner 与独立模型均数值失稳", available=false),
)

@oodef mutable struct App
    UIFigure::Any = nothing
    TitleLabel::Any = nothing
    SubtitleLabel::Any = nothing
    OfflineModeButton::Any = nothing
    LiveModeButton::Any = nothing
    DeployModeButton::Any = nothing
    ModeStatusLabel::Any = nothing

    ConfigSectionLabel::Any = nothing
    ChainSectionLabel::Any = nothing
    InjectionSectionLabel::Any = nothing

    ProfileDropDown::Any = nothing
    VehicleCountDropDown::Any = nothing
    MapDropDown::Any = nothing
    MissionDropDown::Any = nothing
    PositionDropDown::Any = nothing
    AttitudeDropDown::Any = nothing
    AugmentationDropDown::Any = nothing
    SafetyDropDown::Any = nothing
    FaultDropDown::Any = nothing
    FormationDropDown::Any = nothing
    OutputDropDown::Any = nothing
    ProfileSummaryLabel::Any = nothing
    CapabilityLabel::Any = nothing

    ChainLabel::Any = nothing
    ContractLabel::Any = nothing
    TimingLabel::Any = nothing
    TargetHostField::Any = nothing
    Rt1PortField::Any = nothing
    RosMasterField::Any = nothing
    LocalIpField::Any = nothing
    TargetRateDropDown::Any = nothing
    TestConnectionButton::Any = nothing
    ConnectionStatusLabel::Any = nothing

    DeployTargetDropDown::Any = nothing
    BuildModeDropDown::Any = nothing

    TargetUavDropDown::Any = nothing
    WindSlider::Any = nothing
    Motor1Slider::Any = nothing
    Motor2Slider::Any = nothing
    Motor3Slider::Any = nothing
    Motor4Slider::Any = nothing
    InjectionValuesLabel::Any = nothing
    ApplyInjectionButton::Any = nothing
    RestoreInjectionButton::Any = nothing
    ManifestLabel::Any = nothing

    ValidateButton::Any = nothing
    PublishButton::Any = nothing
    PrepareButton::Any = nothing
    QgcButton::Any = nothing
    SafeStopButton::Any = nothing
    OpenModelButton::Any = nothing
    MilButton::Any = nothing
    CodegenButton::Any = nothing
    ResultButton::Any = nothing
    ConsoleToggleButton::Any = nothing
    ConsoleClearButton::Any = nothing
    StatusLabel::Any = nothing

    # ObjectOriented's field parser requires literal defaults; bind source
    # metadata during initApp instead of using macro expressions as defaults.
    Appname::Any = nothing
    Appfile::Any = ""
    CurrentMode::String = "live"
    LastOfflineBatchManifest::String = ""
    LastOfflineBatchId::String = ""
    LastOfflineProfile::String = ""
    CurrentOfflineBatchId::String = ""
    OfflineBatchRunning::Bool = false
    ConsoleLines::Any = nothing
    ConsoleExpanded::Bool = true

    function append_console(app, message; level="信息")
        normalized = replace(string(message), '\n' => "  |  ")
        timestamp = Dates.format(Dates.now(), "HH:MM:SS")
        push!(app.ConsoleLines, timestamp * "  [" * level * "]  " * normalized)
        length(app.ConsoleLines) > 40 && deleteat!(app.ConsoleLines, 1:length(app.ConsoleLines)-40)
        visible_lines = app.ConsoleExpanded ? 6 : 1
        app.StatusLabel.Text = join(last(app.ConsoleLines, min(visible_lines, length(app.ConsoleLines))), "\n")
    end

    function set_top_status(app, text; state="待命")
        marker = state == "正常" ? "●" : (state == "阻断" ? "■" : "◆")
        app.ModeStatusLabel.Text = marker * "  " * text
        app.ModeStatusLabel.FontColor = state == "正常" ? [0.10, 0.42, 0.25] :
            (state == "阻断" ? [0.70, 0.20, 0.16] : [0.55, 0.38, 0.05])
    end

    function ToggleConsolePressed(app, event)
        app.ConsoleExpanded = !app.ConsoleExpanded
        app.StatusLabel.Visible = app.ConsoleExpanded
        app.ConsoleToggleButton.Text = app.ConsoleExpanded ? "收起日志" : "展开日志"
        if app.ConsoleExpanded && !isempty(app.ConsoleLines)
            app.StatusLabel.Text = join(last(app.ConsoleLines, min(6, length(app.ConsoleLines))), "\n")
        end
    end

    function ClearConsolePressed(app, event)
        empty!(app.ConsoleLines)
        app.StatusLabel.Text = ""
        app.append_console("运行日志已清空")
    end

    function refresh_live_capability(app, action="status")
        response = LiveCosimBackend.request(
            app.Appfile,
            action,
            app.ProfileDropDown.Value;
            host=app.TargetHostField.Value,
            port=round(Int, app.Rt1PortField.Value),
            ros_master_uri=app.RosMasterField.Value,
            local_advertised_ip=app.LocalIpField.Value,
            rate_hz=parse(Int, app.TargetRateDropDown.Value),
        )
        accepted = get(response, "accepted", "false") == "true"
        reason = get(response, "reason_code", "live_backend_unknown")
        rate = get(response, "output_rate_hz", "")
        latency = get(response, "latency_p99_ms", "")
        metrics = isempty(rate) ? "" : "\n实测输出 " * rate * " Hz  |  P99 " * latency * " ms"
        app.CapabilityLabel.Text = accepted ?
            "● 运行门禁通过  |  RT0 通过  |  可请求 prepare" * metrics :
            "◆ 运行门禁阻断  |  50 Hz 已测  |  " * reason * metrics
        app.CapabilityLabel.BackgroundColor = MUTED_COLOR
        app.PrepareButton.Enable = accepted && app.live_combination_compatible()
        app.PublishButton.Enable = app.PrepareButton.Enable
        app.QgcButton.Enable = false
        return response
    end

    function set_connection_controls(app, enabled)
        app.TargetHostField.Enable = enabled
        app.Rt1PortField.Enable = enabled
        app.RosMasterField.Enable = enabled
        app.LocalIpField.Enable = enabled
        app.TargetRateDropDown.Enable = enabled
        app.TestConnectionButton.Enable = enabled
    end

    function set_button_state(app, button, active)
        button.BackgroundColor = active ? ACTIVE_COLOR : INACTIVE_COLOR
        button.FontColor = active ? [1.0, 1.0, 1.0] : [0.20, 0.25, 0.28]
        button.FontWeight = "bold"
    end

    function set_visible(app, controls, visible)
        for control in controls
            control.Visible = visible
        end
    end

    function configure_console_workspace(app; left=964, width=452)
        app.configure_section(app.InjectionSectionLabel, "运行日志", [left, 144, width, 34])
        app.StatusLabel.Position = [left, 192, width, 456]
        app.StatusLabel.Visible = true
        app.ConsoleToggleButton.Visible = false
        app.ConsoleClearButton.Position = [left + width - 84, 200, 76, 28]
        app.ConsoleClearButton.Visible = true
    end

    function workspace_controls(app)
        return (
            app.ProfileDropDown, app.VehicleCountDropDown, app.MapDropDown,
            app.MissionDropDown, app.PositionDropDown,
            app.AttitudeDropDown, app.AugmentationDropDown, app.SafetyDropDown,
            app.FaultDropDown, app.FormationDropDown, app.OutputDropDown,
            app.ProfileSummaryLabel, app.CapabilityLabel,
            app.TargetHostField, app.Rt1PortField,
            app.RosMasterField, app.LocalIpField, app.TargetRateDropDown,
            app.TestConnectionButton, app.ConnectionStatusLabel,
            app.DeployTargetDropDown, app.BuildModeDropDown, app.ChainLabel,
            app.ContractLabel, app.TimingLabel, app.TargetUavDropDown,
            app.WindSlider, app.Motor1Slider,
            app.Motor2Slider, app.Motor3Slider, app.Motor4Slider,
            app.InjectionValuesLabel, app.ApplyInjectionButton,
            app.RestoreInjectionButton, app.ManifestLabel,
        )
    end

    function is_three_uav_mission(mission)
        return mission in THREE_UAV_MISSION_OPTIONS
    end

    function mission_vehicle_count(mission)
        return is_three_uav_mission(mission) ? 3 : 1
    end

    function mission_options_for_vehicle_count(vehicle_count)
        return vehicle_count == 3 ? MODEL_MISSION_OPTIONS : SINGLE_UAV_MISSION_OPTIONS
    end

    function sync_vehicle_controls(app)
        vehicle_count = parse(Int, app.VehicleCountDropDown.Value)
        target_items = ["UAV " * string(index) for index in 1:vehicle_count]
        current_target = app.TargetUavDropDown.Value
        app.TargetUavDropDown.Items = target_items
        app.TargetUavDropDown.Value = current_target in target_items ? current_target : target_items[1]

        mission_items = mission_options_for_vehicle_count(vehicle_count)
        current_mission = app.MissionDropDown.Value
        app.MissionDropDown.Items = mission_items
        app.MissionDropDown.Value = current_mission in mission_items ?
            current_mission : mission_items[1]

        app.FormationDropDown.Enable = vehicle_count > 1
        if vehicle_count == 1
            app.FormationDropDown.Value = "无"
        end
    end

    function configure_composition_controls(app; live=false)
        app.set_dropdown_position(app.ProfileDropDown, [24, 192, 440, 32])
        app.ProfileDropDown.Label = "快速预设"
        app.ProfileDropDown.Items = live ? vcat([CUSTOM_PROFILE_LABEL], LIVE_PROFILE_OPTIONS) :
            vcat([CUSTOM_PROFILE_LABEL], OFFLINE_PROFILE_ORDER)
        app.ProfileDropDown.Value = live ? LIVE_PROFILE_OPTIONS[1] : CUSTOM_PROFILE_LABEL

        app.set_dropdown_position(app.VehicleCountDropDown, [24, 238, 210, 32])
        app.VehicleCountDropDown.Items = VEHICLE_COUNT_OPTIONS
        app.VehicleCountDropDown.Value = "1"
        app.set_dropdown_position(app.MapDropDown, [254, 238, 210, 32])
        app.MapDropDown.Items = MAP_OPTIONS
        app.MapDropDown.Value = MAP_OPTIONS[1]

        app.set_dropdown_position(app.MissionDropDown, [24, 284, 440, 32])
        app.MissionDropDown.Items = MODEL_MISSION_OPTIONS
        app.MissionDropDown.Value = MODEL_MISSION_OPTIONS[1]
        app.set_dropdown_position(app.PositionDropDown, [24, 330, 440, 32])
        app.PositionDropDown.Items = MODEL_POSITION_OPTIONS
        app.PositionDropDown.Value = MODEL_POSITION_OPTIONS[1]
        app.set_dropdown_position(app.AttitudeDropDown, [24, 376, 440, 32])
        app.AttitudeDropDown.Items = MODEL_ATTITUDE_OPTIONS
        app.AttitudeDropDown.Value = live ? "px4_attitude_rate_inner [在线专用]" : MODEL_ATTITUDE_OPTIONS[1]
        app.set_dropdown_position(app.AugmentationDropDown, [24, 422, 440, 32])
        app.AugmentationDropDown.Items = MODEL_AUGMENTATION_OPTIONS
        app.AugmentationDropDown.Value = MODEL_AUGMENTATION_OPTIONS[1]
        app.set_dropdown_position(app.SafetyDropDown, [24, 468, 440, 32])
        app.SafetyDropDown.Items = MODEL_SAFETY_OPTIONS
        app.SafetyDropDown.Value = MODEL_SAFETY_OPTIONS[1]
        app.set_dropdown_position(app.FaultDropDown, [24, 514, 440, 32])
        app.FaultDropDown.Items = MODEL_FAULT_OPTIONS
        app.FaultDropDown.Value = MODEL_FAULT_OPTIONS[1]
        app.set_dropdown_position(app.FormationDropDown, [24, 560, 440, 32])
        app.FormationDropDown.Items = MODEL_FORMATION_OPTIONS
        app.FormationDropDown.Value = MODEL_FORMATION_OPTIONS[1]
        app.set_dropdown_position(app.OutputDropDown, [24, 606, 440, 32])
        app.OutputDropDown.Items = MODEL_OUTPUT_OPTIONS
        app.OutputDropDown.Value = live ?
            "ATTITUDE_THRUST / mavros_attitude_thrust [平台已验证]" : MODEL_OUTPUT_OPTIONS[1]

        for control in (app.VehicleCountDropDown, app.MapDropDown, app.MissionDropDown,
            app.PositionDropDown, app.AttitudeDropDown, app.AugmentationDropDown,
            app.SafetyDropDown, app.FaultDropDown, app.OutputDropDown)
            control.Enable = true
        end
        app.sync_vehicle_controls()
    end

    function live_combination_compatible(app)
        return app.VehicleCountDropDown.Value == "1" &&
            app.FormationDropDown.Value == "无" &&
            app.PositionDropDown.Value == MODEL_POSITION_OPTIONS[1] &&
            app.AttitudeDropDown.Value == "px4_attitude_rate_inner [在线专用]" &&
            app.OutputDropDown.Value == "ATTITUDE_THRUST / mavros_attitude_thrust [平台已验证]"
    end

    function action_buttons(app)
        return (
            app.ValidateButton, app.PublishButton, app.PrepareButton,
            app.QgcButton, app.SafeStopButton, app.OpenModelButton,
            app.MilButton, app.CodegenButton, app.ResultButton,
        )
    end

    function apply_preset(app, label)
        haskey(OFFLINE_PROFILES, label) || return
        item = OFFLINE_PROFILES[label]
        app.VehicleCountDropDown.Value = string(mission_vehicle_count(item.mission))
        app.MapDropDown.Value = MAP_OPTIONS[1]
        app.sync_vehicle_controls()
        app.MissionDropDown.Value = item.mission
        app.PositionDropDown.Value = item.controller
        app.AttitudeDropDown.Value = item.attitude
        app.AugmentationDropDown.Value = item.augmentation
        app.SafetyDropDown.Value = item.safety
        app.FaultDropDown.Value = item.fault
        app.FormationDropDown.Value = item.formation
        app.OutputDropDown.Value = item.output
    end

    function selected_model_profile(app)
        label = app.ProfileDropDown.Value
        return haskey(OFFLINE_PROFILES, label) ? OFFLINE_PROFILES[label] : nothing
    end

    function preset_matches_selection(app, item)
        item === nothing && return false
        return app.MissionDropDown.Value == item.mission &&
            app.VehicleCountDropDown.Value == string(mission_vehicle_count(item.mission)) &&
            app.MapDropDown.Value == MAP_OPTIONS[1] &&
            app.PositionDropDown.Value == item.controller &&
            app.AttitudeDropDown.Value == item.attitude &&
            app.AugmentationDropDown.Value == item.augmentation &&
            app.SafetyDropDown.Value == item.safety &&
            app.FaultDropDown.Value == item.fault &&
            app.FormationDropDown.Value == item.formation &&
            app.OutputDropDown.Value == item.output
    end

    function refresh_summary(app)
        if app.CurrentMode == "model"
            item = app.selected_model_profile()
            certified = item !== nothing && item.available && app.preset_matches_selection(item)
            unavailable = occursin("[待接入]", app.PositionDropDown.Value) ||
                occursin("[待接入]", app.AttitudeDropDown.Value) ||
                occursin("[待接入]", app.AugmentationDropDown.Value) ||
                occursin("[待接入]", app.SafetyDropDown.Value) ||
                occursin("[待接入]", app.FaultDropDown.Value) ||
                occursin("[待接入]", app.FormationDropDown.Value)
            incompatible = occursin("[不可执行]", app.AugmentationDropDown.Value) ||
                (app.FormationDropDown.Value != "无" && app.VehicleCountDropDown.Value == "1") ||
                (is_three_uav_mission(app.MissionDropDown.Value) && app.VehicleCountDropDown.Value != "3")
            executable = certified && !unavailable && !incompatible
            app.MilButton.Enable = executable
            app.CodegenButton.Enable = executable && !occursin("Custom", app.ProfileDropDown.Value)
            app.ValidateButton.Enable = true
            state = incompatible ? "结构不兼容" : (unavailable ? "接口待接入" : (executable ? "可直接运行" : "可配置，需保存并验证"))
            gate_mark = executable ? "✓" : (incompatible ? "✕" : "◆")
            app.ChainLabel.Text = gate_mark * " 组合  " * state *
                "  |  模型 ✓  接口 " * (unavailable ? "◆" : "✓") *
                "  参数 ✓  执行 " * (executable ? "✓" : "✕")
            app.ChainLabel.BackgroundColor = MUTED_COLOR
            app.ProfileSummaryLabel.Text =
                "外环  " * app.PositionDropDown.Value * "  |  内环  " * app.AttitudeDropDown.Value * "\n" *
                "增强  " * app.AugmentationDropDown.Value * "  |  安全  " * app.SafetyDropDown.Value
            app.CapabilityLabel.Text = item === nothing ?
                "◆ 自定义 Profile 未验证  |  执行保持禁用" :
                "● " * item.profile * "  |  Result.msr / 动画证据已登记"
            app.CapabilityLabel.BackgroundColor = MUTED_COLOR
            return
        elseif app.CurrentMode == "deploy"
            app.ProfileSummaryLabel.Text = "配置来源  " * app.ProfileDropDown.Value * "\n" *
                "生成目标  " * app.DeployTargetDropDown.Value * "\n" *
                "构建类型  " * app.BuildModeDropDown.Value
            return
        end
        app.ProfileSummaryLabel.Text = "运行Profile  " * app.ProfileDropDown.Value *
            "\n任务  " * app.MissionDropDown.Value
    end

    function configure_model_workspace(app)
        app.set_top_status("在线建模验证  |  未运行  |  Result.msr --"; state="正常")
        app.configure_section(app.ConfigSectionLabel, "控制器组合", [24, 144, 440, 34])
        app.configure_section(app.ChainSectionLabel, "风扰与故障", [494, 144, 440, 34])
        app.configure_console_workspace()
        app.ConfigSectionLabel.Visible = true
        app.ChainSectionLabel.Visible = true
        app.InjectionSectionLabel.Visible = true
        app.set_visible(app.workspace_controls(), false)
        model_controls = (
            app.ProfileDropDown, app.VehicleCountDropDown, app.MapDropDown,
            app.MissionDropDown, app.PositionDropDown,
            app.AttitudeDropDown, app.AugmentationDropDown, app.SafetyDropDown,
            app.FaultDropDown, app.FormationDropDown, app.OutputDropDown,
            app.TargetUavDropDown, app.WindSlider,
            app.Motor1Slider, app.Motor2Slider, app.Motor3Slider,
            app.Motor4Slider,
            app.ApplyInjectionButton, app.RestoreInjectionButton,
        )
        app.set_visible(model_controls, true)
        app.configure_composition_controls()

        app.set_dropdown_position(app.TargetUavDropDown, [494, 192, 440, 32])
        app.WindSlider.Position = [494, 240, 440, 52]
        app.Motor1Slider.Position = [494, 298, 440, 52]
        app.Motor2Slider.Position = [494, 356, 440, 52]
        app.Motor3Slider.Position = [494, 414, 440, 52]
        app.Motor4Slider.Position = [494, 472, 440, 52]
        app.ApplyInjectionButton.Position = [494, 540, 210, 36]
        app.ApplyInjectionButton.Text = "写入仿真场景"
        app.RestoreInjectionButton.Position = [724, 540, 210, 36]
        app.RestoreInjectionButton.Text = "恢复默认"

        app.set_visible(app.action_buttons(), false)
        app.set_visible((app.MilButton, app.SafeStopButton, app.ResultButton), true)
        app.MilButton.Position = [494, 600, 140, 38]
        app.MilButton.Text = "开始仿真"
        app.SafeStopButton.Position = [644, 600, 140, 38]
        app.SafeStopButton.Text = "停止"
        app.SafeStopButton.Enable = app.OfflineBatchRunning
        app.ResultButton.Position = [794, 600, 140, 38]
        app.ResultButton.Text = "打开结果"
    end

    function configure_live_workspace(app)
        app.set_top_status("实时联合仿真  |  运行状态 --  |  控制频率 -- Hz  |  RTT P95 -- ms  |  延迟 P99 -- ms  |  抖动 -- ms  |  丢包率 -- %  |  带宽 -- B/s  |  Deadline miss --"; state="待命")
        app.configure_section(app.ConfigSectionLabel, "控制器组合", [24, 144, 440, 34])
        app.configure_section(app.ChainSectionLabel, "连接与实时故障", [494, 144, 440, 34])
        app.configure_console_workspace()
        app.ConfigSectionLabel.Visible = true
        app.ChainSectionLabel.Visible = true
        app.InjectionSectionLabel.Visible = true
        app.set_visible(app.workspace_controls(), false)
        live_controls = (
            app.ProfileDropDown, app.VehicleCountDropDown, app.MapDropDown,
            app.MissionDropDown, app.PositionDropDown, app.AttitudeDropDown,
            app.AugmentationDropDown, app.SafetyDropDown, app.FaultDropDown,
            app.FormationDropDown, app.OutputDropDown, app.TargetHostField,
            app.Rt1PortField, app.RosMasterField, app.LocalIpField,
            app.TargetRateDropDown, app.TestConnectionButton,
            app.TargetUavDropDown, app.WindSlider, app.Motor1Slider,
            app.Motor2Slider, app.Motor3Slider, app.Motor4Slider,
            app.ApplyInjectionButton, app.RestoreInjectionButton,
        )
        app.set_visible(live_controls, true)
        app.configure_composition_controls(live=true)

        app.TargetHostField.Position = [494, 192, 270, 32]
        app.Rt1PortField.Position = [784, 192, 150, 32]
        app.RosMasterField.Position = [494, 238, 270, 32]
        app.LocalIpField.Position = [784, 238, 150, 32]
        app.set_dropdown_position(app.TargetRateDropDown, [494, 284, 190, 32])
        app.TestConnectionButton.Position = [704, 282, 150, 36]

        app.set_dropdown_position(app.TargetUavDropDown, [494, 330, 440, 32])
        app.WindSlider.Position = [494, 378, 440, 44]
        app.Motor1Slider.Position = [494, 428, 440, 44]
        app.Motor2Slider.Position = [494, 478, 440, 44]
        app.Motor3Slider.Position = [494, 528, 440, 44]
        app.Motor4Slider.Position = [494, 578, 440, 44]
        app.ApplyInjectionButton.Position = [494, 628, 210, 32]
        app.ApplyInjectionButton.Text = "应用故障"
        app.RestoreInjectionButton.Position = [724, 628, 210, 32]
        app.RestoreInjectionButton.Text = "恢复正常"

        app.set_visible(app.action_buttons(), false)
        app.set_visible((app.PublishButton, app.QgcButton, app.SafeStopButton), true)
        app.PublishButton.Position = [494, 674, 140, 38]
        app.PublishButton.Text = "发布并准备"
        app.PublishButton.Enable = false
        app.QgcButton.Position = [644, 674, 140, 38]
        app.QgcButton.Text = "进入 QGC"
        app.SafeStopButton.Position = [794, 674, 140, 38]
        app.SafeStopButton.Text = "安全停止"
    end

    function configure_deploy_workspace(app)
        app.set_top_status("生成代码部署  |  门禁通过  |  构建 Release  |  产物已登记"; state="正常")
        app.configure_section(app.ConfigSectionLabel, "生成配置与操作", [24, 144, 560, 34])
        app.configure_console_workspace(left=614, width=802)
        app.ConfigSectionLabel.Visible = true
        app.ChainSectionLabel.Visible = false
        app.InjectionSectionLabel.Visible = true
        app.set_visible(app.workspace_controls(), false)
        deploy_controls = (
            app.ProfileDropDown, app.DeployTargetDropDown,
            app.BuildModeDropDown, app.OutputDropDown,
        )
        app.set_visible(deploy_controls, true)
        app.set_dropdown_position(app.ProfileDropDown, [24, 192, 560, 32])
        app.ProfileDropDown.Label = "已验证 Profile"
        app.ProfileDropDown.Items = ["Official PID generated-C [已通过]", "PID-INDI generated-C [已通过]", "Linear MPC generated-C [已通过]", "实验控制器 [门禁未通过]"]
        app.ProfileDropDown.Value = "Official PID generated-C [已通过]"
        app.set_dropdown_position(app.DeployTargetDropDown, [24, 246, 560, 32])
        app.set_dropdown_position(app.BuildModeDropDown, [24, 300, 560, 32])
        app.set_dropdown_position(app.OutputDropDown, [24, 354, 560, 32])
        app.OutputDropDown.Items = ["ATTITUDE_THRUST", "BODY_RATE_THRUST", "WRENCH", "ROTOR_COMMAND"]
        app.OutputDropDown.Value = "ATTITUDE_THRUST"

        app.set_visible(app.action_buttons(), false)
        app.set_visible((app.ValidateButton, app.CodegenButton,
            app.ResultButton, app.QgcButton), true)
        app.ValidateButton.Position = [24, 420, 270, 44]
        app.ValidateButton.Text = "检查生成门禁"
        app.CodegenButton.Position = [314, 420, 270, 44]
        app.CodegenButton.Text = "生成 C 代码"
        app.ResultButton.Position = [24, 480, 270, 44]
        app.ResultButton.Text = "打开产物目录"
        app.QgcButton.Position = [314, 480, 270, 44]
        app.QgcButton.Text = "交接至 QGC"
        app.CodegenButton.Enable = true
        app.QgcButton.Enable = true
    end

    function set_mode(app, mode)
        app.CurrentMode = mode
        app.set_button_state(app.OfflineModeButton, mode == "model")
        app.set_button_state(app.LiveModeButton, mode == "live")
        app.set_button_state(app.DeployModeButton, mode == "deploy")
        if mode == "model"
            app.configure_model_workspace()
            app.set_connection_controls(false)
            app.append_console("切换至在线建模验证工作台")
        elseif mode == "live"
            app.configure_live_workspace()
            app.set_connection_controls(true)
            app.append_console("切换至实时联合仿真工作台；实时后端保持未连接")
        else
            app.configure_deploy_workspace()
            app.set_connection_controls(false)
            app.append_console("切换至生成代码部署工作台")
        end
        app.refresh_summary()
    end

    function OfflineModePressed(app, event)
        app.set_mode("model")
    end

    function LiveModePressed(app, event)
        app.set_mode("live")
    end

    function DeployModePressed(app, event)
        app.set_mode("deploy")
    end

    function SelectionChanged(app, event)
        app.sync_vehicle_controls()
        app.refresh_summary()
        if app.CurrentMode == "live"
            app.ConnectionChanged(nothing)
            if !app.live_combination_compatible()
                app.append_console("当前组合超出单机 ATTITUDE_THRUST 实时合同；可保存但不可准备运行"; level="阻断")
            end
        else
            app.append_console("配置已修改；兼容性已自动检查")
        end
    end

    function PresetChanged(app, event)
        if app.CurrentMode == "model"
            app.apply_preset(app.ProfileDropDown.Value)
        elseif app.CurrentMode == "live"
            if app.ProfileDropDown.Value == LIVE_PROFILE_OPTIONS[1]
                app.AugmentationDropDown.Value = "无"
            elseif app.ProfileDropDown.Value == LIVE_PROFILE_OPTIONS[2]
                app.AugmentationDropDown.Value = "awff [已认证]"
            end
        end
        app.sync_vehicle_controls()
        app.refresh_summary()
        app.append_console(app.ProfileDropDown.Value == CUSTOM_PROFILE_LABEL ?
            "进入自由组合模式；所有层级可编辑" :
            "预设已载入：" * app.ProfileDropDown.Value)
    end

    function ConnectionChanged(app, event)
        app.ConnectionStatusLabel.Text = "◆ 配置已修改  |  等待连接测试"
        app.ConnectionStatusLabel.BackgroundColor = MUTED_COLOR
        app.PrepareButton.Enable = false
        app.PublishButton.Enable = false
        app.set_top_status("实时联合仿真  |  等待连接测试  |  Run --"; state="待命")
        app.append_console("连接参数已修改；prepare 保持阻断")
    end

    function TestConnectionPressed(app, event)
        app.TestConnectionButton.Enable = false
        app.ConnectionStatusLabel.Text = "◆ 正在测试 ROS Master / RT1 双向链路"
        app.append_console("开始连接预检：ROS Master / RT1")
        response = LiveCosimBackend.request(
            app.Appfile,
            "connection-test",
            app.ProfileDropDown.Value;
            host=app.TargetHostField.Value,
            port=round(Int, app.Rt1PortField.Value),
            ros_master_uri=app.RosMasterField.Value,
            local_advertised_ip=app.LocalIpField.Value,
            rate_hz=parse(Int, app.TargetRateDropDown.Value),
        )
        connected = get(response, "connection_ok", "false") == "true"
        reason = get(response, "reason_code", "connection_preflight_failed")
        rtt = get(response, "rtt_p95_ms", "")
        wire = get(response, "wire_bytes_per_s", "")
        detail = isempty(rtt) ? "" : "  |  RTT P95 " * rtt * " ms"
        detail *= isempty(wire) ? "" : "  |  wire " * wire * " B/s"
        app.ConnectionStatusLabel.Text = connected ? "● 双向连接通过" * detail : "■ 连接阻断  |  " * reason
        app.ConnectionStatusLabel.BackgroundColor = MUTED_COLOR
        app.TestConnectionButton.Enable = true
        combination_ok = app.live_combination_compatible()
        app.PrepareButton.Enable = connected && parse(Int, app.TargetRateDropDown.Value) == 50 && combination_ok
        app.PublishButton.Enable = app.PrepareButton.Enable
        app.set_top_status("实时联合仿真  |  " * (connected ? "已连接" : "连接阻断") * "  |  Run --";
            state=connected ? "正常" : "阻断")
        if connected && !combination_ok
            app.append_console("连接已通过，但控制器组合不满足单机 ATTITUDE_THRUST 实时合同"; level="阻断")
        else
            app.append_console("连接预检：" * reason * detail; level=connected ? "通过" : "阻断")
        end
    end

    function InjectionChanged(app, event)
        app.InjectionValuesLabel.Text =
            "待应用  风速 " * string(round(app.WindSlider.Value; digits=1)) * " m/s  |  " *
            "电机效率 " * join(string.(round.([
                app.Motor1Slider.Value,
                app.Motor2Slider.Value,
                app.Motor3Slider.Value,
                app.Motor4Slider.Value,
            ]; digits=2)), " / ") *
            "\n实际  风速 0.0 m/s  |  电机效率 1.00 / 1.00 / 1.00 / 1.00"
        app.append_console(app.CurrentMode == "model" ?
            "场景参数已修改；将在下一次模型求解中生效" :
            "实时故障待应用值已修改；尚未发送")
    end

    function ApplyInjectionPressed(app, event)
        app.append_console(app.CurrentMode == "model" ?
            "仿真场景参数已写入当前配置" :
            "故障应用请求未发送；等待实时后端接入"; level=app.CurrentMode == "model" ? "通过" : "待办")
    end

    function RestoreInjectionPressed(app, event)
        app.WindSlider.Value = 0.0
        app.Motor1Slider.Value = 1.0
        app.Motor2Slider.Value = 1.0
        app.Motor3Slider.Value = 1.0
        app.Motor4Slider.Value = 1.0
        app.InjectionChanged(nothing)
        app.append_console(app.CurrentMode == "model" ?
            "仿真场景已恢复默认值" :
            "待应用值已恢复正常；restore 请求未发送")
    end

    function ReviewAction(app, action)
        app.append_console(action * "：界面事件已触发，运行后端未连接"; level="审核")
    end

    function run_offline_batch(app, profile_id)
        if !isfile(OFFLINE_BATCH_RUNNER)
            app.append_console("批量执行器不存在：" * OFFLINE_BATCH_RUNNER; level="错误")
            return
        end
        slug = lowercase(replace(profile_id, r"[^A-Za-z0-9]+" => "-"))
        batch_id = "app-" * slug * "-" * string(round(Int, time() * 1000))
        command_args = [
            "python",
            OFFLINE_BATCH_RUNNER,
            "--batch-id",
            batch_id,
            "--keep-session-open",
        ]
        retry_batch_id = app.LastOfflineProfile == profile_id ? app.LastOfflineBatchId : ""
        if isempty(retry_batch_id)
            append!(command_args, ["--profile-id", profile_id])
        else
            append!(command_args, ["--retry-batch-id", retry_batch_id])
        end
        command = Cmd(command_args; dir=PROJECT_ROOT)
        app.OfflineBatchRunning = true
        app.CurrentOfflineBatchId = batch_id
        app.MilButton.Text = "请求取消"
        app.MilButton.Enable = true
        app.SafeStopButton.Enable = true
        app.ResultButton.Enable = false
        app.LastOfflineBatchManifest = joinpath(
            PROJECT_ROOT,
            "Results",
            "control_platform",
            "offline_batches",
            batch_id,
            "BATCH_MANIFEST.json",
        )
        app.set_top_status("在线建模验证  |  正在运行  |  " * profile_id; state="待命")
        app.append_console("开始 MWORKS 批次：" * profile_id; level="运行")
        @async begin
            try
                process = run(command; wait=false)
                wait(process)
                app.set_top_status("在线建模验证  |  已完成  |  Result.msr 已登记"; state="正常")
                app.append_console("批次完成：" * app.LastOfflineBatchManifest; level="通过")
                app.ResultButton.Enable = true
            catch error
                if isfile(app.LastOfflineBatchManifest)
                    app.set_top_status("在线建模验证  |  批次阻断  |  Manifest 已保留"; state="阻断")
                    app.append_console("批次阻断或取消：" * app.LastOfflineBatchManifest; level="阻断")
                    app.ResultButton.Enable = true
                else
                    app.set_top_status("在线建模验证  |  批次阻断"; state="阻断")
                    app.append_console("批次阻断：" * sprint(showerror, error); level="错误")
                end
            finally
                if isfile(app.LastOfflineBatchManifest)
                    app.LastOfflineBatchId = batch_id
                    app.LastOfflineProfile = profile_id
                end
                app.OfflineBatchRunning = false
                app.CurrentOfflineBatchId = ""
                app.MilButton.Text = "开始仿真"
                app.MilButton.Enable = true
                app.SafeStopButton.Enable = false
            end
        end
    end

    function request_offline_cancel(app)
        if !app.OfflineBatchRunning || isempty(app.CurrentOfflineBatchId)
            app.append_console("当前没有正在运行的模型批次"; level="提示")
            return
        end
        batch_dir = joinpath(PROJECT_ROOT, "Results", "control_platform", "offline_batches", app.CurrentOfflineBatchId)
        for _ in 1:20
            isdir(batch_dir) && break
            sleep(0.05)
        end
        command = Cmd([
            "python",
            OFFLINE_BATCH_RUNNER,
            "--request-cancel",
            app.CurrentOfflineBatchId,
        ]; dir=PROJECT_ROOT)
        try
            run(command)
            app.append_console("已请求安全取消；等待当前 Profile 清理完成"; level="运行")
            app.MilButton.Enable = false
        catch error
            app.append_console("取消请求失败：" * sprint(showerror, error); level="错误")
        end
    end

    function ValidatePressed(app, event)
        if app.CurrentMode == "live"
            response = app.refresh_live_capability("validate")
            app.append_console("实时 Profile 校验：" * get(response, "reason_code", "unknown"))
        else
            app.ReviewAction("校验配置")
        end
    end
    function PublishPressed(app, event)
        if app.CurrentMode == "live"
            response = app.refresh_live_capability("prepare")
            app.append_console("发布并准备：" * get(response, "reason_code", "unknown"))
        else
            app.ReviewAction("发布 Profile")
        end
    end
    function PreparePressed(app, event)
        if app.CurrentMode == "live"
            response = app.refresh_live_capability("prepare")
            app.append_console("实时 prepare：" * get(response, "reason_code", "unknown"))
        else
            app.ReviewAction("准备运行")
        end
    end
    function QgcPressed(app, event); app.ReviewAction("进入 QGC"); end
    function SafeStopPressed(app, event)
        if app.CurrentMode == "model"
            app.request_offline_cancel()
        else
            app.ReviewAction("请求安全停止")
        end
    end
    function OpenModelPressed(app, event); app.ReviewAction("打开模型"); end
    function MilPressed(app, event)
        if app.OfflineBatchRunning
            app.request_offline_cancel()
            return
        end
        if app.CurrentMode == "model" && haskey(OFFLINE_PROFILES, app.ProfileDropDown.Value)
            item = OFFLINE_PROFILES[app.ProfileDropDown.Value]
            if item.available && app.preset_matches_selection(item)
                app.run_offline_batch(item.profile)
            else
                app.append_console("Profile 与当前 UAV 数量、任务或控制链不一致；未启动仿真"; level="阻断")
            end
        else
            app.ReviewAction("运行 MWORKS MIL")
        end
    end
    function CodegenPressed(app, event); app.ReviewAction("生成 C 代码"); end
    function ResultPressed(app, event)
        if app.CurrentMode == "model" && !isempty(app.LastOfflineBatchManifest)
            if !isfile(OFFLINE_ANIMATION_RESUMER)
                app.append_console("动画恢复器不存在：" * OFFLINE_ANIMATION_RESUMER; level="错误")
                return
            end
            app.ResultButton.Enable = false
            app.append_console("正在恢复当前 MWORKS 结果动画"; level="运行")
            @async begin
                try
                    command = Cmd(["python", OFFLINE_ANIMATION_RESUMER]; dir=PROJECT_ROOT)
                    output = read(command, String)
                    app.append_console("当前结果动画已恢复：" * strip(output); level="通过")
                catch error
                    app.append_console("恢复动画失败；请重新执行当前仿真：" * sprint(showerror, error); level="错误")
                finally
                    app.ResultButton.Enable = true
                end
            end
        else
            app.append_console("请先完成一次仿真，再打开当前结果"; level="提示")
        end
    end

    function set_dropdown_position(app, control, position)
        control.Position = position
    end

    function configure_dropdown(app, control, label, position, items, value)
        app.set_dropdown_position(control, position)
        control.Label = label
        control.Items = items
        control.Value = value
        control.ValueChangedFcn = "SelectionChanged"
    end

    function configure_slider(app, control, label, position, value, limits, ticks, labels)
        control.Position = position
        control.Label = label
        control.Value = value
        control.Limits = limits
        control.MajorTicks = ticks
        control.MajorTickLabels = labels
        control.ValueChangedFcn = "InjectionChanged"
    end

    function configure_action(app, button, text, callback, position)
        button.Position = position
        button.Text = text
        button.ButtonPushedFcn = callback
        button.FontWeight = "bold"
    end

    function configure_section(app, label, text, position)
        label.Position = position
        label.Text = "  " * text
        label.FontWeight = "bold"
        label.FontColor = [1.0, 1.0, 1.0]
        label.BackgroundColor = SECTION_COLOR
    end

    function createComponents(app)
        app.UIFigure = TyAppDesigner.uifigure(Visible=false)
        app.UIFigure.Position = [30, 30, 1440, 720]
        app.UIFigure.Name = "MoSim Model Studio 0.6 UI Review"
        app.UIFigure.Color = [0.96, 0.97, 0.97]

        app.TitleLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.TitleLabel.Position = [24, 16, 520, 34]
        app.TitleLabel.Text = "MoSim Model Studio"
        app.TitleLabel.FontSize = 24
        app.TitleLabel.FontWeight = "bold"
        app.TitleLabel.FontColor = [0.08, 0.16, 0.22]

        app.SubtitleLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.SubtitleLabel.Position = [26, 50, 900, 22]
        app.SubtitleLabel.Text = "控制器配置、模型验证与 QGC 运行交接"
        app.SubtitleLabel.FontColor = [0.35, 0.42, 0.47]

        app.OfflineModeButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.OfflineModeButton, "在线建模验证", "OfflineModePressed", [24, 82, 190, 40])
        app.LiveModeButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.LiveModeButton, "实时联合仿真", "LiveModePressed", [218, 82, 190, 40])
        app.DeployModeButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.DeployModeButton, "生成代码部署", "DeployModePressed", [412, 82, 190, 40])

        app.ModeStatusLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ModeStatusLabel.Position = [620, 82, 796, 40]
        app.ModeStatusLabel.HorizontalAlignment = "right"
        app.ModeStatusLabel.WordWrap = true
        app.ModeStatusLabel.FontColor = [0.25, 0.32, 0.36]

        app.ConfigSectionLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.configure_section(app.ConfigSectionLabel, "控制链与实验 Profile", [24, 144, 420, 34])
        app.ChainSectionLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.configure_section(app.ChainSectionLabel, "职责、接口与能力门禁", [468, 144, 470, 34])
        app.InjectionSectionLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.configure_section(app.InjectionSectionLabel, "故障注入与运行状态", [962, 144, 454, 34])

        app.ProfileDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.ProfileDropDown, "实验 Profile", [24, 192, 420, 32], ["正在加载..."], "正在加载...")
        app.ProfileDropDown.ValueChangedFcn = "PresetChanged"
        app.VehicleCountDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.VehicleCountDropDown, "UAV 数量", [24, 238, 210, 32], VEHICLE_COUNT_OPTIONS, "1")
        app.MapDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.MapDropDown, "地图", [254, 238, 210, 32], MAP_OPTIONS, MAP_OPTIONS[1])
        app.MissionDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.MissionDropDown, "任务轨迹", [24, 240, 420, 32], ["起飞-悬停-降落"], "起飞-悬停-降落")
        app.PositionDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.PositionDropDown, "位置 / 平动外环", [24, 288, 420, 32], ["PX4CTRL 官方位置外环 PID"], "PX4CTRL 官方位置外环 PID")
        app.AttitudeDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.AttitudeDropDown, "姿态 / 角速度内环", [24, 336, 420, 32], ["PX4 内置姿态/角速度环 [锁定]"], "PX4 内置姿态/角速度环 [锁定]")
        app.AugmentationDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.AugmentationDropDown, "增强与扰动补偿", [24, 384, 420, 32], ["无", "AWFF", "L1 [门禁待通过]", "DOB/ESO [门禁待通过]", "模糊补偿 [门禁待通过]", "神经网络补偿 [门禁待通过]"], "无")
        app.SafetyDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.SafetyDropDown, "安全层", [24, 432, 420, 32], ["基础限幅", "QP Safety Filter [门禁待通过]", "Return-and-Land [门禁待通过]", "CBF [门禁待通过]"], "基础限幅")
        app.FaultDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.FaultDropDown, "故障容错层", [24, 468, 420, 32], MODEL_FAULT_OPTIONS, MODEL_FAULT_OPTIONS[1])
        app.FormationDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.FormationDropDown, "编队控制层", [24, 514, 420, 32], MODEL_FORMATION_OPTIONS, MODEL_FORMATION_OPTIONS[1])
        app.OutputDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.OutputDropDown, "输出边界", [24, 480, 420, 32], ["ATTITUDE_THRUST [锁定]"], "ATTITUDE_THRUST [锁定]")

        app.ProfileSummaryLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ProfileSummaryLabel.Position = [24, 528, 420, 118]
        app.ProfileSummaryLabel.VerticalAlignment = "top"
        app.ProfileSummaryLabel.WordWrap = true
        app.ProfileSummaryLabel.BackgroundColor = [0.91, 0.94, 0.95]

        app.CapabilityLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.CapabilityLabel.Position = [24, 654, 420, 76]
        app.CapabilityLabel.VerticalAlignment = "top"
        app.CapabilityLabel.WordWrap = true

        app.TargetHostField = TyAppDesigner.uieditfield(app.UIFigure)
        app.TargetHostField.Position = [468, 192, 220, 32]
        app.TargetHostField.Label = "目标 MWORKS / ROS 主机"
        app.TargetHostField.Value = "127.0.0.1"
        app.TargetHostField.ValueChangedFcn = "ConnectionChanged"

        app.Rt1PortField = TyAppDesigner.uinumericeditfield(app.UIFigure)
        app.Rt1PortField.Position = [704, 192, 100, 32]
        app.Rt1PortField.Label = "RT1 UDP 端口"
        app.Rt1PortField.Value = 49020
        app.Rt1PortField.Limits = [1, 65535]
        app.Rt1PortField.ValueChangedFcn = "ConnectionChanged"

        app.TargetRateDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.TargetRateDropDown, "目标频率", [820, 192, 118, 32], ["50", "100", "200"], "200")
        app.TargetRateDropDown.ValueChangedFcn = "ConnectionChanged"

        app.RosMasterField = TyAppDesigner.uieditfield(app.UIFigure)
        app.RosMasterField.Position = [468, 240, 300, 32]
        app.RosMasterField.Label = "ROS Master URI"
        app.RosMasterField.Value = "http://127.0.0.1:11311"
        app.RosMasterField.ValueChangedFcn = "ConnectionChanged"

        app.LocalIpField = TyAppDesigner.uieditfield(app.UIFigure)
        app.LocalIpField.Position = [784, 240, 154, 32]
        app.LocalIpField.Label = "本机广播 IP"
        app.LocalIpField.Value = "auto"
        app.LocalIpField.ValueChangedFcn = "ConnectionChanged"

        app.TestConnectionButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.TestConnectionButton, "测试连接", "TestConnectionPressed", [468, 290, 132, 36])

        app.ConnectionStatusLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ConnectionStatusLabel.Position = [612, 286, 326, 48]
        app.ConnectionStatusLabel.Text = "◆ 尚未测试  |  200 Hz 候选目标"
        app.ConnectionStatusLabel.WordWrap = true
        app.ConnectionStatusLabel.BackgroundColor = MUTED_COLOR

        app.DeployTargetDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.DeployTargetDropDown, "生成目标", [24, 246, 430, 32], ["通用 C 库", "px4ctrl / Gazebo 控制器", "PX4 模块 [接口预留]"], "px4ctrl / Gazebo 控制器")

        app.BuildModeDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.BuildModeDropDown, "构建类型", [24, 300, 430, 32], ["Release", "Debug", "SIL 对比"], "Release")

        app.TargetUavDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.TargetUavDropDown, "故障目标", [494, 192, 440, 32], ["UAV 1"], "UAV 1")

        app.ChainLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ChainLabel.Position = [468, 346, 470, 100]
        app.ChainLabel.Text = ""
        app.ChainLabel.VerticalAlignment = "top"
        app.ChainLabel.WordWrap = true
        app.ChainLabel.BackgroundColor = [0.89, 0.94, 0.96]

        app.ContractLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ContractLabel.Position = [468, 458, 470, 96]
        app.ContractLabel.Text = ""
        app.ContractLabel.VerticalAlignment = "top"
        app.ContractLabel.WordWrap = true
        app.ContractLabel.BackgroundColor = [0.94, 0.95, 0.95]

        app.TimingLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.TimingLabel.Position = [468, 566, 470, 164]
        app.TimingLabel.Text = ""
        app.TimingLabel.VerticalAlignment = "top"
        app.TimingLabel.WordWrap = true
        app.TimingLabel.BackgroundColor = WAIT_COLOR

        app.WindSlider = TyAppDesigner.uislider(app.UIFigure)
        app.configure_slider(app.WindSlider, "风速待应用值（m/s，方向固定）", [962, 194, 454, 52], 0.0, [0.0, 20.0], [0.0, 5.0, 10.0, 15.0, 20.0], ["0", "5", "10", "15", "20"])
        app.Motor1Slider = TyAppDesigner.uislider(app.UIFigure)
        app.configure_slider(app.Motor1Slider, "电机 1 效率", [962, 254, 454, 52], 1.0, [0.0, 1.0], [0.0, 0.5, 1.0], ["0", "50%", "100%"])
        app.Motor2Slider = TyAppDesigner.uislider(app.UIFigure)
        app.configure_slider(app.Motor2Slider, "电机 2 效率", [962, 314, 454, 52], 1.0, [0.0, 1.0], [0.0, 0.5, 1.0], ["0", "50%", "100%"])
        app.Motor3Slider = TyAppDesigner.uislider(app.UIFigure)
        app.configure_slider(app.Motor3Slider, "电机 3 效率", [962, 374, 454, 52], 1.0, [0.0, 1.0], [0.0, 0.5, 1.0], ["0", "50%", "100%"])
        app.Motor4Slider = TyAppDesigner.uislider(app.UIFigure)
        app.configure_slider(app.Motor4Slider, "电机 4 效率", [962, 434, 454, 52], 1.0, [0.0, 1.0], [0.0, 0.5, 1.0], ["0", "50%", "100%"])

        app.InjectionValuesLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.InjectionValuesLabel.Position = [962, 498, 454, 94]
        app.InjectionValuesLabel.VerticalAlignment = "top"
        app.InjectionValuesLabel.WordWrap = true
        app.InjectionValuesLabel.BackgroundColor = [0.94, 0.95, 0.95]

        app.ApplyInjectionButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.ApplyInjectionButton, "应用", "ApplyInjectionPressed", [962, 604, 216, 36])
        app.RestoreInjectionButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.RestoreInjectionButton, "恢复正常", "RestoreInjectionPressed", [1200, 604, 216, 36])

        app.ManifestLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ManifestLabel.Position = [962, 652, 454, 78]
        app.ManifestLabel.Text = "运行状态\nRunManifest：尚未生成\nProfile：未冻结  |  QGC：未交接  |  实际故障：正常"
        app.ManifestLabel.VerticalAlignment = "top"
        app.ManifestLabel.WordWrap = true
        app.ManifestLabel.BackgroundColor = MUTED_COLOR

        app.ValidateButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.ValidateButton, "校验配置", "ValidatePressed", [24, 754, 140, 38])
        app.PublishButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.PublishButton, "发布 Profile", "PublishPressed", [176, 754, 140, 38])
        app.PrepareButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.PrepareButton, "准备运行", "PreparePressed", [328, 754, 140, 38])
        app.QgcButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.QgcButton, "进入 QGC", "QgcPressed", [480, 754, 140, 38])
        app.SafeStopButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.SafeStopButton, "请求安全停止", "SafeStopPressed", [632, 754, 140, 38])
        app.OpenModelButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.OpenModelButton, "打开模型", "OpenModelPressed", [784, 754, 140, 38])
        app.MilButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.MilButton, "运行 MWORKS MIL", "MilPressed", [936, 754, 150, 38])
        app.CodegenButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.CodegenButton, "生成 C 代码", "CodegenPressed", [1098, 754, 140, 38])
        app.ResultButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.ResultButton, "打开结果", "ResultPressed", [1250, 754, 166, 38])

        app.StatusLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.StatusLabel.Position = [964, 192, 452, 456]
        app.StatusLabel.VerticalAlignment = "top"
        app.StatusLabel.HorizontalAlignment = "left"
        app.StatusLabel.WordWrap = true
        app.StatusLabel.BackgroundColor = CONSOLE_COLOR
        app.StatusLabel.FontColor = CONSOLE_TEXT_COLOR

        app.ConsoleToggleButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.ConsoleToggleButton, "收起日志", "ToggleConsolePressed", [24, 738, 112, 28])
        app.ConsoleClearButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.ConsoleClearButton, "清空", "ClearConsolePressed", [146, 738, 76, 28])

        app.set_mode("model")
        app.InjectionChanged(nothing)
        app.append_console("Model Studio 已就绪"; level="系统")
        app.UIFigure.Visible = true
    end

    function initApp(app)
        app.Appname = @__MODULE__
        app.Appfile = @__FILE__
        app.ConsoleLines = String[]
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
