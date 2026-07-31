import QtQuick
import QtPositioning

import QGroundControl

Item {
    required property var map
    required property var mapConfig
    required property var runManifest
    required property var mapState
    required property string runId

    property int maxTrackPoints: 1200
    property var actualTracksByVehicle: ({})
    property int actualTrackRevision: 0
    property string actualTrackRunId: ""
    property string actualTrackSourceIdentity: ""
    property int actualTrackLastSequence: 0

    readonly property var anchorConfig: mapConfig.simulation_geodetic_anchor || ({})
    readonly property var bounds: mapConfig.world_bounds_m || ({})
    readonly property var imageCoordinateContract: mapConfig.image_coordinate_contract || ({})
    readonly property var imageSizePx: imageCoordinateContract.image_size_px || ({})
    readonly property var pixelToWorldMatrix: imageCoordinateContract.pixel_to_world_3x3 || []
    readonly property real imageWidthPx: Number(imageSizePx.width || 0)
    readonly property real imageHeightPx: Number(imageSizePx.height || 0)
    readonly property bool imageCoordinateContractValid: validImageCoordinateContract()
    readonly property bool loadedImageSizeMatchesContract: factoryImage.status !== Image.Ready
            || (Math.round(factoryImage.sourceSize.width) === Math.round(imageWidthPx)
                    && Math.round(factoryImage.sourceSize.height) === Math.round(imageHeightPx))
    readonly property var scenarioConfig: runManifest.scenario_snapshot || ({})
    readonly property var configuredBoundary: mapConfig.indoor_task_overlay_bounds_m || ({})
    readonly property var scenarioBoundary: scenarioConfig.exploration_boundary || ({})
    readonly property var mapMetadata: mapState.map || ({})
    readonly property var mapTransport: mapState.transport || ({})
    readonly property var mapDataStatus: mapState.map_data_status || ({})
    readonly property string frozenMapSnapshotHash: String(runManifest.operator_map_snapshot_hash || "")
    readonly property bool manifestMatchesRun: runId.length > 0 && String(runManifest.run_id || "") === runId
            && String(runManifest.experiment_profile_id || "").length > 0
            && String(runManifest.experiment_profile_hash || "").length > 0
    readonly property bool mapIdentityMatches: String(mapState.schema || "") === "mosim.operator_map_state.v1"
            && manifestMatchesRun
            && String(mapState.run_id || "") === runId
            && String(mapState.profile_id || "") === String(runManifest.experiment_profile_id || "")
            && String(mapState.profile_hash || "") === String(runManifest.experiment_profile_hash || "")
            && String(mapMetadata.operator_map_snapshot_hash || "") === frozenMapSnapshotHash
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
    readonly property bool mapStateReady: mapIdentityMatches && mapTransportFresh
            && String(mapMetadata.coordinate_contract_status || "") === "verified"
            && String(mapDataStatus.state || "accepted") === "accepted"
    readonly property var vehicles: mapStateReady && mapState.vehicles && mapState.vehicles.length !== undefined
        ? mapState.vehicles : []
    readonly property var liveBoundary: mapStateReady && mapState.task_boundary ? mapState.task_boundary : ({})
    readonly property bool liveBoundaryValid:
        isFinite(Number(liveBoundary.min_x_m))
        && isFinite(Number(liveBoundary.max_x_m))
        && isFinite(Number(liveBoundary.min_y_m))
        && isFinite(Number(liveBoundary.max_y_m))
        && Number(liveBoundary.min_x_m) < Number(liveBoundary.max_x_m)
        && Number(liveBoundary.min_y_m) < Number(liveBoundary.max_y_m)
    readonly property bool scenarioBoundaryValid:
        isFinite(Number(scenarioBoundary.min_x_m))
        && isFinite(Number(scenarioBoundary.max_x_m))
        && isFinite(Number(scenarioBoundary.min_y_m))
        && isFinite(Number(scenarioBoundary.max_y_m))
        && Number(scenarioBoundary.min_x_m) < Number(scenarioBoundary.max_x_m)
        && Number(scenarioBoundary.min_y_m) < Number(scenarioBoundary.max_y_m)
    readonly property var explorationBoundary: liveBoundaryValid ? liveBoundary
        : (scenarioBoundaryValid ? scenarioBoundary : configuredBoundary)
    readonly property bool explorationBoundaryValid:
        isFinite(Number(explorationBoundary.min_x_m))
        && isFinite(Number(explorationBoundary.max_x_m))
        && isFinite(Number(explorationBoundary.min_y_m))
        && isFinite(Number(explorationBoundary.max_y_m))
        && Number(explorationBoundary.min_x_m) < Number(explorationBoundary.max_x_m)
        && Number(explorationBoundary.min_y_m) < Number(explorationBoundary.max_y_m)
    readonly property var mapCenter: QtPositioning.coordinate(
        Number(anchorConfig.latitude_deg || 0),
        Number(anchorConfig.longitude_deg || 0),
        Number(anchorConfig.altitude_m || 0))
    readonly property var imageWorldBounds: imageWorldBoundsForPixels()
    readonly property var northWest: coordinateForWorld(
        Number(imageWorldBounds.min_x_m || 0), Number(imageWorldBounds.max_y_m || 0))
    readonly property var southEast: coordinateForWorld(
        Number(imageWorldBounds.max_x_m || 0), Number(imageWorldBounds.min_y_m || 0))
    readonly property point northWestPixel: {
        var centerDependency = map.center
        var zoomDependency = map.zoomLevel
        return map.fromCoordinate(northWest, false)
    }
    readonly property point southEastPixel: {
        var centerDependency = map.center
        var zoomDependency = map.zoomLevel
        return map.fromCoordinate(southEast, false)
    }

    visible: mapConfig.enabled === true && imageCoordinateContractValid && loadedImageSizeMatchesContract
    x: Math.min(northWestPixel.x, southEastPixel.x)
    y: Math.min(northWestPixel.y, southEastPixel.y)
    width: Math.abs(southEastPixel.x - northWestPixel.x)
    height: Math.abs(southEastPixel.y - northWestPixel.y)
    // Above the local opaque backdrop and map tiles, below mission visuals.
    z: 2

    function coordinateForWorld(worldX, worldY) {
        var north = mapCenter.atDistanceAndAzimuth(Math.abs(worldY), worldY >= 0 ? 0 : 180)
        return north.atDistanceAndAzimuth(Math.abs(worldX), worldX >= 0 ? 90 : 270)
    }

    function mapPointForWorld(worldX, worldY) {
        var point = map.fromCoordinate(coordinateForWorld(worldX, worldY), false)
        return Qt.point(point.x - root.x, point.y - root.y)
    }

    function validWorldPoint(point) {
        if (!point)
            return false
        var x = Number(point.x)
        var y = Number(point.y)
        return isFinite(x) && isFinite(y)
                && x >= Number(bounds.min_x_m) && x <= Number(bounds.max_x_m)
                && y >= Number(bounds.min_y_m) && y <= Number(bounds.max_y_m)
    }

    function vehicleMapPositionValid(vehicle) {
        return vehicle && vehicle.state && vehicle.state.connected === true && validWorldPoint(vehicle.state.position)
    }

    function vehicleYawDegrees(vehicle) {
        if (!vehicle || !vehicle.state || !vehicle.state.orientation)
            return 0
        var q = vehicle.state.orientation
        var yaw = Math.atan2(2.0 * (Number(q.w) * Number(q.z) + Number(q.x) * Number(q.y)),
                             1.0 - 2.0 * (Number(q.y) * Number(q.y) + Number(q.z) * Number(q.z)))
        return yaw * 180.0 / Math.PI
    }

    function vehicleColor(index) {
        var colors = ["#00d084", "#ffb020", "#4aa3ff", "#f05d9b", "#9b7cff", "#21c7d9", "#ffffff", "#ff7043", "#8bc34a"]
        return colors[index % colors.length]
    }

    function resetTracks() {
        actualTracksByVehicle = ({})
        actualTrackRevision += 1
        actualTrackRunId = runId
        actualTrackSourceIdentity = String(mapTransport.mode || "") + "|" + String(mapTransport.bag_id || "")
        actualTrackLastSequence = 0
    }

    function appendActualTracks() {
        if (!mapStateReady)
            return
        var sourceIdentity = String(mapTransport.mode || "") + "|" + String(mapTransport.bag_id || "")
        var sequence = Number(mapTransport.sequence || 0)
        if (actualTrackRunId !== runId || actualTrackSourceIdentity !== sourceIdentity
                || (actualTrackLastSequence > 0 && sequence > 0 && sequence < actualTrackLastSequence))
            resetTracks()
        var nextTracks = actualTracksByVehicle
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
        actualTrackLastSequence = Math.max(actualTrackLastSequence, sequence)
    }

    function taskPath(kind) {
        if (!mapStateReady)
            return ({})
        var path = (mapState.task_paths || ({}))[kind] || ({})
        if (path.status !== "available" || !path.points || path.points.length < 2)
            return ({})
        if (path.run_id !== undefined && String(path.run_id) !== runId)
            return ({})
        for (var index = 0; index < path.points.length; ++index) {
            if (!validWorldPoint(path.points[index]))
                return ({})
        }
        return path
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
            var first = mapPointForWorld(points[0].x, points[0].y)
            context.beginPath()
            context.strokeStyle = vehicleColor(idIndex)
            context.moveTo(first.x, first.y)
            for (var pointIndex = 1; pointIndex < points.length; ++pointIndex) {
                var point = mapPointForWorld(points[pointIndex].x, points[pointIndex].y)
                context.lineTo(point.x, point.y)
            }
            context.stroke()
        }
    }

    function paintTaskPaths(canvas) {
        var context = canvas.getContext("2d")
        context.reset()
        var kinds = ["expected", "future"]
        var colors = ["#ffb020", "#4aa3ff"]
        for (var kindIndex = 0; kindIndex < kinds.length; ++kindIndex) {
            var path = taskPath(kinds[kindIndex])
            var points = path.points || []
            if (points.length < 2)
                continue
            var first = mapPointForWorld(Number(points[0].x), Number(points[0].y))
            context.beginPath()
            context.strokeStyle = colors[kindIndex]
            context.lineWidth = kinds[kindIndex] === "future" ? 3 : 2
            context.lineJoin = "round"
            context.lineCap = "round"
            context.moveTo(first.x, first.y)
            for (var pointIndex = 1; pointIndex < points.length; ++pointIndex) {
                var point = mapPointForWorld(Number(points[pointIndex].x), Number(points[pointIndex].y))
                context.lineTo(point.x, point.y)
            }
            context.stroke()
        }
    }

    onMapStateChanged: appendActualTracks()
    onRunIdChanged: resetTracks()

    function validImageCoordinateContract() {
        if (String(imageCoordinateContract.schema || "") !== "mosim.operator_map_image_coordinate_contract.v1"
                || String(imageCoordinateContract.matrix_schema || "") !== "mosim.world_to_pixel.v1"
                || String(imageCoordinateContract.render_mode || "") !== "axis_aligned_image_rect_v1"
                || !isFinite(imageWidthPx) || !isFinite(imageHeightPx)
                || imageWidthPx <= 0 || imageHeightPx <= 0
                || !pixelToWorldMatrix || pixelToWorldMatrix.length !== 3)
            return false
        for (var row = 0; row < 3; ++row) {
            if (!pixelToWorldMatrix[row] || pixelToWorldMatrix[row].length !== 3)
                return false
            for (var column = 0; column < 3; ++column) {
                if (!isFinite(Number(pixelToWorldMatrix[row][column])))
                    return false
            }
        }
        return Math.abs(Number(pixelToWorldMatrix[2][0])) < 0.000000001
                && Math.abs(Number(pixelToWorldMatrix[2][1])) < 0.000000001
                && Math.abs(Number(pixelToWorldMatrix[2][2]) - 1.0) < 0.000000001
                && Math.abs(Number(pixelToWorldMatrix[0][1])) < 0.000000001
                && Math.abs(Number(pixelToWorldMatrix[1][0])) < 0.000000001
                && Math.abs(Number(pixelToWorldMatrix[0][0]) * Number(pixelToWorldMatrix[1][1])) > 0.000000001
    }

    function worldForImagePixel(pixelX, pixelY) {
        if (!imageCoordinateContractValid)
            return ({ x: NaN, y: NaN })
        var denominator = Number(pixelToWorldMatrix[2][0]) * Number(pixelX)
                + Number(pixelToWorldMatrix[2][1]) * Number(pixelY)
                + Number(pixelToWorldMatrix[2][2])
        if (!isFinite(denominator) || Math.abs(denominator) < 0.000000001)
            return ({ x: NaN, y: NaN })
        return {
            x: (Number(pixelToWorldMatrix[0][0]) * Number(pixelX)
                    + Number(pixelToWorldMatrix[0][1]) * Number(pixelY)
                    + Number(pixelToWorldMatrix[0][2])) / denominator,
            y: (Number(pixelToWorldMatrix[1][0]) * Number(pixelX)
                    + Number(pixelToWorldMatrix[1][1]) * Number(pixelY)
                    + Number(pixelToWorldMatrix[1][2])) / denominator
        }
    }

    function imageWorldBoundsForPixels() {
        if (!imageCoordinateContractValid)
            return bounds
        var corners = [
            worldForImagePixel(0, 0),
            worldForImagePixel(imageWidthPx, 0),
            worldForImagePixel(0, imageHeightPx),
            worldForImagePixel(imageWidthPx, imageHeightPx)
        ]
        var minX = corners[0].x
        var maxX = corners[0].x
        var minY = corners[0].y
        var maxY = corners[0].y
        for (var index = 1; index < corners.length; ++index) {
            minX = Math.min(minX, corners[index].x)
            maxX = Math.max(maxX, corners[index].x)
            minY = Math.min(minY, corners[index].y)
            maxY = Math.max(maxY, corners[index].y)
        }
        return { min_x_m: minX, max_x_m: maxX, min_y_m: minY, max_y_m: maxY }
    }

    Image {
        id: factoryImage
        anchors.fill: parent
        source: String(mapConfig.resource_url || "")
        fillMode: Image.Stretch
        smooth: true
        mipmap: true
        cache: true
    }

    Rectangle {
        readonly property var boundaryNorthWest: coordinateForWorld(
            Number(explorationBoundary.min_x_m), Number(explorationBoundary.max_y_m))
        readonly property var boundarySouthEast: coordinateForWorld(
            Number(explorationBoundary.max_x_m), Number(explorationBoundary.min_y_m))
        readonly property point boundaryNorthWestPixel: {
            var centerDependency = map.center
            var zoomDependency = map.zoomLevel
            return map.fromCoordinate(boundaryNorthWest, false)
        }
        readonly property point boundarySouthEastPixel: {
            var centerDependency = map.center
            var zoomDependency = map.zoomLevel
            return map.fromCoordinate(boundarySouthEast, false)
        }

        visible: explorationBoundaryValid
        x: Math.min(boundaryNorthWestPixel.x, boundarySouthEastPixel.x) - parent.x
        y: Math.min(boundaryNorthWestPixel.y, boundarySouthEastPixel.y) - parent.y
        width: Math.abs(boundarySouthEastPixel.x - boundaryNorthWestPixel.x)
        height: Math.abs(boundarySouthEastPixel.y - boundaryNorthWestPixel.y)
        color: "transparent"
        border.color: "#20c7b7"
        border.width: 3
    }

    Canvas {
        id: taskPathCanvas
        anchors.fill: parent
        z: 2
        visible: root.mapStateReady
        property int mapSequence: Number(root.mapTransport.sequence || 0)
        property real mapZoom: root.map.zoomLevel
        property var mapCenter: root.map.center
        onMapSequenceChanged: requestPaint()
        onMapZoomChanged: requestPaint()
        onMapCenterChanged: requestPaint()
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: root.paintTaskPaths(this)
    }

    Canvas {
        id: actualTrackCanvas
        anchors.fill: parent
        z: 3
        visible: root.mapStateReady
        property int trackRevision: root.actualTrackRevision
        property real mapZoom: root.map.zoomLevel
        property var mapCenter: root.map.center
        onTrackRevisionChanged: requestPaint()
        onMapZoomChanged: requestPaint()
        onMapCenterChanged: requestPaint()
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: root.paintActualTracks(this)
    }

    Repeater {
        model: root.vehicles
        delegate: Item {
            required property var modelData
            required property int index
            property var vehicle: modelData
            readonly property point mapPosition: root.vehicleMapPositionValid(vehicle)
                ? root.mapPointForWorld(Number(vehicle.state.position.x), Number(vehicle.state.position.y))
                : Qt.point(-width, -height)
            visible: root.mapStateReady && root.vehicleMapPositionValid(vehicle)
            width: 22
            height: 22
            z: 4
            rotation: 90 - root.vehicleYawDegrees(vehicle)
            x: mapPosition.x - width / 2
            y: mapPosition.y - height / 2

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
