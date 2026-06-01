"""Tests for ``webtailbench.shared_data_adapter.create_datapoint``.

Two flavours of fixture:

* ``_make_trajectory_dir`` — synthesizes a minimal fara ``Trajectory``
  on disk (action log + fake screenshots + FinalAnswer JSON) and
  verifies the DataPoint it produces matches what
  ``MMRubricAgent._extract_input_from_datapoint`` expects.
* ``webeval/data/example_trajectory`` — a real WebTailBench run
  (``alltrails_find_23``) checked in to the repo. The real-trajectory
  test exercises the adapter's ``task_data.json`` precomputed-rubric
  fallback path, which the synthetic fixture cannot reach.
"""

from __future__ import annotations

import json
from pathlib import Path

EXAMPLE_TRAJECTORY_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "example_trajectory"
)


def _make_trajectory_dir(root: Path, n_actions: int = 2) -> Path:
    d = root / "sample_traj"
    d.mkdir(parents=True, exist_ok=True)

    # web_surfer.log: one action per line, fara's format (dict with action/arguments/url).
    log = d / "web_surfer.log"
    events = []
    for i in range(n_actions):
        events.append(
            {
                # ``gpt_solver=True`` in ``Trajectory`` filters on source==WebSurfer.
                "source": "WebSurfer",
                "action": "click" if i < n_actions - 1 else "stop_execution",
                "url": f"https://example.com/step_{i}",
                "arguments": {
                    "action": "click" if i < n_actions - 1 else "stop_execution",
                    "thoughts": f"thinking at step {i}",
                    "screen_description": f"screen at step {i}",
                    "target": f"button_{i}" if i < n_actions - 1 else None,
                },
            }
        )
    log.write_text("\n".join(json.dumps(e) for e in events) + "\n")

    # Fake screenshots on disk — content not validated by the adapter.
    screenshots = []
    for i in range(n_actions):
        p = d / f"screenshot_{i}.png"
        p.write_bytes(b"\x89PNG\r\n\x1a\n")  # PNG signature, harmless for tests
        screenshots.append(p.name)

    # FinalAnswer JSON — follows fara's FinalAnswer schema.
    answer = {
        "final_answer": "done",
        "env_state_json": "{}",
        "env_state_raw": "",
        "screenshots": screenshots,
        "is_aborted": False,
        "is_rel_paths": True,
        "token_usage": {},
    }
    (d / "_answer.json").write_text(json.dumps(answer))
    return d


def test_create_datapoint_normalizes_screenshots_and_actions(tmp_path):
    from webeval.benchmarks.webtailbench.shared_data_adapter import create_datapoint
    from webeval.trajectory import Trajectory

    traj_dir = _make_trajectory_dir(tmp_path, n_actions=3)
    traj = Trajectory(traj_dir, gpt_solver=True)

    task_data = {
        "id": "sample_traj",
        "question": "pretend to click buttons",
        "init_url": "https://example.com",
    }
    dp = create_datapoint(task_data, traj)

    assert dp.task.task_id == "sample_traj"
    assert dp.task.instruction == "pretend to click buttons"
    assert dp.task.environment_config["init_url"] == "https://example.com"

    summaries = dp.solver_log.get_step_summaries()
    assert len(summaries) == 3
    # Last action must have been normalized stop_execution → terminate.
    assert summaries[-1].action_name == "terminate"
    # Screenshot indices must be 1-based and match action index.
    for i, s in enumerate(summaries, start=1):
        assert s.index == i
        assert s.screenshot_path.endswith(f"screenshot_{i}.png")


def test_create_datapoint_handles_missing_init_url(tmp_path):
    """Task_data without ``init_url`` should default to an empty string
    rather than crashing — WebTailBench TSV does not ship init_url."""
    from webeval.benchmarks.webtailbench.shared_data_adapter import create_datapoint
    from webeval.trajectory import Trajectory

    traj_dir = _make_trajectory_dir(tmp_path, n_actions=1)
    traj = Trajectory(traj_dir, gpt_solver=True)

    dp = create_datapoint({"id": "x", "question": "noop"}, traj)
    assert dp.task.environment_config["init_url"] == ""


def test_create_datapoint_from_example_trajectory():
    """End-to-end: load the checked-in example trajectory via
    ``Trajectory.from_folder`` and convert it with ``create_datapoint``.

    Intentionally passes *no* ``precomputed_rubric`` in the task_data dict
    so the adapter has to fall back to reading ``task_data.json`` from
    the trajectory directory (the real-run code path). The example's
    task_data.json carries a ``precomputed_rubric`` object — it must land
    on ``dp.task.metadata``, which is what the Universal Verifier reads.
    """
    from webeval.benchmarks.webtailbench.shared_data_adapter import create_datapoint
    from webeval.trajectory import Trajectory

    assert EXAMPLE_TRAJECTORY_DIR.is_dir(), (
        f"Missing fixture dir: {EXAMPLE_TRAJECTORY_DIR}"
    )

    traj = Trajectory.from_folder(EXAMPLE_TRAJECTORY_DIR, gpt_solver=True)
    assert traj is not None, "from_folder returned None on a valid trajectory"

    task_data = {
        "id": "alltrails_find_23",
        "question": (
            "Identify the best waterfalls to see while hiking "
            "in the Superstition Mountains, Arizona"
        ),
        # Intentionally omit init_url + precomputed_rubric.
    }
    dp = create_datapoint(task_data, traj)

    # Task fields populated from the supplied task_data.
    assert dp.task.task_id == "alltrails_find_23"
    assert dp.task.instruction.startswith("Identify the best waterfalls")
    # Missing init_url defaults to "".
    assert dp.task.environment_config["init_url"] == ""

    # Adapter must have fallen back to task_data.json on disk for the rubric.
    rubric = dp.task.metadata.get("precomputed_rubric")
    assert isinstance(rubric, dict), (
        f"expected precomputed_rubric dict from task_data.json, got {type(rubric)}"
    )
    assert "items" in rubric and rubric.get("total_max_points"), (
        f"rubric missing expected fields: {list(rubric.keys())}"
    )

    # Step summaries: 4 actions, normalized screenshot filenames, terminal
    # action rewritten stop_and_answer_question → terminate.
    summaries = dp.solver_log.get_step_summaries()
    assert len(summaries) == 4
    for i, s in enumerate(summaries, start=1):
        assert s.index == i
        assert s.screenshot_path.endswith(f"screenshot_{i}.png")
    assert summaries[-1].action_name == "terminate"

    # Outcome passthrough of the final answer.
    assert dp.solver_log.outcome is not None
    assert dp.solver_log.outcome.answer.startswith("The two standout waterfalls")
