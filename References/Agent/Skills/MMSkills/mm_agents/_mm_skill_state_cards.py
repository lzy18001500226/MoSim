import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from mm_agents import _mm_skill_planner as v3mod


ARCHITECTURE_VERSION = "mm_skill_state_cards_selective_images"
MAX_IMAGE_SELECTION_ROUNDS = 4
STATE_CARD_PREVIEW_LIMIT = 3


class _MMSkillStateCardsAgent(v3mod._MMSkillPlannerAgent):
    """
    Multimodal-optimized MMSkills agent.

    Compared with v3:
    - Skill selection in the main prompt is informed by compact runtime state-card previews.
    - Branches first receive SKILL.md text plus structured runtime state cards instead of raw images.
    - A branch must explicitly choose whether to load any reference images via LOAD_SKILL_IMAGE([...]).
    - Only the selected images are injected before the planner summary stage.
    """

    def _empty_skill_usage_summary(self) -> Dict[str, object]:
        payload = super()._empty_skill_usage_summary()
        payload.update(
            {
                "architecture_version": ARCHITECTURE_VERSION,
                "load_skill_image_calls": 0,
                "load_skill_image_successes": 0,
                "selected_images_per_skill": {},
                "total_selected_branch_images": 0,
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

    def _append_skill_branch_log(self, branch_log: dict):
        self._skill_invocation_log.append(branch_log)
        self._conversation_log.append(
            {
                "entry_type": "skill_branch",
                **branch_log,
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
            self._runtime_logger().error("[Skills/V4] Failed to save skill_invocations.json: %s", str(e))

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
                "max_skill_consults_per_skill": v3mod.MAX_SKILL_CONSULTS_PER_SKILL,
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
            self._runtime_logger().error("[Skills/V4] Failed to save skill_usage_summary.json: %s", str(e))

    def _skills_with_consult_counts_text(self, *, include_state_previews: bool = True) -> str:
        if not self._task_skill_names:
            return "None"
        lines: List[str] = []
        meta_map = {Path(meta.directory).name: meta for meta in self._task_skill_metadatas}
        for skill_name in self._task_skill_names:
            meta = meta_map.get(skill_name)
            description = ((meta.description or "").strip() if meta is not None else "") or "(no description)"
            consult_count = self._skill_consult_counts.get(skill_name, 0)
            header = f"- {skill_name} — {description} [consulted {consult_count}/{v3mod.MAX_SKILL_CONSULTS_PER_SKILL}]"
            if not include_state_previews:
                lines.append(header)
                continue
            state_cards = self._skill_loader.load_state_cards(skill_name, runtime=True) if self._skill_loader else None
            preview = (
                self._skill_loader.summarize_state_cards_for_preview(
                    state_cards,
                    max_cards=STATE_CARD_PREVIEW_LIMIT,
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
- The final user message includes each skill's short description plus compact runtime state-card previews. Use those previews to judge whether a skill is genuinely relevant BEFORE calling `LOAD_SKILL(...)`.
- Call `LOAD_SKILL("<exact_skill_name>")` only when the CURRENT screenshot, previous steps, and the skill previews indicate that extra procedural guidance is likely useful.
- `LOAD_SKILL(...)` opens a temporary planner branch. It does NOT execute the action for you.
- Inside the branch, you will first see SKILL.md text and structured runtime state cards. You may then choose whether to load any concrete skill images with `LOAD_SKILL_IMAGE([...])`.
- Only load concrete skill images when the current screenshot appears close enough to one or more state cards that the actual reference image is likely to reduce ambiguity. If the current screenshot is far from the card states, loading no images is better.
- Skill text, state cards, and selected images are all references only. They never override the CURRENT screenshot.
- Each skill may be consulted at most {v3mod.MAX_SKILL_CONSULTS_PER_SKILL} times in the same trajectory.

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
            "Available skills for this task (descriptions + compact runtime state-card previews):\n"
            + self._skills_with_consult_counts_text(include_state_previews=True),
            "Active planner memo:\n" + active_memo_text,
            "Planner notes returned in this step:\n" + self._current_step_planner_summaries_text(),
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Ground every action in the CURRENT screenshot.\n"
            "- Treat skills, state cards, and skill images as state guidance, never as coordinate templates.\n"
            f"- Do not reload a skill after {v3mod.MAX_SKILL_CONSULTS_PER_SKILL} consults.\n"
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

    def _build_branch_skill_reference_parts(self, skill_name: str, skill_bundle: Dict[str, Any]) -> List[dict]:
        content = skill_bundle["content"]
        runtime_state_cards = skill_bundle.get("runtime_state_cards")
        parts: List[dict] = [
            {
                "text": (
                    f"# Branch Skill Reference: {content.name} ({skill_name})\n\n"
                    "Treat the material below as supplemental procedural knowledge only.\n"
                    "Use it to understand workflow stages, state cues, likely subgoals, and success/failure signals.\n"
                    "Do NOT treat the text or state cards as coordinate templates.\n"
                    "The CURRENT screenshot remains authoritative for concrete GUI actions.\n\n"
                    f"{content.text}"
                )
            }
        ]
        if self._skill_loader is not None:
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
                        "The branch first decides whether any specific skill images are worth loading.",
                        "State cards already describe what each reference image is for and when it should NOT be used.",
                        "The main agent, not this branch, will choose the concrete GUI action.",
                    ]
                )
            }
        ]
        for skill_name, skill_bundle in branch_skill_payloads:
            parts.extend(self._build_branch_skill_reference_parts(skill_name, skill_bundle))
        return {"role": "user", "parts": parts}

    def _build_selected_image_reference_content(
        self,
        skill_name: str,
        selected_cards: List[Any],
        selected_images: List[Tuple[str, str, str]],
    ) -> Optional[dict]:
        if not selected_cards or not selected_images:
            return None
        parts: List[dict] = [
            {
                "text": (
                    "Selected visual references requested via LOAD_SKILL_IMAGE(...).\n"
                    "Use them only to disambiguate current UI state. They are never coordinate templates."
                )
            }
        ]
        for card, (filename, b64_data, mime_type) in zip(selected_cards, selected_images):
            selector = card.image_id or card.state_id or Path(card.image_path).stem
            cues = ", ".join(card.visible_cues[:4]) if card.visible_cues else "(no visible cues listed)"
            parts.append(
                {
                    "text": "\n".join(
                        [
                            f"[Selected Skill Image - {skill_name}/{selector} -> {filename}]",
                            f"stage: {card.stage or '(unknown)'}",
                            f"image_role: {card.image_role or '(unknown)'}",
                            f"visible_cues: {cues}",
                            f"verification_cue: {card.verification_cue or card.recommended_verification or '(none listed)'}",
                            f"visual_risk: {card.visual_risk or '; '.join(card.non_transferable_parts[:2]) or '(none listed)'}",
                        ]
                    )
                }
            )
            parts.append({"inlineData": {"mimeType": mime_type, "data": b64_data}})
        return {"role": "user", "parts": parts}

    def _build_branch_image_selection_system_message(self, instruction: str, loaded_skill_names: List[str]) -> str:
        loaded_skills = ", ".join(loaded_skill_names) if loaded_skill_names else "None"
        return f"""
You are inside a temporary image-selection branch for a single desktop step.
Your job is to decide whether any specific skill reference images are worth loading before planner reasoning.

Branch rules:
- Do NOT return Python code, planner JSON, WAIT, DONE, FAIL, or LOAD_SKILL.
- The CURRENT screenshot is authoritative.
- The skill text and runtime state cards are already available. Use them to judge whether any concrete images are likely to reduce ambiguity.
- Load images only when the CURRENT screenshot appears close enough to one or more state cards that the image will help.
- If the current screenshot is clearly far from the referenced states, or the cards already provide enough information, request no images.
- Use exact image identifiers from the provided state cards whenever possible.
- Treat the previous-step responses as compact trajectory context. Do not expect extra historical screenshots in this branch.

Currently loaded branch skills:
{loaded_skills}

Output format:
- Return ONLY one code block.
- The code block must contain exactly one `LOAD_SKILL_IMAGE([...])` call.
- If you select one or more images, include one concise `# Reason:` comment immediately above the call explaining what ambiguity those images should resolve.
- The list may be empty.
- Use a JSON string list inside the parentheses.
- Do not return prose outside the code block.

Correct example with images:
```python
# Reason: The current screenshot looks close to the background-fill settings surface and I need the exact modal reference.
LOAD_SKILL_IMAGE(["open_settings_surface", "confirm_dialog_ready"])
```

Correct example without images:
```python
LOAD_SKILL_IMAGE([])
```

The computer password is '{self.client_password}', use it when needed.
You are asked to complete the following task: {instruction}
""".strip()

    def _build_branch_image_selection_user_text(
        self,
        instruction: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        round_feedback: Optional[List[str]] = None,
    ) -> str:
        previous_steps = self._build_previous_steps_text()
        text_sections = [
            "Please inspect the CURRENT UI screenshot and decide whether any specific skill images are worth loading.",
            f"Instruction: {instruction}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            "Environment feedback from the previous step:\n" + self._extract_env_feedback(obs),
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Return `LOAD_SKILL_IMAGE([...])` only.\n"
            "- If you request one or more images, include one concise `# Reason:` comment in the same code block explaining why those images are needed.\n"
            "- The list may be empty when the runtime state cards already suffice or the screenshot is too different.\n"
            "- Select only the minimum number of images likely to materially disambiguate the CURRENT state.\n"
            "- Prefer exact `image_id` values from the runtime state cards.\n"
            "- Do not assume that a visually similar image is helpful if the state card's `when_not_to_use` or `visual_risk` warns against it.",
        ]
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text_sections.append("Loop warning:\n" + repetition_warning)
        if round_feedback:
            feedback_lines = "\n".join(f"- {item}" for item in round_feedback if item)
            if feedback_lines:
                text_sections.append("Additional feedback for this image-selection round:\n" + feedback_lines)
        return "\n\n".join(text_sections)

    def _build_branch_planner_system_message(self, instruction: str, loaded_skill_names: List[str]) -> str:
        loaded_skills = ", ".join(loaded_skill_names) if loaded_skill_names else "None"
        return f"""
You are inside a temporary planner-only skill consultation branch for a single desktop step.
Your job is NOT to return a GUI action. Your job is to summarize whether the loaded skill is useful for the CURRENT state and what the main agent should optimize for next.

Branch rules:
- Do not return Python code, WAIT, DONE, FAIL, LOAD_SKILL, or LOAD_SKILL_IMAGE.
- Do not request another skill in this branch.
- The main agent will choose the concrete GUI action after reading your planner summary.
- Use the current screenshot and previous-step responses to decide whether the skill is effective.
- Structured runtime state cards and any selected reference images are supplemental references only. They never override the CURRENT screenshot.
- If the skill is ineffective for the CURRENT state, say so clearly and instruct the main agent to rely on the CURRENT screenshot instead of skill bias.
- If the skill is effective, summarize only the instruction-relevant subgoal and the minimal transferable guidance that should change the next grounded action.
- Treat any selected skill images as state/knowledge references, NOT as coordinate templates.
- Before implying that the task might be complete, think about whether the main agent should still do a verification action before DONE.
- `subgoal` must describe the next immediate milestone toward the USER instruction, not a generic skill stage.
- `plan` must be concise and concrete. It should distill the core procedural knowledge gained from the loaded skill materials and adapt it to the CURRENT screenshot and previous-step responses in 1-2 short sentences. It must focus on the instruction-relevant knowledge that should guide the next grounded action, and must not restate irrelevant skill content or copy example-specific details from the skill materials.
- `expected_state` must describe the next visible screenshot cues the main agent should aim to reveal after following the plan. It must be something the main agent can verify from the live UI, not an abstract or idealized end state.
- `completion_scope` must be judged against the full USER instruction. Use `local_only` when the branch only advances a local step, `needs_verification` when the task may be close but still needs a visible check, and `maybe_complete` only when the current state suggests the full instruction could already be satisfied after one grounded verification step.

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
  "subgoal": "reach the correct settings surface for the requested option",
  "plan": "stay grounded in the current dialog flow and avoid reopening an already-visible surface",
  "expected_state": "The requested settings control is visible and ready to edit",
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
            "Please inspect the CURRENT UI screenshot and return planner information only.",
            f"Instruction: {instruction}",
            f"Selected skill images for this branch: {selected_text}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            "Environment feedback from the previous step:\n" + self._extract_env_feedback(obs),
            self._screen_resolution_prompt(processed_width, processed_height),
            "Rules:\n"
            "- Return planner JSON only, not an action.\n"
            "- Treat skill text, runtime state cards, and selected images as knowledge/state references, not coordinate templates.\n"
            "- If the current screenshot conflicts with a skill reference, trust the current screenshot.\n"
            "- `subgoal` must be the next immediate milestone for the user instruction under the CURRENT state, not a generic restatement of the skill.\n"
            "- `plan` should capture the core procedural knowledge provided by the loaded skill materials and explain how that knowledge should guide the next grounded step under the CURRENT screenshot and recent responses.\n"
            "- Do not let the skill bias you toward hidden dialogs, example text, or example UI states that are not visible now.\n"
            "- `expected_state` must describe visible screenshot cues, not an abstract goal.\n"
            "- Use `completion_scope` to indicate whether the task is only locally advanced or still needs verification before DONE.",
        ]
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text_sections.append("Loop warning:\n" + repetition_warning)
        if round_feedback:
            feedback_lines = "\n".join(f"- {item}" for item in round_feedback if item)
            if feedback_lines:
                text_sections.append("Additional feedback for this planner round:\n" + feedback_lines)
        return "\n\n".join(text_sections)

    def _build_branch_image_selection_contents(
        self,
        instruction: str,
        trigger_skill_name: str,
        main_trigger_response: str,
        processed_image: str,
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
                        "text": self._build_branch_image_selection_user_text(
                            instruction=instruction,
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

    def _build_branch_planner_contents(
        self,
        instruction: str,
        trigger_skill_name: str,
        main_trigger_response: str,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        branch_skill_payloads: List[Tuple[str, Dict[str, Any]]],
        selected_cards: List[Any],
        selected_images: List[Tuple[str, str, str]],
        round_feedback: Optional[List[str]] = None,
    ) -> List[dict]:
        contents: List[dict] = []
        reference_content = self._build_branch_reference_content(
            trigger_skill_name=trigger_skill_name,
            main_trigger_response=main_trigger_response,
            branch_skill_payloads=branch_skill_payloads,
        )
        selected_content = self._build_selected_image_reference_content(
            trigger_skill_name,
            selected_cards,
            selected_images,
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
                            processed_width=processed_width,
                            processed_height=processed_height,
                            obs=obs,
                            selected_cards=selected_cards,
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
        if self._skill_consult_counts.get(skill_name, 0) >= v3mod.MAX_SKILL_CONSULTS_PER_SKILL:
            return (
                None,
                0,
                f"Skill '{skill_name}' has already been consulted {v3mod.MAX_SKILL_CONSULTS_PER_SKILL} times in this trajectory. "
                "Do not load it again. Continue with grounded GUI interaction using the CURRENT screenshot and previous steps.",
            )

        skill_content = self._skill_loader.load_skill_content(skill_name)
        if not skill_content:
            return None, 0, f"Failed to load skill text for '{skill_name}'."

        runtime_state_cards = self._skill_loader.load_state_cards(skill_name, runtime=True)
        if runtime_state_cards is None:
            runtime_state_cards = self._skill_loader.load_state_cards(skill_name, runtime=False)

        self._skill_consult_counts[skill_name] = self._skill_consult_counts.get(skill_name, 0) + 1
        self._record_consulted_skill(skill_name, 0)
        return {
            "content": skill_content,
            "runtime_state_cards": runtime_state_cards,
        }, 0, None

    def _record_selected_branch_images(self, skill_name: str, selected_cards: List[Any]) -> None:
        images_per_skill = dict(self._skill_usage_summary.get("images_per_skill", {}))
        selected_images_per_skill = dict(self._skill_usage_summary.get("selected_images_per_skill", {}))
        selected_count = len(selected_cards)
        if selected_count > 0:
            images_per_skill[skill_name] = images_per_skill.get(skill_name, 0) + selected_count
            selected_images_per_skill[skill_name] = selected_images_per_skill.get(skill_name, 0) + selected_count
        total_selected = sum(selected_images_per_skill.values())
        self._skill_usage_summary.update(
            {
                "images_per_skill": images_per_skill,
                "selected_images_per_skill": selected_images_per_skill,
                "total_loaded_images": sum(images_per_skill.values()),
                "total_selected_branch_images": total_selected,
            }
        )

    def _extract_load_skill_image_request(
        self, response: str
    ) -> Tuple[Optional[List[str]], Optional[str], Optional[str]]:
        if not response:
            return None, None, "The branch returned an empty image-selection response."

        code_body: Optional[str]
        if self._count_code_blocks(response) == 1:
            code_body = self._extract_first_code_block_text(response)
        elif self._count_code_blocks(response) == 0:
            code_body = self._normalize_non_codeblock_response(response)
        else:
            return None, None, "The image-selection response must contain exactly one code block with LOAD_SKILL_IMAGE([...])."

        if not code_body:
            return None, None, "The image-selection response code block was empty."

        raw_lines = [line.rstrip() for line in code_body.splitlines() if line.strip()]
        reason_lines = [line.strip()[1:].strip() for line in raw_lines if line.strip().startswith("#")]
        reason_text = " ".join(line for line in reason_lines if line).strip() or None
        stripped_lines = [
            line.strip()
            for line in raw_lines
            if line.strip() and not line.strip().startswith("#")
        ]
        normalized = "\n".join(stripped_lines).strip()
        match = re.fullmatch(r"LOAD_SKILL_IMAGE\((.*)\)\s*;?", normalized, re.DOTALL)
        if not match:
            return None, reason_text, "The image-selection response must be a LOAD_SKILL_IMAGE([...]) call."

        payload = match.group(1).strip()
        if not payload:
            return [], reason_text, None

        requested: List[str] = []
        if payload.startswith("["):
            try:
                parsed = json.loads(payload)
            except Exception as exc:
                return None, reason_text, f"LOAD_SKILL_IMAGE(...) must contain a valid JSON string list. Parse error: {exc}"
            if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
                return None, reason_text, "LOAD_SKILL_IMAGE(...) must contain a JSON list of strings."
            requested = [item.strip() for item in parsed if item.strip()]
        else:
            requested = [item.strip() for item in re.findall(r"""['"]([^'"]+)['"]""", payload) if item.strip()]
            if payload and not requested:
                return None, reason_text, "LOAD_SKILL_IMAGE(...) must contain either a JSON list of strings or quoted string arguments."

        deduped: List[str] = []
        for item in requested:
            if item not in deduped:
                deduped.append(item)
        return deduped, reason_text, None

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
        del original_width, original_height  # The branch is planner-only and does not emit concrete coordinates.

        self._skill_invocation_counter += 1
        branch_id = self._skill_invocation_counter

        branch_skill_payloads: List[Tuple[str, Dict[str, Any]]] = []
        branch_loaded_names: Set[str] = set()
        branch_rounds: List[dict] = []
        round_feedback: List[str] = []
        selected_cards: List[Any] = []
        selected_images: List[Tuple[str, str, str]] = []
        selected_image_requests: List[str] = []
        selected_image_reason: Optional[str] = None
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
                "selected_image_requests": [],
                "selected_image_count": 0,
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

        selection_feedback: List[str] = []
        if self.skill_mode == "multimodal":
            for round_idx in range(MAX_IMAGE_SELECTION_ROUNDS):
                system_message = self._build_branch_image_selection_system_message(
                    instruction,
                    sorted(branch_loaded_names),
                )
                contents = self._build_branch_image_selection_contents(
                    instruction=instruction,
                    trigger_skill_name=trigger_skill_name,
                    main_trigger_response=main_trigger_response,
                    processed_image=processed_image,
                    processed_width=processed_width,
                    processed_height=processed_height,
                    obs=obs,
                    branch_skill_payloads=branch_skill_payloads,
                    round_feedback=selection_feedback,
                )
                self._runtime_logger().info("=" * 80)
                self._runtime_logger().info(
                    "[MMSkill/V4][Branch %d] Step %d image-selection round %d",
                    branch_id,
                    step_idx,
                    round_idx + 1,
                )
                self._runtime_logger().info("[MMSkill/V4][Branch %d] System message:\n%s", branch_id, system_message)
                self._runtime_logger().info(
                    "[MMSkill/V4][Branch %d] Contents:\n%s",
                    branch_id,
                    self._format_contents_for_log(contents),
                )

                try:
                    response = self.call_llm(system_text=system_message, contents=contents)
                except Exception as e:
                    self._runtime_logger().error(
                        "[MMSkill/V4][Branch %d] Failed during image selection: %s",
                        branch_id,
                        str(e),
                    )
                    response = ""

                final_response = response or ""
                requested_images, selected_image_reason, parse_error = self._extract_load_skill_image_request(final_response)
                round_record = {
                    "stage": "image_selection",
                    "round": round_idx + 1,
                    "timestamp": time.time(),
                    "loaded_skills_before_response": sorted(branch_loaded_names),
                    "system_message": system_message,
                    "contents": self._serialize_contents_for_json(contents),
                    "response": final_response,
                }
                if parse_error:
                    selection_feedback.append(parse_error)
                    round_record["status"] = "invalid_image_selection"
                    round_record["error"] = parse_error
                    branch_rounds.append(round_record)
                    continue

                selected_image_requests = list(requested_images or [])
                self._skill_usage_summary["load_skill_image_calls"] = int(
                    self._skill_usage_summary.get("load_skill_image_calls", 0)
                ) + 1
                selected_cards, selected_images, missing_images = self._skill_loader.load_selected_skill_images(
                    trigger_skill_name,
                    selected_image_requests,
                    runtime=True,
                )
                round_record["requested_image_ids"] = list(selected_image_requests)
                round_record["selection_reason"] = selected_image_reason
                round_record["selected_image_ids"] = [card.image_id or card.state_id for card in selected_cards]
                round_record["selected_image_paths"] = [card.image_path for card in selected_cards]
                round_record["missing_images"] = list(missing_images)
                if missing_images:
                    selection_feedback.append(
                        "Some requested image identifiers could not be resolved. Use exact image_id values from the runtime state cards."
                    )
                    round_record["status"] = "image_selection_missing_identifiers"
                    branch_rounds.append(round_record)
                    selected_cards = []
                    selected_images = []
                    continue

                self._skill_usage_summary["load_skill_image_successes"] = int(
                    self._skill_usage_summary.get("load_skill_image_successes", 0)
                ) + 1
                self._record_selected_branch_images(trigger_skill_name, selected_cards)
                round_record["status"] = "image_selection_returned"
                round_record["selected_image_count"] = len(selected_cards)
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
                    "selected_image_requests": selected_image_requests,
                    "selected_image_reason": selected_image_reason,
                    "selected_image_count": len(selected_cards),
                    "rounds": branch_rounds,
                    "final_response": final_response,
                    "final_summary": None,
                    "final_feedback": selection_feedback[-1] if selection_feedback else "Image-selection stage failed.",
                }
                return {
                    "success": False,
                    "response": final_response,
                    "summary": None,
                    "feedback": selection_feedback[-1] if selection_feedback else "Image-selection stage failed.",
                    "log": branch_log,
                }

        planner_feedback: List[str] = []
        for round_idx in range(v3mod.v2mod.MAX_SKILL_LOAD_ROUNDS):
            system_message = self._build_branch_planner_system_message(
                instruction,
                sorted(branch_loaded_names),
            )
            contents = self._build_branch_planner_contents(
                instruction=instruction,
                trigger_skill_name=trigger_skill_name,
                main_trigger_response=main_trigger_response,
                processed_image=processed_image,
                processed_width=processed_width,
                processed_height=processed_height,
                obs=obs,
                branch_skill_payloads=branch_skill_payloads,
                selected_cards=selected_cards,
                selected_images=selected_images,
                round_feedback=planner_feedback,
            )

            self._runtime_logger().info("=" * 80)
            self._runtime_logger().info(
                "[MMSkill/V4][Branch %d] Step %d planner round %d",
                branch_id,
                step_idx,
                round_idx + 1,
            )
            self._runtime_logger().info("[MMSkill/V4][Branch %d] System message:\n%s", branch_id, system_message)
            self._runtime_logger().info(
                "[MMSkill/V4][Branch %d] Contents:\n%s",
                branch_id,
                self._format_contents_for_log(contents),
            )

            try:
                response = self.call_llm(system_text=system_message, contents=contents)
            except Exception as e:
                self._runtime_logger().error(
                    "[MMSkill/V4][Branch %d] Failed during planner stage: %s",
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
                "selected_image_ids": [card.image_id or card.state_id for card in selected_cards],
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
            "selected_image_requests": list(selected_image_requests),
            "selected_image_reason": selected_image_reason,
            "selected_image_ids": [card.image_id or card.state_id for card in selected_cards],
            "selected_image_paths": [card.image_path for card in selected_cards],
            "selected_image_count": len(selected_cards),
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
