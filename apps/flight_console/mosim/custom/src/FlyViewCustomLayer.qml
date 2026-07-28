import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import QGroundControl
import QGroundControl.Controls
import QGroundControl.Palette
import QGroundControl.ScreenTools

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

    readonly property var profiles: mosimOperator.operatorProfiles || []
    readonly property var selectedProfile: mosimOperator.selectedProfile || ({})
    readonly property var mapState: (mosimOperator.runtimeTelemetry || ({})).map_state || ({})
    readonly property var pendingFault: mosimOperator.pendingFault || ({})
    readonly property int panelWidth: Math.min(360, Math.max(282, width * 0.30))

    function profileIndex() {
        for (var index = 0; index < profiles.length; ++index) {
            if (String(profiles[index].profile_id || "") === mosimOperator.selectedProfileId)
                return index
        }
        return 0
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

    Component.onCompleted: mosimOperator.refresh()

    Timer {
        interval: 1000
        repeat: true
        running: true
        onTriggered: mosimOperator.refreshRuntimeState()
    }

    FactoryFlyMap {
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

                        QGCLabel { text: "已发布 Profile"; font.bold: true }
                        ComboBox {
                            id: profileBox
                            Layout.fillWidth: true
                            enabled: !mosimOperator.profileSelectionLocked
                            model: root.profiles
                            textRole: "label"
                            currentIndex: root.profileIndex()
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
                                var profile = root.profiles[currentIndex] || ({})
                                mosimOperator.selectProfile(String(profile.profile_id || ""))
                            }
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "控制器：" + String(root.selectedProfile.controller_profile || "-")
                            wrapMode: Text.Wrap
                        }
                        QGCLabel {
                            Layout.fillWidth: true
                            text: "飞机：" + String(root.selectedProfile.vehicle_count || "-")
                                    + "  任务：" + String(root.selectedProfile.planner_profile || "-")
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
                            text: "当前 RunManifest 已冻结 Profile，不能切换或重复启动。"
                            wrapMode: Text.Wrap
                            color: qgcPal.colorOrange
                        }
                        QGCButton {
                            Layout.fillWidth: true
                            visible: mosimOperator.profileSelectionLocked
                            text: "复制结束当前运行命令"
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
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: ScreenTools.defaultFontPixelHeight * 0.35
                        QGCLabel { text: "二维地图图层"; font.bold: true }
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
                            text: String((root.mapState.transport || ({})).mode || "无地图数据")
                                    + "  " + String((root.mapState.transport || ({})).playback_state || "")
                            wrapMode: Text.Wrap
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

            QGCLabel { text: "终端命令"; font.bold: true }
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
