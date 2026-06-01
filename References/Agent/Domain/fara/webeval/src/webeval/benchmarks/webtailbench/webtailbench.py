"""WebTailBench — held-out evaluation scored by the Universal Verifier
(``MMRubricAgent``).

The dataset is downloaded from Hugging Face
(`microsoft/WebTailBench <https://huggingface.co/datasets/microsoft/WebTailBench>`_)
so the benchmark is reproducible outside of Azure.

Dataset schema
--------------
``WebTailBench.tsv`` is a 3-column TSV: ``benchmark``, ``id``,
``task_summary``. We map:

* ``id``            → example ``id`` (unique task identifier)
* ``task_summary``  → example ``question`` (task instruction)
* ``benchmark``     → example ``split`` (task category — one of
  ``flights``, ``hotels``, ``shopping``, …). This matches the split
  filtering used by :meth:`Benchmark.get_split_examples`.

``init_url`` is not shipped in the public WebTailBench TSV (yet); the
adapter defaults it to an empty string. ``precomputed_rubric`` is also
absent in the public release — the MMRubricAgent generates the rubric
from the task description at eval time.
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
from collections import ChainMap
from pathlib import Path
from typing import Any, Dict, List, Optional

from fara import FARA_ACTION_DEFINITIONS
from webeval.oai_clients import ChatCompletionClient
from webeval.trajectory import Trajectory
from webeval.rubric_agent import (
    MMRubricAgent,
    MMRubricAgentConfig,
    MMRubricOutcomeResult,
    MMRubricResult,
)

from ...benchmark import Benchmark
from ...evaluators import compute_rephrasing_consensus_score, safe_mean
from .shared_data_adapter import create_datapoint


_HF_REPO_ID = "microsoft/WebTailBench"
# Prefer the rubrics file: it carries the ``precomputed_rubric`` column the
# Universal Verifier consumes. ``WebTailBench.tsv`` (no rubrics) is kept as
# a fallback for older snapshots.
_RUBRICS_FILENAME = "WebTailBench-v1-rubrics.tsv"
_MAIN_FILENAME = "WebTailBench.tsv"
_REFUSALS_FILENAME = "WebTailBench-Refusals.tsv"


class WebTailBenchBenchmark(Benchmark):
    """Held-out evaluation on WebTailBench, scored with MMRubricAgent."""

    # Recognised values for the ``success_criterion`` argument.
    SUCCESS_OUTCOME = "outcome"
    SUCCESS_PROCESS = "process"
    SUCCESS_BOTH = "both"
    SUCCESS_CRITERIA = (SUCCESS_OUTCOME, SUCCESS_PROCESS, SUCCESS_BOTH)

    def __init__(
        self,
        data_dir: str,
        model_client: Optional[ChatCompletionClient] = None,
        o4mini_client: Optional[ChatCompletionClient] = None,
        gpt5_client: Optional[ChatCompletionClient] = None,
        include_refusals: bool = False,
        rubric_score_threshold: float = 0.8,
        mm_max_images: int = 5,
        mm_max_images_per_criterion: int = 5,
        mm_keypoint_score_threshold: int = 3,
        eval_rephrasings: bool = False,
        redo_eval: bool = False,
        majority_vote_instances: int = 1,
        success_criterion: str = SUCCESS_OUTCOME,
    ):
        super().__init__(name="WebTailBench", data_dir=str(data_dir))
        self.model_client = model_client
        self.o4mini_client = o4mini_client
        self.gpt5_client = gpt5_client
        self.include_refusals = include_refusals
        self.redo_eval = redo_eval
        self.majority_vote_instances = majority_vote_instances
        self.rubric_score_threshold = rubric_score_threshold
        self.mm_max_images = mm_max_images
        self.mm_max_images_per_criterion = mm_max_images_per_criterion
        self.mm_keypoint_score_threshold = mm_keypoint_score_threshold
        self.eval_rephrasings = eval_rephrasings
        self.rephrased_to_og_map: Dict[str, str] = {}
        if success_criterion not in self.SUCCESS_CRITERIA:
            raise ValueError(
                f"success_criterion must be one of {self.SUCCESS_CRITERIA}, "
                f"got {success_criterion!r}"
            )
        self.success_criterion = success_criterion

    # ------------------------------------------------------------------
    # Dataset
    # ------------------------------------------------------------------
    def _local_tsv(self, filename: str) -> Path:
        return Path(self.data_dir) / filename

    def download_dataset(self) -> None:
        """Fetch the WebTailBench TSVs from Hugging Face into ``data_dir``.

        Always pulls ``WebTailBench-v1-rubrics.tsv`` (the file with the
        ``precomputed_rubric`` column) so the Universal Verifier can score
        without re-generating rubrics. Falls back to plain
        ``WebTailBench.tsv`` only if the rubrics file is unavailable.
        """
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

        from huggingface_hub import hf_hub_download
        from huggingface_hub.utils import EntryNotFoundError

        files = [_RUBRICS_FILENAME]
        if self.include_refusals:
            files.append(_REFUSALS_FILENAME)

        for fname in files:
            local = self._local_tsv(fname)
            if local.exists():
                continue
            try:
                downloaded = hf_hub_download(
                    repo_id=_HF_REPO_ID,
                    filename=fname,
                    repo_type="dataset",
                    local_dir=str(self.data_dir),
                    local_dir_use_symlinks=False,
                )
            except EntryNotFoundError:
                if fname == _RUBRICS_FILENAME:
                    # Fallback for snapshots that haven't published the
                    # rubrics file yet. Verifier will warn loudly when the
                    # column turns out to be missing.
                    downloaded = hf_hub_download(
                        repo_id=_HF_REPO_ID,
                        filename=_MAIN_FILENAME,
                        repo_type="dataset",
                        local_dir=str(self.data_dir),
                        local_dir_use_symlinks=False,
                    )
                else:
                    raise
            assert Path(downloaded).exists(), f"Download failed: {downloaded}"

    def load_dataset(self) -> None:
        """Parse the TSV(s) into :attr:`examples`.

        Reads the ``precomputed_rubric`` column when present (the
        ``WebTailBench-v1-rubrics.tsv`` file ships one per task) and
        threads it onto each example so the Universal Verifier scores
        against the published rubric instead of regenerating one.
        """
        self.examples = []

        # Prefer the rubrics file; fall back to the plain TSV.
        primary = self._local_tsv(_RUBRICS_FILENAME)
        if not primary.exists():
            primary = self._local_tsv(_MAIN_FILENAME)
        paths: List[Path] = [primary]
        if self.include_refusals:
            paths.append(self._local_tsv(_REFUSALS_FILENAME))

        n_with_rubric = 0
        n_without_rubric = 0
        for tsv_path in paths:
            if not tsv_path.exists():
                raise FileNotFoundError(
                    f"Missing {tsv_path.name}. Call download_dataset() first or "
                    f"place it under {self.data_dir}/."
                )
            tag = "refusals" if tsv_path.name == _REFUSALS_FILENAME else None
            with open(tsv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    task_id = row.get("id") or row.get("subdir") or ""
                    if not task_id:
                        continue
                    category = (row.get("benchmark") or "").strip()
                    example = {
                        "id": task_id,
                        "question": row.get("task_summary", "").strip(),
                        "init_url": row.get("init_url", "").strip(),
                        # Category from the TSV → split for
                        # ``get_split_examples`` filtering.
                        "split": tag or category,
                        "category": category,
                    }

                    raw_rubric = (row.get("precomputed_rubric") or "").strip()
                    if raw_rubric:
                        try:
                            example["precomputed_rubric"] = json.loads(raw_rubric)
                            n_with_rubric += 1
                        except json.JSONDecodeError as e:
                            logging.getLogger("webeval.core").warning(
                                f"[WebTailBench] task {task_id}: failed to parse "
                                f"precomputed_rubric JSON ({e}); will regenerate."
                            )
                            n_without_rubric += 1
                    else:
                        n_without_rubric += 1

                    self.examples.append(example)

                    if self.eval_rephrasings:
                        rephrasings = row.get("task_rephrasings")
                        if rephrasings:
                            try:
                                rephr_list = json.loads(rephrasings)
                            except Exception:
                                rephr_list = []
                            for i, r in enumerate(rephr_list):
                                rex = {
                                    **example,
                                    "id": f"{task_id}_rephrased_{i}",
                                    "question": r,
                                }
                                self.examples.append(rex)
                                self.rephrased_to_og_map[rex["id"]] = example["id"]

        log = logging.getLogger("webeval.core")
        log.info(
            f"Loaded {len(self.examples)} WebTailBench examples from {self.data_dir} "
            f"({n_with_rubric} with precomputed_rubric, {n_without_rubric} without)"
        )
        if n_without_rubric > 0:
            log.warning(
                f"[WebTailBench] {n_without_rubric}/{len(self.examples)} examples are "
                "MISSING precomputed_rubric — the Universal Verifier will regenerate "
                "rubrics for them, which is NOT the intended reproducible flow. Make "
                f"sure {_RUBRICS_FILENAME} is present under {self.data_dir}."
            )

    def get_split_examples(self, split: Optional[str]) -> List[Dict[str, Any]]:
        if split is None or split == "*" or split == "":
            return self.examples
        return [ex for ex in self.examples if ex.get("split") == split]

    # ------------------------------------------------------------------
    # Evaluation — wraps the MMRubricAgent pipeline (Universal Verifier)
    # ------------------------------------------------------------------
    async def evaluate_by_rubric_evaluator(
        self, task_data: Dict[str, Any], candidate: Trajectory
    ):
        """Run the multimodal rubric pipeline on a candidate Trajectory.

        Converts the trajectory to a DataPoint, invokes
        ``MMRubricAgent._generate_reply`` directly, and returns rubric
        and outcome scores. Retries up to 3 times on transient errors.
        """
        _task_logger = logging.getLogger("webeval.core").getChild(
            str(task_data.get("id", "unknown"))
        )

        dp = create_datapoint(task_data, candidate)

        agent = MMRubricAgent(
            config=MMRubricAgentConfig(
                o4mini_client=self.o4mini_client or self.model_client,
                gpt5_client=self.gpt5_client or self.model_client,
                max_images_per_criterion=self.mm_max_images_per_criterion,
                screenshots_dir=str(candidate.path),
                majority_vote_instances=self.majority_vote_instances,
                redo_eval=self.redo_eval,
                rubric_score_threshold=self.rubric_score_threshold,
                action_definitions=FARA_ACTION_DEFINITIONS,
            )
        )

        input_dict = MMRubricAgent._extract_input_from_datapoint(
            dp,
            screenshots_dir=str(candidate.path),
            redo_eval=self.redo_eval,
        )

        max_retries = 3
        last_error: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                result = await agent._generate_reply(input_dict)

                if not isinstance(result, dict):
                    raise TypeError(
                        f"Expected dict from _generate_reply, got {type(result)}: {result}"
                    )
                if "error" in result:
                    raise RuntimeError(
                        f"Rubric generation failed: {result.get('error')}"
                    )

                verification_results = agent._wrap_result(result)
                rubric_vr = next(
                    vr for vr in verification_results if isinstance(vr, MMRubricResult)
                )
                outcome_vr = next(
                    vr for vr in verification_results
                    if isinstance(vr, MMRubricOutcomeResult)
                )

                # Persist the rubric back to the trajectory's task_data.json
                # under ``precomputed_rubric`` for future cached runs.
                try:
                    candidate_task_data_path = candidate.path / "task_data.json"
                    if candidate_task_data_path.exists():
                        with open(candidate_task_data_path, "r") as f:
                            candidate_data = json.load(f)
                    else:
                        candidate_data = {}
                    if self.redo_eval or "precomputed_rubric" not in candidate_data:
                        candidate_data["precomputed_rubric"] = {
                            k: v for k, v in result.items()
                            if k not in (
                                "intermediate_mm_rubric_steps",
                                "majority_vote_metadata",
                                "all_rubric_dicts",
                                "all_scores_list",
                            )
                        }
                    if (
                        result.get("intermediate_mm_rubric_steps") is not None
                        or self.redo_eval
                    ):
                        candidate_data["intermediate_mm_rubric_steps"] = result.get(
                            "intermediate_mm_rubric_steps"
                        )
                    if (
                        result.get("majority_vote_metadata") is not None
                        or self.redo_eval
                    ):
                        candidate_data["majority_vote_metadata"] = result.get(
                            "majority_vote_metadata"
                        )
                    with open(candidate_task_data_path, "w") as f:
                        json.dump(candidate_data, f, indent=4)
                    _task_logger.info(
                        f"[Rubric] Saved rubric results to {candidate_task_data_path}"
                    )
                except Exception as e:
                    _task_logger.warning(
                        f"[Rubric] Failed to save rubric results to {candidate.path}: {e}"
                    )

                return ChainMap(
                    {f"rubric_{k}": v for k, v in result.items()},
                    {
                        "rubric_is_success": int(rubric_vr.rubric_is_success),
                        "outcome_success": outcome_vr.output_success,
                        "outcome_reasoning": outcome_vr.reasoning,
                        "outcome_primary_intent": outcome_vr.primary_intent,
                    },
                )

            except Exception as e:
                last_error = e
                _task_logger.error(
                    f"[Rubric] Attempt {attempt + 1}/{max_retries} failed: {e}"
                )

        _task_logger.error(
            f"[Rubric] Failed after {max_retries} attempts. Last error: {last_error}"
        )
        return ChainMap(
            {
                "rubric_error": str(last_error),
                "rubric_total_earned_points": 0,
                "rubric_total_max_points": 1,
            },
            {"rubric_is_success": 0, "outcome_success": False},
        )

    async def all_evals(self, task_data: Dict[str, Any], candidate: Trajectory):
        results = await asyncio.gather(
            self.evaluate_by_rubric_evaluator(task_data, candidate)
        )
        return dict(ChainMap(*results))

    @staticmethod
    def _get_action_name(evt: Dict[str, Any]) -> str:
        args = evt.get("arguments") or {}
        name = args.get("action", evt.get("action", ""))
        if name in ("stop_and_answer_question", "stop_execution"):
            name = "terminate"
        return name or ""

    def evaluator(self, task_data: Dict[str, Any], candidate: Trajectory) -> Any:
        action_events = [evt for evt in candidate.events if evt.get("action")]
        if not action_events:
            return 0, json.dumps(
                {
                    "verifier_reasoning": "No actions found in the trajectory.",
                    "verifier_success": False,
                }
            )

        last_action = self._get_action_name(action_events[-1])
        if last_action != "terminate" and not last_action.startswith("finished("):
            return 0, json.dumps(
                {
                    "verifier_reasoning": 'The last action must be "terminate".',
                    "verifier_success": False,
                }
            )
        n_actions = len(action_events)
        n_screenshots = len(candidate.answer.screenshots)
        if abs(n_screenshots - n_actions) >= 2:
            logging.getLogger("webeval.core").warning(
                f"[Evaluator] Actions/screenshots mismatch: actions={n_actions}, "
                f"screenshots={n_screenshots} (task={task_data.get('id', 'unknown')})"
            )
            return 0, json.dumps(
                {
                    "verifier_reasoning": (
                        f"Actions and screenshots mismatch in length by more than 1 "
                        f"(actions={n_actions}, screenshots={n_screenshots})."
                    ),
                    "verifier_success": False,
                }
            )
        result = asyncio.run(self.all_evals(task_data, candidate))
        outcome_pass = result.get("outcome_success") is True
        process_pass = bool(result.get("rubric_is_success"))
        if self.success_criterion == self.SUCCESS_PROCESS:
            is_success = process_pass
        elif self.success_criterion == self.SUCCESS_BOTH:
            is_success = outcome_pass and process_pass
        else:  # SUCCESS_OUTCOME (default)
            is_success = outcome_pass
        result["is_success"] = int(is_success)
        result["success_criterion"] = self.success_criterion
        result["final_answer"] = candidate.answer.final_answer
        return result["is_success"], json.dumps(result)

    # ------------------------------------------------------------------
    # Metrics / identity
    # ------------------------------------------------------------------
    def exec_hash(self) -> str:
        return f"{super().exec_hash()}_hf"

    def eval_hash(self) -> str:
        return (
            f"mmrubric_{self.rubric_score_threshold}-"
            f"{self.mm_max_images}-{self.mm_keypoint_score_threshold}"
        )

    def compute_aggregate_metrics(self, scores: List[Any]) -> Dict[str, Any]:
        agg_scores = super().compute_aggregate_metrics(scores)

        id_to_split = {ex["id"]: ex.get("split") for ex in self.examples}
        split_to_scores: Dict[str, List] = {}
        for score in scores:
            split = id_to_split.get(score.qid)
            if split is not None:
                split_to_scores.setdefault(split, []).append(score.score)
        for split, split_scores in split_to_scores.items():
            agg_scores[f"accuracy_{split}"] = safe_mean(split_scores)
            agg_scores[f"samples_{split}"] = len(split_scores)

        if self.eval_rephrasings:
            valid_scores = [s for s in scores if s.score is not None]
            consensus_scores = compute_rephrasing_consensus_score(
                valid_scores, self.rephrased_to_og_map, only_og_correct=False
            )
            agg_scores.update(consensus_scores)

        return agg_scores
