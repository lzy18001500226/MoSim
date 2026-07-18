module MoSimModelStudio

using ObjectOriented
using TyAppDesigner

const ACTIVE_COLOR = [0.08, 0.36, 0.43]
const INACTIVE_COLOR = [0.88, 0.91, 0.92]
const SECTION_COLOR = [0.12, 0.25, 0.32]
const READY_COLOR = [0.86, 0.95, 0.89]
const WAIT_COLOR = [0.98, 0.93, 0.80]
const MUTED_COLOR = [0.93, 0.94, 0.94]

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

    function set_button_state(app, button, active)
        button.BackgroundColor = active ? ACTIVE_COLOR : INACTIVE_COLOR
        button.FontColor = active ? [1.0, 1.0, 1.0] : [0.20, 0.25, 0.28]
        button.FontWeight = "bold"
    end

    function refresh_summary(app)
        app.ProfileSummaryLabel.Text =
            "实验 Profile\n" * app.ProfileDropDown.Value *
            "\n\n任务：" * app.MissionDropDown.Value *
            "\n外环：" * app.PositionDropDown.Value *
            "\n增强：" * app.AugmentationDropDown.Value
    end

    function set_mode(app, mode)
        app.CurrentMode = mode
        app.set_button_state(app.OfflineModeButton, mode == "offline")
        app.set_button_state(app.LiveModeButton, mode == "live")
        app.set_button_state(app.DeployModeButton, mode == "deploy")

        if mode == "offline"
            app.ModeStatusLabel.Text = "离线建模验证  |  Model Studio 拥有模型检查、MIL、代码生成和结果操作权"
            app.ProfileDropDown.Items = ["控制器组合实验", "官方整机基线", "图形化 Sysblock 审核"]
            app.ProfileDropDown.Value = "控制器组合实验"
            app.MissionDropDown.Items = ["起飞-悬停-降落", "阶梯高度指令", "八字轨迹"]
            app.PositionDropDown.Items = ["PX4CTRL 官方位置外环 PID", "改进 PID", "Linear MPC", "NMPC"]
            app.AttitudeDropDown.Items = ["PID", "INDI", "SMC", "Backstepping"]
            app.AttitudeDropDown.Value = "PID"
            app.AttitudeDropDown.Enable = true
            app.OutputDropDown.Items = ["模型内部控制量", "ATTITUDE_THRUST", "BODY_RATE_THRUST", "WRENCH"]
            app.OutputDropDown.Value = "模型内部控制量"
            app.OutputDropDown.Enable = true
            app.CapabilityLabel.Text = "离线能力\n可组合完整控制链；每个组合仍需分别通过图形模型、MIL、结果和代码生成门禁。"
            app.CapabilityLabel.BackgroundColor = READY_COLOR
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
            app.ModeStatusLabel.Text = "实时联合仿真  |  RT0 能力待验证，MWORKS Live 当前可见禁用"
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
            app.CapabilityLabel.Text = "实时能力门禁\n候选 100 Hz / 10 ms；RT0 前不可准备飞行，不得把候选参数写成已验证能力。"
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
        else
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
        app.StatusLabel.Text = "界面审核模式：已切换到“" * app.ModeStatusLabel.Text * "”。未调用任何运行时。"
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

    function ValidatePressed(app, event); app.ReviewAction("校验配置"); end
    function PublishPressed(app, event); app.ReviewAction("发布 Profile"); end
    function PreparePressed(app, event); app.ReviewAction("准备运行"); end
    function QgcPressed(app, event); app.ReviewAction("进入 QGC"); end
    function SafeStopPressed(app, event); app.ReviewAction("请求安全停止"); end
    function OpenModelPressed(app, event); app.ReviewAction("打开模型"); end
    function MilPressed(app, event); app.ReviewAction("运行 MWORKS MIL"); end
    function CodegenPressed(app, event); app.ReviewAction("生成 C 代码"); end
    function ResultPressed(app, event); app.ReviewAction("打开结果"); end

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

        app.ChainLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ChainLabel.Position = [468, 192, 470, 190]
        app.ChainLabel.Text = "控制链\n\n任务 / 参考 -> 位置外环 -> 期望姿态与总推力\n-> PX4 内置姿态 / 角速度环 -> 控制分配 -> 四电机\n\nATTITUDE_THRUST v1 中，自研姿态内环不可在线选择。"
        app.ChainLabel.VerticalAlignment = "top"
        app.ChainLabel.WordWrap = true
        app.ChainLabel.BackgroundColor = [0.89, 0.94, 0.96]

        app.ContractLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.ContractLabel.Position = [468, 394, 470, 144]
        app.ContractLabel.Text = "三方职责\n\nModel Studio：配置、校验、发布、MIL / codegen、prepare\nQGC：连接、解锁、起飞、任务、降落、安全停止\nOrchestrator：唯一状态机、命令裁决和 RunManifest"
        app.ContractLabel.VerticalAlignment = "top"
        app.ContractLabel.WordWrap = true
        app.ContractLabel.BackgroundColor = [0.94, 0.95, 0.95]

        app.TimingLabel = TyAppDesigner.uilabel(app.UIFigure)
        app.TimingLabel.Position = [468, 550, 470, 180]
        app.TimingLabel.Text = "候选实时合同（未验证）\n\nframe: mosim_enu_flu_quaternion_xyzw_v1\nrate: 100 Hz  |  deadline: 10 ms\ncommand age: 50 ms  |  failsafe escalation: 100 ms\n\nRT0 未通过，MWORKS Live 保持禁用。"
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
        app.StatusLabel.Text = "界面审核版已就绪。所有按钮仅演示状态，不连接 MWORKS、Gazebo、QGC 或 Orchestrator。"
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
