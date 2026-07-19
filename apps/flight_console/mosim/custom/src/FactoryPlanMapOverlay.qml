import QtQuick
import QtPositioning

import QGroundControl

Item {
    required property var map
    required property var mapConfig

    readonly property var anchorConfig: mapConfig.simulation_geodetic_anchor || ({})
    readonly property var bounds: mapConfig.world_bounds_m || ({})
    readonly property var mapCenter: QtPositioning.coordinate(
        Number(anchorConfig.latitude_deg || 0),
        Number(anchorConfig.longitude_deg || 0),
        Number(anchorConfig.altitude_m || 0))
    readonly property var northWest: coordinateForWorld(Number(bounds.min_x_m || 0), Number(bounds.max_y_m || 0))
    readonly property var southEast: coordinateForWorld(Number(bounds.max_x_m || 0), Number(bounds.min_y_m || 0))
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

    visible: mapConfig.enabled === true
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

    Image {
        anchors.fill: parent
        source: String(mapConfig.resource_url || "")
        fillMode: Image.Stretch
        smooth: true
        mipmap: true
        cache: true
    }
}
