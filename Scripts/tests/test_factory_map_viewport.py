from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FLY_MAP = ROOT / "apps" / "flight_console" / "mosim" / "custom" / "src" / "FactoryFlyMap.qml"
PLAN_VIEW = ROOT / "apps" / "flight_console" / "mosim" / "custom" / "src" / "PlanView.qml"
FLY_WIDGET_LAYER = ROOT / "apps" / "flight_console" / "mosim" / "custom" / "src" / "FlyViewWidgetLayer.qml"
CUSTOM_QRC = ROOT / "apps" / "flight_console" / "mosim" / "custom" / "custom.qrc"


def test_fly_map_zoom_uses_viewport_coordinates_and_uses_the_upper_left_scale_controls() -> None:
    qml = FLY_MAP.read_text(encoding="utf-8")

    assert "id: mapWheelArea" in qml
    assert "anchors.fill: mapFlickable" in qml
    assert "var viewportX = clamp(viewX, 0, mapFlickable.width)" in qml
    assert "var viewportY = clamp(viewY, 0, mapFlickable.height)" in qml
    assert "mapFlickable.contentX + viewportX - factoryImage.x" in qml
    assert "mapFlickable.contentY + viewportY - factoryImage.y" in qml
    assert "id: mapScaleControls" in qml
    assert "anchors.leftMargin: root.leftControlInset" in qml
    assert "text: \"+\"; onClicked: root.zoomAt(mapFlickable.width / 2, mapFlickable.height / 2, 1)" in qml
    assert "root.zoomAt(mapFlickable.width / 2, mapFlickable.height / 2, -1)" in qml
    assert "id: mapZoomControls" not in qml
    assert "id: mapTitlePanel" not in qml
    assert "等待当前运行清单" not in qml
    assert "root.manifestMatchesRun && !root.mapStateReady" in qml


def test_factory_fly_view_hides_the_underlying_online_map_scale() -> None:
    widget_layer = FLY_WIDGET_LAYER.read_text(encoding="utf-8")
    qrc = CUSTOM_QRC.read_text(encoding="utf-8")

    assert "property bool   showNativeMapScale:      true" in widget_layer
    assert "visible:            showNativeMapScale && !ScreenTools.isTinyScreen" in widget_layer
    assert 'showNativeMapScale:      false' in (ROOT / "apps" / "flight_console" / "mosim" / "custom" / "src" / "FlyView.qml").read_text(encoding="utf-8")
    assert 'alias="QGroundControl/FlightDisplay/FlyViewWidgetLayer.qml"' in qrc


def test_plan_map_preserves_the_pointer_coordinate_and_exposes_scale_controls() -> None:
    qml = PLAN_VIEW.read_text(encoding="utf-8")

    assert "function zoomAtPointer(viewX, viewY, wheelDelta)" in qml
    assert "var anchor = editorMap.toCoordinate(pointer, false" in qml
    assert "editorMap.alignCoordinateToPoint(anchor, pointer)" in qml
    assert "id: factoryPlanWheelArea" in qml
    assert "editorMap.zoomAtPointer(wheel.x, wheel.y, delta)" in qml
    assert "MapScale {" in qml
    assert "id: factoryPlanMapScale" in qml
    assert "mapControl: editorMap" in qml
