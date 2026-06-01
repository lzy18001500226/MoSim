"""Stand-alone parallel runner for the Universal Verifier (MMRubricAgent).

Skips the Fara solver entirely — pointed at any directory of webeval
trajectories (``web_surfer.log`` + ``screenshot{i}.png`` +
``{task_id}_final_answer.json``), it scores them with MMRubricAgent and
writes one ``scores/mmrubric_<threshold>-<max_imgs>-<keypt>.json`` per
trajectory.

The fastest way to validate the verifier pipeline end-to-end without
paying for a vLLM-backed solver run. Parallelised via
``multiprocessing.Pool``.

Usage (OM2W trajectories — task instruction comes from the OM2W JSON):

    python verify_trajectories.py \\
        --input /path/to/Fara/eval/runs/.../OnlineM2W_.../1/traj \\
        --task-data ../data/om2w/Online_Mind2Web_06042025.json \\
        --task-data-format om2w \\
        --eval-config ../../endpoint_configs/judge_active/prod \\
        --judge-model gpt-5 --o4mini-model o4-mini \\
        --processes 8

Usage (WebTailBench trajectories — instructions + precomputed rubrics
from the HF rubrics TSV):

    python verify_trajectories.py \\
        --input /path/to/Fara/eval/runs/.../WebTailBench_hf/full_v1/traj \\
        --task-data ../data/webtailbench/WebTailBench-v1-rubrics.tsv \\
        --task-data-format webtailbench \\
        --eval-config ../../endpoint_configs/judge_active/prod \\
        --judge-model gpt-5 --o4mini-model o4-mini \\
        --processes 8
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import logging
import multiprocessing as mp
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Repo paths so we can run this script directly without `pip install -e .`
_THIS = Path(__file__).resolve()
sys.path.insert(0, str(_THIS.parent.parent / "src"))
sys.path.insert(0, str(_THIS.parent.parent.parent / "src"))

from fara import FARA_ACTION_DEFINITIONS
from webeval.benchmarks.webtailbench.shared_data_adapter import create_datapoint
from webeval.oai_clients.graceful_client import GracefulRetryClient
from webeval.rubric_agent import (
    MMRubricAgent,
    MMRubricAgentConfig,
    MMRubricOutcomeResult,
    MMRubricResult,
)
from webeval.trajectory import Trajectory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(processName)s - %(message)s",
)
logger = logging.getLogger("verify_trajectories")


# ---------------------------------------------------------------------------
# Task-data loaders — produce a {task_id: {"id", "question", "init_url", ...}}
# dict from various source formats.
# ---------------------------------------------------------------------------

def load_om2w_tasks(path: Path) -> Dict[str, Dict[str, Any]]:
    with open(path) as f:
        rows = json.load(f)
    out: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        tid = str(r["task_id"])
        out[tid] = {
            "id": tid,
            "question": r.get("confirmed_task", ""),
            "init_url": r.get("website", ""),
            "level": r.get("level"),
        }
    return out


def load_webtailbench_tasks(path: Path) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            tid = (row.get("id") or "").strip()
            if not tid:
                continue
            example = {
                "id": tid,
                "question": row.get("task_summary", "").strip(),
                "init_url": row.get("init_url", "").strip(),
                "category": (row.get("benchmark") or "").strip(),
            }
            raw_rubric = (row.get("precomputed_rubric") or "").strip()
            if raw_rubric:
                try:
                    example["precomputed_rubric"] = json.loads(raw_rubric)
                except json.JSONDecodeError as exc:
                    logger.warning(f"[{tid}] failed to parse rubric JSON: {exc}")
            out[tid] = example
    return out


_TASK_LOADERS = {
    "om2w": load_om2w_tasks,
    "webtailbench": load_webtailbench_tasks,
}


# ---------------------------------------------------------------------------
# Per-trajectory verifier — runs in a worker process.
# ---------------------------------------------------------------------------

# Globals populated by ``_pool_init`` so each worker only builds its judge
# clients once, not once per task.
_GLOBAL_AGENT: Optional[MMRubricAgent] = None
_GLOBAL_TASKS: Optional[Dict[str, Dict[str, Any]]] = None
_GLOBAL_ARGS: Dict[str, Any] = {}


def _pool_init(args_dict: Dict[str, Any], tasks: Dict[str, Dict[str, Any]]):
    global _GLOBAL_AGENT, _GLOBAL_TASKS, _GLOBAL_ARGS
    _GLOBAL_TASKS = tasks
    _GLOBAL_ARGS = args_dict

    worker_logger = logging.getLogger("verify_trajectories.worker")
    o4mini_client = GracefulRetryClient.from_path(
        path=args_dict["eval_config"],
        logger=worker_logger,
        eval_model=args_dict["o4mini_model"],
    )
    gpt5_client = GracefulRetryClient.from_path(
        path=args_dict["eval_config"],
        logger=worker_logger,
        eval_model=args_dict["judge_model"],
    )
    _GLOBAL_AGENT = MMRubricAgent(
        config=MMRubricAgentConfig(
            o4mini_client=o4mini_client,
            gpt5_client=gpt5_client,
            max_images_per_criterion=args_dict["max_images_per_criterion"],
            majority_vote_instances=args_dict["majority_vote_instances"],
            redo_eval=args_dict["redo_eval"],
            rubric_score_threshold=args_dict["rubric_threshold"],
            action_definitions=FARA_ACTION_DEFINITIONS,
        )
    )
    worker_logger.info(
        f"Worker ready: gpt5={len(gpt5_client._clients)} clients, "
        f"o4mini={len(o4mini_client._clients)} clients"
    )


def _run_one(traj_dir_str: str) -> Dict[str, Any]:
    """Verify one trajectory. Returns a result dict (also writes scores JSON)."""
    traj_dir = Path(traj_dir_str)
    tid = traj_dir.name
    started = time.time()
    out: Dict[str, Any] = {"task_id": tid, "traj_dir": str(traj_dir)}
    score_path = (
        traj_dir / "scores"
        / f"mmrubric_{_GLOBAL_ARGS['rubric_threshold']}-"
        f"{_GLOBAL_ARGS['max_images_per_criterion']}-"
        f"{_GLOBAL_ARGS['mm_keypoint_score_threshold']}.json"
    )

    if score_path.exists() and not _GLOBAL_ARGS["redo_eval"]:
        out["status"] = "cached"
        out["score_path"] = str(score_path)
        return out

    try:
        task_data = _GLOBAL_TASKS.get(tid)
        if not task_data:
            out["status"] = "no_task_data"
            out["error"] = f"No task definition found for {tid}"
            return out

        traj = Trajectory.from_folder(traj_dir)
        if traj is None:
            out["status"] = "trajectory_unreadable"
            out["error"] = f"Trajectory.from_folder returned None for {traj_dir}"
            return out

        n_actions = len([e for e in traj.events if e.get("action")])
        if n_actions == 0:
            out["status"] = "no_actions"
            out["error"] = "Trajectory has no parsed actions"
            return out

        dp = create_datapoint(task_data, traj)
        input_dict = MMRubricAgent._extract_input_from_datapoint(
            dp,
            screenshots_dir=str(traj.path),
            redo_eval=_GLOBAL_ARGS["redo_eval"],
        )

        result = asyncio.run(_GLOBAL_AGENT._generate_reply(input_dict))
        if not isinstance(result, dict):
            raise TypeError(f"Expected dict from MMRubricAgent, got {type(result)}")
        if "error" in result:
            raise RuntimeError(f"Rubric agent reported error: {result.get('error')}")

        verification_results = _GLOBAL_AGENT._wrap_result(result)
        rubric_vr = next(vr for vr in verification_results if isinstance(vr, MMRubricResult))
        outcome_vr = next(vr for vr in verification_results if isinstance(vr, MMRubricOutcomeResult))

        # Build a flat dict (ChainMap isn't JSON-serializable). The rubric
        # verdict fields take precedence over the raw rubric_* passthrough
        # so callers can read top-level success/score directly. The error
        # taxonomy buckets (steps 9 / 9b / 10) live inside
        # ``intermediate_mm_rubric_steps`` — we lift them to top-level
        # ``error_taxonomy.*`` so downstream tooling doesn't have to peek
        # inside the intermediate dict.
        intermediate = result.get("intermediate_mm_rubric_steps") or {}
        error_taxonomy = {
            "first_point_of_failure": intermediate.get(
                "step9_first_point_of_failure"
            ),
            "task_verification_with_trajectory": intermediate.get(
                "step9b_task_verification_with_trajectory"
            ),
            "task_verification": intermediate.get("step10_task_verification"),
        }

        gpt_response_payload: Dict[str, Any] = {}
        for k, v in result.items():
            if k in (
                "intermediate_mm_rubric_steps",
                "majority_vote_metadata",
                "all_rubric_dicts",
                "all_scores_list",
            ):
                continue
            gpt_response_payload[f"rubric_{k}"] = v
        gpt_response_payload.update(
            {
                "rubric_is_success": int(rubric_vr.rubric_is_success),
                "outcome_success": outcome_vr.output_success,
                "outcome_reasoning": outcome_vr.reasoning,
                "outcome_primary_intent": outcome_vr.primary_intent,
                "rubric_total_max_points": rubric_vr.total_max_points,
                "rubric_total_earned_points": rubric_vr.total_earned_points,
                "error_taxonomy": error_taxonomy,
            }
        )
        outcome_pass = outcome_vr.output_success is True
        process_pass = bool(rubric_vr.rubric_is_success)
        criterion = _GLOBAL_ARGS["success_criterion"]
        if criterion == "process":
            top_score = int(process_pass)
        elif criterion == "both":
            top_score = int(outcome_pass and process_pass)
        else:  # "outcome" (default)
            top_score = int(outcome_pass)
        gpt_response_payload["success_criterion"] = criterion
        score_payload = {
            "score": top_score,
            "gpt_response_text": json.dumps(gpt_response_payload, default=str),
        }
        score_path.parent.mkdir(parents=True, exist_ok=True)
        with open(score_path, "w") as f:
            json.dump(score_payload, f, indent=2)

        # Surface the high-signal taxonomy bits in the per-task report row
        # so downstream tooling doesn't have to re-open the score JSON.
        fpof = error_taxonomy.get("first_point_of_failure") or {}
        tv = error_taxonomy.get("task_verification") or {}
        tvtraj = error_taxonomy.get("task_verification_with_trajectory") or {}
        out.update(
            status="ok",
            score_path=str(score_path),
            rubric_score=rubric_vr.score,
            rubric_total_max_points=rubric_vr.total_max_points,
            rubric_total_earned_points=rubric_vr.total_earned_points,
            rubric_is_success=bool(rubric_vr.rubric_is_success),
            outcome_success=outcome_vr.output_success,
            n_actions=n_actions,
            has_failure=fpof.get("has_failure"),
            first_failure_step=fpof.get("first_failure_step"),
            is_ambiguous=tv.get("is_ambiguous") or tvtraj.get("is_ambiguous"),
            ambiguity_codes=tv.get("ambiguity_codes")
            or tvtraj.get("ambiguity_codes"),
            is_invalid=tv.get("is_invalid") or tvtraj.get("is_invalid"),
            invalid_task_codes=tv.get("invalid_task_codes")
            or tvtraj.get("invalid_task_codes"),
        )
    except Exception as exc:
        out["status"] = "error"
        out["error"] = f"{type(exc).__name__}: {exc}"
        out["traceback"] = traceback.format_exc()
        logger.error(f"[{tid}] {out['error']}")
    finally:
        out["duration_sec"] = round(time.time() - started, 2)

    return out


# ---------------------------------------------------------------------------
# CLI / main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="Directory of trajectory subdirs to verify")
    p.add_argument("--task-data", required=True, help="Path to task-definitions file (JSON or TSV)")
    p.add_argument("--task-data-format", choices=sorted(_TASK_LOADERS), required=True)
    p.add_argument("--eval-config", required=True, help="Endpoint config dir for judge LLMs")
    p.add_argument("--judge-model", default="gpt-5", help="Multimodal judge model (default: gpt-5)")
    p.add_argument("--o4mini-model", default="o4-mini", help="Action-only judge model (default: o4-mini)")
    p.add_argument("--processes", type=int, default=4)
    p.add_argument("--rubric-threshold", type=float, default=0.8)
    p.add_argument(
        "--success",
        choices=("outcome", "process", "both"),
        default="outcome",
        help=(
            "Top-line success criterion. 'outcome' (default) reports the "
            "binary outcome_success — the metric Fara-7B numbers in the "
            "README are reported against. 'process' reports rubric_is_success "
            "(rubric_score >= --rubric-threshold) — more lenient, expect "
            "slightly higher numbers. 'both' requires both."
        ),
    )
    p.add_argument("--max-images-per-criterion", type=int, default=5)
    p.add_argument("--mm-keypoint-score-threshold", type=int, default=3)
    p.add_argument("--majority-vote-instances", type=int, default=1)
    p.add_argument("--redo-eval", action="store_true", help="Re-run even if cached score exists")
    p.add_argument("--limit", type=int, default=None, help="Verify at most N trajectories")
    p.add_argument(
        "--report",
        default=None,
        help="Write a JSONL summary of results to this path (default: <input>/verify_report.jsonl)",
    )
    return p.parse_args()


def find_trajectory_dirs(input_dir: Path) -> List[Path]:
    """A trajectory dir contains web_surfer.log AND a *_final_answer.json."""
    out: List[Path] = []
    for d in sorted(input_dir.iterdir()):
        if not d.is_dir():
            continue
        if (d / "web_surfer.log").exists() and any(d.glob("*_final_answer.json")):
            out.append(d)
    return out


def main():
    args = parse_args()
    input_dir = Path(args.input).resolve()
    if not input_dir.is_dir():
        raise SystemExit(f"--input is not a directory: {input_dir}")
    eval_config = Path(args.eval_config).resolve()
    if not eval_config.exists():
        raise SystemExit(f"--eval-config does not exist: {eval_config}")
    task_data_path = Path(args.task_data).resolve()
    if not task_data_path.exists():
        raise SystemExit(f"--task-data does not exist: {task_data_path}")

    tasks = _TASK_LOADERS[args.task_data_format](task_data_path)
    logger.info(f"Loaded {len(tasks)} task definitions from {task_data_path.name}")

    traj_dirs = find_trajectory_dirs(input_dir)
    if args.limit:
        traj_dirs = traj_dirs[: args.limit]
    logger.info(f"Found {len(traj_dirs)} trajectories under {input_dir}")
    if not traj_dirs:
        return

    args_dict = {
        "eval_config": str(eval_config),
        "judge_model": args.judge_model,
        "o4mini_model": args.o4mini_model,
        "rubric_threshold": args.rubric_threshold,
        "max_images_per_criterion": args.max_images_per_criterion,
        "mm_keypoint_score_threshold": args.mm_keypoint_score_threshold,
        "majority_vote_instances": args.majority_vote_instances,
        "redo_eval": args.redo_eval,
        "success_criterion": args.success,
    }

    report_path = Path(args.report) if args.report else input_dir / "verify_report.jsonl"
    logger.info(f"Report path: {report_path}")

    results: List[Dict[str, Any]] = []
    summary = {"ok": 0, "cached": 0, "error": 0, "no_task_data": 0, "no_actions": 0, "trajectory_unreadable": 0}

    started = time.time()
    if args.processes <= 1:
        _pool_init(args_dict, tasks)
        for d in traj_dirs:
            r = _run_one(str(d))
            results.append(r)
            summary[r["status"]] = summary.get(r["status"], 0) + 1
            _print_result_line(r)
    else:
        ctx = mp.get_context("spawn")
        with ctx.Pool(
            processes=args.processes,
            initializer=_pool_init,
            initargs=(args_dict, tasks),
        ) as pool:
            for r in pool.imap_unordered(_run_one, [str(d) for d in traj_dirs]):
                results.append(r)
                summary[r["status"]] = summary.get(r["status"], 0) + 1
                _print_result_line(r)

    elapsed = time.time() - started

    with open(report_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    logger.info("=" * 60)
    logger.info(f"DONE in {elapsed:.1f}s — {len(results)} trajectories")
    for k, v in summary.items():
        logger.info(f"  {k}: {v}")
    rubric_scores = [r["rubric_score"] for r in results if r.get("status") == "ok"]
    if rubric_scores:
        avg = sum(rubric_scores) / len(rubric_scores)
        n_pass = sum(1 for r in results if r.get("rubric_is_success"))
        n_outcome = sum(1 for r in results if r.get("outcome_success") is True)
        logger.info(f"  avg rubric_score: {avg:.3f}")
        logger.info(f"  rubric_is_success (≥{args.rubric_threshold}): {n_pass}/{len(rubric_scores)}")
        logger.info(f"  outcome_success: {n_outcome}/{len(rubric_scores)}")


def _print_result_line(r: Dict[str, Any]):
    tid = r["task_id"]
    status = r["status"]
    dur = r.get("duration_sec", "?")
    if status == "ok":
        logger.info(
            f"[OK] {tid} ({dur}s) — rubric={r.get('rubric_score'):.3f} "
            f"({r.get('rubric_total_earned_points')}/{r.get('rubric_total_max_points')}), "
            f"outcome={r.get('outcome_success')}"
        )
    elif status == "cached":
        logger.info(f"[CACHED] {tid}")
    else:
        logger.info(f"[{status.upper()}] {tid} ({dur}s) — {r.get('error', '')}")


if __name__ == "__main__":
    main()
