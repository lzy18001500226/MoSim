import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import QGroundControl
import QGroundControl.Controls
import QGroundControl.Palette
import QGroundControl.ScreenTools

import "qrc:/Custom/qml/QGroundControl/FlightDisplay" as MoSimFlightDisplay

Item {
    id: root

    property var parentToolInsets
    property var totalToolInsets: toolInsets
    property var mapControl

    property bool showMapVehicles: true
    property bool showMapActualTracks: true
    property bool showMapExpectedPath: true
    property bool showMapFuturePath: true
    property bool showMapTaskBoundary: true
    property bool showMapFormationTarget: true
    property string assistantReply: "请选择已发布 Profile 或输入任务描述。"
    property string selectedControllerFamilyId: "pid_family"
    property string observedControllerSchemeId: ""

    readonly property var profiles: mosimOperator.operatorProfiles || []
    readonly property var controllerFamilies: mosimOperator.controllerFamilies || []
    readonly property var controllerSchemes: mosimOperator.controllerSchemes || []
    readonly property var operatorMaps: mosimOperator.operatorMaps || []
    readonly property var selectedProfile: mosimOperator.selectedProfile || ({})
    readonly property var selectedController: root.controllerForId(mosimOperator.selectedControllerSchemeId)
    readonly property var compatibleProfiles: root.profilesForController(mosimOperator.selectedControllerSchemeId)
    readonly property var runManifest: mosimOperator.runManifest || ({})
    readonly property var runtimeTelemetry: mosimOperator.runtimeTelemetry || ({})
    readonly property var runtimeStatus: root.runtimeTelemetry.operator_runtime_status || ({})
    readonly property var mapState: root.runtimeTelemetry.map_state || ({})
    readonly property var faultAcks: mosimOperator.faultAcks || []
    readonly property var pendingFault: mosimOperator.pendingFault || ({})
    readonly property int panelWidth: Math.min(360, Math.max(282, width * 0.30))

    function profileIndex(options) {
        for (var index = 0; index < options.length; ++index) {
            if (String(options[index].profile_id || "") === mosimOperator.selectedProfileId)
                return index
        }
        return 0
    }

    function profilesForController(schemeId) {
        if (!schemeId)
            return profiles
        var options = []
        for (var index = 0; index < profiles.length; ++index) {
            if (String(profiles[index].controller_scheme_id || "") === String(schemeId))
                options.push(profiles[index])
        }
        return options
    }

    function controllerForId(schemeId) {
        for (var index = 0; index < controllerSchemes.length; ++index) {
            if (String(controllerSchemes[index].scheme_id || "") === String(schemeId || ""))
                return controllerSchemes[index]
        }
        return ({})
    }

    function controllerFamilyIndex(category) {
        for (var index = 0; index < controllerFamilies.length; ++index) {
            if (String(controllerFamilies[index].category || "") === String(category || ""))
                return index
        }
        return 0
    }

    function controllerOptionsForFamily(category) {
        var options = []
        for (var index = 0; index < controllerSchemes.length; ++index) {
            if (String(controllerSchemes[index].category || "") === String(category || ""))
                options.push(controllerSchemes[index])
        }
        return options
    }

    function controllerOptionIndex(options, schemeId) {
        for (var index = 0; index < options.length; ++index) {
            if (String(options[index].scheme_id || "") === String(schemeId || ""))
                return index
        }
        return 0
    }

    function operatorMapIndex(options, mapId) {
        for (var index = 0; index < options.length; ++index) {
            if (String(options[index].map_id || "") === String(mapId || ""))
                return index
        }
        return 0
    }

    function syncControllerFamily() {
        var schemeId = String(mosimOperator.selectedControllerSchemeId || "")
        if (!schemeId || schemeId === root.observedControllerSchemeId)
            return
        var controller = root.controllerForId(schemeId)
        if (controller.category)
            root.selectedControllerFamilyId = String(controller.category)
        root.observedControllerSchemeId = schemeId
    }

    function vehicleIds() {
        var count = Number(selectedProfile.vehicle_count || 1)
        var values = []
        for (var index = 1; index <= Math.max(1, Math.min(9, count)); ++index)
            values.push("uav" + index)
        return values
    }

    function pendingFaultText() {
        if (!pendingFault.target)
            return "无待应用故障"
        if (pendingFault.target === "motor_effectiveness")
            return String(pendingFault.vehicle_id) + " 电机" + String(pendingFault.rotor_index)
                    + " 效率 " + Number(pendingFault.value).toFixed(2)
        return String(pendingFault.vehicle_id) + " 风速 " + Number(pendingFault.value).toFixed(1) + " m/s"
    }

    function telemetryVehicle(vehicleId) {
        var vehicles = runtimeTelemetry.vehicles || []
        for (var index = 0; index < vehicles.length; ++index) {
            if (String(vehicles[index].vehicle_id || "") === String(vehicleId || ""))
                return vehicles[index]
        }
        return ({})
    }

    function faultStateText(vehicleId) {
        var injectionState = telemetryVehicle(vehicleId).injection_state || ({})
        var effectiveness = injectionState.motor_effectiveness || []
        if (injectionState.wind_speed_mps === undefined || effectiveness.length !== 4)
            return "当前生效值：未收到本次运行遥测"
        var motors = []
        for (var index = 0; index < effectiveness.length; ++index)
            motors.push("M" + String(index + 1) + "=" + Number(effectiveness[index]).toFixed(2))
        return "当前生效值：风速 " + Number(injectionState.wind_speed_mps).toFixed(1)
                + " m/s；" + motors.join(" ")
    }

    function latestFaultAck(vehicleId) {
        var latest = ({})
        var latestAt = -1
        for (var index = 0; index < faultAcks.length; ++index) {
            var ack = faultAcks[index] || ({})
            if (String(ack.vehicle_id || "") !== String(vehicleId || ""))
                continue
            var appliedAt = Number(ack.applied_at || 0)
            if (appliedAt >= latestAt) {
                latest = ack
                latestAt = appliedAt
            }
        }
        return latest
    }

    function faultAckText(vehicleId) {
        var ack = latestFaultAck(vehicleId)
        if (!ack.command_id)
            return "最新 ACK：尚未收到本次运行确认"
        var target = String(ack.target || "故障命令")
        if (target === "motor_effectiveness")
            target = "电机" + String(ack.rotor_index || "-") + "效率"
        else if (target === "wind_speed_mps")
            target = "风扰"
        else if (target === "wind_direction_deg")
            target = "风向"
        var outcome = ack.accepted === true ? "已接受" : "已拒绝"
        var valueText = ack.applied_value === undefined || ack.applied_value === null
                ? "" : "，生效值 " + Number(ack.applied_value).toFixed(2)
        return "最新 ACK：" + outcome + "，" + target + valueText
                + "（" + String(ack.reason_code || "-") + "）"
    }

    function mapTransportStatusText() {
        var transport = mapState.transport || ({})
        var mode = String(transport.mode || "")
        var playbackState = String(transport.playback_state || "")
        if (mode === "live_ros1")
            return "ROS1 实时数据"
        if (mode === "rosbag_replay") {
            if (playbackState === "playing")
                return "rosbag 回放中"
            if (playbackState === "paused")
                return "rosbag 回放已暂停"
            if (playbackState === "completed")
                return "rosbag 回放已完成"
            if (playbackState === "failed")
                return "rosbag 回放失败"
            return "rosbag 回放状态未知"
        }
        return "等待地图数据"
    }

    function mapTransportDetailText() {
        var transport = mapState.transport || ({})
        if (String(transport.mode || "") !== "rosbag_replay")
            return ""
        var details = []
        var bagId = String(transport.bag_id || "")
        if (bagId.length > 0)
            details.push("记录：" + bagId)
        var playbackTime = Number(transport.playback_time_s)
        if (isFinite(playbackTime) && playbackTime >= 0)
            details.push("回放时间：" + playbackTime.toFixed(1) + " s")
        return details.join("；")
    }

    function runtimeStatusIsBound() {
        return String(runtimeStatus.schema || "") === "mosim.operator_runtime_status.v1"
                && String(runtimeStatus.run_id || "") === String(runManifest.run_id || "")
                && String(runtimeStatus.experiment_profile_id || "")
                        === String(runManifest.experiment_profile_id || "")
                && String(runtimeStatus.experiment_profile_hash || "")
                        === String(runManifest.experiment_profile_hash || "")
    }

    function frozenControllerBackendText() {
        if (!runManifest.run_id)
            return "未冻结"
        var backend = String(runManifest.controller_backend || "")
        return backend.length > 0 ? backend : "未声明"
    }

    function runtimeStateText() {
        if (!runtimeStatusIsBound()) {
            return runtimeTelemetry.operator_runtime_status_rejected_reason
                    ? "身份不匹配，已忽略" : "运行端未上报状态"
        }
        var state = String(runtimeStatus.state || "")
        if (state === "starting")
            return "启动中"
        if (state === "running")
            return String(runtimeStatus.reason_code || "") === "runtime_readiness_degraded"
                    ? "运行中（健康降级）" : "运行中"
        if (state === "blocked")
            return "已阻塞"
        if (state === "replaying")
            return "回放中"
        return state.length > 0 ? state : "运行端未上报状态"
    }

    function runtimeReasonText() {
        return runtimeStatusIsBound()
                ? String(runtimeStatus.reason_code || "未上报")
                : "未上报"
    }

    function runtimeMetricText(key, unit, multiplier) {
        if (!runtimeStatusIsBound())
            return "未测量"
        var value = (runtimeStatus.observability || ({}))[key]
        if (typeof value !== "number" || !isFinite(value))
            return "未测量"
        var scale = multiplier === undefined ? 1.0 : multiplier
        return (value * scale).toFixed(2) + unit
    }

    function runtimeAlertsText() {
        if (!runtimeStatusIsBound())
            return "运行端未上报告警"
        var alerts = runtimeStatus.alerts
        if (alerts === undefined || alerts === null)
            return "运行端未上报告警"
        if (alerts.length === 0)
            return "运行端报告无告警"
        var values = []
        for (var index = 0; index < alerts.length; ++index) {
            var alert = alerts[index] || ({})
            values.push(String(alert.code || alert.reason_code || "未命名告警"))
        }
        return values.join("；")
    }

    function agentSuggest() {
        var text = agentPrompt.text.trim().toLowerCase()
        if (text.indexOf("fuel") >= 0 || text.indexOf("探索") >= 0)
            assistantReply = "建议：FUEL 单机自主探索。"
        else if (text.indexOf("三机") >= 0 || text.indexOf("编队") >= 0 || text.indexOf("swarm") >= 0)
            assistantReply = "建议：三机固定编队避障。"
        else if (text.indexOf("8") >= 0 || text.indexOf("八字") >= 0 || text.indexOf("figure") >= 0)
            assistantReply = "建议：单机 8 字飞行。"
        else if (text.length > 0)
            assistantReply = "未匹配已发布任务，请选择 Profile。"
    }

    QGCToolInsets {
        id: toolInsets
        leftEdgeTopInset: parentToolInsets.leftEdgeTopInset
        leftEdgeCenterInset: parentToolInsets.leftEdgeCenterInset
        leftEdgeBottomInset: parentToolInsets.leftEdgeBottomInset
        rightEdgeTopInset: Math.max(parentToolInsets.rightEdgeTopInset, operationPanel.width + ScreenTools.defaultFontPixelWidth)
        rightEdgeCenterInset: Math.max(parentToolInsets.rightEdgeCenterInset, operationPanel.width + ScreenTools.defaultFontPixelWidth)
        rightEdgeBottomInset: Math.max(parentToolInsets.rightEdgeBottomInset, operationPanel.width + ScreenTools.defaultFontPixelWidth)
        topEdgeLeftInset: parentToolInsets.topEdgeLeftInset
        topEdgeCenterInset: parentToolInsets.topEdgeCenterInset
        topEdgeRightInset: parentToolInsets.topEdgeRightInset
        bottomEdgeLeftInset: parentToolInsets.bottomEdgeLeftInset
        bottomEdgeCenterInset: parentToolInsets.bottomEdgeCenterInset
        bottomEdgeRightInset: parentToolInsets.bottomEdgeRightInset
    }

    Component.onCompleted: {
        mosimOperator.refresh()
        root.syncControllerFamily()
    }

    Timer {
        interval: 1000
        repeat: true
        running: true
        onTriggered: mosimOperator.refreshRuntimeState()
    }

    Connections {
        target: mosimOperator
        function onStateChanged() {
            root.syncControllerFamily()
        }
    }

    MoSimFlightDisplay.FactoryFlyMap {
        id: factoryFlyMap
        anchors.fill: parent
        mapConfig: mosimOperator.operatorMap || ({})
        runManifest: mosimOperator.runManifest || ({})
        mapState: root.mapState
        runId: mosimOperator.runId
        showVehicles: root.showMapVehicles
        showActualTracks: root.showMapActualTracks
        showExpectedPath: root.showMapExpectedPath
        showFuturePath: root.showMapFuturePath
        showTaskBoundary: root.showMapTaskBoundary
        showFormationTarget: root.showMapFormationTarget
    }

    Rectangle {
        id: operationPanel
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: ScreenTools.defaultFontPixelWidth
        width: root.panelWidth
        z: 20
        color: qgcPal.window
        opacity: 0.97
        border.width: 1
        border.color: qgcPal.windowShade

        QGCPalette { id: qgcPal; colorGroupEnabled: enabled }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: ScreenTools.defaultFontPixelWidth
            spacing: ScreenTools.defaultFontPixelHeight * 0.35

            RowLayout {
                Layout.fillWidth: true
                QGCLabel {
                    text: "MoSim 地面站"
                    font.bold: true
                    Layout.fillWidth: true
                }
                QGCButton {
                    text: "刷新"
                    onClicked: mosimOperator.refresh()
                }
            }

            QGCLabel {
                Layout.fillWidth: true
                text: mosimOperator.statusText
                wrapMode: Text.Wrap
                color: mosimOperator.reasonCode === "command_copied" ? qgcPal.colorGreen : qgcPal.text
            }

            TabBar {
                id: sectionTabs
                Layout.fillWidth: true
                TabButton { text: "任务" }
                TabButton { text: "故障" }
                TabButton { text: "地图" }
                TabButton { text: "回放" }
                TabButton { text: "助手" }
            }

            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: sectionTabs.currentIndex

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: ScreenTools.defaultFontPixelHeight * 0.45

                        QGCLabel { text: "控制器族"; font.bold: true }
                        ComboBox {
                            id: controllerFamilyBox
                            Layout.fillWidth: true
                            model: root.controllerFamilies
                            textRole: "display_name_zh"
                            currentIndex: root.controllerFamilyIndex(root.selectedControllerFamilyId)
                            enabled: !mosimOperator.profileSelectionLocked
                            onActivated: {
                                var family = root.controllerFamilies[currentIndex] || ({})
                                root.selectedControllerFamilyId = String(family.category || "")
                            }
                        }
                        QGCLabel { text: "控制器"; font.bold: true }
                        ComboBox {
                            id: controllerBox
                            readonly property var options: root.controllerOptionsForFamily(root.selectedControllerFamilyId)
                            Layout.fillWidth: true
                            model: options
                            textRole: "display_name_zh"
                            currentIndex: root.controllerOptionIndex(options, mosimOperator.selectedControllerSchemeId)
                            enabled: !mosimOperator.profileSelectionLocked
                            delegate: ItemDelegate {
                                required property var modelData
                                required property int index
                                width: controllerBox.width
                                text: String(modelData.display_name_zh || "未命名控制器")
                                      + (modelData.selectable === true ? "" : "（未发布）")
                                enabled: modelData.selectable === true
                                opacity: enabled ? 1.0 : 0.55
                                ToolTip.visible: hovered && !enabled
                                ToolTip.text: String(modelData.disabled_reason || "尚无可用 Profile")
                                onClicked: {
                                    controllerBox.currentIndex = index
                                    controllerBox.popup.close()
                                    mosimOperator.selectControllerScheme(String(modelData.scheme_id || ""))
                                }
                            }
                            onActivated: {
                                var controller = options[currentIndex] || ({})
                                mosimOperator.selectControllerScheme(String(controller.scheme_id || ""))
                            }
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "控制：" + String(root.selectedController.display_name_zh
                                                           || root.selectedProfile.controller_profile || "-")
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            visible: root.selectedController.selectable !== true
                            text: String(root.selectedController.disabled_reason || "当前控制器未开放")
                            wrapMode: Text.Wrap
                            color: qgcPal.colorOrange
                        }
                        QGCLabel { text: "任务配置"; font.bold: true }
                        ComboBox {
                            id: profileBox
                            Layout.fillWidth: true
                            enabled: !mosimOperator.profileSelectionLocked
                            model: root.compatibleProfiles
                            textRole: "label"
                            currentIndex: root.profileIndex(root.compatibleProfiles)
                            delegate: ItemDelegate {
                                required property var modelData
                                required property int index
                                width: profileBox.width
                                text: String(modelData.label || "未命名 Profile")
                                enabled: modelData.enabled === true
                                opacity: enabled ? 1.0 : 0.55
                                onClicked: {
                                    profileBox.currentIndex = index
                                    profileBox.popup.close()
                                    mosimOperator.selectProfile(String(modelData.profile_id || ""))
                                }
                            }
                            onActivated: {
                                var profile = root.compatibleProfiles[currentIndex] || ({})
                                mosimOperator.selectProfile(String(profile.profile_id || ""))
                            }
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: String(root.selectedProfile.vehicle_count || "-") + " 架 | "
                                    + String(root.selectedProfile.planner_profile || "-")
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            visible: root.selectedProfile.enabled !== true
                            text: String(root.selectedProfile.disabled_reason || "当前 Profile 未开放")
                            wrapMode: Text.Wrap
                            color: qgcPal.colorOrange
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            visible: mosimOperator.profileSelectionLocked
                            text: "运行已冻结，不能切换。"
                            wrapMode: Text.Wrap
                            color: qgcPal.colorOrange
                        }
                        QGCButton {
                            Layout.fillWidth: true
                            visible: mosimOperator.profileSelectionLocked
                            text: "复制清除运行清单命令"
                            onClicked: mosimOperator.copyClearActiveRunCommand()
                        }
                        QGCButton {
                            text: "复制启动命令"
                            Layout.fillWidth: true
                            enabled: root.selectedProfile.enabled === true && !mosimOperator.profileSelectionLocked
                            onClicked: mosimOperator.copySelectedLaunchCommand()
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "运行：" + (mosimOperator.runId || "未绑定")
                            wrapMode: Text.WrapAnywhere
                        }
                        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: qgcPal.windowShade }
                        QGCLabel { text: "冻结配置"; font.bold: true }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "控制后端：" + root.frozenControllerBackendText()
                            wrapMode: Text.WrapAnywhere
                        }
                        QGCLabel { text: "运行反馈"; font.bold: true }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "状态：" + root.runtimeStateText()
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "原因：" + root.runtimeReasonText()
                            wrapMode: Text.WrapAnywhere
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "RTT（P95）：" + root.runtimeMetricText("rtt_ms", " ms")
                                    + "；抖动：" + root.runtimeMetricText("jitter_ms", " ms")
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "命令年龄：" + root.runtimeMetricText("command_age_ms", " ms")
                                    + "；丢包率：" + root.runtimeMetricText("packet_loss_rate", " %", 100.0)
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "告警：" + root.runtimeAlertsText()
                            wrapMode: Text.Wrap
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: ScreenTools.defaultFontPixelHeight * 0.45

                        QGCLabel { text: "离散故障"; font.bold: true }
                        ComboBox {
                            id: faultVehicle
                            Layout.fillWidth: true
                            model: root.vehicleIds()
                        }
                        QGCLabel { text: "风速 (m/s)" }
                        RowLayout {
                            Layout.fillWidth: true
                            Slider { id: windSlider; Layout.fillWidth: true; from: 0; to: 20; stepSize: 0.5 }
                            QGCLabel { text: windSlider.value.toFixed(1) }
                        }
                        QGCButton {
                            text: "暂存风扰"
                            Layout.fillWidth: true
                            onClicked: mosimOperator.stageWind(faultVehicle.currentText, windSlider.value)
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
                            onClicked: mosimOperator.stageMotorEffectiveness(faultVehicle.currentText, rotorIndex.value, motorSlider.value)
                        }
                        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: qgcPal.windowShade }
                        QGCLabel { text: root.pendingFaultText(); Layout.fillWidth: true; wrapMode: Text.Wrap }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton {
                                text: "复制应用命令"
                                Layout.fillWidth: true
                                enabled: root.pendingFault.target !== undefined
                                onClicked: mosimOperator.copyStagedFaultCommand()
                            }
                            QGCButton {
                                text: "清除暂存"
                                Layout.fillWidth: true
                                onClicked: mosimOperator.clearPendingFault()
                            }
                        }
                        QGCButton {
                            text: "复制恢复正常命令"
                            Layout.fillWidth: true
                            onClicked: mosimOperator.copyRestoreNormalCommand(faultVehicle.currentText)
                        }
                        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: qgcPal.windowShade }
                        QGCLabel { text: "生效状态"; font.bold: true }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: root.faultStateText(faultVehicle.currentText)
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: root.faultAckText(faultVehicle.currentText)
                            wrapMode: Text.Wrap
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: ScreenTools.defaultFontPixelHeight * 0.35
                        QGCLabel { text: "二维地图"; font.bold: true }
                        ComboBox {
                            id: operatorMapBox
                            Layout.fillWidth: true
                            model: root.operatorMaps
                            textRole: "display_name"
                            currentIndex: root.operatorMapIndex(root.operatorMaps, mosimOperator.selectedMapId)
                            enabled: !mosimOperator.profileSelectionLocked
                            delegate: ItemDelegate {
                                required property var modelData
                                required property int index
                                width: operatorMapBox.width
                                text: String(modelData.display_name || "未命名地图")
                                      + (modelData.selectable === true ? "" : "（未发布）")
                                enabled: modelData.selectable === true
                                opacity: enabled ? 1.0 : 0.55
                                ToolTip.visible: hovered && !enabled
                                ToolTip.text: String(modelData.disabled_reason || "尚无兼容 Profile")
                                onClicked: {
                                    operatorMapBox.currentIndex = index
                                    operatorMapBox.popup.close()
                                    mosimOperator.selectOperatorMap(String(modelData.map_id || ""))
                                }
                            }
                            onActivated: {
                                var map = root.operatorMaps[currentIndex] || ({})
                                mosimOperator.selectOperatorMap(String(map.map_id || ""))
                            }
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: mosimOperator.profileSelectionLocked
                                  ? "地图已冻结。"
                                  : "切换地图会同步任务配置。"
                            wrapMode: Text.Wrap
                            color: mosimOperator.profileSelectionLocked ? qgcPal.colorOrange : qgcPal.text
                        }
                        QGCLabel { text: "图层"; font.bold: true }
                        QGCCheckBox { text: "飞机位置与航向"; checked: root.showMapVehicles; onToggled: root.showMapVehicles = checked }
                        QGCCheckBox { text: "实际飞行轨迹"; checked: root.showMapActualTracks; onToggled: root.showMapActualTracks = checked }
                        QGCCheckBox { text: "任务预期轨迹"; checked: root.showMapExpectedPath; onToggled: root.showMapExpectedPath = checked }
                        QGCCheckBox { text: "规划器未来轨迹"; checked: root.showMapFuturePath; onToggled: root.showMapFuturePath = checked }
                        QGCCheckBox { text: "任务边界"; checked: root.showMapTaskBoundary; onToggled: root.showMapTaskBoundary = checked }
                        QGCCheckBox { text: "编队目标"; checked: root.showMapFormationTarget; onToggled: root.showMapFormationTarget = checked }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: factoryFlyMap.taskPathStatusText()
                            wrapMode: Text.Wrap
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: ScreenTools.defaultFontPixelHeight * 0.45
                        QGCLabel { text: "rosbag 回放"; font.bold: true }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: root.mapTransportStatusText()
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: root.mapTransportDetailText()
                            visible: text.length > 0
                            wrapMode: Text.WrapAnywhere
                        }
                        QGCButton {
                            text: "复制回放命令"
                            Layout.fillWidth: true
                            onClicked: mosimOperator.copyRosbagReplayCommand()
                        }
                        QGCButton {
                            text: "刷新回放状态"
                            Layout.fillWidth: true
                            onClicked: mosimOperator.refreshRuntimeState()
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: ScreenTools.defaultFontPixelHeight * 0.45
                        QGCLabel { text: "任务助手"; font.bold: true }
                        QGCLabel { Layout.fillWidth: true; text: root.assistantReply; wrapMode: Text.Wrap }
                        TextArea {
                            id: agentPrompt
                            Layout.fillWidth: true
                            Layout.preferredHeight: 88
                            placeholderText: "输入任务"
                            wrapMode: TextEdit.Wrap
                        }
                        QGCButton {
                            text: "生成建议"
                            Layout.fillWidth: true
                            enabled: agentPrompt.text.trim().length > 0
                            onClicked: root.agentSuggest()
                        }
                    }
                }
            }

            QGCLabel { text: "命令"; font.bold: true }
            TextArea {
                Layout.fillWidth: true
                Layout.preferredHeight: 70
                readOnly: true
                selectByMouse: true
                wrapMode: TextEdit.WrapAnywhere
                text: mosimOperator.lastCommand
            }
            QGCButton {
                text: "复制当前命令"
                Layout.fillWidth: true
                enabled: mosimOperator.lastCommand.length > 0
                onClicked: mosimOperator.copyLastCommand()
            }
        }
    }
}
