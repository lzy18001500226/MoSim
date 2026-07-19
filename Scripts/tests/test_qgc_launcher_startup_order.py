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
    assert "flight_simulation_not_active" in ground
    assert "Gazebo flight simulation launcher" in ground


def test_qgc_start_ack_opens_separate_runtime_status_terminal() -> None:
    bridge = Path("apps/flight_console/mosim/custom/src/MoSimOrchestratorBridge.cc").read_text(encoding="utf-8")
    header = Path("apps/flight_console/mosim/custom/src/MoSimOrchestratorBridge.h").read_text(encoding="utf-8")

    assert "void MoSimOrchestratorBridge::launchRuntimeStatusTerminal()" in bridge
    assert "launchRuntimeStatusTerminal();" in bridge
    assert 'QStringLiteral("启动Gazebo飞行仿真.cmd")' in bridge
    assert 'QStringLiteral("cmd.exe")' in bridge
    assert "QProcess::startDetached" in bridge
    assert "void launchRuntimeStatusTerminal();" in header


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


def test_operator_cmd_entrypoints_are_explicit() -> None:
    flight_cmd = Path("\u542f\u52a8Gazebo\u98de\u884c\u4eff\u771f.cmd").read_text(encoding="utf-8")
    ground_cmd = Path("\u542f\u52a8MoSim\u5730\u9762\u7ad9.cmd").read_text(encoding="utf-8")
    stop_cmd = Path("\u505c\u6b62\u6240\u6709\u4eff\u771f.cmd").read_text(encoding="utf-8")
    compatibility = Path("Start_MoSim_QGC.cmd").read_text(encoding="utf-8")

    assert "start_flight_simulation.ps1" in flight_cmd
    assert "run_qgc_with_ue.ps1" in ground_cmd
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

    assert "使用 QGC 原生飞行操作解锁并起飞" in workflow
    assert "未连接、未解锁或不在 `Position` 模式时" in workflow
    assert "以下任务不要求操作者手动解锁" in workflow
    assert "FUEL单机自主探索" in workflow
    assert "三机固定编队避障" in workflow
    assert "启动并执行自动任务" in workflow
    assert "任务 Adapter 返回终态 ACK" in workflow
    assert "不得再使用 QGC 手动解锁" in workflow
    assert "UE 已嵌入且显示当前运行的飞机，不是上一 `run_id` 的残留画面" in workflow
