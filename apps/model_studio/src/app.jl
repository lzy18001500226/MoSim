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
const IMPLEMENTED_COLOR = [0.86, 0.92, 0.98]
const WAIT_COLOR = [0.98, 0.93, 0.80]
const MUTED_COLOR = [0.93, 0.94, 0.94]
const CONSOLE_COLOR = [0.07, 0.10, 0.12]
const CONSOLE_TEXT_COLOR = [0.82, 0.91, 0.86]
const HIDDEN_CONTROL_POSITION = [-2048, -2048, 1, 1]
const PROJECT_ROOT = normpath(joinpath(@__DIR__, "..", "..", ".."))
const OFFLINE_BATCH_RUNNER = joinpath(PROJECT_ROOT, "Scripts", "mworks", "run_offline_profile_batch.py")
const OFFLINE_ANIMATION_RESUMER = joinpath(PROJECT_ROOT, "Scripts", "mworks", "resume_offline_profile_animation.py")
const OFFLINE_BATCH_INDEX = joinpath(PROJECT_ROOT, "Results", "control_platform", "offline_batches", "BATCH_INDEX.json")
const OPEN_MODEL_SCRIPT = joinpath(PROJECT_ROOT, "Scripts", "ui", "open_model_studio_model.py")
const MODEL_TASK_CONFIG_WRITER = joinpath(PROJECT_ROOT, "Scripts", "ui", "model_studio_task_config.py")

function run_process_in_directory(command_args, directory)
    command = Cmd(Cmd(command_args); dir=directory)
    process = run(command; wait=false)
    wait(process)
    success(process) || error("process exited with code " * string(process.exitcode))
end

const CUSTOM_PROFILE_LABEL = "自定义组合"
const VEHICLE_COUNT_OPTIONS = string.(1:9)
const MAP_OPTIONS = ["空白地图", "Factory 避障地图"]
const MODEL_MAP_OPTIONS = ["空白地图", "OpenBlocks 避障地图"]
const LIVE_PROFILE_OPTIONS = [
    "official_pid_attitude_thrust_v1 [候选]",
    "official_pid + awff_v1 [候选]",
]
const SINGLE_UAV_MISSION_OPTIONS = ["起飞-悬停-降落", "爬升", "八字轨迹", "螺旋轨迹"]
const THREE_UAV_MISSION_OPTIONS = ["三机三角编队 8 字"]
const MODEL_MISSION_OPTIONS = vcat(SINGLE_UAV_MISSION_OPTIONS, THREE_UAV_MISSION_OPTIONS)
const CONTROLLER_FAMILIES = [
    "PID 族", "线性鲁棒族", "非线性自适应族", "滑模族",
    "预测控制族", "几何/平坦族", "学习增强族", "自研控制器",
]
const CONTROLLER_CATALOG = [
    (id="official_pid", family="PID 族", display="official_pid [已认证]", status="已认证", openable=true),
    (id="cascade_pid", family="PID 族", display="cascade_pid [已实现]", status="已实现", openable=true),
    (id="gain_scheduled_pid", family="PID 族", display="gain_scheduled_pid [已实现]", status="已实现", openable=true),
    (id="fuzzy_pid", family="PID 族", display="fuzzy_pid [已实现]", status="已实现", openable=true),
    (id="neural_pid", family="PID 族", display="neural_pid [已实现]", status="已实现", openable=true),
    (id="fopid", family="PID 族", display="fopid [已实现]", status="已实现", openable=true),
    (id="fixed_awff_pid", family="PID 族", display="fixed_awff_pid [已实现]", status="已实现", openable=true),
    (id="fixed_awff_l1_residual", family="PID 族", display="fixed_awff_l1_residual [已实现]", status="已实现", openable=true),
    (id="fixed_awff_l1_indi", family="PID 族", display="fixed_awff_l1_indi [已实现]", status="已实现", openable=true),
    (id="pid_awff_linear_eso", family="PID 族", display="pid_awff_linear_eso [待接入]", status="待接入", openable=false),

    (id="lqr_baseline", family="线性鲁棒族", display="lqr_baseline [已实现]", status="已实现", openable=true),
    (id="lqi_baseline", family="线性鲁棒族", display="lqi_baseline [已实现]", status="已实现", openable=true),
    (id="lqg", family="线性鲁棒族", display="lqg [已实现]", status="已实现", openable=true),
    (id="h2_state_feedback", family="线性鲁棒族", display="h2_state_feedback [已实现]", status="已实现", openable=true),
    (id="hinf_hover_wrench", family="线性鲁棒族", display="hinf_hover_wrench [已实现]", status="已实现", openable=true),
    (id="pole_placement_luenberger", family="线性鲁棒族", display="pole_placement_luenberger [已实现]", status="已实现", openable=true),

    (id="backstepping_baseline", family="非线性自适应族", display="backstepping_baseline [已实现]", status="已实现", openable=true),
    (id="adaptive_backstepping", family="非线性自适应族", display="adaptive_backstepping [已实现]", status="已实现", openable=true),
    (id="feedback_linearization", family="非线性自适应族", display="feedback_linearization [已实现]", status="已实现", openable=true),
    (id="mrac", family="非线性自适应族", display="mrac [已实现]", status="已实现", openable=true),
    (id="ndi", family="非线性自适应族", display="ndi [已实现]", status="已实现", openable=true),
    (id="passivity_based_control", family="非线性自适应族", display="passivity_based_control [已实现]", status="已实现", openable=true),

    (id="integral_smc", family="滑模族", display="integral_smc [已实现]", status="已实现", openable=true),
    (id="terminal_smc", family="滑模族", display="terminal_smc [已实现]", status="已实现", openable=true),
    (id="nonsingular_terminal_smc", family="滑模族", display="nonsingular_terminal_smc [已实现]", status="已实现", openable=true),
    (id="super_twisting_smc", family="滑模族", display="super_twisting_smc [已实现]", status="已实现", openable=true),
    (id="adaptive_smc", family="滑模族", display="adaptive_smc [已实现]", status="已实现", openable=true),
    (id="fuzzy_smc", family="滑模族", display="fuzzy_smc [已实现]", status="已实现", openable=true),
    (id="smc_boundary_layer", family="滑模族", display="smc_boundary_layer [已实现]", status="已实现", openable=true),

    (id="linear_mpc", family="预测控制族", display="linear_mpc [已实现]", status="已实现", openable=true),
    (id="robust_mpc", family="预测控制族", display="robust_mpc [已实现]", status="已实现", openable=true),
    (id="adaptive_mpc", family="预测控制族", display="adaptive_mpc [已实现]", status="已实现", openable=true),
    (id="tube_mpc", family="预测控制族", display="tube_mpc [已实现]", status="已实现", openable=true),
    (id="explicit_gain_scheduled_mpc", family="预测控制族", display="explicit_gain_scheduled_mpc [已实现]", status="已实现", openable=true),
    (id="ilqr", family="预测控制族", display="ilqr [已实现]", status="已实现", openable=true),
    (id="mppi", family="预测控制族", display="mppi [已实现]", status="已实现", openable=true),
    (id="nmpc_outer", family="预测控制族", display="nmpc_outer [已实现]", status="已实现", openable=true),
    (id="fixed_linear_mpc_l1_indi", family="预测控制族", display="fixed_linear_mpc_l1_indi [已实现]", status="已实现", openable=true),
    (id="fixed_qp_nmpc_l1_indi_cbf", family="预测控制族", display="fixed_qp_nmpc_l1_indi_cbf [已实现]", status="已实现", openable=true),

    (id="se3_basic", family="几何/平坦族", display="se3_basic [已实现]", status="已实现", openable=true),
    (id="dfbc_basic", family="几何/平坦族", display="dfbc_basic [已实现]", status="已实现", openable=true),
    (id="dfbc_high_order_attitude", family="几何/平坦族", display="dfbc_high_order_attitude [已实现]", status="已实现", openable=true),
    (id="dfbc_high_order_bodyrate", family="几何/平坦族", display="dfbc_high_order_bodyrate [已实现]", status="已实现", openable=true),
    (id="dfbc_smooth_robust_attitude", family="几何/平坦族", display="dfbc_smooth_robust_attitude [已实现]", status="已实现", openable=true),
    (id="dfbc_smooth_robust_bodyrate", family="几何/平坦族", display="dfbc_smooth_robust_bodyrate [已实现]", status="已实现", openable=true),

    (id="trained_neural_residual", family="学习增强族", display="trained_neural_residual [已实现]", status="已实现", openable=true),
    (id="rl_gain_scheduler", family="学习增强族", display="rl_gain_scheduler [已实现]", status="已实现", openable=true),
    (id="px4ctrl", family="自研控制器", display="px4ctrl [已实现]", status="已实现", openable=true),
]
const LEGACY_PROFILE_CONTROLLERS = [
    (id="improved_pid", family="PID 族", display="improved_pid [已认证]", status="已认证", openable=false),
    (id="linear_mpc", family="预测控制族", display="linear_mpc [已认证]", status="已认证", openable=true),
    (id="fault_compensation", family="PID 族", display="fault_compensation [已认证]", status="已认证", openable=false),
]
const LIVE_BASELINE_CONTROLLER = "official_pid [已认证]"
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
const MODEL_TASKS = [
    (id="climb_path_50s", label="基准：ClimbPath 50 s", duration_s=50.0, vehicle_count=1, map_id="blank", controller_ids=["official_pid", "px4ctrl"], injection_supported=true),
    (id="hover", label="悬停保持", duration_s=35.0, vehicle_count=1, map_id="blank", controller_ids=["official_pid", "px4ctrl"], injection_supported=true),
    (id="step_response", label="阶跃响应", duration_s=45.0, vehicle_count=1, map_id="blank", controller_ids=["official_pid", "px4ctrl"], injection_supported=true),
    (id="figure8", label="8 字轨迹", duration_s=50.0, vehicle_count=1, map_id="blank", controller_ids=["official_pid", "px4ctrl"], injection_supported=true),
    (id="spiral", label="螺旋上升", duration_s=50.0, vehicle_count=1, map_id="blank", controller_ids=["official_pid", "px4ctrl"], injection_supported=true),
    (id="single_uav_autonomous_avoidance", label="单机自主避障", duration_s=80.0, vehicle_count=1, map_id="openblocks", controller_ids=["px4ctrl"], injection_supported=true),
    (id="three_uav_figure8", label="三机三角编队 8 字", duration_s=50.0, vehicle_count=3, map_id="blank", controller_ids=["px4ctrl"], injection_supported=true),
    (id="three_uav_autonomous_avoidance", label="三机自主避障", duration_s=360.0, vehicle_count=3, map_id="openblocks", controller_ids=["linear_mpc"], injection_supported=false),
    (id="multi_uav_route_unavailable", label="多机任务（当前无已登记模型入口）", duration_s=0.0, vehicle_count=0, map_id="blank", controller_ids=String[], injection_supported=false),
]
const MODEL_TASK_LABELS = [task.label for task in MODEL_TASKS if task.vehicle_count == 1]

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
    OfflineModeButton::Any = nothing
    LiveModeButton::Any = nothing
    DeployModeButton::Any = nothing
    AssistantModeButton::Any = nothing
    ModeStatusLabel::Any = nothing

    ConfigSectionLabel::Any = nothing
    ChainSectionLabel::Any = nothing
    InjectionSectionLabel::Any = nothing

    TaskDropDown::Any = nothing
    ProfileDropDown::Any = nothing
    VehicleCountDropDown::Any = nothing
    MapDropDown::Any = nothing
    MissionDropDown::Any = nothing
    ControllerFamilyDropDown::Any = nothing
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
    FaultStartTimeField::Any = nothing
    WindSlider::Any = nothing
    ParameterMismatchSlider::Any = nothing
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

    AssistantContextLabel::Any = nothing
    AssistantChatLabel::Any = nothing
    AssistantInputField::Any = nothing
    AssistantSendButton::Any = nothing
    AssistantExplainButton::Any = nothing
    AssistantMworksGuideButton::Any = nothing
    AssistantQgcGuideButton::Any = nothing
    AssistantResultGuideButton::Any = nothing
    AssistantClearButton::Any = nothing
    AssistantStatusLabel::Any = nothing

    # ObjectOriented's field parser requires literal defaults; bind source
    # metadata during initApp instead of using macro expressions as defaults.
    Appname::Any = nothing
    Appfile::Any = ""
    CurrentMode::String = "live"
    LastOperationalMode::String = "model"
    LastOfflineBatchManifest::String = ""
    LastOfflineBatchId::String = ""
    LastOfflineProfile::String = ""
    CurrentOfflineBatchId::String = ""
    OfflineBatchRunning::Bool = false
    TaskConfigPath::String = ""
    TaskConfigDirty::Bool = true
    ConsoleLines::Any = nothing
    AssistantLines::Any = nothing
    ConsoleExpanded::Bool = true

    function append_console(app, message; level="信息")
        normalized = replace(string(message), '\n' => "  |  ")
        timestamp = Dates.format(Dates.now(), "HH:MM:SS")
        push!(app.ConsoleLines, timestamp * "  [" * level * "]  " * normalized)
        length(app.ConsoleLines) > 40 && deleteat!(app.ConsoleLines, 1:length(app.ConsoleLines)-40)
        visible_lines = app.ConsoleExpanded ? 6 : 1
        app.StatusLabel.Text = join(last(app.ConsoleLines, min(visible_lines, length(app.ConsoleLines))), "\n")
    end

    function assistant_operational_mode_label(app)
        return app.LastOperationalMode == "model" ? "在线建模验证" :
            (app.LastOperationalMode == "live" ? "实时联合仿真" : "代码生成")
    end

    function refresh_assistant_context(app)
        app.AssistantContextLabel === nothing && return
        app.AssistantContextLabel.Text =
            "当前配置\n\n" *
            "来源  " * app.assistant_operational_mode_label() * "\n" *
            "Profile  " * app.ProfileDropDown.Value * "\n" *
            "任务  " * app.MissionDropDown.Value * "\n\n" *
            "控制链\n" *
            "外环  " * app.PositionDropDown.Value * "\n" *
            "增强  " * app.AugmentationDropDown.Value * "\n" *
            "输出  " * app.OutputDropDown.Value
    end

    function append_assistant(app, author, message)
        timestamp = Dates.format(Dates.now(), "HH:MM")
        normalized = string(message)
        push!(app.AssistantLines, author * "  " * timestamp * "\n" * normalized)
        length(app.AssistantLines) > 8 && deleteat!(app.AssistantLines, 1:length(app.AssistantLines)-8)
        app.AssistantChatLabel.Text = join(app.AssistantLines, "\n\n")
    end

    function assistant_reply(app, prompt)
        normalized = lowercase(strip(prompt))
        if occursin("控制", normalized) || occursin("controller", normalized)
            return "当前外环为“" * app.PositionDropDown.Value * "”。控制器选择决定输出合同；增强层只允许叠加与该合同兼容的模块。"
        elseif occursin("mworks", normalized) || occursin("模型", normalized) || occursin("仿真", normalized)
            return "先在“在线建模验证”确认配置，再点击“打开仿真模型”。模型由 MWORKS 打开和运行，结果由原生结果查看器分析。"
        elseif occursin("qgc", normalized) || occursin("地面站", normalized) || occursin("起飞", normalized)
            return "QGC 选择已发布的 Profile，并负责连接、解锁、起飞、任务、降落和安全停止。这里不直接向飞行端发送命令。"
        elseif occursin("故障", normalized) || occursin("风", normalized) || occursin("电机", normalized)
            return "离线页面的风扰和电机效率属于场景配置；飞行侧故障由 QGC 按已冻结 Profile 发起离散应用或恢复请求。"
        elseif occursin("结果", normalized) || occursin("result", normalized) || occursin("曲线", normalized)
            return "Result.msr 和曲线仍由 MWORKS 结果查看器负责。完成仿真后，将结果放入 Profile 的默认结果目录，再从结果入口打开。"
        end
        return "我已读取当前配置。可以继续询问控制链、MWORKS 模型、QGC 操作、故障注入或结果查看。"
    end

    function AssistantSendPressed(app, event)
        prompt = strip(app.AssistantInputField.Value)
        if isempty(prompt)
            app.append_assistant("MoSim 助手", "请先输入问题。")
            return
        end
        app.append_assistant("你", prompt)
        app.AssistantInputField.Value = ""
        app.append_assistant("MoSim 助手", app.assistant_reply(prompt))
    end

    function AssistantExplainPressed(app, event)
        app.append_assistant("MoSim 助手",
            "当前控制链：任务参考 -> " * app.PositionDropDown.Value * " -> " *
            app.AttitudeDropDown.Value * " -> " * app.OutputDropDown.Value * "。")
    end

    function AssistantMworksGuidePressed(app, event)
        app.append_assistant("MoSim 助手",
            "MWORKS 操作顺序：确认配置 -> 打开模型 -> 在 MWORKS 中运行 -> 将 Result.msr 放入默认结果目录 -> 在原生结果查看器分析。")
    end

    function AssistantQgcGuidePressed(app, event)
        app.append_assistant("MoSim 助手",
            "QGC 操作顺序：选择已发布 Profile -> 连接飞行端 -> 解锁 -> 起飞悬停 -> 执行任务 -> 降落或安全停止。")
    end

    function AssistantResultGuidePressed(app, event)
        app.append_assistant("MoSim 助手",
            "结果入口只定位当前 Profile 的默认目录和 Result.msr；曲线、动画和回放继续由 MWORKS 原生结果查看器完成。")
    end

    function AssistantClearPressed(app, event)
        empty!(app.AssistantLines)
        app.append_assistant("MoSim 助手", "已清空对话。我已保留当前实验配置上下文。")
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
            if visible
                control.Visible = true
            else
                # TyAppDesigner hidden controls can still receive mouse input.
                # Park them outside the figure before another workspace reuses the area.
                control.Visible = false
                control.Position = HIDDEN_CONTROL_POSITION
            end
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
            app.TaskDropDown,
            app.ProfileDropDown, app.VehicleCountDropDown, app.MapDropDown,
            app.MissionDropDown, app.ControllerFamilyDropDown, app.PositionDropDown,
            app.AttitudeDropDown, app.AugmentationDropDown, app.SafetyDropDown,
            app.FaultDropDown, app.FormationDropDown, app.OutputDropDown,
            app.ProfileSummaryLabel, app.CapabilityLabel,
            app.TargetHostField, app.Rt1PortField,
            app.RosMasterField, app.LocalIpField, app.TargetRateDropDown,
            app.TestConnectionButton, app.ConnectionStatusLabel,
            app.DeployTargetDropDown, app.BuildModeDropDown, app.ChainLabel,
            app.ContractLabel, app.TimingLabel, app.TargetUavDropDown,
            app.FaultStartTimeField,
            app.WindSlider, app.ParameterMismatchSlider, app.Motor1Slider,
            app.Motor2Slider, app.Motor3Slider, app.Motor4Slider,
            app.InjectionValuesLabel, app.ApplyInjectionButton,
            app.RestoreInjectionButton, app.ManifestLabel,
            app.AssistantContextLabel, app.AssistantChatLabel,
            app.AssistantInputField, app.AssistantSendButton,
            app.AssistantExplainButton, app.AssistantMworksGuideButton,
            app.AssistantQgcGuideButton, app.AssistantResultGuideButton,
            app.AssistantClearButton, app.AssistantStatusLabel,
        )
    end

    function assistant_controls(app)
        return (
            app.AssistantContextLabel, app.AssistantChatLabel,
            app.AssistantInputField, app.AssistantSendButton,
            app.AssistantExplainButton, app.AssistantMworksGuideButton,
            app.AssistantQgcGuideButton, app.AssistantResultGuideButton,
            app.AssistantClearButton, app.AssistantStatusLabel,
        )
    end

    function controller_entries(app)
        return vcat(CONTROLLER_CATALOG, LEGACY_PROFILE_CONTROLLERS)
    end

    function selected_controller_entry(app)
        return app.controller_entry(app.PositionDropDown.Value)
    end

    function controller_entry(app, display)
        for entry in app.controller_entries()
            entry.display == display && return entry
        end
        return nothing
    end

    function controller_options_for_family(app, family; include_legacy=false)
        entries = [entry for entry in CONTROLLER_CATALOG if entry.family == family]
        if include_legacy
            append!(entries, [entry for entry in LEGACY_PROFILE_CONTROLLERS if entry.family == family])
        end
        return [entry.display for entry in entries]
    end

    function controller_status_color(app, entry)
        entry === nothing && return MUTED_COLOR
        return entry.status == "已认证" ? READY_COLOR :
            (entry.status == "已实现" ? IMPLEMENTED_COLOR : MUTED_COLOR)
    end

    function selected_controller_id(app)
        entry = app.selected_controller_entry()
        return entry === nothing ? "" : entry.id
    end

    function sync_controller_selection(app, desired=LIVE_BASELINE_CONTROLLER)
        entry = app.controller_entry(desired)
        family = entry === nothing ? CONTROLLER_FAMILIES[1] : entry.family
        include_legacy = any(item -> item.display == desired, LEGACY_PROFILE_CONTROLLERS)
        app.ControllerFamilyDropDown.Items = CONTROLLER_FAMILIES
        app.ControllerFamilyDropDown.Value = family
        items = app.controller_options_for_family(family; include_legacy=include_legacy)
        app.PositionDropDown.Items = items
        app.PositionDropDown.Value = desired in items ? desired : items[1]
    end

    function selected_model_task(app)
        for task in MODEL_TASKS
            task.label == app.TaskDropDown.Value && return task
        end
        return MODEL_TASKS[1]
    end

    function selected_model_vehicle_count(app)
        return parse(Int, app.VehicleCountDropDown.Value)
    end

    function model_tasks_for_vehicle_count(app, vehicle_count)
        tasks = [task for task in MODEL_TASKS if task.vehicle_count == vehicle_count]
        return isempty(tasks) ? [MODEL_TASKS[end]] : tasks
    end

    function model_map_label(app, map_id)
        return map_id == "openblocks" ? MODEL_MAP_OPTIONS[2] : MODEL_MAP_OPTIONS[1]
    end

    function model_map_id(app)
        return app.MapDropDown.Value == MODEL_MAP_OPTIONS[2] ? "openblocks" : "blank"
    end

    function selected_fault_target_index(app)
        return parse(Int, replace(app.TargetUavDropDown.Value, "UAV " => ""))
    end

    function selected_motor_effectiveness(app)
        return [
            app.Motor1Slider.Value,
            app.Motor2Slider.Value,
            app.Motor3Slider.Value,
            app.Motor4Slider.Value,
        ]
    end

    function model_task_controller_supported(app)
        task = app.selected_model_task()
        controller = app.selected_controller_entry()
        return task.vehicle_count == app.selected_model_vehicle_count() &&
            controller !== nothing && controller.id in task.controller_ids
    end

    function model_task_output_boundary(app)
        task = app.selected_model_task()
        controller = app.selected_controller_entry()
        task.vehicle_count == 0 && return "当前数量无已登记模型入口"
        controller === nothing && return "由当前任务模型决定"
        if controller.id == "official_pid"
            return "ROTOR_COMMAND / OfficialPidFormalRunner"
        elseif controller.id == "px4ctrl"
            return task.vehicle_count == 3 ?
                "ROTOR_COMMAND / Px4CtrlThreeUavFigure8Runner" :
                "ATTITUDE_THRUST / Px4CtrlFormalRunner"
        elseif controller.id == "linear_mpc"
            return "ROTOR_COMMAND / 已登记多机规划模型"
        end
        return "当前任务未登记输出边界"
    end

    function configure_model_fixed_layers(app)
        app.AttitudeDropDown.Items = ["模型内部姿态/角速度环 [已认证]"]
        app.AttitudeDropDown.Value = app.AttitudeDropDown.Items[1]
        app.AttitudeDropDown.Enable = false

        app.AugmentationDropDown.Items = ["无"]
        app.AugmentationDropDown.Value = app.AugmentationDropDown.Items[1]
        app.AugmentationDropDown.Enable = false

        app.SafetyDropDown.Items = ["basic_limiter [已认证]"]
        app.SafetyDropDown.Value = app.SafetyDropDown.Items[1]
        app.SafetyDropDown.Enable = false

        output = app.model_task_output_boundary()
        app.OutputDropDown.Items = [output]
        app.OutputDropDown.Value = output
        app.OutputDropDown.Enable = false
    end

    function configure_model_controller_selection(app)
        current_family = app.ControllerFamilyDropDown.Value
        selected_family = current_family in CONTROLLER_FAMILIES ? current_family : CONTROLLER_FAMILIES[1]
        app.ControllerFamilyDropDown.Items = CONTROLLER_FAMILIES
        app.ControllerFamilyDropDown.Value = selected_family
        app.ControllerFamilyDropDown.Enable = true

        items = app.controller_options_for_family(selected_family)
        current_display = app.PositionDropDown.Value
        app.PositionDropDown.Items = items
        app.PositionDropDown.Value = current_display in items ? current_display : items[1]
        app.PositionDropDown.Enable = true
    end

    function sync_fault_target_options(app, vehicle_count)
        target_items = ["UAV " * string(index) for index in 1:vehicle_count]
        current_target = app.TargetUavDropDown.Value
        app.TargetUavDropDown.Items = target_items
        app.TargetUavDropDown.Value = current_target in target_items ? current_target : target_items[1]
    end

    function update_model_task_control_enablement(app)
        task = app.selected_model_task()
        enabled = task.injection_supported
        app.TargetUavDropDown.Enable = enabled
        app.FaultStartTimeField.Enable = enabled
        app.WindSlider.Enable = enabled
        app.ParameterMismatchSlider.Enable = enabled
        app.Motor1Slider.Enable = enabled
        app.Motor2Slider.Enable = enabled
        app.Motor3Slider.Enable = enabled
        app.Motor4Slider.Enable = enabled
    end

    function apply_model_task_defaults(app)
        app.WindSlider.Value = 0.0
        app.ParameterMismatchSlider.Value = 1.0
        app.FaultStartTimeField.Value = 15.0
        app.Motor1Slider.Value = 1.0
        app.Motor2Slider.Value = 1.0
        app.Motor3Slider.Value = 1.0
        app.Motor4Slider.Value = 1.0
        app.TaskConfigPath = ""
        app.TaskConfigDirty = true
        app.update_model_task_control_enablement()
    end

    function configure_model_task_controls(app)
        previous_vehicle = app.VehicleCountDropDown.Value
        previous_task = app.TaskDropDown.Value
        app.VehicleCountDropDown.Items = VEHICLE_COUNT_OPTIONS
        app.VehicleCountDropDown.Value = previous_vehicle in VEHICLE_COUNT_OPTIONS ? previous_vehicle : "1"
        app.VehicleCountDropDown.Label = "UAV 数量"
        app.VehicleCountDropDown.Position = [24, 192, 210, 32]
        app.VehicleCountDropDown.Enable = true

        vehicle_count = app.selected_model_vehicle_count()
        tasks = app.model_tasks_for_vehicle_count(vehicle_count)
        task_labels = [task.label for task in tasks]
        app.TaskDropDown.Items = task_labels
        app.TaskDropDown.Value = previous_task in task_labels ? previous_task : task_labels[1]
        app.TaskDropDown.Label = "验证任务"
        app.TaskDropDown.Position = [24, 234, 440, 32]
        app.TaskDropDown.Enable = true

        task = app.selected_model_task()
        app.MapDropDown.Items = [app.model_map_label(task.map_id)]
        app.MapDropDown.Value = app.MapDropDown.Items[1]
        app.MapDropDown.Label = "地图"
        app.MapDropDown.Position = [254, 192, 210, 32]
        app.MapDropDown.Enable = false
        app.sync_fault_target_options(vehicle_count)

        app.configure_model_controller_selection()
        app.ControllerFamilyDropDown.Label = "控制器家族"
        app.ControllerFamilyDropDown.Position = [24, 276, 440, 32]
        app.PositionDropDown.Label = "控制器实例"
        app.PositionDropDown.Position = [24, 318, 440, 32]

        for (control, label, y) in (
            (app.AttitudeDropDown, "姿态内环", 360),
            (app.AugmentationDropDown, "增强层", 402),
            (app.SafetyDropDown, "安全层", 444),
            (app.OutputDropDown, "输出边界", 486),
        )
            control.Label = label
            control.Position = [24, y, 440, 32]
        end
        app.configure_model_fixed_layers()
        app.update_model_task_control_enablement()
    end

    function is_three_uav_mission(app, mission)
        return mission in THREE_UAV_MISSION_OPTIONS
    end

    function mission_vehicle_count(app, mission)
        return app.is_three_uav_mission(mission) ? 3 : 1
    end

    function mission_options_for_vehicle_count(app, vehicle_count)
        return vehicle_count == 3 ? MODEL_MISSION_OPTIONS : SINGLE_UAV_MISSION_OPTIONS
    end

    function sync_vehicle_controls(app)
        vehicle_count = parse(Int, app.VehicleCountDropDown.Value)
        app.sync_fault_target_options(vehicle_count)

        mission_items = app.mission_options_for_vehicle_count(vehicle_count)
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
        app.set_dropdown_position(app.ControllerFamilyDropDown, [24, 330, 170, 32])
        app.ControllerFamilyDropDown.Label = "控制器家族"
        app.set_dropdown_position(app.PositionDropDown, [204, 330, 260, 32])
        app.PositionDropDown.Label = "控制器实例"
        app.sync_controller_selection(LIVE_BASELINE_CONTROLLER)
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
            app.ControllerFamilyDropDown, app.PositionDropDown, app.AttitudeDropDown, app.AugmentationDropDown,
            app.SafetyDropDown, app.FaultDropDown, app.OutputDropDown)
            control.Enable = true
        end
        app.sync_vehicle_controls()
    end

    function live_combination_compatible(app)
        return app.VehicleCountDropDown.Value == "1" &&
            app.FormationDropDown.Value == "无" &&
            app.PositionDropDown.Value == LIVE_BASELINE_CONTROLLER &&
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
        app.VehicleCountDropDown.Value = string(app.mission_vehicle_count(item.mission))
        app.MapDropDown.Value = MAP_OPTIONS[1]
        app.sync_vehicle_controls()
        app.MissionDropDown.Value = item.mission
        app.sync_controller_selection(item.controller)
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
            app.VehicleCountDropDown.Value == string(app.mission_vehicle_count(item.mission)) &&
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
        if app.CurrentMode == "assistant"
            app.refresh_assistant_context()
            return
        elseif app.CurrentMode == "model"
            supported = app.model_task_controller_supported()
            app.ApplyInjectionButton.Enable = supported
            app.OpenModelButton.Enable = supported && !app.TaskConfigDirty && isfile(app.TaskConfigPath)
            return
        elseif app.CurrentMode == "deploy"
            controller = app.selected_controller_entry()
            controller_status = controller === nothing ? "待接入" : controller.status
            app.ProfileSummaryLabel.Text = "控制器家族  " * app.ControllerFamilyDropDown.Value * "\n" *
                "控制器实例  " * app.PositionDropDown.Value * "\n" *
                "状态  " * controller_status
            app.ProfileSummaryLabel.BackgroundColor = app.controller_status_color(controller)
            app.CodegenButton.Enable = controller !== nothing && controller.openable
            return
        end
        app.ProfileSummaryLabel.Text = "运行Profile  " * app.ProfileDropDown.Value *
            "\n任务  " * app.MissionDropDown.Value
    end

    function configure_model_workspace(app)
        app.set_top_status("在线建模验证  |  未运行  |  Result.msr --"; state="正常")
        app.configure_section(app.ConfigSectionLabel, "验证任务与控制器", [24, 144, 440, 34])
        app.configure_section(app.ChainSectionLabel, "场景参数", [494, 144, 440, 34])
        app.configure_console_workspace()
        app.ConfigSectionLabel.Visible = true
        app.ChainSectionLabel.Visible = true
        app.InjectionSectionLabel.Visible = true
        app.set_visible(app.workspace_controls(), false)
        model_controls = (
            app.VehicleCountDropDown, app.MapDropDown, app.TaskDropDown,
            app.ControllerFamilyDropDown, app.PositionDropDown, app.AttitudeDropDown,
            app.AugmentationDropDown, app.SafetyDropDown, app.OutputDropDown,
            app.TargetUavDropDown, app.FaultStartTimeField, app.WindSlider,
            app.ParameterMismatchSlider,
            app.Motor1Slider, app.Motor2Slider, app.Motor3Slider,
            app.Motor4Slider,
            app.ApplyInjectionButton, app.RestoreInjectionButton,
        )
        app.set_visible(model_controls, true)
        app.configure_model_task_controls()
        app.apply_model_task_defaults()

        app.TargetUavDropDown.Position = [494, 192, 210, 32]
        app.TargetUavDropDown.Label = "故障目标"
        app.FaultStartTimeField.Position = [724, 192, 210, 32]
        app.FaultStartTimeField.Label = "工况开始时刻（s）"
        app.FaultStartTimeField.Limits = [0.0, 1000.0]

        app.WindSlider.Position = [494, 234, 440, 46]
        app.WindSlider.Label = "外力扰动（+X，N）"
        app.WindSlider.Limits = [0.0, 0.5]
        app.WindSlider.MajorTicks = [0.0, 0.1, 0.25, 0.5]
        app.WindSlider.MajorTickLabels = ["0", "0.10", "0.25", "0.50"]
        app.ParameterMismatchSlider.Position = [494, 290, 440, 46]
        app.ParameterMismatchSlider.Label = "参数失配（质量/惯量倍率）"
        app.ParameterMismatchSlider.Limits = [1.0, 1.4]
        app.ParameterMismatchSlider.MajorTicks = [1.0, 1.1, 1.2, 1.3, 1.4]
        app.ParameterMismatchSlider.MajorTickLabels = ["1.00", "1.10", "1.20", "1.30", "1.40"]
        for (control, label, y) in (
            (app.Motor1Slider, "电机 1 效率（工况后）", 346),
            (app.Motor2Slider, "电机 2 效率（工况后）", 402),
            (app.Motor3Slider, "电机 3 效率（工况后）", 458),
            (app.Motor4Slider, "电机 4 效率（工况后）", 514),
        )
            control.Position = [494, y, 440, 46]
            control.Label = label
            control.Limits = [0.0, 1.0]
            control.MajorTicks = [0.0, 0.5, 1.0]
            control.MajorTickLabels = ["0", "50%", "100%"]
        end
        app.ApplyInjectionButton.Position = [494, 570, 180, 36]
        app.ApplyInjectionButton.Text = "写入配置"
        app.RestoreInjectionButton.Position = [884, 570, 50, 36]
        app.RestoreInjectionButton.Text = "重置"

        app.set_visible(app.action_buttons(), false)
        app.set_visible((app.OpenModelButton,), true)
        app.OpenModelButton.Position = [684, 570, 190, 36]
        app.OpenModelButton.Text = "打开仿真模型"
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
            app.MissionDropDown, app.ControllerFamilyDropDown, app.PositionDropDown, app.AttitudeDropDown,
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
        app.set_visible((app.ValidateButton, app.OpenModelButton), true)
        app.ValidateButton.Position = [494, 674, 210, 38]
        app.ValidateButton.Text = "应用配置"
        app.OpenModelButton.Position = [724, 674, 210, 38]
        app.OpenModelButton.Text = "打开联合仿真模型"
    end

    function configure_deploy_workspace(app)
        app.set_top_status("MWORKS 代码生成  |  由用户在原生 MWORKS 中执行"; state="待命")
        app.configure_section(app.ConfigSectionLabel, "代码生成模型", [24, 144, 560, 34])
        app.configure_section(app.InjectionSectionLabel, "操作日志", [614, 144, 802, 34])
        app.configure_console_workspace(left=614, width=802)
        app.ConfigSectionLabel.Visible = true
        app.ChainSectionLabel.Visible = false
        app.InjectionSectionLabel.Visible = true
        app.set_visible(app.workspace_controls(), false)
        deploy_controls = (
            app.ControllerFamilyDropDown, app.PositionDropDown,
            app.OutputDropDown, app.ProfileSummaryLabel,
        )
        app.set_visible(deploy_controls, true)
        desired = app.selected_controller_entry() === nothing ? LIVE_BASELINE_CONTROLLER : app.PositionDropDown.Value
        app.set_dropdown_position(app.ControllerFamilyDropDown, [24, 192, 270, 32])
        app.ControllerFamilyDropDown.Label = "控制器家族"
        app.set_dropdown_position(app.PositionDropDown, [314, 192, 270, 32])
        app.PositionDropDown.Label = "控制器实例"
        app.sync_controller_selection(desired)
        app.set_dropdown_position(app.OutputDropDown, [24, 246, 560, 32])
        app.OutputDropDown.Label = "模型输出接口"
        app.OutputDropDown.Items = ["由已打开的 MWORKS 模型确定"]
        app.OutputDropDown.Value = app.OutputDropDown.Items[1]
        app.OutputDropDown.Enable = false
        app.ProfileSummaryLabel.Position = [24, 292, 560, 80]

        app.set_visible(app.action_buttons(), false)
        app.set_visible((app.CodegenButton,), true)
        app.CodegenButton.Position = [24, 390, 560, 44]
        app.CodegenButton.Text = "打开 MWORKS 代码生成模型"
    end

    function configure_assistant_workspace(app)
        app.set_top_status("MoSim 助手  |  当前配置上下文已读取  |  不直接控制仿真或飞行端"; state="正常")
        app.configure_section(app.ConfigSectionLabel, "当前配置", [24, 144, 320, 34])
        app.configure_section(app.ChainSectionLabel, "MoSim 助手", [364, 144, 692, 34])
        app.configure_section(app.InjectionSectionLabel, "快捷问题", [1076, 144, 340, 34])
        app.ConfigSectionLabel.Visible = true
        app.ChainSectionLabel.Visible = true
        app.InjectionSectionLabel.Visible = true
        app.set_visible(app.workspace_controls(), false)
        app.set_visible(app.action_buttons(), false)
        app.StatusLabel.Visible = false
        app.ConsoleToggleButton.Visible = false
        app.ConsoleClearButton.Visible = false
        app.set_visible(app.assistant_controls(), true)

        app.AssistantContextLabel.Position = [24, 192, 320, 468]
        app.AssistantChatLabel.Position = [364, 192, 692, 394]
        app.AssistantInputField.Position = [364, 616, 510, 32]
        app.AssistantSendButton.Position = [890, 614, 166, 36]
        app.AssistantClearButton.Position = [364, 664, 166, 32]
        app.AssistantExplainButton.Position = [1076, 192, 340, 40]
        app.AssistantMworksGuideButton.Position = [1076, 246, 340, 40]
        app.AssistantQgcGuideButton.Position = [1076, 300, 340, 40]
        app.AssistantResultGuideButton.Position = [1076, 354, 340, 40]
        app.AssistantStatusLabel.Position = [1076, 418, 340, 242]

        app.refresh_assistant_context()
        isempty(app.AssistantLines) && app.append_assistant("MoSim 助手", "你好，我已读取当前实验配置。")
    end

    function set_mode(app, mode)
        app.CurrentMode = mode
        app.set_button_state(app.OfflineModeButton, mode == "model")
        app.set_button_state(app.LiveModeButton, mode == "live")
        app.set_button_state(app.DeployModeButton, mode == "deploy")
        app.set_button_state(app.AssistantModeButton, mode == "assistant")
        if mode == "model"
            app.LastOperationalMode = mode
            app.configure_model_workspace()
            app.set_connection_controls(false)
            app.append_console("切换至在线建模验证工作台")
        elseif mode == "live"
            app.LastOperationalMode = mode
            app.configure_live_workspace()
            app.set_connection_controls(true)
            app.append_console("切换至实时联合仿真工作台；实时后端保持未连接")
        elseif mode == "deploy"
            app.LastOperationalMode = mode
            app.configure_deploy_workspace()
            app.set_connection_controls(false)
            app.append_console("切换至 MWORKS 代码生成工作台")
        else
            app.configure_assistant_workspace()
            app.set_connection_controls(false)
            app.append_console("切换至 MoSim 助手；仅提供本地配置指引")
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

    function AssistantModePressed(app, event)
        app.set_mode("assistant")
    end

    function FamilyChanged(app, event)
        if app.CurrentMode == "model"
            app.configure_model_controller_selection()
        else
            family = app.ControllerFamilyDropDown.Value
            app.PositionDropDown.Items = app.controller_options_for_family(family)
            app.PositionDropDown.Value = app.PositionDropDown.Items[1]
        end
        app.SelectionChanged(event)
    end

    function TaskChanged(app, event)
        app.configure_model_task_controls()
        app.TaskConfigPath = ""
        app.TaskConfigDirty = true
        app.configure_model_fixed_layers()
        app.refresh_summary()
        app.append_console("验证任务已切换；场景参数保持当前组合")
    end

    function VehicleCountChanged(app, event)
        if app.CurrentMode == "model"
            app.configure_model_task_controls()
            app.TaskConfigPath = ""
            app.TaskConfigDirty = true
            app.refresh_summary()
            app.append_console("UAV 数量已切换；已更新可用任务与故障目标")
        else
            app.SelectionChanged(event)
        end
    end

    function SelectionChanged(app, event)
        if app.CurrentMode == "model"
            app.configure_model_fixed_layers()
            app.TaskConfigPath = ""
            app.TaskConfigDirty = true
            app.refresh_summary()
            app.append_console("控制器已修改；请重新写入 MWORKS 配置")
        else
            app.sync_vehicle_controls()
            app.refresh_summary()
        end
        if app.CurrentMode == "live"
            app.ConnectionChanged(nothing)
            if !app.live_combination_compatible()
                app.append_console("当前组合超出单机 ATTITUDE_THRUST 实时合同；可保存但不可准备运行"; level="阻断")
            end
        elseif app.CurrentMode != "model"
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
        if app.CurrentMode == "model"
            app.TaskConfigPath = ""
            app.TaskConfigDirty = true
            app.refresh_summary()
            app.append_console("场景参数已修改；请重新写入 MWORKS 配置")
            return
        end
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
        if app.CurrentMode != "model"
            app.append_console("故障应用请求未发送；等待实时后端接入"; level="待办")
            return
        end
        if !app.model_task_controller_supported()
            app.append_console("当前数量、任务与控制器组合没有已登记的 MWORKS 模型入口；未写入配置"; level="阻断")
            return
        end
        if !isfile(MODEL_TASK_CONFIG_WRITER)
            app.append_console("任务配置写入器不存在：" * MODEL_TASK_CONFIG_WRITER; level="错误")
            return
        end
        task = app.selected_model_task()
        controller = app.selected_controller_entry()
        motors = join(string.(app.selected_motor_effectiveness()), ",")
        app.ApplyInjectionButton.Enable = false
        app.OpenModelButton.Enable = false
        app.append_console("正在冻结 " * task.label * " 的 MWORKS 配置"; level="运行")
        @async begin
            try
                command_args = [
                    "python", MODEL_TASK_CONFIG_WRITER,
                    "--task-id", task.id,
                    "--controller-id", controller.id,
                    "--vehicle-count", app.VehicleCountDropDown.Value,
                    "--map-id", app.model_map_id(),
                    "--fault-target-uav", string(app.selected_fault_target_index()),
                    "--fault-start-s", string(app.FaultStartTimeField.Value),
                    "--gust-force-x-n", string(app.WindSlider.Value),
                    "--mass-inertia-scale", string(app.ParameterMismatchSlider.Value),
                    "--motor-effectiveness", motors,
                ]
                run_process_in_directory(command_args, PROJECT_ROOT)
                config_path = joinpath(PROJECT_ROOT, "Results", "ui_platform", "model_studio_task_handoffs", "latest.json")
                isfile(config_path) || error("task_config_not_created: " * config_path)
                app.TaskConfigPath = config_path
                app.TaskConfigDirty = false
                app.refresh_summary()
                app.set_top_status("在线建模验证  |  配置已冻结  |  等待用户在 MWORKS 中仿真"; state="正常")
                app.append_console("配置已冻结：" * config_path * "；未启动仿真"; level="通过")
            catch error
                app.TaskConfigPath = ""
                app.TaskConfigDirty = true
                app.refresh_summary()
                app.append_console("写入配置失败：" * sprint(showerror, error); level="错误")
            finally
                app.ApplyInjectionButton.Enable = app.model_task_controller_supported()
            end
        end
    end

    function RestoreInjectionPressed(app, event)
        if app.CurrentMode == "model"
            app.apply_model_task_defaults()
            app.refresh_summary()
            app.append_console("验证任务已恢复标准参数；请重新写入配置")
            return
        end
        app.WindSlider.Value = 0.0
        app.ParameterMismatchSlider.Value = 1.0
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
        Base.@async begin
            try
                run_process_in_directory(command_args, PROJECT_ROOT)
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
        if app.CurrentMode == "model"
            app.ApplyInjectionPressed(event)
        elseif app.CurrentMode == "live"
            app.refresh_summary()
            app.append_console("联合仿真配置已应用；未启动实时链路", level="通过")
            app.set_top_status("实时联合仿真  |  配置已应用  |  尚未连接"; state="待命")
        else
            app.ReviewAction("应用部署配置")
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
    function open_mworks_model(app, mode)
        if !isfile(OPEN_MODEL_SCRIPT)
            app.append_console("打开模型入口不存在：" * OPEN_MODEL_SCRIPT; level="错误")
            return
        end
        controller = app.selected_controller_entry()
        if controller === nothing
            app.append_console("当前控制器没有可解析的 MWORKS 模型入口"; level="错误")
            return
        end
        if mode == "codegen" && !controller.openable
            app.append_console("当前控制器尚无可打开的 MWORKS 代码生成模型"; level="阻断")
            return
        end
        if mode == "model"
            if !app.model_task_controller_supported()
                app.append_console("当前数量、任务与控制器组合没有已登记的 MWORKS 模型入口；未打开模型"; level="阻断")
                return
            end
            if app.TaskConfigDirty || isempty(app.TaskConfigPath) || !isfile(app.TaskConfigPath)
                app.append_console("请先写入配置，再打开对应的 MWORKS 仿真模型"; level="阻断")
                return
            end
        end
        opening_text = mode == "codegen" ? "正在打开 MWORKS 代码生成模型" :
            (mode == "live" ? "正在打开联合仿真模型" : "正在打开当前仿真模型")
        app.append_console(opening_text; level="运行")
        @async begin
            try
                command_args = [
                    "python", OPEN_MODEL_SCRIPT,
                    "--mode", mode,
                    "--controller-id", controller.id,
                ]
                if mode == "model"
                    append!(command_args, ["--task-config", app.TaskConfigPath])
                elseif mode != "codegen"
                    profile_id = haskey(OFFLINE_PROFILES, app.ProfileDropDown.Value) ?
                        OFFLINE_PROFILES[app.ProfileDropDown.Value].profile : ""
                    append!(command_args, [
                        "--profile-id", profile_id,
                        "--vehicle-count", app.VehicleCountDropDown.Value,
                        "--output-variant", app.OutputDropDown.Value,
                    ])
                end
                run_process_in_directory(command_args, PROJECT_ROOT)
                if mode == "codegen"
                    app.append_console("代码生成模型已打开；请在 MWORKS 的“代码生成”页签中自行点击“代码生成”"; level="通过")
                elseif mode == "live"
                    app.append_console("联合仿真模型已打开；请在 MWORKS 中自行点击仿真"; level="通过")
                else
                    app.append_console("仿真模型已打开；请在 MWORKS 中自行点击仿真"; level="通过")
                end
            catch error
                app.append_console("打开模型失败：" * sprint(showerror, error); level="错误")
            end
        end
    end

    function OpenModelPressed(app, event)
        app.open_mworks_model(app.CurrentMode == "live" ? "live" : "model")
    end
    function MilPressed(app, event)
        if app.OfflineBatchRunning
            app.request_offline_cancel()
            return
        end
        if app.CurrentMode == "model"
            app.append_console("在线建模验证不从 Studio 启动仿真；请在已打开的 MWORKS 模型中自行点击仿真"; level="提示")
        else
            app.ReviewAction("运行 MWORKS MIL")
        end
    end
    function CodegenPressed(app, event)
        app.open_mworks_model("codegen")
    end
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
        app.UIFigure.Name = "MoSim Studio"
        app.UIFigure.Color = [0.96, 0.97, 0.97]

        app.TitleLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.TitleLabel.Position = [24, 16, 520, 34]
        app.TitleLabel.Text = "MoSim Studio"
        app.TitleLabel.FontSize = 24
        app.TitleLabel.FontWeight = "bold"
        app.TitleLabel.FontColor = [0.08, 0.16, 0.22]
        app.TitleLabel.HorizontalAlignment = "left"

        app.OfflineModeButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.OfflineModeButton, "在线建模验证", "OfflineModePressed", [24, 82, 190, 40])
        app.LiveModeButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.LiveModeButton, "实时联合仿真", "LiveModePressed", [218, 82, 190, 40])
        app.DeployModeButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.DeployModeButton, "代码生成", "DeployModePressed", [412, 82, 190, 40])
        app.AssistantModeButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.AssistantModeButton, "MoSim 助手", "AssistantModePressed", [606, 82, 190, 40])

        app.ModeStatusLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ModeStatusLabel.Position = [814, 82, 602, 40]
        app.ModeStatusLabel.HorizontalAlignment = "right"
        app.ModeStatusLabel.WordWrap = true
        app.ModeStatusLabel.FontColor = [0.25, 0.32, 0.36]

        app.ConfigSectionLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.configure_section(app.ConfigSectionLabel, "控制链与实验 Profile", [24, 144, 420, 34])
        app.ChainSectionLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.configure_section(app.ChainSectionLabel, "职责、接口与能力门禁", [468, 144, 470, 34])
        app.InjectionSectionLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.configure_section(app.InjectionSectionLabel, "故障注入与运行状态", [962, 144, 454, 34])

        app.TaskDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.TaskDropDown, "验证任务", [24, 192, 420, 32], MODEL_TASK_LABELS, MODEL_TASK_LABELS[1])
        app.TaskDropDown.ValueChangedFcn = "TaskChanged"
        app.ProfileDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.ProfileDropDown, "实验 Profile", [24, 192, 420, 32], ["正在加载..."], "正在加载...")
        app.ProfileDropDown.ValueChangedFcn = "PresetChanged"
        app.VehicleCountDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.VehicleCountDropDown, "UAV 数量", [24, 238, 210, 32], VEHICLE_COUNT_OPTIONS, "1")
        app.VehicleCountDropDown.ValueChangedFcn = "VehicleCountChanged"
        app.MapDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.MapDropDown, "地图", [254, 238, 210, 32], MAP_OPTIONS, MAP_OPTIONS[1])
        app.MissionDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.MissionDropDown, "任务轨迹", [24, 240, 420, 32], ["起飞-悬停-降落"], "起飞-悬停-降落")
        app.ControllerFamilyDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.ControllerFamilyDropDown, "控制器家族", [24, 288, 170, 32], CONTROLLER_FAMILIES, CONTROLLER_FAMILIES[1])
        app.ControllerFamilyDropDown.ValueChangedFcn = "FamilyChanged"
        app.PositionDropDown = TyAppDesigner.uidropdown(app.UIFigure)
        app.configure_dropdown(app.PositionDropDown, "控制器实例", [204, 288, 260, 32], [LIVE_BASELINE_CONTROLLER], LIVE_BASELINE_CONTROLLER)
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
        app.TargetUavDropDown.ValueChangedFcn = "InjectionChanged"
        app.FaultStartTimeField = TyAppDesigner.uinumericeditfield(app.UIFigure)
        app.FaultStartTimeField.Position = [724, 192, 210, 32]
        app.FaultStartTimeField.Label = "工况开始时刻（s）"
        app.FaultStartTimeField.Value = 15.0
        app.FaultStartTimeField.Limits = [0.0, 1000.0]
        app.FaultStartTimeField.ValueChangedFcn = "InjectionChanged"

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
        app.ParameterMismatchSlider = TyAppDesigner.uislider(app.UIFigure)
        app.configure_slider(app.ParameterMismatchSlider, "参数失配（质量/惯量倍率）", [962, 224, 454, 52], 1.0, [1.0, 1.4], [1.0, 1.1, 1.2, 1.3, 1.4], ["1.00", "1.10", "1.20", "1.30", "1.40"])
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
        app.configure_action(app.CodegenButton, "打开 MWORKS 代码生成模型", "CodegenPressed", [1098, 754, 140, 38])
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

        app.AssistantContextLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.AssistantContextLabel.Position = [24, 192, 320, 468]
        app.AssistantContextLabel.VerticalAlignment = "top"
        app.AssistantContextLabel.WordWrap = true
        app.AssistantContextLabel.BackgroundColor = [0.91, 0.94, 0.95]

        app.AssistantChatLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.AssistantChatLabel.Position = [364, 192, 692, 394]
        app.AssistantChatLabel.VerticalAlignment = "top"
        app.AssistantChatLabel.WordWrap = true
        app.AssistantChatLabel.BackgroundColor = [1.0, 1.0, 1.0]
        app.AssistantChatLabel.FontColor = [0.08, 0.16, 0.22]

        app.AssistantInputField = TyAppDesigner.uieditfield(app.UIFigure)
        app.AssistantInputField.Position = [364, 616, 510, 32]
        app.AssistantInputField.Label = "输入问题"
        app.AssistantInputField.Value = ""

        app.AssistantSendButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.AssistantSendButton, "发送", "AssistantSendPressed", [890, 614, 166, 36])
        app.AssistantClearButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.AssistantClearButton, "清空对话", "AssistantClearPressed", [364, 664, 166, 32])

        app.AssistantExplainButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.AssistantExplainButton, "解释当前控制链", "AssistantExplainPressed", [1076, 192, 340, 40])
        app.AssistantMworksGuideButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.AssistantMworksGuideButton, "MWORKS 操作指引", "AssistantMworksGuidePressed", [1076, 246, 340, 40])
        app.AssistantQgcGuideButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.AssistantQgcGuideButton, "QGC 操作指引", "AssistantQgcGuidePressed", [1076, 300, 340, 40])
        app.AssistantResultGuideButton = TyAppDesigner.uibutton(app.UIFigure)
        app.configure_action(app.AssistantResultGuideButton, "结果查看指引", "AssistantResultGuidePressed", [1076, 354, 340, 40])

        app.AssistantStatusLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.AssistantStatusLabel.Position = [1076, 418, 340, 242]
        app.AssistantStatusLabel.Text = "助手状态\n\n本地上下文模式\n已读取当前实验配置\n\n运行控制：未接管\n模型、QGC 与结果查看仍由各自页面和原生工具负责"
        app.AssistantStatusLabel.VerticalAlignment = "top"
        app.AssistantStatusLabel.WordWrap = true
        app.AssistantStatusLabel.BackgroundColor = MUTED_COLOR

        app.set_mode("model")
        app.InjectionChanged(nothing)
        app.append_console("Model Studio 已就绪"; level="系统")
        app.UIFigure.Visible = true
    end

    function initApp(app)
        app.Appname = @__MODULE__
        app.Appfile = @__FILE__
        app.ConsoleLines = String[]
        app.AssistantLines = String[]
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
