# webeval

Evaluation framework for [Fara-7B](https://huggingface.co/microsoft/Fara-7B)
on agentic web benchmarks (WebVoyager, OnlineMind2Web, WebTailBench).

For installation + the full reproducibility CLI, see the repo-root
[`README.md`](../README.md). Activate the **`fara_webeval`** conda env
before running anything below.

This document focuses on a single internal contract that every
benchmark, system, and verifier reads or writes: the **trajectory** —
i.e. the on-disk record of one agent run on one task.

## Trajectory format

Every executed task lives in its own directory under
`<out_url>/runs/<system.hash>/<model_prefix>/<user>/<benchmark.exec_hash>/<run_id>/traj/<task_id>/`,
e.g.:

```
/path/to/Fara/eval/runs/WebSurfer-fara-100-max_n_images-3/
  fara-7b/<user>/WebTailBench_hf/<run_id>/traj/<task_id>/
    web_surfer.log                 # newline-delimited JSON action+observation log
    <task_id>_final_answer.json    # FinalAnswer dump (final_answer, screenshots, token_usage)
    screenshot_1.png ... screenshot_N.png
    times.json                     # {start_time, end_time, duration} of the solver run
    core.log                       # webeval.core per-task log (Execution / Evaluation lifecycle)
    task_data.json                 # only present after the rubric verifier runs (see below)
    scores/
      <benchmark.eval_hash>.json   # {score: float, gpt_response_text: str|json}
```

A concrete example is checked in at
[`webeval/data/example_trajectory/`](data/example_trajectory/) — a
single WebTailBench AllTrails task (`alltrails_find_23`) with its
`web_surfer.log`, `alltrails_find_23_final_answer.json`,
`screenshot_{1..4}.png` frames, `times.json`, `core.log`,
`task_data.json` (written by the rubric verifier on re-eval), and the
`scores/mmrubric_0.8-5-3.json` rubric verdict (`score=1`). Point
`Trajectory.from_folder(...)` at that dir to see every field below
populated end-to-end.

### `web_surfer.log` (one JSON object per line)

Written by the `LogHandler` in `webeval/utils.py`, attached to the
`WebSurferLogger` inside `WebSurferSystem.get_answer()`. The handler
runs at `DEBUG` level so the `FaraAgent.{generate_model_call,
execute_action}` methods (`src/fara/fara_agent.py`) — which emit at
`logger.debug(...)` — actually flow through. Every line carries a
top-level `type` field (`LogHandler.emit` in `webeval/utils.py:124`).
In the current `FaraAgent` pipeline only two of them are actually
produced:

| `type`           | Source                                          | Key fields |
|------------------|-------------------------------------------------|---|
| `WebSurferEvent` | `FaraAgent.execute_action` (`src/fara/fara_agent.py:467`) | `timestamp`, `source`, `message`, `url`, `action`, `arguments`. The structured action event — one per tool call, with `action=<tool>` and `arguments=<dict>`. |
| `OtherEvent`     | `FaraAgent`'s raw `logger.debug(...)` strings (`fara_agent.py:403,415`) | `timestamp`, `type`, `message`. The `Thought #N: ...\nAction #N: executing tool '<tool>' with arguments {...}` and `Observation#N: ...` prints land here, because they're plain strings, not dataclasses, and `LogHandler.emit` falls through to its catch-all branch. |

Three more event dataclasses (`OrchestrationEvent`, `AgentEvent`,
`LLMCallEvent`) are declared in `webeval/systems/messages.py` /
`webeval/utils.py` and handled by `LogHandler.emit`, but have no
construction callsites in the current repo — they're reserved for
other solver systems / legacy trajectories and won't appear in a
fresh `FaraAgent` run.

`Trajectory.__init__` reads every line and either:

1. Uses each event's top-level `action` field directly (the
   `WebSurferEvent` shape), OR
2. If no event has an `action` field (the all-`OtherEvent` case), runs
   `parse_text_based_event` to extract `action` + `arguments` (with
   `thoughts`) from the `Thought #N: ... Action #N: executing tool …`
   text. This is how trajectories from older `WebSurferSystem` runs
   are recovered.

After parsing, `Trajectory.actions` is a list of JSON-encoded action
arg dicts (with `thoughts` stripped) and `Trajectory.thoughts` is the
parallel list of thought strings.

> **Gotcha**: if `web_surfer.log` is empty, `Trajectory.events == []`
> and `Trajectory.actions == []`. Downstream evaluators (e.g.
> `WebTailBenchBenchmark.evaluator`) treat that as
> `verifier_reasoning="No actions found in the trajectory"` and return
> score 0 **without** invoking MMRubricAgent. The fix is in
> `WebSurferSystem.get_answer()`, which now bumps the logger to `DEBUG`
> before the `FaraAgent` runs.

### `<task_id>_final_answer.json` (`FinalAnswer` dataclass)

Written by `WebSurferSystem.get_answer()` once the agent terminates or
hits `max_rounds`. Field reference (`webeval/trajectory.py:FinalAnswer`):

| Field            | Type                       | Notes |
|------------------|----------------------------|---|
| `final_answer`   | `str`                      | The agent's final response text. Defaults to `"<no_answer>"` — see the next section for what that means. |
| `env_state_json` | `str` (JSON)               | Parsed JSON dump of the final webpage `<pre>` element at `/finish` (synthetic envs only). |
| `env_state_raw`  | `str`                      | Raw text from that `<pre>` element (debugging / fallback if `env_state_json` parse failed). |
| `screenshots`    | `List[str]`                | Screenshot filenames captured during the run, **relative** to the trajectory dir if `is_rel_paths` is true (the default), else absolute. |
| `is_aborted`     | `bool`                     | True if the trajectory was killed mid-execution by an environment error. Aborted trajectories are typically retried up to `--max_error_task_retries` (see `webeval/core.py`). |
| `is_rel_paths`   | `bool`                     | Whether `screenshots` paths are relative to `trajectory.path`. New runs use `True`. |
| `token_usage`    | `Dict[str, RequestUsage]`  | Per-component LLM token usage. The example uses `{"FaraAgent": {"prompt_tokens": 23383, "completion_tokens": 1920}}` — the key is whichever component name `WebSurferSystem.get_answer()` attributes the call to. Aggregated via `RequestUsage.__add__`. |

Persisted via `FinalAnswer.save(path)`; loaded via `FinalAnswer.load(path)`.
`Trajectory.__init__` calls `FinalAnswer.load(...)` on the single
`*_final_answer.json` it finds in the dir (raises `ValueError` if 0
or >1 are present), reattaches the loaded `FinalAnswer` as
`trajectory.answer`, and exposes the screenshot list directly as
`trajectory.screenshots`. `trajectory.is_aborted` is just a
pass-through to `trajectory.answer.is_aborted`.

#### `final_answer == "<no_answer>"` is the load-bearing flag

`FinalAnswer` is constructed with `final_answer = "<no_answer>"` as the
default, and `WebSurferSystem.get_answer()` only **overwrites it with
the agent's actual answer string when the agent calls `terminate(...)`
within `--max_rounds` steps**. Three trajectory outcomes therefore look
different on disk:

| Outcome                                    | `is_aborted` | `final_answer`        | Notes |
|--------------------------------------------|--------------|-----------------------|---|
| Agent called `terminate(...)` within budget| `False`      | the model's response  | Only this case has a real string to score. |
| Agent never called `terminate`, hit `--max_rounds` | `False` | `"<no_answer>"`       | Trajectory ran to completion-by-cutoff; downstream is free to score the final state but the model itself produced no answer. |
| Run errored mid-execution (browser crash, timeout, …) | `True`  | `"<no_answer>"`       | Will be retried up to `--max_error_task_retries` (`webeval/core.py:run_eval_single_example`); only the final attempt's `_final_answer.json` is kept. |

**Filtering "actually completed" runs**: anywhere you want trajectories
that finished within step budget AND produced a real model answer, the
canonical check is

```python
candidate.answer.final_answer != "<no_answer>" and not candidate.is_aborted
```

This is what `webeval/post_eval_analysis.py` uses when computing
"average score across non-aborted, non-step-budget-exceeded
trajectories", and it's also why `WebTailBenchBenchmark.evaluator`
short-circuits with `verifier_reasoning='The last action must be
"terminate"'` for any trajectory whose last logged action is not
`terminate` — those are guaranteed to have `final_answer ==
"<no_answer>"` and therefore nothing the rubric judge can grade.

> **Auto-0 vs excluded**: two superficially similar cases are scored
> very differently.
>
> - **Over-budget** (`<no_answer>`, `is_aborted=False`): WebTailBench
>   short-circuits to `score=0` without calling the rubric judge,
>   writes it to `scores/<eval_hash>.json`, and **counts it as 0 in
>   the mean**.
> - **Aborted / errored mid-run** (`is_aborted=True`, loader fails,
>   or evaluator raises): returns `score=None`, no score file is
>   written, and every aggregator filters on `score is not None` —
>   so aborted trajectories are **excluded from all final metrics**
>   rather than counted as 0.

`screenshot_{i}.png` files keep accumulating regardless of how the
trajectory ended, so screenshot count alone is **not** a proxy for
"in budget" — always combine it with the `final_answer` check above.
Note: `trajectory.latest_screenshot` is a static convenience path
(`trajectory.path / "screenshot_scaled.png"`, see
`webeval/trajectory.py:131`) that may not exist on disk for every
run — the example directory, for instance, has only
`screenshot_1..4.png`.

### `times.json`

`{"start_time": <unix-float>, "end_time": <unix-float>, "duration":
<float-seconds>}`, written around the solver call in
`webeval/core.py:run_single_task` (`webeval/core.py:86-93`). Both
stamps are `time.time()` values (not ISO-8601); e.g. the example is
`{"start_time": 1762809276.0520103, "end_time": 1762809454.79363,
"duration": 178.74161958694458}`. `evaluate_single_example` reads
`duration` to populate `EvalResult.duration`.

### `scores/<benchmark.eval_hash>.json`

Written by `webeval/core.py:evaluate_single_example` after a successful
`Benchmark.evaluate_example()` call. Single writer, single shape across
all benchmarks (top-level `{score, gpt_response_text}`); the
benchmark-specific verdict lives inside `gpt_response_text`.

| Field               | Type             | Notes |
|---------------------|------------------|---|
| `score`             | `float` or `int` | Top-line success metric (0/1 for outcome-style judges; fraction for rubric-style judges). |
| `gpt_response_text` | `str` (often a JSON-encoded dict) | Free-form judge output. See per-benchmark table below. |

#### Where each benchmark's verdict lives

The score file is the **single source of truth for an evaluation
result**. `final_answer.json` is never overwritten by the verifier.
`task_data.json` is a separate dump the WebTailBench rubric verifier
writes alongside the score file (`benchmarks/webtailbench.py:346` →
`[Rubric] Saved rubric results to …/task_data.json`), so a fresh
solver-only run won't have one, but any trajectory that's been
re-scored — including the checked-in example — will. Re-running the
verifier (`--redo_eval` or `scripts/verify_trajectories.py`) rewrites
the score file in place and, for webtailbench, refreshes
`task_data.json` with the latest rubric payload.

| Benchmark | Score file path under `traj/<task_id>/` | `gpt_response_text` payload |
|---|---|---|
| `webvoyager` | `scores/gpt_eval.json` | gpt-4o judge text — verdict is `"SUCCESS"` / `"NOT SUCCESS"` parsed back to `score ∈ {0.0, 1.0}` (`benchmarks/webvoyager/webvoyager.py`). |
| `om2w` | `scores/<eval_method>-<threshold>.json` (e.g. `WebJudge_Online_Mind2Web_eval-3.json`) | o4-mini judge text — verdict via `extract_predication(...)` from the OnlineMind2Web judge methods (`benchmarks/om2w/om2w.py`). |
| `webtailbench` | `scores/mmrubric_<rubric_threshold>-<max_imgs>-<keypt>.json` | JSON-encoded dict assembled in `benchmarks/webtailbench/webtailbench.py:355-442`: `is_success` (int 0/1), `success_criterion` (`outcome` / `process` / `both`), `final_answer`, `outcome_success` (bool), `outcome_reasoning`, `outcome_primary_intent`, `rubric_is_success` (int), the `rubric_*` family forwarded from MMRubricAgent (`rubric_items`, `rubric_total_earned_points`, `rubric_total_max_points`, `rubric_all_scores_list`, `rubric_all_rubric_dicts`, `rubric_intermediate_mm_rubric_steps`, `rubric_outcome_verification`, `rubric_majority_vote_metadata`), and the error-taxonomy fields nested inside the rubric payload (`first_point_of_failure`, `is_ambiguous` / `ambiguity_codes`, `is_invalid` / `invalid_task_codes` — `mm_rubric_agent.py:392-406`). Top-level `score` equals `is_success`, which is driven by `--success`: `outcome` → `int(outcome_success)`, `process` → `rubric_is_success`, `both` → both. |
| `verify_trajectories.py` (stand-alone) | same path + shape as `webtailbench` | same Universal Verifier output. |

### `core.log`

Per-task log lines from the `webeval.core.<task_id>` logger. Useful
when a task hangs or errors and the rest of the pipeline keeps
moving. A run's `core.log` typically mixes:

- `[Execution <task_id>] Start / Trajectory is not complete. Reexecuting... / Completed / Error`
- BrowserBase plumbing: `Initializing BrowserBase session...`,
  `Connected to BrowserBase session: <url>`, `Closing browser...`
- Every `WebSurferEvent` event re-emitted as its dataclass
  `repr(...)` (so the same step shows up both here and in
  `web_surfer.log`, just unparsed)
- `[Evaluation <task_id>] Start / Loading from: <path> / Completed: score=<n>, duration=<seconds> / Error`
- `[Rubric] Saved rubric results to <path>/task_data.json` when the
  WebTailBench rubric verifier runs

The example's `core.log` shows the full sequence for one solve on
2025-11-10 plus three separate rubric re-eval passes on 2026-03-26,
all against the same trajectory directory.

### `task_data.json` (optional, rubric-verifier output)

Only written by the WebTailBench rubric verifier
(`benchmarks/webtailbench/webtailbench.py:346`), so trajectories that
have never been re-scored won't have one. When present, it's a large
JSON dump of the task's rubric/outcome state — everything MMRubricAgent
produced plus the task metadata it loaded. In the example,
`task_data.json` has 76 keys, including `task_summary`, `task_type`,
`rubric_score`, `verifier_agent_response`, `verifier_rubric`,
`start_timestamp`, `end_timestamp`, `token_usage`, `plan_list`,
`facts_list`, `observations_list`, `actions`, `actions_summary`, and
the boolean error-taxonomy flags (`did_web_surfing_fail`,
`web_surfing_stalled`, `encountered_captcha`, …). Treat this file as
diagnostic detail; the authoritative score still lives in
`scores/<eval_hash>.json`.

## `Trajectory` consumers

```python
from webeval.trajectory import Trajectory
traj = Trajectory.from_folder("/path/to/<task_id>/")
# Returns None if the dir is missing the answer file or the log can't be parsed.
traj.events                # list[dict] of parsed action/observation events
traj.actions               # list[str]  of JSON-encoded action-arg dicts
traj.thoughts              # list[str]  parallel to .actions
traj.screenshots           # list[Path] absolute paths to screenshot files
traj.answer                # FinalAnswer
traj.is_aborted            # bool (delegates to .answer.is_aborted)
traj.latest_screenshot     # convenience: trajectory.path / "screenshot_scaled.png"
```

Three places consume it today:

1. **Benchmark verifiers** (`webeval/benchmarks/*/<bench>.py`): each
   benchmark's `evaluator(task_data, candidate)` receives a
   `Trajectory` and returns `(score, gpt_response_text)`. WebTailBench
   wraps `MMRubricAgent` (the Universal Verifier) for this; webvoyager
   / om2w call their own GPT judges.
2. **`webeval/scripts/verify_trajectories.py`**: stand-alone parallel
   runner that points `MMRubricAgent` at any directory of
   `Trajectory`-shaped folders and writes per-task
   `scores/mmrubric_<…>.json`. Useful for re-scoring an existing
   eval run with new judge parameters.
3. **`webeval/post_eval_analysis.py`**: aggregates
   `_final_answer.json` + `scores/<…>.json` + counts of
   `WebSurferEvent` lines in `web_surfer.log` for run-level reporting.

## Where each file is written

| File                              | Writer                                                                                    |
|-----------------------------------|-------------------------------------------------------------------------------------------|
| `web_surfer.log`                  | `LogHandler` attached in `WebSurferSystem.get_answer()` (capturing `FaraAgent` log calls) |
| `<task_id>_final_answer.json`     | `WebSurferSystem.get_answer()` → `FinalAnswer.save()`                                     |
| `screenshot{i}.png`               | `FaraAgent.execute_action` (browser screenshots; one per action by default)               |
| `times.json`                      | `webeval/core.py:run_single_task`                                                         |
| `core.log`                        | `_logger = logger.getChild(task_id)` in `webeval/core.py:run_eval_single_example`         |
| `scores/<benchmark.eval_hash>.json` | `webeval/core.py:evaluate_single_example`                                                 |
| `scores/mmrubric_<…>.json`        | `webeval/scripts/verify_trajectories.py`                                                  |
