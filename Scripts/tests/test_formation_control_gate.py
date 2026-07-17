from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER = (ROOT / "Scripts/control_platform/formation_control_core.h").read_text(encoding="utf-8")
SOURCE = (ROOT / "Scripts/control_platform/formation_control_core.c").read_text(encoding="utf-8")


def test_all_required_formation_modes_are_fixed_size_and_registered():
    for token in (
        "MOSIM_FORMATION_LEADER_FOLLOWER", "MOSIM_FORMATION_VIRTUAL_STRUCTURE",
        "MOSIM_FORMATION_CONSENSUS", "MOSIM_FORMATION_CONTAINMENT",
        "MOSIM_FORMATION_TRACKING", "MOSIM_FORMATION_RECONFIGURATION",
        "MOSIM_FORMATION_FAULT_TOLERANT", "MOSIM_FORMATION_CBF",
        "MOSIM_FORMATION_DISTRIBUTED_MPC",
    ):
        assert token in HEADER
    assert "MOSIM_FORMATION_AGENTS 3" in HEADER


def test_core_contains_health_reconfiguration_cbf_and_speed_guards():
    assert "input->healthy[agent]" in SOURCE
    assert "input->reconfigure" in SOURCE
    assert "apply_cbf(params, input, output)" in SOURCE
    assert "apply_speed_limit(params, output)" in SOURCE
    assert "finite_input(input)" in SOURCE
