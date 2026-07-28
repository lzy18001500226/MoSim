import QtQuick

import QGroundControl.Controls
import QGroundControl.ScreenTools

Item {
    id: root

    // The component deliberately receives plain data. It never discovers a
    // process or reads UE state, so live and rosbag sources share one map path.
    required property var mapConfig
    required property var runManifest
    required property var mapState
    required property string runId

    property real minZoom: 1.0
    property real maxZoom: 12.0
    property real zoomFactor: minZoom
    property int maxTrackPoints: 1200
    property var actualTracksByVehicle: ({})
    property int actualTrackRevision: 0
    property string actualTrackRunId: ""
    property bool showVehicles: true
    property bool showActualTracks: true
    property bool showExpectedPath: true
    property bool showFuturePath: true
    property bool showTaskBoundary: true
    property bool showFormationTarget: true

    readonly property var bounds: mapConfig.world_bounds_m || ({})
    readonly property bool mapConfigValid: mapConfig.enabled === true
            && isFinite(Number(bounds.min_x_m)) && isFinite(Number(bounds.max_x_m))
            && isFinite(Number(bounds.min_y_m)) && isFinite(Number(bounds.max_y_m))
            && Number(bounds.min_x_m) < Number(bounds.max_x_m)
            && Number(bounds.min_y_m) < Number(bounds.max_y_m)
    readonly property real worldWidthM: Number(bounds.max_x_m) - Number(bounds.min_x_m)
    readonly property real worldHeightM: Number(bounds.max_y_m) - Number(bounds.min_y_m)
    readonly property real imageAspectRatio: factoryImage.status === Image.Ready
            && factoryImage.sourceSize.width > 0 && factoryImage.sourceSize.height > 0
        ? factoryImage.sourceSize.width / factoryImage.sourceSize.height
        : 2048.0 / 800.0
    readonly property var mapMetadata: mapState.map || ({})
    readonly property var mapTransport: mapState.transport || ({})
    readonly property bool manifestMatchesRun: runId.length > 0 && runManifest.run_id === runId
            && String(runManifest.experiment_profile_id || "").length > 0
            && String(runManifest.experiment_profile_hash || "").length > 0
    readonly property string frozenMapSnapshotHash: String(runManifest.operator_map_snapshot_hash || "")
    readonly property string configuredMapSnapshotHash: String(mapConfig.operator_map_snapshot_hash || "")
    readonly property string stateMapSnapshotHash: String(mapMetadata.operator_map_snapshot_hash || "")
    readonly property bool mapSnapshotHashMatches: frozenMapSnapshotHash.length > 0
            && configuredMapSnapshotHash === frozenMapSnapshotHash
            && stateMapSnapshotHash === frozenMapSnapshotHash
    readonly property bool mapIdentityMatches: String(mapState.schema || "") === "mosim.operator_map_state.v1"
            && manifestMatchesRun
            && String(mapState.run_id || "") === runId
            && String(mapState.profile_id || "") === String(runManifest.experiment_profile_id || "")
            && String(mapState.profile_hash || "") === String(runManifest.experiment_profile_hash || "")
            && mapSnapshotHashMatches
            && String(mapMetadata.map_id || "") === String(mapConfig.map_id || "")
            && String(mapMetadata.map_version || "") === String(mapConfig.map_version || "")
            && String(mapMetadata.asset_sha256 || "") === String(mapConfig.asset_sha256 || "")
            && String(mapMetadata.world_frame || "") === String(mapConfig.world_frame || "")
            && String(mapMetadata.coordinate_contract_id || "")
                    === String(mapConfig.coordinate_contract_id || "")
    readonly property bool mapTransportFresh: {
        var mode = String(mapTransport.mode || "")
        var sequence = Number(mapTransport.sequence || 0)
        if (sequence <= 0)
            return false
        if (mode === "live_ros1") {
            var receivedAt = Number(mapTransport.received_at_unix_s || 0)
            return receivedAt > 0 && Math.abs(Date.now() / 1000.0 - receivedAt) <= 2.5
        }
        if (mode === "rosbag_replay")
            return ["playing", "paused", "completed"].indexOf(String(mapTransport.playback_state || "")) >= 0
        return false
    }
    readonly property bool mapStateReady: mapConfigValid && mapIdentityMatches && mapTransportFresh
            && String(mapMetadata.coordinate_contract_status || "") === "verified"
    readonly property var vehicles: mapStateReady && mapState.vehicles && mapState.vehicles.length !== undefined
        ? mapState.vehicles : []
    readonly property string taskPathSummary: taskPathStatusText()

    function clamp(value, lower, upper) {
        return Math.max(lower, Math.min(value, upper))
    }

    function resetTracks() {
        actualTracksByVehicle = ({})
        actualTrackRevision += 1
        actualTrackRunId = runId
    }

    function validWorldPoint(point) {
        if (!point || !mapConfigValid)
            return false
        var x = Number(point.x)
        var y = Number(point.y)
        return isFinite(x) && isFinite(y)
                && x >= Number(bounds.min_x_m) && x <= Number(bounds.max_x_m)
                && y >= Number(bounds.min_y_m) && y <= Number(bounds.max_y_m)
    }

    function vehicleMapPositionValid(vehicle) {
        return vehicle && vehicle.state && vehicle.state.connected === true
                && validWorldPoint(vehicle.state.position)
    }

    function vehicleYawDegrees(vehicle) {
        if (!vehicle || !vehicle.state || !vehicle.state.orientation)
            return 0
        var q = vehicle.state.orientation
        var yaw = Math.atan2(2.0 * (Number(q.w) * Number(q.z) + Number(q.x) * Number(q.y)),
                             1.0 - 2.0 * (Number(q.y) * Number(q.y) + Number(q.z) * Number(q.z)))
        return yaw * 180.0 / Math.PI
    }

    function imageXForWorld(worldX) {
        return (Number(worldX) - Number(bounds.min_x_m)) / worldWidthM * factoryImage.width
    }

    function imageYForWorld(worldY) {
        return (Number(bounds.max_y_m) - Number(worldY)) / worldHeightM * factoryImage.height
    }

    function appendActualTracks() {
        if (!mapStateReady)
            return
        if (actualTrackRunId !== runId)
            resetTracks()
        var nextTracks = actualTracksByVehicle
        var changed = false
        for (var index = 0; index < vehicles.length; ++index) {
            var vehicle = vehicles[index]
            if (!vehicleMapPositionValid(vehicle))
                continue
            var id = String(vehicle.vehicle_id || ("uav" + (index + 1)))
            var points = nextTracks[id] || []
            var point = {
                x: Number(vehicle.state.position.x),
                y: Number(vehicle.state.position.y)
            }
            var previous = points.length > 0 ? points[points.length - 1] : null
            if (!previous || Math.hypot(point.x - previous.x, point.y - previous.y) >= 0.05) {
                points = points.slice(Math.max(0, points.length - (maxTrackPoints - 1)))
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

    function taskPath(kind) {
        if (!mapStateReady)
            return ({})
        var paths = mapState.task_paths || ({})
        var path = paths[kind] || ({})
        if (path.status !== "available" || !path.points || path.points.length < 2)
            return ({})
        if (path.run_id !== undefined && String(path.run_id) !== runId)
            return ({})
        if (kind === "future" && String(mapTransport.mode || "") === "live_ros1"
                && Date.now() / 1000.0 - Number(path.updated_at || 0) > 5.0)
            return ({})
        for (var index = 0; index < path.points.length; ++index) {
            if (!validWorldPoint(path.points[index]))
                return ({})
        }
        return path
    }

    function taskPathLabel(kind) {
        var semantics = String(taskPath(kind).semantics || "")
        if (semantics === "formation_center_reference")
            return "编队中心预期"
        if (semantics === "exploration_target_sequence")
            return "探索目标序列"
        if (semantics === "planner_sampled_future_trajectory")
            return "规划器未来轨迹"
        return kind === "future" ? "未来轨迹" : "任务预期轨迹"
    }

    function taskPathStatusText() {
        if (!mapStateReady)
            return mapDataGateText()
        var labels = []
        if (taskPath("expected").status === "available")
            labels.push(taskPathLabel("expected") + "已接收")
        if (taskPath("future").status === "available")
            labels.push(taskPathLabel("future") + "已接收")
        if (Object.keys(actualTracksByVehicle).length > 0)
            labels.push(String(mapTransport.mode || "") === "rosbag_replay" ? "实际轨迹回放中" : "实际轨迹实时记录中")
        return labels.length > 0 ? labels.join("；") : "等待任务轨迹与飞机位置"
    }

    function mapDataGateText() {
        if (!mapConfigValid)
            return "等待地图配置"
        if (!manifestMatchesRun)
            return "等待当前运行清单"
        if (String(mapState.run_id || "") !== runId)
            return "等待当前运行地图数据"
        if (!mapSnapshotHashMatches)
            return "地图快照身份不匹配"
        if (!mapIdentityMatches)
            return "地图或 Profile 身份不匹配"
        if (String(mapMetadata.coordinate_contract_status || "") !== "verified")
            return "坐标契约待验证"
        if (String(mapTransport.mode || "") === "live_ros1")
            return "实时地图数据已过期"
        if (String(mapTransport.mode || "") === "rosbag_replay")
            return "回放地图数据未就绪"
        return "等待有效地图数据"
    }

    function explorationBoundary() {
        if (!mapStateReady)
            return null
        var boundary = mapState.task_boundary || null
        if (!boundary)
            return null
        var minX = Number(boundary.min_x_m)
        var maxX = Number(boundary.max_x_m)
        var minY = Number(boundary.min_y_m)
        var maxY = Number(boundary.max_y_m)
        if (!isFinite(minX) || !isFinite(maxX) || !isFinite(minY) || !isFinite(maxY)
                || minX >= maxX || minY >= maxY
                || !validWorldPoint({ x: minX, y: minY })
                || !validWorldPoint({ x: maxX, y: maxY }))
            return null
        return { min_x_m: minX, max_x_m: maxX, min_y_m: minY, max_y_m: maxY }
    }

    function formationTarget() {
        if (!mapStateReady)
            return null
        var formation = mapState.formation_target || null
        var target = formation ? formation.target_center_xy_m : null
        if (!target || target.length !== 2 || !validWorldPoint({ x: target[0], y: target[1] }))
            return null
        return { x: Number(target[0]), y: Number(target[1]) }
    }

    function vehicleColor(index) {
        var colors = ["#00d084", "#ffb020", "#4aa3ff", "#f05d9b", "#9b7cff", "#21c7d9", "#ffffff", "#ff7043", "#8bc34a"]
        return colors[index % colors.length]
    }

    function paintActualTracks(canvas) {
        var revision = actualTrackRevision
        var context = canvas.getContext("2d")
        context.reset()
        context.lineWidth = 2
        context.lineJoin = "round"
        context.lineCap = "round"
        var ids = Object.keys(actualTracksByVehicle).sort()
        for (var idIndex = 0; idIndex < ids.length; ++idIndex) {
            var points = actualTracksByVehicle[ids[idIndex]]
            if (!points || points.length < 2)
                continue
            context.beginPath()
            context.strokeStyle = vehicleColor(idIndex)
            context.moveTo(imageXForWorld(points[0].x), imageYForWorld(points[0].y))
            for (var pointIndex = 1; pointIndex < points.length; ++pointIndex)
                context.lineTo(imageXForWorld(points[pointIndex].x), imageYForWorld(points[pointIndex].y))
            context.stroke()
        }
    }

    function paintTaskPaths(canvas) {
        var context = canvas.getContext("2d")
        context.reset()
        var kinds = ["expected", "future"]
        var colors = ["#ffb020", "#4aa3ff"]
        for (var kindIndex = 0; kindIndex < kinds.length; ++kindIndex) {
            if ((kinds[kindIndex] === "expected" && !showExpectedPath)
                    || (kinds[kindIndex] === "future" && !showFuturePath))
                continue
            var path = taskPath(kinds[kindIndex])
            var points = path.points || []
            if (points.length < 2)
                continue
            context.beginPath()
            context.strokeStyle = colors[kindIndex]
            context.lineWidth = kinds[kindIndex] === "future" ? 3 : 2
            context.lineJoin = "round"
            context.lineCap = "round"
            context.moveTo(imageXForWorld(Number(points[0].x)), imageYForWorld(Number(points[0].y)))
            for (var pointIndex = 1; pointIndex < points.length; ++pointIndex)
                context.lineTo(imageXForWorld(Number(points[pointIndex].x)),
                               imageYForWorld(Number(points[pointIndex].y)))
            context.stroke()
        }
    }

    function paintTaskBoundary(canvas) {
        var context = canvas.getContext("2d")
        context.reset()
        var boundary = explorationBoundary()
        if (!boundary)
            return
        var left = imageXForWorld(boundary.min_x_m)
        var right = imageXForWorld(boundary.max_x_m)
        var top = imageYForWorld(boundary.max_y_m)
        var bottom = imageYForWorld(boundary.min_y_m)
        context.strokeStyle = "#20c7b7"
        context.lineWidth = 3
        context.strokeRect(left, top, right - left, bottom - top)
    }

    function paintFormationTarget(canvas) {
        var context = canvas.getContext("2d")
        context.reset()
        var target = formationTarget()
        if (!target)
            return
        var x = imageXForWorld(target.x)
        var y = imageYForWorld(target.y)
        var radius = Math.max(7, Math.min(13, factoryImage.width / 70))
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

    function niceScaleMeters(targetMeters) {
        if (!isFinite(targetMeters) || targetMeters <= 0)
            return 1
        var base = Math.pow(10, Math.floor(Math.log(targetMeters) / Math.LN10))
        var normalized = targetMeters / base
        var multiplier = normalized <= 1 ? 1 : (normalized <= 2 ? 2 : (normalized <= 5 ? 5 : 10))
        return multiplier * base
    }

    function zoomAt(viewX, viewY, wheelDelta) {
        var oldZoom = zoomFactor
        var nextZoom = clamp(oldZoom * (wheelDelta > 0 ? 1.2 : 1.0 / 1.2), minZoom, maxZoom)
        if (Math.abs(nextZoom - oldZoom) < 0.0001)
            return
        var imageX = mapFlickable.contentX + viewX - factoryImage.x
        var imageY = mapFlickable.contentY + viewY - factoryImage.y
        var imageRatioX = clamp(imageX / factoryImage.width, 0, 1)
        var imageRatioY = clamp(imageY / factoryImage.height, 0, 1)
        zoomFactor = nextZoom
        Qt.callLater(function() {
            var targetX = factoryImage.x + imageRatioX * factoryImage.width - viewX
            var targetY = factoryImage.y + imageRatioY * factoryImage.height - viewY
            mapFlickable.contentX = clamp(targetX, 0, Math.max(0, mapFlickable.contentWidth - mapFlickable.width))
            mapFlickable.contentY = clamp(targetY, 0, Math.max(0, mapFlickable.contentHeight - mapFlickable.height))
        })
    }

    function fitMap() {
        zoomFactor = minZoom
        Qt.callLater(function() {
            mapFlickable.contentX = Math.max(0, (mapFlickable.contentWidth - mapFlickable.width) / 2)
            mapFlickable.contentY = Math.max(0, (mapFlickable.contentHeight - mapFlickable.height) / 2)
        })
    }

    onRunIdChanged: resetTracks()
    onMapStateChanged: appendActualTracks()
    onWidthChanged: Qt.callLater(fitMap)
    onHeightChanged: Qt.callLater(fitMap)

    Rectangle {
        anchors.fill: parent
        color: "#15191d"
    }

    Flickable {
        id: mapFlickable
        anchors.fill: parent
        clip: true
        interactive: factoryImage.width > width || factoryImage.height > height
        boundsBehavior: Flickable.StopAtBounds
        contentWidth: Math.max(width, mapSurface.width)
        contentHeight: Math.max(height, mapSurface.height)

        Item {
            id: mapSurface
            width: Math.max(mapFlickable.width, factoryImage.width)
            height: Math.max(mapFlickable.height, factoryImage.height)

            Image {
                id: factoryImage
                readonly property real fittedWidth: Math.min(mapFlickable.width,
                    mapFlickable.height * root.imageAspectRatio)
                width: Math.max(1, fittedWidth * root.zoomFactor)
                height: width / root.imageAspectRatio
                anchors.centerIn: parent
                source: String(root.mapConfig.resource_url || "")
                fillMode: Image.Stretch
                smooth: true
                mipmap: true
                cache: true
                onStatusChanged: Qt.callLater(root.fitMap)
            }

            Canvas {
                id: taskBoundaryCanvas
                x: factoryImage.x
                y: factoryImage.y
                width: factoryImage.width
                height: factoryImage.height
                visible: root.showTaskBoundary && root.explorationBoundary() !== null
                z: 1
                property int mapSequence: Number(root.mapTransport.sequence || 0)
                onMapSequenceChanged: requestPaint()
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()
                onPaint: root.paintTaskBoundary(this)
            }

            Canvas {
                id: taskPathCanvas
                x: factoryImage.x
                y: factoryImage.y
                width: factoryImage.width
                height: factoryImage.height
                visible: root.mapStateReady && (root.showExpectedPath || root.showFuturePath)
                z: 2
                property int mapSequence: Number(root.mapTransport.sequence || 0)
                onMapSequenceChanged: requestPaint()
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()
                onPaint: root.paintTaskPaths(this)
            }

            Canvas {
                id: formationTargetCanvas
                x: factoryImage.x
                y: factoryImage.y
                width: factoryImage.width
                height: factoryImage.height
                visible: root.showFormationTarget && root.formationTarget() !== null
                z: 3
                property int mapSequence: Number(root.mapTransport.sequence || 0)
                onMapSequenceChanged: requestPaint()
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()
                onPaint: root.paintFormationTarget(this)
            }

            Canvas {
                id: actualTrackCanvas
                x: factoryImage.x
                y: factoryImage.y
                width: factoryImage.width
                height: factoryImage.height
                visible: root.mapStateReady && root.showActualTracks
                z: 4
                property int trackRevision: root.actualTrackRevision
                onTrackRevisionChanged: requestPaint()
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()
                onPaint: root.paintActualTracks(this)
            }

            Repeater {
                model: root.showVehicles ? root.vehicles : []
                delegate: Item {
                    required property var modelData
                    required property int index
                    property var vehicle: modelData
                    visible: root.mapStateReady && root.vehicleMapPositionValid(vehicle)
                    width: 22
                    height: 22
                    z: 5
                    rotation: 90 - root.vehicleYawDegrees(vehicle)
                    x: factoryImage.x + root.imageXForWorld(Number(vehicle.state.position.x)) - width / 2
                    y: factoryImage.y + root.imageYForWorld(Number(vehicle.state.position.y)) - height / 2

                    Canvas {
                        anchors.fill: parent
                        onPaint: {
                            var context = getContext("2d")
                            context.reset()
                            context.beginPath()
                            context.moveTo(width, height / 2)
                            context.lineTo(2, 2)
                            context.lineTo(6, height / 2)
                            context.lineTo(2, height - 2)
                            context.closePath()
                            context.fillStyle = root.vehicleColor(index)
                            context.fill()
                            context.strokeStyle = "#ffffff"
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
                root.zoomAt(wheel.x, wheel.y, wheel.angleDelta.y)
                wheel.accepted = true
            }
        }
    }

    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.margins: ScreenTools.defaultFontPixelWidth
        width: mapTitle.implicitWidth + ScreenTools.defaultFontPixelWidth * 2
        height: mapTitle.implicitHeight + ScreenTools.defaultFontPixelHeight
        color: "#bf111820"
        border.color: "#7d8a94"
        border.width: 1

        Text {
            id: mapTitle
            anchors.centerIn: parent
            text: String(root.mapConfig.display_name || "Factory L2")
            color: "#ffffff"
            font.pixelSize: ScreenTools.defaultFontPixelHeight
        }
    }

    Row {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: ScreenTools.defaultFontPixelWidth
        spacing: 4

        QGCButton { text: "-"; onClicked: root.zoomAt(root.width / 2, root.height / 2, -1) }
        QGCButton { text: "适配"; onClicked: root.fitMap() }
        QGCButton { text: "+"; onClicked: root.zoomAt(root.width / 2, root.height / 2, 1) }
    }

    Column {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: ScreenTools.defaultFontPixelWidth
        spacing: 4
        visible: root.mapConfigValid

        readonly property real metersPerPixel: root.worldWidthM / factoryImage.width
        readonly property real scaleMeters: root.niceScaleMeters(105 * metersPerPixel)
        readonly property real scaleWidth: scaleMeters / metersPerPixel

        Text {
            text: scaleMeters >= 1000 ? (scaleMeters / 1000).toFixed(1) + " km" : scaleMeters.toFixed(0) + " m"
            color: "#ffffff"
            font.pixelSize: ScreenTools.defaultFontPixelHeight * 0.9
        }
        Rectangle {
            width: Math.max(24, Math.min(150, parent.scaleWidth))
            height: 3
            color: "#ffffff"
        }
    }

    Column {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: ScreenTools.defaultFontPixelWidth
        spacing: 3

        Text { text: "N"; color: "#ffffff"; font.bold: true; horizontalAlignment: Text.AlignHCenter; width: 24 }
        Rectangle {
            width: 2
            height: 24
            x: 11
            color: "#f05d9b"
        }
        Text { text: "X ->    Y ^"; color: "#d7e0e5"; font.pixelSize: ScreenTools.defaultFontPixelHeight * 0.8 }
    }

    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: ScreenTools.defaultFontPixelWidth
        spacing: ScreenTools.defaultFontPixelWidth
        visible: root.mapStateReady

        Repeater {
            model: [
                { label: "实际", color: "#00d084", visible: root.showActualTracks && Object.keys(root.actualTracksByVehicle).length > 0 },
                { label: root.taskPathLabel("expected"), color: "#ffb020", visible: root.showExpectedPath && root.taskPath("expected").status === "available" },
                { label: root.taskPathLabel("future"), color: "#4aa3ff", visible: root.showFuturePath && root.taskPath("future").status === "available" },
                { label: "编队目标", color: "#f05d9b", visible: root.showFormationTarget && root.formationTarget() !== null }
            ]
            delegate: Row {
                required property var modelData
                visible: modelData.visible
                spacing: 4
                Rectangle { width: 14; height: 3; anchors.verticalCenter: parent.verticalCenter; color: modelData.color }
                Text { text: modelData.label; color: "#ffffff"; font.pixelSize: ScreenTools.defaultFontPixelHeight * 0.85 }
            }
        }
    }

    Text {
        anchors.centerIn: parent
        visible: !root.mapConfigValid || factoryImage.status === Image.Error || !root.mapStateReady
        text: !root.mapConfigValid ? "等待地图配置"
              : (factoryImage.status === Image.Error ? "工厂地图资源不可用" : root.mapDataGateText())
        color: "#f4b183"
        font.pixelSize: ScreenTools.largeFontPixelSize
    }
}
