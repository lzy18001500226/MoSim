from pathlib import Path

from Scripts.ui.materialize_qgc_custom_overlay import SOURCE


def test_qgc_map_shows_dense_qgc_plan_actual_and_planner_trajectory_layers() -> None:
    fly_layer = (SOURCE / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")
    fly_map = (SOURCE / "src" / "FactoryFlyMap.qml").read_text(encoding="utf-8")
    plan_map = (SOURCE / "src" / "FactoryPlanMapOverlay.qml").read_text(encoding="utf-8")

    assert "showMapExpectedPath" not in fly_layer
    assert "任务预期轨迹" not in fly_layer
    assert "showMapFormationTarget" not in fly_layer
    assert "编队目标" not in fly_layer
    assert 'text: "规划器轨迹"' in fly_layer
    assert 'text: "QGC航点路线"' in fly_layer

    assert "showExpectedPath" not in fly_map
    assert "taskPath(\"expected\")" not in fly_map
    assert "任务预期轨迹" not in fly_map
    assert "paths.expected" not in fly_map
    assert "showTaskEndpoint" not in fly_map
    assert "taskEndpoint()" not in fly_map
    assert "formationTarget()" not in fly_map
    assert "function plannerPath()" in fly_map
    assert "function qgcWaypointPlanRoute()" in fly_map
    assert "mosim.qgc_waypoint_plan_route_preview.v1" in fly_map
    assert "route.source_points" in fly_map
    assert 'context.strokeStyle = "#ffb020"' in fly_map
    assert "property real actualTrackMinDistanceM: 0.02" in fly_map
    assert ">= root.actualTrackMinDistanceM" in fly_map
    assert "track.sampling_min_distance_m" in fly_map
    assert "Number(track.sampling_min_distance_m) > 0.02" in fly_map
    assert "var path = paths.future || ({})" in fly_map
    assert 'String(path.source_type) !== "traj_utils/PolyTraj"' in fly_map
    assert "Number(path.sampling_period_s) > 0.01" in fly_map
    assert "Number(path.requested_sampling_period_s) > 0.01" in fly_map
    assert "Number(path.sample_count) !== path.points.length" in fly_map
    assert 'visible: root.mapContractReady && root.showFuturePath' in fly_map
    assert '{ label: root.plannerPathLabel(), color: "#4aa3ff"' in fly_map

    assert 'var kinds = ["expected", "future"]' not in plan_map
    assert "function taskPath(kind)" not in plan_map
    assert "function plannerPath()" in plan_map
    assert "function qgcWaypointPlanRoute()" in plan_map
    assert "mosim.qgc_waypoint_plan_route_preview.v1" in plan_map
    assert "route.source_points" in plan_map
    assert 'context.strokeStyle = "#ffb020"' in plan_map
    assert "property real actualTrackMinDistanceM: 0.02" in plan_map
    assert ">= root.actualTrackMinDistanceM" in plan_map
    assert "track.sampling_min_distance_m" in plan_map
    assert "Number(track.sampling_min_distance_m) > 0.02" in plan_map
    assert ").future || ({})" in plan_map
    assert 'String(path.source_type) !== "traj_utils/PolyTraj"' in plan_map
    assert "Number(path.sampling_period_s) > 0.01" in plan_map
    assert "Number(path.requested_sampling_period_s) > 0.01" in plan_map
    assert "Number(path.sample_count) !== path.points.length" in plan_map
    assert "mapTransport.qgc_received_at_unix_s" in plan_map
    assert "function publishedActualTracks()" in plan_map
    assert "var publishedTracks = publishedActualTracks()" in plan_map
    assert "actualTracksByVehicle = publishedTracks" in plan_map
    assert "context.strokeStyle = vehicleColor(pathIndex + 2)" in plan_map
