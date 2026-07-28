import QtQuick
import QtPositioning

import QGroundControl

Item {
    required property var map
    required property var mapConfig
    required property var runManifest

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
    readonly property bool scenarioBoundaryValid:
        isFinite(Number(scenarioBoundary.min_x_m))
        && isFinite(Number(scenarioBoundary.max_x_m))
        && isFinite(Number(scenarioBoundary.min_y_m))
        && isFinite(Number(scenarioBoundary.max_y_m))
        && Number(scenarioBoundary.min_x_m) < Number(scenarioBoundary.max_x_m)
        && Number(scenarioBoundary.min_y_m) < Number(scenarioBoundary.max_y_m)
    readonly property var explorationBoundary: scenarioBoundaryValid ? scenarioBoundary : configuredBoundary
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
}
