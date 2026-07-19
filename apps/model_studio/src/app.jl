module MoSimModelStudio

using ObjectOriented
using TyAppDesigner
include(joinpath(@__DIR__, "live_cosim_backend.jl"))
using .LiveCosimBackend

const ACTIVE_COLOR = [0.08, 0.36, 0.43]
const INACTIVE_COLOR = [0.88, 0.91, 0.92]
const SECTION_COLOR = [0.12, 0.25, 0.32]
const READY_COLOR = [0.86, 0.95, 0.89]
const WAIT_COLOR = [0.98, 0.93, 0.80]
const MUTED_COLOR = [0.93, 0.94, 0.94]
const PROJECT_ROOT = normpath(joinpath(@__DIR__, "..", ".."))
const OFFLINE_BATCH_RUNNER = joinpath(PROJECT_ROOT, "Scripts", "mworks", "run_offline_profile_batch.py")
const OFFLINE_BATCH_INDEX = joinpath(PROJECT_ROOT, "Results", "control_platform", "offline_batches", "BATCH_INDEX.json")

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
    "Official PID 爬升 [已认证]" => (profile="offline_official_pid_climb_v1", mission="爬升", controller="Official PID", augmentation="无", safety="基础限幅", evidence="Results/mworks_generated_profiles/cert-official-pid-20260719-v2", available=true),
    "改进 PID 爬升 [已认证]" => (profile="offline_improved_pid_climb_v1", mission="爬升", controller="改进 PID", augmentation="无", safety="基础限幅", evidence="Results/mworks_generated_profiles/cert-improved-pid-20260719-v1", available=true),
    "AWFF 爬升 [已认证]" => (profile="offline_awff_climb_v1", mission="爬升", controller="AWFF", augmentation="AWFF", safety="基础限幅", evidence="Results/mworks_generated_profiles/cert-awff-20260719-v1", available=true),
    "PID-INDI 爬升 [已认证]" => (profile="offline_pid_indi_climb_v1", mission="爬升", controller="PID-INDI", augmentation="INDI", safety="基础限幅", evidence="Results/mworks_generated_profiles/cert-pid-indi-20260719-v1", available=true),
    "Linear MPC 爬升 [已认证]" => (profile="offline_linear_mpc_climb_v1", mission="爬升", controller="Linear MPC", augmentation="无", safety="基础限幅", evidence="Results/mworks_generated_profiles/cert-linear-mpc-20260719-v1", available=true),
    "L1/AWFF 爬升 [已认证]" => (profile="offline_l1_awff_climb_v1", mission="爬升", controller="L1/AWFF", augmentation="L1", safety="基础限幅", evidence="Results/mworks_generated_profiles/cert-l1-awff-climb-20260719-v1", available=true),
    "L1/AWFF 风扰 [已认证]" => (profile="offline_l1_awff_wind_v1", mission="爬升 + 风扰", controller="L1/AWFF", augmentation="L1", safety="基础限幅", evidence="Results/mworks_generated_profiles/cert-l1-awff-wind-20260719-v1", available=true),
    "故障补偿：电机 1 效率 85% [已认证]" => (profile="offline_fault_comp_rotor1_85_v1", mission="爬升 + 电机效率下降", controller="故障补偿", augmentation="故障重构", safety="基础限幅", evidence="Results/mworks_generated_profiles/cert-fault-comp-rotor1-85-20260719-v1", available=true),
    "三机 Linear MPC 三角编队 8 字 [已认证]" => (profile="offline_three_uav_linear_mpc_figure8_v1", mission="三机三角编队 8 字", controller="Linear MPC", augmentation="Leader-Follower", safety="基础限幅", evidence="Results/mworks_generated_profiles/cert-three-uav-linear-mpc-figure8-20260719-v2", available=true),
    "Custom：改进 PID + 轻风扰 [已验证]" => (profile="custom_improved_pid_mild_wind_v1", mission="爬升 + 轻风扰", controller="改进 PID", augmentation="无", safety="基础限幅", evidence="Results/mworks_generated_profiles/p7-custom-improved-pid-mild-wind-20260719-v2", available=true),
    "Custom：故障补偿 + 轻风扰 [已验证]" => (profile="custom_fault_comp_mixed_v1", mission="爬升 + 轻风扰 + 电机效率下降", controller="故障补偿", augmentation="故障重构", safety="基础限幅", evidence="Results/mworks_generated_profiles/p7-custom-fault-comp-mixed-20260719-v2", available=true),
    "QP/NMPC Safety [当前禁用]" => (profile="offline_qp_nmpc_safety_climb_v1", mission="爬升", controller="Linear MPC", augmentation="无", safety="QP/NMPC Safety", evidence="当前共用 Runner 与独立模型均数值失稳", available=false),
)

@oodef mutable struct App
    UIFigure::TyAppDesigner.Figure = TyAppDesigner.create_figure()
    TitleLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    SubtitleLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    OfflineModeButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    LiveModeButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    DeployModeButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    ModeStatusLabel::TyAppDesigner.Label = TyAppDesigner.create_label()

    ConfigSectionLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    ChainSectionLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    InjectionSectionLabel::TyAppDesigner.Label = TyAppDesigner.create_label()

    ProfileDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    MissionDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    PositionDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    AttitudeDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    AugmentationDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    SafetyDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    OutputDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    ProfileSummaryLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    CapabilityLabel::TyAppDesigner.Label = TyAppDesigner.create_label()

    ChainLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    ContractLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    TimingLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    TargetHostField::TyAppDesigner.EditField = TyAppDesigner.create_editfield()
    Rt1PortField::TyAppDesigner.NumericEditField = TyAppDesigner.create_numericeditfield()
    RosMasterField::TyAppDesigner.EditField = TyAppDesigner.create_editfield()
    LocalIpField::TyAppDesigner.EditField = TyAppDesigner.create_editfield()
    TargetRateDropDown::TyAppDesigner.DropDown = TyAppDesigner.create_dropdown()
    TestConnectionButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    ConnectionStatusLabel::TyAppDesigner.Label = TyAppDesigner.create_label()

    WindSlider::TyAppDesigner.Slider = TyAppDesigner.create_slider()
    Motor1Slider::TyAppDesigner.Slider = TyAppDesigner.create_slider()
    Motor2Slider::TyAppDesigner.Slider = TyAppDesigner.create_slider()
    Motor3Slider::TyAppDesigner.Slider = TyAppDesigner.create_slider()
    Motor4Slider::TyAppDesigner.Slider = TyAppDesigner.create_slider()
    InjectionValuesLabel::TyAppDesigner.Label = TyAppDesigner.create_label()
    ApplyInjectionButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    RestoreInjectionButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    ManifestLabel::TyAppDesigner.Label = TyAppDesigner.create_label()

    ValidateButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    PublishButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    PrepareButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    QgcButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    SafeStopButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    OpenModelButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    MilButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    CodegenButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    ResultButton::TyAppDesigner.Button = TyAppDesigner.create_button()
    StatusLabel::TyAppDesigner.Label = TyAppDesigner.create_label()

    Appname::Module = @__MODULE__
    Appfile::String = @__FILE__
    CurrentMode::String = "live"
    LastOfflineBatchManifest::String = ""
    LastOfflineBatchId::String = ""
    LastOfflineProfile::String = ""
    CurrentOfflineBatchId::String = ""
    OfflineBatchRunning::Bool = false

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
            "实时能力门禁\nRT0 已通过；Profile 已发布，可请求 prepare。" * metrics :
            "实时能力门禁\n200 Hz 为待验证目标，50 Hz 为已测基线；当前原因：" * reason * metrics
        app.CapabilityLabel.BackgroundColor = accepted ? READY_COLOR : WAIT_COLOR
        app.PrepareButton.Enable = accepted
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

    function refresh_summary(app)
        if app.CurrentMode == "offline" && haskey(OFFLINE_PROFILES, app.ProfileDropDown.Value)
            item = OFFLINE_PROFILES[app.ProfileDropDown.Value]
            app.MissionDropDown.Items = [item.mission]
            app.MissionDropDown.Value = item.mission
            app.PositionDropDown.Items = [item.controller]
            app.PositionDropDown.Value = item.controller
            app.AttitudeDropDown.Items = ["模型内部姿态环与控制分配 [冻结]"]
            app.AttitudeDropDown.Value = "模型内部姿态环与控制分配 [冻结]"
            app.AugmentationDropDown.Items = [item.augmentation]
            app.AugmentationDropDown.Value = item.augmentation
            app.SafetyDropDown.Items = [item.safety]
            app.SafetyDropDown.Value = item.safety
            app.OutputDropDown.Items = ["ROTOR_COMMAND [离线]"]
            app.OutputDropDown.Value = "ROTOR_COMMAND [离线]"
            app.MilButton.Enable = item.available
            app.ResultButton.Enable = item.available
            app.CodegenButton.Enable = item.available && !occursin("Custom", app.ProfileDropDown.Value)
            app.CapabilityLabel.Text = item.available ?
                "离线证据已通过\nResult.msr、指标、曲线与原生动画窗口均已验收。" :
                "当前禁用\n共用 Runner 与既有独立模型均数值失稳；不得用窗口打开替代控制质量。"
            app.CapabilityLabel.BackgroundColor = item.available ? READY_COLOR : WAIT_COLOR
            app.ProfileSummaryLabel.Text =
                "实验 Profile\n" * item.profile *
                "\n\n任务：" * item.mission *
                "\n控制器：" * item.controller *
                "\n增强：" * item.augmentation *
                "\n证据：" * item.evidence
            return
        end
        app.ProfileSummaryLabel.Text =
            "实验 Profile\n" * app.ProfileDropDown.Value *
            "\n\n任务：" * app.MissionDropDown.Value *
            "\n外环：" * app.PositionDropDown.Value *
            "\n增强：" * app.AugmentationDropDown.Value
    end

    function set_mode(app, mode)
        app.CurrentMode = mode
        live_reason = ""
        app.set_button_state(app.OfflineModeButton, mode == "offline")
        app.set_button_state(app.LiveModeButton, mode == "live")
        app.set_button_state(app.DeployModeButton, mode == "deploy")
        app.MissionDropDown.Enable = true
        app.PositionDropDown.Enable = true
        app.AttitudeDropDown.Enable = true
        app.AugmentationDropDown.Enable = true
        app.SafetyDropDown.Enable = true
        app.OutputDropDown.Enable = true

        if mode == "offline"
            app.set_connection_controls(false)
            app.ModeStatusLabel.Text = "离线建模验证  |  Model Studio 拥有模型检查、MIL、代码生成和结果操作权"
            app.ProfileDropDown.Items = OFFLINE_PROFILE_ORDER
            app.ProfileDropDown.Value = OFFLINE_PROFILE_ORDER[1]
            app.MissionDropDown.Enable = false
            app.PositionDropDown.Enable = false
            app.AttitudeDropDown.Enable = false
            app.AugmentationDropDown.Enable = false
            app.SafetyDropDown.Enable = false
            app.OutputDropDown.Enable = false
            app.ValidateButton.Enable = true
            app.PublishButton.Enable = true
            app.PrepareButton.Enable = false
            app.QgcButton.Enable = false
            app.SafeStopButton.Enable = false
            app.OpenModelButton.Enable = true
            app.MilButton.Enable = true
            app.CodegenButton.Enable = true
            app.ResultButton.Enable = true
        elseif mode == "live"
            app.set_connection_controls(true)
            app.ModeStatusLabel.Text = "实时联合仿真  |  50 Hz 已通过，200 Hz 能力待验证"
            app.ProfileDropDown.Items = ["official_pid_attitude_thrust_v1 [候选]", "official_pid + awff_v1 [候选]"]
            app.ProfileDropDown.Value = "official_pid_attitude_thrust_v1 [候选]"
            app.MissionDropDown.Items = ["起飞-悬停-降落"]
            app.MissionDropDown.Value = "起飞-悬停-降落"
            app.PositionDropDown.Items = ["PX4CTRL 官方位置外环 PID"]
            app.PositionDropDown.Value = "PX4CTRL 官方位置外环 PID"
            app.AttitudeDropDown.Items = ["PX4 内置姿态/角速度环 [锁定]", "INDI [当前模式不可用]", "SMC [当前模式不可用]", "Backstepping [当前模式不可用]"]
            app.AttitudeDropDown.Value = "PX4 内置姿态/角速度环 [锁定]"
            app.AttitudeDropDown.Enable = false
            app.OutputDropDown.Items = ["ATTITUDE_THRUST [锁定]"]
            app.OutputDropDown.Value = "ATTITUDE_THRUST [锁定]"
            app.OutputDropDown.Enable = false
            app.CapabilityLabel.Text = "实时能力门禁\n目标扫描 50 / 100 / 200 Hz；只有同频 RT0 通过后才能发布对应 Profile。"
            app.CapabilityLabel.BackgroundColor = WAIT_COLOR
            app.ValidateButton.Enable = true
            app.PublishButton.Enable = true
            app.PrepareButton.Enable = false
            app.QgcButton.Enable = false
            app.SafeStopButton.Enable = false
            app.OpenModelButton.Enable = true
            app.MilButton.Enable = false
            app.CodegenButton.Enable = false
            app.ResultButton.Enable = true
            live_response = app.refresh_live_capability()
            live_reason = get(live_response, "reason_code", "unknown")
        else
            app.set_connection_controls(false)
            app.ModeStatusLabel.Text = "生成代码部署  |  Model Studio 发布并准备，QGC 执行飞行"
            app.ProfileDropDown.Items = ["已发布 generated-C Profile", "实验控制器 Profile [未通过门禁]"]
            app.ProfileDropDown.Value = "已发布 generated-C Profile"
            app.MissionDropDown.Items = ["起飞-悬停-降落", "八字轨迹", "自主避障", "多机编队"]
            app.PositionDropDown.Items = ["由已发布 Profile 冻结"]
            app.PositionDropDown.Value = "由已发布 Profile 冻结"
            app.AttitudeDropDown.Items = ["由 output_variant 与 Profile 冻结"]
            app.AttitudeDropDown.Value = "由 output_variant 与 Profile 冻结"
            app.AttitudeDropDown.Enable = false
            app.OutputDropDown.Items = ["由已发布 Profile 冻结"]
            app.OutputDropDown.Value = "由已发布 Profile 冻结"
            app.OutputDropDown.Enable = false
            app.CapabilityLabel.Text = "部署边界\n控制器参数和输出边界在起飞前冻结；QGC 只选择 Profile 和任务工件。"
            app.CapabilityLabel.BackgroundColor = READY_COLOR
            app.ValidateButton.Enable = true
            app.PublishButton.Enable = true
            app.PrepareButton.Enable = true
            app.QgcButton.Enable = true
            app.SafeStopButton.Enable = false
            app.OpenModelButton.Enable = true
            app.MilButton.Enable = false
            app.CodegenButton.Enable = true
            app.ResultButton.Enable = true
        end
        app.refresh_summary()
        app.StatusLabel.Text = mode == "live" ?
            "已读取 MWORKS Live 能力门禁：" * live_reason :
            "界面审核模式：已切换到“" * app.ModeStatusLabel.Text * "”。未调用任何运行时。"
    end

    function OfflineModePressed(app, event)
        app.set_mode("offline")
    end

    function LiveModePressed(app, event)
        app.set_mode("live")
    end

    function DeployModePressed(app, event)
        app.set_mode("deploy")
    end

    function SelectionChanged(app, event)
        app.refresh_summary()
        app.StatusLabel.Text = "配置已修改，尚未校验或发布。"
    end

    function ConnectionChanged(app, event)
        app.ConnectionStatusLabel.Text = "连接配置已修改，尚未测试；prepare 将保持阻断。"
        app.ConnectionStatusLabel.BackgroundColor = WAIT_COLOR
        app.PrepareButton.Enable = false
    end

    function TestConnectionPressed(app, event)
        app.TestConnectionButton.Enable = false
        app.ConnectionStatusLabel.Text = "正在测试地址、ROS Master 与 RT1 双向握手..."
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
        app.ConnectionStatusLabel.Text = connected ? "双向连接通过" * detail : "连接阻断：" * reason
        app.ConnectionStatusLabel.BackgroundColor = connected ? READY_COLOR : WAIT_COLOR
        app.TestConnectionButton.Enable = true
        app.PrepareButton.Enable = connected && parse(Int, app.TargetRateDropDown.Value) == 50
        app.StatusLabel.Text = "连接预检：" * reason * detail
    end

    function InjectionChanged(app, event)
        app.InjectionValuesLabel.Text =
            "待应用值\n风速 " * string(round(app.WindSlider.Value; digits=1)) * " m/s  |  " *
            "电机效率 " * join(string.(round.([
                app.Motor1Slider.Value,
                app.Motor2Slider.Value,
                app.Motor3Slider.Value,
                app.Motor4Slider.Value,
            ]; digits=2)), " / ") *
            "\n\n实际值\n风速 0.0 m/s  |  电机效率 1.00 / 1.00 / 1.00 / 1.00"
        app.StatusLabel.Text = "故障参数已修改为待应用值；点击“应用”前不会发送。"
    end

    function ApplyInjectionPressed(app, event)
        app.StatusLabel.Text = "界面审核模式：应用故障需要 Orchestrator accepted -> applied 事件，本版未发送。"
    end

    function RestoreInjectionPressed(app, event)
        app.WindSlider.Value = 0.0
        app.Motor1Slider.Value = 1.0
        app.Motor2Slider.Value = 1.0
        app.Motor3Slider.Value = 1.0
        app.Motor4Slider.Value = 1.0
        app.InjectionChanged(nothing)
        app.StatusLabel.Text = "待应用值已恢复正常；审核版未发送 restore_all_injections。"
    end

    function ReviewAction(app, action)
        app.StatusLabel.Text = "界面审核模式：已触发“" * action * "”界面状态，未连接 MWORKS、QGC 或 Orchestrator。"
    end

    function run_offline_batch(app, profile_id)
        if !isfile(OFFLINE_BATCH_RUNNER)
            app.StatusLabel.Text = "离线批量执行器不存在：" * OFFLINE_BATCH_RUNNER
            return
        end
        slug = lowercase(replace(profile_id, r"[^A-Za-z0-9]+" => "-"))
        batch_id = "app-" * slug * "-" * string(round(Int, time() * 1000))
        command_args = [
            "python",
            OFFLINE_BATCH_RUNNER,
            "--batch-id",
            batch_id,
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
        app.ResultButton.Enable = false
        app.LastOfflineBatchManifest = joinpath(
            PROJECT_ROOT,
            "Results",
            "control_platform",
            "offline_batches",
            batch_id,
            "BATCH_MANIFEST.json",
        )
        app.StatusLabel.Text = "正在执行离线 MWORKS 批次：" * profile_id
        @async begin
            try
                process = run(command; wait=false)
                wait(process)
                app.StatusLabel.Text = "离线批次完成：" * app.LastOfflineBatchManifest
                app.ResultButton.Enable = true
            catch error
                if isfile(app.LastOfflineBatchManifest)
                    app.StatusLabel.Text = "离线批次已阻断或取消，manifest：" * app.LastOfflineBatchManifest
                    app.ResultButton.Enable = true
                else
                    app.StatusLabel.Text = "离线批次阻断：" * sprint(showerror, error)
                end
            finally
                if isfile(app.LastOfflineBatchManifest)
                    app.LastOfflineBatchId = batch_id
                    app.LastOfflineProfile = profile_id
                end
                app.OfflineBatchRunning = false
                app.CurrentOfflineBatchId = ""
                app.MilButton.Text = "运行 MWORKS MIL"
                app.MilButton.Enable = true
            end
        end
    end

    function request_offline_cancel(app)
        if !app.OfflineBatchRunning || isempty(app.CurrentOfflineBatchId)
            app.StatusLabel.Text = "当前没有正在运行的离线批次。"
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
            app.StatusLabel.Text = "已请求安全取消；当前 Profile 完成证据与会话清理后停止后续任务。"
            app.MilButton.Enable = false
        catch error
            app.StatusLabel.Text = "取消请求失败：" * sprint(showerror, error)
        end
    end

    function ValidatePressed(app, event)
        if app.CurrentMode == "live"
            response = app.refresh_live_capability("validate")
            app.StatusLabel.Text = "MWORKS Live Profile 校验结果：" * get(response, "reason_code", "unknown")
        else
            app.ReviewAction("校验配置")
        end
    end
    function PublishPressed(app, event); app.ReviewAction("发布 Profile"); end
    function PreparePressed(app, event)
        if app.CurrentMode == "live"
            response = app.refresh_live_capability("prepare")
            app.StatusLabel.Text = "MWORKS Live prepare：" * get(response, "reason_code", "unknown")
        else
            app.ReviewAction("准备运行")
        end
    end
    function QgcPressed(app, event); app.ReviewAction("进入 QGC"); end
    function SafeStopPressed(app, event); app.ReviewAction("请求安全停止"); end
    function OpenModelPressed(app, event); app.ReviewAction("打开模型"); end
    function MilPressed(app, event)
        if app.OfflineBatchRunning
            app.request_offline_cancel()
            return
        end
        if app.CurrentMode == "offline" && haskey(OFFLINE_PROFILES, app.ProfileDropDown.Value)
            item = OFFLINE_PROFILES[app.ProfileDropDown.Value]
            if item.available
                app.run_offline_batch(item.profile)
            else
                app.StatusLabel.Text = "当前 Profile 已禁用，未启动离线仿真。"
            end
        else
            app.ReviewAction("运行 MWORKS MIL")
        end
    end
    function CodegenPressed(app, event); app.ReviewAction("生成 C 代码"); end
    function ResultPressed(app, event)
        if app.CurrentMode == "offline" && !isempty(app.LastOfflineBatchManifest)
            app.StatusLabel.Text = "离线批次记录：" * app.LastOfflineBatchManifest * "\n结果索引：" * OFFLINE_BATCH_INDEX
        else
            app.ReviewAction("打开结果")
        end
    end

    function configure_dropdown(app, control, label, position, items, value)
        control.Position = position
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
        app.UIFigure.Position = [30, 30, 1440, 900]
        app.UIFigure.Name = "MoSim Model Studio 0.5 UI Review"
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
        app.configure_action(app.OfflineModeButton, "离线建模验证", "OfflineModePressed", [24, 82, 190, 40])
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
        app.ConnectionStatusLabel.Text = "尚未测试双向连接；200 Hz 为待验证目标。"
        app.ConnectionStatusLabel.WordWrap = true
        app.ConnectionStatusLabel.BackgroundColor = WAIT_COLOR

        app.ChainLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ChainLabel.Position = [468, 346, 470, 100]
        app.ChainLabel.Text = "控制链\n\n任务 / 参考 -> 位置外环 -> 期望姿态与总推力\n-> PX4 内置姿态 / 角速度环 -> 控制分配 -> 四电机\n\nATTITUDE_THRUST v1 中，自研姿态内环不可在线选择。"
        app.ChainLabel.VerticalAlignment = "top"
        app.ChainLabel.WordWrap = true
        app.ChainLabel.BackgroundColor = [0.89, 0.94, 0.96]

        app.ContractLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ContractLabel.Position = [468, 458, 470, 96]
        app.ContractLabel.Text = "三方职责\n\nModel Studio：配置、校验、发布、MIL / codegen、prepare\nQGC：连接、解锁、起飞、任务、降落、安全停止\nOrchestrator：唯一状态机、命令裁决和 RunManifest"
        app.ContractLabel.VerticalAlignment = "top"
        app.ContractLabel.WordWrap = true
        app.ContractLabel.BackgroundColor = [0.94, 0.95, 0.95]

        app.TimingLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.TimingLabel.Position = [468, 566, 470, 164]
        app.TimingLabel.Text = "实时与可观测性\n\n已通过基线：50 Hz  |  目标扫描：50 / 100 / 200 Hz\n每条链路记录 rate / latency / jitter / loss / bandwidth\nGazebo 记录 RTF；UE 记录 FPS 与 Game / Draw / GPU。\n\n200 Hz 未通过 RT0 前禁止 prepare。"
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
        app.StatusLabel.Position = [24, 810, 1392, 62]
        app.StatusLabel.VerticalAlignment = "top"
        app.StatusLabel.WordWrap = true
        app.StatusLabel.BackgroundColor = [0.90, 0.93, 0.94]

        app.set_mode("live")
        app.InjectionChanged(nothing)
        app.StatusLabel.Text = "Model Studio 已就绪。测试连接会执行 ROS Master 与 RT1 双向预检；飞行操作仍由 QGC 和 Orchestrator 负责。"
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
