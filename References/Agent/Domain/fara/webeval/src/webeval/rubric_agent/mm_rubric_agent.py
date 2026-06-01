"""
================================================================================
Scoring Summary — Multimodal Rubric Verification Pipeline (v3_mm)
================================================================================

This module implements a multi-step rubric-based scoring pipeline that evaluates
web navigation agent trajectories using both action logs and screenshot evidence.
It produces two independent signals:

  - PROCESS REWARD (Steps 0–7): A fine-grained rubric score reflecting how well
    the agent executed each sub-goal. Expressed as earned_points / max_points.
  - OUTCOME REWARD (Step 8): A binary success/failure judgment on whether the
    task was accomplished from the user's perspective (output_success: bool).

Regarding failure analysis:
  - POINTS OF FAILURE (Step 9a): Identifies all failure points in the
    trajectory using a structured error taxonomy (10 categories), pinpoints
    the first (earliest) failure step, and classifies each failure by type
    and severity.
  - TRAJECTORY-INFORMED TASK VERIFICATION (Step 9b): Post-execution task
    verification using full trajectory context.  Same axes as Step 10
    (ambiguity + validity) but informed by action history, rubric scores,
    screenshot evidence, and outcome verification.
  - TASK VERIFICATION (Step 10): Unified task verification via
    CHECK_VALID_TASK_PROMPT.  Classifies the task along two axes — ambiguity
    (is_ambiguous) and validity (is_invalid) — in a single LLM call using
    only the task description, starting URL, and current date.

Pre-Pipeline: Rubric Generation & Action-Only Scoring
------------------------------------------------------
  - Step 0a — Rubric Generation: Given only the task description, generate a
    structured rubric of evaluation criteria with max_points, descriptions, and
    partial-credit guidance. Criteria are designed to be disjoint (no double-
    penalty) and merged when overlapping. Conditional criteria (with a "condition"
    field) model mutually exclusive alternatives (e.g., "buy organic OR if
    unavailable buy non-organic").

  - Step 0b — Rubric Dependency Checking: Review the generated rubric and
    reformulate criteria to fairly account for external dependencies outside the
    agent's control (site down, out of stock, entity doesn't exist). May
    decompose, merge, or relax criteria.

  - Step 0c — Action-Only Scoring: Score the rubric using only the text action
    history (no screenshots). This serves as the baseline. Key principles:
      * Controllable vs. Uncontrollable: Distinguish agent mistakes (penalize)
        from environment blockers like CAPTCHAs, login walls, out-of-stock
        (award full credit).
      * Cascading Dependencies: Don't cascade penalties for uncontrollable
        blockers to downstream criteria. Do cascade for controllable errors.
        Don't re-penalize the same deviation across multiple criteria.
      * Conditional Criteria: Evaluate is_condition_met and exclude unmet
        conditions from totals.

Multimodal Pipeline (9 Steps)
-----------------------------
  Step 1 — Load Screenshots:
    Load all trajectory screenshots in chronological order with strict 1-to-1
    correspondence to actions (every action must have exactly one screenshot).

  Step 2 — Screenshot-Criterion Relevance Scoring:
    For each screenshot, score its relevance (0–10) to ALL rubric criteria.
    Runs M parallel LLM calls (one per screenshot). Determines which screenshots
    are most informative for evaluating each criterion.

  Step 3 — Group Top-K Screenshots Per Criterion:
    Pure computation. For each criterion, select the K most relevant screenshots.
    Optionally filters out clearly irrelevant screenshots: if any screenshot
    scored >=6 for a criterion, drop screenshots scoring <5 that are >2 points
    below the weakest high-relevance screenshot.

  Step 4 — Screenshot Evidence Analysis:
    Analyze each (criterion, screenshot) pair to extract structured visual
    evidence. Two modes available:
      * Batched (default): One LLM call per unique screenshot, analyzing all
        criteria relevant to that screenshot simultaneously. More efficient.
      * Per-pair (legacy): One LLM call per (criterion, screenshot) pair.
    Extracts: screenshot_evidence (what is literally visible), criterion_analysis
    (success/partial/failure), discrepancies (agent claims vs. visual reality),
    environment_issues_confirmed, and condition_verification (for conditionals).
    CRITICAL: Analysis is grounded in actual screenshot pixels — does NOT assume
    or infer from action history. Action history is only for comparison.

  Step 4.5 — Conditional Criteria Disambiguation (if >=2 conditional criteria):
    Resolves potential mutual-exclusivity conflicts. Each conditional criterion
    was verified against its own screenshot subset in Step 4, which can produce
    contradictions. This step looks at ALL conditional criteria and ALL evidence
    together to determine the correct is_condition_met for each, ensuring
    mutually exclusive conditions have exactly one set to true. When evidence
    conflicts, latest (highest-numbered) screenshot takes precedence.

  Step 5 — Rubric Reality Check:
    Compares the rubric's original assumptions (written from the task description
    alone) against what the screenshots actually show. Adds a "reality_notes"
    field to each criterion providing interpretive context — e.g., "the product
    'Atom' is actually a product line, not a single item." Does NOT change
    max_points or scoring standards, only clarifies factual grounding so
    downstream rescoring is fair.

  Step 6 — Multimodal Rescoring:
    Rescore each criterion using screenshot evidence + action history + reality
    notes. Produces post_image_earned_points and post_image_justification. Two
    modes:
      * Whole-rubric (default): 1 gpt-5 call rescores all criteria in a single
        pass, seeing the full rubric context for better cascading-dependency
        handling.
      * Per-criterion (legacy): N sequential o4-mini calls, each scoring one
        criterion with previously rescored criteria visible for context.
    Key rescoring principles:
      * Trust latest screenshot when multiple show the same UI element.
      * Visual evidence overrides action history claims.
      * Verify environment blockers are actually visible in screenshots.
      * Cascading dependencies: don't re-penalize same upstream deviation.
      * Reality notes override criterion descriptions for conflicting facts.
      * Distinguish contradiction, fabrication, and supported inference from
        absence (only the first two are penalized).

  Step 7 — Unsolicited Side-Effect Detection:
    Safety-net check for extraneous actions with material side effects that were
    NOT already penalized by existing rubric criteria. Creates new penalty
    criteria (earned_points=0) if issues are found. Only targets:
      * Wrong substitutions that went unpenalized (e.g., added wrong product to
        cart when correct one was unavailable, but no existing criterion deducted
        for it).
      * Completely extraneous actions with lasting consequences (unrequested
        items added to cart, unauthorized enrollments, etc.).
    Does NOT penalize:
      * Exploratory navigation (browsing wrong pages, trying different queries).
      * Reasonable default choices (selecting current year, quantity=1).
      * Workarounds for uncontrollable blockers (trying alternative sites).
      * Critical Point violations (handled by existing rubric criteria).

  Final — Compute Scores:
    Pure computation. Computes total_max_points and total_earned_points using
    post_image_earned_points, respecting conditional criteria rules (unmet
    conditions excluded from both numerator and denominator).

  Step 8 — Outcome Verification:
    Independent binary assessment: did the agent actually accomplish the task
    from the user's perspective? Returns output_success (bool). Key principles:
      * Primary intent over literal compliance — if the user wanted to "book a
        restaurant via gayot.com" and the agent booked the right restaurant via
        opentable.com, the primary intent is satisfied.
      * Stopping at a Critical Point is expected behavior, not a failure.
      * Environment blockers (site down, CAPTCHA) that prevented the real-world
        outcome mean the task is NOT successful, even if the rubric awarded
        full credit for effort.
      * Rubric scores are informative but not deterministic — a high rubric
        score does not guarantee outcome success, and vice versa.
      * Wrong answers are worse than no answers for information retrieval tasks.

  Step 9a — Points of Failure Analysis:
    Identifies ALL failure points in the trajectory using a structured error
    taxonomy of 7 categories with numbered sub-codes: Selection (1.1–1.5),
    Hallucination (2.1–2.5), Execution & Strategy (3.1–3.6), Critical Point
    (4.1–4.3), Task Ambiguity (5.1–5.4), Unsolicited Side-Effect (6.1–6.2),
    Tool Interaction (7.1–7.4). Each failure is identified by error_code,
    category, and type. The FIRST (earliest step number) failure is computed
    programmatically from the LLM's failure_points list. Uses the scored
    rubric, screenshot evidence, action history, and outcome verification as
    context. Produces a diagnostic signal for error analysis — does not affect
    scoring.

  Step 9b — Trajectory-Informed Task Verification:
    Same classification axes as Step 10 (Ambiguity and Invalid Task) but
    performed after execution with full trajectory context: action history,
    predicted output, scored rubric, screenshot evidence, and outcome
    verification.  This allows the LLM to use execution evidence to make a
    more informed judgment about whether the *task itself* was ambiguous or
    invalid (as opposed to the agent simply failing).
      - Ambiguity (Category 7): {reasoning_is_ambiguous, is_ambiguous,
        ambiguity_codes}.
      - Invalid Task (Category 8): {reasoning_is_invalid, is_invalid,
        invalid_task_codes}.
    Does not affect scoring.

  Step 10 — Unified Task Verification (CHECK_VALID_TASK_PROMPT):
    Classifies the task along two axes in a single LLM call using only the
    task description, starting URL, and current date (no screenshots or
    action history):
      - Ambiguity (Category 7): is the task underspecified, ambiguous, or
        unsafe?  Produces {reasoning_is_ambiguous, is_ambiguous,
        ambiguity_codes}.
      - Invalid Task (Category 8): is the task impossible, illegal, NSFW, or
        otherwise infeasible?  Produces {reasoning_is_invalid, is_invalid,
        invalid_task_codes}.
    Does not affect scoring.

Cross-Cutting Design Principles
--------------------------------
  1. Process vs. Outcome Separation: The rubric score (process) measures how
     well the agent executed each step. The outcome verification (Step 8) judges
     whether the user's goal was met. These are independent signals — an agent
     can score high on process but fail on outcome (e.g., environment blocker
     prevented completion) or vice versa.

  2. Controllable vs. Uncontrollable Attribution: The single most important
     scoring principle. Uncontrollable failures (CAPTCHA, login walls, out of
     stock, site down, entity doesn't exist) earn full credit. Controllable
     failures (wrong selection, poor execution, hallucination, insufficient
     effort) are penalized. This applies across all steps.

  3. Conditional Criteria: Not all criteria always apply. Criteria with a
     "condition" field are only counted when is_condition_met=true. Mutually
     exclusive alternatives (buy organic vs. buy non-organic) ensure only one
     branch counts, and unmet conditions are excluded from totals entirely.

  4. Disjoint Criteria / No Double-Penalty: Rubric criteria are designed to be
     non-overlapping. If criterion A penalizes for using the wrong platform,
     criterion B must NOT also penalize for information sourced from the wrong
     platform. Each mistake is penalized exactly once.

  5. Cascading Dependency Rules: Uncontrollable upstream blocker → full credit
     for all downstream criteria. Controllable upstream error → cascade penalty
     to dependent downstream criteria. Upstream deviation already penalized →
     don't re-penalize in downstream criteria that evaluate a separable quality.

  6. Unsolicited Side-Effect Penalties: Actions beyond the task scope with
     material consequences (wrong items in cart, unauthorized enrollments) incur
     additional penalty criteria — but only if not already penalized by existing
     rubric criteria.

  7. Critical Point Awareness: The agent is expected to stop before binding
     transactions requiring personal/payment info unless explicitly authorized.
     Stopping at a critical point is correct behavior, not a failure.

  8. Visual Grounding: Screenshot evidence overrides action history claims.
     Chronologically ordered screenshots with latest-state-wins semantics.
     The reality check (Step 5) grounds rubric assumptions in observed reality.

     Agent claims are evaluated against visual evidence using five categories:

     ┌─────────────────────────────────────────┬──────────┬─────────────────────────────────────┐
     │ Category                                │ Penalize │ Example                             │
     ├─────────────────────────────────────────┼──────────┼─────────────────────────────────────┤
     │ Contradiction: screenshots show X,      │   YES    │ Screenshot shows booking calendar   │
     │ agent claims not-X                       │          │ but agent says "no booking system"  │
     ├─────────────────────────────────────────┼──────────┼─────────────────────────────────────┤
     │ Fabrication: agent claims X with zero   │   YES    │ Agent states a price that appears   │
     │ evidentiary basis                        │          │ nowhere in any screenshot           │
     ├─────────────────────────────────────────┼──────────┼─────────────────────────────────────┤
     │ Omission: agent didn't view everything  │   YES    │ Task: "highest ranked NHL team in   │
     │ it needed to; screenshots show no        │          │ Western Conference." Agent only     │
     │ evidence of X, but X is commonly known   │          │ checked Central Division, never     │
     │ to exist                                 │          │ viewed Pacific Division.            │
     ├─────────────────────────────────────────┼──────────┼─────────────────────────────────────┤
     │ Supported inference from absence:       │    NO    │ No booking UI visible across all    │
     │ screenshots show no evidence of X, AND   │          │ pages → agent concludes "no online  │
     │ X is not commonly known to exist         │          │ booking available"                  │
     ├─────────────────────────────────────────┼──────────┼─────────────────────────────────────┤
     │ Visual confirmation without explicit    │    NO    │ Agent found female cardiologists    │
     │ statement: agent omits justification     │          │ but didn't say "female" — photos    │
     │ but screenshots visually confirm result  │          │ in screenshots confirm it           │
     └─────────────────────────────────────────┴──────────┴─────────────────────────────────────┘

Verifier Comparison — How Each Scoring Component Handles Different Scenarios
-----------------------------------------------------------------------------
Three independent verifiers each produce a score. They differ in what they
penalize and what they forgive:

                          ┌──────────────┬──────────────┬──────────────┐
                          │  Critical    │   Rubric     │   Rubric     │
                          │  Point       │  (Process)   │  (Outcome)   │
  Scenario                │  Verifier*   │  Steps 0–7   │   Step 8     │
  ════════════════════════╪══════════════╪══════════════╪══════════════╡
  Environment blocker     │              │   FORGIVE    │   PENALIZE   │
  (CAPTCHA, login wall,   │   N/A        │  Full credit │  Task NOT    │
  out of stock, site      │              │  for good    │  accomplished│
  down, entity gone)      │              │  effort      │              │
  ────────────────────────┼──────────────┼──────────────┼──────────────┤
  Agent stopped at        │   REWARD     │   REWARD     │   FORGIVE    │
  Critical Point          │  Correct     │  Adherence   │  Not a       │
  (no permission to       │  adherence   │  if a        │  failure     │
  cross)                  │              │  criterion   │              │
  ────────────────────────┼──────────────┼──────────────┼──────────────┤
  Agent crossed           │   PENALIZE   │   PENALIZE   │   SHOULD     │
  Critical Point          │  Violation   │  Via rubric  │  PENALIZE    │
  (no permission given)   │  detected    │  criterion   │              │
  ────────────────────────┼──────────────┼──────────────┼──────────────┤
  Agent stopped at        │   PENALIZE   │   PENALIZE   │   PENALIZE   │
  Critical Point but      │  Failure to  │  Did not     │  Task NOT    │
  HAD permission to       │  proceed     │  complete    │  accomplished│
  cross                   │  when given  │  task steps  │              │
  ────────────────────────┼──────────────┼──────────────┼──────────────┤
  Controllable mistake    │              │   PENALIZE   │   PENALIZE   │
  (wrong product, wrong   │   N/A        │  Deduct per  │  if mistake  │
  date, missed option)    │              │  criterion   │  affects goal│
  ────────────────────────┼──────────────┼──────────────┼──────────────┤
  Unsolicited side        │              │   PENALIZE   │   PENALIZE   │
  effects (extraneous     │   N/A        │  New penalty │  Extraneous  │
  cart items, wrong       │              │  criteria    │  actions =   │
  substitutions)          │              │  (Step 7)    │  failure     │
  ────────────────────────┼──────────────┼──────────────┼──────────────┤
  Hallucination /         │              │   PENALIZE   │   PENALIZE   │
  grounding error         │   N/A        │  Visual      │  Wrong info  │
  (claims contradicted    │              │  evidence    │  = failure   │
  by screenshots)         │              │  overrides   │              │
  └────────────────────────────────────────────────────────────────────┘

  * Critical Point Verifier is implemented separately (by Luiz) and is not
    part of this module. It evaluates whether the agent correctly adhered to
    Critical Point definitions — stopping before binding transactions unless
    the user granted explicit permission to proceed.

  Key insight: The Process and Outcome verifiers diverge on environment
  blockers. Process awards full credit for best-effort when blocked (the agent
  did everything it could). Outcome marks it as failure because the user's
  real-world goal was not achieved. This means an agent can score 100% on
  process but 0 on outcome if the environment prevented completion.

Output Fields — What This Agent Writes Back
--------------------------------------------
The agent writes all output via shared_data_point attributes. Nothing is
written directly to disk; the caller is responsible for persisting to
task_data.json and scores/*.json.

Top-level fields on task_data.json (via shared_data_point setters):

  verifier_rubric : Dict | List[Dict]
      The complete scored rubric(s). When majority_vote_instances > 1 this
      is a list of all N instances; otherwise a single dict.

  rubric_score : float | List[float]
      Normalized rubric score(s) as earned_points / total_max_points. List
      when majority voting. The median is the canonical score.

  precomputed_rubric : Dict | List[Dict]
      Cached scored rubric(s) for reuse. When redo_eval=False on a
      subsequent run, the agent returns this instead of re-scoring.

  intermediate_mm_rubric_steps : Dict
      Comprehensive per-step outputs from the multimodal pipeline (see
      sub-fields below).

  majority_vote_metadata : Dict
      Voting statistics: n_instances, median_instance_idx, all_scores,
      median_score, outcome_votes, majority_output_success.

intermediate_mm_rubric_steps sub-fields:

  step1_num_screenshots : int
      Number of loaded screenshots (verified 1-to-1 with actions).

  step2_relevance_scores : Dict[str, Dict]
      Per-screenshot relevance scores (0-10) to all criteria.
      Format: {"screenshot_0": {criterion_idx: score, ...}, ...}.

  step3_grouped_screenshots : Dict[str, List[int]]
      Top-K screenshot indices grouped per criterion after filtering.

  step4_evidence_by_criterion : Dict[str, List[Dict]]
      Per-criterion screenshot evidence analysis. Each evidence dict has:
      screenshot_evidence, criterion_analysis, discrepancies,
      environment_issues_confirmed, condition_verification.

  step4_mode : str
      "batched" (all criteria per screenshot in 1 call) or "per_pair"
      (one call per criterion-screenshot pair).

  step4_num_llm_calls : int
      Total LLM calls made in Step 4.

  step4_5_disambiguation : Dict[str, Dict]
      (Only if >=2 conditional criteria) Disambiguation results:
      {criterion_idx: {"is_condition_met": bool, "reasoning": str}}.

  step5_reality_check : Dict[str, str]
      Reality notes per criterion from rubric-vs-screenshot comparison.

  step6_rescoring_summary : Dict
      Rescoring details from the median instance.

  step7_penalty_criteria : List[Dict]
      Penalty criteria added for unsolicited side effects (median instance).

  step7_reasoning : str
      Reasoning for penalty detection.

  step7_requires_penalty : bool
      Whether penalties were detected.

  majority_vote_steps67 : Dict
      All N instances for steps 6-7: all_scores, median_instance_idx,
      all_instances.

  step8_outcome_verification : Dict
      Outcome verification from median instance:
      {primary_intent, reasoning, output_success}.

  majority_vote_step8 : Dict
      All N outcome votes: all_votes, majority_output_success, all_results.

  step9_first_point_of_failure : Dict
      Points of failure analysis:
      {reasoning, has_failure, failure_points, first_failure_step,
       first_failure_summary}.

  step9b_task_verification_with_trajectory : Dict
      Trajectory-informed task verification (same schema as step10 but
      with full trajectory context):
      {reasoning_is_ambiguous, is_ambiguous, ambiguity_codes,
       reasoning_is_invalid, is_invalid, invalid_task_codes}.

  step10_task_verification : Dict
      Unified task verification (task + URL only):
      {reasoning_is_ambiguous, is_ambiguous, ambiguity_codes,
       reasoning_is_invalid, is_invalid, invalid_task_codes}.

Rubric dict structure (each entry in verifier_rubric):

  items : List[Dict]         — Array of scored criteria (see below).
  total_earned_points : float — Sum of earned points (conditional-excluded
                                criteria omitted from both numerator and
                                denominator).
  total_max_points : float   — Sum of max points.
  outcome_verification : Dict — {primary_intent, reasoning, output_success}.

Each criterion in items contains:

  criterion : str               — Criterion description.
  max_points : int              — Maximum possible points.
  earned_points : str/int       — Points from action-only scoring (Step 0c).
  justification : str           — Reasoning for action-only score.
  post_image_earned_points : str/int — Rescored points after MM analysis
                                       (Step 6).
  post_image_justification : str — Rescoring justification.
  is_condition_met : bool       — (Conditional criteria only) Whether the
                                  condition applies.
  applicable_evidence : List[str] — Screenshot IDs with relevant evidence.
  reality_notes : str           — Factual grounding notes from Step 5.
  penalty : bool                — (Step 7 additions only) Marks unsolicited
                                  side-effect penalties.
================================================================================

Model Assignment — Which LLM Client Is Used Where
---------------------------------------------------
Three client parameters are accepted: model_client, o4mini_client, gpt5_client.
In practice, model_client is typically o4-mini.

  gpt5_client (gpt-5.2):
    - Step 0a — Rubric Generation (_generate_rubric)
    - Step 0b — Rubric Dependency Checking (_check_rubric_dependencies)
    - Step 2  — Screenshot-Criterion Relevance Scoring
    - Step 4  — Screenshot Evidence Analysis (batched or per-pair)
    - Step 5  — Rubric Reality Check
    - Step 6  — Whole-Rubric Rescoring (default, rescore_whole_mm_rubric=True)
    - Step 7  — Unsolicited Side-Effect Detection
    - Step 8  — Outcome Verification
    - Step 9a — Points of Failure Analysis

  o4mini_client (o4-mini):
    - Step 0c — Action-Only Rubric Scoring (the text-only baseline scorer)
    - Step 6  — Per-Criterion Rescoring (legacy path, rescore_whole_mm_rubric=False)
    - Step 9b — Trajectory-Informed Task Verification
    - Step 10 — Unified Task Verification (CHECK_VALID_TASK_PROMPT)

  NOTE: model_client (_model_client) is no longer used directly in any pipeline
  step. It is retained for backward compatibility but all calls have been routed
  to either gpt5_client or o4mini_client as listed above.

"""

import asyncio
import copy
import io
import json
import logging
import re
import traceback
from difflib import SequenceMatcher
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Optional, Set, Tuple

from PIL import Image
from pydantic import ConfigDict, model_validator

from .base import AgentConfig, RunContext, VerifierAgent
from .data_point import (
    DataPoint,
    MajorityVoteMetadata,
    MMRubricOutcomeResult,
    MMRubricResult,
    StepSummary,
    UserMessageType,
    VerificationResult,
)

# webeval's native chat completion client interface.
from webeval.oai_clients import (
    ChatCompletionClient,  # noqa: F401 — re-exported for type hints only
)


def resolve_tools(names):  # stub — tool-derived action_definitions are optional
    """Stub: the optional tool registry used for action-schema validation
    is not shipped with this package.

    ``MMRubricAgentConfig.tools`` is optional — when unset, the
    failure-point analysis step simply falls back to a name-only check of
    the logged actions instead of cross-referencing arg schemas. Callers
    who do need schema-level validation should supply
    ``action_definitions`` directly.
    """
    raise RuntimeError(
        "resolve_tools is a stub. Supply MMRubricAgentConfig.action_definitions "
        "directly (or leave both tools and action_definitions unset to skip "
        "schema-level failure validation)."
    )


def tools_to_action_definitions(tools):  # pragma: no cover — stub
    raise RuntimeError("tools_to_action_definitions is a stub.")


from .prompts import (  # noqa: E402
    ACTION_ONLY_RUBRIC_SCORER_PROMPT,
    RUBRIC_GENERATION_PROMPT_TEMPLATE,
    RUBRIC_DEPENDENCY_CHECKING_PROMPT,
    MM_SCREENSHOT_CRITERION_RELEVANCE_PROMPT,
    MM_SCREENSHOT_EVIDENCE_ANALYSIS_PROMPT,
    MM_SCREENSHOT_BATCHED_EVIDENCE_ANALYSIS_PROMPT,
    MM_CRITERION_RESCORING_PROMPT,
    MM_RUBRIC_RESCORING_PROMPT,
    RUBRIC_REALITY_CHECK_PROMPT,
    CONDITIONAL_CRITERIA_DISAMBIGUATION_PROMPT,
    PENALIZE_UNSOLICITED_SIDE_EFFECTS_PROMPT,
    OUTCOME_VERIFICATION_PROMPT,
    FIRST_POINT_OF_FAILURE_PROMPT,
    CHECK_VALID_TASK_WITH_TRAJECTORY_PROMPT,
)
from .task_classification import classify_task, _validate_verification_result

logger = logging.getLogger(__name__)


def _build_client_from_endpoint_config(cfg: Any) -> Any:
    """Turn an endpoint-config dict, dict-list, file path, or directory into
    a :class:`webeval.oai_clients.ChatCompletionClient`.

    Plain dicts are handled by fara's ``create_completion_client_from_env``.
    Lists of dicts (or file paths resolving to a directory of JSON configs)
    are wrapped in a :class:`GracefulRetryClient` so multiple Azure
    endpoints can be load-balanced and retried — matching the pattern
    used by the rest of the webeval CLI (see ``scripts/om2w.py``).
    """
    from webeval.oai_clients.graceful_client import GracefulRetryClient
    from webeval.oai_clients.wrapper import ClientWrapper

    if isinstance(cfg, (str, Path)):
        p = Path(cfg).expanduser()
        if p.is_dir() or (p.is_file() and p.suffix == ".json"):
            return GracefulRetryClient.from_path(p, logger=logger, eval_model="*")
        raise FileNotFoundError(f"Endpoint config not found: {p}")

    if isinstance(cfg, list):
        clients = [ClientWrapper.from_config(c) for c in cfg]
        return GracefulRetryClient(clients=clients, logger=logger)

    if isinstance(cfg, dict):
        return ClientWrapper.from_config(cfg)

    raise TypeError(
        f"Unsupported endpoint config type {type(cfg).__name__}; expected "
        "dict, list[dict], or str path."
    )

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RUBRIC_THRESHOLD = 0.8
CRITERION_SIMILARITY_THRESHOLD = 0.7


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
class MMRubricAgentConfig(AgentConfig):
    """Configuration for the multimodal rubric verification agent."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    name: str = "mm_rubric_agent"

    # LLM clients — callers pass concrete ChatCompletionClient instances
    o4mini_client: Any = None
    gpt5_client: Any = None

    # LLM client configs — alternative to passing concrete clients.
    # When provided (and the corresponding client is None), the client
    # is created via ``create_client_from_config`` at init time.
    o4mini_client_config: Optional[Dict[str, Any]] = None
    gpt5_client_config: Optional[Dict[str, Any]] = None

    # Pipeline knobs
    max_images_per_criterion: int = 5
    screenshots_dir: Optional[str] = None
    rescore_whole_mm_rubric: bool = True
    batch_screenshot_analysis: bool = True
    min_relevance_threshold: int = 0
    ignore_irrelevant_screenshots: bool = True
    majority_vote_instances: int = 1
    redo_eval: bool = False
    failure_analysis_only: bool = False
    rubric_score_threshold: float = 0.8
    max_iters: int = 5

    # Action definitions for failure-point analysis (Step 9a).
    # Maps action_name -> set(arg_names).  Derived automatically from
    # ``tools`` (a list of tool-group names like
    # ``["GPT54_BROWSER_TOOLS_CORE"]``).  Callers *must* supply ``tools``
    # so the verifier checks against the solver's actual action space.
    tools: Optional[List[str]] = None
    action_definitions: Optional[Dict[str, Set[str]]] = None

    @model_validator(mode="after")
    def _set_action_definitions_from_tools(self) -> "MMRubricAgentConfig":
        if self.action_definitions is None and self.tools is not None:
            self.action_definitions = tools_to_action_definitions(
                resolve_tools(self.tools)
            )
        return self


# ---------------------------------------------------------------------------
# Rubric validation helpers (module-level, unchanged from original)
# ---------------------------------------------------------------------------
def verify_rubric(d: dict) -> bool:
    assert isinstance(d, dict), f"Expected a dict, got {type(d)}"
    assert "items" in d, "Expected 'items' field in dict"
    assert isinstance(d["items"], list), "Expected 'items' field to be a list"
    for item in d["items"]:
        assert "criterion" in item, "Expected 'criterion' field in each item"
        if "items" in item:
            verify_rubric(item)
        else:
            assert "max_points" in item, "Expected 'max_points' field in each item"
            assert isinstance(
                item["max_points"], (int, float)
            ), "'max_points' should be a number"
            assert (
                "earned_points" in item
            ), "Expected 'earned_points' field in each item"
            assert isinstance(
                item["earned_points"], (int, float)
            ), "'earned_points' should be a number"
            assert (
                "justification" in item
            ), "Expected 'justification' field in each item"
            assert (
                isinstance(item["justification"], str) and item["justification"]
            ), "'justification' should be a string"
            if "condition" in item:
                assert (
                    "is_condition_met" in item
                ), f"Conditional criterion '{item['criterion']}' must have 'is_condition_met' field"
                assert isinstance(
                    item["is_condition_met"], bool
                ), f"'is_condition_met' must be a boolean for criterion '{item['criterion']}'"
            if "post_image_justification" in item:
                assert (
                    isinstance(item["post_image_justification"], str)
                    and item["post_image_justification"]
                ), "'post_image_justification' should be a non-empty string"
            if "post_image_earned_points" in item:
                assert isinstance(
                    item["post_image_earned_points"], (int, float)
                ), "'post_image_earned_points' should be a number"
                assert (
                    0 <= item["post_image_earned_points"] <= item["max_points"]
                ), f"'post_image_earned_points' ({item['post_image_earned_points']}) must be between 0 and max_points ({item['max_points']})"
    return True


def verify_generated_rubric(d: dict) -> bool:
    assert isinstance(d, dict), f"Expected a dict, got {type(d)}"
    assert "items" in d, "Expected 'items' field in dict"
    assert isinstance(d["items"], list), "Expected 'items' field to be a list"
    assert len(d["items"]) > 0, "Expected at least one item in rubric"
    for item in d["items"]:
        assert "criterion" in item, "Expected 'criterion' field in each item"
        assert "description" in item, "Expected 'description' field in each item"
        assert "max_points" in item, "Expected 'max_points' field in each item"
        assert isinstance(
            item["max_points"], (int, float)
        ), "'max_points' should be a number"
        assert item["max_points"] > 0, "'max_points' should be greater than 0"
        assert "justification" in item, "Expected 'justification' field in each item"
        assert "earned_points" in item, "Expected 'earned_points' field in each item"
        assert (
            item["justification"] == ""
        ), "'justification' should be empty string in generated rubric"
        assert (
            item["earned_points"] == ""
        ), "'earned_points' should be empty string in generated rubric"
        if "items" in item:
            verify_generated_rubric(item)
    return True


def verify_conditional_totals(d: dict) -> bool:
    """Verify that total_max_points and total_earned_points correctly account for conditional criteria.

    Rules:
    - Non-conditional criteria: Always count max_points and earned_points toward totals
    - Conditional criteria with is_condition_met=true: Count max_points and earned_points toward totals
    - Conditional criteria with is_condition_met=false: Do NOT count toward totals (excluded from both numerator and denominator)
    """
    assert isinstance(d, dict), f"Expected a dict, got {type(d)}"
    assert "items" in d, "Expected 'items' field in dict"
    assert "total_max_points" in d, "Expected 'total_max_points' field in dict"
    assert "total_earned_points" in d, "Expected 'total_earned_points' field in dict"

    def sum_points_recursive(items, breakdown_list):
        total_max = 0
        total_earned = 0

        for item in items:
            if "items" in item:
                sub_max, sub_earned = sum_points_recursive(
                    item["items"], breakdown_list
                )
                total_max += sub_max
                total_earned += sub_earned
            else:
                is_conditional = "condition" in item
                criterion_name = item.get("criterion", "unnamed")

                if is_conditional:
                    assert (
                        "is_condition_met" in item
                    ), f"Conditional criterion '{criterion_name}' missing 'is_condition_met' field"

                    if item["is_condition_met"]:
                        total_max += item["max_points"]
                        total_earned += item["earned_points"]
                        breakdown_list.append(
                            f"  COUNTED (conditional, condition met): '{criterion_name}' "
                            f"[max: {item['max_points']}, earned: {item['earned_points']}]"
                        )
                    else:
                        breakdown_list.append(
                            f"  EXCLUDED (conditional, condition NOT met): '{criterion_name}' "
                            f"[max: {item['max_points']}, earned: {item['earned_points']}] - NOT counted in totals"
                        )
                else:
                    total_max += item["max_points"]
                    total_earned += item["earned_points"]
                    breakdown_list.append(
                        f"  COUNTED (non-conditional): '{criterion_name}' "
                        f"[max: {item['max_points']}, earned: {item['earned_points']}]"
                    )

        return total_max, total_earned

    breakdown = []
    expected_max, expected_earned = sum_points_recursive(d["items"], breakdown)

    max_matches = abs(d["total_max_points"] - expected_max) < 0.01
    earned_matches = abs(d["total_earned_points"] - expected_earned) < 0.01

    if not max_matches or not earned_matches:
        error_msg = [
            "\n" + "=" * 80,
            "ERROR: Total points calculation does not follow conditional criteria rules!",
            "=" * 80,
            "",
            "RULES REMINDER:",
            "  1. Non-conditional criteria: ALWAYS count max_points and earned_points",
            "  2. Conditional criteria (has 'condition' field):",
            "     - If is_condition_met = true: COUNT the points",
            "     - If is_condition_met = false: DO NOT COUNT (exclude from both numerator and denominator)",
            "",
            "BREAKDOWN OF ALL CRITERIA:",
        ]
        error_msg.extend(breakdown)
        error_msg.extend(
            [
                "",
                "CALCULATION SUMMARY:",
                f"  Expected total_max_points:    {expected_max}",
                f"  Reported total_max_points:    {d['total_max_points']}",
                f"  Match: {'YES' if max_matches else 'NO - MISMATCH!'}",
                "",
                f"  Expected total_earned_points: {expected_earned}",
                f"  Reported total_earned_points: {d['total_earned_points']}",
                f"  Match: {'YES' if earned_matches else 'NO - MISMATCH!'}",
                "",
                "REQUIRED FIX:",
            ]
        )

        if not max_matches:
            error_msg.append(
                f"  - Change 'total_max_points' from {d['total_max_points']} to {expected_max}"
            )
        if not earned_matches:
            error_msg.append(
                f"  - Change 'total_earned_points' from {d['total_earned_points']} to {expected_earned}"
            )

        error_msg.extend(
            [
                "",
                "=" * 80,
            ]
        )

        raise AssertionError("\n".join(error_msg))

    return True


def graft_scores_onto_rubric(original: dict, scored: dict) -> dict:
    """Copy scoring fields from the model response onto the original rubric.

    Validates lexical overlap of criterion strings using
    CRITERION_SIMILARITY_THRESHOLD, then grafts only scoring fields onto
    a deep-copy of the original rubric.
    """
    result = copy.deepcopy(original)
    orig_items = result.get("items", [])
    scored_items = scored.get("items", [])

    if len(orig_items) != len(scored_items):
        raise ValueError(
            f"Rubric item count mismatch: expected {len(orig_items)} items "
            f"but your response has {len(scored_items)}. "
            f"Return exactly the same number of rubric items."
        )

    for i, (orig_item, scored_item) in enumerate(zip(orig_items, scored_items)):
        orig_crit = orig_item.get("criterion", "")
        scored_crit = scored_item.get("criterion", "")
        similarity = SequenceMatcher(
            None, orig_crit.lower(), scored_crit.lower()
        ).ratio()
        if similarity < CRITERION_SIMILARITY_THRESHOLD:
            raise ValueError(
                f"Criterion mismatch at position {i}: expected '{orig_crit}' "
                f"but got '{scored_crit}' (similarity={similarity:.2f}, "
                f"threshold={CRITERION_SIMILARITY_THRESHOLD}). "
                f"Do not rephrase or reorder criteria — return them exactly "
                f"as they appear in the original rubric."
            )
        orig_item["justification"] = scored_item.get("justification", "")
        orig_item["earned_points"] = scored_item.get("earned_points", 0)
        if "condition" in orig_item:
            orig_item["is_condition_met"] = scored_item.get("is_condition_met", False)

    return result


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
class MMRubricAgent(VerifierAgent):
    """Multimodal rubric-based scoring agent (v3_mm).

    Produces two independent signals:
      - PROCESS REWARD (Steps 0-7): fine-grained rubric score
      - OUTCOME REWARD (Step 8): binary success/failure
    Regarding failure analysis:
    - POINTS OF FAILURE (Step 9a): Identifies all failure points in the
        trajectory using a structured error taxonomy (10 categories), pinpoints
        the first (earliest) failure step, and classifies each failure by type
        and severity.
    - TRAJECTORY-INFORMED TASK VERIFICATION (Step 9b): Post-execution task
        verification using full trajectory context — ambiguity (is_ambiguous)
        and validity (is_invalid).
    - TASK VERIFICATION (Step 10): Unified classification via
        CHECK_VALID_TASK_PROMPT — ambiguity (is_ambiguous) and validity
        (is_invalid) in a single LLM call.
    """

    DEFAULT_SYSTEM_MESSAGES = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]

    _STEP_NUMBERS_RE = re.compile(r"^\d+(-\d+)?(,\d+)*$")

    config: MMRubricAgentConfig  # type: narrow from AgentConfig

    def __init__(
        self, config: MMRubricAgentConfig | dict[str, Any] | None = None, **kwargs: Any
    ):
        super().__init__(config, **kwargs)

        # Instantiate clients lazily from endpoint config dicts/paths when
        # no concrete client instance was supplied. Uses webeval's client
        # factory so MMRubricAgent plugs into the same endpoint-config
        # format the rest of the webeval package already consumes.
        if self.config.o4mini_client is None and self.config.o4mini_client_config:
            self.config.o4mini_client = _build_client_from_endpoint_config(
                self.config.o4mini_client_config
            )
        if self.config.gpt5_client is None and self.config.gpt5_client_config:
            self.config.gpt5_client = _build_client_from_endpoint_config(
                self.config.gpt5_client_config
            )

        assert (
            self.config.o4mini_client is not None
        ), "o4mini_client or o4mini_client_config must be provided"
        assert (
            self.config.gpt5_client is not None
        ), "gpt5_client or gpt5_client_config must be provided"
        assert (
            self.config.majority_vote_instances >= 1
            and self.config.majority_vote_instances % 2 == 1
        ), f"majority_vote_instances must be a positive odd number, got {self.config.majority_vote_instances}"

    @classmethod
    def _get_config_class(cls) -> type[AgentConfig]:
        return MMRubricAgentConfig

    @property
    def _o4mini_client(self) -> ChatCompletionClient:
        return self.config.o4mini_client

    @property
    def _gpt5_client(self) -> ChatCompletionClient:
        return self.config.gpt5_client

    # ------------------------------------------------------------------
    # Core Agent interface
    # ------------------------------------------------------------------
    async def initialize(self, run_context: RunContext) -> None:
        await super().initialize(run_context)
        # Default screenshots_dir to the run output directory
        if not self.config.screenshots_dir:
            self.config.screenshots_dir = str(run_context.output_dir)

    async def run(
        self, run_context: RunContext, input: Any = None
    ) -> list[VerificationResult]:
        """Run the full rubric verification pipeline.

        Reads the :class:`DataPoint` from ``run_context.data_point``.

        Returns a list with two :class:`VerificationResult` entries:
          - :class:`MMRubricResult`
          - :class:`MMRubricOutcomeResult`
        """
        dp = run_context.data_point
        input_dict = self._extract_input_from_datapoint(
            dp,
            screenshots_dir=self.config.screenshots_dir,
            redo_eval=self.config.redo_eval,
        )
        result = await self._generate_reply(input_dict)
        return self._wrap_result(result)

    # ------------------------------------------------------------------
    # DataPoint helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _format_action_history(
        summaries: List[StepSummary], max_url_chars: int = 150
    ) -> str:
        """Format step summaries into the ``State N / Action N`` text format."""
        lines: List[str] = []
        for s in summaries:
            for msg_type, msg_content in s.user_messages_before:
                if msg_type == UserMessageType.CRITICAL_POINT_RESPONSE:
                    lines.append(f"[User Response] {msg_content}")
                elif msg_type == UserMessageType.FOLLOWUP_TASK:
                    lines.append(f"[Follow-up Task] {msg_content}")

            url_shortened = s.url.split("?")[0].split("#")[0]
            if len(url_shortened) > max_url_chars:
                url_shortened = url_shortened[:max_url_chars] + "..."

            state_str = f"{url_shortened}, state_description: {s.state_description}"
            action_str = f"{s.action_name}({json.dumps(s.action_args, indent=4)})"

            idx = s.index
            entry = f"State {idx}: {state_str}\nAction {idx}: {action_str}"

            if s.previous_error:
                entry += f"\nError! The above Action {idx} encountered an Error: {s.previous_error}"

            lines.append(entry)

        return "\n".join(lines)

    @staticmethod
    def _extract_input_from_datapoint(
        dp: DataPoint,
        screenshots_dir: str | None,
        redo_eval: bool,
    ) -> dict:
        """Convert a DataPoint into the dict expected by _generate_reply."""
        summaries = dp.solver_log.get_step_summaries()

        # Build actions_list with pre-action screenshots (state before each action).
        actions_list = [
            {"id": s.index, "screenshot": s.screenshot_path.replace("_post.", "_pre.")}
            for s in summaries
        ]

        # Per-step action name + arg keys for programmatic tool-error detection.
        step_actions = [
            {
                "step_number": s.index,
                "action_name": s.action_name,
                "action_args_keys": list(s.action_args.keys()),
            }
            for s in summaries
            if s.action_name
        ]

        # Extract app names from environment_config (e.g. ["pdf", "word"]).
        env_cfg = dp.task.environment_config or {}
        apps = env_cfg.get("apps", [])

        # The starting URL may be stored under different keys depending on
        # the data source: "init_url" (old/legacy), "start_page" (task
        # proposal / webvoyager), or "start_url" (viewer convention).
        init_url = (
            env_cfg.get("init_url")
            or env_cfg.get("start_page")
            or env_cfg.get("start_url", "")
        )

        return {
            "task": dp.task.instruction,
            "action_history": MMRubricAgent._format_action_history(summaries),
            "predicted_output": (
                dp.solver_log.outcome.answer if dp.solver_log.outcome else ""
            ),
            "screenshots_dir": screenshots_dir,
            "actions_list": actions_list,
            "step_actions": step_actions,
            "precomputed_rubric": dp.task.metadata.get("precomputed_rubric"),
            "init_url": init_url,
            "apps": apps,
            "redo_eval": redo_eval,
        }

    def _wrap_result(self, result: dict) -> list[VerificationResult]:
        """Wrap the raw rubric dict into two VerificationResult objects."""
        total_max = result.get("total_max_points", 1)
        total_earned = result.get("total_earned_points", 0)
        rubric_score = total_earned / total_max if total_max > 0 else 0.0

        outcome_verification = result.get("outcome_verification", {})
        output_success = outcome_verification.get("output_success")

        mv_raw = result.get("majority_vote_metadata", {})

        rubric_vr = MMRubricResult(
            score=rubric_score,
            reasoning=json.dumps(
                {
                    "items": result.get("items", []),
                    "total_max_points": total_max,
                    "total_earned_points": total_earned,
                },
                indent=2,
            ),
            verifier_name="mm_rubric",
            total_max_points=total_max,
            total_earned_points=total_earned,
            rubric_is_success=rubric_score >= self.config.rubric_score_threshold,
            intermediate_mm_rubric_steps=result.get("intermediate_mm_rubric_steps", {}),
            majority_vote_metadata=MajorityVoteMetadata(
                n_instances=mv_raw.get("n_instances", 0),
                median_instance_idx=mv_raw.get("median_instance_idx", 0),
                all_scores=mv_raw.get("all_scores", []),
                median_score=mv_raw.get("median_score", 0.0),
                outcome_votes=mv_raw.get("outcome_votes", []),
                majority_output_success=mv_raw.get("majority_output_success"),
            ),
            all_rubric_dicts=result.get("all_rubric_dicts", []),
            all_scores_list=result.get("all_scores_list", []),
        )

        outcome_vr = MMRubricOutcomeResult(
            score=1.0 if output_success else 0.0,
            reasoning=outcome_verification.get("reasoning", ""),
            verifier_name="mm_rubric_outcome",
            output_success=output_success,
            primary_intent=outcome_verification.get("primary_intent", ""),
        )

        return [rubric_vr, outcome_vr]

    # ------------------------------------------------------------------
    # LLM call helper
    # ------------------------------------------------------------------
    async def _call_llm(
        self,
        messages: list[dict],
        client: Any,
        json_output: bool = False,
    ) -> str:
        """Call a :class:`ChatCompletionClient` and return the response text.

        ``messages`` is a list of OpenAI-chat-completion dicts (with
        ``image_url`` blocks for screenshots). The wrappers in
        :mod:`webeval.oai_clients.wrapper` accept these dicts directly
        — no message-type conversion needed.
        """
        supports_json = True
        fn = getattr(client, "supports_json", None)
        if callable(fn):
            try:
                supports_json = bool(fn())
            except TypeError:
                supports_json = bool(fn)
        result = await client.create(
            messages=messages,
            json_output=json_output if supports_json else False,
        )
        content = result.content
        # Some wrappers historically returned a ChatCompletionMessage object;
        # the current wrappers return the response text directly.
        if hasattr(content, "content"):
            content = content.content
        assert isinstance(content, str), (
            f"Expected str content from client, got {type(content).__name__}: {content!r}"
        )
        return content

    # ------------------------------------------------------------------
    # Task / URL helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _get_init_url_context(init_url: str | None) -> str:
        if not init_url:
            return ""
        if init_url.lower() in [
            "",
            "bing.com",
            "https://bing.com",
            "https://bing.com/",
            "http://bing.com",
            "https://www.bing.com",
            "http://www.bing.com",
        ]:
            return ""
        return (
            f"\n\nIMPORTANT: The agent MAY have started on the URL: {init_url}\n"
            "This starting URL may be considered part of the task context. "
            "The agent should NOT be penalized for using or assuming information "
            "that is implicit in this starting URL."
        )

    # ------------------------------------------------------------------
    # Step 0a: Rubric Generation
    # ------------------------------------------------------------------
    async def _generate_rubric(self, task: str, init_url_context: str) -> dict:
        prompt = Template(RUBRIC_GENERATION_PROMPT_TEMPLATE).substitute(
            task_id=task, init_url_context=init_url_context
        )
        messages = [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        attempt = 0
        errors = []
        while max_iters > 0:
            attempt += 1
            try:
                response_text = await self._call_llm(
                    messages, self._gpt5_client, json_output=True
                )
                rubric_dict = json.loads(response_text)
                verify_generated_rubric(rubric_dict)
                logger.info(f"Successfully generated rubric: {rubric_dict}")

                # Step 0b: Check rubric dependencies
                rubric_dict = await self._check_rubric_dependencies(
                    rubric_dict, task, init_url_context
                )
                verify_generated_rubric(rubric_dict)
                return rubric_dict
            except Exception as e:
                error_type = type(e).__name__
                response_preview = (
                    (response_text[:200] + "...")
                    if "response_text" in dir() and response_text
                    else "N/A"
                )
                errors.append(f"  Attempt {attempt}: [{error_type}] {e}")
                logger.warning(
                    f"Rubric generation attempt {attempt}/5 failed: [{error_type}] {e} | Response preview: {response_preview}"
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error: {e}. Please ensure the rubric follows the exact format specified with 'items' list containing objects with 'criterion', 'description', 'max_points', 'justification' (empty string), and 'earned_points' (empty string) fields.",
                    }
                )
                max_iters -= 1
        error_summary = "\n".join(errors)
        raise RuntimeError(
            f"Failed to generate a valid rubric after {self.config.max_iters} attempts:\n{error_summary}"
        )

    # ------------------------------------------------------------------
    # Step 0b: Rubric Dependency Checking
    # ------------------------------------------------------------------
    async def _check_rubric_dependencies(
        self, rubric_dict: dict, task: str, init_url_context: str
    ) -> dict:
        prompt = Template(RUBRIC_DEPENDENCY_CHECKING_PROMPT).substitute(
            task_id=task,
            rubric=json.dumps(rubric_dict, indent=2),
            init_url_context=init_url_context,
        )
        messages = [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        attempt = 0
        errors = []
        while max_iters > 0:
            attempt += 1
            try:
                response_text = await self._call_llm(
                    messages, self._gpt5_client, json_output=True
                )
                result = json.loads(response_text)
                if result.get("needs_reformulation", False):
                    reformulated = result.get("reformulated_rubric", {})
                    if reformulated:
                        verify_generated_rubric(reformulated)
                        return reformulated
                    raise ValueError(
                        "needs_reformulation is True but reformulated_rubric is empty"
                    )
                return rubric_dict
            except Exception as e:
                error_type = type(e).__name__
                response_preview = (
                    (response_text[:200] + "...")
                    if "response_text" in dir() and response_text
                    else "N/A"
                )
                errors.append(f"  Attempt {attempt}: [{error_type}] {e}")
                logger.warning(
                    f"Rubric dependency check attempt {attempt}/5 failed: [{error_type}] {e} | Response preview: {response_preview}"
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error: {e}. Please ensure the output follows the exact format specified with 'reasoning', 'needs_reformulation', and 'reformulated_rubric' fields.",
                    }
                )
                max_iters -= 1
        error_summary = "\n".join(errors)
        raise RuntimeError(
            f"Failed to check rubric dependencies after {self.config.max_iters} attempts:\n{error_summary}"
        )

    # ------------------------------------------------------------------
    # Step 0c helpers: clear scores
    # ------------------------------------------------------------------
    @staticmethod
    def _clear_rubric_scores(rubric_dict: dict) -> dict:
        cleared = copy.deepcopy(rubric_dict)

        def remove_penalty_criteria(items):
            return [item for item in items if not item.get("penalty", False)]

        def clear_scores_recursive(items):
            for item in items:
                if "earned_points" in item:
                    item["earned_points"] = ""
                if "justification" in item:
                    item["justification"] = ""
                for key in [
                    "is_condition_met",
                    "applicable_evidence",
                    "post_image_justification",
                    "post_image_earned_points",
                    "reality_notes",
                ]:
                    item.pop(key, None)
                if "items" in item and isinstance(item["items"], list):
                    item["items"] = remove_penalty_criteria(item["items"])
                    clear_scores_recursive(item["items"])

        if "items" in cleared:
            cleared["items"] = remove_penalty_criteria(cleared["items"])
            clear_scores_recursive(cleared["items"])
        cleared.pop("total_earned_points", None)
        return cleared

    # ------------------------------------------------------------------
    # Step 1: Load Screenshots
    # ------------------------------------------------------------------
    @staticmethod
    def _load_screenshots(
        screenshots_dir: str, actions_list: list
    ) -> List[Image.Image]:
        """Load all screenshots in chronological order with strict 1-to-1 verification."""

        def _screenshot_index(filename: str) -> int:
            # Handles both "screenshot_3.png" and "screenshot_3_pre.png" patterns
            match = re.search(r"screenshot_(\d+)", Path(filename).stem)
            return int(match.group(1)) if match else 0

        sorted_actions = sorted(
            actions_list, key=lambda a: _screenshot_index(str(a.get("screenshot", "")))
        )

        screenshots: List[Image.Image] = []
        missing, load_errors, id_mismatches = [], [], []

        for action in sorted_actions:
            screenshot_file = action.get("screenshot", "")
            if not screenshot_file:
                missing.append(f"Action {action.get('id')} has no screenshot field")
                continue

            sid = _screenshot_index(screenshot_file)
            try:
                aid = int(action["id"])
            except (TypeError, ValueError, KeyError):
                raise ValueError(
                    f"Action id '{action.get('id')}' is not an int (file: {screenshot_file})"
                )
            if aid != sid:
                id_mismatches.append(
                    f"Action id {aid} does not match screenshot index {sid} (file: {screenshot_file})"
                )

            screenshot_path = Path(screenshots_dir) / screenshot_file
            if not screenshot_path.exists():
                missing.append(
                    f"Action {action.get('id')}: file does not exist at {screenshot_path}"
                )
                continue
            try:
                img = Image.open(screenshot_path).convert("RGB").copy()
                screenshots.append(img)
            except Exception as e:
                load_errors.append(f"Action {action.get('id')}: failed to load - {e}")

        if id_mismatches:
            raise ValueError(
                f"Screenshot-action ordering mismatch ({len(id_mismatches)}):\n"
                + "\n".join(f"  - {m}" for m in id_mismatches)
            )

        sorted_indices = sorted(
            _screenshot_index(a.get("screenshot", ""))
            for a in sorted_actions
            if a.get("screenshot")
        )
        if sorted_indices:
            expected = list(
                range(sorted_indices[0], sorted_indices[0] + len(sorted_indices))
            )
            if sorted_indices != expected:
                raise ValueError(
                    f"Screenshot indices not consecutive. Got {sorted_indices}, expected {expected}"
                )

        if missing or load_errors:
            error_msg = f"Failed to load ALL screenshots. Expected {len(sorted_actions)}, got {len(screenshots)}.\n"
            if missing:
                error_msg += (
                    "Missing:\n" + "\n".join(f"  - {m}" for m in missing[:10]) + "\n"
                )
            if load_errors:
                error_msg += (
                    "Errors:\n" + "\n".join(f"  - {m}" for m in load_errors[:10]) + "\n"
                )
            raise RuntimeError(error_msg)

        if len(screenshots) != len(sorted_actions):
            raise RuntimeError(
                f"Screenshot count mismatch: expected {len(sorted_actions)}, loaded {len(screenshots)}"
            )
        return screenshots

    # ------------------------------------------------------------------
    # Step 2: Screenshot-Criterion Relevance Scoring
    # ------------------------------------------------------------------
    async def _score_screenshot_criterion_relevance(
        self,
        screenshots: List[Image.Image],
        rubric: dict,
        task: str,
        init_url_context: str,
    ) -> Dict[int, Dict]:
        rubric_criteria_text = ""
        for idx, criterion in enumerate(rubric["items"]):
            rubric_criteria_text += f"\n{idx}. **{criterion['criterion']}**\n"
            rubric_criteria_text += f"   Description: {criterion['description']}\n"

        num_criteria = len(rubric["items"])

        async def score_single_screenshot(screenshot_idx: int, screenshot: Image.Image):
            prompt = Template(MM_SCREENSHOT_CRITERION_RELEVANCE_PROMPT).substitute(
                task_definition=task,
                init_url_context=init_url_context,
                rubric_criteria=rubric_criteria_text,
            )

            img_b64 = self._encode_image(screenshot)
            messages = self.DEFAULT_SYSTEM_MESSAGES + [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}",
                                "detail": "high",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            max_iters = self.config.max_iters
            last_error = None
            while max_iters > 0:
                try:
                    response_text = await self._call_llm(
                        messages, self._gpt5_client, json_output=True
                    )
                    scores_dict = json.loads(response_text)
                    result = {}
                    missing_keys, invalid_values = [], []

                    for criterion_idx in range(num_criteria):
                        key_variants = [
                            f"criterion_{criterion_idx}",
                            str(criterion_idx),
                            criterion_idx,
                        ]
                        found = False
                        for key in key_variants:
                            if key in scores_dict:
                                try:
                                    score = int(scores_dict[key])
                                    if 0 <= score <= 10:
                                        result[criterion_idx] = score
                                        found = True
                                        break
                                    else:
                                        invalid_values.append(
                                            f"criterion_{criterion_idx}: score {score} not in range [0, 10]"
                                        )
                                except (ValueError, TypeError):
                                    invalid_values.append(
                                        f"criterion_{criterion_idx}: value '{scores_dict[key]}' is not an integer"
                                    )
                        if not found:
                            missing_keys.append(f"criterion_{criterion_idx}")

                    if missing_keys or invalid_values:
                        error_msg = f"Incomplete or invalid scores for screenshot {screenshot_idx}. "
                        if missing_keys:
                            error_msg += (
                                f"Missing scores for: {', '.join(missing_keys)}. "
                            )
                        if invalid_values:
                            error_msg += (
                                f"Invalid values: {'; '.join(invalid_values)}. "
                            )
                        error_msg += f"Expected scores for ALL {num_criteria} criteria (criterion_0 through criterion_{num_criteria - 1})."
                        raise ValueError(error_msg)

                    result["screenshot_idx"] = screenshot_idx
                    return result
                except Exception as e:
                    last_error = str(e)
                    logger.error(
                        f"Error scoring screenshot {screenshot_idx} (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": f"Error: {e}. Please provide scores for ALL {num_criteria} criteria using the exact format specified.",
                        }
                    )
                    max_iters -= 1

            logger.warning(
                f"Failed to score screenshot {screenshot_idx} after {self.config.max_iters} attempts. Last error: {last_error}"
            )
            fallback = {i: 0 for i in range(num_criteria)}
            fallback["screenshot_idx"] = screenshot_idx
            return fallback

        tasks = [score_single_screenshot(idx, s) for idx, s in enumerate(screenshots)]
        results = await asyncio.gather(*tasks)
        return {r["screenshot_idx"]: r for r in results}

    # ------------------------------------------------------------------
    # Step 3: Group Top-K Screenshots Per Criterion
    # ------------------------------------------------------------------
    def _group_screenshots_by_criterion(
        self, relevance_scores: Dict[int, Dict], num_criteria: int
    ) -> Dict[int, List[int]]:
        grouped = {c: [] for c in range(num_criteria)}
        for screenshot_idx, scores_dict in relevance_scores.items():
            for key, score in scores_dict.items():
                if key == "screenshot_idx":
                    continue
                grouped[key].append((screenshot_idx, score))

        max_k = self.config.max_images_per_criterion
        for c in grouped:
            grouped[c].sort(key=lambda x: (x[1], x[0]), reverse=True)
            grouped[c] = [s for s, _ in grouped[c][:max_k]]
        return grouped

    @staticmethod
    def _invert_grouped_screenshots(
        grouped: Dict[int, List[int]],
    ) -> Dict[int, List[int]]:
        inverted: Dict[int, List[int]] = {}
        for c_idx, s_indices in grouped.items():
            for s_idx in s_indices:
                inverted.setdefault(s_idx, []).append(c_idx)
        for s_idx in inverted:
            inverted[s_idx].sort()
        return inverted

    def _filter_irrelevant_screenshots(
        self, grouped: Dict[int, List[int]], relevance_scores: Dict[int, Dict]
    ) -> Dict[int, List[int]]:
        filtered: Dict[int, List[int]] = {}
        total_removed = 0
        for c_idx, s_indices in grouped.items():
            scored = [(s, relevance_scores.get(s, {}).get(c_idx, 0)) for s in s_indices]
            high_scores = [s for _, s in scored if s >= 6]
            if not high_scores:
                filtered[c_idx] = s_indices
                continue
            min_high = min(high_scores)
            kept = [
                s for s, score in scored if not (score < 5 and (min_high - score) > 2)
            ]
            if not kept:
                kept = s_indices
            total_removed += len(s_indices) - len(kept)
            filtered[c_idx] = kept
        if total_removed > 0:
            logger.info(
                f"[MM Pipeline] Filtered {total_removed} irrelevant (criterion, screenshot) "
                f"pairs before step 4"
            )
        return filtered

    # ------------------------------------------------------------------
    # Step 4: Screenshot Evidence Analysis
    # ------------------------------------------------------------------
    async def _analyze_screenshot_evidence(
        self,
        screenshots: List[Image.Image],
        rubric: dict,
        grouped_screenshots: Dict[int, List[int]],
        task: str,
        init_url_context: str,
        action_history: str,
        predicted_output: str,
    ) -> Dict[int, List[Dict]]:
        async def analyze_single_pair(criterion_idx: int, screenshot_idx: int):
            criterion = rubric["items"][criterion_idx]
            screenshot = screenshots[screenshot_idx]

            criterion_info = (
                f"**Criterion {criterion_idx}:** {criterion['criterion']}\n"
            )
            criterion_info += f"**Description:** {criterion['description']}\n"
            criterion_info += f"**Max Points:** {criterion['max_points']}"

            conditional_check, conditional_output = "", ""
            is_conditional = "condition" in criterion
            if is_conditional:
                conditional_check = (
                    f'\n\n5. **condition_verification**: This is a CONDITIONAL criterion that only applies if: "{criterion["condition"]}"\n'
                    "   Based on what you see in the screenshot, verify whether this condition is actually met.\n"
                    "   - Output true if the condition IS met (criterion should be evaluated)\n"
                    "   - Output false if the condition is NOT met (criterion should be skipped)"
                )
                conditional_output = ',\n  "condition_verification": true/false'

            prompt = Template(MM_SCREENSHOT_EVIDENCE_ANALYSIS_PROMPT).substitute(
                task_definition=task,
                init_url_context=init_url_context,
                action_history=action_history,
                agent_predicted_output=predicted_output,
                criterion_info=criterion_info,
                conditional_check=conditional_check,
                conditional_output=conditional_output,
            )

            img_b64 = self._encode_image(screenshot)
            messages = self.DEFAULT_SYSTEM_MESSAGES + [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}",
                                "detail": "high",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            max_iters = self.config.max_iters
            last_error = None
            while max_iters > 0:
                try:
                    response_text = await self._call_llm(
                        messages, self._gpt5_client, json_output=True
                    )
                    analysis = json.loads(response_text)
                    self._validate_evidence_analysis(analysis, is_conditional)
                    analysis["screenshot_idx"] = screenshot_idx
                    return (criterion_idx, analysis)
                except Exception as e:
                    last_error = str(e)
                    logger.error(
                        f"Error analyzing criterion {criterion_idx}, screenshot {screenshot_idx} (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": f"Error: {e}. Please ensure your output includes all required fields in the correct format.",
                        }
                    )
                    max_iters -= 1

            logger.warning(
                f"Failed to analyze criterion {criterion_idx}, screenshot {screenshot_idx} after {self.config.max_iters} attempts. Last error: {last_error}"
            )
            return (
                criterion_idx,
                {
                    "screenshot_evidence": f"Error: Analysis failed after {self.config.max_iters} attempts",
                    "criterion_analysis": "Unable to analyze due to repeated errors",
                    "discrepancies": "N/A",
                    "environment_issues_confirmed": False,
                    "screenshot_idx": screenshot_idx,
                },
            )

        all_tasks = []
        for c_idx, s_indices in grouped_screenshots.items():
            for s_idx in s_indices:
                all_tasks.append(analyze_single_pair(c_idx, s_idx))
        results = await asyncio.gather(*all_tasks)

        evidence_by_criterion: Dict[int, List[Dict]] = {
            i: [] for i in range(len(rubric["items"]))
        }
        for c_idx, analysis in results:
            evidence_by_criterion[c_idx].append(analysis)
        return evidence_by_criterion

    async def _analyze_screenshot_evidence_batched(
        self,
        screenshots: List[Image.Image],
        rubric: dict,
        grouped_screenshots: Dict[int, List[int]],
        task: str,
        init_url_context: str,
        action_history: str,
        predicted_output: str,
        relevance_scores: Dict[int, Dict] | None = None,
        min_relevance_threshold: int = 0,
    ) -> Dict[int, List[Dict]]:
        screenshots_to_criteria = self._invert_grouped_screenshots(grouped_screenshots)

        if min_relevance_threshold > 0 and relevance_scores is not None:
            for s_idx in list(screenshots_to_criteria.keys()):
                scores = relevance_scores.get(s_idx, {})
                filtered = [
                    c
                    for c in screenshots_to_criteria[s_idx]
                    if scores.get(c, 0) > min_relevance_threshold
                ]
                if filtered:
                    screenshots_to_criteria[s_idx] = filtered
                else:
                    del screenshots_to_criteria[s_idx]

        async def analyze_single_pair_for_batch(
            criterion_idx: int, screenshot_idx: int
        ):
            criterion = rubric["items"][criterion_idx]
            screenshot = screenshots[screenshot_idx]

            criterion_info = (
                f"**Criterion {criterion_idx}:** {criterion['criterion']}\n"
            )
            criterion_info += f"**Description:** {criterion['description']}\n"
            criterion_info += f"**Max Points:** {criterion['max_points']}"

            conditional_check, conditional_output = "", ""
            is_conditional = "condition" in criterion
            if is_conditional:
                conditional_check = (
                    f'\n\n5. **condition_verification**: This is a CONDITIONAL criterion that only applies if: "{criterion["condition"]}"\n'
                    "   Based on what you see in the screenshot, verify whether this condition is actually met.\n"
                    "   - Output true if the condition IS met (criterion should be evaluated)\n"
                    "   - Output false if the condition is NOT met (criterion should be skipped)"
                )
                conditional_output = ',\n  "condition_verification": true/false'

            prompt = Template(MM_SCREENSHOT_EVIDENCE_ANALYSIS_PROMPT).substitute(
                task_definition=task,
                init_url_context=init_url_context,
                action_history=action_history,
                agent_predicted_output=predicted_output,
                criterion_info=criterion_info,
                conditional_check=conditional_check,
                conditional_output=conditional_output,
            )

            img_b64 = self._encode_image(screenshot)
            messages = self.DEFAULT_SYSTEM_MESSAGES + [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}",
                                "detail": "high",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            max_iters = self.config.max_iters
            last_error = None
            while max_iters > 0:
                try:
                    response_text = await self._call_llm(
                        messages, self._gpt5_client, json_output=True
                    )
                    analysis = json.loads(response_text)
                    self._validate_evidence_analysis(analysis, is_conditional)
                    analysis["screenshot_idx"] = screenshot_idx
                    return [(criterion_idx, analysis)]
                except Exception as e:
                    last_error = str(e)
                    logger.error(
                        f"Error analyzing criterion {criterion_idx}, screenshot {screenshot_idx} (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": f"Error: {e}. Please ensure your output includes all required fields in the correct format.",
                        }
                    )
                    max_iters -= 1

            logger.warning(
                f"Failed to analyze criterion {criterion_idx}, screenshot {screenshot_idx} after {self.config.max_iters} attempts. Last error: {last_error}"
            )
            return [
                (
                    criterion_idx,
                    {
                        "screenshot_evidence": f"Error: Analysis failed after {self.config.max_iters} attempts",
                        "criterion_analysis": "Unable to analyze due to repeated errors",
                        "discrepancies": "N/A",
                        "environment_issues_confirmed": False,
                        "screenshot_idx": screenshot_idx,
                    },
                )
            ]

        async def analyze_multi_criteria_screenshot(
            screenshot_idx: int, criterion_indices: List[int]
        ):
            screenshot = screenshots[screenshot_idx]
            criteria_info_block = ""
            conditional_criteria = set()
            for c_idx in criterion_indices:
                criterion = rubric["items"][c_idx]
                criteria_info_block += (
                    f"\n**Criterion {c_idx}:** {criterion['criterion']}\n"
                )
                criteria_info_block += f"**Description:** {criterion['description']}\n"
                criteria_info_block += f"**Max Points:** {criterion['max_points']}\n"
                if "condition" in criterion:
                    conditional_criteria.add(c_idx)
                    criteria_info_block += f'**CONDITIONAL:** This criterion only applies if: "{criterion["condition"]}". You MUST include "condition_verification": true/false in the output for this criterion.\n'

            prompt = Template(
                MM_SCREENSHOT_BATCHED_EVIDENCE_ANALYSIS_PROMPT
            ).substitute(
                task_definition=task,
                init_url_context=init_url_context,
                action_history=action_history,
                agent_predicted_output=predicted_output,
                criteria_info_block=criteria_info_block,
            )

            img_b64 = self._encode_image(screenshot)
            messages = self.DEFAULT_SYSTEM_MESSAGES + [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}",
                                "detail": "high",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            max_iters = self.config.max_iters
            last_error = None
            while max_iters > 0:
                try:
                    response_text = await self._call_llm(
                        messages, self._gpt5_client, json_output=True
                    )
                    analyses = json.loads(response_text)
                    analyses = self._normalize_batched_analysis_response(
                        analyses, criterion_indices
                    )
                    if analyses is None or len(analyses) != len(criterion_indices):
                        raise ValueError(
                            f"Expected {len(criterion_indices)} entries, got {len(analyses) if analyses else 'None'}"
                        )

                    for i, (analysis, expected_c_idx) in enumerate(
                        zip(analyses, criterion_indices)
                    ):
                        if not isinstance(analysis, dict):
                            raise ValueError(f"Entry {i} is not a dict")
                        returned_idx = analysis.get("criterion_idx")
                        if returned_idx is None:
                            analysis["criterion_idx"] = expected_c_idx
                        elif returned_idx != expected_c_idx:
                            raise ValueError(
                                f"Entry {i}: expected criterion_idx={expected_c_idx}, got {returned_idx}"
                            )
                        is_conditional = expected_c_idx in conditional_criteria
                        self._validate_evidence_analysis(analysis, is_conditional)

                    results = []
                    for analysis, expected_c_idx in zip(analyses, criterion_indices):
                        analysis.pop("criterion_idx", None)
                        analysis["screenshot_idx"] = screenshot_idx
                        results.append((expected_c_idx, analysis))
                    return results
                except Exception as e:
                    last_error = str(e)
                    logger.error(
                        f"Error analyzing screenshot {screenshot_idx} "
                        f"(criteria {criterion_indices}, attempt {self.config.max_iters + 1 - max_iters}): {e}"
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": f'Error: {e}. Please output a JSON object like {{"analyses": [...]}} where the "analyses" list has exactly {len(criterion_indices)} entries, one per criterion. Each entry must have screenshot_evidence, criterion_analysis, discrepancies, environment_issues_confirmed, and criterion_idx. You ARE given a screenshot image — analyze the attached image.',
                        }
                    )
                    max_iters -= 1

            # Batched call failed — fall back to individual per-pair calls
            logger.warning(
                f"Batched analysis failed for screenshot {screenshot_idx} "
                f"(criteria {criterion_indices}) after {self.config.max_iters} attempts. "
                f"Falling back to per-pair calls. Last error: {last_error}"
            )
            fallback_tasks = [
                analyze_single_pair_for_batch(c, screenshot_idx)
                for c in criterion_indices
            ]
            fallback_results = await asyncio.gather(*fallback_tasks)
            return [item for sublist in fallback_results for item in sublist]

        all_tasks = []
        for s_idx, c_indices in screenshots_to_criteria.items():
            if len(c_indices) == 1:
                all_tasks.append(analyze_single_pair_for_batch(c_indices[0], s_idx))
            else:
                all_tasks.append(analyze_multi_criteria_screenshot(s_idx, c_indices))
        all_results = await asyncio.gather(*all_tasks)

        evidence_by_criterion: Dict[int, List[Dict]] = {
            i: [] for i in range(len(rubric["items"]))
        }
        for result_list in all_results:
            for c_idx, analysis in result_list:
                evidence_by_criterion[c_idx].append(analysis)
        return evidence_by_criterion

    # ------------------------------------------------------------------
    # Step 4 validation helper
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_evidence_analysis(analysis: dict, is_conditional: bool) -> None:
        required = [
            "screenshot_evidence",
            "criterion_analysis",
            "discrepancies",
            "environment_issues_confirmed",
        ]
        if is_conditional:
            required.append("condition_verification")
        missing, type_errors = [], []
        for field in required:
            if field not in analysis:
                missing.append(field)
            elif field in ("environment_issues_confirmed", "condition_verification"):
                if not isinstance(analysis[field], bool):
                    type_errors.append(
                        f"{field} must be a boolean, got {type(analysis[field]).__name__}"
                    )
            elif not isinstance(analysis[field], str):
                type_errors.append(
                    f"{field} must be a string, got {type(analysis[field]).__name__}"
                )
            elif not analysis[field]:
                type_errors.append(f"{field} cannot be empty")
        if missing or type_errors:
            error_msg = "Invalid analysis output. "
            if missing:
                error_msg += f"Missing required fields: {', '.join(missing)}. "
            if type_errors:
                error_msg += f"Type errors: {'; '.join(type_errors)}."
            raise ValueError(error_msg)

    @staticmethod
    def _normalize_batched_analysis_response(
        raw: Any, criterion_indices: List[int]
    ) -> list | None:
        expected = len(criterion_indices)
        analysis_fields = {
            "screenshot_evidence",
            "criterion_analysis",
            "discrepancies",
            "environment_issues_confirmed",
        }

        if isinstance(raw, list):
            return raw if len(raw) == expected else None
        if not isinstance(raw, dict):
            return None

        for val in raw.values():
            if (
                isinstance(val, list)
                and len(val) == expected
                and all(isinstance(item, dict) for item in val)
            ):
                return val

        recovered = []
        for c_idx in criterion_indices:
            key_variants = [
                str(c_idx),
                c_idx,
                f"criterion_{c_idx}",
                f"Criterion {c_idx}",
                f"criterion {c_idx}",
            ]
            found = False
            for key in key_variants:
                if key in raw and isinstance(raw[key], dict):
                    entry = raw[key]
                    entry["criterion_idx"] = c_idx
                    recovered.append(entry)
                    found = True
                    break
            if not found:
                break
        if len(recovered) == expected:
            return recovered

        if expected == 1 and analysis_fields.intersection(raw.keys()):
            return [raw]
        if expected == 1:
            for val in raw.values():
                if isinstance(val, dict) and analysis_fields.intersection(val.keys()):
                    if "criterion_idx" in raw and "criterion_idx" not in val:
                        val["criterion_idx"] = raw["criterion_idx"]
                    return [val]

        return None

    # ------------------------------------------------------------------
    # Step 4.5: Conditional Criteria Disambiguation
    # ------------------------------------------------------------------
    async def _disambiguate_conditional_criteria(
        self,
        rubric: dict,
        evidence_by_criterion: Dict[int, List[Dict]],
        task: str,
        init_url_context: str,
    ) -> dict:
        conditional_indices = [
            i for i, item in enumerate(rubric["items"]) if "condition" in item
        ]

        conditional_criteria_with_evidence = ""
        for c_idx in conditional_indices:
            criterion = rubric["items"][c_idx]
            conditional_criteria_with_evidence += (
                f"\n## Criterion {c_idx}: {criterion['criterion']}\n"
            )
            conditional_criteria_with_evidence += (
                f"**Condition:** {criterion['condition']}\n"
            )
            conditional_criteria_with_evidence += (
                f"**Description:** {criterion['description']}\n"
            )
            conditional_criteria_with_evidence += (
                f"**Max Points:** {criterion['max_points']}\n"
            )

            for analysis in sorted(
                evidence_by_criterion.get(c_idx, []),
                key=lambda x: x.get("screenshot_idx", 0),
            ):
                sn = analysis.get("screenshot_idx", 0)
                conditional_criteria_with_evidence += (
                    f"\n### Screenshot {sn + 1} Evidence:\n"
                )
                conditional_criteria_with_evidence += (
                    f"- Evidence: {analysis.get('screenshot_evidence', 'N/A')}\n"
                )
                conditional_criteria_with_evidence += (
                    f"- Analysis: {analysis.get('criterion_analysis', 'N/A')}\n"
                )
                conditional_criteria_with_evidence += (
                    f"- Discrepancies: {analysis.get('discrepancies', 'N/A')}\n"
                )
                if "condition_verification" in analysis:
                    conditional_criteria_with_evidence += f"- Per-screenshot condition verification: {analysis['condition_verification']}\n"

        prompt = Template(CONDITIONAL_CRITERIA_DISAMBIGUATION_PROMPT).substitute(
            task_definition=task,
            init_url_context=init_url_context,
            num_conditional=len(conditional_indices),
            conditional_criteria_with_evidence=conditional_criteria_with_evidence,
        )
        messages = self.DEFAULT_SYSTEM_MESSAGES + [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        last_error = None
        while max_iters > 0:
            try:
                response_text = await self._call_llm(
                    messages, self._gpt5_client, json_output=True
                )
                result = json.loads(response_text)
                if "disambiguation" not in result:
                    raise ValueError("Missing required field: 'disambiguation'")
                entries = result["disambiguation"]
                if not isinstance(entries, list):
                    raise ValueError(
                        f"'disambiguation' must be a list, got {type(entries).__name__}"
                    )
                if len(entries) != len(conditional_indices):
                    raise ValueError(
                        f"Expected {len(conditional_indices)} entries, got {len(entries)}"
                    )

                for i, entry in enumerate(entries):
                    expected_idx = conditional_indices[i]
                    if "criterion_idx" not in entry:
                        raise ValueError(f"Entry {i} missing 'criterion_idx'")
                    if entry["criterion_idx"] != expected_idx:
                        raise ValueError(
                            f"Entry {i} has criterion_idx={entry['criterion_idx']}, expected {expected_idx}"
                        )
                    if "condition" not in entry:
                        raise ValueError(f"Entry {i} missing 'condition'")
                    expected_condition = rubric["items"][expected_idx]["condition"]
                    if entry["condition"] != expected_condition:
                        raise ValueError(
                            f"Entry {i}: condition text mismatch. "
                            f"Expected verbatim: {expected_condition!r}, "
                            f"got: {entry['condition']!r}"
                        )
                    if "reasoning" not in entry:
                        raise ValueError(f"Entry {i} missing 'reasoning'")
                    if not isinstance(entry["reasoning"], str):
                        raise ValueError(f"Entry {i}: 'reasoning' must be a string")
                    if "is_condition_met" not in entry:
                        raise ValueError(f"Entry {i} missing 'is_condition_met'")
                    if not isinstance(entry["is_condition_met"], bool):
                        raise ValueError(
                            f"Entry {i}: 'is_condition_met' must be a boolean"
                        )

                for entry in entries:
                    idx = entry["criterion_idx"]
                    rubric["items"][idx]["is_condition_met"] = entry["is_condition_met"]
                    rubric["items"][idx]["condition_disambiguation_reasoning"] = entry[
                        "reasoning"
                    ]
                return rubric
            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"Error in conditional criteria disambiguation (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error: {e}. Please ensure your output follows the exact format specified.",
                    }
                )
                max_iters -= 1

        # Fallback: OR-semantics (graceful degradation)
        logger.warning(
            f"Failed conditional criteria disambiguation after {self.config.max_iters} attempts. Last error: {last_error}. "
            f"Falling back to per-criterion OR semantics."
        )
        for c_idx in conditional_indices:
            verifications = [
                a["condition_verification"]
                for a in evidence_by_criterion.get(c_idx, [])
                if "condition_verification" in a
            ]
            if verifications:
                rubric["items"][c_idx]["is_condition_met"] = any(verifications)
        return rubric

    # ------------------------------------------------------------------
    # Step 5: Rubric Reality Check
    # ------------------------------------------------------------------
    async def _rubric_reality_check(
        self,
        rubric: dict,
        evidence_by_criterion: Dict[int, List[Dict]],
        task: str,
        init_url_context: str,
    ) -> dict:
        criteria_with_evidence = ""
        for c_idx, criterion in enumerate(rubric["items"]):
            criteria_with_evidence += (
                f"\n## Criterion {c_idx}: {criterion['criterion']}\n"
            )
            criteria_with_evidence += f"**Description:** {criterion['description']}\n"
            criteria_with_evidence += f"**Max Points:** {criterion['max_points']}\n"
            for analysis in sorted(
                evidence_by_criterion.get(c_idx, []),
                key=lambda x: x.get("screenshot_idx", 0),
            ):
                sn = analysis.get("screenshot_idx", 0)
                criteria_with_evidence += f"\n### Screenshot {sn + 1} Evidence:\n"
                criteria_with_evidence += (
                    f"- Evidence: {analysis.get('screenshot_evidence', 'N/A')}\n"
                )
                criteria_with_evidence += (
                    f"- Analysis: {analysis.get('criterion_analysis', 'N/A')}\n"
                )
                criteria_with_evidence += (
                    f"- Discrepancies: {analysis.get('discrepancies', 'N/A')}\n"
                )
            if not evidence_by_criterion.get(c_idx):
                criteria_with_evidence += "\nNo screenshot evidence available.\n"

        num_criteria = len(rubric["items"])
        prompt = Template(RUBRIC_REALITY_CHECK_PROMPT).substitute(
            task_definition=task,
            init_url_context=init_url_context,
            num_criteria=num_criteria,
            last_criterion_idx=num_criteria - 1,
            criteria_with_evidence=criteria_with_evidence,
        )
        messages = self.DEFAULT_SYSTEM_MESSAGES + [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        last_error = None
        while max_iters > 0:
            try:
                response_text = await self._call_llm(
                    messages, self._gpt5_client, json_output=True
                )
                result = json.loads(response_text)
                if "reality_checks" not in result:
                    raise ValueError("Missing required field: 'reality_checks'")
                checks = result["reality_checks"]
                if not isinstance(checks, list):
                    raise ValueError(
                        f"'reality_checks' must be a list, got {type(checks).__name__}"
                    )
                if len(checks) != num_criteria:
                    raise ValueError(
                        f"Expected {num_criteria} reality_checks entries, got {len(checks)}"
                    )
                for i, check in enumerate(checks):
                    if "criterion_idx" not in check:
                        raise ValueError(f"Entry {i} missing 'criterion_idx'")
                    if check["criterion_idx"] != i:
                        raise ValueError(
                            f"Entry {i} has criterion_idx={check['criterion_idx']}, expected {i}"
                        )
                    if "reality_notes" not in check:
                        raise ValueError(f"Entry {i} missing 'reality_notes'")
                    if not isinstance(check["reality_notes"], str):
                        raise ValueError(
                            f"Entry {i}: 'reality_notes' must be string, got {type(check['reality_notes']).__name__}"
                        )

                for check in checks:
                    rubric["items"][check["criterion_idx"]]["reality_notes"] = check[
                        "reality_notes"
                    ]
                return rubric
            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"Error in rubric reality check (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error: {e}. Please ensure your output follows the exact format specified.",
                    }
                )
                max_iters -= 1

        logger.warning(
            f"Failed rubric reality check after {self.config.max_iters} attempts. Last error: {last_error}. "
            f"Proceeding without reality notes."
        )
        for item in rubric["items"]:
            item["reality_notes"] = ""
        return rubric

    # ------------------------------------------------------------------
    # Step 6a: Per-Criterion Rescoring (legacy, sequential)
    # ------------------------------------------------------------------
    async def _rescore_criterion_with_screenshots(
        self,
        rubric: dict,
        evidence_by_criterion: Dict[int, List[Dict]],
        task: str,
        init_url_context: str,
        action_history: str,
        predicted_output: str,
        total_screenshots: int = 0,
    ) -> dict:
        for c_idx in range(len(rubric["items"])):
            criterion = rubric["items"][c_idx]
            if "condition" in criterion and not criterion.get(
                "is_condition_met", False
            ):
                criterion["applicable_evidence"] = (
                    "N/A — condition not met, criterion skipped."
                )
                criterion["post_image_justification"] = (
                    "Condition not met; criterion does not apply and was not rescored."
                )
                criterion["post_image_earned_points"] = 0.0
                continue

            analyses = sorted(
                evidence_by_criterion.get(c_idx, []),
                key=lambda x: x.get("screenshot_idx", 0),
            )
            concatenated = ""
            for i_a, analysis in enumerate(analyses):
                sn = analysis.get("screenshot_idx", i_a)
                concatenated += (
                    f"\n### Screenshot {sn + 1} of {total_screenshots} Analysis:\n"
                )
                concatenated += (
                    f"**Evidence:** {analysis.get('screenshot_evidence', 'N/A')}\n"
                )
                concatenated += (
                    f"**Analysis:** {analysis.get('criterion_analysis', 'N/A')}\n"
                )
                concatenated += (
                    f"**Discrepancies:** {analysis.get('discrepancies', 'N/A')}\n"
                )
                concatenated += f"**Environment Issues Confirmed:** {analysis.get('environment_issues_confirmed', False)}\n"
            if not concatenated:
                concatenated = "No screenshot evidence available for this criterion."

            full_rubric_context = self._build_full_rubric_context(rubric, c_idx)
            prompt = Template(MM_CRITERION_RESCORING_PROMPT).substitute(
                task_definition=task,
                init_url_context=init_url_context,
                action_history=action_history,
                agent_predicted_output=predicted_output,
                full_rubric_context=full_rubric_context,
                max_points=criterion["max_points"],
                concatenated_screenshot_analyses=concatenated,
            )
            messages = self.DEFAULT_SYSTEM_MESSAGES + [
                {"role": "user", "content": prompt}
            ]

            max_iters = self.config.max_iters
            last_error = None
            while max_iters > 0:
                try:
                    response_text = await self._call_llm(
                        messages, self._o4mini_client, json_output=True
                    )
                    rescore = json.loads(response_text)
                    self._validate_rescore(rescore, criterion["max_points"])
                    criterion["applicable_evidence"] = rescore["applicable_evidence"]
                    criterion["post_image_justification"] = rescore[
                        "post_image_justification"
                    ]
                    criterion["post_image_earned_points"] = float(
                        rescore["post_image_earned_points"]
                    )
                    break
                except Exception as e:
                    last_error = str(e)
                    logger.error(
                        f"Error rescoring criterion {c_idx} (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": f"Error: {e}. Please ensure your output includes all required fields in the correct format.",
                        }
                    )
                    max_iters -= 1
            else:
                logger.warning(
                    f"Failed to rescore criterion {c_idx} after {self.config.max_iters} attempts. Last error: {last_error}"
                )
                criterion["post_image_justification"] = (
                    f"Rescoring failed after {self.config.max_iters} attempts, keeping baseline score. Last error: {last_error}"
                )
                criterion["post_image_earned_points"] = float(
                    criterion.get("earned_points", 0)
                )
        return rubric

    # ------------------------------------------------------------------
    # Step 6b: Whole-Rubric Rescoring (default, 1 gpt-5 call)
    # ------------------------------------------------------------------
    async def _rescore_rubric_with_screenshots(
        self,
        rubric: dict,
        evidence_by_criterion: Dict[int, List[Dict]],
        task: str,
        init_url_context: str,
        action_history: str,
        predicted_output: str,
        total_screenshots: int = 0,
    ) -> dict:
        num_criteria = len(rubric["items"])
        skipped = set()
        for c_idx, criterion in enumerate(rubric["items"]):
            if "condition" in criterion and not criterion.get(
                "is_condition_met", False
            ):
                criterion["applicable_evidence"] = (
                    "N/A — condition not met, criterion skipped."
                )
                criterion["post_image_justification"] = (
                    "Condition not met; criterion does not apply and was not rescored."
                )
                criterion["post_image_earned_points"] = 0.0
                skipped.add(c_idx)

        full_rubric = self._build_full_rubric_with_baselines(rubric)
        all_evidence = self._build_all_screenshot_evidence_text(
            rubric, evidence_by_criterion, total_screenshots
        )

        prompt = Template(MM_RUBRIC_RESCORING_PROMPT).substitute(
            task_definition=task,
            init_url_context=init_url_context,
            action_history=action_history,
            agent_predicted_output=predicted_output,
            full_rubric_with_baselines=full_rubric,
            all_screenshot_evidence=all_evidence,
            num_criteria=num_criteria,
            num_criteria_minus_1=num_criteria - 1,
        )
        messages = self.DEFAULT_SYSTEM_MESSAGES + [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        last_error = None
        while max_iters > 0:
            try:
                response_text = await self._call_llm(
                    messages, self._gpt5_client, json_output=True
                )
                result = json.loads(response_text)
                if "items" not in result:
                    raise ValueError("Missing required field: 'items'")
                items = result["items"]
                if not isinstance(items, list):
                    raise ValueError(
                        f"'items' must be a list, got {type(items).__name__}"
                    )
                if len(items) != num_criteria:
                    raise ValueError(f"Expected {num_criteria} items, got {len(items)}")

                for i, item in enumerate(items):
                    if "criterion_idx" not in item:
                        raise ValueError(f"Item {i} missing 'criterion_idx'")
                    if item["criterion_idx"] != i:
                        raise ValueError(
                            f"Item {i} has criterion_idx={item['criterion_idx']}, expected {i}"
                        )

                    # Validate required fields (inline with Item prefix, matching original)
                    required_fields = [
                        "applicable_evidence",
                        "post_image_justification",
                        "post_image_earned_points",
                    ]
                    missing_fields = []
                    type_errors = []

                    max_points = rubric["items"][i]["max_points"]

                    for field in required_fields:
                        if field not in item:
                            missing_fields.append(field)
                        elif field in (
                            "post_image_justification",
                            "applicable_evidence",
                        ):
                            if not isinstance(item[field], str):
                                type_errors.append(
                                    f"Item {i}: {field} must be a string, got {type(item[field]).__name__}"
                                )
                            elif not item[field]:
                                type_errors.append(f"Item {i}: {field} cannot be empty")
                        elif field == "post_image_earned_points":
                            if not isinstance(item[field], (int, float)):
                                type_errors.append(
                                    f"Item {i}: {field} must be a number, got {type(item[field]).__name__}"
                                )
                            elif not (0 <= item[field] <= max_points):
                                type_errors.append(
                                    f"Item {i}: {field} must be between 0 and {max_points}, got {item[field]}"
                                )

                    if missing_fields or type_errors:
                        error_msg = "Invalid rescoring output. "
                        if missing_fields:
                            error_msg += (
                                f"Missing fields: {', '.join(missing_fields)}. "
                            )
                        if type_errors:
                            error_msg += f"Errors: {'; '.join(type_errors)}."
                        raise ValueError(error_msg)

                for i, item in enumerate(items):
                    if i in skipped:
                        continue
                    rubric["items"][i]["applicable_evidence"] = item[
                        "applicable_evidence"
                    ]
                    rubric["items"][i]["post_image_justification"] = item[
                        "post_image_justification"
                    ]
                    rubric["items"][i]["post_image_earned_points"] = float(
                        item["post_image_earned_points"]
                    )
                return rubric
            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"Error rescoring rubric (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error: {e}. Please ensure your output includes all {num_criteria} criteria in the correct format.",
                    }
                )
                max_iters -= 1

        logger.warning(
            f"Failed to rescore rubric after {self.config.max_iters} attempts. Last error: {last_error}"
        )
        for i, criterion in enumerate(rubric["items"]):
            if i not in skipped:
                criterion["post_image_justification"] = (
                    f"Rescoring failed after {self.config.max_iters} attempts, keeping baseline score. Last error: {last_error}"
                )
                criterion["post_image_earned_points"] = float(
                    criterion.get("earned_points", 0)
                )
        return rubric

    @staticmethod
    def _validate_rescore(rescore: dict, max_points: float) -> None:
        required_fields = [
            "applicable_evidence",
            "post_image_justification",
            "post_image_earned_points",
        ]
        missing_fields = []
        type_errors = []

        for field in required_fields:
            if field not in rescore:
                missing_fields.append(field)
            elif field in ("post_image_justification", "applicable_evidence"):
                if not isinstance(rescore[field], str):
                    type_errors.append(
                        f"{field} must be a string, got {type(rescore[field]).__name__}"
                    )
                elif not rescore[field]:
                    type_errors.append(f"{field} cannot be empty")
            elif field == "post_image_earned_points":
                if not isinstance(rescore[field], (int, float)):
                    type_errors.append(
                        f"{field} must be a number, got {type(rescore[field]).__name__}"
                    )
                elif not (0 <= rescore[field] <= max_points):
                    type_errors.append(
                        f"{field} must be between 0 and {max_points}, got {rescore[field]}"
                    )

        if missing_fields or type_errors:
            error_msg = "Invalid rescoring output. "
            if missing_fields:
                error_msg += f"Missing fields: {', '.join(missing_fields)}. "
            if type_errors:
                error_msg += f"Errors: {'; '.join(type_errors)}."
            raise ValueError(error_msg)

    # ------------------------------------------------------------------
    # Step 7: Detect Unsolicited Side Effects
    # ------------------------------------------------------------------
    async def _detect_unsolicited_side_effects(
        self,
        rubric: dict,
        evidence_by_criterion: Dict[int, List[Dict]],
        task: str,
        init_url_context: str,
        action_history: str,
    ) -> dict:
        all_evidence_text = ""
        for c_idx, analyses in evidence_by_criterion.items():
            criterion = rubric["items"][c_idx]
            all_evidence_text += f"\n\n## Criterion {c_idx}: {criterion['criterion']}\n"
            for analysis in analyses:
                all_evidence_text += (
                    f"- **Evidence:** {analysis.get('screenshot_evidence', 'N/A')}\n"
                )
                all_evidence_text += (
                    f"- **Analysis:** {analysis.get('criterion_analysis', 'N/A')}\n"
                )
                all_evidence_text += (
                    f"- **Discrepancies:** {analysis.get('discrepancies', 'N/A')}\n"
                )

        scored_summary = self._build_scored_rubric_summary(rubric)
        prompt = Template(PENALIZE_UNSOLICITED_SIDE_EFFECTS_PROMPT).substitute(
            task_definition=task,
            init_url_context=init_url_context,
            action_history=action_history,
            scored_rubric_summary=scored_summary,
            all_concatenated_evidence=all_evidence_text,
        )
        messages = self.DEFAULT_SYSTEM_MESSAGES + [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        last_error = None
        while max_iters > 0:
            try:
                response_text = await self._call_llm(
                    messages, self._gpt5_client, json_output=True
                )
                result = json.loads(response_text)
                if "reasoning" not in result:
                    raise ValueError("Missing required field: reasoning")
                if not isinstance(result["reasoning"], str) or not result["reasoning"]:
                    raise ValueError(
                        f"reasoning must be a non-empty string, got {type(result['reasoning']).__name__}"
                    )
                if "requires_penalty" not in result:
                    raise ValueError("Missing required field: requires_penalty")
                if not isinstance(result["requires_penalty"], bool):
                    raise ValueError(
                        f"requires_penalty must be a boolean, got {type(result['requires_penalty']).__name__}"
                    )
                if "penalty_criteria" not in result:
                    raise ValueError("Missing required field: penalty_criteria")
                if not isinstance(result["penalty_criteria"], list):
                    raise ValueError(
                        f"penalty_criteria must be a list, got {type(result['penalty_criteria']).__name__}"
                    )

                for i, penalty in enumerate(result["penalty_criteria"]):
                    required_penalty_fields = [
                        "criterion",
                        "description",
                        "max_points",
                        "post_image_justification",
                        "post_image_earned_points",
                    ]
                    missing_fields = [
                        f for f in required_penalty_fields if f not in penalty
                    ]
                    if missing_fields:
                        raise ValueError(
                            f"Penalty criterion {i} missing fields: {', '.join(missing_fields)}"
                        )

                    # Type validation
                    if (
                        not isinstance(penalty["criterion"], str)
                        or not penalty["criterion"]
                    ):
                        raise ValueError(
                            f"Penalty criterion {i}: 'criterion' must be a non-empty string"
                        )
                    if (
                        not isinstance(penalty["description"], str)
                        or not penalty["description"]
                    ):
                        raise ValueError(
                            f"Penalty criterion {i}: 'description' must be a non-empty string"
                        )
                    if (
                        not isinstance(penalty["max_points"], (int, float))
                        or penalty["max_points"] <= 0
                    ):
                        raise ValueError(
                            f"Penalty criterion {i}: 'max_points' must be a positive number"
                        )
                    if penalty["post_image_earned_points"] != 0:
                        raise ValueError(
                            f"Penalty criterion {i}: 'post_image_earned_points' must be 0 for penalties"
                        )
                    penalty["earned_points"] = penalty["post_image_earned_points"]
                    penalty["justification"] = penalty["post_image_justification"]

                if result.get("requires_penalty"):
                    for p in result["penalty_criteria"]:
                        p["penalty"] = True
                    return {
                        "reasoning": result["reasoning"],
                        "requires_penalty": True,
                        "penalty_criteria": result["penalty_criteria"],
                    }
                return {
                    "reasoning": result["reasoning"],
                    "requires_penalty": False,
                    "penalty_criteria": [],
                }
            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"Error detecting side effects (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error: {e}. Please ensure your output follows the exact format specified with all required fields.",
                    }
                )
                max_iters -= 1

        logger.warning(
            f"Failed to detect side effects after {self.config.max_iters} attempts. Last error: {last_error}"
        )
        return {
            "reasoning": f"Failed after {self.config.max_iters} attempts. Last error: {last_error}",
            "requires_penalty": False,
            "penalty_criteria": [],
        }

    # ------------------------------------------------------------------
    # Step 8: Outcome Verification
    # ------------------------------------------------------------------
    async def _outcome_verification(
        self,
        rubric: dict,
        evidence_by_criterion: Dict[int, List[Dict]],
        task: str,
        init_url_context: str,
        action_history: str,
        predicted_output: str,
        total_screenshots: int = 0,
    ) -> dict:
        rubric_summary = self._build_scored_rubric_summary(rubric)
        evidence_summary = self._build_all_screenshot_evidence_text(
            rubric, evidence_by_criterion, total_screenshots
        )

        prompt = Template(OUTCOME_VERIFICATION_PROMPT).substitute(
            task_definition=task,
            init_url_context=init_url_context,
            rubric_summary=rubric_summary,
            evidence_summary=evidence_summary,
            action_history=action_history,
            predicted_output=predicted_output or "N/A",
        )
        messages = self.DEFAULT_SYSTEM_MESSAGES + [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        last_error = None
        while max_iters > 0:
            try:
                response_text = await self._call_llm(
                    messages, self._gpt5_client, json_output=True
                )
                result = json.loads(response_text)
                if "primary_intent" not in result:
                    raise ValueError("Missing required field: primary_intent")
                if (
                    not isinstance(result["primary_intent"], str)
                    or not result["primary_intent"]
                ):
                    raise ValueError("primary_intent must be a non-empty string")
                if "reasoning" not in result:
                    raise ValueError("Missing required field: reasoning")
                if not isinstance(result["reasoning"], str) or not result["reasoning"]:
                    raise ValueError("reasoning must be a non-empty string")
                if "output_success" not in result:
                    raise ValueError("Missing required field: output_success")
                if not isinstance(result["output_success"], bool):
                    raise ValueError(
                        f"output_success must be a boolean, got {type(result['output_success']).__name__}"
                    )
                logger.info(
                    f"Outcome verification result: output_success={result['output_success']}, primary_intent={result['primary_intent']}"
                )
                return result
            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"Error in outcome verification (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error: {e}. Please ensure your output follows the exact JSON format specified with all required fields.",
                    }
                )
                max_iters -= 1

        logger.warning(
            f"Failed outcome verification after {self.config.max_iters} attempts. Last error: {last_error}"
        )
        return {
            "primary_intent": f"Failed after {self.config.max_iters} attempts. Last error: {last_error}",
            "reasoning": f"Outcome verification failed after {self.config.max_iters} attempts. Last error: {last_error}",
            "output_success": None,
        }

    # ------------------------------------------------------------------
    # Step 9a: Points of Failure Analysis
    # ------------------------------------------------------------------
    async def _first_point_of_failure_analysis(
        self,
        rubric: dict,
        evidence_by_criterion: Dict[int, List[Dict]],
        task: str,
        init_url_context: str,
        action_history: str,
        predicted_output: str,
        outcome_result: dict,
        total_screenshots: int = 0,
        action_definitions: Optional[Dict[str, Set[str]]] = None,
        step_actions: Optional[List[Dict[str, Any]]] = None,
    ) -> dict:
        """Step 9a: Failure Point Analysis — identify all failure points in the
        trajectory.  The first (earliest) point of failure is computed
        programmatically from the LLM's ``failure_points`` list.

        Tool interaction errors 6.1 (Invalid invocation) and 6.2
        (Hallucinated action) are also detected programmatically from
        ``step_actions`` when available, and injected into the result.

        Uses 1 gpt-5 call (with up to 5 retry attempts on validation errors).

        Args:
            action_definitions: Mapping of ``{action_name: set(arg_names)}``
                describing the agent's available tools.  If ``None``, defaults
                are derived from ``resolve_tools(["BROWSER_TOOLS_WITH_READ_PAGE"])``.

        Returns:
            Dict with ``reasoning``, ``has_failure``, ``failure_points``,
            ``first_failure_step``, ``first_failure_summary``.
        """
        if action_definitions is None:
            action_definitions = self.config.action_definitions

        rubric_summary = self._build_scored_rubric_summary(rubric)
        evidence_summary = self._build_all_screenshot_evidence_text(
            rubric, evidence_by_criterion, total_screenshots
        )

        outcome_success = outcome_result.get("output_success")
        if outcome_success is True:
            outcome_label = "SUCCESS"
        elif outcome_success is False:
            outcome_label = "FAILURE"
        else:
            outcome_label = "UNKNOWN"
        outcome_text = (
            f"Task outcome: {outcome_label}\n"
            f"Primary intent: {outcome_result.get('primary_intent', 'N/A')}\n"
            f"Reasoning: {outcome_result.get('reasoning', 'N/A')}"
        )

        # Build prompt variables from action_definitions
        action_space_str = ", ".join(f"`{a}`" for a in action_definitions)
        action_defs_lines = []
        for act_name in sorted(action_definitions):
            args_str = ", ".join(sorted(action_definitions[act_name]))
            action_defs_lines.append(f"  - `{act_name}({args_str})`")
        action_definitions_text = "\n".join(action_defs_lines)

        prompt = Template(FIRST_POINT_OF_FAILURE_PROMPT).substitute(
            task_definition=task,
            init_url_context=init_url_context,
            action_history=action_history,
            predicted_output=predicted_output or "N/A",
            rubric_summary=rubric_summary,
            evidence_summary=evidence_summary,
            outcome_verification=outcome_text,
            action_space=action_space_str,
            action_definitions_text=action_definitions_text,
        )
        messages = self.DEFAULT_SYSTEM_MESSAGES + [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        last_error = None
        while max_iters > 0:
            try:
                response_text = await self._call_llm(
                    messages, self._gpt5_client, json_output=True
                )
                result = json.loads(response_text)

                # -- Validate top-level fields --
                if "reasoning" not in result:
                    raise ValueError("Missing required field: reasoning")
                if not isinstance(result["reasoning"], str) or not result["reasoning"]:
                    raise ValueError("reasoning must be a non-empty string")
                if "has_failure" not in result:
                    raise ValueError("Missing required field: has_failure")
                if not isinstance(result["has_failure"], bool):
                    raise ValueError(
                        f"has_failure must be a boolean, got {type(result['has_failure']).__name__}"
                    )
                if "failure_points" not in result:
                    raise ValueError("Missing required field: failure_points")
                if not isinstance(result["failure_points"], list):
                    raise ValueError(
                        f"failure_points must be a list, got {type(result['failure_points']).__name__}"
                    )

                # -- Validate each failure point --
                for i, fp in enumerate(result["failure_points"]):
                    required_fields = [
                        "step_numbers",
                        "error_code",
                        "error_category",
                        "error_type",
                        "what_happened",
                        "agent_reasoning",
                        "evidence",
                        "impact",
                    ]
                    missing = [f for f in required_fields if f not in fp]
                    if missing:
                        raise ValueError(
                            f"failure_points[{i}] missing fields: {', '.join(missing)}"
                        )

                    # Validate step_numbers format: "INT", "INT-INT", or "INT,INT,..."
                    sn = str(fp["step_numbers"]).replace(" ", "")
                    if not self._STEP_NUMBERS_RE.match(sn):
                        raise ValueError(
                            f'failure_points[{i}].step_numbers must be "INT", '
                            f'"INT-INT", or "INT,INT,..." (e.g. "5", "5-7", or '
                            f'"5,8,12"), got "{fp["step_numbers"]}". '
                            f"Never use N/A or descriptive text."
                        )
                    fp["step_numbers"] = sn

                # -- Inject programmatic 6.1/6.2 errors --
                if step_actions is not None and action_definitions:
                    prog_fps = self._detect_tool_interaction_errors(
                        step_actions, action_definitions
                    )
                    if prog_fps:
                        existing = {
                            (fp.get("step_numbers"), fp.get("error_code"))
                            for fp in result["failure_points"]
                        }
                        for pfp in prog_fps:
                            key = (pfp["step_numbers"], pfp["error_code"])
                            if key not in existing:
                                result["failure_points"].append(pfp)
                        result["failure_points"].sort(
                            key=lambda fp: self._parse_first_step_number(
                                fp.get("step_numbers", "")
                            )
                        )
                        if result["failure_points"]:
                            result["has_failure"] = True

                # -- Compute first_failure_step programmatically --
                first_failure_step, first_failure_summary = self._compute_first_failure(
                    result["failure_points"]
                )
                result["first_failure_step"] = first_failure_step
                result["first_failure_summary"] = first_failure_summary

                logger.info(
                    f"Points of failure result: has_failure={result['has_failure']}, "
                    f"first_failure_step={result['first_failure_step']}, "
                    f"num_failure_points={len(result['failure_points'])}"
                )
                return result
            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"Error in points of failure analysis (attempt {self.config.max_iters + 1 - max_iters}): {e}"
                )
                messages.append(
                    {
                        "role": "user",
                        "content": f"Error: {e}. Please ensure your output follows the exact JSON format specified with all required fields.",
                    }
                )
                max_iters -= 1

        logger.warning(
            f"Failed points of failure analysis after {self.config.max_iters} attempts. Last error: {last_error}"
        )
        return {
            "reasoning": f"Failed after {self.config.max_iters} attempts. Last error: {last_error}",
            "has_failure": False,
            "failure_points": [],
            "first_failure_step": None,
            "first_failure_summary": "",
        }

    @staticmethod
    def _parse_first_step_number(step_numbers: str) -> int:
        """Parse the minimum step number from a ``step_numbers`` string.

        Handles formats: ``"5"``, ``"5-7"``, ``"5,8,12"``, ``"8,5"``, ``"3-7,12"``.
        For ranges, takes the min of endpoints.  For comma-separated lists,
        takes the global minimum across all entries.
        Returns a large sentinel value if parsing fails.
        """
        try:
            step_numbers = step_numbers.strip()
            values: list[int] = []
            for token in step_numbers.split(","):
                token = token.strip()
                if "-" in token:
                    values.extend(int(p.strip()) for p in token.split("-"))
                else:
                    values.append(int(token))
            return min(values) if values else 999999
        except (ValueError, IndexError):
            return 999999

    @staticmethod
    def _compute_first_failure(
        failure_points: List[Dict],
    ) -> Tuple[Optional[int], str]:
        """Compute ``first_failure_step`` and ``first_failure_summary`` from
        the LLM's ``failure_points`` list.

        Priority: first failure of any kind by step number (the LLM no longer
        outputs severity tiers, so we simply pick the earliest failure point).
        If no failures at all, returns ``(None, "")``.
        """
        if not failure_points:
            return None, ""

        def sort_key(fp: Dict) -> int:
            return MMRubricAgent._parse_first_step_number(fp.get("step_numbers", ""))

        sorted_fps = sorted(failure_points, key=sort_key)

        fp = sorted_fps[0]
        step = MMRubricAgent._parse_first_step_number(fp.get("step_numbers", ""))
        summary = (
            f"[{fp.get('error_code', '')}] {fp.get('error_type', '')}: "
            f"{fp.get('what_happened', '')}"
        )
        return step if step != 999999 else None, summary

    @staticmethod
    def _detect_tool_interaction_errors(
        step_actions: List[Dict[str, Any]],
        action_definitions: Dict[str, Set[str]],
    ) -> List[Dict]:
        """Programmatically detect 6.1 (Invalid invocation) and 6.2
        (Hallucinated action) errors by comparing each step's action
        name and argument keys against ``action_definitions``.

        Returns a list of failure-point dicts matching the schema used
        by the LLM's ``failure_points`` list, with an extra
        ``"programmatic": True`` flag.
        """
        errors: List[Dict] = []
        valid_action_names = set(action_definitions.keys())

        for sa in step_actions:
            step = sa["step_number"]
            name = sa["action_name"]
            args_keys = set(sa["action_args_keys"]) - {"_call_id"}

            if not name:
                continue

            if name not in valid_action_names:
                errors.append(
                    {
                        "step_numbers": str(step),
                        "error_code": "6.2",
                        "error_category": "Tool Interaction",
                        "error_type": "Hallucinated action",
                        "what_happened": (
                            f"The agent invoked `{name}` which does not exist "
                            f"in the available action space "
                            f"[{', '.join(sorted(valid_action_names))}]."
                        ),
                        "agent_reasoning": "",
                        "evidence": (
                            f"Action `{name}` is not defined in the tool schema."
                        ),
                        "impact": "The action could not be executed as intended.",
                        "programmatic": True,
                    }
                )
            else:
                expected_args = action_definitions[name]
                unknown_args = args_keys - expected_args
                if unknown_args:
                    errors.append(
                        {
                            "step_numbers": str(step),
                            "error_code": "6.1",
                            "error_category": "Tool Interaction",
                            "error_type": "Invalid invocation",
                            "what_happened": (
                                f"The agent called `{name}` with unknown "
                                f"argument(s): {', '.join(sorted(unknown_args))}. "
                                f"Valid arguments are: "
                                f"{', '.join(sorted(expected_args))}."
                            ),
                            "agent_reasoning": "",
                            "evidence": (
                                f"Arguments {sorted(unknown_args)} are not in "
                                f"the schema for `{name}`."
                            ),
                            "impact": (
                                "The action may not execute correctly due to "
                                "invalid arguments."
                            ),
                            "programmatic": True,
                        }
                    )

        return errors

    # ------------------------------------------------------------------
    # Step 9b: Post-execution Task Verification (trajectory-informed)
    # ------------------------------------------------------------------
    async def _classify_task_with_trajectory(
        self,
        rubric: dict,
        evidence_by_criterion: Dict[int, List[Dict]],
        task: str,
        init_url_context: str,
        action_history: str,
        predicted_output: str,
        outcome_result: dict,
        total_screenshots: int = 0,
        apps: str = "N/A",
    ) -> dict:
        """Step 9b: Trajectory-informed task verification.

        Uses the same ambiguity / validity axes as Step 10
        (``CHECK_VALID_TASK_PROMPT``), but enriched with the full trajectory
        context (action history, scored rubric, screenshot evidence, and
        outcome verification).  This allows the LLM to use execution evidence
        to make a more informed judgment about whether the *task itself* was
        ambiguous or invalid.

        Uses 1 o4-mini call (with up to 5 retry attempts on validation errors).

        Returns:
            Dict matching the ``TaskAgentResult`` schema, including
            ``is_ambiguous``, ``is_invalid``, etc.
        """
        from datetime import datetime, timezone

        rubric_summary = self._build_scored_rubric_summary(rubric)
        evidence_summary = self._build_all_screenshot_evidence_text(
            rubric, evidence_by_criterion, total_screenshots
        )

        outcome_success = outcome_result.get("output_success")
        if outcome_success is True:
            outcome_label = "SUCCESS"
        elif outcome_success is False:
            outcome_label = "FAILURE"
        else:
            outcome_label = "UNKNOWN"
        outcome_text = (
            f"Task outcome: {outcome_label}\n"
            f"Primary intent: {outcome_result.get('primary_intent', 'N/A')}\n"
            f"Reasoning: {outcome_result.get('reasoning', 'N/A')}"
        )

        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        prompt = Template(CHECK_VALID_TASK_WITH_TRAJECTORY_PROMPT).substitute(
            task_definition=task,
            init_url_context=init_url_context,
            apps=apps,
            date=date,
            action_history=action_history,
            predicted_output=predicted_output or "N/A",
            rubric_summary=rubric_summary,
            evidence_summary=evidence_summary,
            outcome_verification=outcome_text,
        )
        messages = self.DEFAULT_SYSTEM_MESSAGES + [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        last_error = None
        while max_iters > 0:
            try:
                response_text = await self._call_llm(
                    messages, self._o4mini_client, json_output=True
                )
                result = json.loads(response_text)
                _validate_verification_result(result)
                logger.info(
                    "Step 9b task verification result: is_ambiguous=%s, "
                    "is_invalid=%s",
                    result["is_ambiguous"],
                    result["is_invalid"],
                )
                return result
            except Exception as e:
                last_error = str(e)
                attempt = self.config.max_iters + 1 - max_iters
                logger.error(
                    f"Error in trajectory-informed task verification "
                    f"(attempt {attempt}): {e}"
                )
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"Error: {e}. Please ensure your output follows "
                            "the exact JSON format specified with all required "
                            "fields."
                        ),
                    }
                )
                max_iters -= 1

        logger.warning(
            "Failed trajectory-informed task verification after %d attempts. "
            "Last error: %s",
            self.config.max_iters,
            last_error,
        )
        return {
            "reasoning_is_ambiguous": (
                f"Failed after {self.config.max_iters} attempts. Last error: {last_error}"
            ),
            "is_ambiguous": None,
            "ambiguity_codes": [],
            "reasoning_is_invalid": (
                f"Failed after {self.config.max_iters} attempts. Last error: {last_error}"
            ),
            "is_invalid": None,
            "invalid_task_codes": [],
        }

    # ------------------------------------------------------------------
    # Step 10: Unified Task Verification (CHECK_VALID_TASK_PROMPT)
    # ------------------------------------------------------------------
    async def _classify_task(
        self,
        task: str,
        url: str,
        apps: list[str] | None = None,
    ) -> dict:
        """Step 10: Delegates to :func:`task_classification.classify_task`.

        Returns the ``TaskAgentResult`` as a plain dict so it can be stored
        directly in the rubric JSON.
        """
        result = await classify_task(
            task,
            url,
            self._o4mini_client,
            apps=apps,
            system_messages=self.DEFAULT_SYSTEM_MESSAGES,
        )
        return result.model_dump()

    # ------------------------------------------------------------------
    # Score computation
    # ------------------------------------------------------------------
    @staticmethod
    def _compute_final_scores(
        rubric: dict, earned_points_field: str = "post_image_earned_points"
    ) -> Dict[str, float]:
        def sum_recursive(items):
            total_max, total_earned = 0.0, 0.0
            for criterion in items:
                if "items" in criterion and isinstance(criterion["items"], list):
                    sm, se = sum_recursive(criterion["items"])
                    total_max += sm
                    total_earned += se
                else:
                    if "condition" in criterion:
                        if criterion.get("is_condition_met", False):
                            total_max += float(criterion["max_points"])
                            total_earned += float(criterion.get(earned_points_field, 0))
                    else:
                        total_max += float(criterion["max_points"])
                        total_earned += float(criterion.get(earned_points_field, 0))
            return total_max, total_earned

        total_max, total_earned = sum_recursive(rubric["items"])
        return {"total_max_points": total_max, "total_earned_points": total_earned}

    # ------------------------------------------------------------------
    # Steps 6+7 single instance (for majority voting)
    # ------------------------------------------------------------------
    async def _run_steps_6_7_single_instance(
        self,
        rubric_dict: dict,
        evidence_by_criterion: Dict,
        screenshots: List,
        task: str,
        init_url_context: str,
        action_history: str,
        predicted_output: str,
        instance_idx: int,
    ) -> Tuple[dict, float, dict]:
        rubric_copy = copy.deepcopy(rubric_dict)
        instance_steps = {}

        if self.config.rescore_whole_mm_rubric:
            rubric_copy = await self._rescore_rubric_with_screenshots(
                rubric_copy,
                evidence_by_criterion,
                task,
                init_url_context,
                action_history,
                predicted_output,
                total_screenshots=len(screenshots),
            )
        else:
            rubric_copy = await self._rescore_criterion_with_screenshots(
                rubric_copy,
                evidence_by_criterion,
                task,
                init_url_context,
                action_history,
                predicted_output,
                total_screenshots=len(screenshots),
            )

        instance_steps["step6_rescoring_summary"] = [
            {
                "criterion": item.get("criterion", ""),
                "earned_points": item.get("earned_points"),
                "post_image_earned_points": item.get("post_image_earned_points"),
                "max_points": item.get("max_points"),
                "justification": item.get("justification", ""),
                "applicable_evidence": item.get("applicable_evidence", ""),
                "post_image_justification": item.get("post_image_justification", ""),
                "reality_notes": item.get("reality_notes", ""),
                **({"condition": item["condition"]} if "condition" in item else {}),
                **(
                    {"is_condition_met": item["is_condition_met"]}
                    if "is_condition_met" in item
                    else {}
                ),
            }
            for item in rubric_copy["items"]
        ]

        side_effect_result = await self._detect_unsolicited_side_effects(
            rubric_copy,
            evidence_by_criterion,
            task,
            init_url_context,
            action_history,
        )
        instance_steps["step7_penalty_criteria"] = side_effect_result.get(
            "penalty_criteria", []
        )
        instance_steps["step7_reasoning"] = side_effect_result.get("reasoning", "")
        instance_steps["step7_requires_penalty"] = side_effect_result.get(
            "requires_penalty", False
        )

        if side_effect_result.get("penalty_criteria"):
            rubric_copy["items"].extend(side_effect_result["penalty_criteria"])

        final_scores = self._compute_final_scores(rubric_copy)
        rubric_copy["total_max_points"] = final_scores["total_max_points"]
        rubric_copy["total_earned_points"] = final_scores["total_earned_points"]

        score = (
            final_scores["total_earned_points"] / final_scores["total_max_points"]
            if final_scores["total_max_points"] > 0
            else 0.0
        )
        logger.info(f"[Majority Vote] Instance {instance_idx}: Score={score:.4f}")
        return rubric_copy, score, instance_steps

    @staticmethod
    def _select_median_instance(
        instances: List[Tuple[dict, float, dict]],
    ) -> Tuple[int, dict, float, dict]:
        sorted_by_score = sorted(enumerate(instances), key=lambda x: x[1][1])
        median_pos = len(sorted_by_score) // 2
        median_idx, (rubric_dict, score, steps) = sorted_by_score[median_pos]
        return median_idx, rubric_dict, score, steps

    # ------------------------------------------------------------------
    # Text-building helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _build_full_rubric_context(rubric: dict, target_criterion_idx: int) -> str:
        lines = []
        for j, criterion in enumerate(rubric["items"]):
            name = criterion.get("criterion", f"Criterion {j}")
            description = criterion.get("description", "")
            max_points = criterion.get("max_points", 0)
            baseline_earned = criterion.get("earned_points", 0)
            baseline_justification = criterion.get("justification", "")
            condition = criterion.get("condition")
            reality_notes = criterion.get("reality_notes", "")

            if j < target_criterion_idx:
                rescored_earned = criterion.get(
                    "post_image_earned_points", baseline_earned
                )
                rescored_justification = criterion.get(
                    "post_image_justification", baseline_justification
                )
                lines.append(f'--- Criterion {j}: "{name}" [ALREADY RESCORED] ---')
                lines.append(f"Description: {description}")
                if reality_notes:
                    lines.append(f"Reality Notes: {reality_notes}")
                if condition:
                    lines.append(f"Condition: {condition}")
                    lines.append(
                        f"Condition Met: {criterion.get('is_condition_met', 'unknown')}"
                    )
                lines.append(f"Max Points: {max_points}")
                lines.append(
                    f'Baseline: {baseline_earned}/{max_points} — "{baseline_justification}"'
                )
                lines.append(
                    f'Rescored: {rescored_earned}/{max_points} — "{rescored_justification}"'
                )
            elif j == target_criterion_idx:
                lines.append(
                    f'>>> Criterion {j}: "{name}" <<< SCORE THIS CRITERION <<<'
                )
                lines.append(f"Description: {description}")
                if reality_notes:
                    lines.append(f"Reality Notes: {reality_notes}")
                if condition:
                    lines.append(f"Condition: {condition}")
                    lines.append(
                        f"Condition Met: {criterion.get('is_condition_met', 'unknown')}"
                    )
                lines.append(f"Max Points: {max_points}")
                lines.append(
                    f'Baseline: {baseline_earned}/{max_points} — "{baseline_justification}"'
                )
            else:
                lines.append(f'--- Criterion {j}: "{name}" [NOT YET SCORED] ---')
                lines.append(f"Description: {description}")
                if reality_notes:
                    lines.append(f"Reality Notes: {reality_notes}")
                if condition:
                    lines.append(f"Condition: {condition}")
                lines.append(f"Max Points: {max_points}")
                lines.append(
                    f'Baseline: {baseline_earned}/{max_points} — "{baseline_justification}"'
                )
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _build_full_rubric_with_baselines(rubric: dict) -> str:
        lines = []
        for j, criterion in enumerate(rubric["items"]):
            lines.append(
                f'--- Criterion {j}: "{criterion.get("criterion", f"Criterion {j}")}" ---'
            )
            lines.append(f"Description: {criterion.get('description', '')}")
            if criterion.get("reality_notes"):
                lines.append(f"Reality Notes: {criterion['reality_notes']}")
            if criterion.get("condition"):
                lines.append(f"Condition: {criterion['condition']}")
                lines.append(
                    f"Condition Met (from action-only scoring): {criterion.get('is_condition_met', 'unknown')}"
                )
            lines.append(f"Max Points: {criterion.get('max_points', 0)}")
            lines.append(
                f"Baseline Score: {criterion.get('earned_points', 0)}/{criterion.get('max_points', 0)}"
            )
            lines.append(
                f'Baseline Justification: "{criterion.get("justification", "")}"'
            )
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _build_all_screenshot_evidence_text(
        rubric: dict,
        evidence_by_criterion: Dict[int, List[Dict]],
        total_screenshots: int,
    ) -> str:
        lines = []
        for c_idx, criterion in enumerate(rubric["items"]):
            lines.append(
                f'## Criterion {c_idx}: "{criterion.get("criterion", f"Criterion {c_idx}")}"'
            )
            analyses = evidence_by_criterion.get(c_idx, [])
            if not analyses:
                lines.append("No screenshot evidence available for this criterion.")
                lines.append("")
                continue
            for analysis in sorted(analyses, key=lambda x: x.get("screenshot_idx", 0)):
                sn = analysis.get("screenshot_idx", 0)
                lines.append(
                    f"### Screenshot {sn + 1} of {total_screenshots} Analysis:"
                )
                lines.append(
                    f"**Evidence:** {analysis.get('screenshot_evidence', 'N/A')}"
                )
                lines.append(
                    f"**Analysis:** {analysis.get('criterion_analysis', 'N/A')}"
                )
                lines.append(
                    f"**Discrepancies:** {analysis.get('discrepancies', 'N/A')}"
                )
                lines.append(
                    f"**Environment Issues Confirmed:** {analysis.get('environment_issues_confirmed', False)}"
                )
                lines.append("")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _build_scored_rubric_summary(rubric: dict) -> str:
        lines = []
        for j, item in enumerate(rubric["items"]):
            lines.append(
                f'--- Criterion {j}: "{item.get("criterion", f"Criterion {j}")}" ---'
            )
            lines.append(f"Description: {item.get('description', '')}")
            if item.get("reality_notes"):
                lines.append(f"Reality Notes: {item['reality_notes']}")
            if item.get("condition"):
                lines.append(f"Condition: {item['condition']}")
                lines.append(
                    f"Condition Met: {item.get('is_condition_met', 'unknown')}"
                )
            lines.append(f"Max Points: {item.get('max_points', 0)}")
            lines.append(
                f"Baseline Score (action-only): {item.get('earned_points', 'N/A')}/{item.get('max_points', 0)}"
            )
            lines.append(
                f"Final Score (post-image): {item.get('post_image_earned_points', 'N/A')}/{item.get('max_points', 0)}"
            )
            lines.append(
                f'Final Justification: "{item.get("post_image_justification", "N/A")}"'
            )
            if item.get("penalty"):
                lines.append("[PENALTY CRITERION]")
            lines.append("")
        lines.append(
            f"Total: {rubric.get('total_earned_points', 'N/A')}/{rubric.get('total_max_points', 'N/A')}"
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Image encoding helper
    # ------------------------------------------------------------------
    @staticmethod
    def _encode_image(image: Image.Image) -> str:
        import base64

        if image.mode == "RGBA":
            image = image.convert("RGB")
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    # ------------------------------------------------------------------
    # Failure-points-only pipeline
    # ------------------------------------------------------------------
    async def run_failure_points_only(self, input: dict) -> dict:
        """Run only Steps 9a, 9b, and 10 (failure analysis + task classification)
        on an existing scored rubric, skipping Steps 0–8.

        Requires that the input contains a fully scored ``precomputed_rubric``
        and that ``intermediate_mm_rubric_steps`` is available (either in the
        input dict or loaded from ``task_data.json`` on disk at the candidate
        path indicated by ``screenshots_dir``).

        Returns the rubric dict with ``first_point_of_failure``,
        ``task_verification_with_trajectory``, and ``task_verification``
        populated.
        """
        task: str = input["task"]
        action_history: str = input["action_history"]
        predicted_output: str = input.get("predicted_output", "")
        screenshots_dir: str = (
            input.get("screenshots_dir") or self.config.screenshots_dir
        )
        init_url: str = input.get("init_url", "")
        apps_list: list = input.get("apps", [])
        init_url_context = self._get_init_url_context(init_url)
        apps_str = ", ".join(apps_list) if apps_list else "N/A"

        # --- Load the scored rubric ---
        precomputed_rubric = input.get("precomputed_rubric")
        if isinstance(precomputed_rubric, list) and len(precomputed_rubric) > 0:
            precomputed_rubric = precomputed_rubric[0]
        if not precomputed_rubric or not isinstance(precomputed_rubric, dict):
            raise ValueError(
                "failure_analysis_only requires a precomputed scored rubric "
                "but none was found."
            )

        rubric_dict = precomputed_rubric
        try:
            verify_rubric(rubric_dict)
        except Exception as e:
            raise ValueError(
                f"failure_analysis_only requires a fully scored rubric, "
                f"but validation failed: {e}"
            ) from e

        # --- Load intermediate steps (for evidence and outcome) ---
        intermediate = input.get("intermediate_mm_rubric_steps")
        if intermediate is None and screenshots_dir:
            td_path = Path(screenshots_dir) / "task_data.json"
            if td_path.exists():
                with open(td_path, "r", encoding="utf-8") as f:
                    td = json.load(f)
                intermediate = td.get("intermediate_mm_rubric_steps")

        if not intermediate or not isinstance(intermediate, dict):
            raise ValueError(
                "failure_analysis_only requires intermediate_mm_rubric_steps "
                "(from a previous full evaluation) but none was found."
            )

        # Reconstruct evidence_by_criterion (keys were stringified for JSON)
        raw_evidence = intermediate.get("step4_evidence_by_criterion", {})
        evidence_by_criterion: Dict[int, List[Dict]] = {
            int(k): v for k, v in raw_evidence.items()
        }

        # Outcome result from step 8
        outcome_result = intermediate.get(
            "step8_outcome_verification",
            rubric_dict.get("outcome_verification", {}),
        )

        total_screenshots = intermediate.get("step1_num_screenshots", 0)

        # --- Step 9a: Points of failure analysis ---
        step_actions: Optional[List[Dict[str, Any]]] = input.get("step_actions")
        action_definitions = (
            input.get("action_definitions") or self.config.action_definitions
        )
        logger.info("[failure_analysis_only] Running step 9a (points of failure)...")
        step9_result = await self._first_point_of_failure_analysis(
            rubric_dict,
            evidence_by_criterion,
            task,
            init_url_context,
            action_history,
            predicted_output,
            outcome_result=outcome_result,
            total_screenshots=total_screenshots,
            action_definitions=action_definitions,
            step_actions=step_actions,
        )
        intermediate["step9_first_point_of_failure"] = step9_result
        rubric_dict["first_point_of_failure"] = step9_result

        # --- Step 9b: Trajectory-informed task verification ---
        logger.info(
            "[failure_analysis_only] Running step 9b "
            "(trajectory-informed task verification)..."
        )
        step9b_result = await self._classify_task_with_trajectory(
            rubric_dict,
            evidence_by_criterion,
            task,
            init_url_context,
            action_history,
            predicted_output,
            outcome_result=outcome_result,
            total_screenshots=total_screenshots,
            apps=apps_str,
        )
        intermediate["step9b_task_verification_with_trajectory"] = step9b_result
        rubric_dict["task_verification_with_trajectory"] = step9b_result

        # --- Step 10: Unified task verification (CHECK_VALID_TASK_PROMPT) ---
        logger.info("[failure_analysis_only] Running step 10 (task verification)...")
        step10_result = await self._classify_task(task, init_url, apps=apps_list)
        intermediate["step10_task_verification"] = step10_result
        rubric_dict["task_verification"] = step10_result

        rubric_dict["intermediate_mm_rubric_steps"] = intermediate

        logger.info(
            f"[failure_analysis_only] Done. has_failure={step9_result.get('has_failure')}, "
            f"first_failure_step={step9_result.get('first_failure_step')}"
        )
        return rubric_dict

    # ------------------------------------------------------------------
    # Main pipeline: _generate_reply
    # ------------------------------------------------------------------
    async def _generate_reply(self, input: dict) -> dict:
        """Full rubric verification pipeline.

        This is the direct port of the original _generate_reply() from
        rubric_agent_v3_mm.py, adapted to work with explicit input dict
        instead of shared_data_point.
        """
        task: str = input["task"]
        action_history: str = input["action_history"]
        predicted_output: str = input.get("predicted_output", "")
        screenshots_dir: str = (
            input.get("screenshots_dir") or self.config.screenshots_dir
        )
        actions_list: list = input["actions_list"]
        step_actions: Optional[List[Dict[str, Any]]] = input.get("step_actions")
        precomputed_rubric = input.get("precomputed_rubric")
        init_url: str = input.get("init_url", "")
        apps: list = input.get("apps", [])
        redo_eval: bool = input.get("redo_eval", self.config.redo_eval)

        init_url_context = self._get_init_url_context(init_url)
        apps_str = ", ".join(apps) if apps else "N/A"

        # ---- Handle precomputed rubric (5 scenarios) ----
        rubric_dict = None
        if isinstance(precomputed_rubric, list) and len(precomputed_rubric) > 0:
            precomputed_rubric = precomputed_rubric[0]

        if precomputed_rubric and isinstance(precomputed_rubric, dict):
            rubric_dict = precomputed_rubric

            is_scored = False
            try:
                verify_rubric(rubric_dict)
                is_scored = True
            except Exception:
                pass

            if self.config.failure_analysis_only and is_scored:
                # Rubric already scored — skip steps 0-8, run only 9+10
                logger.info(
                    "[failure_analysis_only] Scored rubric found, "
                    "skipping to steps 9-10."
                )
                return await self.run_failure_points_only(input)
            elif redo_eval and is_scored:
                rubric_dict = self._clear_rubric_scores(rubric_dict)
                try:
                    verify_generated_rubric(rubric_dict)
                except Exception:
                    rubric_dict = None
            elif is_scored and not redo_eval:
                return rubric_dict  # Early return: cached scored rubric
            elif not is_scored:
                try:
                    verify_generated_rubric(rubric_dict)
                except Exception:
                    rubric_dict = None

        if rubric_dict is None:
            rubric_dict = await self._generate_rubric(task, init_url_context)

        # ---- Action-only scoring (Step 0c) ----
        prompt = Template(ACTION_ONLY_RUBRIC_SCORER_PROMPT).substitute(
            task_definition=task,
            rubric=rubric_dict,
            action_history=action_history,
            predicted_target=predicted_output,
            init_url_context=init_url_context,
        )
        messages = [{"role": "user", "content": prompt}]

        max_iters = self.config.max_iters
        while max_iters > 0:
            try:
                response_text = await self._call_llm(
                    messages, self._o4mini_client, json_output=True
                )
                response_dict = json.loads(response_text)
                response_dict = graft_scores_onto_rubric(rubric_dict, response_dict)
                verify_rubric(response_dict)

                action_only_scores = self._compute_final_scores(
                    response_dict, "earned_points"
                )
                response_dict["total_max_points"] = action_only_scores[
                    "total_max_points"
                ]
                response_dict["total_earned_points"] = action_only_scores[
                    "total_earned_points"
                ]
                rubric_dict = response_dict
                break
            except Exception as e:
                logger.warning(f"Action-only scoring attempt failed: {e}")
                messages.append({"role": "user", "content": f"Error: {e}"})
                max_iters -= 1

        if max_iters == 0:
            return {
                "error": f"Failed to generate action-only rubric after {self.config.max_iters} attempts.",
                "total_max_points": 1,
                "total_earned_points": 0,
                "items": [],
            }

        # ---- Multimodal Pipeline ----
        if screenshots_dir is None:
            raise RuntimeError("screenshots_dir is required for rubric evaluation.")

        try:
            intermediate = {}

            # Step 1: Load screenshots
            logger.info("[Step 1/9] Loading screenshots...")
            screenshots = self._load_screenshots(screenshots_dir, actions_list)
            logger.info(f"[Step 1/9] Loaded {len(screenshots)} screenshots")
            intermediate["step1_num_screenshots"] = len(screenshots)

            # Step 2: Relevance scoring
            logger.info(
                f"[Step 2/9] Scoring relevance ({len(screenshots)} screenshots)..."
            )
            relevance_scores = await self._score_screenshot_criterion_relevance(
                screenshots, rubric_dict, task, init_url_context
            )
            # Validate: every screenshot must have scores for ALL criteria
            num_criteria = len(rubric_dict["items"])
            for sid, scores in relevance_scores.items():
                criterion_keys = {k for k in scores if k != "screenshot_idx"}
                assert len(criterion_keys) == num_criteria, (
                    f"Screenshot {sid} has {len(criterion_keys)} criterion scores but expected {num_criteria}. "
                    f"Got keys: {sorted(criterion_keys)}, expected: {list(range(num_criteria))}"
                )
                assert (
                    scores["screenshot_idx"] == sid
                ), f"screenshot_idx mismatch: dict key is {sid} but stored screenshot_idx is {scores['screenshot_idx']}"

            intermediate["step2_relevance_scores"] = {
                f"screenshot_{sid}": {str(k): v for k, v in scores.items()}
                for sid, scores in relevance_scores.items()
            }

            # Step 3: Group screenshots
            logger.info("[Step 3/9] Grouping screenshots...")
            grouped_screenshots = self._group_screenshots_by_criterion(
                relevance_scores, len(rubric_dict["items"])
            )
            intermediate["step3_grouped_screenshots"] = {
                str(k): v for k, v in grouped_screenshots.items()
            }

            if self.config.ignore_irrelevant_screenshots:
                grouped_screenshots = self._filter_irrelevant_screenshots(
                    grouped_screenshots, relevance_scores
                )

            # Step 4: Evidence analysis
            logger.info("[Step 4/9] Analyzing screenshot evidence...")
            if self.config.batch_screenshot_analysis:
                evidence_by_criterion = await self._analyze_screenshot_evidence_batched(
                    screenshots,
                    rubric_dict,
                    grouped_screenshots,
                    task,
                    init_url_context,
                    action_history,
                    predicted_output,
                    relevance_scores=relevance_scores,
                    min_relevance_threshold=self.config.min_relevance_threshold,
                )
            else:
                evidence_by_criterion = await self._analyze_screenshot_evidence(
                    screenshots,
                    rubric_dict,
                    grouped_screenshots,
                    task,
                    init_url_context,
                    action_history,
                    predicted_output,
                )
            intermediate["step4_evidence_by_criterion"] = {
                str(k): v for k, v in evidence_by_criterion.items()
            }

            # Step 4.5: Conditional criteria disambiguation
            conditional_indices = [
                i for i, c in enumerate(rubric_dict["items"]) if "condition" in c
            ]
            if len(conditional_indices) >= 2:
                logger.info(
                    f"[Step 4.5/9] Disambiguating {len(conditional_indices)} conditional criteria..."
                )
                rubric_dict = await self._disambiguate_conditional_criteria(
                    rubric_dict, evidence_by_criterion, task, init_url_context
                )
                intermediate["step4_5_disambiguation"] = {
                    str(i): {
                        "is_condition_met": rubric_dict["items"][i].get(
                            "is_condition_met"
                        ),
                        "reasoning": rubric_dict["items"][i].get(
                            "condition_disambiguation_reasoning", ""
                        ),
                    }
                    for i in conditional_indices
                }
            elif len(conditional_indices) == 1:
                c_idx = conditional_indices[0]
                verifications = [
                    a["condition_verification"]
                    for a in evidence_by_criterion.get(c_idx, [])
                    if "condition_verification" in a
                ]
                if verifications:
                    rubric_dict["items"][c_idx]["is_condition_met"] = any(verifications)

            # Step 5: Reality check
            logger.info("[Step 5/9] Running rubric reality check...")
            rubric_dict = await self._rubric_reality_check(
                rubric_dict, evidence_by_criterion, task, init_url_context
            )
            intermediate["step5_reality_check"] = {
                str(i): item.get("reality_notes", "")
                for i, item in enumerate(rubric_dict["items"])
            }

            # Steps 6-7: Majority voting
            N = self.config.majority_vote_instances
            logger.info(f"[Steps 6-7/9] Running {N} majority vote instance(s)...")

            step67_tasks = [
                self._run_steps_6_7_single_instance(
                    rubric_dict,
                    evidence_by_criterion,
                    screenshots,
                    task,
                    init_url_context,
                    action_history,
                    predicted_output,
                    instance_idx=i,
                )
                for i in range(N)
            ]
            step67_results = await asyncio.gather(*step67_tasks)

            median_idx, rubric_dict, score, median_steps = self._select_median_instance(
                step67_results
            )
            all_scores = [r[1] for r in step67_results]
            logger.info(f"[Steps 6-7/9] Scores: {all_scores}, median_idx={median_idx}")

            intermediate["step6_rescoring_summary"] = median_steps[
                "step6_rescoring_summary"
            ]
            intermediate["step7_penalty_criteria"] = median_steps[
                "step7_penalty_criteria"
            ]
            intermediate["step7_reasoning"] = median_steps["step7_reasoning"]
            intermediate["step7_requires_penalty"] = median_steps[
                "step7_requires_penalty"
            ]
            intermediate["majority_vote_steps67"] = {
                "all_scores": all_scores,
                "median_instance_idx": median_idx,
                "all_instances": [
                    {
                        "instance_idx": i,
                        "score": r[1],
                        "total_earned_points": r[0].get("total_earned_points"),
                        "total_max_points": r[0].get("total_max_points"),
                        "step6_rescoring_summary": r[2].get("step6_rescoring_summary"),
                        "step7_requires_penalty": r[2].get(
                            "step7_requires_penalty", False
                        ),
                        "step7_reasoning": r[2].get("step7_reasoning", ""),
                        "step7_penalty_criteria": r[2].get(
                            "step7_penalty_criteria", []
                        ),
                    }
                    for i, r in enumerate(step67_results)
                ],
            }

            # Step 8: Outcome verification (majority voted)
            logger.info(f"[Step 8/9] Running {N} outcome verification(s)...")
            step8_tasks = [
                self._outcome_verification(
                    rubric_dict,
                    evidence_by_criterion,
                    task,
                    init_url_context,
                    action_history,
                    predicted_output,
                    total_screenshots=len(screenshots),
                )
                for _ in range(N)
            ]
            step8_results = await asyncio.gather(*step8_tasks)

            success_votes = [r.get("output_success") for r in step8_results]
            non_none_votes = [v for v in success_votes if v is not None]
            if len(non_none_votes) >= (N // 2 + 1):
                majority_output_success = sum(non_none_votes) > len(non_none_votes) / 2
            else:
                majority_output_success = None

            majority_outcome_result = None
            for r in step8_results:
                if r.get("output_success") == majority_output_success:
                    majority_outcome_result = r
                    break
            if majority_outcome_result is None:
                majority_outcome_result = step8_results[0]
            majority_outcome_result = copy.deepcopy(majority_outcome_result)
            majority_outcome_result["output_success"] = majority_output_success

            intermediate["step8_outcome_verification"] = majority_outcome_result
            intermediate["majority_vote_step8"] = {
                "all_votes": success_votes,
                "majority_output_success": majority_output_success,
                "all_results": step8_results,
            }
            rubric_dict["outcome_verification"] = majority_outcome_result

            # Step 9a: Points of failure analysis
            cached_step9 = (
                precomputed_rubric.get("first_point_of_failure")
                if isinstance(precomputed_rubric, dict)
                else None
            )
            if cached_step9 and not redo_eval:
                logger.info("[Step 9a/9] Reusing cached points of failure analysis.")
                step9_result = cached_step9
            else:
                logger.info("[Step 9a/9] Running points of failure analysis...")
                step9_result = await self._first_point_of_failure_analysis(
                    rubric_dict,
                    evidence_by_criterion,
                    task,
                    init_url_context,
                    action_history,
                    predicted_output,
                    outcome_result=majority_outcome_result,
                    total_screenshots=len(screenshots),
                    action_definitions=self.config.action_definitions,
                    step_actions=step_actions,
                )
            intermediate["step9_first_point_of_failure"] = step9_result
            rubric_dict["first_point_of_failure"] = step9_result

            # Step 9b: Trajectory-informed task verification
            cached_step9b = (
                precomputed_rubric.get("task_verification_with_trajectory")
                if isinstance(precomputed_rubric, dict)
                else None
            )
            if cached_step9b and not redo_eval:
                logger.info(
                    "[Step 9b] Reusing cached trajectory-informed " "task verification."
                )
                step9b_result = cached_step9b
            else:
                logger.info(
                    "[Step 9b] Running trajectory-informed " "task verification..."
                )
                step9b_result = await self._classify_task_with_trajectory(
                    rubric_dict,
                    evidence_by_criterion,
                    task,
                    init_url_context,
                    action_history,
                    predicted_output,
                    outcome_result=majority_outcome_result,
                    total_screenshots=len(screenshots),
                    apps=apps_str,
                )
            intermediate["step9b_task_verification_with_trajectory"] = step9b_result
            rubric_dict["task_verification_with_trajectory"] = step9b_result

            # Step 10: Unified task verification (CHECK_VALID_TASK_PROMPT)
            cached_step10 = (
                precomputed_rubric.get("task_verification")
                if isinstance(precomputed_rubric, dict)
                else None
            )
            if cached_step10 and not redo_eval:
                logger.info("[Step 10] Reusing cached task verification.")
                step10_result = cached_step10
            else:
                logger.info("[Step 10] Running task verification...")
                step10_result = await self._classify_task(task, init_url, apps=apps)
            intermediate["step10_task_verification"] = step10_result
            rubric_dict["task_verification"] = step10_result

            # Store ALL rubric instances and scores as lists.
            # deepcopy to break circular refs: rubric_dict IS one of
            # step67_results[median_idx][0], so storing the originals
            # would make rubric_dict contain itself.
            all_rubric_dicts = [copy.deepcopy(r[0]) for r in step67_results]
            all_scores_list = [r[1] for r in step67_results]

            # Build final output (intermediate also references step67
            # result dicts, so deepcopy it too)
            rubric_dict["intermediate_mm_rubric_steps"] = copy.deepcopy(intermediate)
            rubric_dict["majority_vote_metadata"] = {
                "n_instances": N,
                "median_instance_idx": median_idx,
                "all_scores": all_scores,
                "median_score": score,
                "outcome_votes": success_votes,
                "majority_output_success": majority_output_success,
            }
            rubric_dict["all_rubric_dicts"] = all_rubric_dicts
            rubric_dict["all_scores_list"] = all_scores_list

            return rubric_dict

        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(f"[MM Pipeline] Pipeline failed: {e}\n{tb_str}")
            raise
