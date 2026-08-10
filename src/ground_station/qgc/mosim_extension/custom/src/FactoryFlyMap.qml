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
    required property var runtimeStatus
    required property string runId

    property real minZoom: 1.0
    property real maxZoom: 48.0
    // `default_zoom_level` belongs to the native QGC PlanView. This custom
    // image surface uses a relative scale where 1.0 is the full-map fit.
    readonly property real defaultZoomFactor: minZoom
    property real zoomFactor: defaultZoomFactor
    property int maxTrackPoints: 1200
    property var actualTracksByVehicle: ({})
    property int actualTrackRevision: 0
    property string actualTrackRunId: ""
    property string actualTrackSourceIdentity: ""
    property int actualTrackLastSequence: 0
    property bool showVehicles: true
    property bool showActualTracks: true
    property bool showExpectedPath: true
    property bool showFuturePath: true
    property bool showTaskBoundary: true
    property bool showFormationTarget: true
    property bool showTaskEndpoint: true
    property real leftControlInset: ScreenTools.defaultFontPixelWidth * 7

    readonly property var bounds: mapConfig.world_bounds_m || ({})
    readonly property bool mapConfigValid: mapConfig.enabled === true && imageCoordinateContractValid
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
    readonly property real renderedPixelsPerMeter: imageCoordinateContractValid && factoryImage.width > 0
            ? Math.abs(Number(worldToPixelMatrix[0][0])) * factoryImage.width / imageWidthPx : 0
    readonly property real metersPerPixel: renderedPixelsPerMeter > 0 ? 1.0 / renderedPixelsPerMeter : 1.0
    readonly property real scaleMeters: niceScaleMeters(105 * metersPerPixel)
    readonly property real scaleWidth: scaleMeters / metersPerPixel
    readonly property var imageCoordinateContract: mapConfig.image_coordinate_contract || ({})
    readonly property var imageSizePx: imageCoordinateContract.image_size_px || ({})
    readonly property var worldToPixelMatrix: imageCoordinateContract.world_to_pixel_3x3 || []
    readonly property real imageWidthPx: Number(imageSizePx.width || 0)
    readonly property real imageHeightPx: Number(imageSizePx.height || 0)
    readonly property bool imageCoordinateContractValid: validImageCoordinateContract()
    readonly property bool loadedImageSizeMatchesContract: factoryImage.status !== Image.Ready
            || (Math.round(factoryImage.sourceSize.width) === Math.round(imageWidthPx)
                    && Math.round(factoryImage.sourceSize.height) === Math.round(imageHeightPx))
    readonly property var mapMetadata: mapState.map || ({})
    readonly property var mapDataStatus: mapState.map_data_status || ({})
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
            // The sidecar can cross the WSL/Windows filesystem boundary before
            // this process sees the new JSON. Prefer the local receipt time,
            // but update it only when the transport sequence advances.
            var receivedAt = Number(mapTransport.qgc_received_at_unix_s
                                    || mapTransport.received_at_unix_s || 0)
            return receivedAt > 0 && (Math.abs(Date.now() / 1000.0 - receivedAt) <= 2.5
                    || completedLiveFrame)
        }
        if (mode === "rosbag_replay")
            return ["playing", "paused", "completed"].indexOf(String(mapTransport.playback_state || "")) >= 0
        return false
    }
    readonly property bool runtimeStatusMatchesRun: String(runtimeStatus.schema || "")
            === "mosim.operator_runtime_status.v1"
            && String(runtimeStatus.run_id || "") === runId
            && String(runtimeStatus.experiment_profile_id || "")
                    === String(runManifest.experiment_profile_id || "")
            && String(runtimeStatus.experiment_profile_hash || "")
                    === String(runManifest.experiment_profile_hash || "")
    readonly property bool completedLiveFrame: String(mapTransport.mode || "") === "live_ros1"
            && runtimeStatusMatchesRun
            && ["completed", "blocked", "failed"].indexOf(String(runtimeStatus.state || "")) >= 0
    readonly property bool mapFrameAccepted: String(mapDataStatus.state || "accepted") === "accepted"
    readonly property bool mapContractReady: mapConfigValid && loadedImageSizeMatchesContract && mapIdentityMatches && mapTransportFresh
            && String(mapMetadata.coordinate_contract_status || "") === "verified"
    readonly property bool mapStateReady: mapContractReady && mapFrameAccepted
    readonly property var vehicles: mapStateReady && mapState.vehicles && mapState.vehicles.length !== undefined
        ? mapState.vehicles : []
    readonly property string taskPathSummary: taskPathStatusText()
    readonly property bool displayDataAvailable: hasDisplayData()

    function clamp(value, lower, upper) {
        return Math.max(lower, Math.min(value, upper))
    }

    function validImageCoordinateContract() {
        if (String(imageCoordinateContract.schema || "") !== "mosim.operator_map_image_coordinate_contract.v1"
                || String(imageCoordinateContract.matrix_schema || "") !== "mosim.world_to_pixel.v1"
                || String(imageCoordinateContract.render_mode || "") !== "axis_aligned_image_rect_v1"
                || !/^[0-9a-f]{64}$/.test(String(imageCoordinateContract.matrix_sha256 || ""))
                || !isFinite(imageWidthPx) || !isFinite(imageHeightPx)
                || imageWidthPx <= 0 || imageHeightPx <= 0
                || !worldToPixelMatrix || worldToPixelMatrix.length !== 3)
            return false
        for (var row = 0; row < 3; ++row) {
            if (!worldToPixelMatrix[row] || worldToPixelMatrix[row].length !== 3)
                return false
            for (var column = 0; column < 3; ++column) {
                if (!isFinite(Number(worldToPixelMatrix[row][column])))
                    return false
            }
        }
        return Math.abs(Number(worldToPixelMatrix[2][0])) < 0.000000001
                && Math.abs(Number(worldToPixelMatrix[2][1])) < 0.000000001
                && Math.abs(Number(worldToPixelMatrix[2][2]) - 1.0) < 0.000000001
                && Math.abs(Number(worldToPixelMatrix[0][1])) < 0.000000001
                && Math.abs(Number(worldToPixelMatrix[1][0])) < 0.000000001
                && Math.abs(Number(worldToPixelMatrix[0][0]) * Number(worldToPixelMatrix[1][1])) > 0.000000001
    }

    function sourcePixelForWorld(worldX, worldY) {
        if (!imageCoordinateContractValid)
            return ({ u: NaN, v: NaN })
        var denominator = Number(worldToPixelMatrix[2][0]) * Number(worldX)
                + Number(worldToPixelMatrix[2][1]) * Number(worldY)
                + Number(worldToPixelMatrix[2][2])
        if (!isFinite(denominator) || Math.abs(denominator) < 0.000000001)
            return ({ u: NaN, v: NaN })
        return {
            u: (Number(worldToPixelMatrix[0][0]) * Number(worldX)
                    + Number(worldToPixelMatrix[0][1]) * Number(worldY)
                    + Number(worldToPixelMatrix[0][2])) / denominator,
            v: (Number(worldToPixelMatrix[1][0]) * Number(worldX)
                    + Number(worldToPixelMatrix[1][1]) * Number(worldY)
                    + Number(worldToPixelMatrix[1][2])) / denominator
        }
    }

    function resetTracks() {
        actualTracksByVehicle = ({})
        actualTrackRevision += 1
        actualTrackRunId = runId
        actualTrackSourceIdentity = String(mapTransport.mode || "") + "|" + String(mapTransport.bag_id || "")
        actualTrackLastSequence = 0
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
        return sourcePixelForWorld(worldX, 0).u / imageWidthPx * factoryImage.width
    }

    function imageYForWorld(worldY) {
        return sourcePixelForWorld(0, worldY).v / imageHeightPx * factoryImage.height
    }

    function publishedActualTracks() {
        if (!mapStateReady || !mapState || mapState.actual_tracks === undefined)
            return null
        var rawTracks = mapState.actual_tracks
        if (!rawTracks || typeof rawTracks !== "object")
            return ({})
        var normalized = ({})
        var ids = Object.keys(rawTracks).sort()
        for (var idIndex = 0; idIndex < ids.length; ++idIndex) {
            var id = ids[idIndex]
            var track = rawTracks[id]
            if (!track || typeof track !== "object"
                    || String(track.status || "") !== "available"
                    || String(track.semantics || "") !== "actual_vehicle_track"
                    || String(track.vehicle_id || "") !== id
                    || String(track.run_id || "") !== runId
                    || String(track.frame_id || "") !== String(mapConfig.world_frame || "")
                    || !isFinite(Number(track.updated_at))
                    || !track.points || track.points.length === undefined)
                return ({})
            var points = []
            for (var pointIndex = 0; pointIndex < track.points.length; ++pointIndex) {
                var point = track.points[pointIndex]
                if (!validWorldPoint(point))
                    return ({})
                if (point.z !== undefined && !isFinite(Number(point.z)))
                    return ({})
                var normalizedPoint = { x: Number(point.x), y: Number(point.y) }
                if (point.z !== undefined)
                    normalizedPoint.z = Number(point.z)
                points.push(normalizedPoint)
            }
            normalized[id] = points
        }
        return normalized
    }

    function appendActualTracks() {
        if (!mapStateReady)
            return
        var sourceIdentity = String(mapTransport.mode || "") + "|" + String(mapTransport.bag_id || "")
        var sequence = Number(mapTransport.sequence || 0)
        if (actualTrackRunId !== runId || actualTrackSourceIdentity !== sourceIdentity
                || (actualTrackLastSequence > 0 && sequence > 0 && sequence < actualTrackLastSequence))
            resetTracks()
        var publishedTracks = publishedActualTracks()
        if (publishedTracks !== null) {
            actualTracksByVehicle = publishedTracks
            actualTrackRevision += 1
            actualTrackLastSequence = Math.max(actualTrackLastSequence, sequence)
            return
        }
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
        actualTrackLastSequence = Math.max(actualTrackLastSequence, sequence)
    }

    function taskPath(kind) {
        if (!mapContractReady)
            return ({})
        var paths = mapState.task_paths || ({})
        var path = paths[kind] || ({})
        if (path.status !== "available" || !path.points || path.points.length < 2)
            return ({})
        if (path.run_id !== undefined && String(path.run_id) !== runId)
            return ({})
        if (kind === "future" && String(mapTransport.mode || "") === "live_ros1") {
            // This timestamp advances only when QGC observes a new future-path
            // update, so a still-running sidecar cannot keep an old path alive.
            var futureReceivedAt = Number(path.qgc_received_at_unix_s || path.updated_at || 0)
            if (futureReceivedAt <= 0 || Date.now() / 1000.0 - futureReceivedAt > 5.0)
                return ({})
        }
        for (var index = 0; index < path.points.length; ++index) {
            if (!validWorldPoint(path.points[index]))
                return ({})
        }
        // A vertical takeoff-hover-land reference has no planar extent.  Keep
        // its real final point as the target marker instead of drawing a
        // misleading zero-length 2D route.
        if (kind === "expected" && !hasPlanarExtent(path.points))
            return ({})
        return path
    }

    function hasPlanarExtent(points) {
        if (!points || points.length < 2)
            return false
        var first = points[0]
        for (var index = 1; index < points.length; ++index) {
            var point = points[index]
            if (Math.hypot(Number(point.x) - Number(first.x), Number(point.y) - Number(first.y)) >= 0.01)
                return true
        }
        return false
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
        if (!mapContractReady)
            return mapDataGateText()
        var labels = []
        if (!mapFrameAccepted)
            labels.push("实时飞机位置已拒绝")
        if (taskPath("expected").status === "available")
            labels.push(taskPathLabel("expected") + "已接收")
        if (taskEndpoint() !== null)
            labels.push("任务终点已接收（非返航点）")
        if (taskPath("future").status === "available")
            labels.push(taskPathLabel("future") + "已接收")
        if (Object.keys(actualTracksByVehicle).length > 0)
            labels.push(completedLiveFrame ? "实际轨迹已保留"
                     : (String(mapTransport.mode || "") === "rosbag_replay" ? "实际轨迹回放中" : "实际轨迹实时记录中"))
        return labels.length > 0 ? labels.join("；") : "等待任务轨迹与飞机位置"
    }

    function hasDisplayData() {
        if (!mapContractReady)
            return false
        if (mapStateReady && Object.keys(actualTracksByVehicle).length > 0)
            return true
        if (taskPath("expected").status === "available" || taskPath("future").status === "available")
            return true
        return taskEndpoint() !== null || vehicles.length > 0
    }

    function displayWorldPoints() {
        var points = []
        function appendPoint(point) {
            if (validWorldPoint(point))
                points.push({ x: Number(point.x), y: Number(point.y) })
        }

        var trackIds = Object.keys(actualTracksByVehicle)
        for (var trackIndex = 0; trackIndex < trackIds.length; ++trackIndex) {
            var track = actualTracksByVehicle[trackIds[trackIndex]] || []
            for (var pointIndex = 0; pointIndex < track.length; ++pointIndex)
                appendPoint(track[pointIndex])
        }

        var pathKinds = ["expected", "future"]
        for (var kindIndex = 0; kindIndex < pathKinds.length; ++kindIndex) {
            var path = taskPath(pathKinds[kindIndex])
            var pathPoints = path.points || []
            for (var pathIndex = 0; pathIndex < pathPoints.length; ++pathIndex)
                appendPoint(pathPoints[pathIndex])
        }

        var endpoint = taskEndpoint()
        appendPoint(endpoint)
        for (var vehicleIndex = 0; vehicleIndex < vehicles.length; ++vehicleIndex) {
            var vehicle = vehicles[vehicleIndex]
            if (vehicle && vehicle.state)
                appendPoint(vehicle.state.position)
        }
        return points
    }

    function mapDataGateText() {
        if (!mapConfigValid)
            return "等待地图配置"
        if (!loadedImageSizeMatchesContract)
            return "工厂地图尺寸与坐标契约不匹配"
        if (!manifestMatchesRun)
            return ""
        if (String(mapState.run_id || "") !== runId)
            return "等待当前运行地图数据"
        if (!mapSnapshotHashMatches)
            return "地图快照身份不匹配"
        if (!mapIdentityMatches)
            return "地图或 Profile 身份不匹配"
        if (String(mapMetadata.coordinate_contract_status || "") !== "verified")
            return "坐标契约待验证"
        if (!mapFrameAccepted) {
            var reason = String(mapDataStatus.reason_code || "")
            if (reason === "operator_map_coordinate_evidence_source_frame_mismatch")
                return "实时地图坐标系与证据不匹配"
            if (reason === "operator_map_coordinate_vector_invalid"
                    || reason === "operator_map_coordinate_orientation_invalid")
                return "实时地图坐标数据无效"
            if (reason === "operator_map_vehicle_position_invalid")
                return "实时地图位置超出 Factory L2 范围"
            if (reason === "operator_map_task_path_points_invalid")
                return "任务轨迹超出 Factory L2 范围"
            return "实时地图帧已拒绝"
        }
        if (completedLiveFrame)
            return "任务已结束，显示最后有效地图帧"
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

    function taskEndpoint() {
        if (!mapContractReady)
            return null
        var paths = mapState.task_paths || ({})
        var path = paths.expected || ({})
        // A takeoff-hover-land reference is vertical in 3D, so all XY points
        // may be identical. Keep its final published reference as a task
        // endpoint marker; it is not a home or return point.
        if (path.status !== "available" || !path.points || path.points.length < 1)
            return null
        if (path.run_id !== undefined && String(path.run_id) !== runId)
            return null
        var point = path.points[path.points.length - 1]
        if (!validWorldPoint(point))
            return null
        return { x: Number(point.x), y: Number(point.y) }
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

    function paintTaskEndpoint(canvas) {
        var context = canvas.getContext("2d")
        context.reset()
        var target = taskEndpoint()
        if (!target)
            return
        var x = imageXForWorld(target.x)
        var y = imageYForWorld(target.y)
        var radius = Math.max(7, Math.min(13, factoryImage.width / 70))
        context.beginPath()
        context.arc(x, y, radius, 0, Math.PI * 2)
        context.strokeStyle = "#ffb020"
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
        if (!isFinite(wheelDelta) || Math.abs(wheelDelta) < 0.0001)
            return
        var oldZoom = zoomFactor
        var nextZoom = clamp(oldZoom * (wheelDelta > 0 ? 1.2 : 1.0 / 1.2), minZoom, maxZoom)
        if (Math.abs(nextZoom - oldZoom) < 0.0001)
            return

        // viewX/viewY are always viewport-local. Preserve this exact image
        // point while the content surface and the image anchors are resized.
        var viewportX = clamp(viewX, 0, mapFlickable.width)
        var viewportY = clamp(viewY, 0, mapFlickable.height)
        var imageX = mapFlickable.contentX + viewportX - factoryImage.x
        var imageY = mapFlickable.contentY + viewportY - factoryImage.y
        var imageRatioX = clamp(imageX / factoryImage.width, 0, 1)
        var imageRatioY = clamp(imageY / factoryImage.height, 0, 1)
        zoomFactor = nextZoom
        Qt.callLater(function() {
            var targetX = factoryImage.x + imageRatioX * factoryImage.width - viewportX
            var targetY = factoryImage.y + imageRatioY * factoryImage.height - viewportY
            mapFlickable.contentX = clamp(targetX, 0, Math.max(0, mapFlickable.contentWidth - mapFlickable.width))
            mapFlickable.contentY = clamp(targetY, 0, Math.max(0, mapFlickable.contentHeight - mapFlickable.height))
        })
    }

    function fitMap() {
        zoomFactor = defaultZoomFactor
        Qt.callLater(function() {
            mapFlickable.contentX = Math.max(0, (mapFlickable.contentWidth - mapFlickable.width) / 2)
            mapFlickable.contentY = Math.max(0, (mapFlickable.contentHeight - mapFlickable.height) / 2)
        })
    }

    function focusDisplay() {
        var points = displayWorldPoints()
        if (points.length === 0) {
            fitMap()
            return
        }

        var minX = Number(points[0].x)
        var maxX = minX
        var minY = Number(points[0].y)
        var maxY = minY
        for (var index = 1; index < points.length; ++index) {
            minX = Math.min(minX, Number(points[index].x))
            maxX = Math.max(maxX, Number(points[index].x))
            minY = Math.min(minY, Number(points[index].y))
            maxY = Math.max(maxY, Number(points[index].y))
        }

        var centerX = (minX + maxX) / 2.0
        var centerY = (minY + maxY) / 2.0
        var halfSpanX = Math.max((maxX - minX) * 0.55, 10.0)
        var halfSpanY = Math.max((maxY - minY) * 0.55, 10.0)
        minX = centerX - halfSpanX
        maxX = centerX + halfSpanX
        minY = centerY - halfSpanY
        maxY = centerY + halfSpanY

        var baseWidth = Math.max(1.0, Number(factoryImage.fittedWidth || mapFlickable.width))
        var baseHeight = Math.max(1.0, baseWidth / imageAspectRatio)
        var sourceXMin = sourcePixelForWorld(minX, 0).u
        var sourceXMax = sourcePixelForWorld(maxX, 0).u
        var sourceYMin = sourcePixelForWorld(0, minY).v
        var sourceYMax = sourcePixelForWorld(0, maxY).v
        var baseSpanX = Math.abs(sourceXMax - sourceXMin) / imageWidthPx * baseWidth
        var baseSpanY = Math.abs(sourceYMax - sourceYMin) / imageHeightPx * baseHeight
        var targetWidth = Math.max(160.0, mapFlickable.width * 0.72)
        var targetHeight = Math.max(120.0, mapFlickable.height * 0.72)
        var requestedZoom = Math.min(targetWidth / baseSpanX, targetHeight / baseSpanY)
        if (!isFinite(requestedZoom) || requestedZoom <= 0.0)
            requestedZoom = defaultZoomFactor
        zoomFactor = clamp(requestedZoom, minZoom, maxZoom)

        // Wait for the image dimensions to settle after the zoom binding changes.
        Qt.callLater(function() {
            var centerImageX = imageXForWorld(centerX)
            var centerImageY = imageYForWorld(centerY)
            if (!isFinite(centerImageX) || !isFinite(centerImageY)) {
                fitMap()
                return
            }
            var targetX = factoryImage.x + centerImageX - mapFlickable.width / 2.0
            var targetY = factoryImage.y + centerImageY - mapFlickable.height / 2.0
            mapFlickable.contentX = clamp(targetX, 0, Math.max(0, mapFlickable.contentWidth - mapFlickable.width))
            mapFlickable.contentY = clamp(targetY, 0, Math.max(0, mapFlickable.contentHeight - mapFlickable.height))
        })
    }

    onRunIdChanged: {
        resetTracks()
        fitMap()
    }
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
                visible: root.mapContractReady && (root.showExpectedPath || root.showFuturePath)
                z: 2
                property int mapSequence: Number(root.mapTransport.sequence || 0)
                onMapSequenceChanged: requestPaint()
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()
                onPaint: root.paintTaskPaths(this)
            }

            Canvas {
                id: taskEndpointCanvas
                x: factoryImage.x
                y: factoryImage.y
                width: factoryImage.width
                height: factoryImage.height
                visible: root.showTaskEndpoint && root.taskEndpoint() !== null
                z: 3
                property int mapSequence: Number(root.mapTransport.sequence || 0)
                onMapSequenceChanged: requestPaint()
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()
                onPaint: root.paintTaskEndpoint(this)
            }

            Canvas {
                id: formationTargetCanvas
                x: factoryImage.x
                y: factoryImage.y
                width: factoryImage.width
                height: factoryImage.height
                visible: root.showFormationTarget && root.formationTarget() !== null
                z: 4
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
                z: 5
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
                    z: 6
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

    }

    // This area belongs to the viewport, not Flickable.contentItem. Wheel
    // coordinates therefore stay stable after the map has been panned.
    MouseArea {
        id: mapWheelArea
        anchors.fill: mapFlickable
        acceptedButtons: Qt.NoButton
        hoverEnabled: true
        z: 10
        onWheel: function(wheel) {
            var delta = wheel.angleDelta.y
            if (Math.abs(delta) < 0.0001)
                delta = wheel.pixelDelta.y
            root.zoomAt(wheel.x, wheel.y, delta)
            wheel.accepted = true
        }
    }

    // This replaces QGC's online-tile MapScale in the same upper-left
    // location. Its buttons drive the Factory raster rather than the hidden
    // background FlightMap.
    Row {
        id: mapScaleControls
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: root.leftControlInset
        anchors.topMargin: ScreenTools.defaultFontPixelWidth
        spacing: 4
        z: 20

        QGCButton { text: "+"; onClicked: root.zoomAt(mapFlickable.width / 2, mapFlickable.height / 2, 1) }
        QGCButton { text: "-"; onClicked: root.zoomAt(mapFlickable.width / 2, mapFlickable.height / 2, -1) }

        Column {
            spacing: 2
            readonly property real scaleMeters: root.scaleMeters
            readonly property real scaleWidth: root.scaleWidth

            Text {
                text: parent.scaleMeters >= 1000 ? (parent.scaleMeters / 1000).toFixed(1) + " km" : parent.scaleMeters.toFixed(0) + " m"
                color: "#ffffff"
                font.pixelSize: ScreenTools.defaultFontPixelHeight * 0.9
            }
            Rectangle {
                width: Math.max(24, Math.min(150, parent.scaleWidth))
                height: 3
                color: "#ffffff"
            }
        }
    }

    Row {
        id: mapViewControls
        anchors.left: mapScaleControls.left
        anchors.top: mapScaleControls.bottom
        anchors.topMargin: 4
        spacing: 4
        z: 20

        QGCButton {
            text: "定位轨迹"
            enabled: root.displayDataAvailable
            onClicked: root.focusDisplay()
        }
        QGCButton {
            text: "全图"
            onClicked: root.fitMap()
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
        id: mapLegend
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: ScreenTools.defaultFontPixelWidth
        spacing: ScreenTools.defaultFontPixelWidth
        visible: root.mapContractReady

        Repeater {
            model: [
                { label: "实际", color: "#00d084", visible: root.showActualTracks && Object.keys(root.actualTracksByVehicle).length > 0 },
                { label: "任务终点（非返航点）", color: "#ffb020", visible: root.showTaskEndpoint && root.taskEndpoint() !== null },
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
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: mapLegend.top
        anchors.bottomMargin: 4
        visible: root.mapContractReady && !root.mapFrameAccepted
        text: root.mapDataGateText() + "；飞机和实际轨迹已隐藏"
        color: "#f4b183"
        font.pixelSize: ScreenTools.defaultFontPixelHeight * 0.85
    }

    Text {
        anchors.centerIn: parent
        // The floorplan remains useful before a run is prepared. Only surface
        // a telemetry/map diagnostic after the current run is identifiable.
        visible: !root.mapConfigValid || factoryImage.status === Image.Error
                 || (root.manifestMatchesRun && !root.mapContractReady)
        text: !root.mapConfigValid ? "等待地图配置"
              : (factoryImage.status === Image.Error ? "工厂地图资源不可用" : root.mapDataGateText())
        color: "#f4b183"
        font.pixelSize: ScreenTools.largeFontPixelSize
    }
}
