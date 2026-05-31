import json
import logging
import os
import time
from io import BytesIO
from typing import Any, Dict, List, Optional, Set, Tuple

from PIL import Image

from mm_agents import _mm_skill_base as v2mod


MAX_SKILL_CONSULTS_PER_SKILL = 2
ARCHITECTURE_VERSION = "mm_skill_planner_branch"


class _MMSkillPlannerAgent(v2mod._MMSkillBaseAgent):
    """
    Planner-oriented MMSkills agent.

    Compared with v2:
    - Skill branches are planners, not step executors.
    - A LOAD_SKILL call does not consume an interaction step.
    - Branches return structured planner summaries, and the main agent remains
      responsible for grounded GUI actions.
    - The main trajectory keeps an active skill state plus per-skill consult counts
      to reduce repeated same-skill loops.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._skill_consult_counts: Dict[str, int] = {}
        self._active_skill_state: Optional[Dict[str, Any]] = None
        self._current_step_planner_summaries: List[Dict[str, Any]] = []

    def _runtime_logger(self):
        return v2mod.base_agent_mod.logger if v2mod.base_agent_mod.logger is not None else logging.getLogger(
            "desktopenv.mm_skill.planner"
        )

    def _empty_skill_usage_summary(self) -> Dict[str, object]:
        payload = super()._empty_skill_usage_summary()
        payload.update(
            {
                "architecture_version": ARCHITECTURE_VERSION,
                "max_skill_consults_per_skill": MAX_SKILL_CONSULTS_PER_SKILL,
                "skill_consult_counts": {},
                "active_skill_state": None,
            }
        )
        return payload

    def reset(self, _logger=None, vm_ip=None, **kwargs):
        runtime_logger = _logger if _logger is not None else logging.getLogger("desktopenv.mm_skill.planner")
        super().reset(_logger=runtime_logger, vm_ip=vm_ip, **kwargs)
        self._skill_consult_counts = {}
        self._active_skill_state = None
        self._current_step_planner_summaries = []
        self._skill_usage_summary = self._empty_skill_usage_summary()

    def _skills_with_consult_counts_text(self) -> str:
        if not self._task_skill_names:
            return "None"
        lines = []
        meta_map = {v2mod.Path(meta.directory).name: meta for meta in self._task_skill_metadatas}
        for skill_name in self._task_skill_names:
            meta = meta_map.get(skill_name)
            description = ((meta.description or "").strip() if meta is not None else "") or "(no description)"
            count = self._skill_consult_counts.get(skill_name, 0)
            lines.append(f"- {skill_name} — {description} [consulted {count}/{MAX_SKILL_CONSULTS_PER_SKILL}]")
        return "\n".join(lines)

    def _active_skill_state_text(self) -> str:
        state = self._active_skill_state
        if not state:
            return "None"
        return "\n".join(
            [
                f"- Skill: {state.get('skill_name', 'Unknown')}",
                f"- Applicability: {state.get('skill_applicability', 'unknown')}",
                f"- Plan: {state.get('plan', 'None')}",
                f"- Expected state: {state.get('expected_state', 'None')}",
                f"- Completion scope: {state.get('completion_scope', 'needs_verification')}",
                f"- Last consulted at step: {state.get('last_consult_step', 'unknown')}",
                f"- Consult count: {state.get('consult_count', 0)}/{MAX_SKILL_CONSULTS_PER_SKILL}",
            ]
        )

    def _current_step_planner_summaries_text(self) -> str:
        if not self._current_step_planner_summaries:
            return "None"
        chunks = []
        for idx, item in enumerate(self._current_step_planner_summaries, start=1):
            chunks.append(
                "\n".join(
                    [
                        f"Planner note {idx}:",
                        f"- Skill: {item.get('skill_name', 'Unknown')}",
                        f"- Applicability: {item.get('skill_applicability', 'unknown')}",
                        f"- Subgoal: {item.get('subgoal', 'None')}",
                        f"- Plan: {item.get('plan', 'None')}",
                        f"- Expected state: {item.get('expected_state', 'None')}",
                        f"- Completion scope: {item.get('completion_scope', 'needs_verification')}",
                        f"- Consult count: {item.get('consult_count', 0)}/{MAX_SKILL_CONSULTS_PER_SKILL}",
                    ]
                )
            )
        return "\n\n".join(chunks)

    def _planner_summary_to_record(self, skill_name: str, summary: Dict[str, str]) -> Dict[str, Any]:
        return {
            "skill_name": skill_name,
            "skill_applicability": summary["skill_applicability"],
            "subgoal": summary["subgoal"],
            "plan": summary["plan"],
            "expected_state": summary["expected_state"],
            "completion_scope": summary["completion_scope"],
            "consult_count": self._skill_consult_counts.get(skill_name, 0),
        }

    def _upsert_current_step_planner_summary(self, planner_note: Dict[str, Any]) -> None:
        for idx, existing in enumerate(self._current_step_planner_summaries):
            if existing.get("skill_name") == planner_note.get("skill_name"):
                self._current_step_planner_summaries[idx] = planner_note
                return
        self._current_step_planner_summaries.append(planner_note)

    def _update_active_skill_state(self, planner_note: Dict[str, Any]) -> None:
        applicability = planner_note.get("skill_applicability")
        if applicability == "ineffective":
            active_skill_name = self._active_skill_state.get("skill_name") if self._active_skill_state else None
            if active_skill_name == planner_note.get("skill_name"):
                self._active_skill_state = None
            return
        self._active_skill_state = {
            "skill_name": planner_note.get("skill_name"),
            "skill_applicability": planner_note.get("skill_applicability"),
            "plan": planner_note.get("plan"),
            "expected_state": planner_note.get("expected_state"),
            "completion_scope": planner_note.get("completion_scope"),
            "consult_count": planner_note.get("consult_count", 0),
            "last_consult_step": len(self.actions) + 1,
        }

    def _extract_planner_summary(self, response: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        if self._count_code_blocks(response) != 1:
            return None, (
                "The branch response must contain exactly one code block with a JSON object containing "
                "`skill_applicability`, `subgoal`, `plan`, `expected_state`, and `completion_scope`."
            )
        code_body = self._extract_first_code_block_text(response)
        if not code_body:
            return None, "The branch response code block was empty."
        try:
            payload = json.loads(code_body)
        except Exception as exc:
            return None, f"The branch response must be valid JSON. Parse error: {exc}"
        if not isinstance(payload, dict):
            return None, "The branch response JSON must be an object."

        applicability = str(payload.get("skill_applicability", "")).strip().lower()
        if applicability not in {"effective", "ineffective", "uncertain"}:
            return None, "The `skill_applicability` field must be one of: effective, ineffective, uncertain."

        subgoal = str(payload.get("subgoal", "")).strip()
        plan = str(payload.get("plan", "")).strip()
        expected_state = str(payload.get("expected_state", "")).strip()
        completion_scope = str(payload.get("completion_scope", "")).strip().lower()
        if not subgoal:
            return None, "The `subgoal` field must be a non-empty string."
        if not plan:
            return None, "The `plan` field must be a non-empty string."
        if not expected_state:
            return None, "The `expected_state` field must be a non-empty string."
        if completion_scope not in {"local_only", "needs_verification", "maybe_complete"}:
            return None, (
                "The `completion_scope` field must be one of: "
                "local_only, needs_verification, maybe_complete."
            )

        return {
            "skill_applicability": applicability,
            "subgoal": subgoal,
            "plan": plan,
            "expected_state": expected_state,
            "completion_scope": completion_scope,
        }, None

    def _build_planner_augmented_history_response(
        self,
        planner_notes: List[Dict[str, Any]],
        main_response: str,
        actions: List[str],
    ) -> str:
        code_body = self._extract_first_code_block_text(main_response)
        if code_body is None:
            code_body = "\n".join(actions) if actions else (main_response.strip() or "FAIL")

        code_lines = [line.rstrip() for line in code_body.splitlines()]
        header_lines = [
            "# One or more skill planners were consulted in this same interaction step.",
            "# The concrete action below was chosen by the main agent from the CURRENT screenshot and previous steps.",
        ]
        for note in planner_notes:
            header_lines.extend(
                [
                    f"# Consulted planner skill: {note.get('skill_name', 'Unknown')}",
                    f"# Skill applicability: {note.get('skill_applicability', 'unknown')}",
                    f"# Planner subgoal: {note.get('subgoal', 'None')}",
                    f"# Planner summary: {note.get('plan', 'None')}",
                    f"# Expected state: {note.get('expected_state', 'None')}",
                    f"# Completion scope: {note.get('completion_scope', 'needs_verification')}",
                    f"# Skill consult count: {note.get('consult_count', 0)}/{MAX_SKILL_CONSULTS_PER_SKILL}",
                ]
            )

        return f"```python\n{chr(10).join(header_lines + code_lines)}\n```"

    def _build_main_system_message(self, instruction: str) -> str:
        available_skills = self._available_skills_text()
        return f"""
Follow the instruction to perform desktop computer tasks.
You control the computer using Python code with `pyautogui`.

For each step, you will receive the current screenshot and the recent visible trajectory history.
Use the screenshot to decide the next action. Do not assume that previous clicks succeeded.
If an earlier action failed, adjust based on the CURRENT screenshot instead of repeating the same guess.

Task skills are optional procedural planners only.
- Call `LOAD_SKILL("<exact_skill_name>")` only when the CURRENT screenshot and previous steps are not enough.
- `LOAD_SKILL(...)` opens a temporary planner branch. It does NOT execute the action for you.
- The branch returns structured planner information: skill applicability, subgoal, plan, expected state, and completion scope.
- `LOAD_SKILL(...)` does not consume an interaction step. After the planner summary returns, you must still choose the concrete grounded GUI action in the same step.
- Skill text and images are knowledge/state references only, never coordinate templates.
- Trust the CURRENT screenshot over any skill when they conflict.
- Each skill may be consulted at most {MAX_SKILL_CONSULTS_PER_SKILL} times in the same trajectory.

Available skills for this task:
{available_skills}

Important rules:
- Use `pyautogui` only for GUI actions.
- Do NOT use `pyautogui.locateCenterOnScreen`.
- Do NOT use `pyautogui.screenshot()`.
- Each response must be self-contained; do not rely on variables from previous steps.
- When a click does not work, revise the target based on the new screenshot.
- Prefer short, direct grounded actions over long speculative scripts.
- Strictly avoid repetitive, unproductive action loops.
- Before outputting `DONE`, verify that the FULL user instruction has been completed, not just a local subgoal. If needed, do one verification action first.

Output format:
- Return ONLY one code block.
- The code block must contain exactly one of the following:
  1. Python code using `pyautogui`
  2. `WAIT`
  3. `DONE`
  4. `FAIL`
  5. `LOAD_SKILL("<exact_skill_name>")`
- Do not return prose outside the code block.
- Do not return Python code and `LOAD_SKILL(...)` in the same response.
- Do not load more than one skill in a single response.
- Use only the exact skill names listed above when calling `LOAD_SKILL(...)`.
- If you return Python code, include concise `#` comments that explain the purpose of the step or sub-step.

Correct skill request example:
```python
LOAD_SKILL("Example_Skill_Name")
```

Correct Python action example:
```python
# Open the relevant menu so I can continue the task from the current state.
pyautogui.click(120, 54)
```

Special codes:
- ```WAIT``` when the UI is still loading.
- ```DONE``` only when the full task has been verified as complete.
- ```FAIL``` only when the task is truly impossible.

Coordinate system:
- When the prompt says the screen resolution is 1000x1000, use that normalized coordinate space in your `pyautogui` calls.
- When the prompt says the screen resolution is WxH, use that exact resolution.

The computer password is '{self.client_password}', use it when needed.
You are asked to complete the following task: {instruction}
""".strip()

    def _build_main_user_text(
        self,
        instruction: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        extra_feedback: Optional[List[str]] = None,
    ) -> str:
        previous_steps = self._build_previous_steps_text()
        active_memo_text = self._active_skill_state_text()
        active_skill_name = self._active_skill_state.get("skill_name") if self._active_skill_state else None
        current_step_skills = {item.get("skill_name") for item in self._current_step_planner_summaries}
        if active_skill_name and active_skill_name in current_step_skills:
            active_memo_text = "Covered by the planner notes returned in this step."
        text_sections = [
            "Please generate the next grounded GUI action from the CURRENT screenshot.",
            f"Instruction: {instruction}",
            "Skills:\n" + self._skills_with_consult_counts_text(),
            "Active planner memo:\n" + active_memo_text,
            "Planner notes returned in this step:\n"
            + self._current_step_planner_summaries_text(),
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Ground every action in the CURRENT screenshot.\n"
            "- Treat skills and skill images as state guidance, never as coordinate templates.\n"
            f"- Do not reload a skill after {MAX_SKILL_CONSULTS_PER_SKILL} consults.\n"
            "- If planner notes already exist for this step, use them before consulting again.\n"
            "- If recent actions repeated without progress, change strategy.\n"
            "- Before DONE, verify the full instruction, not just a local subgoal.\n"
            "- If you return Python, include concise `#` comments.",
        ]
        if extra_feedback:
            feedback_lines = "\n".join(f"- {item}" for item in extra_feedback if item)
            if feedback_lines:
                text_sections.insert(4, "Feedback for this step:\n" + feedback_lines)

        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text_sections.append("Loop warning:\n" + repetition_warning)
        return "\n\n".join(text_sections)

    def _skill_parts_for_mode(self, skill_name: str, full_skill: Dict) -> List[dict]:
        content = full_skill["content"]
        parts: List[dict] = [
            {
                "text": (
                    f"# Branch Skill Reference: {content.name} ({skill_name})\n\n"
                    "Treat the material below as supplemental procedural knowledge only.\n"
                    "Use it to understand workflow stages, state cues, likely subgoals, and success/failure signals.\n"
                    "Do NOT treat the text or images as coordinate templates.\n"
                    "The CURRENT screenshot remains authoritative for concrete GUI actions.\n\n"
                    f"{content.text}"
                )
            }
        ]
        if self.skill_mode == "multimodal":
            for filename, b64_data, mime_type in full_skill.get("images", []):
                parts.append(
                    {
                        "text": (
                            f"[Branch Skill Visual State Reference - {skill_name}/{filename}] "
                            "Use this to recognize dialog/state cues, not to copy coordinates."
                        )
                    }
                )
                parts.append({"inlineData": {"mimeType": mime_type, "data": b64_data}})
        return parts

    def _build_branch_reference_content(
        self,
        trigger_skill_name: str,
        main_trigger_response: str,
        branch_skill_payloads: List[Tuple[str, Dict]],
    ) -> dict:
        loaded_skill_names = ", ".join(skill_name for skill_name, _ in branch_skill_payloads) or "None"
        parts: List[dict] = [
            {
                "text": "\n\n".join(
                    [
                        "Skill reference package for this temporary planner branch.",
                        "The materials below are supplemental procedural references only.",
                        f"Requested skill in the main context: LOAD_SKILL(\"{trigger_skill_name}\")",
                        f"Loaded skills in this branch: {loaded_skill_names}",
                        "The main agent, not this branch, will choose the concrete action.",
                        "Use the skill materials to judge applicability, subgoal, plan, expected state, and completion scope.",
                        "Treat images as state references, not coordinate templates.",
                    ]
                )
            }
        ]
        for skill_name, full_skill in branch_skill_payloads:
            parts.extend(self._skill_parts_for_mode(skill_name, full_skill))
        return {"role": "user", "parts": parts}

    def _build_branch_system_message(self, instruction: str, loaded_skill_names: List[str]) -> str:
        loaded_skills = ", ".join(loaded_skill_names) if loaded_skill_names else "None"
        return f"""
You are inside a temporary planner-only skill consultation branch for a single desktop step.
Your job is NOT to return a GUI action. Your job is to summarize whether the loaded skill is useful for the CURRENT state and what the main agent should optimize for next.

Branch rules:
- Do not return Python code, WAIT, DONE, FAIL, or LOAD_SKILL.
- Do not request another skill in this branch.
- The main agent will choose the concrete GUI action after reading your planner summary.
- Use the current screenshot and previous steps to decide whether the skill is effective.
- If the skill is ineffective for the CURRENT state, say so clearly and instruct the main agent to rely on the CURRENT screenshot instead of skill bias.
- If the skill is effective, summarize the current subgoal, the planning guidance, the expected next visible state, and whether the task still needs verification.
- Treat any skill images as state/knowledge references, NOT as coordinate templates.
- Before implying that the task might be complete, think about whether the main agent should still do a verification action before DONE.

Currently loaded branch skills:
{loaded_skills}

Output format:
- Return ONLY one code block.
- The code block must contain exactly one JSON object with these keys:
  - `"skill_applicability"`: one of `"effective"`, `"ineffective"`, `"uncertain"`
  - `"subgoal"`: a short string
  - `"plan"`: a short string
  - `"expected_state"`: a short string describing visible screenshot cues the main agent should aim for next
  - `"completion_scope"`: one of `"local_only"`, `"needs_verification"`, `"maybe_complete"`
- Do not return prose outside the code block.

Correct example:
```json
{{
  "skill_applicability": "effective",
  "subgoal": "open the correct validation dialog for the selected range",
  "plan": "stay grounded in the current dialog flow and avoid reopening the menu if the target dialog is already visible",
  "expected_state": "The correct validation dialog is visible for the currently selected range",
  "completion_scope": "local_only"
}}
```

The computer password is '{self.client_password}', use it when needed.
You are asked to complete the following task: {instruction}
""".strip()

    def _build_branch_current_user_text(
        self,
        instruction: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        round_feedback: Optional[List[str]] = None,
    ) -> str:
        previous_steps = self._build_previous_steps_text()
        text_sections = [
            "Please inspect the CURRENT UI screenshot and return planner information only.",
            f"Instruction: {instruction}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Return planner JSON only, not an action.\n"
            "- Treat skill text and images as knowledge/state references, not coordinate templates.\n"
            "- If the current screenshot conflicts with the skill, trust the current screenshot.\n"
            "- `expected_state` must describe visible screenshot cues, not an abstract goal.\n"
            "- Use `completion_scope` to indicate whether the task is only locally advanced or still needs verification before DONE.",
        ]
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text_sections.append("Loop warning:\n" + repetition_warning)
        if round_feedback:
            feedback_lines = "\n".join(f"- {item}" for item in round_feedback if item)
            if feedback_lines:
                text_sections.append("Additional feedback for this branch round:\n" + feedback_lines)
        return "\n\n".join(text_sections)

    def _load_skill_for_branch(
        self,
        skill_name: str,
        branch_loaded_names: Set[str],
    ) -> Tuple[Optional[Dict], int, Optional[str]]:
        self._skill_usage_summary["load_skill_calls"] = int(self._skill_usage_summary.get("load_skill_calls", 0)) + 1
        if not skill_name:
            return None, 0, "Missing skill name in LOAD_SKILL(...)."
        if skill_name not in self._task_skill_names:
            return None, 0, f"Unknown skill '{skill_name}'. Use only a skill from the available skill list."
        if skill_name in branch_loaded_names:
            return None, 0, f"Skill '{skill_name}' is already loaded in this branch. Do not reload it inside the same branch."
        if self._skill_consult_counts.get(skill_name, 0) >= MAX_SKILL_CONSULTS_PER_SKILL:
            return (
                None,
                0,
                f"Skill '{skill_name}' has already been consulted {MAX_SKILL_CONSULTS_PER_SKILL} times in this trajectory. "
                "Do not load it again. Continue with grounded GUI interaction using the CURRENT screenshot and previous steps.",
            )

        full_skill = self._skill_loader.load_full_skill(skill_name)
        if not full_skill:
            return None, 0, f"Failed to load skill '{skill_name}'."

        self._skill_consult_counts[skill_name] = self._skill_consult_counts.get(skill_name, 0) + 1
        image_count = len(full_skill.get("images", [])) if self.skill_mode == "multimodal" else 0
        self._record_consulted_skill(skill_name, image_count)
        return full_skill, image_count, None

    def _save_skill_usage_summary(self):
        if not self._result_dir:
            return
        payload = dict(self._skill_usage_summary)
        payload.update(
            {
                "architecture_version": ARCHITECTURE_VERSION,
                "task_skill_names": list(self._task_skill_names),
                "loaded_skill_names": sorted(self._consulted_skills),
                "consulted_skill_names": sorted(self._consulted_skills),
                "skill_branch_invocations": len(self._skill_invocation_log),
                "skill_branch_successes": sum(1 for item in self._skill_invocation_log if item.get("success")),
                "steps_recorded": len(self.actions),
                "final_actions": list(self.actions),
                "max_skill_consults_per_skill": MAX_SKILL_CONSULTS_PER_SKILL,
                "skill_consult_counts": dict(self._skill_consult_counts),
                "active_skill_state": dict(self._active_skill_state) if self._active_skill_state else None,
            }
        )
        output_path = os.path.join(self._result_dir, "skill_usage_summary.json")
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._runtime_logger().error("[Skills/V3] Failed to save skill_usage_summary.json: %s", str(e))

    def _run_skill_branch(
        self,
        instruction: str,
        obs: Dict,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        original_width: int,
        original_height: int,
        trigger_skill_name: str,
        main_trigger_response: str,
        step_idx: int,
    ) -> Dict[str, Any]:
        self._skill_invocation_counter += 1
        branch_id = self._skill_invocation_counter

        branch_skill_payloads: List[Tuple[str, Dict]] = []
        branch_loaded_names: Set[str] = set()
        round_feedback: List[str] = []
        pending_skill_name: Optional[str] = trigger_skill_name
        branch_rounds: List[dict] = []
        final_response = ""
        final_summary: Optional[Dict[str, str]] = None
        success = False

        for round_idx in range(v2mod.MAX_SKILL_LOAD_ROUNDS):
            load_event: Optional[dict] = None
            if pending_skill_name is not None:
                full_skill, image_count, load_error = self._load_skill_for_branch(pending_skill_name, branch_loaded_names)
                if full_skill is not None:
                    branch_loaded_names.add(pending_skill_name)
                    branch_skill_payloads.append((pending_skill_name, full_skill))
                    load_event = {
                        "skill_name": pending_skill_name,
                        "status": "loaded",
                        "image_count": image_count,
                        "consult_count": self._skill_consult_counts.get(pending_skill_name, 0),
                    }
                else:
                    load_event = {
                        "skill_name": pending_skill_name,
                        "status": "error",
                        "error": load_error,
                    }
                    if load_error:
                        round_feedback.append(load_error)
                pending_skill_name = None

            system_message = self._build_branch_system_message(instruction, sorted(branch_loaded_names))
            contents = self._build_branch_contents(
                instruction=instruction,
                trigger_skill_name=trigger_skill_name,
                main_trigger_response=main_trigger_response,
                processed_image=processed_image,
                processed_width=processed_width,
                processed_height=processed_height,
                obs=obs,
                branch_skill_payloads=branch_skill_payloads,
                round_feedback=round_feedback,
            )

            self._runtime_logger().info("=" * 80)
            self._runtime_logger().info(
                "[MMSkill/V3][Branch %d] Step %d round %d",
                branch_id,
                step_idx,
                round_idx + 1,
            )
            self._runtime_logger().info("[MMSkill/V3][Branch %d] System message:\n%s", branch_id, system_message)
            self._runtime_logger().info(
                "[MMSkill/V3][Branch %d] Contents:\n%s",
                branch_id,
                self._format_contents_for_log(contents),
            )

            try:
                response = self.call_llm(system_text=system_message, contents=contents)
            except Exception as e:
                self._runtime_logger().error(
                    "[MMSkill/V3][Branch %d] Failed to call model %s: %s",
                    branch_id,
                    self.model,
                    str(e),
                )
                response = ""

            final_response = response or ""
            self._runtime_logger().info("[MMSkill/V3][Branch %d] Response: %s", branch_id, final_response)

            round_record = {
                "round": round_idx + 1,
                "timestamp": time.time(),
                "loaded_skills_before_response": sorted(branch_loaded_names),
                "load_event_before_prompt": load_event,
                "system_message": system_message,
                "contents": self._serialize_contents_for_json(contents),
                "response": final_response,
            }

            summary, parse_error = self._extract_planner_summary(final_response)
            if parse_error:
                round_feedback.append(parse_error)
                round_record["status"] = "invalid_planner_summary"
                round_record["error"] = parse_error
                branch_rounds.append(round_record)
                continue

            success = True
            final_summary = summary
            round_record["status"] = "planner_summary_returned"
            round_record["planner_summary"] = dict(summary)
            branch_rounds.append(round_record)
            break

        branch_log = {
            "architecture_version": ARCHITECTURE_VERSION,
            "branch_id": branch_id,
            "step": step_idx,
            "skill_mode": self.skill_mode,
            "trigger_skill_name": trigger_skill_name,
            "main_trigger_response": main_trigger_response,
            "success": success,
            "loaded_skills": sorted(branch_loaded_names),
            "rounds": branch_rounds,
            "final_response": final_response,
            "final_summary": dict(final_summary) if final_summary else None,
            "final_feedback": round_feedback[-1] if round_feedback else None,
        }
        return {
            "success": success,
            "response": final_response,
            "summary": final_summary,
            "feedback": round_feedback[-1] if round_feedback else "Skill planner branch did not produce a valid summary.",
            "log": branch_log,
        }

    def _finalize_step(self, processed_image: str, response: str, actions: List[str]) -> Tuple[str, List[str]]:
        result = super()._finalize_step(processed_image, response, actions)
        self._current_step_planner_summaries = []
        return result

    def predict(self, instruction: str, obs: Dict) -> List:
        self._current_step_planner_summaries = []

        screenshot_bytes = obs["screenshot"]
        image = Image.open(BytesIO(screenshot_bytes))
        original_width, original_height = image.size

        processed_image, processed_width, processed_height = v2mod.base_agent_mod.process_image(screenshot_bytes)
        system_message = self._build_main_system_message(instruction)

        round_feedback: List[str] = []
        final_response = ""
        step_idx = len(self.actions)

        for round_idx in range(v2mod.MAX_SKILL_LOAD_ROUNDS):
            contents = self._build_main_contents(
                instruction=instruction,
                processed_image=processed_image,
                processed_width=processed_width,
                processed_height=processed_height,
                obs=obs,
                extra_feedback=round_feedback,
            )

            self._runtime_logger().info("=" * 80)
            self._runtime_logger().info("[MMSkill/V3] Step %d main round %d", step_idx, round_idx + 1)
            self._runtime_logger().info("[MMSkill/V3] System message:\n%s", system_message)
            self._runtime_logger().info("[MMSkill/V3] Contents:\n%s", self._format_contents_for_log(contents))

            try:
                response = self.call_llm(system_text=system_message, contents=contents)
            except Exception as e:
                self._runtime_logger().error("Failed to call skill v3 model %s: %s", self.model, str(e))
                response = ""

            final_response = response or ""
            self._runtime_logger().info("[MMSkill/V3] Main response: %s", final_response)
            self._append_main_conversation_log(
                step_idx=step_idx,
                round_idx=round_idx + 1,
                system_message=system_message,
                contents=contents,
                response=final_response,
            )

            bare_skill_name = self._extract_bare_load_skill(final_response)
            parsed_actions = self.parse_actions(
                final_response,
                original_width=original_width,
                original_height=original_height,
                processed_width=processed_width,
                processed_height=processed_height,
            )

            if self._count_code_blocks(final_response) != 1 and bare_skill_name is None and not parsed_actions:
                round_feedback.append(
                    "The previous response must contain exactly one code block. Output only one code block containing Python, WAIT, DONE, FAIL, or LOAD_SKILL(\"<exact_skill_name>\"). "
                    "If you return Python, include concise '#' comments explaining the action."
                )
                continue

            skill_name = bare_skill_name or self._extract_load_skill(final_response)
            if skill_name is not None:
                branch_result = self._run_skill_branch(
                    instruction=instruction,
                    obs=obs,
                    processed_image=processed_image,
                    processed_width=processed_width,
                    processed_height=processed_height,
                    original_width=original_width,
                    original_height=original_height,
                    trigger_skill_name=skill_name,
                    main_trigger_response=final_response,
                    step_idx=step_idx,
                )
                self._append_skill_branch_log(branch_result["log"])
                if branch_result["success"] and branch_result["summary"]:
                    planner_note = self._planner_summary_to_record(skill_name, branch_result["summary"])
                    self._upsert_current_step_planner_summary(planner_note)
                    self._update_active_skill_state(planner_note)
                else:
                    round_feedback.append(branch_result["feedback"])
                continue

            actions = parsed_actions
            if actions:
                response_to_store = final_response
                if self._current_step_planner_summaries:
                    response_to_store = self._build_planner_augmented_history_response(
                        self._current_step_planner_summaries,
                        final_response,
                        actions,
                    )
                return self._finalize_step(processed_image, response_to_store, actions)

            round_feedback.append(
                "The previous response did not contain a valid GUI action or LOAD_SKILL call. Output exactly one code block. "
                "If you return Python, include concise '#' comments explaining the action."
            )

        fallback_response = final_response or "No valid action"
        if self._current_step_planner_summaries:
            fallback_response = self._build_planner_augmented_history_response(
                self._current_step_planner_summaries,
                fallback_response,
                [],
            )
        self.screenshots.append(processed_image)
        self.responses.append(fallback_response)
        self.actions.append("No valid action")
        self._save_skill_usage_summary()
        self._save_skill_invocation_log()
        self._save_conversation_json()
        self._current_step_planner_summaries = []
        return fallback_response, []
