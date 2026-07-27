import json
from pathlib import Path
import sys


if str(Path(__file__).resolve().parents[2]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import argparse
import tempfile

from CoAgent.runtime import mosim_agent_runtime as runtime


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "CoAgent" / "protocol"


CANONICAL_TASK_CLASSES = {
    "simple_message",
    "clear_task",
    "complicated_task",
    "complex_task",
    "chaotic_incident",
    "disordered_task",
    "long_running_task",
}

CANONICAL_STATES = {
    "planned",
    "ready",
    "working",
    "input_required",
    "auth_required",
    "review_required",
    "blocked",
    "failed",
    "completed",
    "canceled",
    "rejected",
    "superseded",
}

RUNTIME_STATE_ALIASES = {
    "queued",
    "claimed",
    "running",
    "done",
    "done_with_concerns",
    "cancelled",
}


def load_schema(name: str) -> dict:
    return json.loads((PROTOCOL / name).read_text(encoding="utf-8"))


def assert_required_fields(schema: dict, payload: dict) -> None:
    missing = [field for field in schema.get("required", []) if field not in payload or payload[field] in (None, "")]
    assert not missing, missing


def test_task_packet_schema_exposes_canonical_task_classes() -> None:
    schema = load_schema("task_packet_schema.json")

    assert set(schema["$defs"]["task_class"]["enum"]) == CANONICAL_TASK_CLASSES
    for field in [
        "project_goal",
        "phase_objective",
        "canonical_task_goal",
        "conversation_objective",
        "accountable_owner",
        "definition_of_done",
        "appetite",
        "circuit_breaker",
        "checkpoint_plan",
        "escalation_conditions",
        "review_gates",
        "worktree_path",
        "branch_or_base",
        "merge_owner",
        "close_condition",
        "review_owner",
        "human_review_points",
        "git_status",
    ]:
        assert field in schema["properties"]


def test_result_packet_schema_exposes_canonical_states_and_aliases() -> None:
    schema = load_schema("result_packet_schema.json")

    canonical = set(schema["$defs"]["canonical_status"]["enum"])
    accepted_statuses = set(schema["properties"]["status"]["enum"])

    assert canonical == CANONICAL_STATES
    assert CANONICAL_STATES <= accepted_statuses
    assert RUNTIME_STATE_ALIASES <= accepted_statuses
    assert set(schema["$defs"]["task_class"]["enum"]) == CANONICAL_TASK_CLASSES


def test_protocol_readme_names_the_goal_hierarchy_and_v1_limit() -> None:
    readme = (PROTOCOL / "README.md").read_text(encoding="utf-8")

    for term in [
        "Project Goal",
        "Canonical Task Goal",
        "Conversation Objective",
        "Subagent Objective",
        "PMO/main -> DispatchCenter -> department or dedicated task conversation -> short-lived subagent",
    ]:
        assert term in readme


def test_runtime_exports_schema_required_packet_fields() -> None:
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        db = Path(tmp) / "tasks.sqlite3"
        events = Path(tmp) / "events.jsonl"
        task_id = "protocol_vocabulary_runtime_export"
        runtime.create_task(
            argparse.Namespace(
                db=db,
                events=events,
                task_id=task_id,
                objective="Verify runtime packet exports match protocol schema requirements",
                role="Verification",
                read_scope=["CoAgent/protocol"],
                write_scope=["Results/tmp"],
                acceptance="runtime exports required fields",
                stop_condition="test passes",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "task_class": "long_running_task",
                        "canonical_task_goal": "Verify runtime packet exports match protocol schema requirements",
                        "conversation_objective": "Export packets for schema smoke",
                        "accountable_owner": "Verification",
                        "definition_of_done": "required fields present",
                        "appetite": "one test",
                        "circuit_breaker": "missing field",
                        "checkpoint_plan": "single checkpoint",
                        "worktree_path": "worktrees/verification/protocol-vocabulary",
                        "branch_or_base": "main",
                        "merge_owner": "GitIntegrator",
                        "close_condition": "review accepted",
                        "review_owner": "Verification",
                        "human_review_points": ["accept packet exports before transport expansion"],
                        "git_status": "worktree_ready",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=100,
                actor="Verification",
            )
        )
        runtime.update_task(
            argparse.Namespace(
                db=db,
                events=events,
                task_id=task_id,
                actor="Verification",
                claim_token="",
                summary="runtime packet export complete",
                data="",
            ),
            state="done",
            event_type="task_completed",
        )

        task_packet = runtime.export_task_packet(argparse.Namespace(db=db, events=events, task_id=task_id))
        result_packet = runtime.export_result_packet(argparse.Namespace(db=db, events=events, task_id=task_id))

    assert_required_fields(load_schema("task_packet_schema.json"), task_packet)
    assert_required_fields(load_schema("result_packet_schema.json"), result_packet)
    assert result_packet["canonical_status"] == "completed"
    assert task_packet["worktree_path"] == "worktrees/verification/protocol-vocabulary"
    assert result_packet["review_owner"] == "Verification"
