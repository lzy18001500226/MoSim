from __future__ import annotations

import json
import logging
import os
import re
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from PIL import Image

from mm_agents import general_agent as base_agent_mod
from mm_agents import general_skill_agent as inline_mod


TEXT_SKILL_MODE_INLINE_CONTEXT = "inline_context"
TEXT_SKILL_MODE_BRANCH_PLANNER = "branch_planner"
TEXT_SKILL_MODE_CHOICES = {
    TEXT_SKILL_MODE_INLINE_CONTEXT,
    TEXT_SKILL_MODE_BRANCH_PLANNER,
}

INLINE_ARCHITECTURE_VERSION = "general_text_skill_agent_inline_context"
BRANCH_ARCHITECTURE_VERSION = "general_text_skill_agent_branch_planner"
MAX_BRANCH_SKILL_CONSULTS_PER_SKILL = 2
ACTIVE_PLANNER_MEMO_TTL_STEPS = 5

PLANNER_HISTORY_META_COMMENT_PREFIXES = (
    "# One or more text-only skill planners were consulted in this same interaction step.",
    "# The concrete action below was chosen by the main agent from the CURRENT screenshot and previous steps.",
    "# Consulted planner skill:",
    "# Skill applicability:",
    "# Planner subgoal:",
    "# Planner summary:",
    "# Expected state:",
    "# Completion scope:",
    "# Skill consult count:",
)


class _InlineContextGeneralTextSkillAgent(inline_mod.GeneralSkillAgent):
    def __init__(self, *args, text_skill_mode: str = TEXT_SKILL_MODE_INLINE_CONTEXT, **kwargs):
        kwargs["skill_mode"] = "text_only"
        super().__init__(*args, **kwargs)
        self.text_skill_mode = text_skill_mode

    def reset(self, _logger=None, vm_ip=None, **kwargs):
        super().reset(_logger=_logger, vm_ip=vm_ip, **kwargs)
        self._skill_usage_summary.update(
            {
                "architecture_version": INLINE_ARCHITECTURE_VERSION,
                "text_skill_mode": self.text_skill_mode,
            }
        )

    def set_task_skills(self, skill_names: List[str]):
        super().set_task_skills(skill_names)
        self._skill_usage_summary.update(
            {
                "architecture_version": INLINE_ARCHITECTURE_VERSION,
                "text_skill_mode": self.text_skill_mode,
            }
        )

    def _save_skill_usage_summary(self):
        if not self._result_dir:
            return
        output_path = os.path.join(self._result_dir, "skill_usage_summary.json")
        payload = dict(self._skill_usage_summary)
        payload.update(
            {
                "architecture_version": INLINE_ARCHITECTURE_VERSION,
                "text_skill_mode": self.text_skill_mode,
                "steps_recorded": len(self.actions),
                "final_actions": list(self.actions),
            }
        )
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            if base_agent_mod.logger:
                base_agent_mod.logger.error(
                    "[TextSkills/Inline] Failed to save skill_usage_summary.json: %s",
                    str(e),
                )


class _BranchPlannerGeneralTextSkillAgent(inline_mod.GeneralSkillAgent):
    def __init__(self, *args, text_skill_mode: str = TEXT_SKILL_MODE_BRANCH_PLANNER, **kwargs):
        kwargs["skill_mode"] = "text_only"
        super().__init__(*args, **kwargs)
        self.text_skill_mode = text_skill_mode
        self._skill_consult_counts: Dict[str, int] = {}
        self._active_skill_state: Optional[Dict[str, Any]] = None
        self._current_step_planner_summaries: List[Dict[str, str]] = []
        self._skill_invocation_log: List[Dict[str, Any]] = []
        self._skill_invocation_counter = 0
        self._consulted_branch_skills: Set[str] = set()

    def _runtime_logger(self):
        return (
            base_agent_mod.logger
            if base_agent_mod.logger is not None
            else logging.getLogger("desktopenv.general_text_skill_agent")
        )

    def _empty_usage_summary(self) -> Dict[str, Any]:
        return {
            "architecture_version": BRANCH_ARCHITECTURE_VERSION,
            "skill_mode": "text_only",
            "text_skill_mode": self.text_skill_mode,
            "task_skill_names": list(self._task_skill_names),
            "consulted_skill_names": [],
            "load_skill_calls": 0,
            "load_skill_successes": 0,
            "skill_branch_invocations": 0,
            "skill_branch_successes": 0,
            "skill_consult_counts": {},
            "active_skill_state": None,
        }

    def reset(self, _logger=None, vm_ip=None, **kwargs):
        super().reset(_logger=_logger, vm_ip=vm_ip, **kwargs)
        self._skill_context_messages = []
        self._skill_consult_counts = {}
        self._active_skill_state = None
        self._current_step_planner_summaries = []
        self._skill_invocation_log = []
        self._skill_invocation_counter = 0
        self._consulted_branch_skills = set()
        self._skill_usage_summary = self._empty_usage_summary()

    def set_task_skills(self, skill_names: List[str]):
        super().set_task_skills(skill_names)
        self._skill_context_messages = []
        self._skill_consult_counts = {}
        self._active_skill_state = None
        self._current_step_planner_summaries = []
        self._skill_invocation_log = []
        self._skill_invocation_counter = 0
        self._consulted_branch_skills = set()
        self._skill_usage_summary = self._empty_usage_summary()

    @staticmethod
    def _extract_first_code_block_text(response: str) -> Optional[str]:
        if not response:
            return None
        matches = re.findall(r"```(?:\w+\s+)?(.*?)```", response, re.DOTALL)
        if len(matches) != 1:
            return None
        return matches[0].strip()

    @staticmethod
    def _extract_bare_or_inline_load_skill(response: str) -> Optional[str]:
        """Accept exact bare or inline-code LOAD_SKILL responses from weaker models."""
        if not response:
            return None
        text = response.strip()
        inline_match = re.fullmatch(r"`\s*(.*?)\s*`", text, re.DOTALL)
        if inline_match:
            text = inline_match.group(1).strip()
        match = re.fullmatch(r"LOAD_SKILL\(\s*['\"]([^'\"]+)['\"]\s*\)", text)
        if not match:
            return None
        return match.group(1).strip() or None

    def _build_previous_steps_text(self) -> str:
        current_step = len(self.responses)
        history_start = max(0, current_step - self.max_trajectory_length)
        history_responses = self.responses[history_start:current_step]
        if not history_responses:
            return "None"
        return "\n\n".join(
            [
                f"Step {history_start + idx + 1} full response:\n"
                f"{self._sanitize_previous_step_response(response)}"
                for idx, response in enumerate(history_responses)
            ]
        )

    def _build_repetition_warning_text(self) -> Optional[str]:
        recent_actions = [action for action in self.actions[-3:] if action and action != "No valid action"]
        if len(recent_actions) >= 2 and recent_actions[-1] == recent_actions[-2]:
            return (
                "Recent steps already repeated the same action sequence. Do not repeat the same coordinates, "
                "menu path, or hotkey again unless the CURRENT screenshot shows clear new evidence that it is now correct."
            )
        if len(recent_actions) >= 3 and len(set(recent_actions[-3:])) == 1:
            return (
                "The recent trajectory is looping on the same action sequence. Break the loop by grounding on the "
                "CURRENT screenshot and choosing a meaningfully different next step."
            )
        return None

    def _skills_with_consult_counts_text(self) -> str:
        if not self._task_skill_names:
            return "None"
        meta_map = {Path(meta.directory).name: meta for meta in self._task_skill_metadatas}
        lines = []
        for skill_name in self._task_skill_names:
            meta = meta_map.get(skill_name)
            desc = ((meta.description or "").strip() if meta is not None else "") or "(no description)"
            count = self._skill_consult_counts.get(skill_name, 0)
            lines.append(
                f"- {skill_name}: {desc} [consulted {count}/{MAX_BRANCH_SKILL_CONSULTS_PER_SKILL}]"
            )
        return "\n".join(lines)

    def _visible_active_skill_state(self) -> Optional[Dict[str, Any]]:
        state = self._active_skill_state
        if not state:
            return None

        last_consult_step_raw = state.get("last_consult_step")
        try:
            last_consult_step = int(last_consult_step_raw)
        except (TypeError, ValueError):
            last_consult_step = 0
        if last_consult_step <= 0:
            return state

        current_step_number = len(self.responses) + 1
        steps_since_consult = current_step_number - last_consult_step
        if steps_since_consult > ACTIVE_PLANNER_MEMO_TTL_STEPS:
            return None
        return state

    def _active_skill_state_text(self) -> str:
        state = self._visible_active_skill_state()
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
                f"- Consult count: {state.get('consult_count', 0)}/{MAX_BRANCH_SKILL_CONSULTS_PER_SKILL}",
            ]
        )

    def _sanitize_previous_step_response(self, response: str) -> str:
        if not response:
            return "No valid action"
        if self._count_code_blocks(response) != 1:
            return response

        code_body = self._extract_first_code_block_text(response)
        if code_body is None:
            return response

        filtered_lines: List[str] = []
        removed_meta = False
        for line in code_body.splitlines():
            stripped = line.strip()
            if any(stripped.startswith(prefix) for prefix in PLANNER_HISTORY_META_COMMENT_PREFIXES):
                removed_meta = True
                continue
            filtered_lines.append(line.rstrip())

        if not removed_meta:
            return response

        while filtered_lines and not filtered_lines[0].strip():
            filtered_lines.pop(0)
        while filtered_lines and not filtered_lines[-1].strip():
            filtered_lines.pop()

        sanitized_body = "\n".join(filtered_lines).strip()
        if not sanitized_body:
            return response
        return f"```python\n{sanitized_body}\n```"

    def _current_step_planner_summaries_text(self) -> str:
        if not self._current_step_planner_summaries:
            return "None"
        chunks: List[str] = []
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
                        f"- Consult count: {item.get('consult_count', 0)}/{MAX_BRANCH_SKILL_CONSULTS_PER_SKILL}",
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
            "# One or more text-only skill planners were consulted in this same interaction step.",
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
                    f"# Skill consult count: {note.get('consult_count', 0)}/{MAX_BRANCH_SKILL_CONSULTS_PER_SKILL}",
                ]
            )
        return f"```python\n{chr(10).join(header_lines + code_lines)}\n```"

    def _build_skill_system_message(self, instruction: str) -> str:
        return f"""
Follow the instruction to perform desktop computer tasks.
You control the computer using Python code with `pyautogui`.

Task skills are optional text-only procedural planners.
- Call `LOAD_SKILL("<exact_skill_name>")` only when the CURRENT screenshot and previous steps are not enough.
- `LOAD_SKILL(...)` opens a temporary text-only planner branch. It does NOT execute the action for you.
- The branch reads SKILL.md text, the CURRENT screenshot, and recent interaction history, then returns structured planner information:
  `skill_applicability`, `subgoal`, `plan`, `expected_state`, and `completion_scope`.
- `LOAD_SKILL(...)` does not consume an interaction step. After the planner summary returns, you must still choose the concrete grounded GUI action in the same step.
- Skill text is a procedural reference only, never a coordinate template.
- Trust the CURRENT screenshot over any skill when they conflict.
- Each skill may be consulted at most {MAX_BRANCH_SKILL_CONSULTS_PER_SKILL} times in the same trajectory.

Available skills for this task:
{self._skills_with_consult_counts_text()}

Rules:
- Use `pyautogui` only for GUI actions.
- Do NOT use `pyautogui.locateCenterOnScreen`.
- Do NOT use `pyautogui.screenshot()`.
- Keep actions grounded in the CURRENT screenshot.
- Use skills as procedural references only, never as coordinate templates.
- Before outputting `DONE`, verify that the FULL instruction has been completed, not just a local subgoal.
- If you return Python code, include short `#` comments.

Output format:
- Return ONLY one code block.
- The code block must contain exactly one of:
  1. Python code using `pyautogui`
  2. `WAIT`
  3. `DONE`
  4. `FAIL`
  5. `LOAD_SKILL("<exact_skill_name>")`

The computer password is '{self.client_password}', use it when needed.
You are asked to complete the following task: {instruction}
""".strip()

    def _build_current_user_message(
        self,
        instruction: str,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        extra_feedback: Optional[List[str]] = None,
    ) -> dict:
        previous_steps = self._build_previous_steps_text()
        active_memo_text = self._active_skill_state_text()
        active_skill_name = self._active_skill_state.get("skill_name") if self._active_skill_state else None
        current_step_skills = {item.get("skill_name") for item in self._current_step_planner_summaries}
        if active_skill_name and active_skill_name in current_step_skills:
            active_memo_text = "Covered by the planner notes returned in this step."
        env_feedback_parts = [self._extract_env_feedback(obs)]
        if extra_feedback:
            env_feedback_parts.extend(item for item in extra_feedback if item)
        env_feedback = "\n\n".join(part for part in env_feedback_parts if part and part != "None") or "None"
        text = "\n\n".join(
            [
                "Please generate the next grounded GUI action from the CURRENT screenshot.",
                f"Instruction: {instruction}",
                "Available skills:\n" + self._skills_with_consult_counts_text(),
                "Active planner memo:\n" + active_memo_text,
                "Planner notes returned in this step:\n" + self._current_step_planner_summaries_text(),
                "Environment feedback:\n" + env_feedback,
                "Previous steps (full model responses, including any action comments):\n" + previous_steps,
                self._screen_resolution_prompt(processed_width, processed_height),
                "Rules:\n"
                "- Ground every action in the CURRENT screenshot.\n"
                "- Treat skills as procedural guidance, never as coordinate templates.\n"
                f"- Do not reload a skill after {MAX_BRANCH_SKILL_CONSULTS_PER_SKILL} consults.\n"
                "- If planner notes already exist for this step, use them before consulting again.\n"
                "- If recent actions repeated without progress, change strategy.\n"
                "- Before DONE, verify the full instruction, not just a local subgoal.\n"
                "- If you return Python, include concise `#` comments.",
            ]
        )
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text = text + "\n\nLoop warning:\n" + repetition_warning
        return {
            "role": "user",
            "parts": [
                {"text": text},
                self._image_part(processed_image),
            ],
        }

    def _build_contents(
        self,
        instruction: str,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        extra_feedback: Optional[List[str]] = None,
    ) -> List[dict]:
        return [
            self._build_current_user_message(
                instruction,
                processed_image,
                processed_width,
                processed_height,
                obs,
                extra_feedback,
            )
        ]

    def _build_branch_reference_content(
        self,
        trigger_skill_name: str,
        branch_skill_payloads: List[Tuple[str, Dict]],
    ) -> dict:
        parts: List[dict] = [
            {
                "text": "\n\n".join(
                    [
                        "Skill reference package for this temporary text-only planner branch.",
                        "The materials below are supplemental procedural references only.",
                        f"Requested skill in the main context: LOAD_SKILL(\"{trigger_skill_name}\")",
                        f"Loaded skills in this branch: {', '.join(skill_name for skill_name, _ in branch_skill_payloads) or 'None'}",
                        "The main agent, not this branch, will choose the concrete action.",
                        "Use the skill materials to judge applicability, subgoal, plan, expected state, and completion scope.",
                    ]
                )
            }
        ]
        for skill_name, full_skill in branch_skill_payloads:
            content = full_skill["content"]
            parts.append(
                {
                    "text": (
                        f"# Loaded Skill: {content.name} ({skill_name})\n\n"
                        f"{content.text}"
                    )
                }
            )
        return {"role": "user", "parts": parts}

    def _build_branch_system_message(self, instruction: str, loaded_skill_names: List[str]) -> str:
        loaded = ", ".join(loaded_skill_names) if loaded_skill_names else "None"
        return f"""
You are inside a temporary planner-only text skill consultation branch for a single desktop step.
Your job is NOT to return a GUI action. Your job is to summarize whether the loaded skill is useful for the CURRENT state and what the main agent should optimize for next.

Loaded skills:
{loaded}

Rules:
- Do not return Python code, WAIT, DONE, FAIL, or LOAD_SKILL.
- Use the live screenshot over the skill text when they conflict.
- Use the current screenshot and previous steps to decide whether the skill is effective.
- If the skill is ineffective for the CURRENT state, say so clearly and instruct the main agent to rely on the CURRENT screenshot instead of skill bias.
- If the skill is effective, summarize the current subgoal, the planning guidance, the expected next visible state, and whether the task still needs verification.
- Treat skill text as knowledge/state guidance, NOT as a coordinate template.
- Before implying that the task might be complete, think about whether the main agent should still do a verification action before DONE.

Output format:
- Return ONLY one code block.
- The code block must contain exactly one JSON object with:
  - `"skill_applicability"`: one of `"effective"`, `"ineffective"`, `"uncertain"`
  - `"subgoal"`: a short string
  - `"plan"`: a short string
  - `"expected_state"`: a short string describing visible screenshot cues the main agent should aim for next
  - `"completion_scope"`: one of `"local_only"`, `"needs_verification"`, `"maybe_complete"`

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
        lines = [
            "Please inspect the CURRENT UI screenshot and return planner information only.",
            f"Instruction: {instruction}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Return planner JSON only, not an action.\n"
            "- Treat skill text as knowledge/state references, not coordinate templates.\n"
            "- If the current screenshot conflicts with the skill, trust the current screenshot.\n"
            "- `expected_state` must describe visible screenshot cues, not an abstract goal.\n"
            "- Use `completion_scope` to indicate whether the task is only locally advanced or still needs verification before DONE.",
        ]
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            lines.append("Loop warning:\n" + repetition_warning)
        if round_feedback:
            feedback_lines = "\n".join(f"- {item}" for item in round_feedback if item)
            if feedback_lines:
                lines.append("Additional feedback for this branch round:\n" + feedback_lines)
        return "\n\n".join(lines)

    def _build_branch_contents(
        self,
        instruction: str,
        trigger_skill_name: str,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        branch_skill_payloads: List[Tuple[str, Dict]],
        round_feedback: Optional[List[str]] = None,
    ) -> List[dict]:
        return [
            self._build_branch_reference_content(
                trigger_skill_name=trigger_skill_name,
                branch_skill_payloads=branch_skill_payloads,
            ),
            {
                "role": "user",
                "parts": [
                    {
                        "text": self._build_branch_current_user_text(
                            instruction=instruction,
                            processed_width=processed_width,
                            processed_height=processed_height,
                            obs=obs,
                            round_feedback=round_feedback,
                        )
                    },
                    self._image_part(processed_image),
                ],
            },
        ]

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

    def _load_skill_for_branch(
        self,
        skill_name: str,
        branch_loaded_names: Set[str],
    ) -> Tuple[Optional[Dict], Optional[str]]:
        self._skill_usage_summary["load_skill_calls"] = int(self._skill_usage_summary.get("load_skill_calls", 0)) + 1
        if not skill_name:
            return None, "Missing skill name in LOAD_SKILL(...)."
        if skill_name not in self._task_skill_names:
            return None, f"Unknown skill '{skill_name}'. Use only a skill from the available skill list."
        if skill_name in branch_loaded_names:
            return None, f"Skill '{skill_name}' is already loaded in this branch."
        if self._skill_consult_counts.get(skill_name, 0) >= MAX_BRANCH_SKILL_CONSULTS_PER_SKILL:
            return None, (
                f"Skill '{skill_name}' has already been consulted {MAX_BRANCH_SKILL_CONSULTS_PER_SKILL} times. "
                "Do not load it again."
            )

        full_skill = self._skill_loader.load_full_skill(skill_name)
        if not full_skill:
            return None, f"Failed to load skill '{skill_name}'."

        self._skill_consult_counts[skill_name] = self._skill_consult_counts.get(skill_name, 0) + 1
        self._consulted_branch_skills.add(skill_name)
        self._skill_usage_summary["load_skill_successes"] = int(
            self._skill_usage_summary.get("load_skill_successes", 0)
        ) + 1
        return full_skill, None

    def _append_skill_branch_log(self, payload: Dict[str, Any]):
        self._skill_invocation_log.append(payload)

    def _save_skill_invocation_log(self):
        if not self._result_dir:
            return
        output_path = os.path.join(self._result_dir, "skill_invocations.json")
        payload = {
            "architecture_version": BRANCH_ARCHITECTURE_VERSION,
            "text_skill_mode": self.text_skill_mode,
            "skill_mode": "text_only",
            "task_skill_names": list(self._task_skill_names),
            "invocations": self._skill_invocation_log,
        }
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._runtime_logger().error(
                "[TextSkills/Branch] Failed to save skill_invocations.json: %s",
                str(e),
            )

    def _save_skill_usage_summary(self):
        if not self._result_dir:
            return
        payload = dict(self._skill_usage_summary)
        payload.update(
            {
                "architecture_version": BRANCH_ARCHITECTURE_VERSION,
                "text_skill_mode": self.text_skill_mode,
                "task_skill_names": list(self._task_skill_names),
                "consulted_skill_names": sorted(self._consulted_branch_skills),
                "skill_branch_invocations": len(self._skill_invocation_log),
                "skill_branch_successes": sum(1 for item in self._skill_invocation_log if item.get("success")),
                "skill_consult_counts": dict(self._skill_consult_counts),
                "active_skill_state": dict(self._active_skill_state) if self._active_skill_state else None,
                "steps_recorded": len(self.actions),
                "final_actions": list(self.actions),
            }
        )
        output_path = os.path.join(self._result_dir, "skill_usage_summary.json")
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._runtime_logger().error(
                "[TextSkills/Branch] Failed to save skill_usage_summary.json: %s",
                str(e),
            )

    def _run_skill_branch(
        self,
        instruction: str,
        obs: Dict,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        trigger_skill_name: str,
        step_idx: int,
    ) -> Dict[str, Any]:
        self._skill_invocation_counter += 1
        branch_id = self._skill_invocation_counter
        branch_loaded_names: Set[str] = set()
        branch_skill_payloads: List[Tuple[str, Dict]] = []
        round_feedback: List[str] = []
        branch_rounds: List[Dict[str, Any]] = []
        final_response = ""
        final_summary: Optional[Dict[str, str]] = None
        success = False

        full_skill, load_error = self._load_skill_for_branch(trigger_skill_name, branch_loaded_names)
        if full_skill is not None:
            branch_loaded_names.add(trigger_skill_name)
            branch_skill_payloads.append((trigger_skill_name, full_skill))
        elif load_error:
            round_feedback.append(load_error)
            return {
                "success": False,
                "summary": None,
                "feedback": load_error,
                "log": {
                    "architecture_version": BRANCH_ARCHITECTURE_VERSION,
                    "branch_id": branch_id,
                    "step": step_idx,
                    "success": False,
                    "trigger_skill_name": trigger_skill_name,
                    "loaded_skills": [],
                    "rounds": [],
                    "final_response": "",
                    "final_summary": None,
                    "final_feedback": load_error,
                },
            }

        for round_idx in range(inline_mod.MAX_SKILL_LOAD_ROUNDS):
            system_message = self._build_branch_system_message(instruction, sorted(branch_loaded_names))
            contents = self._build_branch_contents(
                instruction=instruction,
                trigger_skill_name=trigger_skill_name,
                processed_image=processed_image,
                processed_width=processed_width,
                processed_height=processed_height,
                obs=obs,
                branch_skill_payloads=branch_skill_payloads,
                round_feedback=round_feedback,
            )
            self._runtime_logger().info("=" * 80)
            self._runtime_logger().info(
                "[TextSkills/Branch %d] Step %d round %d",
                branch_id,
                step_idx,
                round_idx + 1,
            )
            self._runtime_logger().info("[TextSkills/Branch %d] System message:\n%s", branch_id, system_message)
            self._runtime_logger().info(
                "[TextSkills/Branch %d] Contents:\n%s",
                branch_id,
                self._format_contents_for_log(contents),
            )
            try:
                response = self.call_llm(system_text=system_message, contents=contents)
            except Exception as e:
                self._runtime_logger().error(
                    "[TextSkills/Branch %d] Failed to call model %s: %s",
                    branch_id,
                    self.model,
                    str(e),
                )
                response = ""
            final_response = response or ""
            round_record = {
                "round": round_idx + 1,
                "timestamp": time.time(),
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

        return {
            "success": success,
            "summary": final_summary,
            "feedback": round_feedback[-1] if round_feedback else "Skill branch failed.",
            "log": {
                "architecture_version": BRANCH_ARCHITECTURE_VERSION,
                "branch_id": branch_id,
                "step": step_idx,
                "success": success,
                "trigger_skill_name": trigger_skill_name,
                "loaded_skills": sorted(branch_loaded_names),
                "rounds": branch_rounds,
                "final_response": final_response,
                "final_summary": dict(final_summary) if final_summary else None,
            },
        }

    def predict(self, instruction: str, obs: Dict) -> List:
        self._current_step_planner_summaries = []

        screenshot_bytes = obs["screenshot"]
        image = Image.open(BytesIO(screenshot_bytes))
        original_width, original_height = image.size
        processed_image, processed_width, processed_height = base_agent_mod.process_image(screenshot_bytes)
        system_message = self._build_skill_system_message(instruction)

        round_feedback: List[str] = []
        final_response = ""

        for round_idx in range(inline_mod.MAX_SKILL_LOAD_ROUNDS):
            contents = self._build_contents(
                instruction,
                processed_image,
                processed_width,
                processed_height,
                obs,
                round_feedback,
            )
            self._runtime_logger().info("=" * 80)
            self._runtime_logger().info("[TextSkills/Main] Step %d round %d", len(self.actions), round_idx + 1)
            self._runtime_logger().info("[TextSkills/Main] System message:\n%s", system_message)
            self._runtime_logger().info("[TextSkills/Main] Contents:\n%s", self._format_contents_for_log(contents))
            try:
                response = self.call_llm(system_text=system_message, contents=contents)
            except Exception as e:
                self._runtime_logger().error(
                    "[TextSkills/Main] Failed to call model %s: %s",
                    self.model,
                    str(e),
                )
                response = ""

            final_response = response or ""
            self._runtime_logger().info("[TextSkills/Main] Response: %s", final_response)

            if self.save_conversation_json:
                self._conversation_log.append(
                    {
                        "step": len(self.actions),
                        "round": round_idx + 1,
                        "timestamp": time.time(),
                        "system_message": system_message,
                        "contents": self._serialize_contents_for_json(contents),
                        "response": final_response,
                    }
                )

            bare_skill_name = self._extract_bare_or_inline_load_skill(final_response)
            if self._count_code_blocks(final_response) != 1 and bare_skill_name is None:
                round_feedback.append(
                    "The previous response must contain exactly one code block containing Python, WAIT, DONE, FAIL, or LOAD_SKILL(\"<exact_skill_name>\")."
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
                    trigger_skill_name=skill_name,
                    step_idx=len(self.actions),
                )
                self._append_skill_branch_log(branch_result["log"])
                if branch_result["success"] and branch_result["summary"]:
                    planner_note = self._planner_summary_to_record(skill_name, branch_result["summary"])
                    self._upsert_current_step_planner_summary(planner_note)
                    self._update_active_skill_state(planner_note)
                else:
                    round_feedback.append(branch_result["feedback"])
                continue

            actions = self.parse_actions(
                final_response,
                original_width=original_width,
                original_height=original_height,
                processed_width=processed_width,
                processed_height=processed_height,
            )
            if actions:
                response_to_store = final_response
                if self._current_step_planner_summaries:
                    response_to_store = self._build_planner_augmented_history_response(
                        self._current_step_planner_summaries,
                        final_response,
                        actions,
                    )
                self.screenshots.append(processed_image)
                self.responses.append(response_to_store)
                self.actions.append(" | ".join(actions))
                self._save_skill_usage_summary()
                self._save_skill_invocation_log()
                self._save_conversation_json()
                self._current_step_planner_summaries = []
                return final_response, actions

            round_feedback.append(
                "The previous response did not contain a valid GUI action or LOAD_SKILL call. Output exactly one code block."
            )

        self.screenshots.append(processed_image)
        self.responses.append(final_response or "No valid action")
        self.actions.append("No valid action")
        self._save_skill_usage_summary()
        self._save_skill_invocation_log()
        self._save_conversation_json()
        self._current_step_planner_summaries = []
        return final_response or "No valid action", []


class GeneralTextSkillAgent:
    def __init__(self, *args, text_skill_mode: str = TEXT_SKILL_MODE_INLINE_CONTEXT, **kwargs):
        if text_skill_mode not in TEXT_SKILL_MODE_CHOICES:
            raise ValueError(
                f"text_skill_mode must be one of {sorted(TEXT_SKILL_MODE_CHOICES)}, got: {text_skill_mode}"
            )
        if text_skill_mode == TEXT_SKILL_MODE_INLINE_CONTEXT:
            impl = _InlineContextGeneralTextSkillAgent(
                *args,
                text_skill_mode=text_skill_mode,
                **kwargs,
            )
        else:
            impl = _BranchPlannerGeneralTextSkillAgent(
                *args,
                text_skill_mode=text_skill_mode,
                **kwargs,
            )
        self._impl = impl

    def __getattr__(self, item):
        return getattr(self._impl, item)
