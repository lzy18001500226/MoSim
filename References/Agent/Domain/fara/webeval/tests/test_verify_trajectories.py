"""Smoke tests for ``webeval/scripts/verify_trajectories.py``.

The script is the Universal Verifier's stand-alone runner. It can't be
imported as a normal module (lives under ``scripts/``, not ``src/``), so
we load it via :mod:`importlib.util`. Three layers of coverage:

1. **Pure helpers** — ``find_trajectory_dirs`` and
   ``load_webtailbench_tasks`` don't need the LLM stack and are tested
   directly.
2. **End-to-end with a stub agent** — ``_run_one`` is exercised against
   the checked-in example trajectory with ``_GLOBAL_AGENT`` monkey-
   patched to a fake. This verifies the data-prep pipeline
   (Trajectory → DataPoint → input_dict) and the score-file writer
   without incurring any LLM cost.
3. **Live LLM** — a skipped-by-default variant that hits the real
   verifier. Gate via ``FARA_VERIFY_LIVE_TEST=1`` and a valid
   ``--eval-config`` env (``FARA_VERIFY_EVAL_CONFIG=/path/to/configs``).
"""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import shutil
import sys
import types
from pathlib import Path
from typing import Any, Dict

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_PATH = REPO_ROOT / "webeval" / "scripts" / "verify_trajectories.py"
EXAMPLE_TRAJECTORY_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "example_trajectory"
)
EXAMPLE_TASK_ID = "alltrails_find_23"


# ---------------------------------------------------------------------------
# Module loader — ``verify_trajectories.py`` lives under ``scripts/`` and
# isn't on any package path. Load it once per test session.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def verify_mod() -> types.ModuleType:
    assert SCRIPT_PATH.is_file(), f"Missing script: {SCRIPT_PATH}"
    spec = importlib.util.spec_from_file_location(
        "verify_trajectories_under_test", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # Ensure sibling packages (webeval, fara) are importable — the script
    # does its own sys.path tweaking at import time, so nothing extra is
    # required here, but conftest.py already covers local dev usage too.
    sys.modules["verify_trajectories_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_find_trajectory_dirs_picks_up_example(tmp_path: Path, verify_mod):
    """The example trajectory satisfies the discovery predicate
    (``web_surfer.log`` + ``*_final_answer.json``)."""
    parent = tmp_path / "traj"
    parent.mkdir()
    shutil.copytree(EXAMPLE_TRAJECTORY_DIR, parent / EXAMPLE_TASK_ID)

    # A sibling dir without a web_surfer.log must be ignored.
    (parent / "not_a_trajectory").mkdir()
    (parent / "not_a_trajectory" / "README.txt").write_text("ignore me")

    found = verify_mod.find_trajectory_dirs(parent)
    assert [d.name for d in found] == [EXAMPLE_TASK_ID]


def test_load_webtailbench_tasks_parses_rubric(tmp_path: Path, verify_mod):
    """The WebTailBench TSV loader must pull ``id``, ``task_summary``,
    ``init_url``, and JSON-decode ``precomputed_rubric``."""
    tsv = tmp_path / "WebTailBench-v1-rubrics.tsv"
    rubric = {
        "items": [{"criterion": "sample", "max_points": 1}],
        "total_max_points": 1,
    }
    with open(tsv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "benchmark",
                "id",
                "task_summary",
                "init_url",
                "precomputed_rubric",
            ],
            delimiter="\t",
        )
        w.writeheader()
        w.writerow(
            {
                "benchmark": "things_to_do",
                "id": EXAMPLE_TASK_ID,
                "task_summary": (
                    "Identify the best waterfalls to see while hiking in the "
                    "Superstition Mountains, Arizona"
                ),
                "init_url": "",
                "precomputed_rubric": json.dumps(rubric),
            }
        )

    tasks = verify_mod.load_webtailbench_tasks(tsv)
    assert EXAMPLE_TASK_ID in tasks
    task = tasks[EXAMPLE_TASK_ID]
    assert task["question"].startswith("Identify the best waterfalls")
    assert task["category"] == "things_to_do"
    assert task["precomputed_rubric"] == rubric


# ---------------------------------------------------------------------------
# End-to-end _run_one against the example trajectory (no LLM)
# ---------------------------------------------------------------------------

class _StubAgent:
    """Minimal stand-in for ``MMRubricAgent`` used by ``_run_one``.

    Returns a fixed rubric+outcome verdict so we can exercise the full
    data-prep pipeline (Trajectory → DataPoint → input_dict) and the
    score-file writer without hitting an LLM.
    """

    async def _generate_reply(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        # Record the input so the test can assert on it.
        self.last_input = input_dict
        return {
            "items": [{"criterion": "stubbed", "earned_points": 1, "max_points": 1}],
            "total_max_points": 1,
            "total_earned_points": 1,
            "outcome_verification": {
                "output_success": True,
                "reasoning": "stubbed",
                "primary_intent": "stubbed intent",
            },
            "intermediate_mm_rubric_steps": {
                "step9_first_point_of_failure": {
                    "has_failure": False,
                    "first_failure_step": None,
                },
                "step9b_task_verification_with_trajectory": {
                    "is_ambiguous": False,
                    "ambiguity_codes": [],
                    "is_invalid": False,
                    "invalid_task_codes": [],
                },
                "step10_task_verification": {
                    "is_ambiguous": False,
                    "ambiguity_codes": [],
                    "is_invalid": False,
                    "invalid_task_codes": [],
                },
            },
            "majority_vote_metadata": {},
        }

    def _wrap_result(self, result):
        from webeval.rubric_agent.data_point import (
            MajorityVoteMetadata,
            MMRubricOutcomeResult,
            MMRubricResult,
        )

        rubric_vr = MMRubricResult(
            score=1.0,
            reasoning="stubbed",
            verifier_name="mm_rubric",
            total_max_points=result["total_max_points"],
            total_earned_points=result["total_earned_points"],
            rubric_is_success=True,
            intermediate_mm_rubric_steps=result["intermediate_mm_rubric_steps"],
            majority_vote_metadata=MajorityVoteMetadata(),
        )
        outcome_vr = MMRubricOutcomeResult(
            score=1.0,
            reasoning="stubbed",
            verifier_name="mm_rubric_outcome",
            output_success=True,
            primary_intent="stubbed intent",
        )
        return [rubric_vr, outcome_vr]


def test_run_one_end_to_end_with_stubbed_agent(tmp_path: Path, verify_mod):
    """``_run_one`` against a copy of the example trajectory must:

    * Find the task in ``_GLOBAL_TASKS``.
    * Load the Trajectory + convert to DataPoint + build the
      MMRubricAgent input dict (stubbed agent records the dict).
    * Write ``scores/mmrubric_<threshold>-<max_imgs>-<keypt>.json``.
    * Return a result row with ``status == "ok"`` plus success fields.
    """
    # Work on a copy so we don't pollute the checked-in fixture with new
    # score files the verifier writes.
    traj_dir = tmp_path / EXAMPLE_TASK_ID
    shutil.copytree(EXAMPLE_TRAJECTORY_DIR, traj_dir)

    stub = _StubAgent()
    verify_mod._GLOBAL_AGENT = stub
    verify_mod._GLOBAL_TASKS = {
        EXAMPLE_TASK_ID: {
            "id": EXAMPLE_TASK_ID,
            "question": (
                "Identify the best waterfalls to see while hiking in the "
                "Superstition Mountains, Arizona"
            ),
            "init_url": "",
            "category": "things_to_do",
        }
    }
    verify_mod._GLOBAL_ARGS = {
        "rubric_threshold": 0.8,
        "max_images_per_criterion": 5,
        "mm_keypoint_score_threshold": 3,
        "redo_eval": True,
        "success_criterion": "outcome",
    }

    out = verify_mod._run_one(str(traj_dir))

    # Top-line status
    assert out["status"] == "ok", out
    assert out["task_id"] == EXAMPLE_TASK_ID
    assert out["rubric_is_success"] is True
    assert out["outcome_success"] is True
    assert out["n_actions"] == 4

    # Score file is written under scores/mmrubric_*.json with the naming
    # convention the dashboard / post_eval_analysis expects.
    score_path = Path(out["score_path"])
    assert score_path.exists()
    assert score_path.name == "mmrubric_0.8-5-3.json"
    payload = json.loads(score_path.read_text())
    assert payload["score"] == 1  # outcome criterion
    gpt_payload = json.loads(payload["gpt_response_text"])
    assert gpt_payload["outcome_success"] is True
    assert gpt_payload["rubric_is_success"] == 1
    assert gpt_payload["success_criterion"] == "outcome"
    assert "error_taxonomy" in gpt_payload

    # The stub captured the input dict the real agent would have seen —
    # this is the contract the verifier relies on.
    inp = stub.last_input
    assert inp["task"].startswith("Identify the best waterfalls")
    assert inp["predicted_output"].startswith("The two standout waterfalls")
    assert inp["screenshots_dir"] == str(traj_dir)
    assert len(inp["actions_list"]) == 4
    assert len(inp["step_actions"]) == 4
    # The adapter reads the precomputed_rubric from task_data.json on
    # disk when task_data dict omits it — verify that propagated.
    assert isinstance(inp["precomputed_rubric"], dict)
    assert inp["precomputed_rubric"].get("total_max_points")


def test_run_one_reports_no_task_data(tmp_path: Path, verify_mod):
    """If the trajectory id isn't in ``_GLOBAL_TASKS`` the runner must
    fail soft with ``status='no_task_data'``, not raise."""
    traj_dir = tmp_path / EXAMPLE_TASK_ID
    shutil.copytree(EXAMPLE_TRAJECTORY_DIR, traj_dir)

    verify_mod._GLOBAL_AGENT = _StubAgent()
    verify_mod._GLOBAL_TASKS = {}  # empty
    verify_mod._GLOBAL_ARGS = {
        "rubric_threshold": 0.8,
        "max_images_per_criterion": 5,
        "mm_keypoint_score_threshold": 3,
        "redo_eval": True,
        "success_criterion": "outcome",
    }

    out = verify_mod._run_one(str(traj_dir))
    assert out["status"] == "no_task_data"


# ---------------------------------------------------------------------------
# Live LLM — gated, expensive; not run in CI.
# ---------------------------------------------------------------------------

def _resolve_live_eval_config(dst: Path) -> Path | None:
    """Resolve the ``--eval-config`` dir for the live test from env vars.

    ``GracefulRetryClient.from_path`` lists ``*.json`` directly under its
    ``--eval-config`` argument (non-recursive) and filters by the
    ``eval_model`` field, so the script needs a single flat dir
    containing BOTH the judge (gpt-5) and action-judge (o4-mini)
    endpoint configs.

    Supported env-var shapes:

    * ``FARA_VERIFY_EVAL_CONFIG`` — a single dir already containing
      both sets of configs. Used as-is.
    * ``FARA_VERIFY_JUDGE_CONFIG`` + ``FARA_VERIFY_O4MINI_CONFIG`` — two
      separate dirs; we symlink all ``*.json`` from each into ``dst``
      and return that merged dir.

    Returns ``None`` if no env vars are set (caller should skip the
    live test).
    """
    flat = os.environ.get("FARA_VERIFY_EVAL_CONFIG")
    if flat:
        p = Path(flat)
        return p if p.is_dir() else None

    judge_dir = os.environ.get("FARA_VERIFY_JUDGE_CONFIG")
    o4mini_dir = os.environ.get("FARA_VERIFY_O4MINI_CONFIG")
    if not (judge_dir and o4mini_dir):
        return None

    dst.mkdir(parents=True, exist_ok=True)
    for src_str in (judge_dir, o4mini_dir):
        src = Path(src_str)
        if not src.is_dir():
            return None
        for cfg in src.glob("*.json"):
            link = dst / cfg.name
            if not link.exists():
                link.symlink_to(cfg)
    return dst


@pytest.mark.skipif(
    os.environ.get("FARA_VERIFY_LIVE_TEST") != "1",
    reason="Set FARA_VERIFY_LIVE_TEST=1 to run the live verifier (hits real LLM endpoints)",
)
def test_verify_trajectories_live_llm(tmp_path: Path, verify_mod):
    """Actually call the real MMRubricAgent against the example
    trajectory. Skips unless env vars below are set:

    * ``FARA_VERIFY_LIVE_TEST=1`` (opt-in gate)
    * ``FARA_VERIFY_EVAL_CONFIG`` — flat dir with judge endpoint JSONs, OR
    * ``FARA_VERIFY_JUDGE_CONFIG`` + ``FARA_VERIFY_O4MINI_CONFIG`` —
      per-model dirs (merged via symlink into tmp_path).

    Optional overrides: ``FARA_VERIFY_JUDGE_MODEL`` (default ``gpt-5``),
    ``FARA_VERIFY_O4MINI_MODEL`` (default ``o4-mini``).
    """
    merged_eval_config = _resolve_live_eval_config(tmp_path / "eval_config")
    if merged_eval_config is None:
        pytest.skip(
            "Live verifier needs endpoint configs — set FARA_VERIFY_EVAL_CONFIG "
            "or FARA_VERIFY_JUDGE_CONFIG + FARA_VERIFY_O4MINI_CONFIG"
        )

    traj_dir = tmp_path / EXAMPLE_TASK_ID
    shutil.copytree(EXAMPLE_TRAJECTORY_DIR, traj_dir)

    args_dict = {
        "eval_config": str(merged_eval_config),
        "judge_model": os.environ.get("FARA_VERIFY_JUDGE_MODEL", "gpt-5"),
        "o4mini_model": os.environ.get("FARA_VERIFY_O4MINI_MODEL", "o4-mini"),
        "rubric_threshold": 0.8,
        "max_images_per_criterion": 5,
        "mm_keypoint_score_threshold": 3,
        "majority_vote_instances": 1,
        "redo_eval": True,
        "success_criterion": "outcome",
    }
    tasks = {
        EXAMPLE_TASK_ID: {
            "id": EXAMPLE_TASK_ID,
            "question": (
                "Identify the best waterfalls to see while hiking in the "
                "Superstition Mountains, Arizona"
            ),
            "init_url": "",
        }
    }
    verify_mod._pool_init(args_dict, tasks)
    out = verify_mod._run_one(str(traj_dir))
    assert out["status"] == "ok", out
    assert out["outcome_success"] is True, (
        "Expected live LLM to verify this trajectory succeeds — it "
        "correctly answers the waterfalls question."
    )
    score_path = Path(out["score_path"])
    assert score_path.exists()
    payload = json.loads(score_path.read_text())
    assert payload["score"] in (0, 1)  # hard gate: score file parseable
