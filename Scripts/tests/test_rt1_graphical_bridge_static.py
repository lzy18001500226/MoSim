from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = (
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Control"
    / "Px4Ctrl"
    / "Px4CtrlAttitudeThrustSysblockAdapter.mo"
)
BRIDGE = (
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "RealTime"
    / "MworksRt1Px4CtrlGraphicalShadow100Hz.mo"
)
RUNNER = ROOT / "Scripts" / "mworks" / "run_rt1_graphical_loopback_mcp.py"


def test_adapter_uses_only_the_graphical_sysblock_output() -> None:
    adapter = ADAPTER.read_text(encoding="utf-8")

    assert "Px4CtrlOuterLoopGraphicalSysblock outer_loop" in adapter
    assert "if time < controller_sample_period_s" not in adapter
    assert "EquationBridge law" not in adapter
    for axis in range(1, 4):
        assert (
            f"desired_acceleration[{axis}] = graphical_desired_acceleration[{axis}];"
            in adapter
        )


def test_rt1_waits_for_graphical_core_before_first_send() -> None:
    bridge = BRIDGE.read_text(encoding="utf-8")

    assert "discrete Integer graphicalStateTicks(start = 0, fixed = true);" in bridge
    assert "graphicalStateTicks := pre(graphicalStateTicks) + 1;" in bridge
    assert "pendingCommand := pre(graphicalStateTicks) >= 1;" in bridge
    assert "controller_sample_period_s = samplePeriod" not in bridge


def test_loopback_runner_has_no_prewarm_simulation() -> None:
    runner = RUNNER.read_text(encoding="utf-8")

    assert "BATCH_SIM_MODE = 2" in runner
    assert '"sim_mode": BATCH_SIM_MODE' in runner
    assert '"startup_strategy": "fixture_precedes_single_batch_simulation"' in runner
    assert "warmup_simulation = client.call_tool" not in runner
    assert '"sim_mode": 0' not in runner
    assert runner.index("fixture_process = subprocess.Popen") < runner.index(
        "simulation = client.call_tool"
    )
    assert '"--fixture-profile"' in runner
    assert '"rt2_outer_loop_excitation"' in runner
    assert '"RT2_LOCAL_UDP_LOOPBACK.json"' in runner
