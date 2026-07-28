import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtLocation
import QtPositioning

import QGroundControl
import QGroundControl.Controls
import QGroundControl.FlightDisplay
import QGroundControl.FlightMap
import QGroundControl.Palette
import QGroundControl.ScreenTools

Item {
    id: root
    focus: true
    property bool manualKeyboardEnabled: false
    property bool manualForward: false
    property bool manualBackward: false
    property bool manualLeft: false
    property bool manualRight: false
    property string observedFlightRunId: ""
    property bool observedArmedDuringRun: false

    property var parentToolInsets
    property var totalToolInsets: toolInsets
    property var mapControl
    property bool operatorProfileCatalogSynced: false
    property bool _showSingleVehicleUI: true
    readonly property var activeVehicle: QGroundControl.multiVehicleManager.activeVehicle
    readonly property var profiles: mosimOrchestrator.operatorProfiles || []
    readonly property var emptyProfile: ({
        id: "", label: "正在读取已发布配置", profile_path: "", controller_id: "",
        controller_label: "-", vehicle_count: 0, enabled: false,
        disabled_reason: "正在读取已发布配置", operator_mode: "mission_adapter", manual_control: false
    })

    readonly property bool manualTaskSelected: currentProfile().manual_control === true
    readonly property bool flightConfigurationEditable: !mosimOrchestrator.busy
                                                        && mosimOrchestrator.lifecycleState !== "starting"
                                                        && mosimOrchestrator.lifecycleState !== "running"
    readonly property bool manualControlReady: manualTaskSelected
                                                && selectionMatchesPreparedRun()
                                                && mosimOrchestrator.lifecycleState === "running"
                                                && activeVehicle !== null
                                                && activeVehicle.initialConnectComplete
                                                && activeVehicle.armed
                                                && activeVehicle.flightMode === "Position"
    readonly property bool faultStagingAllowed: !mosimOrchestrator.busy
                                                && mosimOrchestrator.runId.length > 0
                                                && ["ready", "starting", "running"].indexOf(mosimOrchestrator.lifecycleState) >= 0
    readonly property bool faultApplyAllowed: !mosimOrchestrator.busy
                                              && mosimOrchestrator.lifecycleState === "running"
                                              && pendingInjectionIsReady()
    readonly property bool faultRestoreAllowed: !mosimOrchestrator.busy
                                                && mosimOrchestrator.lifecycleState === "running"

    function injectionVehicleIds() {
        var count = Math.max(0, Number(currentProfile().vehicle_count || 0))
        var vehicles = []
        for (var index = 1; index <= count; ++index)
            vehicles.push("uav" + index)
        return vehicles
    }

    function pendingInjectionCommand() {
        var pending = mosimOrchestrator.pendingInjection || ({})
        return pending.command || ({})
    }

    function pendingInjectionIsReady() {
        var pending = mosimOrchestrator.pendingInjection || ({})
        var command = pendingInjectionCommand()
        return String(pending.state || "") === "pending" && String(command.target || "") !== ""
    }

    function pendingInjectionText() {
        var pending = mosimOrchestrator.pendingInjection || ({})
        var command = pendingInjectionCommand()
        var target = String(command.target || "")
        if (target === "")
            return "暂无待应用故障"
        var vehicle = String(command.vehicle_id || "-")
        var detail = ""
        if (target === "wind_speed_mps")
            detail = "风扰 " + Number(command.value || 0).toFixed(1) + " m/s"
        else if (target === "motor_effectiveness")
            detail = "电机 " + String(command.rotor_index || "-")
                    + " 效率 " + Number(command.value || 0).toFixed(2)
        else
            detail = target + " " + String(command.value || "-")
        if (String(pending.state || "") === "apply_failed")
            return "应用未确认，请重新暂存：" + vehicle + " · " + detail
        return "待应用：" + vehicle + " · " + detail
    }

    function sendManualStick(forceNeutral) {
        if (!activeVehicle || !activeVehicle.initialConnectComplete)
            return
        if (!forceNeutral && !manualControlReady)
            return
        var pitch = manualKeyboardEnabled && !forceNeutral
                ? (manualForward ? 0.35 : 0.0) + (manualBackward ? -0.35 : 0.0)
                : 0.0
        var roll = manualKeyboardEnabled && !forceNeutral
                ? (manualRight ? 0.35 : 0.0) + (manualLeft ? -0.35 : 0.0)
                : 0.0
        // MANUAL_CONTROL z uses 0..1000, so QGC's centered throttle is 0.5.
        activeVehicle.virtualTabletJoystickValue(roll, pitch, 0.0, 0.5)
    }

    function updateManualVelocity() {
        sendManualStick()
    }

    function qgcConnectedVehicleCount() {
        var vehicles = QGroundControl.multiVehicleManager.vehicles
        var connected = 0
        for (var index = 0; index < vehicles.count; ++index) {
            var vehicle = vehicles.get(index)
            if (vehicle && vehicle.initialConnectComplete)
                connected += 1
        }
        return connected
    }

    function qgcArmedVehicleCount() {
        var vehicles = QGroundControl.multiVehicleManager.vehicles
        var armed = 0
        for (var index = 0; index < vehicles.count; ++index) {
            var vehicle = vehicles.get(index)
            if (vehicle && vehicle.armed)
                armed += 1
        }
        return armed
    }

    function canStopRuntime() {
        var expected = currentProfile().vehicle_count
        if (manualTaskSelected)
            return qgcConnectedVehicleCount() === expected && qgcArmedVehicleCount() === 0
        return mosimOrchestrator.operationState === "completed"
                && mosimOrchestrator.operationStage === "Safe stop complete"
    }

    function flightPhaseText() {
        var profile = currentProfile()
        var expected = profile.vehicle_count
        var connected = qgcConnectedVehicleCount()
        var armed = qgcArmedVehicleCount()
        if (mosimOrchestrator.operationState === "running"
                && (mosimOrchestrator.operationStage.indexOf("Safe stop") >= 0
                    || mosimOrchestrator.operationStage.indexOf("Quiescing") >= 0
                    || mosimOrchestrator.operationStage.indexOf("Holding position") >= 0
                    || mosimOrchestrator.operationStage === "Landing"))
            return "安全停止执行中：" + operationStageText(mosimOrchestrator.operationStage)
        if (mosimOrchestrator.lifecycleState === "completed")
            return "任务进程已结束；请确认全部飞机已落地并查看结果。"
        if (mosimOrchestrator.lifecycleState === "blocked" || mosimOrchestrator.lifecycleState === "failed")
            return "任务异常；禁止重复启动，请按告警执行悬停、降落或安全停止。"
        if (mosimOrchestrator.lifecycleState !== "starting" && mosimOrchestrator.lifecycleState !== "running")
            return "尚未启动飞行运行时。"
        if (connected < expected)
            return "等待飞机连接：" + connected + "/" + expected
        if (profile.manual_control === true) {
            if (armed === 0)
                return observedArmedDuringRun ? "飞机已落地并锁定；现在可以停止当前仿真。"
                                              : "飞机已连接；下一步使用QGC原生解锁/起飞。"
            if (activeVehicle && activeVehicle.flightMode !== "Position")
                return "飞机已解锁；下一步切换到Position模式。"
            return manualKeyboardEnabled ? "Position模式；W/A/S/D定点操纵已启用。"
                                         : "Position模式；现在可以启用W/A/S/D定点操纵。"
        }
        if (armed === 0)
            return observedArmedDuringRun ? "自动任务已完成飞行并落地；等待结果包。"
                                          : "全部飞机已连接；等待任务Adapter自动解锁和起飞。"
        if (armed < expected)
            return "自动任务正在逐机解锁/起飞：" + armed + "/" + expected + " 已解锁。"
        return "全部飞机已解锁；自动起飞或任务执行中。"
    }

    function reasonText(reason) {
        var labels = {
            "idle": "等待操作",
            "request_pending": "请求处理中",
            "run_prepared": "配置已验证并冻结",
            "run_starting": "正在启动飞行运行时",
            "run_started": "飞行运行时已启动",
            "run_state_ready": "运行状态已刷新",
            "runtime_readiness_gate_pending": "等待Gazebo/PX4/MAVROS就绪",
            "runtime_ready": "飞行运行时已就绪",
            "run_stopped": "当前仿真已停止",
            "safe_stop_requested": "已请求安全停止",
            "safe_stop_request_reused": "安全停止请求已存在",
            "safe_stop_completed": "安全停止完成，飞机已落地锁定",
            "safe_stop_disarm_not_confirmed": "安全停止未确认解除武装",
            "safe_stop_adapter_not_supported": "当前任务不支持自动安全停止，请使用QGC原生降落",
            "runtime_stop_requires_fresh_disarm_evidence": "缺少实时解除武装证据，禁止关闭飞行进程",
            "runtime_stop_telemetry_stale": "飞机遥测已过期，禁止关闭飞行进程",
            "runtime_stop_vehicle_state_incomplete": "飞机状态不完整，禁止关闭飞行进程",
            "runtime_stop_rejected_vehicle_armed": "仍有飞机处于解锁状态，请先安全停止或降落",
            "run_reset": "任务已复位",
            "active_run_must_stop_before_prepare": "已有任务正在运行，请先安全结束",
            "telemetry_ready": "遥测已刷新",
            "telemetry_not_available": "遥测暂不可用",
            "runtime_gate_completed": "任务运行完成",
            "runtime_gate_failed": "任务运行失败",
            "runtime_process_spawn_failed": "飞行运行时启动失败",
            "runtime_profile_not_allowlisted": "该运行配置未获准启动",
            "display_attached": "显示窗口已连接",
            "display_detached": "显示窗口已分离",
            "rviz_sessions_closed": "RViz窗口已关闭",
            "injection_staged": "故障已暂存，等待人工应用",
            "injection_staged_replaced": "已替换待应用故障",
            "injection_pending_missing": "没有待应用故障",
            "injection_pending_requires_restage": "上次应用未确认，请重新暂存",
            "run_not_stageable": "当前任务状态不允许暂存故障",
            "run_not_active": "飞行运行时未就绪，不能应用故障",
            "restore_normal_applied": "已恢复正常：风扰归零，四电机效率恢复",
            "restore_normal_partial_failure": "恢复正常部分失败，请查看运行日志",
            "agent_proposal_ready": "任务建议已生成，等待人工确认",
            "agent_prompt_empty": "请输入任务需求",
            "agent_prompt_too_long": "任务描述过长，请简化后重试",
            "agent_intent_not_recognized": "未识别任务，请明确填写定点、8字、FUEL或三机编队"
        }
        return labels[reason] || reason
    }

    function operationStageText(stage) {
        var labels = {
            "Idle": "等待操作",
            "Starting runtime process": "正在启动飞行运行时",
            "Waiting for runtime readiness": "等待Gazebo、PX4和MAVROS就绪",
            "Runtime ready": "飞行运行时已就绪",
            "Runtime start failed": "飞行运行时启动失败",
            "Starting display session": "正在启动显示会话",
            "Waiting for display readiness": "等待UE/RViz显示就绪",
            "Displays ready": "显示窗口已就绪"
            ,"Safe stop requested": "已请求安全停止"
            ,"Quiescing planner commands": "正在停止规划器命令"
            ,"Holding position": "正在悬停稳定"
            ,"Landing": "正在降落"
            ,"Disarmed": "已落地并解除武装"
            ,"Safe stop complete": "安全停止完成"
            ,"Safe stop failed": "安全停止失败"
        }
        return labels[stage] || stage
    }

    function handleManualKey(key, pressed, event) {
        if (!manualKeyboardEnabled)
            return false
        if (key === Qt.Key_W) manualForward = pressed
        else if (key === Qt.Key_S) manualBackward = pressed
        else if (key === Qt.Key_A) manualLeft = pressed
        else if (key === Qt.Key_D) manualRight = pressed
        else return false
        updateManualVelocity()
        event.accepted = true
        return true
    }

    Keys.onPressed: function(event) {
        handleManualKey(event.key, true, event)
    }
    Keys.onReleased: function(event) {
        handleManualKey(event.key, false, event)
    }

    Timer {
        interval: 40
        repeat: true
        running: manualKeyboardEnabled && manualControlReady
        onTriggered: root.sendManualStick()
    }

    Timer {
        interval: 250
        repeat: true
        running: true
        onTriggered: {
            if (root.observedFlightRunId !== mosimOrchestrator.runId) {
                root.observedFlightRunId = mosimOrchestrator.runId
                root.observedArmedDuringRun = false
            }
            if (root.qgcArmedVehicleCount() > 0)
                root.observedArmedDuringRun = true
        }
    }

    Timer {
        interval: 500
        repeat: true
        running: mosimOrchestrator.runId !== ""
                 && (mosimOrchestrator.lifecycleState === "starting"
                     || mosimOrchestrator.lifecycleState === "running")
        onTriggered: {
            if (!mosimOrchestrator.busy)
                mosimOrchestrator.refreshTelemetry()
        }
    }

    function runtimeTelemetryFresh() {
        var telemetry = mosimOrchestrator.runtimeTelemetry || ({})
        var timestamp = Number(telemetry.timestamp || 0)
        return telemetry.run_id === mosimOrchestrator.runId
                && timestamp > 0
                && Math.abs(Date.now() / 1000.0 - timestamp) <= 2.5
    }

    function runtimeVehicles() {
        if (!runtimeTelemetryFresh())
            return []
        var vehicles = mosimOrchestrator.runtimeTelemetry.vehicles
        return vehicles && vehicles.length !== undefined ? vehicles : []
    }

    function runtimeVehicleStateText(vehicle) {
        if (!vehicle || !vehicle.state || !vehicle.state.connected)
            return "未连接"
        var mode = String(vehicle.state.mode || "未知模式")
        return vehicle.state.armed ? "已解锁 · " + mode : "已连接 · 未解锁 · " + mode
    }

    function runtimeVehiclePositionText(vehicle) {
        if (!vehicle || !vehicle.state || !vehicle.state.position)
            return "位置：暂不可用"
        var position = vehicle.state.position
        return "位置：X " + Number(position.x).toFixed(2)
                + " m  Y " + Number(position.y).toFixed(2)
                + " m  Z " + Number(position.z).toFixed(2) + " m"
    }

    function runtimeVehicleStateColor(vehicle) {
        if (!vehicle || !vehicle.state || !vehicle.state.connected)
            return qgcPal.colorRed
        return vehicle.state.armed ? qgcPal.colorGreen : qgcPal.colorOrange
    }

    function missionStatus() {
        if (!runtimeTelemetryFresh())
            return ({ transport_state: "unavailable", reason_code: "runtime_telemetry_unavailable" })
        return mosimOrchestrator.runtimeTelemetry.mission_status
                || ({ transport_state: "unavailable", reason_code: "mission_status_missing" })
    }

    function missionPhaseText(phase) {
        var labels = {
            "init": "任务节点初始化",
            "wait_static_odom": "等待静态定位",
            "pre_takeoff_state_stable": "起飞前状态检查",
            "pre_takeoff_settle": "编队起飞前稳定检查",
            "takeoff": "自动解锁与起飞",
            "hover_before": "起飞后悬停",
            "figure8": "8字轨迹执行",
            "ego_triggered": "规划器已触发",
            "ego_execute": "规划/编队任务执行",
            "exploration_execute": "自主探索执行",
            "safe_stop_hover": "安全停止悬停",
            "land": "自动降落",
            "done": "任务结束"
        }
        return labels[String(phase || "")] || String(phase || "未知阶段")
    }

    function missionStatusText() {
        if (currentProfile().manual_control === true)
            return "不适用：当前由QGC原生控制，用户负责解锁、起飞和降落"
        var status = missionStatus()
        if (status.transport_state === "unavailable")
            return "等待任务Adapter状态"
        if (status.transport_state === "stale")
            return "任务Adapter状态已过期，禁止据此判断任务成功"
        if (status.terminal)
            return (status.accepted ? "终态已通过" : "终态未通过")
                    + " · " + missionPhaseText(status.phase)
        return "实时阶段 · " + missionPhaseText(status.phase)
    }

    function missionStatusColor() {
        if (currentProfile().manual_control === true)
            return qgcPal.text
        var status = missionStatus()
        if (status.transport_state === "unavailable" || status.transport_state === "stale")
            return qgcPal.colorOrange
        if (status.terminal)
            return status.accepted ? qgcPal.colorGreen : qgcPal.colorRed
        return qgcPal.colorGreen
    }

    function missionAdapterVehicleText(vehicle) {
        if (!vehicle)
            return "状态不可用"
        var connection = vehicle.connected ? "已连接" : "未连接"
        var arm = vehicle.armed ? "已解锁" : "未解锁"
        return connection + " · " + arm + " · " + String(vehicle.mode || "未知模式")
    }

    QGCPalette { id: qgcPal; colorGroupEnabled: true }

    // The custom Flight Console owns the visual surface. Preserve the native
    // QGC map object and restore it when this layer is unloaded, but do not let
    // its online tiles bleed through the Factory map.
    Component.onCompleted: {
        forceActiveFocus()
        if (mapControl)
            mapControl.visible = false
    }
    Component.onDestruction: {
        mosimOrchestrator.setManualControlEnabled(false)
        if (mapControl)
            mapControl.visible = true
    }

    function currentProfile() {
        if (profileBox.currentIndex >= 0 && profileBox.currentIndex < profiles.length)
            return profiles[profileBox.currentIndex]
        return emptyProfile
    }

    function profileIndex(profileId) {
        for (var index = 0; index < profiles.length; ++index) {
            if (profiles[index].id === profileId)
                return index
        }
        return -1
    }

    function agentProposalReady() {
        var proposal = mosimOrchestrator.agentProposal || ({})
        var index = profileIndex(String(proposal.profile_id || ""))
        return proposal.requires_user_confirmation === true
                && proposal.may_start_flight === false
                && index >= 0 && profiles[index].enabled === true
    }

    function confirmAgentProposal() {
        if (!agentProposalReady() || !flightConfigurationEditable || mosimOrchestrator.busy)
            return
        var proposal = mosimOrchestrator.agentProposal
        var index = profileIndex(String(proposal.profile_id))
        if (index < 0 || !profiles[index].enabled)
            return
        profileBox.currentIndex = index
        syncProfileSelection()
        mosimOrchestrator.clearAgentProposal()
        var profile = currentProfile()
        mosimOrchestrator.prepareRun(String(profile.profile_path), String(profile.controller_id),
                                     Number(profile.vehicle_count), 0,
                                     profile.manual_control === true)
    }

    function syncProfileSelection() {
        injectionVehicle.currentIndex = 0
        manualModeCheck.checked = false
    }

    function taskGuideText() {
        var profile = currentProfile()
        if (!profile.enabled)
            return "当前不可启动：" + profile.disabled_reason
        if (profile.manual_control === true)
            return "操作顺序：启动并等待连接 → 使用QGC原生解锁/起飞 → 切换Position模式 → 点击键盘控制区后使用W/A/S/D → 使用QGC原生降落。"
        return "操作顺序：验证配置 → 启动任务。Orchestrator将自动完成连接、解锁、起飞、任务执行和降落；全过程必须在QGC确认阶段、告警和结束状态。"
    }

    function flightAuthorityText() {
        var profile = currentProfile()
        if (!profile.enabled)
            return "未授权：当前Profile尚未通过运行门禁"
        if (profile.manual_control === true)
            return "QGC原生控制：你负责解锁、起飞、Position模式操纵和降落"
        if (profile.vehicle_count > 1)
            return "编队Mission Adapter独占控制：自动逐机解锁、起飞、编队任务和降落"
        return "任务Mission Adapter独占控制：自动解锁、起飞、任务执行和降落"
    }

    function selectionMatchesPreparedRun() {
        if (mosimOrchestrator.runId === "")
            return false
        var profile = currentProfile()
        return mosimOrchestrator.experimentProfileId === profile.id
                && mosimOrchestrator.selectedControllerId === profile.controller_id
                && mosimOrchestrator.selectedVehicleCount === profile.vehicle_count
    }

    function nextOperatorStepText() {
        var profile = currentProfile()
        if (!profile.enabled)
            return "当前任务尚未通过运行门禁，不能启动。"
        if (mosimOrchestrator.busy)
            return "正在处理请求，请勿重复点击。"
        if (mosimOrchestrator.lifecycleState === "starting")
            return "正在启动 Gazebo、PX4、MAVROS 和任务节点，请等待连接完成。"
        if (mosimOrchestrator.lifecycleState === "running" && !selectionMatchesPreparedRun())
            return "另一个任务仍在运行：先确认飞机已降落且未解锁，再点击“停止当前仿真”，然后验证所选任务。"
        if (mosimOrchestrator.lifecycleState === "running" && selectionMatchesPreparedRun()) {
            if (profile.manual_control !== true)
                return "自动任务已接管：在QGC确认连接、解锁、起飞、执行和降落阶段；异常时请求安全停止。"
            if (!activeVehicle)
                return "仿真已运行，正在等待 QGC 发现飞机。"
            if (!activeVehicle.initialConnectComplete)
                return "QGC已发现飞机，正在同步参数和飞行状态；连接完成前不要解锁。"
            if (observedArmedDuringRun && !activeVehicle.armed)
                return "飞机已降落并锁定：确认高度为零后，可以点击“停止当前仿真”。"
            if (!activeVehicle.armed)
                return "飞机已连接：使用QGC原生飞行操作栏执行解锁和起飞。"
            if (!activeVehicle.flying)
                return "飞机已解锁但仍在地面：使用QGC原生飞行操作栏执行起飞。"
            if (activeVehicle.flightMode !== "Position")
                return "飞机已起飞：将QGC飞行模式切换为Position。"
            if (!manualKeyboardEnabled)
                return "飞机已悬停在Position模式：勾选“启用W/A/S/D定点操纵”。"
            return "W/A/S/D定点操纵已启用；结束时使用QGC原生降落，落地锁定后再停止仿真。"
        }
        if (mosimOrchestrator.runId !== "" && !selectionMatchesPreparedRun())
            return "当前选择与已验证任务不一致，请重新点击“验证配置”。"
        if (mosimOrchestrator.lifecycleState === "ready" && selectionMatchesPreparedRun())
            return "配置已冻结，可以点击“启动仿真并连接飞机”。"
        if (mosimOrchestrator.lifecycleState === "blocked" || mosimOrchestrator.lifecycleState === "failed")
            return "任务启动失败：查看上方原因，确认飞机已降落后复位或重新验证。"
        if (mosimOrchestrator.lifecycleState === "completed")
            return "本次任务已结束，可以查看结果包或选择下一个任务重新验证。"
        return "先选择已发布任务，然后点击“验证配置”。"
    }

    function operatorChecklist() {
        var profile = currentProfile()
        var selected = selectionMatchesPreparedRun()
        var running = mosimOrchestrator.lifecycleState === "starting"
                || mosimOrchestrator.lifecycleState === "running"
        var connected = qgcConnectedVehicleCount() >= profile.vehicle_count
        var armed = qgcArmedVehicleCount() >= profile.vehicle_count
        var manualAirborne = profile.manual_control === true && activeVehicle
                && activeVehicle.initialConnectComplete && activeVehicle.armed && activeVehicle.flying
        var manualExecuting = manualAirborne && activeVehicle.flightMode === "Position"
        var mission = missionStatus()
        var missionPhase = String(mission.phase || "")
        var automaticExecuting = profile.manual_control !== true
                && mission.transport_state !== "unavailable"
                && mission.transport_state !== "stale"
                && !mission.terminal
                && ["hover_before", "figure8", "ego_triggered", "ego_execute",
                    "exploration_execute", "safe_stop_hover", "land"].indexOf(missionPhase) >= 0
        var missionFailed = profile.manual_control !== true && mission.terminal === true
                && mission.accepted !== true
        var landed = profile.manual_control === true
                ? observedArmedDuringRun && connected && qgcArmedVehicleCount() === 0
                : mission.terminal === true && mission.accepted === true && qgcArmedVehicleCount() === 0
        var takeoffComplete = profile.manual_control === true
                ? manualAirborne || landed
                : observedArmedDuringRun || automaticExecuting || mission.terminal === true
        var executionState = profile.manual_control === true
                ? (landed ? "已完成" : (manualExecuting ? "当前" : "等待"))
                : (missionFailed ? "失败"
                                 : (mission.terminal === true ? "已完成"
                                                              : (automaticExecuting ? "当前" : "等待")))
        var landingActive = profile.manual_control === true
                ? activeVehicle && activeVehicle.landing
                : ["safe_stop_hover", "land"].indexOf(missionPhase) >= 0
        return [
            { label: "1. 配置冻结", state: selected ? "已完成" : "当前" },
            { label: "2. 运行时与飞机连接", state: connected ? "已完成" : (running ? "当前" : "等待") },
            { label: profile.manual_control === true ? "3. QGC原生解锁与起飞" : "3. Adapter自动解锁与起飞",
              state: takeoffComplete ? "已完成" : (connected ? "当前" : "等待") },
            { label: profile.manual_control === true ? "4. Position / W/A/S/D" : "4. 自主任务执行",
              state: executionState },
            { label: "5. 降落、锁定与结束",
              state: landed ? "已完成" : (missionFailed ? "失败" : (landingActive ? "当前" : "等待")) }
        ]
    }

    function operatorChecklistColor(state) {
        if (state === "已完成")
            return qgcPal.colorGreen
        if (state === "当前")
            return qgcPal.colorOrange
        if (state === "失败")
            return qgcPal.colorRed
        return qgcPal.text
    }

    readonly property var flightStageLabels: ["配置", "环境", "连接", "起飞", "执行", "降落"]

    function currentFlightStageIndex() {
        var profile = currentProfile()
        var connected = qgcConnectedVehicleCount() >= profile.vehicle_count
        var armed = qgcArmedVehicleCount() > 0
        var mission = missionStatus()
        var missionPhase = String(mission.phase || "")
        if (mosimOrchestrator.lifecycleState === "completed"
                || mission.terminal === true
                || missionPhase === "land"
                || missionPhase === "safe_stop_hover"
                || (observedArmedDuringRun && connected && !armed))
            return 5
        if (armed || ["hover_before", "figure8", "ego_triggered", "ego_execute",
                      "exploration_execute"].indexOf(missionPhase) >= 0)
            return 4
        if (connected)
            return 3
        if (mosimOrchestrator.lifecycleState === "starting"
                || mosimOrchestrator.lifecycleState === "running")
            return 2
        if (mosimOrchestrator.lifecycleState === "ready" || mosimOrchestrator.runId !== "")
            return 1
        return 0
    }

    QGCToolInsets {
        id: toolInsets
        leftEdgeTopInset: parentToolInsets.leftEdgeTopInset
        leftEdgeCenterInset: parentToolInsets.leftEdgeCenterInset
        leftEdgeBottomInset: parentToolInsets.leftEdgeBottomInset
        rightEdgeTopInset: consolePanel.visible ? consolePanel.width : parentToolInsets.rightEdgeTopInset
        rightEdgeCenterInset: consolePanel.visible ? consolePanel.width : parentToolInsets.rightEdgeCenterInset
        rightEdgeBottomInset: consolePanel.visible ? consolePanel.width : parentToolInsets.rightEdgeBottomInset
        topEdgeLeftInset: parentToolInsets.topEdgeLeftInset
        topEdgeCenterInset: parentToolInsets.topEdgeCenterInset
        topEdgeRightInset: parentToolInsets.topEdgeRightInset
        bottomEdgeLeftInset: parentToolInsets.bottomEdgeLeftInset
        bottomEdgeCenterInset: parentToolInsets.bottomEdgeCenterInset
        bottomEdgeRightInset: parentToolInsets.bottomEdgeRightInset
    }

    FactoryFlyMap {
        id: factoryFlyMap
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: consolePanel.left
        anchors.bottom: parent.bottom
        z: 0
        mapConfig: mosimOrchestrator.operatorMap || ({})
        runManifest: mosimOrchestrator.runManifest || ({})
        mapState: (mosimOrchestrator.runtimeTelemetry || ({})).map_state || ({})
        runId: mosimOrchestrator.runId
    }

    FlyViewBottomRightRowLayout {
        id: flightTelemetryHud
        anchors.right: consolePanel.left
        anchors.bottom: parent.bottom
        anchors.margins: ScreenTools.defaultFontPixelWidth * 0.75
        spacing: ScreenTools.defaultFontPixelWidth
        visible: activeVehicle !== null
        z: 10
    }

    Rectangle {
        id: consolePanel
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: Math.min(360, Math.max(320, parent.width * 0.30))
        color: qgcPal.window
        z: 100
        border.color: qgcPal.text
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: ScreenTools.defaultFontPixelWidth
            spacing: ScreenTools.defaultFontPixelHeight * 0.45

            RowLayout {
                objectName: "启动进度"
                Layout.fillWidth: true
                QGCLabel { text: "飞行控制"; font.bold: true; Layout.fillWidth: true }
                QGCLabel {
                    text: flightStageLabels[currentFlightStageIndex()]
                    color: qgcPal.colorOrange
                    font.bold: true
                }
                BusyIndicator { running: mosimOrchestrator.busy; visible: running; implicitWidth: 24; implicitHeight: 24 }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 26
                color: mosimOrchestrator.accepted ? qgcPal.colorGreen : (mosimOrchestrator.reasonCode === "idle" ? qgcPal.windowShade : qgcPal.colorOrange)
                QGCLabel {
                    anchors.fill: parent
                    anchors.margins: 5
                    text: (mosimOrchestrator.accepted ? "成功：" : (mosimOrchestrator.reasonCode === "idle" ? "" : "失败："))
                          + reasonText(mosimOrchestrator.reasonCode)
                    elide: Text.ElideRight
                    color: qgcPal.buttonText
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 42
                spacing: 2
                Repeater {
                    model: flightStageLabels
                    delegate: ColumnLayout {
                        required property string modelData
                        required property int index
                        Layout.fillWidth: true
                        spacing: 2
                        Rectangle {
                            Layout.alignment: Qt.AlignHCenter
                            implicitWidth: index === root.currentFlightStageIndex() ? 12 : 8
                            implicitHeight: implicitWidth
                            radius: implicitWidth / 2
                            color: index < root.currentFlightStageIndex()
                                   ? qgcPal.colorGreen
                                   : (index === root.currentFlightStageIndex()
                                      ? qgcPal.colorOrange : qgcPal.windowShade)
                            border.width: 1
                            border.color: index <= root.currentFlightStageIndex()
                                          ? color : qgcPal.text
                        }
                        QGCLabel {
                            Layout.alignment: Qt.AlignHCenter
                            text: modelData
                            font.pixelSize: ScreenTools.smallFontPixelSize
                            color: index < root.currentFlightStageIndex()
                                   ? qgcPal.colorGreen
                                   : (index === root.currentFlightStageIndex()
                                      ? qgcPal.colorOrange : qgcPal.text)
                            opacity: index > root.currentFlightStageIndex() ? 0.5 : 1.0
                        }
                    }
                }
            }

            TabBar {
                id: tabs
                Layout.fillWidth: true
                TabButton { text: "任务" }
                TabButton { text: "状态" }
                TabButton { text: "故障" }
                TabButton { text: "显示" }
                TabButton { text: "结果" }
                TabButton { text: "助手" }
            }

            StackLayout {
                currentIndex: tabs.currentIndex
                Layout.fillWidth: true
                Layout.fillHeight: true

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: 8
                        QGCLabel {
                            visible: currentProfile().manual_control !== true
                            text: "任务Adapter阶段：" + missionStatusText()
                            color: missionStatusColor()
                            font.bold: true
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            columnSpacing: 8
                            rowSpacing: 7

                            QGCLabel { text: "任务"; font.bold: true }
                            ComboBox {
                                id: profileBox
                                Layout.fillWidth: true
                                enabled: flightConfigurationEditable
                                model: profiles
                                textRole: "label"
                                delegate: ItemDelegate {
                                    width: profileBox.width
                                    text: modelData.label
                                    enabled: modelData.enabled
                                    ToolTip.visible: hovered && !modelData.enabled
                                    ToolTip.text: modelData.disabled_reason
                                }
                                onActivated: syncProfileSelection()
                            }

                            QGCLabel { text: "控制器（已绑定）"; font.bold: true }
                            QGCLabel {
                                Layout.fillWidth: true
                                text: String(currentProfile().controller_label || "-")
                                      + " · " + String(currentProfile().controller_id || "-")
                                wrapMode: Text.Wrap
                            }

                            QGCLabel { text: "无人机（已绑定）"; font.bold: true }
                            QGCLabel {
                                Layout.fillWidth: true
                                text: currentProfile().vehicle_count > 0
                                      ? String(currentProfile().vehicle_count) + " 架"
                                      : "-"
                            }
                        }

                        QGCLabel {
                            Layout.fillWidth: true
                            visible: !currentProfile().enabled
                            text: currentProfile().disabled_reason
                            color: qgcPal.colorOrange
                            wrapMode: Text.Wrap
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton {
                                text: "验证配置"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy
                                         && mosimOrchestrator.lifecycleState !== "starting"
                                         && mosimOrchestrator.lifecycleState !== "running"
                                         && currentProfile().id !== ""
                                         && currentProfile().enabled
                                onClicked: mosimOrchestrator.prepareRun(currentProfile().profile_path,
                                                                        currentProfile().controller_id,
                                                                        currentProfile().vehicle_count, 0,
                                                                        manualTaskSelected)
                            }
                            QGCButton {
                                text: manualTaskSelected ? "启动仿真" : "执行任务"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy
                                         && mosimOrchestrator.lifecycleState === "ready"
                                         && selectionMatchesPreparedRun()
                                onClicked: {
                                    root.forceActiveFocus()
                                    mosimOrchestrator.setManualControlEnabled(false)
                                    mosimOrchestrator.startRun()
                                }
                            }
                        }
                        QGCCheckBox {
                            id: manualModeCheck
                            text: "W/A/S/D定点操纵"
                            visible: manualTaskSelected
                            enabled: manualControlReady
                            onCheckedChanged: {
                                root.manualKeyboardEnabled = checked
                                root.manualForward = false
                                root.manualBackward = false
                                root.manualLeft = false
                                root.manualRight = false
                                root.sendManualStick(!checked)
                            }
                        }
                        QGCButton {
                            text: manualKeyboardEnabled ? "已启用，点击后使用W/A/S/D"
                                                        : "起飞并切换Position后启用"
                            visible: manualTaskSelected
                            Layout.fillWidth: true
                            enabled: manualKeyboardEnabled && manualControlReady
                            onClicked: root.forceActiveFocus()
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton {
                                text: "请求安全停止"
                                Layout.fillWidth: true
                                enabled: !manualTaskSelected
                                         && !mosimOrchestrator.busy
                                         && (mosimOrchestrator.lifecycleState === "starting"
                                             || mosimOrchestrator.lifecycleState === "running")
                                         && mosimOrchestrator.operationState !== "running"
                                onClicked: mosimOrchestrator.requestSafeStop()
                            }
                            QGCButton {
                                text: "停止当前仿真"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy && mosimOrchestrator.runId !== ""
                                         && canStopRuntime()
                                onClicked: mosimOrchestrator.stopRun()
                            }
                            QGCButton {
                                text: "复位任务"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy && mosimOrchestrator.runId !== ""
                                         && (!activeVehicle || !activeVehicle.armed)
                                onClicked: mosimOrchestrator.resetRun()
                            }
                        }
                        QGCLabel {
                            text: "运行 " + (mosimOrchestrator.runId || "-")
                            elide: Text.ElideMiddle
                            Layout.fillWidth: true
                            color: qgcPal.text
                            opacity: 0.6
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: 10
                        QGCLabel { text: "逐机运行状态"; font.bold: true }
                        QGCLabel {
                            text: runtimeTelemetryFresh()
                                  ? "Sidecar实时遥测：新鲜，且属于当前运行编号"
                                  : "Sidecar实时遥测：不可用或已过期"
                            color: runtimeTelemetryFresh() ? qgcPal.colorGreen : qgcPal.colorRed
                            font.bold: true
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel {
                            text: "地图轨迹：" + factoryFlyMap.taskPathStatusText()
                            color: runtimeTelemetryFresh() ? qgcPal.colorGreen : qgcPal.colorOrange
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel { text: "任务Adapter确认"; font.bold: true }
                        QGCLabel {
                            text: missionStatusText()
                            color: missionStatusColor()
                            font.bold: true
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel {
                            visible: currentProfile().manual_control !== true
                                     && missionStatus().adapter_id !== undefined
                            text: "Adapter：" + String(missionStatus().adapter_id || "-")
                                  + " · 状态：" + String(missionStatus().state || "-")
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        Repeater {
                            model: currentProfile().manual_control === true
                                   ? [] : (missionStatus().vehicles || [])
                            delegate: QGCLabel {
                                required property var modelData
                                text: String(modelData.vehicle_id || "未知飞机")
                                      + " ACK：" + root.missionAdapterVehicleText(modelData)
                                color: modelData.connected ? qgcPal.colorGreen : qgcPal.colorRed
                                wrapMode: Text.Wrap
                                Layout.fillWidth: true
                            }
                        }
                        QGCLabel {
                            visible: currentProfile().manual_control !== true
                                     && missionStatus().terminal === true
                                     && missionStatus().accepted !== true
                            text: "终态原因：" + String(missionStatus().reason_code || "未知")
                                  + (missionStatus().blockers && missionStatus().blockers.length
                                     ? " · " + missionStatus().blockers.join("；") : "")
                            color: qgcPal.colorRed
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel { text: "Sidecar逐机遥测"; font.bold: true }
                        Repeater {
                            model: root.runtimeVehicles()
                            delegate: ColumnLayout {
                                required property var modelData
                                Layout.fillWidth: true
                                spacing: 3
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 1
                                    color: qgcPal.button
                                }
                                QGCLabel {
                                    text: String(modelData.vehicle_id || "未知飞机") + "：" + root.runtimeVehicleStateText(modelData)
                                    color: root.runtimeVehicleStateColor(modelData)
                                    font.bold: true
                                    Layout.fillWidth: true
                                }
                                QGCLabel {
                                    text: root.runtimeVehiclePositionText(modelData)
                                    wrapMode: Text.Wrap
                                    Layout.fillWidth: true
                                }
                            }
                        }
                        QGCLabel {
                            visible: runtimeTelemetryFresh() && runtimeVehicles().length !== currentProfile().vehicle_count
                            text: "状态不完整：收到 " + runtimeVehicles().length + "/"
                                  + currentProfile().vehicle_count + " 架飞机遥测"
                            color: qgcPal.colorRed
                            font.bold: true
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel { text: "QGC活动飞机"; font.bold: true }
                        QGCLabel { text: "飞机数量：" + QGroundControl.multiVehicleManager.vehicles.count }
                        QGCLabel { text: "已解锁：" + (activeVehicle ? activeVehicle.armed : false) }
                        QGCLabel { text: "飞行模式：" + (activeVehicle ? activeVehicle.flightMode : "-") }
                        QGCLabel { text: "相对高度：" + (activeVehicle ? activeVehicle.altitudeRelative.valueString : "-") }
                        QGCLabel { text: "地速：" + (activeVehicle ? activeVehicle.groundSpeed.valueString : "-") }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton { text: "刷新运行状态"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.refreshState() }
                            QGCButton { text: "刷新遥测"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.refreshTelemetry() }
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: 10
                        QGCLabel { text: "目标无人机" }
                        ComboBox {
                            id: injectionVehicle
                            Layout.fillWidth: true
                            model: root.injectionVehicleIds()
                        }
                        QGCLabel { text: "风速（m/s）" }
                        Slider { id: windSlider; Layout.fillWidth: true; from: 0; to: 20; stepSize: 0.5 }
                        QGCLabel { text: windSlider.value.toFixed(1) }
                        QGCButton {
                            text: "暂存风扰"
                            Layout.fillWidth: true
                            enabled: faultStagingAllowed && injectionVehicle.currentText.length > 0
                            onClicked: mosimOrchestrator.stageWind(injectionVehicle.currentText, windSlider.value)
                        }
                        QGCLabel { text: "电机效率" }
                        RowLayout {
                            Layout.fillWidth: true
                            SpinBox { id: rotorIndex; from: 1; to: 4; value: 1 }
                            Slider { id: motorSlider; Layout.fillWidth: true; from: 0; to: 1; value: 1; stepSize: 0.05 }
                            QGCLabel { text: motorSlider.value.toFixed(2) }
                        }
                        QGCButton {
                            text: "暂存电机故障"
                            Layout.fillWidth: true
                            enabled: faultStagingAllowed && injectionVehicle.currentText.length > 0
                            onClicked: mosimOrchestrator.stageMotorEffectiveness(injectionVehicle.currentText,
                                                                                  rotorIndex.value, motorSlider.value)
                        }
                        QGCLabel { text: "待应用故障"; font.bold: true }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: pendingInjectionText()
                            color: pendingInjectionIsReady() ? qgcPal.colorOrange : qgcPal.text
                            wrapMode: Text.Wrap
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton {
                                text: "应用待应用故障"
                                Layout.fillWidth: true
                                enabled: faultApplyAllowed
                                onClicked: mosimOrchestrator.applyStagedInjection()
                            }
                            QGCButton {
                                text: "恢复正常"
                                Layout.fillWidth: true
                                enabled: faultRestoreAllowed && injectionVehicle.currentText.length > 0
                                onClicked: mosimOrchestrator.restoreNormal(injectionVehicle.currentText)
                            }
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        QGCCheckBox { id: pointCloudDisplay; text: "RViz点云地图"; checked: true }
                        QGCCheckBox { id: gridMapDisplay; text: "RViz栅格地图"; checked: true }
                        QGCCheckBox { id: unrealDisplay; text: "独立UE视图"; checked: true }
                        QGCCheckBox {
                            id: mworksDisplay
                            text: "MWORKS实时曲线（由Model Studio启动）"
                            enabled: false
                            checked: false
                        }
                        QGCButton {
                            text: "准备独立显示窗口"
                            Layout.fillWidth: true
                            enabled: !mosimOrchestrator.busy
                            onClicked: {
                                var selected = []
                                if (pointCloudDisplay.checked) selected.push("rviz_pointcloud")
                                if (gridMapDisplay.checked) selected.push("rviz_gridmap")
                                if (unrealDisplay.checked) selected.push("unreal")
                                if (mworksDisplay.checked) selected.push("mworks_result")
                                mosimOrchestrator.prepareDisplays(selected)
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton {
                                text: "打开所选窗口"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy && mosimOrchestrator.displaySessionId.length > 0
                                onClicked: mosimOrchestrator.attachDisplays()
                            }
                            QGCButton {
                                text: "关闭所选窗口"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy && mosimOrchestrator.displaySessionId.length > 0
                                onClicked: mosimOrchestrator.detachDisplays()
                            }
                        }
                        QGCButton {
                            text: "一键关闭全部RViz"
                            Layout.fillWidth: true
                            enabled: !mosimOrchestrator.busy && mosimOrchestrator.runId !== ""
                            onClicked: mosimOrchestrator.closeAllRviz()
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton {
                                text: "录制UE画面"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy && mosimOrchestrator.runId !== ""
                                         && !mosimOrchestrator.recordingActive
                                onClicked: mosimOrchestrator.startUeRecording()
                            }
                            QGCButton {
                                text: "停止UE录制"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy && mosimOrchestrator.recordingActive
                                onClicked: mosimOrchestrator.stopUeRecording()
                            }
                        }
                        QGCLabel {
                            text: mosimOrchestrator.recordingActive ? "正在录制" : "未录制"
                            color: mosimOrchestrator.recordingActive ? qgcPal.colorRed : qgcPal.text
                        }
                    }
                }

                ColumnLayout {
                    spacing: 10
                    QGCLabel { text: "Profile哈希"; font.bold: true }
                    QGCLabel { text: mosimOrchestrator.profileHash || "-"; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
                    QGCLabel { text: "控制器目录哈希"; font.bold: true }
                    QGCLabel { text: mosimOrchestrator.registryHash || "-"; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
                    RowLayout {
                        Layout.fillWidth: true
                        QGCButton { text: "请求Model Studio打开模型"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.openModelContext() }
                        QGCButton { text: "查看结果包"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.getResultPacket() }
                    }
                    TextArea {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        readOnly: true
                        wrapMode: TextEdit.WrapAnywhere
                        text: mosimOrchestrator.lastResponse
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: 8
                        QGCLabel {
                            text: "实验助手"
                            font.bold: true
                            Layout.fillWidth: true
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: assistantGreeting.implicitHeight + 18
                            radius: 6
                            color: qgcPal.windowShade
                            QGCLabel {
                                id: assistantGreeting
                                anchors.fill: parent
                                anchors.margins: 9
                                text: "你好，我可以根据自然语言匹配已登记的任务、控制器和无人机配置。"
                                wrapMode: Text.Wrap
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: exampleUserPrompt.implicitHeight + 18
                            radius: 6
                            color: "#31566b"
                            QGCLabel {
                                id: exampleUserPrompt
                                anchors.fill: parent
                                anchors.margins: 9
                                text: "运行FUEL单机自主探索，使用px4ctrl，按64 m边界执行。"
                                wrapMode: Text.Wrap
                                color: "white"
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: exampleAgentReply.implicitHeight + 18
                            radius: 6
                            color: qgcPal.windowShade
                            QGCLabel {
                                id: exampleAgentReply
                                anchors.fill: parent
                                anchors.margins: 9
                                text: "已匹配 FUEL 单机自主探索任务。控制器 px4ctrl，无人机 1 架；配置验证后由你确认启动。"
                                wrapMode: Text.Wrap
                            }
                        }
                        TextArea {
                            id: agentPrompt
                            Layout.fillWidth: true
                            Layout.preferredHeight: 82
                            placeholderText: "输入任务，例如：运行三机固定编队避障"
                            enabled: flightConfigurationEditable && !mosimOrchestrator.busy
                        }
                        QGCButton {
                            text: "生成受控任务建议"
                            Layout.fillWidth: true
                            enabled: agentPrompt.enabled && agentPrompt.text.trim().length > 0
                            onClicked: mosimOrchestrator.proposeOperatorTask(agentPrompt.text)
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            visible: agentProposalReady()
                            implicitHeight: agentProposalLabel.implicitHeight + 18
                            radius: 6
                            color: qgcPal.windowShade
                            QGCLabel {
                                id: agentProposalLabel
                                anchors.fill: parent
                                anchors.margins: 9
                                wrapMode: Text.Wrap
                                color: qgcPal.colorGreen
                                text: "已匹配：" + String(mosimOrchestrator.agentProposal.label || "-")
                                      + "\n控制器 " + String(mosimOrchestrator.agentProposal.controller_id || "-")
                                      + "，飞机 " + String(mosimOrchestrator.agentProposal.vehicle_count || "-") + " 架"
                            }
                        }
                        QGCButton {
                            text: "采用建议并验证配置"
                            Layout.fillWidth: true
                            visible: agentProposalReady()
                            enabled: visible && flightConfigurationEditable && !mosimOrchestrator.busy
                                     && profiles[profileIndex(String(mosimOrchestrator.agentProposal.profile_id || ""))].enabled
                            onClicked: confirmAgentProposal()
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: mosimOrchestrator
        function onResponseChanged() {
            if (!operatorProfileCatalogSynced && mosimOrchestrator.operatorProfiles.length > 0) {
                syncProfileSelection()
                operatorProfileCatalogSynced = true
            }
        }
    }
}
