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
    property var actualTracksByVehicle: ({})
    property int actualTrackRevision: 0
    property string actualTrackRunId: ""

    property var parentToolInsets
    property var totalToolInsets: toolInsets
    property var mapControl
    property bool controllerCatalogSynced: false
    property bool factoryMapExpanded: false
    property bool _showSingleVehicleUI: true
    readonly property var activeVehicle: QGroundControl.multiVehicleManager.activeVehicle

    readonly property bool manualTaskSelected: profiles[profileBox.currentIndex].manual === true
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
        var expected = profiles[profileBox.currentIndex].count
        if (manualTaskSelected)
            return qgcConnectedVehicleCount() === expected && qgcArmedVehicleCount() === 0
        return mosimOrchestrator.operationState === "completed"
                && mosimOrchestrator.operationStage === "Safe stop complete"
    }

    function flightPhaseText() {
        var profile = profiles[profileBox.currentIndex]
        var expected = profile.count
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
        if (profile.takeoff === "qgc") {
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
            "rviz_sessions_closed": "RViz窗口已关闭"
            ,"agent_proposal_ready": "任务建议已生成，等待人工确认"
            ,"agent_prompt_empty": "请输入任务需求"
            ,"agent_prompt_too_long": "任务描述过长，请简化后重试"
            ,"agent_intent_not_recognized": "未识别任务，请明确填写定点、8字、FUEL或三机编队"
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

    Connections {
        target: mosimOrchestrator
        function onResponseChanged() { root.captureRuntimeTelemetry() }
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
        if (profiles[profileBox.currentIndex].takeoff === "qgc")
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
        if (profiles[profileBox.currentIndex].takeoff === "qgc")
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

    function vehicleMapPositionValid(vehicle) {
        if (!vehicle || !vehicle.state || !vehicle.state.connected || !vehicle.state.position)
            return false
        var bounds = mosimOrchestrator.operatorMap.world_bounds_m || ({})
        var x = Number(vehicle.state.position.x)
        var y = Number(vehicle.state.position.y)
        return isFinite(x) && isFinite(y)
                && x >= Number(bounds.min_x_m || 0) && x <= Number(bounds.max_x_m || 0)
                && y >= Number(bounds.min_y_m || 0) && y <= Number(bounds.max_y_m || 0)
    }

    function vehicleYawDegrees(vehicle) {
        if (!vehicle || !vehicle.state || !vehicle.state.orientation)
            return 0
        var q = vehicle.state.orientation
        var yaw = Math.atan2(2.0 * (Number(q.w) * Number(q.z) + Number(q.x) * Number(q.y)),
                             1.0 - 2.0 * (Number(q.y) * Number(q.y) + Number(q.z) * Number(q.z)))
        return yaw * 180.0 / Math.PI
    }

    function mapPixelX(worldX, imageX, imageWidth) {
        var bounds = mosimOrchestrator.operatorMap.world_bounds_m
        return imageX + (worldX - Number(bounds.min_x_m))
                / (Number(bounds.max_x_m) - Number(bounds.min_x_m)) * imageWidth
    }

    function mapPixelY(worldY, imageY, imageHeight) {
        var bounds = mosimOrchestrator.operatorMap.world_bounds_m
        return imageY + (Number(bounds.max_y_m) - worldY)
                / (Number(bounds.max_y_m) - Number(bounds.min_y_m)) * imageHeight
    }

    function explorationBoundary() {
        var manifest = mosimOrchestrator.runManifest || ({})
        if (manifest.run_id !== mosimOrchestrator.runId
                || manifest.experiment_profile_id !== profiles[profileBox.currentIndex].id)
            return null
        var scenario = manifest.scenario_snapshot || ({})
        var boundary = scenario.exploration_boundary || null
        if (!boundary)
            return null
        var minX = Number(boundary.min_x_m)
        var maxX = Number(boundary.max_x_m)
        var minY = Number(boundary.min_y_m)
        var maxY = Number(boundary.max_y_m)
        if (!isFinite(minX) || !isFinite(maxX) || !isFinite(minY) || !isFinite(maxY)
                || minX >= maxX || minY >= maxY)
            return null
        return { min_x_m: minX, max_x_m: maxX, min_y_m: minY, max_y_m: maxY }
    }

    function paintExplorationBoundary(canvas, imageX, imageY, imageWidth, imageHeight) {
        var context = canvas.getContext("2d")
        context.reset()
        var boundary = explorationBoundary()
        if (!boundary)
            return
        var left = mapPixelX(boundary.min_x_m, imageX, imageWidth)
        var right = mapPixelX(boundary.max_x_m, imageX, imageWidth)
        var top = mapPixelY(boundary.max_y_m, imageY, imageHeight)
        var bottom = mapPixelY(boundary.min_y_m, imageY, imageHeight)
        context.strokeStyle = "#20c7b7"
        context.lineWidth = 3
        context.strokeRect(left, top, right - left, bottom - top)
    }

    function formationTarget() {
        var manifest = mosimOrchestrator.runManifest || ({})
        if (manifest.run_id !== mosimOrchestrator.runId
                || manifest.experiment_profile_id !== profiles[profileBox.currentIndex].id)
            return null
        var scenario = manifest.scenario_snapshot || ({})
        var formation = scenario.formation || null
        var target = formation ? formation.target_center_xy_m : null
        if (!target || target.length !== 2)
            return null
        var x = Number(target[0])
        var y = Number(target[1])
        if (!isFinite(x) || !isFinite(y))
            return null
        return { x: x, y: y }
    }

    function paintFormationTarget(canvas, imageX, imageY, imageWidth, imageHeight) {
        var context = canvas.getContext("2d")
        context.reset()
        var target = formationTarget()
        if (!target)
            return
        var x = mapPixelX(target.x, imageX, imageWidth)
        var y = mapPixelY(target.y, imageY, imageHeight)
        var radius = Math.max(6, Math.min(12, imageWidth / 45))
        context.beginPath()
        context.arc(x, y, radius, 0, Math.PI * 2)
        context.strokeStyle = "#f05d9b"
        context.lineWidth = 3
        context.stroke()
        context.beginPath()
        context.moveTo(x - radius - 4, y)
        context.lineTo(x + radius + 4, y)
        context.moveTo(x, y - radius - 4)
        context.lineTo(x, y + radius + 4)
        context.stroke()
    }

    function frozenScenarioSummary() {
        var manifest = mosimOrchestrator.runManifest || ({})
        if (manifest.run_id !== mosimOrchestrator.runId || !manifest.scenario_snapshot)
            return "任务参数尚未冻结"
        var scenario = manifest.scenario_snapshot
        var mission = scenario.mission || ({})
        var boundary = scenario.exploration_boundary || null
        if (boundary) {
            return "已冻结：边界 X[" + Number(boundary.min_x_m).toFixed(2) + ", "
                    + Number(boundary.max_x_m).toFixed(2) + "] m，Y["
                    + Number(boundary.min_y_m).toFixed(2) + ", "
                    + Number(boundary.max_y_m).toFixed(2) + "] m；时长 "
                    + Number(mission.duration_s || 0).toFixed(0) + " s；种子 "
                    + String(mission.random_seed === undefined ? "-" : mission.random_seed)
                    + "；最大速度 " + Number(mission.max_velocity_mps || 0).toFixed(1) + " m/s"
        }
        var formation = scenario.formation || null
        if (formation) {
            var target = formation.target_center_xy_m || []
            return "已冻结：三机编队；目标中心 (" + Number(target[0]).toFixed(2) + ", "
                    + Number(target[1]).toFixed(2) + ") m；最小机间距 "
                    + Number(formation.expected_min_pair_distance_m || 0).toFixed(2) + " m"
        }
        return "已冻结场景；场景哈希 " + String(manifest.scenario_hash || "-").slice(0, 12)
    }

    function captureRuntimeTelemetry() {
        var telemetry = mosimOrchestrator.runtimeTelemetry || ({})
        if (!runtimeTelemetryFresh())
            return
        if (actualTrackRunId !== telemetry.run_id) {
            actualTracksByVehicle = ({})
            actualTrackRevision += 1
            actualTrackRunId = telemetry.run_id
        }
        var nextTracks = actualTracksByVehicle
        var vehicles = runtimeVehicles()
        var changed = false
        for (var index = 0; index < vehicles.length; ++index) {
            var vehicle = vehicles[index]
            if (!vehicleMapPositionValid(vehicle))
                continue
            var id = String(vehicle.vehicle_id || ("uav" + (index + 1)))
            var points = nextTracks[id] || []
            var point = { x: Number(vehicle.state.position.x), y: Number(vehicle.state.position.y) }
            var previous = points.length > 0 ? points[points.length - 1] : null
            if (!previous || Math.hypot(point.x - previous.x, point.y - previous.y) >= 0.05) {
                points = points.slice(Math.max(0, points.length - 1198))
                points.push(point)
                nextTracks[id] = points
                changed = true
            }
        }
        if (changed) {
            actualTracksByVehicle = nextTracks
            actualTrackRevision += 1
        }
    }

    function paintActualTracks(canvas, imageX, imageY, imageWidth, imageHeight) {
        var revision = actualTrackRevision
        var context = canvas.getContext("2d")
        context.reset()
        context.lineWidth = 2
        context.lineJoin = "round"
        context.lineCap = "round"
        var colors = ["#00d084", "#ffb020", "#4aa3ff", "#f05d9b", "#9b7cff", "#21c7d9", "#ffffff", "#ff7043", "#8bc34a"]
        var ids = Object.keys(actualTracksByVehicle).sort()
        for (var idIndex = 0; idIndex < ids.length; ++idIndex) {
            var points = actualTracksByVehicle[ids[idIndex]]
            if (!points || points.length < 2)
                continue
            context.beginPath()
            context.strokeStyle = colors[idIndex % colors.length]
            context.moveTo(mapPixelX(points[0].x, imageX, imageWidth), mapPixelY(points[0].y, imageY, imageHeight))
            for (var pointIndex = 1; pointIndex < points.length; ++pointIndex)
                context.lineTo(mapPixelX(points[pointIndex].x, imageX, imageWidth), mapPixelY(points[pointIndex].y, imageY, imageHeight))
            context.stroke()
        }
    }

    function taskPath(kind) {
        if (!runtimeTelemetryFresh())
            return ({})
        var paths = mosimOrchestrator.runtimeTelemetry.task_paths || ({})
        var path = paths[kind] || ({})
        if (path.status !== "available" || !path.points || path.points.length < 2)
            return ({})
        if (kind === "future" && Date.now() / 1000.0 - Number(path.updated_at || 0) > 5.0)
            return ({})
        return path
    }

    function taskPathLabel(kind) {
        var path = taskPath(kind)
        var semantics = String(path.semantics || "")
        if (semantics === "formation_center_reference")
            return "编队中心预期"
        if (semantics === "exploration_target_sequence")
            return "探索目标序列"
        if (semantics === "planner_sampled_future_trajectory")
            return "规划器未来轨迹"
        return kind === "future" ? "未来轨迹" : "任务预期轨迹"
    }

    function taskPathStatusText() {
        var expected = taskPath("expected")
        var future = taskPath("future")
        var labels = []
        if (expected.status === "available")
            labels.push(taskPathLabel("expected") + "已接收")
        if (future.status === "available")
            labels.push(taskPathLabel("future") + "已接收")
        if (actualTrackRevision > 0)
            labels.push("实际轨迹实时记录中")
        return labels.length > 0 ? labels.join("；") : "等待任务轨迹与飞机位置"
    }

    function paintTaskPaths(canvas, imageX, imageY, imageWidth, imageHeight) {
        var context = canvas.getContext("2d")
        context.reset()
        var kinds = ["expected", "future"]
        var colors = ["#ffb020", "#4aa3ff"]
        for (var kindIndex = 0; kindIndex < kinds.length; ++kindIndex) {
            var path = taskPath(kinds[kindIndex])
            var points = path.points || []
            if (points.length < 2)
                continue
            context.beginPath()
            context.strokeStyle = colors[kindIndex]
            context.lineWidth = kinds[kindIndex] === "future" ? 3 : 2
            context.lineJoin = "round"
            context.lineCap = "round"
            context.moveTo(mapPixelX(Number(points[0].x), imageX, imageWidth),
                           mapPixelY(Number(points[0].y), imageY, imageHeight))
            for (var pointIndex = 1; pointIndex < points.length; ++pointIndex)
                context.lineTo(mapPixelX(Number(points[pointIndex].x), imageX, imageWidth),
                               mapPixelY(Number(points[pointIndex].y), imageY, imageHeight))
            context.stroke()
        }
    }

    function vehicleColor(index) {
        var colors = ["#00d084", "#ffb020", "#4aa3ff", "#f05d9b", "#9b7cff", "#21c7d9", "#ffffff", "#ff7043", "#8bc34a"]
        return colors[index % colors.length]
    }

    function syncUnrealOverlayHole() {
        if (!mosimOrchestrator.unrealWindow)
            return

        mosimOrchestrator.setUnrealOverlayHole(
            factoryMapPreview.x,
            factoryMapPreview.y,
            factoryMapPreview.width,
            factoryMapPreview.height,
            unrealViewport.width,
            unrealViewport.height,
            factoryMapPreview.visible)
    }

    onFactoryMapExpandedChanged: Qt.callLater(syncUnrealOverlayHole)

    Connections {
        target: mainWindow
        function onMosimNativeOverlayVisibleChanged() {
            mosimOrchestrator.setUnrealPresentationSuppressed(mainWindow.mosimNativeOverlayVisible)
        }
    }

    QGCPalette { id: qgcPal; colorGroupEnabled: true }

    // The custom Flight Console owns the visual surface. Preserve the native
    // QGC map object and restore it when this layer is unloaded, but do not let
    // its online tiles bleed through the UE/factory display.
    Component.onCompleted: {
        forceActiveFocus()
        if (mapControl)
            mapControl.visible = false
    }
    Component.onDestruction: {
        mosimOrchestrator.setManualControlEnabled(false)
        mosimOrchestrator.setUnrealOverlayHole(0, 0, 0, 0, 0, 0, false)
        if (mapControl)
            mapControl.visible = true
    }

    readonly property var profiles: [
        { id: "px4ctrl_ground_standby_v1", label: "单机定点操纵", path: "Config/profiles/experiments/px4ctrl_ground_standby_v1.json", controller: "px4ctrl", count: 1, enabled: true, manual: true, takeoff: "qgc", disabledReason: "" },
        { id: "px4ctrl_figure8_baseline_v1", label: "单机8字飞行", path: "Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json", controller: "px4ctrl", count: 1, enabled: true, manual: false, takeoff: "automatic", disabledReason: "" },
        { id: "cascade_pid_figure8_generated_c_v1", label: "生成代码控制器8字飞行", path: "Config/profiles/experiments/cascade_pid_figure8_generated_c_v1.json", controller: "cascade_pid", count: 1, enabled: true, manual: false, takeoff: "automatic", disabledReason: "" },
        { id: "factory_l2_fuel_fixed64_exploration_v1", label: "FUEL单机自主探索", path: "Config/profiles/experiments/factory_l2_fuel_fixed64_exploration_v1.json", controller: "px4ctrl", count: 1, enabled: true, manual: false, takeoff: "automatic", disabledReason: "" },
        { id: "factory_l2_three_uav_swarm_formation_v1", label: "三机固定编队避障", path: "Config/profiles/experiments/factory_l2_three_uav_swarm_formation_v1.json", controller: "px4ctrl", count: 3, enabled: true, manual: false, takeoff: "automatic", disabledReason: "" },
        { id: "mworks_live_official_pid_hover_50hz_v2", label: "MWORKS实时联合仿真（50 Hz）", path: "Config/profiles/experiments/mworks_live_official_pid_hover_50hz_v2.json", controller: "official_pid", count: 1, enabled: false, manual: false, takeoff: "automatic", disabledReason: "实时数据展示已具备，在线控制接管仍待运行验收" },
        { id: "mworks_live_official_pid_hover_200hz_v1", label: "MWORKS实时联合仿真（200 Hz）", path: "Config/profiles/experiments/mworks_live_official_pid_hover_200hz_v1.json", controller: "official_pid", count: 1, enabled: false, manual: false, takeoff: "automatic", disabledReason: "比赛版冻结为候选能力，不作为录制主线" }
    ]
    readonly property var vehicleCounts: [
        { label: "1", value: 1, enabled: true },
        { label: "3", value: 3, enabled: true },
        { label: "4（规模验收未完成）", value: 4, enabled: false },
        { label: "5（规模验收未完成）", value: 5, enabled: false },
        { label: "6（规模验收未完成）", value: 6, enabled: false },
        { label: "7（规模验收未完成）", value: 7, enabled: false },
        { label: "8（规模验收未完成）", value: 8, enabled: false },
        { label: "9（规模验收未完成）", value: 9, enabled: false }
    ]

    function controllerIndex(moduleId) {
        for (var index = 0; index < mosimOrchestrator.controllers.length; ++index) {
            if (mosimOrchestrator.controllers[index].module_id === moduleId)
                return index
        }
        return -1
    }

    function controllerCompatibleWithTask(moduleId) {
        return String(moduleId || "") === String(profiles[profileBox.currentIndex].controller)
    }

    function vehicleCountCompatibleWithTask(vehicleCount) {
        return Number(vehicleCount) === Number(profiles[profileBox.currentIndex].count)
    }

    function taskSelectionCompatible() {
        return controllerCompatibleWithTask(controllerBox.currentValue)
                && vehicleCountCompatibleWithTask(vehicleCounts[vehicleBox.currentIndex].value)
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
        return proposal.requires_user_confirmation === true
                && proposal.may_start_flight === false
                && profileIndex(String(proposal.profile_id || "")) >= 0
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
        mosimOrchestrator.prepareRun(String(proposal.profile_path), String(proposal.controller_id),
                                     Number(proposal.vehicle_count), 0,
                                     proposal.manual_control === true)
    }

    function syncProfileSelection() {
        var profile = profiles[profileBox.currentIndex]
        var index = controllerIndex(profile.controller)
        if (index >= 0)
            controllerBox.currentIndex = index
        vehicleBox.currentIndex = profile.count === 3 ? 1 : 0
        injectionVehicle.currentIndex = 0
        manualModeCheck.checked = false
    }

    function taskGuideText() {
        var profile = profiles[profileBox.currentIndex]
        if (!profile.enabled)
            return "当前不可启动：" + profile.disabledReason
        if (profile.takeoff === "qgc")
            return "操作顺序：启动并等待连接 → 使用QGC原生解锁/起飞 → 切换Position模式 → 点击键盘控制区后使用W/A/S/D → 使用QGC原生降落。"
        return "操作顺序：验证配置 → 启动任务。Orchestrator将自动完成连接、解锁、起飞、任务执行和降落；全过程必须在QGC确认阶段、告警和结束状态。"
    }

    function flightAuthorityText() {
        var profile = profiles[profileBox.currentIndex]
        if (!profile.enabled)
            return "未授权：当前Profile尚未通过运行门禁"
        if (profile.takeoff === "qgc")
            return "QGC原生控制：你负责解锁、起飞、Position模式操纵和降落"
        if (profile.count > 1)
            return "编队Mission Adapter独占控制：自动逐机解锁、起飞、编队任务和降落"
        return "任务Mission Adapter独占控制：自动解锁、起飞、任务执行和降落"
    }

    function selectionMatchesPreparedRun() {
        if (mosimOrchestrator.runId === "")
            return false
        return mosimOrchestrator.experimentProfileId === profiles[profileBox.currentIndex].id
                && mosimOrchestrator.selectedControllerId === controllerBox.currentValue
                && mosimOrchestrator.selectedVehicleCount === vehicleCounts[vehicleBox.currentIndex].value
    }

    function nextOperatorStepText() {
        var profile = profiles[profileBox.currentIndex]
        if (!profile.enabled)
            return "当前任务尚未通过运行门禁，不能启动。"
        if (mosimOrchestrator.busy)
            return "正在处理请求，请勿重复点击。"
        if (mosimOrchestrator.lifecycleState === "starting")
            return "正在启动 Gazebo、PX4、MAVROS 和任务节点，请等待连接完成。"
        if (mosimOrchestrator.lifecycleState === "running" && !selectionMatchesPreparedRun())
            return "另一个任务仍在运行：先确认飞机已降落且未解锁，再点击“停止当前仿真”，然后验证所选任务。"
        if (mosimOrchestrator.lifecycleState === "running" && selectionMatchesPreparedRun()) {
            if (profile.takeoff !== "qgc")
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
        return "先选择任务和控制器，然后点击“验证配置”。"
    }

    function operatorChecklist() {
        var profile = profiles[profileBox.currentIndex]
        var selected = selectionMatchesPreparedRun()
        var running = mosimOrchestrator.lifecycleState === "starting"
                || mosimOrchestrator.lifecycleState === "running"
        var connected = qgcConnectedVehicleCount() >= profile.count
        var armed = qgcArmedVehicleCount() >= profile.count
        var manualAirborne = profile.takeoff === "qgc" && activeVehicle
                && activeVehicle.initialConnectComplete && activeVehicle.armed && activeVehicle.flying
        var manualExecuting = manualAirborne && activeVehicle.flightMode === "Position"
        var mission = missionStatus()
        var missionPhase = String(mission.phase || "")
        var automaticExecuting = profile.takeoff !== "qgc"
                && mission.transport_state !== "unavailable"
                && mission.transport_state !== "stale"
                && !mission.terminal
                && ["hover_before", "figure8", "ego_triggered", "ego_execute",
                    "exploration_execute", "safe_stop_hover", "land"].indexOf(missionPhase) >= 0
        var missionFailed = profile.takeoff !== "qgc" && mission.terminal === true
                && mission.accepted !== true
        var landed = profile.takeoff === "qgc"
                ? observedArmedDuringRun && connected && qgcArmedVehicleCount() === 0
                : mission.terminal === true && mission.accepted === true && qgcArmedVehicleCount() === 0
        var takeoffComplete = profile.takeoff === "qgc"
                ? manualAirborne || landed
                : observedArmedDuringRun || automaticExecuting || mission.terminal === true
        var executionState = profile.takeoff === "qgc"
                ? (landed ? "已完成" : (manualExecuting ? "当前" : "等待"))
                : (missionFailed ? "失败"
                                 : (mission.terminal === true ? "已完成"
                                                              : (automaticExecuting ? "当前" : "等待")))
        var landingActive = profile.takeoff === "qgc"
                ? activeVehicle && activeVehicle.landing
                : ["safe_stop_hover", "land"].indexOf(missionPhase) >= 0
        return [
            { label: "1. 配置冻结", state: selected ? "已完成" : "当前" },
            { label: "2. 运行时与飞机连接", state: connected ? "已完成" : (running ? "当前" : "等待") },
            { label: profile.takeoff === "qgc" ? "3. QGC原生解锁与起飞" : "3. Adapter自动解锁与起飞",
              state: takeoffComplete ? "已完成" : (connected ? "当前" : "等待") },
            { label: profile.takeoff === "qgc" ? "4. Position / W/A/S/D" : "4. 自主任务执行",
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

    Rectangle {
        id: unrealViewport
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: consolePanel.left
        anchors.bottom: parent.bottom
        color: "#111315"
        // This is the display surface for the embedded UE window. It must sit
        // above QGC's native map; otherwise an unattached UE window exposes the
        // online satellite map behind the Factory thumbnail.
        z: 0

        WindowContainer {
            id: unrealWindowContainer
            anchors.fill: parent
            window: mosimOrchestrator.unrealWindow
            // Keep the native host mounted even while a QGC drawer is open.
            // Toggling WindowContainer.visible can release the foreign HWND
            // during startup and leave UE as a standalone top-level window.
            visible: window !== null
            onWindowChanged: {
                if (window !== null) {
                    mosimOrchestrator.setUnrealPresentationSuppressed(mainWindow.mosimNativeOverlayVisible)
                    Qt.callLater(mosimOrchestrator.confirmUnrealContainerReady)
                }
            }
        }

        MouseArea {
            id: unrealOrbitArea
            anchors.fill: parent
            z: 2
            enabled: mosimOrchestrator.unrealWindow !== null
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            cursorShape: pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor
            preventStealing: true
            focus: true
            property real previousX: 0
            property real previousY: 0

            Component.onCompleted: forceActiveFocus()

            onPressed: function(mouse) {
                forceActiveFocus()
                previousX = mouse.x
                previousY = mouse.y
            }
            onPositionChanged: function(mouse) {
                if (!pressed) {
                    return
                }
                mosimOrchestrator.orbitUnreal(mouse.x - previousX, mouse.y - previousY)
                previousX = mouse.x
                previousY = mouse.y
            }
        }

        MouseArea {
            anchors.fill: parent
            z: 3
            enabled: factoryMapExpanded
            acceptedButtons: Qt.LeftButton
            onClicked: factoryMapExpanded = false
        }

        Rectangle {
            id: factoryMapPreview
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.margins: 12
            width: factoryMapExpanded ? Math.min(parent.width - 48, 960) : Math.min(parent.width * 0.32, 360)
            height: factoryMapExpanded ? Math.min(parent.height - 48, 560) : width * 800 / 2048
            color: "#10151a"
            border.color: "#d7e0e5"
            border.width: 1
            z: 4

            onXChanged: Qt.callLater(root.syncUnrealOverlayHole)
            onYChanged: Qt.callLater(root.syncUnrealOverlayHole)
            onWidthChanged: Qt.callLater(root.syncUnrealOverlayHole)
            onHeightChanged: Qt.callLater(root.syncUnrealOverlayHole)
            onVisibleChanged: Qt.callLater(root.syncUnrealOverlayHole)

            Behavior on width { NumberAnimation { duration: 140 } }
            Behavior on height { NumberAnimation { duration: 140 } }

            Image {
                id: factoryMapThumbnail
                anchors.fill: parent
                anchors.margins: 2
                visible: !factoryMapExpanded
                source: "qrc:/Custom/maps/factory_l2/v1/floorplan.png"
                fillMode: Image.PreserveAspectFit
                asynchronous: true
                cache: true
            }

            Canvas {
                id: factoryExplorationBoundaryPreview
                anchors.fill: parent
                anchors.margins: 2
                visible: !factoryMapExpanded && root.explorationBoundary() !== null
                z: 1
                property string scenarioHash: String(mosimOrchestrator.runManifest.scenario_hash || "")
                onScenarioHashChanged: requestPaint()
                onPaint: root.paintExplorationBoundary(this, 0, 0, width, height)
            }

            Canvas {
                id: factoryTaskPathPreview
                anchors.fill: parent
                anchors.margins: 2
                visible: !factoryMapExpanded && root.runtimeTelemetryFresh()
                z: 2
                property real telemetryTimestamp: Number(mosimOrchestrator.runtimeTelemetry.timestamp || 0)
                onTelemetryTimestampChanged: requestPaint()
                onPaint: root.paintTaskPaths(this, 0, 0, width, height)
            }

            Canvas {
                id: factoryFormationTargetPreview
                anchors.fill: parent
                anchors.margins: 2
                visible: !factoryMapExpanded && root.formationTarget() !== null
                z: 3
                property string scenarioHash: String(mosimOrchestrator.runManifest.scenario_hash || "")
                onScenarioHashChanged: requestPaint()
                onPaint: root.paintFormationTarget(this, 0, 0, width, height)
            }

            Canvas {
                id: factoryActualTrackPreview
                anchors.fill: parent
                anchors.margins: 2
                visible: !factoryMapExpanded && root.runtimeTelemetryFresh()
                z: 4
                property int trackRevision: root.actualTrackRevision
                onTrackRevisionChanged: requestPaint()
                onPaint: root.paintActualTracks(this, 0, 0, width, height)
            }

            Repeater {
                model: !factoryMapExpanded ? root.runtimeVehicles() : []
                delegate: Item {
                    required property var modelData
                    required property int index
                    property var vehicle: modelData
                    visible: root.vehicleMapPositionValid(vehicle)
                    width: 18
                    height: 18
                    z: 5
                    rotation: 90 - root.vehicleYawDegrees(vehicle)
                    x: root.mapPixelX(Number(vehicle.state.position.x), 2, factoryMapPreview.width - 4) - width / 2
                    y: root.mapPixelY(Number(vehicle.state.position.y), 2, factoryMapPreview.height - 4) - height / 2

                    Canvas {
                        anchors.fill: parent
                        onPaint: {
                            var context = getContext("2d")
                            context.reset()
                            context.beginPath()
                            context.moveTo(width, height / 2)
                            context.lineTo(2, 2)
                            context.lineTo(5, height / 2)
                            context.lineTo(2, height - 2)
                            context.closePath()
                            context.fillStyle = root.vehicleColor(index)
                            context.fill()
                            context.strokeStyle = "white"
                            context.lineWidth = 1.5
                            context.stroke()
                        }
                    }
                }
            }

            Loader {
                id: factoryMapLoader
                anchors.fill: parent
                anchors.topMargin: 38
                anchors.margins: 2
                visible: factoryMapExpanded
                active: factoryMapExpanded

                sourceComponent: Rectangle {
                    id: factoryMapCanvas
                    clip: true
                    color: "#10151a"
                    property real zoomFactor: 1.0

                    function zoomAt(viewX, viewY, wheelDelta) {
                        var oldZoom = zoomFactor
                        var nextZoom = Math.max(1.0, Math.min(8.0,
                            oldZoom * (wheelDelta > 0 ? 1.2 : 1 / 1.2)))
                        if (Math.abs(nextZoom - oldZoom) < 0.0001)
                            return

                        var imageX = factoryMapFlickable.contentX + viewX - factoryMapImage.x
                        var imageY = factoryMapFlickable.contentY + viewY - factoryMapImage.y
                        var imageRatioX = Math.max(0.0, Math.min(1.0, imageX / factoryMapImage.width))
                        var imageRatioY = Math.max(0.0, Math.min(1.0, imageY / factoryMapImage.height))
                        zoomFactor = nextZoom
                        Qt.callLater(function() {
                            var targetX = factoryMapImage.x + imageRatioX * factoryMapImage.width - viewX
                            var targetY = factoryMapImage.y + imageRatioY * factoryMapImage.height - viewY
                            factoryMapFlickable.contentX = Math.max(0,
                                Math.min(targetX, factoryMapFlickable.contentWidth - factoryMapFlickable.width))
                            factoryMapFlickable.contentY = Math.max(0,
                                Math.min(targetY, factoryMapFlickable.contentHeight - factoryMapFlickable.height))
                        })
                    }

                    Flickable {
                        id: factoryMapFlickable
                        anchors.fill: parent
                        clip: true
                        boundsBehavior: Flickable.StopAtBounds
                        contentWidth: Math.max(width, factoryMapSurface.width)
                        contentHeight: Math.max(height, factoryMapSurface.height)

                        Item {
                            id: factoryMapSurface
                            width: Math.max(factoryMapFlickable.width,
                                            factoryMapImage.width)
                            height: Math.max(factoryMapFlickable.height,
                                             factoryMapImage.height)

                            Image {
                                id: factoryMapImage
                                readonly property real fittedWidth: Math.min(
                                    factoryMapFlickable.width,
                                    factoryMapFlickable.height * 2048 / 800)
                                width: fittedWidth * factoryMapCanvas.zoomFactor
                                height: width * 800 / 2048
                                anchors.centerIn: parent
                                source: "qrc:/Custom/maps/factory_l2/v1/floorplan.png"
                                fillMode: Image.Stretch
                                smooth: true
                                mipmap: true
                                cache: true
                            }

                            Canvas {
                                id: factoryExplorationBoundaryExpanded
                                x: factoryMapImage.x
                                y: factoryMapImage.y
                                width: factoryMapImage.width
                                height: factoryMapImage.height
                                visible: root.explorationBoundary() !== null
                                z: 1
                                property string scenarioHash: String(mosimOrchestrator.runManifest.scenario_hash || "")
                                onScenarioHashChanged: requestPaint()
                                onWidthChanged: requestPaint()
                                onHeightChanged: requestPaint()
                                onPaint: root.paintExplorationBoundary(this, 0, 0, width, height)
                            }

                            Canvas {
                                id: factoryTaskPathExpanded
                                x: factoryMapImage.x
                                y: factoryMapImage.y
                                width: factoryMapImage.width
                                height: factoryMapImage.height
                                visible: root.runtimeTelemetryFresh()
                                z: 2
                                property real telemetryTimestamp: Number(mosimOrchestrator.runtimeTelemetry.timestamp || 0)
                                onTelemetryTimestampChanged: requestPaint()
                                onWidthChanged: requestPaint()
                                onHeightChanged: requestPaint()
                                onPaint: root.paintTaskPaths(this, 0, 0, width, height)
                            }

                            Canvas {
                                id: factoryFormationTargetExpanded
                                x: factoryMapImage.x
                                y: factoryMapImage.y
                                width: factoryMapImage.width
                                height: factoryMapImage.height
                                visible: root.formationTarget() !== null
                                z: 3
                                property string scenarioHash: String(mosimOrchestrator.runManifest.scenario_hash || "")
                                onScenarioHashChanged: requestPaint()
                                onWidthChanged: requestPaint()
                                onHeightChanged: requestPaint()
                                onPaint: root.paintFormationTarget(this, 0, 0, width, height)
                            }

                            Canvas {
                                id: factoryActualTrackExpanded
                                x: factoryMapImage.x
                                y: factoryMapImage.y
                                width: factoryMapImage.width
                                height: factoryMapImage.height
                                visible: root.runtimeTelemetryFresh()
                                z: 4
                                property int trackRevision: root.actualTrackRevision
                                onTrackRevisionChanged: requestPaint()
                                onWidthChanged: requestPaint()
                                onHeightChanged: requestPaint()
                                onPaint: root.paintActualTracks(this, 0, 0, width, height)
                            }

                            Repeater {
                                model: root.runtimeVehicles()
                                delegate: Item {
                                    required property var modelData
                                    required property int index
                                    property var vehicle: modelData
                                    visible: root.vehicleMapPositionValid(vehicle)
                                    width: 20
                                    height: 20
                                    z: 4
                                    rotation: 90 - root.vehicleYawDegrees(vehicle)
                                    x: root.mapPixelX(Number(vehicle.state.position.x), factoryMapImage.x, factoryMapImage.width) - width / 2
                                    y: root.mapPixelY(Number(vehicle.state.position.y), factoryMapImage.y, factoryMapImage.height) - height / 2

                                    Canvas {
                                        anchors.fill: parent
                                        onPaint: {
                                            var context = getContext("2d")
                                            context.reset()
                                            context.beginPath()
                                            context.moveTo(width, height / 2)
                                            context.lineTo(2, 2)
                                            context.lineTo(5, height / 2)
                                            context.lineTo(2, height - 2)
                                            context.closePath()
                                            context.fillStyle = root.vehicleColor(index)
                                            context.fill()
                                            context.strokeStyle = "white"
                                            context.lineWidth = 1.5
                                            context.stroke()
                                        }
                                    }
                                }
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.NoButton
                            hoverEnabled: true
                            onWheel: function(wheel) {
                                factoryMapCanvas.zoomAt(wheel.x, wheel.y, wheel.angleDelta.y)
                                wheel.accepted = true
                            }
                        }
                    }
                }
            }

            MouseArea {
                anchors.fill: parent
                enabled: !factoryMapExpanded
                cursorShape: Qt.PointingHandCursor
                onClicked: factoryMapExpanded = true
            }

            Row {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 5
                spacing: 4
                visible: factoryMapExpanded
                z: 2

                QGCButton {
                    text: "X"
                    width: 38
                    height: 28
                    onClicked: factoryMapExpanded = false
                }
            }

            Row {
                anchors.left: parent.left
                anchors.bottom: parent.bottom
                anchors.margins: 6
                spacing: 10
                visible: root.runtimeTelemetryFresh()
                z: 5

                Repeater {
                    model: [
                        { label: "实际", color: "#00d084", visible: Object.keys(root.actualTracksByVehicle).length > 0 },
                        { label: root.taskPathLabel("expected"), color: "#ffb020", visible: root.taskPath("expected").status === "available" },
                        { label: root.taskPathLabel("future"), color: "#4aa3ff", visible: root.taskPath("future").status === "available" },
                        { label: "编队目标", color: "#f05d9b", visible: root.formationTarget() !== null }
                    ]
                    delegate: Row {
                        required property var modelData
                        visible: modelData.visible
                        spacing: 4
                        Rectangle { width: 14; height: 3; anchors.verticalCenter: parent.verticalCenter; color: modelData.color }
                        Text { text: modelData.label; color: "white"; font.pixelSize: 12 }
                    }
                }
            }
        }

        FlyViewBottomRightRowLayout {
            id: unrealTelemetryHud
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: ScreenTools.defaultFontPixelWidth * 0.75
            spacing: ScreenTools.defaultFontPixelWidth
            visible: activeVehicle !== null && !factoryMapExpanded
            z: 5
        }

        Shortcut {
            sequence: "N"
            enabled: mosimOrchestrator.unrealWindow !== null
            onActivated: mosimOrchestrator.zoomUnrealIn()
        }

        Shortcut {
            sequence: "M"
            enabled: mosimOrchestrator.unrealWindow !== null
            onActivated: mosimOrchestrator.zoomUnrealOut()
        }

        Shortcut {
            sequence: "Left"
            context: Qt.ApplicationShortcut
            autoRepeat: true
            enabled: mosimOrchestrator.unrealWindow !== null && !factoryMapExpanded
            onActivated: mosimOrchestrator.orbitUnreal(-4, 0)
        }

        Shortcut {
            sequence: "Right"
            context: Qt.ApplicationShortcut
            autoRepeat: true
            enabled: mosimOrchestrator.unrealWindow !== null && !factoryMapExpanded
            onActivated: mosimOrchestrator.orbitUnreal(4, 0)
        }

        Shortcut {
            sequence: "Up"
            context: Qt.ApplicationShortcut
            autoRepeat: true
            enabled: mosimOrchestrator.unrealWindow !== null && !factoryMapExpanded
            onActivated: mosimOrchestrator.orbitUnreal(0, -4)
        }

        Shortcut {
            sequence: "Down"
            context: Qt.ApplicationShortcut
            autoRepeat: true
            enabled: mosimOrchestrator.unrealWindow !== null && !factoryMapExpanded
            onActivated: mosimOrchestrator.orbitUnreal(0, 4)
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: Math.min(parent.width - 48, 520)
            visible: mosimOrchestrator.unrealWindow === null
            spacing: 10

            QGCLabel {
                Layout.alignment: Qt.AlignHCenter
                text: "UE三维视图"
                font.bold: true
                font.pixelSize: ScreenTools.largeFontPixelSize
            }
            QGCLabel {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.Wrap
                text: mosimOrchestrator.unrealEmbedState === "waiting_for_window"
                      ? "正在等待受管UE窗口..."
                      : mosimOrchestrator.unrealEmbedState === "window_discovered_hidden"
                        ? "正在把UE嵌入QGC主视图..."
                      : mosimOrchestrator.unrealEmbedState === "blocked"
                        ? "UE原生嵌入未完成，窗口已保持隐藏。"
                        : "启动显示会话后，这里将显示工厂UE场景。"
                color: qgcPal.text
            }
            QGCLabel {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                visible: mosimOrchestrator.unrealEmbedReason.length > 0
                text: mosimOrchestrator.unrealEmbedReason
                color: qgcPal.colorOrange
                wrapMode: Text.WrapAnywhere
            }
            QGCButton {
                Layout.alignment: Qt.AlignHCenter
                text: "重试UE嵌入"
                visible: mosimOrchestrator.displaySessionId.length > 0
                         && mosimOrchestrator.unrealWindow === null
                enabled: !mosimOrchestrator.busy
                onClicked: mosimOrchestrator.refreshUnrealEmbedding()
            }
        }

        onWidthChanged: Qt.callLater(root.syncUnrealOverlayHole)
        onHeightChanged: Qt.callLater(root.syncUnrealOverlayHole)
    }

    Rectangle {
        id: consolePanel
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: Math.min(460, parent.width * 0.42)
        color: qgcPal.window
        z: 100
        border.color: qgcPal.text
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: ScreenTools.defaultFontPixelWidth
            spacing: ScreenTools.defaultFontPixelHeight * 0.45

            RowLayout {
                Layout.fillWidth: true
                QGCLabel { text: "MoSim飞行控制台"; font.bold: true; Layout.fillWidth: true }
                BusyIndicator { running: mosimOrchestrator.busy; visible: running; implicitWidth: 24; implicitHeight: 24 }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 28
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

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 3
                RowLayout {
                    Layout.fillWidth: true
                    QGCLabel { text: "启动进度"; font.bold: true; Layout.fillWidth: true }
                    QGCLabel {
                        text: mosimOrchestrator.operationAttempt > 0
                              ? mosimOrchestrator.operationAttempt + "/" + mosimOrchestrator.operationMaxAttempts
                              : "-"
                    }
                }
                QGCLabel {
                    text: operationStageText(mosimOrchestrator.operationStage)
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
                ProgressBar {
                    Layout.fillWidth: true
                    indeterminate: mosimOrchestrator.operationState === "running" && mosimOrchestrator.operationProgress < 0
                    value: mosimOrchestrator.operationProgress < 0 ? 0 : mosimOrchestrator.operationProgress / 100
                }
            }

            TabBar {
                id: tabs
                Layout.fillWidth: true
                TabButton { text: "任务" }
                TabButton { text: "遥测" }
                TabButton { text: "故障" }
                TabButton { text: "显示" }
                TabButton { text: "证据" }
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
                        spacing: 10
                        QGCLabel { text: "任务配置"; font.bold: true }
                        QGCCheckBox {
                            id: manualModeCheck
                            text: "启用W/A/S/D定点操纵"
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
                        QGCLabel {
                            text: taskGuideText()
                            color: manualModeCheck.checked ? qgcPal.colorGreen : qgcPal.text
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel {
                            text: "控制权与解锁责任：" + flightAuthorityText()
                            color: manualTaskSelected ? qgcPal.colorGreen : qgcPal.colorOrange
                            font.bold: true
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel {
                            text: "下一步：" + nextOperatorStepText()
                            color: qgcPal.colorOrange
                            font.bold: true
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel { text: "操作进度"; font.bold: true }
                        Repeater {
                            model: operatorChecklist()
                            delegate: RowLayout {
                                Layout.fillWidth: true
                                QGCLabel {
                                    text: modelData.state
                                    color: operatorChecklistColor(modelData.state)
                                    font.bold: modelData.state !== "等待"
                                    Layout.preferredWidth: 56
                                }
                                QGCLabel {
                                    text: modelData.label
                                    color: operatorChecklistColor(modelData.state)
                                    wrapMode: Text.Wrap
                                    Layout.fillWidth: true
                                }
                            }
                        }
                        QGCLabel {
                            text: "飞行阶段：" + flightPhaseText()
                            color: qgcPal.text
                            font.bold: true
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel {
                            visible: profiles[profileBox.currentIndex].takeoff !== "qgc"
                            text: "任务Adapter阶段：" + missionStatusText()
                            color: missionStatusColor()
                            font.bold: true
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
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
                                ToolTip.text: modelData.disabledReason
                            }
                            onActivated: {
                                syncProfileSelection()
                            }
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            visible: !profiles[profileBox.currentIndex].enabled
                            text: profiles[profileBox.currentIndex].disabledReason
                            color: qgcPal.colorOrange
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            visible: mosimOrchestrator.runId !== "" && selectionMatchesPreparedRun()
                            text: frozenScenarioSummary()
                            color: qgcPal.colorGreen
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            visible: mosimOrchestrator.runId !== "" && selectionMatchesPreparedRun()
                            text: "场景哈希：" + String(mosimOrchestrator.runManifest.scenario_hash || "-")
                            color: qgcPal.text
                            wrapMode: Text.WrapAnywhere
                        }
                        QGCLabel { text: "控制器Profile" }
                        ComboBox {
                            id: controllerBox
                            Layout.fillWidth: true
                            enabled: flightConfigurationEditable
                            model: mosimOrchestrator.controllers
                            textRole: "label"
                            valueRole: "module_id"
                            delegate: ItemDelegate {
                                width: controllerBox.width
                                text: modelData.label
                                enabled: modelData.enabled && root.controllerCompatibleWithTask(modelData.module_id)
                                ToolTip.visible: hovered && !enabled
                                ToolTip.text: !modelData.enabled
                                              ? modelData.disabled_reason
                                              : "当前任务没有该控制器的运行后端"
                            }
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            visible: controllerBox.currentIndex >= 0
                                     && !mosimOrchestrator.controllers[controllerBox.currentIndex].enabled
                            text: visible ? mosimOrchestrator.controllers[controllerBox.currentIndex].disabled_reason : ""
                            color: qgcPal.colorOrange
                            wrapMode: Text.Wrap
                        }
                        QGCLabel { text: "无人机数量" }
                        ComboBox {
                            id: vehicleBox
                            Layout.fillWidth: true
                            enabled: flightConfigurationEditable
                            model: vehicleCounts
                            textRole: "label"
                            delegate: ItemDelegate {
                                width: vehicleBox.width
                                text: modelData.label
                                enabled: modelData.enabled && root.vehicleCountCompatibleWithTask(modelData.value)
                                ToolTip.visible: hovered && !enabled
                                ToolTip.text: !modelData.enabled ? "该机数尚未通过规模验收"
                                                                  : "当前任务固定为" + profiles[profileBox.currentIndex].count + "架飞机"
                            }
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            visible: !taskSelectionCompatible()
                            text: "当前控制器或机数与任务运行后端不匹配，请重新选择任务。"
                            color: qgcPal.colorRed
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: manualTaskSelected
                                  ? "手动定点：运行时就绪后，使用QGC原生解锁、起飞和Position模式。"
                                  : "自动任务：Mission Adapter将独占完成连接检查、解锁、起飞、任务执行和降落；无需手动解锁。"
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
                                         && controllerBox.currentIndex >= 0
                                         && mosimOrchestrator.controllers[controllerBox.currentIndex].enabled
                                         && vehicleCounts[vehicleBox.currentIndex].enabled
                                         && profiles[profileBox.currentIndex].enabled
                                         && taskSelectionCompatible()
                                onClicked: mosimOrchestrator.prepareRun(profiles[profileBox.currentIndex].path,
                                                                        controllerBox.currentValue,
                                                                        vehicleCounts[vehicleBox.currentIndex].value, 0,
                                                                        manualTaskSelected)
                            }
                            QGCButton {
                                text: manualTaskSelected ? "启动仿真并连接飞机" : "启动并执行自动任务"
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
                        QGCButton {
                            text: manualKeyboardEnabled ? "点击后使用W/A/S/D"
                                                        : (manualTaskSelected ? "起飞并切换Position后启用W/A/S/D"
                                                                              : "当前任务不使用键盘操纵")
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
                        QGCLabel { text: "运行编号"; font.bold: true }
                        QGCLabel { text: mosimOrchestrator.runId || "-"; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
                        QGCLabel { text: "运行状态：" + mosimOrchestrator.lifecycleState }
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
                            text: "地图轨迹：" + taskPathStatusText()
                            color: runtimeTelemetryFresh() ? qgcPal.colorGreen : qgcPal.colorOrange
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCLabel {
                            text: "以下为逐机遥测确认，不代替任务Adapter终态ACK。自动任务只有全部飞机完成并收到终态ACK才算成功。"
                            color: qgcPal.colorOrange
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
                            visible: profiles[profileBox.currentIndex].takeoff !== "qgc"
                                     && missionStatus().adapter_id !== undefined
                            text: "Adapter：" + String(missionStatus().adapter_id || "-")
                                  + " · 状态：" + String(missionStatus().state || "-")
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        Repeater {
                            model: profiles[profileBox.currentIndex].takeoff === "qgc"
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
                            visible: profiles[profileBox.currentIndex].takeoff !== "qgc"
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
                            visible: runtimeTelemetryFresh() && runtimeVehicles().length !== profiles[profileBox.currentIndex].count
                            text: "状态不完整：收到 " + runtimeVehicles().length + "/"
                                  + profiles[profileBox.currentIndex].count + " 架飞机遥测"
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
                            model: ["uav1", "uav2", "uav3"]
                            delegate: ItemDelegate {
                                width: injectionVehicle.width
                                text: modelData
                                enabled: index < profiles[profileBox.currentIndex].count
                            }
                        }
                        QGCLabel { text: "风速（m/s）" }
                        Slider { id: windSlider; Layout.fillWidth: true; from: 0; to: 20; stepSize: 0.5 }
                        QGCLabel { text: windSlider.value.toFixed(1) }
                        QGCButton { text: "应用风扰"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.applyWind(injectionVehicle.currentText, windSlider.value) }
                        QGCLabel { text: "电机效率" }
                        RowLayout {
                            Layout.fillWidth: true
                            SpinBox { id: rotorIndex; from: 1; to: 4; value: 1 }
                            Slider { id: motorSlider; Layout.fillWidth: true; from: 0; to: 1; value: 1; stepSize: 0.05 }
                            QGCLabel { text: motorSlider.value.toFixed(2) }
                        }
                        QGCButton { text: "应用电机故障"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.applyMotorEffectiveness(injectionVehicle.currentText, rotorIndex.value, motorSlider.value) }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton { text: "恢复无风"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.restoreInjection(injectionVehicle.currentText, "wind_speed_mps") }
                            QGCButton { text: "恢复电机"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.restoreInjection(injectionVehicle.currentText, "motor_effectiveness", rotorIndex.value) }
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        QGCCheckBox { id: pointCloudDisplay; text: "RViz点云地图"; checked: true }
                        QGCCheckBox { id: gridMapDisplay; text: "RViz栅格地图"; checked: true }
                        QGCCheckBox { id: unrealDisplay; text: "UE三维视图"; checked: true }
                        QGCCheckBox {
                            id: mworksDisplay
                            text: "MWORKS实时曲线（由Model Studio启动）"
                            enabled: false
                            checked: false
                        }
                        QGCLabel {
                            text: "自动拉起MWORKS实时模型尚未完成验收；当前请在Model Studio启动实时曲线，Flight Console不伪装为已打开。"
                            color: qgcPal.colorOrange
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                        }
                        QGCButton {
                            text: "准备显示窗口"
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
                                text: "切换UE视角"
                                Layout.fillWidth: true
                                enabled: mosimOrchestrator.unrealWindow !== null
                                onClicked: mosimOrchestrator.cycleUnrealView()
                            }
                            QGCButton {
                                text: "-"
                                enabled: mosimOrchestrator.unrealWindow !== null
                                onClicked: mosimOrchestrator.zoomUnrealOut()
                            }
                            QGCButton {
                                text: "+"
                                enabled: mosimOrchestrator.unrealWindow !== null
                                onClicked: mosimOrchestrator.zoomUnrealIn()
                            }
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
                        spacing: 10
                        QGCLabel { text: "MoSim智能助手"; font.bold: true }
                        QGCLabel {
                            Layout.fillWidth: true
                            wrapMode: Text.Wrap
                            text: "受控任务助手把自然语言转换为已登记的任务Profile。采用建议只会验证并冻结配置；启动、解锁和飞行仍需在任务页人工确认。"
                        }
                        TextArea {
                            id: agentPrompt
                            Layout.fillWidth: true
                            Layout.preferredHeight: 110
                            placeholderText: "例如：运行FUEL单机自主探索，或运行三机固定编队避障"
                            enabled: flightConfigurationEditable && !mosimOrchestrator.busy
                        }
                        QGCButton {
                            text: "生成受控任务建议"
                            Layout.fillWidth: true
                            enabled: agentPrompt.enabled && agentPrompt.text.trim().length > 0
                            onClicked: mosimOrchestrator.proposeOperatorTask(agentPrompt.text)
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            wrapMode: Text.Wrap
                            visible: agentProposalReady()
                            color: qgcPal.colorGreen
                            text: "建议任务：" + String(mosimOrchestrator.agentProposal.label || "-")
                                  + "\n控制器：" + String(mosimOrchestrator.agentProposal.controller_id || "-")
                                  + "；飞机数量：" + String(mosimOrchestrator.agentProposal.vehicle_count || "-")
                                  + "\n安全边界：助手不能启动或控制飞机。"
                        }
                        QGCButton {
                            text: "采用建议并验证配置"
                            Layout.fillWidth: true
                            visible: agentProposalReady()
                            enabled: visible && flightConfigurationEditable && !mosimOrchestrator.busy
                                     && profiles[profileIndex(String(mosimOrchestrator.agentProposal.profile_id || ""))].enabled
                            onClicked: confirmAgentProposal()
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            wrapMode: Text.Wrap
                            color: qgcPal.colorOrange
                            text: "当前为本机受控意图路由器；Codex诊断能力尚未接入，不作为飞行控制权所有者。"
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: mosimOrchestrator
        function onUnrealWindowChanged() {
            Qt.callLater(root.syncUnrealOverlayHole)
        }
        function onResponseChanged() {
            if (!controllerCatalogSynced && mosimOrchestrator.controllers.length > 0) {
                syncProfileSelection()
                controllerCatalogSynced = true
            }
        }
    }
}
