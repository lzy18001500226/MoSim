import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from mm_agents import _mm_skill_adapter_base as _adapter_base


ARCHITECTURE_VERSION = "mm_skill_branch_loaded_gated_views"
_BranchLoadedSkillAdapterBase = _adapter_base._MMSkillAdapterBase

MAIN_STATE_BUNDLE_PREVIEW_LIMIT = _adapter_base.MAIN_STATE_BUNDLE_PREVIEW_LIMIT
MAX_STAGE1_SELECTED_STATES = _adapter_base.MAX_STAGE1_SELECTED_STATES
MAX_STAGE1_SELECTED_VIEWS = _adapter_base.MAX_STAGE1_SELECTED_VIEWS

EVIDENCE_GOALS: Set[str] = {
    "locate_control",
    "recognize_before",
    "verify_after",
    "compare_transition",
}

GOAL_ALLOWED_VIEWS: Dict[str, Set[str]] = {
    "locate_control": {"full_frame", "focus_crop"},
    "recognize_before": {"before", "full_frame"},
    "verify_after": {"after", "full_frame"},
    "compare_transition": {"full_frame", "focus_crop", "before", "after"},
}

GOAL_REQUIRED_VIEWS: Dict[str, Set[str]] = {
    "locate_control": set(),
    "recognize_before": {"before"},
    "verify_after": {"after"},
    "compare_transition": set(),
}

PLANNER_STAGE2_EXAMPLES: List[Dict[str, object]] = [
    {
        "name": "Spreadsheet selection correction",
        "stage1": {
            "visual_reference_needed": True,
            "why_not_text_only": "The visible selected range may be wrong, so a local visual state reference can reduce ambiguity.",
            "requests": [
                {
                    "state_id": "selected_header_merge_span",
                    "views": ["focus_crop"],
                    "evidence_goal": "locate_control",
                    "reason": "focus_crop is more useful than full_frame+focus_crop here because the unresolved evidence is the exact local cell span, not the whole window.",
                }
            ],
        },
        "planner_json": {
            "skill_applicability": "effective",
            "subgoal": "select the correct header range before merging",
            "plan": (
                "Correct the live selection first, then apply the merge command only after the intended range is visibly highlighted. "
                "After the merge, type the header text and verify the merged header occupies the requested columns before moving to the next range."
            ),
            "do_not_do": "Do not keep the current wider selection or use the fill handle as a substitute for selecting the requested range.",
            "fallback_if_no_progress": (
                "If the merge button or selected range does not change after one attempt, stop following the visual reference and use the name box or direct range selection to set the exact cells before applying merge again."
            ),
            "expected_state": "Only the requested header cells are selected as the next merge target.",
            "completion_scope": "local_only",
        },
    },
    {
        "name": "Text-only menu-path planning",
        "stage1": {
            "visual_reference_needed": False,
            "why_not_text_only": "The selected text and the skill text already specify a stable menu path; loading a reference image would mostly anchor on an example window.",
            "requests": [],
        },
        "planner_json": {
            "skill_applicability": "effective",
            "subgoal": "open the menu path for the requested text transformation",
            "plan": (
                "Use the current selection and follow the textual menu path from the skill. Open the relevant top menu, choose the text transformation command, then verify the document text changes before declaring completion."
            ),
            "do_not_do": "Do not spend a step loading or matching reference screenshots when the operation is a stable menu command.",
            "fallback_if_no_progress": (
                "If the menu command is not where expected, close the menu, use the application search or an alternate shortcut/menu route for the same command, then verify the transformed text on the live document."
            ),
            "expected_state": "The selected document text has been transformed according to the instruction.",
            "completion_scope": "needs_verification",
        },
    },
]


class MMSkillAgent(_BranchLoadedSkillAdapterBase):
    """
    MMSkillAgent is the public branch-loaded multimodal skill architecture:
    - Stage 1 first gates whether visual references are needed.
    - Stage 1 explicitly declares an evidence goal and constrains view choices.
    - Exhausted skills disappear from the main prompt and are blocked before branch work.
    - Stage 2 planner summaries include do_not_do and fallback_if_no_progress.
    - Main-context state hints are reduced to state name plus use_when.
    """

    def _consult_limit(self) -> int:
        return _adapter_base.v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL

    def _is_skill_exhausted(self, skill_name: str) -> bool:
        return self._skill_consult_counts.get(skill_name, 0) >= self._consult_limit()

    def _empty_skill_usage_summary(self) -> Dict[str, object]:
        payload = super()._empty_skill_usage_summary()
        payload.update(
            {
                "architecture_version": ARCHITECTURE_VERSION,
                "stage1_visual_reference_needed_counts": {
                    "true": 0,
                    "false": 0,
                    "unspecified": 0,
                },
                "stage1_evidence_goal_counts": {},
                "stage1_text_only_gated_branches": 0,
                "exhausted_skill_load_blocks": 0,
            }
        )
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
            self._runtime_logger().error("[MMSkills] Failed to save skill_invocations.json: %s", str(e))

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
                "max_skill_consults_per_skill": self._consult_limit(),
                "skill_consult_counts": dict(self._skill_consult_counts),
                "exhausted_skill_names": sorted(
                    skill_name for skill_name in self._task_skill_names if self._is_skill_exhausted(skill_name)
                ),
                "active_skill_state": dict(self._active_skill_state) if self._active_skill_state else None,
            }
        )
        payload.pop("load_skill_image_calls", None)
        payload.pop("load_skill_image_successes", None)
        output_path = os.path.join(self._result_dir, "skill_usage_summary.json")
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._runtime_logger().error("[MMSkills] Failed to save skill_usage_summary.json: %s", str(e))

    @staticmethod
    def _compact_fragment(text: str, *, fallback: str = "no recommended usage was provided", max_chars: int = 130) -> str:
        cleaned = re.sub(r"\s+", " ", str(text or "").strip())
        for prefix in ("Use when", "Use it when", "Use this card when", "Match this card when"):
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
                break
        cleaned = cleaned.lstrip(":,- ").strip().rstrip(" .;")
        if not cleaned:
            cleaned = fallback
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[: max(0, max_chars - 3)].rstrip(" ,;:.") + "..."

    def _minimal_state_bundle_preview(self, skill_name: str) -> str:
        if self._skill_loader is None:
            return "(no state hints)"

        state_bundles = self._skill_loader.load_state_bundles(skill_name, runtime=True)
        if state_bundles is not None and state_bundles.bundles:
            lines: List[str] = []
            for bundle in state_bundles.bundles[:MAIN_STATE_BUNDLE_PREVIEW_LIMIT]:
                state_name = bundle.state_name or bundle.state_id or "(unnamed state)"
                when_to_use = self._compact_fragment(bundle.when_to_use)
                lines.append(f"  - {state_name}: use when {when_to_use}.")
            remaining = len(state_bundles.bundles) - MAIN_STATE_BUNDLE_PREVIEW_LIMIT
            if remaining > 0:
                lines.append(f"  - ... {remaining} more states")
            return "\n".join(lines)

        state_cards = self._skill_loader.load_state_cards(skill_name, runtime=True)
        if state_cards is not None and state_cards.cards:
            lines = []
            for card in state_cards.cards[:MAIN_STATE_BUNDLE_PREVIEW_LIMIT]:
                state_name = card.image_id or card.state_id or Path(card.image_path).stem or "(unnamed state)"
                when_to_use = self._compact_fragment(card.when_to_use)
                lines.append(f"  - {state_name}: use when {when_to_use}.")
            remaining = len(state_cards.cards) - MAIN_STATE_BUNDLE_PREVIEW_LIMIT
            if remaining > 0:
                lines.append(f"  - ... {remaining} more states")
            return "\n".join(lines)

        return "(no state hints)"

    def _skills_with_consult_counts_text(self, *, include_state_previews: bool = True) -> str:
        if not self._task_skill_names:
            return "None"
        lines: List[str] = []
        meta_map = {Path(meta.directory).name: meta for meta in self._task_skill_metadatas}
        for skill_name in self._task_skill_names:
            if self._is_skill_exhausted(skill_name):
                continue
            meta = meta_map.get(skill_name)
            description = ((meta.description or "").strip() if meta is not None else "") or "(no description)"
            consult_count = self._skill_consult_counts.get(skill_name, 0)
            header = f"- {skill_name} - {description} [consulted {consult_count}/{self._consult_limit()}]"
            if not include_state_previews:
                lines.append(header)
                continue
            lines.append("\n".join([header, self._minimal_state_bundle_preview(skill_name)]))
        if lines:
            return "\n".join(lines)
        return "None (all mapped skills are exhausted for this trajectory)"

    def _active_skill_state_text(self) -> str:
        state = self._visible_active_skill_state()
        if not state:
            return "None"
        lines = [
            f"- Skill: {state.get('skill_name', 'Unknown')}",
            f"- Applicability: {state.get('skill_applicability', 'unknown')}",
            f"- Plan: {state.get('plan', 'None')}",
            f"- Do not do: {state.get('do_not_do', 'None')}",
            f"- Fallback if no progress: {state.get('fallback_if_no_progress', 'None')}",
            f"- Expected state: {state.get('expected_state', 'None')}",
            f"- Completion scope: {state.get('completion_scope', 'needs_verification')}",
            f"- Last consulted at step: {state.get('last_consult_step', 'unknown')}",
            f"- Consult count: {state.get('consult_count', 0)}/{self._consult_limit()}",
        ]
        if state.get("consult_exhausted"):
            lines.append("- Consult exhausted: true; this skill is no longer loadable, so act from the memo and current screenshot.")
        return "\n".join(lines)

    def _current_step_planner_summaries_text(self) -> str:
        if not self._current_step_planner_summaries:
            return "None"
        chunks = []
        for idx, item in enumerate(self._current_step_planner_summaries, start=1):
            lines = [
                f"Planner note {idx}:",
                f"- Skill: {item.get('skill_name', 'Unknown')}",
                f"- Applicability: {item.get('skill_applicability', 'unknown')}",
                f"- Subgoal: {item.get('subgoal', 'None')}",
                f"- Plan: {item.get('plan', 'None')}",
                f"- Do not do: {item.get('do_not_do', 'None')}",
                f"- Fallback if no progress: {item.get('fallback_if_no_progress', 'None')}",
                f"- Expected state: {item.get('expected_state', 'None')}",
                f"- Completion scope: {item.get('completion_scope', 'needs_verification')}",
                f"- Consult count: {item.get('consult_count', 0)}/{self._consult_limit()}",
            ]
            if item.get("consult_exhausted"):
                lines.append("- Consult exhausted: true; do not call this skill again.")
            chunks.append("\n".join(lines))
        return "\n\n".join(chunks)

    def _planner_summary_to_record(self, skill_name: str, summary: Dict[str, str]) -> Dict[str, Any]:
        consult_count = self._skill_consult_counts.get(skill_name, 0)
        return {
            "skill_name": skill_name,
            "skill_applicability": summary["skill_applicability"],
            "subgoal": summary["subgoal"],
            "plan": summary["plan"],
            "do_not_do": summary.get("do_not_do", ""),
            "fallback_if_no_progress": summary.get("fallback_if_no_progress", ""),
            "expected_state": summary["expected_state"],
            "completion_scope": summary["completion_scope"],
            "consult_count": consult_count,
            "consult_exhausted": consult_count >= self._consult_limit(),
        }

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
            "do_not_do": planner_note.get("do_not_do"),
            "fallback_if_no_progress": planner_note.get("fallback_if_no_progress"),
            "expected_state": planner_note.get("expected_state"),
            "completion_scope": planner_note.get("completion_scope"),
            "consult_count": planner_note.get("consult_count", 0),
            "consult_exhausted": bool(planner_note.get("consult_exhausted")),
            "last_consult_step": len(self.actions) + 1,
        }

    def _build_main_system_message(self, instruction: str) -> str:
        available_skills = self._skills_with_consult_counts_text(include_state_previews=False)
        return f"""
Follow the instruction to perform desktop computer tasks.
You control the computer using Python code with `pyautogui`.

For each step, you will receive the current screenshot and the recent visible trajectory history.
Use the screenshot to decide the next action. Do not assume that previous clicks succeeded.
If an earlier action failed, adjust based on the CURRENT screenshot instead of repeating the same guess.

Task skills are optional procedural planners only.
- The final user message includes each non-exhausted skill's short description plus minimal runtime state hints. Use those hints to judge whether a skill is genuinely relevant BEFORE calling `LOAD_SKILL(...)`.
- Call `LOAD_SKILL("<exact_skill_name>")` only when the CURRENT screenshot, recent steps, and the skill hints suggest that extra procedural guidance is likely useful.
- `LOAD_SKILL(...)` opens a temporary planner branch for extra skill-guided reasoning. It does NOT execute the action for you.
- Skill hints and planner notes are references only. They are never coordinate templates.
- Each skill may be consulted at most {self._consult_limit()} times in the same trajectory.
- Skills that reached this limit are removed from the available skill list. If a skill is not listed, do not call it; act from the current screenshot and any existing planner memo instead.

Available non-exhausted skills for this task:
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
            "Please decide the next grounded response for the CURRENT screenshot. Return either the next GUI action or `LOAD_SKILL(...)` when extra procedural guidance is useful.",
            f"Instruction: {instruction}",
            "Available non-exhausted skills for this task (name + description + minimal use-when state hints):\n"
            + self._skills_with_consult_counts_text(include_state_previews=True),
            "Active planner memo:\n" + active_memo_text,
            "Planner notes returned in this step:\n" + self._current_step_planner_summaries_text(),
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Ground every action in the CURRENT screenshot.\n"
            "- Planner notes are fallible references only. They may still be incomplete or partially wrong for the live UI.\n"
            "- Re-decide the real action from the CURRENT screenshot, full recent history, and execution feedback before acting.\n"
            "- Treat state hints, selected reference views, and planner notes as references only, never as coordinate templates.\n"
            f"- Do not reload a skill after {self._consult_limit()} consults; exhausted skills are intentionally absent from the available list.\n"
            "- If no listed skill is clearly useful, act directly from the current screenshot.\n"
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

    def _build_branch_reference_content(
        self,
        trigger_skill_name: str,
        main_trigger_response: str,
        branch_skill_payloads: List[Tuple[str, Dict[str, Any]]],
    ) -> dict:
        parts: List[dict] = [
            {
                "text": "\n\n".join(
                    [
                        "Skill reference package for this temporary planner branch.",
                        f"Requested skill in the main context: LOAD_SKILL(\"{trigger_skill_name}\")",
                        "The materials below are supplemental procedural references only.",
                        "Stage 1 must first decide whether visual reference images are needed at all.",
                        "When images are needed, Stage 1 must identify the evidence goal and request only the view types that fit that goal.",
                        "The main agent, not this branch, will choose the concrete GUI action.",
                    ]
                )
            }
        ]
        for skill_name, skill_bundle in branch_skill_payloads:
            parts.extend(self._build_branch_skill_reference_parts(skill_name, skill_bundle))
        return {"role": "user", "parts": parts}

    def _build_branch_view_selection_system_message(self, instruction: str, loaded_skill_names: List[str]) -> str:
        loaded_skills = ", ".join(loaded_skill_names) if loaded_skill_names else "None"
        return f"""
You are inside Stage 1 of a temporary state-view selection branch for a single desktop step.
Your job is to decide whether visual reference images are needed before planner reasoning, and if so which evidence goal they should serve.

View semantics:
- `full_frame`: global placement and window context.
- `focus_crop`: detailed control localization.
- `before`: current pre-change state; useful for recognizing whether the UI is still before a change and avoiding repeated toggles.
- `after`: target completion state; useful for verifying what the result should look like after save/enable/format/apply.

Evidence goals and allowed view combinations:
- `locate_control`: request exactly one of `full_frame` or `focus_crop`.
- `recognize_before`: request `before`, optionally with `full_frame`.
- `verify_after`: request `after`, optionally with `full_frame`.
- `compare_transition`: request any minimal non-default transition evidence; do not request exactly the default `full_frame` + `focus_crop` pair. Prefer `before` and/or `after` when those views are available and useful.

Visual gating policy:
- First decide `visual_reference_needed`.
- If the next useful help is a generic shortcut, formula, file operation, stable menu path, or textual procedure, default to `visual_reference_needed=false` and request no images.
- Load images only for state transitions, visual result verification, or complex UI state recognition where text alone is likely insufficient.
- Do not default to `full_frame` + `focus_crop`. The requested views must match the evidence goal.

Branch rules:
- Do NOT return Python code, planner JSON, WAIT, DONE, FAIL, LOAD_SKILL, or LOAD_SKILL_IMAGE.
- The CURRENT screenshot is authoritative.
- Use exact `state_id` and exact `view_type` values from the provided state bundles.
- Keep the request minimal: at most {MAX_STAGE1_SELECTED_STATES} states and at most {MAX_STAGE1_SELECTED_VIEWS} total views.

Currently loaded branch skills:
{loaded_skills}

Output format:
- Return ONLY one code block.
- The code block must contain exactly one `LOAD_STATE_VIEWS(...)` call.
- The payload must be a JSON object with:
  - `"visual_reference_needed"`: true or false
  - `"why_not_text_only"`: explain why text-only is insufficient, or why no images are needed
  - `"requests"`: a JSON list of request objects
- Each request object must contain:
  - `"state_id"`: an exact state ID from the bundle manifest
  - `"views"`: a non-empty list of exact view types for that state
  - `"evidence_goal"`: one of `locate_control`, `recognize_before`, `verify_after`, `compare_transition`
  - `"reason"`: explain why these views are more useful than the default `full_frame` + `focus_crop` habit for the current uncertainty
- When `"visual_reference_needed"` is false, `"requests"` must be empty.
- Do not return prose outside the code block.

Correct example with a before/after transition:
```python
LOAD_STATE_VIEWS({{
  "visual_reference_needed": true,
  "why_not_text_only": "The task depends on whether the setting is currently before or after the toggle, so text alone may cause a repeated toggle.",
  "requests": [
    {{
      "state_id": "developer_mode_toggle",
      "views": ["before", "after"],
      "evidence_goal": "compare_transition",
      "reason": "before+after is more useful than full_frame+focus_crop because the uncertainty is the state transition, not the control location."
    }}
  ]
}})
```

Correct example without reference views:
```python
LOAD_STATE_VIEWS({{
  "visual_reference_needed": false,
  "why_not_text_only": "The current task is a stable menu path described in the skill text, so loading screenshots would add visual anchoring without resolving new uncertainty.",
  "requests": []
}})
```

The computer password is '{self.client_password}', use it when needed.
You are asked to complete the following task: {instruction}
""".strip()

    def _build_branch_view_selection_user_text(
        self,
        instruction: str,
        original_width: int,
        original_height: int,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        round_feedback: Optional[List[str]] = None,
    ) -> str:
        previous_steps = self._build_previous_steps_text()
        env_feedback = self._normalized_branch_env_feedback(
            obs,
            original_width=original_width,
            original_height=original_height,
            processed_width=processed_width,
            processed_height=processed_height,
        )
        text_sections = [
            "Please inspect the CURRENT UI screenshot and decide whether visual reference images are needed before planner reasoning.",
            f"Instruction: {instruction}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            "Environment feedback from the previous step:\n" + env_feedback,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Return `LOAD_STATE_VIEWS({...})` only.\n"
            "- If text and the live screenshot are sufficient, set `visual_reference_needed=false` and use an empty `requests` list.\n"
            "- If the uncertainty is control location, use `locate_control` with only one of `full_frame` or `focus_crop`.\n"
            "- If the uncertainty is whether the UI is still before the change, use `recognize_before` with `before` and optional `full_frame`.\n"
            "- If the uncertainty is target/result verification, use `verify_after` with `after` and optional `full_frame`.\n"
            "- If the uncertainty is the transition itself, use `compare_transition` and avoid exactly the default `full_frame` + `focus_crop` pair; prefer `before` and/or `after` when useful.\n"
            f"- Select at most {MAX_STAGE1_SELECTED_STATES} states and at most {MAX_STAGE1_SELECTED_VIEWS} total views.\n"
            "- Do not request reference views that mainly duplicate one another without adding new evidence.",
        ]
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text_sections.append("Loop warning:\n" + repetition_warning)
        if round_feedback:
            feedback_lines = "\n".join(f"- {item}" for item in round_feedback if item)
            if feedback_lines:
                text_sections.append("Additional feedback for this state-view selection round:\n" + feedback_lines)
        return "\n\n".join(text_sections)

    @staticmethod
    def _parse_stage1_bool(value: object) -> Optional[bool]:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "yes", "1"}:
                return True
            if normalized in {"false", "no", "0"}:
                return False
        return None

    def _record_stage1_decision(self, decision: Dict[str, object], requests: List[Dict[str, object]]) -> None:
        counts = dict(self._skill_usage_summary.get("stage1_visual_reference_needed_counts", {}))
        visual_needed = decision.get("visual_reference_needed")
        if visual_needed is True:
            visual_key = "true"
        elif visual_needed is False:
            visual_key = "false"
        else:
            visual_key = "unspecified"
        counts[visual_key] = int(counts.get(visual_key, 0)) + 1
        self._skill_usage_summary["stage1_visual_reference_needed_counts"] = counts
        if visual_key == "false":
            self._skill_usage_summary["stage1_text_only_gated_branches"] = int(
                self._skill_usage_summary.get("stage1_text_only_gated_branches", 0)
            ) + 1

        goal_counts = dict(self._skill_usage_summary.get("stage1_evidence_goal_counts", {}))
        for item in requests:
            goal = str(item.get("evidence_goal", "") or "").strip()
            if goal:
                goal_counts[goal] = int(goal_counts.get(goal, 0)) + 1
        self._skill_usage_summary["stage1_evidence_goal_counts"] = goal_counts

    def _extract_load_state_views_request(
        self,
        response: str,
    ) -> Tuple[Optional[List[Dict[str, object]]], Optional[str]]:
        self._last_stage1_selection_decision = None
        self._last_stage1_request_by_state = {}

        if not response:
            return None, "The branch returned an empty state-view selection response."

        if self._count_code_blocks(response) == 1:
            code_body = self._extract_first_code_block_text(response)
        elif self._count_code_blocks(response) == 0:
            code_body = self._normalize_non_codeblock_response(response)
        else:
            return None, "The state-view selection response must contain exactly one code block with LOAD_STATE_VIEWS({...})."

        if not code_body:
            return None, "The state-view selection response code block was empty."

        raw_lines = [line.rstrip() for line in code_body.splitlines() if line.strip()]
        stripped_lines = [line.strip() for line in raw_lines if not line.strip().startswith("#")]
        normalized = "\n".join(stripped_lines).strip()
        match = re.fullmatch(r"LOAD_STATE_VIEWS\((.*)\)\s*;?", normalized, re.DOTALL)
        if not match:
            return None, "The state-view selection response must be a LOAD_STATE_VIEWS({...}) call."

        payload = match.group(1).strip()
        if not payload:
            payload = '{"visual_reference_needed": false, "why_not_text_only": "No visual references requested.", "requests": []}'

        try:
            parsed = json.loads(payload)
        except Exception as exc:
            return None, f"LOAD_STATE_VIEWS(...) must contain valid JSON. Parse error: {exc}"

        parent_goal = ""
        if isinstance(parsed, dict):
            visual_reference_needed = self._parse_stage1_bool(parsed.get("visual_reference_needed"))
            requests_raw = parsed.get("requests", [])
            why_not_text_only = str(parsed.get("why_not_text_only", "") or "").strip()
            parent_goal = str(parsed.get("evidence_goal", "") or "").strip()
        elif isinstance(parsed, list):
            visual_reference_needed = bool(parsed)
            requests_raw = parsed
            why_not_text_only = ""
        else:
            return None, "LOAD_STATE_VIEWS(...) must contain a JSON object with a `requests` list."

        if not isinstance(requests_raw, list):
            return None, "`requests` in LOAD_STATE_VIEWS(...) must be a JSON list."

        if visual_reference_needed is None:
            visual_reference_needed = bool(requests_raw)
        if visual_reference_needed is False and requests_raw:
            return None, "When `visual_reference_needed` is false, `requests` must be empty."
        if visual_reference_needed is False and not why_not_text_only:
            return None, "When `visual_reference_needed` is false, `why_not_text_only` must explain why no images are needed."
        if visual_reference_needed is True and not requests_raw:
            return None, "When `visual_reference_needed` is true, `requests` must contain at least one state-view request."
        if visual_reference_needed is True and not why_not_text_only:
            return None, "When `visual_reference_needed` is true, `why_not_text_only` must explain why text-only is insufficient."

        merged: Dict[str, Dict[str, object]] = {}
        for item in requests_raw:
            if not isinstance(item, dict):
                return None, "Each `requests` item must be a JSON object."

            state_id = str(item.get("state_id", "") or "").strip()
            if not state_id:
                return None, "Each `requests` item must include a non-empty `state_id`."

            evidence_goal = str(item.get("evidence_goal", "") or parent_goal).strip()
            if evidence_goal not in EVIDENCE_GOALS:
                return None, (
                    f"`evidence_goal` for state '{state_id}' must be one of: "
                    "locate_control, recognize_before, verify_after, compare_transition."
                )

            raw_views = item.get("views", [])
            if not isinstance(raw_views, list):
                return None, f"`views` for state '{state_id}' must be a list of strings."
            deduped_views: List[str] = []
            for raw_view in raw_views:
                view_type = str(raw_view).strip()
                if view_type and view_type not in deduped_views:
                    deduped_views.append(view_type)
            if not deduped_views:
                return None, f"`views` for state '{state_id}' must contain at least one non-empty view type."

            allowed_views = GOAL_ALLOWED_VIEWS[evidence_goal]
            disallowed = [view for view in deduped_views if view not in allowed_views]
            if disallowed:
                return None, (
                    f"`views` for state '{state_id}' do not match evidence_goal '{evidence_goal}'. "
                    f"Disallowed views: {', '.join(disallowed)}."
                )
            missing_required = sorted(GOAL_REQUIRED_VIEWS[evidence_goal] - set(deduped_views))
            if missing_required:
                return None, (
                    f"`views` for state '{state_id}' with evidence_goal '{evidence_goal}' must include: "
                    f"{', '.join(missing_required)}."
                )
            if evidence_goal == "locate_control" and len(deduped_views) != 1:
                return None, "`locate_control` must request exactly one of `full_frame` or `focus_crop`, not both."
            if evidence_goal == "compare_transition" and set(deduped_views) == {"full_frame", "focus_crop"}:
                return None, "`compare_transition` must not request exactly the default `full_frame` + `focus_crop` pair."

            reason = str(item.get("reason", "") or "").strip()
            if not reason:
                return None, f"`reason` for state '{state_id}' must explain why the selected views are needed."

            existing = merged.get(state_id)
            if existing is not None and existing.get("evidence_goal") != evidence_goal:
                return None, f"State '{state_id}' was requested with multiple evidence goals. Use one evidence goal per state."
            if existing is None:
                merged[state_id] = {
                    "state_id": state_id,
                    "views": deduped_views,
                    "evidence_goal": evidence_goal,
                    "visual_reference_needed": visual_reference_needed,
                    "why_not_text_only": why_not_text_only,
                    "reason": reason,
                }
            else:
                existing_views = list(existing.get("views", []))
                for view_type in deduped_views:
                    if view_type not in existing_views:
                        existing_views.append(view_type)
                existing["views"] = existing_views
                if reason and reason not in str(existing.get("reason", "")):
                    existing["reason"] = f"{existing.get('reason', '')} {reason}".strip()

        normalized_items = list(merged.values())
        total_view_count = sum(len(item.get("views", [])) for item in normalized_items)
        if len(normalized_items) > MAX_STAGE1_SELECTED_STATES:
            return None, (
                f"Select at most {MAX_STAGE1_SELECTED_STATES} states in LOAD_STATE_VIEWS(...), "
                f"but received {len(normalized_items)}."
            )
        if total_view_count > MAX_STAGE1_SELECTED_VIEWS:
            return None, (
                f"Select at most {MAX_STAGE1_SELECTED_VIEWS} total views in LOAD_STATE_VIEWS(...), "
                f"but received {total_view_count}."
            )

        decision = {
            "visual_reference_needed": visual_reference_needed,
            "why_not_text_only": why_not_text_only,
            "request_count": len(normalized_items),
            "total_view_count": total_view_count,
            "evidence_goals": sorted({str(item.get("evidence_goal", "")) for item in normalized_items if item.get("evidence_goal")}),
        }
        self._last_stage1_selection_decision = decision
        self._last_stage1_request_by_state = {str(item["state_id"]): dict(item) for item in normalized_items}
        self._record_stage1_decision(decision, normalized_items)
        return normalized_items, None

    def _build_selected_state_view_reference_content(
        self,
        skill_name: str,
        selected_selections: List[Any],
    ) -> Optional[dict]:
        if not selected_selections:
            return None

        request_meta = getattr(self, "_last_stage1_request_by_state", {}) or {}
        parts: List[dict] = [
            {
                "text": (
                    "Stage-1 selection record for this branch.\n"
                    "Use the evidence goal, requested states, requested view types, and selection reasons as planner evidence.\n"
                    "The loaded reference views below are supplemental references only. They are never coordinate templates."
                )
            }
        ]
        for selection in selected_selections:
            requested_view_text = ", ".join(selection.requested_view_types) if selection.requested_view_types else "None"
            meta = request_meta.get(selection.state.state_id, {})
            parts.append(
                {
                    "text": "\n".join(
                        [
                            f"[Stage-1 Selection - {skill_name}/{selection.state.state_id}]",
                            f"stage: {selection.state.stage or '(unknown)'}",
                            f"evidence_goal: {meta.get('evidence_goal', '(missing)')}",
                            f"visual_reference_needed: {meta.get('visual_reference_needed', '(missing)')}",
                            f"why_not_text_only: {meta.get('why_not_text_only', '(missing)')}",
                            f"requested_views: {requested_view_text}",
                            f"reason: {selection.reason or meta.get('reason') or '(none provided)'}",
                            f"when_to_use: {selection.state.when_to_use or '(missing)'}",
                            f"verification_cue: {selection.state.verification_cue or '(none listed)'}",
                        ]
                    )
                }
            )
            for loaded_view in selection.loaded_views:
                filename, b64_data, mime_type = loaded_view.image
                cues = ", ".join(selection.state.visible_cues[:4]) if selection.state.visible_cues else "(no visible cues listed)"
                parts.append(
                    {
                        "text": "\n".join(
                            [
                                f"[Selected State View - {skill_name}/{selection.state.state_id}/{loaded_view.view.view_type} -> {filename}]",
                                f"state_name: {selection.state.state_name or selection.state.state_id}",
                                f"stage: {selection.state.stage or '(unknown)'}",
                                f"use_for: {loaded_view.view.use_for or '(missing)'}",
                                f"label: {loaded_view.view.label or '(missing)'}",
                                f"visible_cues: {cues}",
                                f"verification_cue: {selection.state.verification_cue or '(none listed)'}",
                                f"visual_risk: {selection.state.visual_risk or '(none listed)'}",
                            ]
                        )
                    }
                )
                parts.append({"inlineData": {"mimeType": mime_type, "data": b64_data}})
        return {"role": "user", "parts": parts}

    def _planner_stage2_examples_text(self) -> str:
        chunks: List[str] = ["High-quality planner examples:"]
        for idx, example in enumerate(PLANNER_STAGE2_EXAMPLES, start=1):
            stage1_json = json.dumps(example["stage1"], ensure_ascii=False, indent=2)
            planner_json = json.dumps(example["planner_json"], ensure_ascii=False, indent=2)
            chunks.extend(
                [
                    f"Example {idx}: {example['name']}",
                    "Stage-1 selection decision:",
                    f"```json\n{stage1_json}\n```",
                    "Good planner JSON:",
                    f"```json\n{planner_json}\n```",
                ]
            )
        return "\n".join(chunks)

    def _build_branch_planner_system_message(self, instruction: str, loaded_skill_names: List[str]) -> str:
        loaded_skills = ", ".join(loaded_skill_names) if loaded_skill_names else "None"
        examples_text = self._planner_stage2_examples_text()
        return f"""
You are inside Stage 2 of a temporary planner-only skill consultation branch for a single desktop step.
Your job is NOT to return a GUI action. Your job is to return a structured planner summary for the CURRENT state.

Branch rules:
- Do not return Python code, WAIT, DONE, FAIL, LOAD_SKILL, LOAD_SKILL_IMAGE, or LOAD_STATE_VIEWS.
- Do not request another skill in this branch.
- The main agent will choose the real GUI action after reading your planner summary.
- Use the CURRENT screenshot first. Skill text, runtime state bundles, the stage-1 selection decision, and any loaded reference views are supplemental references only.
- If Stage 1 chose no visual references, respect that decision and avoid inventing image-based assumptions.
- If a skill is ineffective for the CURRENT state, say so clearly and avoid forcing the plan toward the skill.
- Treat any loaded reference views as state references, never as coordinate templates.
- `subgoal` must be the next immediate local milestone for the user instruction under the CURRENT state.
- `plan` must be the longer-range instruction-solving route for the CURRENT state after integrating the skill materials, Stage-1 decision, selected references if any, and the CURRENT screenshot.
- `plan` must identify the currently relevant UI surface or control area, the next 2 to 4 key actions/checks/transitions, and the visible cue that means advance versus re-plan.
- `do_not_do` must name the most likely wrong path the skill/reference might bias the main agent toward.
- `fallback_if_no_progress` must be detailed, similar in specificity to `plan`, and must give a concrete alternate route if the skill path stops making progress.
- Strong planners correct mismatched current state before continuing the skill flow.
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
  - `"do_not_do"`: a concrete bad path to avoid
  - `"fallback_if_no_progress"`: a detailed alternate route if the skill-guided path stalls
  - `"expected_state"`: a short string describing visible screenshot cues the main agent should aim for next
  - `"completion_scope"`: one of `"local_only"`, `"needs_verification"`, `"maybe_complete"`
- Do not return prose outside the code block.

Correct minimal example:
```json
{{
  "skill_applicability": "effective",
  "subgoal": "open the settings surface that exposes the requested control",
  "plan": "Stay on the currently visible settings path, operate the row or submenu that should reveal the requested control, then verify the control itself becomes visible before editing it.",
  "do_not_do": "Do not repeat the same click on an unrelated settings row if the expected control does not appear.",
  "fallback_if_no_progress": "If the settings path does not reveal the control after one attempt, return to the current page's search field or top-level category list, search for the exact setting name, and continue only after the live UI shows the requested control.",
  "expected_state": "The requested control is visible and ready to edit on the active settings surface",
  "completion_scope": "local_only"
}}
```

{examples_text}

The computer password is '{self.client_password}', use it when needed.
You are asked to complete the following task: {instruction}
""".strip()

    def _build_branch_planner_user_text(
        self,
        instruction: str,
        original_width: int,
        original_height: int,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        selected_selections: List[Any],
        round_feedback: Optional[List[str]] = None,
    ) -> str:
        previous_steps = self._build_previous_steps_text()
        env_feedback = self._normalized_branch_env_feedback(
            obs,
            original_width=original_width,
            original_height=original_height,
            processed_width=processed_width,
            processed_height=processed_height,
        )
        selected_text = ", ".join(self._flatten_selection_view_ids(selected_selections)) if selected_selections else "None"
        stage1_decision = getattr(self, "_last_stage1_selection_decision", None)
        if stage1_decision:
            stage1_text = json.dumps(stage1_decision, ensure_ascii=False)
        else:
            stage1_text = "None"
        text_sections = [
            "Please inspect the CURRENT UI screenshot and return planner JSON only.",
            "The screenshot attached BELOW this instruction is the true live environment state. It is more authoritative than any loaded skill reference view, and the next grounded action must ultimately follow that live screenshot.",
            f"Instruction: {instruction}",
            f"Stage-1 visual selection decision: {stage1_text}",
            f"Selected state views for this branch: {selected_text}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            "Environment feedback from the previous step:\n" + env_feedback,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Keep the planner grounded in the CURRENT screenshot.\n"
            "- Use the loaded skill only for the specific procedural knowledge that matters now.\n"
            "- Use the Stage-1 decision as evidence about whether visual references were needed and which uncertainty type is active.\n"
            "- `subgoal` should stay local and immediate: the next small milestone under the live UI.\n"
            "- `plan` should cover the currently relevant UI surface, the next 2 to 4 key actions/checks or transitions, and what visible cue means advance versus re-plan.\n"
            "- `do_not_do` should explicitly block the likely skill-induced mistake or repetitive path.\n"
            "- `fallback_if_no_progress` should be as detailed as `plan` and should name a concrete alternate route.\n"
            "- Do not let skill examples or selected views override what is actually visible now.\n"
            "- If the live UI is not yet at the local state assumed by the skill, say what must be corrected first.\n"
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

    def _extract_planner_summary(self, response: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        if self._count_code_blocks(response) != 1:
            return None, (
                "The branch response must contain exactly one code block with a JSON object containing "
                "`skill_applicability`, `subgoal`, `plan`, `do_not_do`, `fallback_if_no_progress`, "
                "`expected_state`, and `completion_scope`."
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
        do_not_do = str(payload.get("do_not_do", "")).strip()
        fallback_if_no_progress = str(payload.get("fallback_if_no_progress", "")).strip()
        expected_state = str(payload.get("expected_state", "")).strip()
        completion_scope = str(payload.get("completion_scope", "")).strip().lower()
        if not subgoal:
            return None, "The `subgoal` field must be a non-empty string."
        if not plan:
            return None, "The `plan` field must be a non-empty string."
        if not do_not_do:
            return None, "The `do_not_do` field must be a non-empty string."
        if not fallback_if_no_progress:
            return None, "The `fallback_if_no_progress` field must be a non-empty string."
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
            "do_not_do": do_not_do,
            "fallback_if_no_progress": fallback_if_no_progress,
            "expected_state": expected_state,
            "completion_scope": completion_scope,
        }, None

    def _load_skill_for_branch(
        self,
        skill_name: str,
        branch_loaded_names: Set[str],
    ) -> Tuple[Optional[Dict[str, Any]], int, Optional[str]]:
        if skill_name and skill_name in self._task_skill_names and self._is_skill_exhausted(skill_name):
            self._skill_usage_summary["load_skill_calls"] = int(self._skill_usage_summary.get("load_skill_calls", 0)) + 1
            self._skill_usage_summary["exhausted_skill_load_blocks"] = int(
                self._skill_usage_summary.get("exhausted_skill_load_blocks", 0)
            ) + 1
            return (
                None,
                0,
                "That skill has reached its consult limit and is no longer available. "
                "You must continue from the CURRENT screenshot, recent history, and any active planner memo without loading it again.",
            )
        return super()._load_skill_for_branch(skill_name, branch_loaded_names)

    def _run_skill_branch(self, *args, **kwargs) -> Dict[str, Any]:
        self._last_stage1_selection_decision = None
        self._last_stage1_request_by_state = {}
        result = super()._run_skill_branch(*args, **kwargs)
        log = result.get("log") if isinstance(result, dict) else None
        if isinstance(log, dict):
            log["architecture_version"] = ARCHITECTURE_VERSION
            decision = getattr(self, "_last_stage1_selection_decision", None)
            if decision is not None:
                log["stage1_selection_decision"] = dict(decision)
                for round_record in log.get("rounds", []) or []:
                    if isinstance(round_record, dict) and round_record.get("stage") == "state_view_selection":
                        round_record.setdefault("stage1_selection_decision", dict(decision))
        return result
