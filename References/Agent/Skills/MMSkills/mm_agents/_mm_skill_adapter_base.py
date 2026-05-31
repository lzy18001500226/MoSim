import ast
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from mm_agents import general_agent as base_agent_mod
from mm_agents import _mm_skill_state_cards as v4mod
from mm_agents import _mm_skill_long_plan as v6mod


ARCHITECTURE_VERSION = "mm_skill_expiring_active_memo_sanitized_history"
MAIN_STATE_BUNDLE_PREVIEW_LIMIT = 3
MAX_STATE_VIEW_SELECTION_ROUNDS = 4
MAX_STAGE1_SELECTED_STATES = 3
MAX_STAGE1_SELECTED_VIEWS = 6
ACTIVE_PLANNER_MEMO_TTL_STEPS = 5
PYAUTOGUI_CALL_PATTERN = re.compile(r"pyautogui\.[A-Za-z_][A-Za-z0-9_]*\([^)\n]*\)")

PLANNER_HISTORY_META_COMMENT_PREFIXES = (
    "# One or more skill planners were consulted in this same interaction step.",
    "# The concrete action below was chosen by the main agent from the CURRENT screenshot and previous steps.",
    "# Consulted planner skill:",
    "# Skill applicability:",
    "# Planner subgoal:",
    "# Planner summary:",
    "# Expected state:",
    "# Completion scope:",
    "# Skill consult count:",
)


class _PromptCoordinateTransformer(ast.NodeTransformer):
    COORD_FUNCS = {
        "click",
        "rightClick",
        "middleClick",
        "doubleClick",
        "moveTo",
        "dragTo",
        "moveRel",
        "dragRel",
    }

    def __init__(
        self,
        coordinate_type: str,
        original_width: int | None,
        original_height: int | None,
        processed_width: int | None,
        processed_height: int | None,
    ) -> None:
        self.coordinate_type = coordinate_type
        self.original_width = original_width
        self.original_height = original_height
        self.processed_width = processed_width
        self.processed_height = processed_height

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)

        func_name = self._get_func_name(node.func)
        if func_name not in self.COORD_FUNCS:
            return node

        if func_name in {"moveRel", "dragRel"}:
            return node

        positional_pairs = {
            "click": (0, 1),
            "rightClick": (0, 1),
            "middleClick": (0, 1),
            "doubleClick": (0, 1),
            "moveTo": (0, 1),
            "dragTo": (0, 1),
        }
        x_idx, y_idx = positional_pairs.get(func_name, (None, None))

        if x_idx is not None and len(node.args) > x_idx:
            node.args[x_idx] = self._transform_coord(node.args[x_idx], axis="x")
        if y_idx is not None and len(node.args) > y_idx:
            node.args[y_idx] = self._transform_coord(node.args[y_idx], axis="y")

        for keyword in node.keywords:
            if keyword.arg == "x":
                keyword.value = self._transform_coord(keyword.value, axis="x")
            elif keyword.arg == "y":
                keyword.value = self._transform_coord(keyword.value, axis="y")

        return node

    @staticmethod
    def _get_func_name(func: ast.expr) -> str | None:
        if isinstance(func, ast.Attribute):
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
        return None

    def _transform_coord(self, node: ast.expr, axis: str) -> ast.expr:
        value = self._get_numeric_value(node)
        if value is None:
            return node

        normalized = self._normalize(value, axis=axis)
        return ast.copy_location(ast.Constant(value=normalized), node)

    @staticmethod
    def _get_numeric_value(node: ast.expr) -> float | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            inner = _PromptCoordinateTransformer._get_numeric_value(node.operand)
            return -inner if inner is not None else None
        return None

    def _normalize(self, value: float, axis: str) -> int:
        original_dimension = self.original_width if axis == "x" else self.original_height
        if not original_dimension:
            return int(round(value))

        if self.coordinate_type == "relative":
            limit = base_agent_mod.RELATIVE_COORDINATE_MAX
            scaled = value * limit / original_dimension
            return max(0, min(int(round(scaled)), limit))

        processed_dimension = self.processed_width if axis == "x" else self.processed_height
        if not processed_dimension:
            return max(0, min(int(round(value)), original_dimension - 1))

        scaled = value * processed_dimension / original_dimension
        return max(0, min(int(round(scaled)), processed_dimension - 1))

PLANNER_STAGE2_EXAMPLES: List[Dict[str, object]] = [
    {
        "name": "Spreadsheet selection correction",
        "stage1": [
            {
                "state_id": "selected_header_merge_span",
                "views": ["focus_crop"],
                "reason": (
                    "The live sheet selection looks too wide for the requested merged header, "
                    "so I want a local reference for the correct span before planning the fix."
                ),
            }
        ],
        "planner_json": {
            "skill_applicability": "effective",
            "subgoal": "select the correct range A1:C1 for the first header",
            "plan": (
                "The current selection A1:D1 is incorrect for the first header. I will re-select exactly A1:C1, then "
                "use the 'Merge and Center Cells' toolbar button to create the first header block. After merging, I "
                "will type 'Investment Summary'. I will then repeat this selection and merge process for the second "
                "row: A2:B2 for 'High Interest Rate' and C2:D2 for 'Low Interest Rate'. I will verify each merge "
                "result on the worksheet before moving to the next range."
            ),
            "expected_state": "Cells A1:C1 are highlighted as a single selection, excluding column D.",
            "completion_scope": "local_only",
        },
    },
    {
        "name": "Writer menu-path planning",
        "stage1": [
            {
                "state_id": "apply_case_transforms_capitalize_command",
                "views": ["full_frame"],
                "reason": (
                    "The text is already selected. I need a menu-path reference for the case-transform command rather "
                    "than another action guess from memory."
                ),
            }
        ],
        "planner_json": {
            "skill_applicability": "effective",
            "subgoal": "open the Format menu to access text case transformation options",
            "plan": (
                "With the document text already selected, click the 'Format' menu in the top toolbar. From there, "
                "navigate to the 'Text' submenu and select 'Capitalize Every Word' as shown in the skill reference. "
                "Once clicked, verify that the first letter of each word in the document body has changed to uppercase "
                "while the rest of the letters remain in their current case or change to lowercase as per standard "
                "title-casing behavior."
            ),
            "expected_state": "The 'Format' menu is open, revealing the 'Text' submenu and the 'Capitalize Every Word' option.",
            "completion_scope": "local_only",
        },
    },
]


class _MMSkillAdapterBase(v6mod._MMSkillLongPlanAgent):
    """
    V8 preserves V7's two-stage multi-view bundle flow, while making two
    prompt-surface changes only:
    - Active planner memos expire after a fixed number of subsequent steps.
    - Previous-step history strips planner meta-comments but keeps the action comment/code.
    - Stage 1 selects state IDs plus explicit view types from runtime state bundles.
    - Stage 2 sees the stage-1 selection record, the loaded views, and then emits the
      same planner JSON schema used by V6.
    """

    def _empty_skill_usage_summary(self) -> Dict[str, object]:
        payload = super()._empty_skill_usage_summary()
        payload.update(
            {
                "architecture_version": ARCHITECTURE_VERSION,
                "load_state_view_calls": 0,
                "load_state_view_successes": 0,
                "selected_state_views_per_skill": {},
                "total_selected_state_views": 0,
            }
        )
        payload.pop("load_skill_image_calls", None)
        payload.pop("load_skill_image_successes", None)
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
            self._runtime_logger().error("[Skills/V7] Failed to save skill_invocations.json: %s", str(e))

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
        payload.pop("load_skill_image_calls", None)
        payload.pop("load_skill_image_successes", None)
        output_path = os.path.join(self._result_dir, "skill_usage_summary.json")
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._runtime_logger().error("[Skills/V7] Failed to save skill_usage_summary.json: %s", str(e))

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

            preview = "(no state-bundle preview)"
            if self._skill_loader is not None:
                state_bundles = self._skill_loader.load_state_bundles(skill_name, runtime=True)
                if state_bundles is not None:
                    preview = self._skill_loader.summarize_state_bundles_for_preview(
                        state_bundles,
                        max_states=MAIN_STATE_BUNDLE_PREVIEW_LIMIT,
                    )
                else:
                    state_cards = self._skill_loader.load_state_cards(skill_name, runtime=True)
                    preview = self._skill_loader.summarize_state_cards_for_preview(
                        state_cards,
                        max_cards=MAIN_STATE_BUNDLE_PREVIEW_LIMIT,
                    )
            lines.append("\n".join([header, preview]))
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
                f"- Consult count: {state.get('consult_count', 0)}/{v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL}",
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

    def _build_previous_steps_text(self) -> str:
        current_step = len(self.responses)
        history_start = max(0, current_step - self.max_trajectory_length)
        history_responses = self.responses[history_start:current_step]
        if not history_responses:
            return "None"
        return "\n\n".join(
            [
                f"Step {history_start + idx + 1} full response:\n{self._sanitize_previous_step_response(response or 'No valid action')}"
                for idx, response in enumerate(history_responses)
            ]
        )

    def _normalize_feedback_call_to_prompt_space(
        self,
        call_text: str,
        *,
        original_width: int,
        original_height: int,
        processed_width: int,
        processed_height: int,
    ) -> str:
        try:
            tree = ast.parse(call_text)
            transformer = _PromptCoordinateTransformer(
                coordinate_type=self.coordinate_type,
                original_width=original_width,
                original_height=original_height,
                processed_width=processed_width,
                processed_height=processed_height,
            )
            tree = transformer.visit(tree)
            ast.fix_missing_locations(tree)
            return ast.unparse(tree).strip()
        except Exception:
            return call_text

    def _normalized_branch_env_feedback(
        self,
        obs: Dict,
        *,
        original_width: int,
        original_height: int,
        processed_width: int,
        processed_height: int,
    ) -> str:
        env_feedback = self._extract_env_feedback(obs)
        if not env_feedback or env_feedback == "None":
            return "None"

        def replace_call(match: re.Match[str]) -> str:
            return self._normalize_feedback_call_to_prompt_space(
                match.group(0),
                original_width=original_width,
                original_height=original_height,
                processed_width=processed_width,
                processed_height=processed_height,
            )

        return PYAUTOGUI_CALL_PATTERN.sub(replace_call, env_feedback)

    def _build_main_system_message(self, instruction: str) -> str:
        available_skills = self._skills_with_consult_counts_text(include_state_previews=False)
        return f"""
Follow the instruction to perform desktop computer tasks.
You control the computer using Python code with `pyautogui`.

For each step, you will receive the current screenshot and the recent visible trajectory history.
Use the screenshot to decide the next action. Do not assume that previous clicks succeeded.
If an earlier action failed, adjust based on the CURRENT screenshot instead of repeating the same guess.

Task skills are optional procedural planners only.
- The final user message includes each skill's short description plus compact runtime state-bundle previews. Use those previews to judge whether a skill is genuinely relevant BEFORE calling `LOAD_SKILL(...)`.
- Call `LOAD_SKILL("<exact_skill_name>")` only when the CURRENT screenshot, recent steps, and the skill previews suggest that extra procedural guidance is likely useful.
- `LOAD_SKILL(...)` opens a temporary planner branch for extra skill-guided reasoning. It does NOT execute the action for you.
- Skill previews and planner notes are references only. They are never coordinate templates.
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
            "Available skills for this task (descriptions + compact runtime state-bundle previews):\n"
            + self._skills_with_consult_counts_text(include_state_previews=True),
            "Active planner memo:\n" + active_memo_text,
            "Planner notes returned in this step:\n" + self._current_step_planner_summaries_text(),
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Ground every action in the CURRENT screenshot.\n"
            "- Planner notes are fallible references only. They may still be incomplete or partially wrong for the live UI.\n"
            "- Re-decide the real action from the CURRENT screenshot, full recent history, and execution feedback before acting.\n"
            "- Treat state-bundle previews, selected reference views, and planner notes as references only, never as coordinate templates.\n"
            f"- Do not reload a skill after {v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL} consults.\n"
            "- Use the runtime state-bundle previews to avoid misloading unrelated skills.\n"
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

    def _build_branch_skill_reference_parts(self, skill_name: str, skill_bundle: Dict[str, Any]) -> List[dict]:
        content = skill_bundle["content"]
        runtime_state_bundles = skill_bundle.get("runtime_state_bundles")
        runtime_state_cards = skill_bundle.get("runtime_state_cards")
        parts: List[dict] = [
            {
                "text": (
                    f"# Branch Skill Reference: {content.name} ({skill_name})\n\n"
                    "Treat the material below as supplemental procedural knowledge only.\n"
                    "Use it to understand workflow stages, state cues, likely subgoals, and success/failure signals.\n"
                    "Do NOT treat the text or state bundles as coordinate templates.\n"
                    "The CURRENT screenshot remains authoritative for concrete GUI actions.\n\n"
                    f"{content.text}"
                )
            }
        ]
        if self._skill_loader is not None:
            if runtime_state_bundles is not None:
                parts.append({"text": self._skill_loader.format_state_bundles_for_branch(runtime_state_bundles)})
            elif runtime_state_cards is not None:
                parts.append({"text": self._skill_loader.format_state_cards_for_branch(runtime_state_cards)})
        return parts

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
                        "Stage 1 must decide which specific state IDs and view types are worth loading.",
                        "A single state may request multiple complementary views when that helps comparison or transition reasoning.",
                        "The main agent, not this branch, will choose the concrete GUI action.",
                    ]
                )
            }
        ]
        for skill_name, skill_bundle in branch_skill_payloads:
            parts.extend(self._build_branch_skill_reference_parts(skill_name, skill_bundle))
        return {"role": "user", "parts": parts}

    @staticmethod
    def _flatten_selection_view_ids(selections: List[Any]) -> List[str]:
        flattened: List[str] = []
        for selection in selections:
            state_id = selection.state.state_id
            for loaded_view in selection.loaded_views:
                flattened.append(f"{state_id}/{loaded_view.view.view_type}")
        return flattened

    @staticmethod
    def _flatten_selection_image_paths(selections: List[Any]) -> List[str]:
        flattened: List[str] = []
        for selection in selections:
            for loaded_view in selection.loaded_views:
                flattened.append(loaded_view.view.image_path)
        return flattened

    def _build_selected_state_view_reference_content(
        self,
        skill_name: str,
        selected_selections: List[Any],
    ) -> Optional[dict]:
        if not selected_selections:
            return None

        parts: List[dict] = [
            {
                "text": (
                    "Stage-1 selection record for this branch.\n"
                    "Use the requested states, requested view types, and selection reasons as part of the planner evidence.\n"
                    "The loaded reference views below are supplemental references only. They are never coordinate templates."
                )
            }
        ]
        for selection in selected_selections:
            requested_view_text = ", ".join(selection.requested_view_types) if selection.requested_view_types else "None"
            parts.append(
                {
                    "text": "\n".join(
                        [
                            f"[Stage-1 Selection - {skill_name}/{selection.state.state_id}]",
                            f"stage: {selection.state.stage or '(unknown)'}",
                            f"requested_views: {requested_view_text}",
                            f"reason: {selection.reason or '(none provided)'}",
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

    def _build_branch_view_selection_system_message(self, instruction: str, loaded_skill_names: List[str]) -> str:
        loaded_skills = ", ".join(loaded_skill_names) if loaded_skill_names else "None"
        return f"""
You are inside a temporary state-view selection branch for a single desktop step.
Your job is to decide whether any specific state bundles and view types are worth loading before planner reasoning.

Branch rules:
- Do NOT return Python code, planner JSON, WAIT, DONE, FAIL, LOAD_SKILL, or LOAD_SKILL_IMAGE.
- The CURRENT screenshot is authoritative.
- The skill text and runtime state bundles are already available. Use them to judge whether any concrete state views are likely to reduce ambiguity.
- Load state views only when the CURRENT screenshot appears close enough to one or more state bundles that the reference views will help.
- If the current screenshot is clearly far from the referenced states, or the bundles already provide enough information, request no views.
- Use exact `state_id` and exact `view_type` values from the provided state bundles.
- You may request multiple views from the same state if those views help compare global context, local targets, or before/after transitions.
- Keep the request minimal: at most {MAX_STAGE1_SELECTED_STATES} states and at most {MAX_STAGE1_SELECTED_VIEWS} total views.

Currently loaded branch skills:
{loaded_skills}

Output format:
- Return ONLY one code block.
- The code block must contain exactly one `LOAD_STATE_VIEWS([...])` call.
- The payload must be a JSON list of objects. Each object must contain:
  - `"state_id"`: an exact state ID from the bundle manifest
  - `"views"`: a non-empty list of exact view types for that state
  - `"reason"`: one short sentence explaining why those views are needed
- The list may be empty.
- Do not return prose outside the code block.

Correct example with state views:
```python
LOAD_STATE_VIEWS([
  {{
    "state_id": "rename_sheet_dialog_open",
    "views": ["full_frame", "focus_crop"],
    "reason": "I need both the modal-level context and the focused input field before planning the rename flow."
  }}
])
```

Correct example without state views:
```python
LOAD_STATE_VIEWS([])
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
            "Please inspect the CURRENT UI screenshot and decide whether any specific state views are worth loading.",
            f"Instruction: {instruction}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            "Environment feedback from the previous step:\n" + env_feedback,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Return `LOAD_STATE_VIEWS([...])` only.\n"
            "- The list may be empty when the runtime state bundles already suffice or the screenshot is too different.\n"
            f"- Select at most {MAX_STAGE1_SELECTED_STATES} states and at most {MAX_STAGE1_SELECTED_VIEWS} total views.\n"
            "- You may request multiple views from the same state when they are complementary.\n"
            "- Prefer exact `state_id` and `view_type` values from the runtime state bundles.\n"
            "- Do not request reference views that mainly duplicate one another without adding new evidence.\n"
            "- Do not assume that a visually similar state is helpful if the bundle's `when_not_to_use` or `visual_risk` warns against it.",
        ]
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text_sections.append("Loop warning:\n" + repetition_warning)
        if round_feedback:
            feedback_lines = "\n".join(f"- {item}" for item in round_feedback if item)
            if feedback_lines:
                text_sections.append("Additional feedback for this state-view selection round:\n" + feedback_lines)
        return "\n\n".join(text_sections)

    def _build_branch_view_selection_contents(
        self,
        instruction: str,
        trigger_skill_name: str,
        main_trigger_response: str,
        processed_image: str,
        original_width: int,
        original_height: int,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        branch_skill_payloads: List[Tuple[str, Dict[str, Any]]],
        round_feedback: Optional[List[str]] = None,
    ) -> List[dict]:
        contents: List[dict] = []
        contents.append(
            self._build_branch_reference_content(
                trigger_skill_name=trigger_skill_name,
                main_trigger_response=main_trigger_response,
                branch_skill_payloads=branch_skill_payloads,
            )
        )
        contents.append(
            {
                "role": "user",
                "parts": [
                    {
                        "text": self._build_branch_view_selection_user_text(
                            instruction=instruction,
                            original_width=original_width,
                            original_height=original_height,
                            processed_width=processed_width,
                            processed_height=processed_height,
                            obs=obs,
                            round_feedback=round_feedback,
                        )
                    },
                    self._image_part(processed_image),
                ],
            }
        )
        return contents

    def _planner_stage2_examples_text(self) -> str:
        chunks: List[str] = ["High-quality planner examples:"]
        for idx, example in enumerate(PLANNER_STAGE2_EXAMPLES, start=1):
            stage1_json = json.dumps(example["stage1"], ensure_ascii=False, indent=2)
            planner_json = json.dumps(example["planner_json"], ensure_ascii=False, indent=2)
            chunks.extend(
                [
                    f"Example {idx}: {example['name']}",
                    "Stage-1 selection record:",
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
You are inside a temporary planner-only skill consultation branch for a single desktop step.
Your job is NOT to return a GUI action. Your job is to return a structured planner summary for the CURRENT state.

Branch rules:
- Do not return Python code, WAIT, DONE, FAIL, LOAD_SKILL, LOAD_SKILL_IMAGE, or LOAD_STATE_VIEWS.
- Do not request another skill in this branch.
- The main agent will choose the real GUI action after reading your planner summary.
- Use the CURRENT screenshot first. Skill text, runtime state bundles, the stage-1 selection record, and any loaded reference views are supplemental references only.
- The stage-1 selection record tells you which states and view types were requested and why. Treat that record as part of the reasoning context instead of ignoring it.
- If a skill is ineffective for the CURRENT state, say so clearly and avoid forcing the plan toward the skill.
- Treat any loaded reference views as state references, never as coordinate templates.
- `subgoal` must be the next immediate local milestone for the user instruction under the CURRENT state.
- Keep `subgoal` short, local, and near-term.
- `plan` must be the longer-range instruction-solving route for the CURRENT state after integrating the loaded skill materials, the stage-1 selection record, the selected reference views, and the CURRENT screenshot.
- `plan` must not collapse into the same content as `subgoal`.
- `plan` must identify the currently relevant UI surface or control area, the next 2 to 4 key actions, checks, or transitions that matter, and the visible cue that means advance versus re-plan.
- Strong planners correct mismatched current state before continuing the skill flow. If the live UI is not yet at the expected local state, say what must be corrected first.
- When multiple views from the same state were loaded, use them jointly if they provide complementary evidence such as global context, local focus, or a transition/verification cue.
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

Correct minimal example:
```json
{{
  "skill_applicability": "effective",
  "subgoal": "open the settings surface that exposes the requested control",
  "plan": "stay on the currently visible settings path, operate the row or submenu that should reveal the requested control, then verify the control itself becomes visible before editing it. If the click opens an unrelated panel or the expected control still does not appear, stop following the skill pattern and re-plan from the live UI instead of repeating blindly.",
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
        if selected_selections:
            selected_text = ", ".join(self._flatten_selection_view_ids(selected_selections))
        else:
            selected_text = "None"
        text_sections = [
            "Please inspect the CURRENT UI screenshot and return planner JSON only.",
            "The screenshot attached BELOW this instruction is the true live environment state. It is more authoritative than any loaded skill reference view, and the next grounded action must ultimately follow that live screenshot.",
            f"Instruction: {instruction}",
            f"Selected state views for this branch: {selected_text}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            "Environment feedback from the previous step:\n" + env_feedback,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Keep the planner grounded in the CURRENT screenshot.\n"
            "- Use the loaded skill only for the specific procedural knowledge that matters now.\n"
            "- Use the stage-1 selection record as evidence about why these references were loaded.\n"
            "- `subgoal` should stay local and immediate: the next small milestone under the live UI.\n"
            "- `plan` should be the longer-range behavior route for solving the user instruction from the CURRENT state after incorporating the loaded skill materials and selected reference views.\n"
            "- `plan` should cover the currently relevant UI surface, the next 2 to 4 key actions/checks or transitions, and what visible cue means advance versus re-plan.\n"
            "- Do not let `plan` collapse into the same content as `subgoal`.\n"
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

    def _build_branch_planner_contents(
        self,
        instruction: str,
        trigger_skill_name: str,
        main_trigger_response: str,
        processed_image: str,
        original_width: int,
        original_height: int,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        branch_skill_payloads: List[Tuple[str, Dict[str, Any]]],
        selected_selections: List[Any],
        round_feedback: Optional[List[str]] = None,
    ) -> List[dict]:
        contents: List[dict] = []
        reference_content = self._build_branch_reference_content(
            trigger_skill_name=trigger_skill_name,
            main_trigger_response=main_trigger_response,
            branch_skill_payloads=branch_skill_payloads,
        )
        selected_content = self._build_selected_state_view_reference_content(
            trigger_skill_name,
            selected_selections,
        )
        if selected_content is not None:
            reference_content["parts"].extend(selected_content["parts"])
        contents.append(reference_content)
        contents.append(
            {
                "role": "user",
                "parts": [
                    {
                        "text": self._build_branch_planner_user_text(
                            instruction=instruction,
                            original_width=original_width,
                            original_height=original_height,
                            processed_width=processed_width,
                            processed_height=processed_height,
                            obs=obs,
                            selected_selections=selected_selections,
                            round_feedback=round_feedback,
                        )
                    },
                    self._image_part(processed_image),
                ],
            }
        )
        return contents

    def _load_skill_for_branch(
        self,
        skill_name: str,
        branch_loaded_names: Set[str],
    ) -> Tuple[Optional[Dict[str, Any]], int, Optional[str]]:
        self._skill_usage_summary["load_skill_calls"] = int(self._skill_usage_summary.get("load_skill_calls", 0)) + 1
        if not skill_name:
            return None, 0, "Missing skill name in LOAD_SKILL(...)."
        if skill_name not in self._task_skill_names:
            return None, 0, f"Unknown skill '{skill_name}'. Use only a skill from the available skill list."
        if skill_name in branch_loaded_names:
            return None, 0, f"Skill '{skill_name}' is already loaded in this branch. Do not reload it inside the same branch."
        if self._skill_consult_counts.get(skill_name, 0) >= v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL:
            return (
                None,
                0,
                f"Skill '{skill_name}' has already been consulted {v4mod.v3mod.MAX_SKILL_CONSULTS_PER_SKILL} times in this trajectory. "
                "Do not load it again. Continue with grounded GUI interaction using the CURRENT screenshot and previous steps.",
            )

        skill_content = self._skill_loader.load_skill_content(skill_name)
        if not skill_content:
            return None, 0, f"Failed to load skill text for '{skill_name}'."

        runtime_state_bundles = self._skill_loader.load_state_bundles(skill_name, runtime=True)
        runtime_state_cards = None
        if runtime_state_bundles is None:
            runtime_state_cards = self._skill_loader.load_state_cards(skill_name, runtime=True)
            if runtime_state_cards is None:
                runtime_state_cards = self._skill_loader.load_state_cards(skill_name, runtime=False)

        self._skill_consult_counts[skill_name] = self._skill_consult_counts.get(skill_name, 0) + 1
        self._record_consulted_skill(skill_name, 0)
        return {
            "content": skill_content,
            "runtime_state_bundles": runtime_state_bundles,
            "runtime_state_cards": runtime_state_cards,
        }, 0, None

    def _record_selected_branch_state_views(self, skill_name: str, selected_selections: List[Any]) -> None:
        images_per_skill = dict(self._skill_usage_summary.get("images_per_skill", {}))
        selected_state_views_per_skill = dict(self._skill_usage_summary.get("selected_state_views_per_skill", {}))
        selected_count = sum(len(selection.loaded_views) for selection in selected_selections)
        if selected_count > 0:
            images_per_skill[skill_name] = images_per_skill.get(skill_name, 0) + selected_count
            selected_state_views_per_skill[skill_name] = (
                selected_state_views_per_skill.get(skill_name, 0) + selected_count
            )
        total_selected = sum(selected_state_views_per_skill.values())
        self._skill_usage_summary.update(
            {
                "images_per_skill": images_per_skill,
                "selected_state_views_per_skill": selected_state_views_per_skill,
                "total_loaded_images": sum(images_per_skill.values()),
                "total_selected_state_views": total_selected,
            }
        )

    def _extract_load_state_views_request(
        self,
        response: str,
    ) -> Tuple[Optional[List[Dict[str, object]]], Optional[str]]:
        if not response:
            return None, "The branch returned an empty state-view selection response."

        code_body: Optional[str]
        if self._count_code_blocks(response) == 1:
            code_body = self._extract_first_code_block_text(response)
        elif self._count_code_blocks(response) == 0:
            code_body = self._normalize_non_codeblock_response(response)
        else:
            return None, "The state-view selection response must contain exactly one code block with LOAD_STATE_VIEWS([...])."

        if not code_body:
            return None, "The state-view selection response code block was empty."

        raw_lines = [line.rstrip() for line in code_body.splitlines() if line.strip()]
        stripped_lines = [line.strip() for line in raw_lines if not line.strip().startswith("#")]
        normalized = "\n".join(stripped_lines).strip()
        match = re.fullmatch(r"LOAD_STATE_VIEWS\((.*)\)\s*;?", normalized, re.DOTALL)
        if not match:
            return None, "The state-view selection response must be a LOAD_STATE_VIEWS([...]) call."

        payload = match.group(1).strip()
        if not payload:
            return [], None

        try:
            parsed = json.loads(payload)
        except Exception as exc:
            return None, f"LOAD_STATE_VIEWS(...) must contain a valid JSON list. Parse error: {exc}"
        if not isinstance(parsed, list):
            return None, "LOAD_STATE_VIEWS(...) must contain a JSON list of objects."

        merged: Dict[str, Dict[str, object]] = {}
        total_view_count = 0
        for item in parsed:
            if not isinstance(item, dict):
                return None, "Each LOAD_STATE_VIEWS(...) item must be a JSON object."
            state_id = str(item.get("state_id", "") or "").strip()
            if not state_id:
                return None, "Each LOAD_STATE_VIEWS(...) item must include a non-empty `state_id`."
            raw_views = item.get("views", [])
            if not isinstance(raw_views, list):
                return None, f"`views` for state '{state_id}' must be a list of strings."
            deduped_views: List[str] = []
            for raw_view in raw_views:
                view_type = str(raw_view).strip()
                if not view_type:
                    continue
                if view_type not in deduped_views:
                    deduped_views.append(view_type)
            if not deduped_views:
                return None, f"`views` for state '{state_id}' must contain at least one non-empty view type."

            reason = str(item.get("reason", "") or "").strip()
            existing = merged.get(state_id)
            if existing is None:
                merged[state_id] = {
                    "state_id": state_id,
                    "views": deduped_views,
                    "reason": reason,
                }
            else:
                existing_views = list(existing.get("views", []))
                for view_type in deduped_views:
                    if view_type not in existing_views:
                        existing_views.append(view_type)
                existing["views"] = existing_views
                if reason and not str(existing.get("reason", "") or "").strip():
                    existing["reason"] = reason

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
        return normalized_items, None

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

        branch_skill_payloads: List[Tuple[str, Dict[str, Any]]] = []
        branch_loaded_names: Set[str] = set()
        branch_rounds: List[dict] = []
        stage1_feedback: List[str] = []
        planner_feedback: List[str] = []
        selected_state_view_requests: List[Dict[str, object]] = []
        selected_selections: List[Any] = []
        final_response = ""
        final_summary: Optional[Dict[str, str]] = None
        success = False

        full_skill, _, load_error = self._load_skill_for_branch(trigger_skill_name, branch_loaded_names)
        if full_skill is None:
            branch_log = {
                "architecture_version": ARCHITECTURE_VERSION,
                "branch_id": branch_id,
                "step": step_idx,
                "skill_mode": self.skill_mode,
                "trigger_skill_name": trigger_skill_name,
                "main_trigger_response": main_trigger_response,
                "success": False,
                "loaded_skills": [],
                "selected_state_view_requests": [],
                "selected_state_view_ids": [],
                "selected_state_view_paths": [],
                "selected_state_view_count": 0,
                "rounds": [],
                "final_response": "",
                "final_summary": None,
                "final_feedback": load_error or "Failed to load the requested skill.",
            }
            return {
                "success": False,
                "response": "",
                "summary": None,
                "feedback": load_error or "Failed to load the requested skill.",
                "log": branch_log,
            }

        branch_loaded_names.add(trigger_skill_name)
        branch_skill_payloads.append((trigger_skill_name, full_skill))

        if self.skill_mode == "multimodal":
            for round_idx in range(MAX_STATE_VIEW_SELECTION_ROUNDS):
                system_message = self._build_branch_view_selection_system_message(
                    instruction,
                    sorted(branch_loaded_names),
                )
                contents = self._build_branch_view_selection_contents(
                    instruction=instruction,
                    trigger_skill_name=trigger_skill_name,
                    main_trigger_response=main_trigger_response,
                    processed_image=processed_image,
                    original_width=original_width,
                    original_height=original_height,
                    processed_width=processed_width,
                    processed_height=processed_height,
                    obs=obs,
                    branch_skill_payloads=branch_skill_payloads,
                    round_feedback=stage1_feedback,
                )
                self._runtime_logger().info("=" * 80)
                self._runtime_logger().info(
                    "[MMSkill/V7][Branch %d] Step %d state-view selection round %d",
                    branch_id,
                    step_idx,
                    round_idx + 1,
                )
                self._runtime_logger().info("[MMSkill/V7][Branch %d] System message:\n%s", branch_id, system_message)
                self._runtime_logger().info(
                    "[MMSkill/V7][Branch %d] Contents:\n%s",
                    branch_id,
                    self._format_contents_for_log(contents),
                )

                try:
                    response = self.call_llm(system_text=system_message, contents=contents)
                except Exception as e:
                    self._runtime_logger().error(
                        "[MMSkill/V7][Branch %d] Failed during state-view selection: %s",
                        branch_id,
                        str(e),
                    )
                    response = ""

                final_response = response or ""
                requested_items, parse_error = self._extract_load_state_views_request(final_response)
                round_record = {
                    "stage": "state_view_selection",
                    "round": round_idx + 1,
                    "timestamp": time.time(),
                    "loaded_skills_before_response": sorted(branch_loaded_names),
                    "system_message": system_message,
                    "contents": self._serialize_contents_for_json(contents),
                    "response": final_response,
                }
                if parse_error:
                    stage1_feedback.append(parse_error)
                    round_record["status"] = "invalid_state_view_selection"
                    round_record["error"] = parse_error
                    branch_rounds.append(round_record)
                    continue

                selected_state_view_requests = list(requested_items or [])
                self._skill_usage_summary["load_state_view_calls"] = int(
                    self._skill_usage_summary.get("load_state_view_calls", 0)
                ) + 1
                selected_selections, missing_items = self._skill_loader.load_selected_state_views(
                    trigger_skill_name,
                    selected_state_view_requests,
                    runtime=True,
                )
                round_record["requested_state_view_requests"] = list(selected_state_view_requests)
                round_record["selected_state_view_ids"] = self._flatten_selection_view_ids(selected_selections)
                round_record["selected_state_view_paths"] = self._flatten_selection_image_paths(selected_selections)
                round_record["missing_state_views"] = list(missing_items)
                if missing_items:
                    stage1_feedback.append(
                        "Some requested state IDs or view types could not be resolved. Use exact `state_id` and `view_type` values from the runtime state bundles."
                    )
                    round_record["status"] = "state_view_selection_missing_identifiers"
                    branch_rounds.append(round_record)
                    selected_selections = []
                    continue

                self._skill_usage_summary["load_state_view_successes"] = int(
                    self._skill_usage_summary.get("load_state_view_successes", 0)
                ) + 1
                self._record_selected_branch_state_views(trigger_skill_name, selected_selections)
                round_record["status"] = "state_view_selection_returned"
                round_record["selected_state_view_count"] = len(self._flatten_selection_view_ids(selected_selections))
                branch_rounds.append(round_record)
                break
            else:
                branch_log = {
                    "architecture_version": ARCHITECTURE_VERSION,
                    "branch_id": branch_id,
                    "step": step_idx,
                    "skill_mode": self.skill_mode,
                    "trigger_skill_name": trigger_skill_name,
                    "main_trigger_response": main_trigger_response,
                    "success": False,
                    "loaded_skills": sorted(branch_loaded_names),
                    "selected_state_view_requests": selected_state_view_requests,
                    "selected_state_view_ids": self._flatten_selection_view_ids(selected_selections),
                    "selected_state_view_paths": self._flatten_selection_image_paths(selected_selections),
                    "selected_state_view_count": len(self._flatten_selection_view_ids(selected_selections)),
                    "rounds": branch_rounds,
                    "final_response": final_response,
                    "final_summary": None,
                    "final_feedback": stage1_feedback[-1] if stage1_feedback else "State-view selection stage failed.",
                }
                return {
                    "success": False,
                    "response": final_response,
                    "summary": None,
                    "feedback": stage1_feedback[-1] if stage1_feedback else "State-view selection stage failed.",
                    "log": branch_log,
                }

        for round_idx in range(v4mod.v3mod.v2mod.MAX_SKILL_LOAD_ROUNDS):
            system_message = self._build_branch_planner_system_message(
                instruction,
                sorted(branch_loaded_names),
            )
            contents = self._build_branch_planner_contents(
                instruction=instruction,
                trigger_skill_name=trigger_skill_name,
                main_trigger_response=main_trigger_response,
                processed_image=processed_image,
                original_width=original_width,
                original_height=original_height,
                processed_width=processed_width,
                processed_height=processed_height,
                obs=obs,
                branch_skill_payloads=branch_skill_payloads,
                selected_selections=selected_selections,
                round_feedback=planner_feedback,
            )

            self._runtime_logger().info("=" * 80)
            self._runtime_logger().info(
                "[MMSkill/V7][Branch %d] Step %d planner round %d",
                branch_id,
                step_idx,
                round_idx + 1,
            )
            self._runtime_logger().info("[MMSkill/V7][Branch %d] System message:\n%s", branch_id, system_message)
            self._runtime_logger().info(
                "[MMSkill/V7][Branch %d] Contents:\n%s",
                branch_id,
                self._format_contents_for_log(contents),
            )

            try:
                response = self.call_llm(system_text=system_message, contents=contents)
            except Exception as e:
                self._runtime_logger().error(
                    "[MMSkill/V7][Branch %d] Failed during planner stage: %s",
                    branch_id,
                    str(e),
                )
                response = ""

            final_response = response or ""
            summary, parse_error = self._extract_planner_summary(final_response)
            round_record = {
                "stage": "planner",
                "round": round_idx + 1,
                "timestamp": time.time(),
                "loaded_skills_before_response": sorted(branch_loaded_names),
                "selected_state_view_requests": list(selected_state_view_requests),
                "selected_state_view_ids": self._flatten_selection_view_ids(selected_selections),
                "system_message": system_message,
                "contents": self._serialize_contents_for_json(contents),
                "response": final_response,
            }
            if parse_error:
                planner_feedback.append(parse_error)
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
            "selected_state_view_requests": list(selected_state_view_requests),
            "selected_state_view_ids": self._flatten_selection_view_ids(selected_selections),
            "selected_state_view_paths": self._flatten_selection_image_paths(selected_selections),
            "selected_state_view_count": len(self._flatten_selection_view_ids(selected_selections)),
            "rounds": branch_rounds,
            "final_response": final_response,
            "final_summary": dict(final_summary) if final_summary else None,
            "final_feedback": planner_feedback[-1] if planner_feedback else None,
        }
        return {
            "success": success,
            "response": final_response,
            "summary": final_summary,
            "feedback": planner_feedback[-1] if planner_feedback else "Skill planner branch did not produce a valid summary.",
            "log": branch_log,
        }
