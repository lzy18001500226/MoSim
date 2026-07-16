import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import QGroundControl
import QGroundControl.Controls
import QGroundControl.Palette
import QGroundControl.ScreenTools

Item {
    property var parentToolInsets
    property var totalToolInsets: toolInsets
    property var mapControl

    QGCPalette { id: qgcPal; colorGroupEnabled: true }

    readonly property var profiles: [
        { label: "Single UAV / Figure 8", path: "Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json", controller: "px4ctrl", count: 1, enabled: true },
        { label: "Single UAV / Cascade PID generated C / Figure 8", path: "Config/profiles/experiments/cascade_pid_figure8_generated_c_v1.json", controller: "cascade_pid", count: 1, enabled: true },
        { label: "Factory L2 / Three UAV", path: "Config/profiles/experiments/factory_l2_three_uav_swarm_formation_v1.json", controller: "px4ctrl", count: 3, enabled: true }
    ]
    readonly property var vehicleCounts: [
        { label: "1", value: 1, enabled: true },
        { label: "3", value: 3, enabled: true },
        { label: "4 (scale gate pending)", value: 4, enabled: false },
        { label: "5 (scale gate pending)", value: 5, enabled: false },
        { label: "6 (scale gate pending)", value: 6, enabled: false },
        { label: "7 (scale gate pending)", value: 7, enabled: false },
        { label: "8 (scale gate pending)", value: 8, enabled: false },
        { label: "9 (scale gate pending)", value: 9, enabled: false }
    ]
    readonly property var controllers: [
        { label: "px4ctrl", value: "px4ctrl", enabled: true },
        { label: "Cascade PID / MWORKS generated C", value: "cascade_pid", enabled: true },
        { label: "PID / runtime gate pending", value: "official_pid", enabled: false },
        { label: "INDI / runtime gate pending", value: "indi", enabled: false },
        { label: "NMPC / runtime gate pending", value: "nmpc_outer", enabled: false }
    ]

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
        id: consolePanel
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: Math.min(460, parent.width * 0.42)
        color: qgcPal.window
        border.color: qgcPal.text
        border.width: 1
        z: 100

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: ScreenTools.defaultFontPixelWidth
            spacing: ScreenTools.defaultFontPixelHeight * 0.45

            RowLayout {
                Layout.fillWidth: true
                QGCLabel { text: "MoSim Flight Console"; font.bold: true; Layout.fillWidth: true }
                BusyIndicator { running: mosimOrchestrator.busy; visible: running; implicitWidth: 24; implicitHeight: 24 }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 28
                color: mosimOrchestrator.accepted ? qgcPal.colorGreen : (mosimOrchestrator.reasonCode === "idle" ? qgcPal.windowShade : qgcPal.colorOrange)
                QGCLabel {
                    anchors.fill: parent
                    anchors.margins: 5
                    text: mosimOrchestrator.statusText
                    elide: Text.ElideRight
                    color: qgcPal.buttonText
                }
            }

            TabBar {
                id: tabs
                Layout.fillWidth: true
                TabButton { text: "Run" }
                TabButton { text: "Telemetry" }
                TabButton { text: "Inject" }
                TabButton { text: "Displays" }
                TabButton { text: "Evidence" }
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
                        QGCLabel { text: "Experiment"; font.bold: true }
                        ComboBox {
                            id: profileBox
                            Layout.fillWidth: true
                            model: profiles
                            textRole: "label"
                            onActivated: {
                                controllerBox.currentIndex = profiles[currentIndex].controller === "cascade_pid" ? 1 : 0
                                vehicleBox.currentIndex = profiles[currentIndex].count === 3 ? 1 : 0
                                injectionVehicle.currentIndex = 0
                            }
                        }
                        QGCLabel { text: "Controller" }
                        ComboBox {
                            id: controllerBox
                            Layout.fillWidth: true
                            model: controllers
                            textRole: "label"
                            delegate: ItemDelegate { width: controllerBox.width; text: modelData.label; enabled: modelData.enabled }
                        }
                        QGCLabel { text: "UAV count" }
                        ComboBox {
                            id: vehicleBox
                            Layout.fillWidth: true
                            model: vehicleCounts
                            textRole: "label"
                            delegate: ItemDelegate { width: vehicleBox.width; text: modelData.label; enabled: modelData.enabled }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton {
                                text: "Prepare"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy && profiles[profileBox.currentIndex].enabled && vehicleCounts[vehicleBox.currentIndex].enabled
                                onClicked: mosimOrchestrator.prepareRun(profiles[profileBox.currentIndex].path,
                                                                        profiles[profileBox.currentIndex].controller,
                                                                        profiles[profileBox.currentIndex].count, 0)
                            }
                            QGCButton { text: "Start"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy && mosimOrchestrator.runId !== ""; onClicked: mosimOrchestrator.startRun() }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton { text: "Stop"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy && mosimOrchestrator.runId !== ""; onClicked: mosimOrchestrator.stopRun() }
                            QGCButton { text: "Reset"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy && mosimOrchestrator.runId !== ""; onClicked: mosimOrchestrator.resetRun() }
                        }
                        QGCButton {
                            text: "Emergency stop"
                            Layout.fillWidth: true
                            enabled: !mosimOrchestrator.busy && mosimOrchestrator.runId !== ""
                            onClicked: mosimOrchestrator.stopRun()
                        }
                        QGCLabel { text: "Run ID"; font.bold: true }
                        QGCLabel { text: mosimOrchestrator.runId || "-"; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
                        QGCLabel { text: "Lifecycle: " + mosimOrchestrator.lifecycleState }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: 10
                        readonly property var activeVehicle: QGroundControl.multiVehicleManager.activeVehicle
                        QGCLabel { text: "QGC vehicle telemetry"; font.bold: true }
                        QGCLabel { text: "Vehicles: " + QGroundControl.multiVehicleManager.vehicles.count }
                        QGCLabel { text: "Armed: " + (activeVehicle ? activeVehicle.armed : false) }
                        QGCLabel { text: "Mode: " + (activeVehicle ? activeVehicle.flightMode : "-") }
                        QGCLabel { text: "Altitude: " + (activeVehicle ? activeVehicle.altitudeRelative.valueString : "-") }
                        QGCLabel { text: "Ground speed: " + (activeVehicle ? activeVehicle.groundSpeed.valueString : "-") }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton { text: "Run state"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.refreshState() }
                            QGCButton { text: "Telemetry"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.refreshTelemetry() }
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: 10
                        QGCLabel { text: "Target UAV" }
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
                        QGCLabel { text: "Wind speed (m/s)" }
                        Slider { id: windSlider; Layout.fillWidth: true; from: 0; to: 20; stepSize: 0.5 }
                        QGCLabel { text: windSlider.value.toFixed(1) }
                        QGCButton { text: "Apply wind"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.applyWind(injectionVehicle.currentText, windSlider.value) }
                        QGCLabel { text: "Motor effectiveness" }
                        RowLayout {
                            Layout.fillWidth: true
                            SpinBox { id: rotorIndex; from: 1; to: 4; value: 1 }
                            Slider { id: motorSlider; Layout.fillWidth: true; from: 0; to: 1; value: 1; stepSize: 0.05 }
                            QGCLabel { text: motorSlider.value.toFixed(2) }
                        }
                        QGCButton { text: "Apply motor"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.applyMotorEffectiveness(injectionVehicle.currentText, rotorIndex.value, motorSlider.value) }
                        RowLayout {
                            Layout.fillWidth: true
                            QGCButton { text: "Restore wind"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.restoreInjection(injectionVehicle.currentText, "wind_speed_mps") }
                            QGCButton { text: "Restore motor"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.restoreInjection(injectionVehicle.currentText, "motor_effectiveness", rotorIndex.value) }
                        }
                    }
                }

                ScrollView {
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        CheckBox { id: pointCloudDisplay; text: "RViz point cloud"; checked: true }
                        CheckBox { id: gridMapDisplay; text: "RViz grid map"; checked: true }
                        CheckBox { id: unrealDisplay; text: "Unreal"; checked: true }
                        CheckBox { id: mworksDisplay; text: "MWORKS result" }
                        QGCButton {
                            text: "Prepare displays"
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
                                text: "Attach"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy && mosimOrchestrator.displaySessionId.length > 0
                                onClicked: mosimOrchestrator.attachDisplays()
                            }
                            QGCButton {
                                text: "Detach"
                                Layout.fillWidth: true
                                enabled: !mosimOrchestrator.busy && mosimOrchestrator.displaySessionId.length > 0
                                onClicked: mosimOrchestrator.detachDisplays()
                            }
                        }
                    }
                }

                ColumnLayout {
                    spacing: 10
                    QGCLabel { text: "Profile hash"; font.bold: true }
                    QGCLabel { text: mosimOrchestrator.profileHash || "-"; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
                    RowLayout {
                        Layout.fillWidth: true
                        QGCButton { text: "Open model"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.openModelContext() }
                        QGCButton { text: "Result packet"; Layout.fillWidth: true; enabled: !mosimOrchestrator.busy; onClicked: mosimOrchestrator.getResultPacket() }
                    }
                    TextArea {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        readOnly: true
                        wrapMode: TextEdit.WrapAnywhere
                        text: mosimOrchestrator.lastResponse
                    }
                }
            }
        }
    }
}
