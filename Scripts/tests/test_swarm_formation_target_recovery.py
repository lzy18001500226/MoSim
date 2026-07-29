from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MISSION = ROOT / "Scripts/sunray/px4ctrl_ego_swarm_mission_node.py"
RUNNER = ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"


def test_formation_center_recovery_is_bounded_and_preserves_first_takeover_evidence() -> None:
    source = MISSION.read_text(encoding="utf-8")

    assert "def maybe_recover_formation_center_target" in source
    assert "formation_target_recovery_max_attempts" in source
    assert 'event["action"] = "exhausted"' in source
    assert 'self.planner_command_quiesce("formation_target_recovery_exhausted")' in source
    assert "self.publish_formation_center_goal(reset_planner_markers=False)" in source
    assert "planner_markers_reset" in source
    assert "formation_target_recovery" in source


def test_formation_target_recovery_is_opt_in_for_the_stable_swarm_baseline() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert 'EGO_GATE_FORMATION_TARGET_RECOVERY_MAX_ATTEMPTS="${EGO_GATE_FORMATION_TARGET_RECOVERY_MAX_ATTEMPTS:-0}"' in source
    formation_case = source.split("swarm_formation|swarm-formation|formation)", 1)[1].split(";;", 1)[0]
    assert 'EGO_GATE_FORMATION_TARGET_RECOVERY_MAX_ATTEMPTS="2"' not in formation_case
    assert "--formation-target-recovery-max-attempts" in source
    assert '"mission_target_recovery"' in source
