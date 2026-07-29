from pathlib import Path


def test_flight_simulation_and_ground_station_have_separate_owners() -> None:
    flight = Path("Scripts/ui/start_flight_simulation.ps1").read_text(encoding="utf-8")
    ground = Path("Scripts/ui/run_qgc_with_ue.ps1").read_text(encoding="utf-8")

    assert '"prepare_run"' in flight
    assert '"start_run"' in flight
    assert 'lifecycle_state -eq "ready"' in flight
    assert "Starting the QGC-validated task" in flight
    assert "flight_terminal_" in flight
    assert "A Gazebo status terminal is already monitoring run" in flight
    assert "RUNTIME_STATUS.json" in flight
    assert "Keep this window open while testing" in flight

    assert '"prepare_run"' not in ground
    assert '"start_run"' not in ground
    assert '"get_run_state"' in ground
    assert '"prepare_display_session"' in ground
    assert '"unreal"' in ground
    assert "run_flight_console.ps1" in ground
    assert "Start-FlightConsoleConfigurationMode" in ground
    assert "no active flight simulation" in ground
    assert "Select a task, validate its Profile, then start it from QGC" in ground
    assert "managed UE viewport will start for that run_id" in ground


def test_qgc_command_surface_does_not_autostart_runtime() -> None:
    operator_bridge = Path("apps/flight_console/mosim/custom/src/MoSimOperatorBridge.cc").read_text(
        encoding="utf-8"
    )
    operator_qml = Path("apps/flight_console/mosim/custom/src/FlyViewCustomLayer.qml").read_text(
        encoding="utf-8"
    )
    legacy_bridge = Path("apps/flight_console/mosim/custom/src/MoSimOrchestratorBridge.cc").read_text(
        encoding="utf-8"
    )

    assert "void MoSimOperatorBridge::copySelectedLaunchCommand()" in operator_bridge
    assert "copyCommand(renderRuntimeCommand" in operator_bridge
    assert "QProcess" not in operator_bridge
    assert "startDetached" not in operator_bridge
    assert "mosimOperator.copySelectedLaunchCommand()" in operator_qml

    # The legacy bridge remains for compatibility, but the active QML must not
    # route a launch through it or auto-open an additional terminal.
    assert "void MoSimOrchestratorBridge::launchRuntimeStatusTerminal()" in legacy_bridge
    assert "launchRuntimeStatusTerminal();" not in legacy_bridge
    assert "mosimOrchestrator" not in operator_qml


def test_ground_station_reconciles_duplicate_managed_unreal_processes() -> None:
    ground = Path("Scripts/ui/run_qgc_with_ue.ps1").read_text(encoding="utf-8")

    assert "Get-TrackedDisplayRecords" in ground
    assert "DISPLAY_SESSION.json" in ground
    assert "DISPLAY_PROCESSES.json" in ground
    assert "Test-TrackedDisplayOwnership" in ground
    assert "MoSimSceneLibrary.uproject" in ground
    assert "-MoSimObservabilityRunId=$RunId" in ground
    assert "launch_ros1_display.sh" in ground
    assert "PreserveProcessIds" in ground
    assert "WaitForExit(5000)" in ground
    assert "stale_display_process_survived" in ground
    assert "foreach ($record in $parsedRecords)" in ground


def test_stop_script_flattens_display_process_json_records() -> None:
    stopper = Path("Scripts/ui/stop_all_simulation.ps1").read_text(encoding="utf-8")

    assert "foreach ($record in $parsedRecords)" in stopper


def test_operator_cmd_entrypoints_are_explicit() -> None:
    flight_cmd = Path("cmd/\u542f\u52a8Gazebo\u98de\u884c\u4eff\u771f.cmd").read_text(encoding="utf-8")
    ground_cmd = Path("cmd/\u542f\u52a8MoSim\u5730\u9762\u7ad9.cmd").read_text(encoding="utf-8")
    stop_cmd = Path("cmd/\u505c\u6b62\u6240\u6709\u4eff\u771f.cmd").read_text(encoding="utf-8")
    compatibility = Path("cmd/Start_MoSim_QGC.cmd").read_text(encoding="utf-8")

    assert "start_flight_simulation.ps1" in flight_cmd
    assert "run_flight_console.ps1" in ground_cmd
    assert "run_qgc_with_ue.ps1" not in ground_cmd
    assert "Review the error above and the startup logs" in ground_cmd
    assert "stop_all_simulation.ps1" in stop_cmd
    assert "\u542f\u52a8MoSim\u5730\u9762\u7ad9.cmd" in compatibility


def test_stop_script_uses_active_run_and_scoped_process_records() -> None:
    stopper = Path("Scripts/ui/stop_all_simulation.ps1").read_text(encoding="utf-8")

    assert "Get-MoSimActiveRun" in stopper
    assert "DISPLAY_PROCESSES.json" in stopper
    assert "DISPLAY_SESSION.json" in stopper
    assert "Test-ManagedDisplayOwnership" in stopper
    assert "MoSimSceneLibrary.uproject" in stopper
    assert "WaitForExit(10000)" in stopper
    assert "managed_process_survived" in stopper
    assert '"stop_run"' in stopper
    assert "stop_orchestrated_runtime.sh" in stopper
    assert "Stop-Process -Name" not in stopper


def test_operator_workflow_distinguishes_manual_and_automatic_flight_authority() -> None:
    workflow = Path("Docs/Workflows/qgc_ue_operator_startup.md").read_text(encoding="utf-8")

    assert "\u5f53\u524d\u5165\u53e3\uff1a`cmd/\u542f\u52a8MoSim\u5730\u9762\u7ad9.cmd`" in workflow
    assert "\u5b83\u4e0d\u542f\u52a8 UE\u3001Gazebo\u3001PX4\u3001MAVROS\u3001RViz\u3001ROS \u8282\u70b9\u6216" in workflow
    assert "\u6240\u6709\u8fd0\u884c\u547d\u4ee4\u5747\u7531\u7528\u6237\u5728\u4e00\u4e2a\u53ef\u89c1\u7ec8\u7aef\u6267\u884c" in workflow
    assert "Plan View \u53ef\u7f16\u8f91\u539f\u751f QGC \u822a\u70b9\u548c\u8fb9\u754c\u8349\u6848" in workflow
