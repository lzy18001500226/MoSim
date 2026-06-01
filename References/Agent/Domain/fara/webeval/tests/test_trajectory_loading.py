"""Tests for ``webeval.trajectory.Trajectory`` against the bundled
example trajectory at ``webeval/data/example_trajectory``.

The example is a real WebTailBench run (``alltrails_find_23``) checked
into the repo so the loader has a stable fixture — no network access,
no LLM calls, no hard-coded absolute paths.
"""

from __future__ import annotations

from pathlib import Path

import pytest


EXAMPLE_TRAJECTORY_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "example_trajectory"
)


@pytest.fixture(scope="module")
def example_traj_path() -> Path:
    assert EXAMPLE_TRAJECTORY_DIR.is_dir(), (
        f"Missing fixture dir: {EXAMPLE_TRAJECTORY_DIR}"
    )
    return EXAMPLE_TRAJECTORY_DIR


def test_required_trajectory_files_present(example_traj_path: Path):
    """The fixture dir must contain the file set the current webeval
    pipeline produces — ``verify_trajectories.find_trajectory_dirs``
    keys off ``web_surfer.log`` + ``*_final_answer.json``.
    """
    assert (example_traj_path / "web_surfer.log").exists()
    assert (example_traj_path / "core.log").exists()
    assert (example_traj_path / "times.json").exists()
    assert (example_traj_path / "task_data.json").exists()

    answer_files = list(example_traj_path.glob("*_final_answer.json"))
    assert len(answer_files) == 1, f"expected 1 final-answer file, got {answer_files}"

    screenshots = sorted(example_traj_path.glob("screenshot_*.png"))
    assert len(screenshots) >= 1

    scores = list((example_traj_path / "scores").glob("*.json"))
    assert len(scores) >= 1


def test_from_folder_returns_none_on_missing_log(tmp_path: Path):
    """``Trajectory.from_folder`` swallows exceptions and returns None;
    an empty dir has no web_surfer.log, so the call must not raise."""
    from webeval.trajectory import Trajectory

    assert Trajectory.from_folder(tmp_path) is None


def test_from_folder_loads_example_trajectory(example_traj_path: Path):
    """Real trajectory must load, parse events, and resolve screenshot
    paths relative to the trajectory directory."""
    from webeval.trajectory import Trajectory

    traj = Trajectory.from_folder(example_traj_path, gpt_solver=True)
    assert traj is not None, "from_folder returned None on a valid trajectory"

    # web_surfer.log has interleaved SummarizedAction (action=null) and
    # WebSurfer (actual action) rows. With gpt_solver=True the loader
    # filters to source==WebSurfer AND action!=null → exactly one event
    # per taken step. The example has 4 steps.
    assert len(traj.events) == 4
    action_names = [e.get("action") for e in traj.events]
    assert action_names == [
        "input_text",
        "click",
        "pause_and_memorize_fact",
        "stop_and_answer_question",
    ]

    # FinalAnswer was loaded from the *_final_answer.json file.
    assert traj.answer is not None
    assert traj.answer.final_answer.startswith("The two standout waterfalls")
    assert not traj.is_aborted

    # Screenshots listed in the answer JSON are resolved to abs paths
    # rooted at the trajectory dir (is_rel_paths=True → joined in __init__).
    assert len(traj.screenshots) == 4
    for s in traj.screenshots:
        p = Path(s)
        assert p.is_absolute(), f"screenshot path should be absolute: {s}"
        assert p.parent == example_traj_path
        assert p.name.startswith("screenshot_") and p.name.endswith(".png")
        assert p.exists(), f"screenshot file missing: {p}"


def test_repr_describes_screenshots_and_actions(example_traj_path: Path):
    """``repr(Trajectory)`` reports the counts debugging scripts rely on."""
    from webeval.trajectory import Trajectory

    traj = Trajectory.from_folder(example_traj_path, gpt_solver=True)
    assert traj is not None
    r = repr(traj)
    assert "4 screenshots" in r
    # gpt_solver=True short-circuits actions/thoughts construction, so
    # the "actions" count in repr is 0 in this mode — verify stable.
    assert "0 actions" in r


if __name__ == "__main__":
    # Keep the old ad-hoc behaviour: running this file directly prints a
    # human-readable summary of the example trajectory. Useful for
    # eyeballing parse output without pytest.
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
    from webeval.trajectory import Trajectory

    traj = Trajectory(EXAMPLE_TRAJECTORY_DIR, gpt_solver=True)
    print(repr(traj))
    print(f"events: {len(traj.events)}")
    print(f"screenshots: {len(traj.screenshots)}")
    print(f"answer: {traj.answer.final_answer[:120]}...")
