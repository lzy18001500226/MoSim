import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mm_agents import _mm_skill_state_cards as v4mod


ARCHITECTURE_VERSION = "mm_skill_long_plan_no_advisory_action"
MAIN_STATE_CARD_PREVIEW_LIMIT = 3


class _MMSkillLongPlanAgent(v4mod._MMSkillStateCardsAgent):
    """
    V6 keeps V5's richer main-context prompting while removing advisory branch
    actions. Branches return planner guidance only, with a stricter distinction:
    - subgoal: the immediate local milestone for the current state
    - plan: the longer-range instruction-solving route informed by the loaded
      skill materials plus the live screenshot
    """

    def _empty_skill_usage_summary(self) -> Dict[str, object]:
        payload = super()._empty_skill_usage_summary()
        payload.update({"architecture_version": ARCHITECTURE_VERSION})
        payload.pop("planner_suggested_actions_nonempty", None)
        return payload

    def _append_main_conversation_log(
        self,
        step_idx: int,
        round_idx: int,
        system_message: str,
        contents: List[dict],
        response: str,
    ):
        self._conversation_log.append(
            {
                "entry_type": "main_interaction",
                "architecture_version": ARCHITECTURE_VERSION,
                "step": step_idx,
                "round": round_idx,
                "timestamp": time.time(),
                "system_message": system_message,
                "contents": self._serialize_contents_for_json(contents),
                "response": response,
            }
        )

    def _save_skill_invocation_log(self):
        if not self._result_dir:
            return
        output_path = os.path.join(self._result_dir, "skill_invocations.json")
        payload = {
            "architecture_version": ARCHITECTURE_VERSION,
            "skill_mode": self.skill_mode,
            "task_skill_names": list(self._task_skill_names),
            "invocations": self._skill_invocation_log,
        }
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._runtime_logger().error("[Skills/V6] Failed to save skill_invocations.json: %s", str(e))

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
                "max_skill_consults_per_skill": v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL,
                "skill_consult_counts": dict(self._skill_consult_counts),
                "active_skill_state": dict(self._active_skill_state) if self._active_skill_state else None,
            }
        )
        payload.pop("planner_suggested_actions_nonempty", None)
        output_path = os.path.join(self._result_dir, "skill_usage_summary.json")
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._runtime_logger().error("[Skills/V6] Failed to save skill_usage_summary.json: %s", str(e))

    def _skills_with_consult_counts_text(self, *, include_state_previews: bool = True) -> str:
        if not self._task_skill_names:
            return "None"
        lines: List[str] = []
        meta_map = {Path(meta.directory).name: meta for meta in self._task_skill_metadatas}
        for skill_name in self._task_skill_names:
            meta = meta_map.get(skill_name)
            description = ((meta.description or "").strip() if meta is not None else "") or "(no description)"
            consult_count = self._skill_consult_counts.get(skill_name, 0)
            header = (
                f"- {skill_name} - {description} "
                f"[consulted {consult_count}/{v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL}]"
            )
            if not include_state_previews:
                lines.append(header)
                continue
            state_cards = self._skill_loader.load_state_cards(skill_name, runtime=True) if self._skill_loader else None
            preview = (
                self._skill_loader.summarize_state_cards_for_preview(
                    state_cards,
                    max_cards=MAIN_STATE_CARD_PREVIEW_LIMIT,
                )
                if self._skill_loader
                else "(no state-card preview)"
            )
            lines.append("\n".join([header, preview]))
        return "\n".join(lines)

    def _build_main_system_message(self, instruction: str) -> str:
        available_skills = self._skills_with_consult_counts_text(include_state_previews=False)
        return f"""
Follow the instruction to perform desktop computer tasks.
You control the computer using Python code with `pyautogui`.

For each step, you will receive the current screenshot and the recent visible trajectory history.
Use the screenshot to decide the next action. Do not assume that previous clicks succeeded.
If an earlier action failed, adjust based on the CURRENT screenshot instead of repeating the same guess.

Task skills are optional procedural planners only.
- The final user message includes each skill's short description plus three compact runtime state-card previews. Use those previews to judge whether a skill is genuinely relevant BEFORE calling `LOAD_SKILL(...)`.
- Call `LOAD_SKILL("<exact_skill_name>")` only when the CURRENT screenshot, recent steps, and the skill previews suggest that extra procedural guidance is likely useful.
- `LOAD_SKILL(...)` opens a temporary planner branch for extra skill-guided reasoning. It does NOT execute the action for you.
- The branch returns structured planner guidance only: `skill_applicability`, `subgoal`, `plan`, `expected_state`, and `completion_scope`.
- In branch summaries, `subgoal` is the next local milestone for the CURRENT state, while `plan` is the longer-range route for solving the user instruction after integrating the loaded skill materials with the CURRENT screenshot.
- Skill descriptions, state-card previews, and planner notes are references only. They are never coordinate templates.
- Each skill may be consulted at most {v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL} times in the same trajectory.

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
                        f"- Consult count: {item.get('consult_count', 0)}/{v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL}",
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
            "Please decide the next grounded response for the CURRENT screenshot. Return either the next GUI action or `LOAD_SKILL(...)` when extra procedural guidance is useful.",
            f"Instruction: {instruction}",
            "Available skills for this task (descriptions + compact runtime state-card previews):\n"
            + self._skills_with_consult_counts_text(include_state_previews=True),
            "Active planner memo:\n" + active_memo_text,
            "Planner notes returned in this step:\n" + self._current_step_planner_summaries_text(),
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Ground every action in the CURRENT screenshot.\n"
            "- Planner notes are fallible references only. They may still be incomplete or partially wrong for the live UI.\n"
            "- Re-decide the real action from the CURRENT screenshot, full recent history, and execution feedback before acting.\n"
            "- Treat skills, state cards, and planner notes as references only, never as coordinate templates.\n"
            f"- Do not reload a skill after {v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL} consults.\n"
            "- Use the runtime state-card previews to avoid misloading unrelated skills.\n"
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

    def _build_branch_planner_system_message(self, instruction: str, loaded_skill_names: List[str]) -> str:
        loaded_skills = ", ".join(loaded_skill_names) if loaded_skill_names else "None"
        return f"""
You are inside a temporary planner-only skill consultation branch for a single desktop step.
Your job is NOT to return a GUI action. Your job is to return a structured planner summary for the CURRENT state.

Branch rules:
- Do not return Python code, WAIT, DONE, FAIL, LOAD_SKILL, or LOAD_SKILL_IMAGE.
- Do not request another skill in this branch.
- The main agent will choose the real GUI action after reading your planner summary.
- Use the CURRENT screenshot first. Skill text, runtime state cards, and any selected skill images are supplemental references only.
- If a skill is ineffective for the CURRENT state, say so clearly and avoid forcing the plan toward the skill.
- Treat any selected skill images as state references, never as coordinate templates.
- `subgoal` must be the next immediate local milestone for the user instruction under the CURRENT state.
- Keep `subgoal` short, local, and near-term. It should answer what local state the main agent should reach next.
- `plan` must be the longer-range instruction-solving route for the CURRENT state after integrating the loaded skill materials with the CURRENT screenshot and recent responses.
- `plan` must not collapse into the same content as `subgoal`.
- `plan` must identify the currently relevant UI surface or control area, the next 2 to 4 key actions, checks, or transitions that matter, and the visible cue that means advance versus re-plan.
- `plan` should reflect the loaded skill's core transferable knowledge, but it must stay grounded in the CURRENT screenshot instead of blindly following skill examples.
- `expected_state` must describe visible screenshot cues the main agent should aim to reveal next.
- `completion_scope` must be judged against the full user instruction, not only the local subgoal.

Currently loaded branch skills:
{loaded_skills}

Output format:
- Return ONLY one code block.
- The code block must contain exactly one JSON object with these keys:
  - `"skill_applicability"`: one of `"effective"`, `"ineffective"`, `"uncertain"`
  - `"subgoal"`: a short local milestone string
  - `"plan"`: a longer-range behavior plan grounded in the current state
  - `"expected_state"`: a short string describing visible screenshot cues the main agent should aim for next
  - `"completion_scope"`: one of `"local_only"`, `"needs_verification"`, `"maybe_complete"`
- Do not return prose outside the code block.

Correct example:
```json
{{
  "skill_applicability": "effective",
  "subgoal": "open the settings surface that exposes the requested control",
  "plan": "stay on the currently visible settings path, operate the row or submenu that should reveal the requested control, then verify the control itself becomes visible before editing it. If the click opens an unrelated panel or the expected control still does not appear, stop following the skill pattern and re-plan from the live UI instead of repeating blindly.",
  "expected_state": "The requested control is visible and ready to edit on the active settings surface",
  "completion_scope": "local_only"
}}
```

The computer password is '{self.client_password}', use it when needed.
You are asked to complete the following task: {instruction}
""".strip()

    def _build_branch_planner_user_text(
        self,
        instruction: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        selected_cards: List[Any],
        round_feedback: Optional[List[str]] = None,
    ) -> str:
        previous_steps = self._build_previous_steps_text()
        selected_text = (
            ", ".join(card.image_id or card.state_id or Path(card.image_path).stem for card in selected_cards)
            if selected_cards
            else "None"
        )
        text_sections = [
            "Please inspect the CURRENT UI screenshot and return planner JSON only.",
            f"Instruction: {instruction}",
            f"Selected skill images for this branch: {selected_text}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            "Environment feedback from the previous step:\n" + self._extract_env_feedback(obs),
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Keep the planner grounded in the CURRENT screenshot.\n"
            "- Use the loaded skill only for the specific procedural knowledge that matters now.\n"
            "- `subgoal` should stay local and immediate: the next small milestone under the live UI.\n"
            "- `plan` should be the longer-range behavior route for solving the user instruction from the CURRENT state after incorporating the loaded skill materials.\n"
            "- `plan` should cover the currently relevant UI surface, the next 2 to 4 key actions/checks or transitions, and what visible cue means advance versus re-plan.\n"
            "- Do not let `plan` collapse into the same content as `subgoal`.\n"
            "- Do not let skill examples or selected images override what is actually visible now.\n"
            "- `expected_state` must describe visible cues, not an abstract end goal.",
        ]
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text_sections.append("Loop warning:\n" + repetition_warning)
        if round_feedback:
            feedback_lines = "\n".join(f"- {item}" for item in round_feedback if item)
            if feedback_lines:
                text_sections.append("Additional feedback for this planner round:\n" + feedback_lines)
        return "\n\n".join(text_sections)

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
        result = super()._run_skill_branch(
            instruction=instruction,
            obs=obs,
            processed_image=processed_image,
            processed_width=processed_width,
            processed_height=processed_height,
            original_width=original_width,
            original_height=original_height,
            trigger_skill_name=trigger_skill_name,
            main_trigger_response=main_trigger_response,
            step_idx=step_idx,
        )
        branch_log = result.get("log")
        if isinstance(branch_log, dict):
            branch_log["architecture_version"] = ARCHITECTURE_VERSION
        return result
