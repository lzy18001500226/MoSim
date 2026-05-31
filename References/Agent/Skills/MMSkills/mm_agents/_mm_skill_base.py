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


MAX_SKILL_LOAD_ROUNDS = 8
ARCHITECTURE_VERSION = "mm_skill_base_contextual_history"


class _MMSkillBaseAgent(base_agent_mod.GeneralAgent):
    """
    MMSkill agent with branch-based skill consultation.

    Key design points:
    - The main trajectory history stores a step-level response that remains visible to
      later turns, including skill usage when a temporary branch was consulted.
    - A `LOAD_SKILL(...)` response opens a temporary branch prompt that receives the
      current state plus the requested skill materials.
    - Skill text/images never persist in the main dialogue history.
    - Every branch prompt/response round is logged for auditability.
    """

    def __init__(
        self,
        *args,
        skill_mode: str = "text_only",
        skills_library_dir: str = "skills_library",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        assert skill_mode in {"text_only", "multimodal"}, "skill_mode must be text_only or multimodal"
        self.skill_mode = skill_mode
        self.skills_library_dir = skills_library_dir
        self._skill_loader = None
        self._task_skill_names: List[str] = []
        self._task_skill_metadatas = []
        self._consulted_skills: Set[str] = set()
        self._skill_usage_summary: Dict[str, object] = {}
        self._skill_invocation_log: List[dict] = []
        self._skill_invocation_counter = 0

    def _runtime_logger(self):
        return base_agent_mod.logger if base_agent_mod.logger is not None else logging.getLogger(
            "desktopenv.mm_skill_base"
        )

    def _init_skill_loader(self):
        if self._skill_loader is None:
            from mm_agents.skill_loader import SkillLoader

            self._skill_loader = SkillLoader(skills_library_dir=self.skills_library_dir)
            self._runtime_logger().info("[Skills/V2] SkillLoader initialized with library: %s", self.skills_library_dir)

    def _empty_skill_usage_summary(self) -> Dict[str, object]:
        return {
            "architecture_version": ARCHITECTURE_VERSION,
            "skill_mode": self.skill_mode,
            "task_skill_names": list(self._task_skill_names),
            "loaded_skill_names": [],
            "consulted_skill_names": [],
            "total_loaded_skills": 0,
            "total_loaded_images": 0,
            "images_per_skill": {},
            "load_skill_calls": 0,
            "load_skill_successes": 0,
            "skill_branch_invocations": 0,
            "skill_branch_successes": 0,
        }

    def reset(self, _logger=None, vm_ip=None, **kwargs):
        runtime_logger = _logger if _logger is not None else logging.getLogger("desktopenv.mm_skill_base")
        super().reset(_logger=runtime_logger, vm_ip=vm_ip, **kwargs)
        self._task_skill_names = []
        self._task_skill_metadatas = []
        self._consulted_skills = set()
        self._skill_usage_summary = self._empty_skill_usage_summary()
        self._skill_invocation_log = []
        self._skill_invocation_counter = 0

    def set_task_skills(self, skill_names: List[str]):
        self._init_skill_loader()
        self._task_skill_names = list(skill_names or [])
        all_metadata = self._skill_loader.discover_all_skills()
        meta_map = {Path(meta.directory).name: meta for meta in all_metadata}
        self._task_skill_metadatas = [meta_map[name] for name in self._task_skill_names if name in meta_map]
        self._consulted_skills = set()
        self._skill_usage_summary = self._empty_skill_usage_summary()
        self._runtime_logger().info("[Skills/V2] MMSkill task skills resolved: %s", self._task_skill_names)

    def _available_skills_text(self) -> str:
        lines = [
            f"- {Path(meta.directory).name}: {(meta.description or '').strip() or '(no description)'}"
            for meta in self._task_skill_metadatas
        ]
        return "\n".join(lines) if lines else "- None"

    def _consulted_skills_text(self) -> str:
        if not self._consulted_skills:
            return "None"
        return ", ".join(sorted(self._consulted_skills))

    @staticmethod
    def _extract_first_code_block_text(response: str) -> Optional[str]:
        if not response:
            return None
        matches = re.findall(r"```(?:\w+\s+)?(.*?)```", response, re.DOTALL)
        if len(matches) != 1:
            return None
        return matches[0].strip()

    def _build_previous_steps_text(self) -> str:
        current_step = len(self.responses)
        history_start = max(0, current_step - self.max_trajectory_length)
        history_responses = self.responses[history_start:current_step]
        if not history_responses:
            return "None"
        return "\n\n".join(
            [
                f"Step {history_start + idx + 1} full response:\n{response or 'No valid action'}"
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

    def _build_skill_step_history_response(
        self,
        skill_name: str,
        branch_response: str,
        actions: List[str],
    ) -> str:
        code_body = self._extract_first_code_block_text(branch_response)
        if code_body is None:
            code_body = "\n".join(actions) if actions else (branch_response.strip() or "FAIL")

        code_lines = [line.rstrip() for line in code_body.splitlines()]
        has_comment = any(line.strip().startswith("#") for line in code_lines if line.strip())

        header_lines = [
            f"# Loaded procedural reference skill: {skill_name}",
            "# The skill was used only as workflow guidance.",
            "# The action below is chosen from the current screenshot and previous steps.",
        ]
        if has_comment:
            final_code = "\n".join(header_lines + code_lines)
        else:
            final_code = "\n".join(
                header_lines
                + [
                    "# Execute the next immediate grounded action shown below.",
                    code_body,
                ]
            )
        return f"```python\n{final_code}\n```"

    def _build_main_system_message(self, instruction: str) -> str:
        available_skills = self._available_skills_text()
        return f"""
Follow the instruction to perform desktop computer tasks.
You control the computer using Python code with `pyautogui`.

For each step, you will receive the current screenshot and the recent visible trajectory history.
Use the screenshot to decide the next action. Do not assume that previous clicks succeeded.
If an earlier action failed, adjust based on the CURRENT screenshot instead of repeating the same guess.

Task skills are optional references only.
- Skills are external procedural references, not default actions. Call `LOAD_SKILL(...)` only when the next step genuinely needs extra workflow knowledge, settings-path knowledge, or other procedural guidance that is not already clear from the current screenshot and previous steps.
- A skill never overrides the current screenshot, previous steps, environment feedback, or task instruction. Treat skill contents as workflow guidance only.
- Skills are references, not scripts to replay. After loading a skill, decide the concrete action from the CURRENT screenshot and recent history.
- When you need a skill, output `LOAD_SKILL("<exact_skill_name>")`. That request opens a temporary branch prompt using the current state plus the skill's complete contents.
- The main trajectory history will record which skill was loaded and the resulting final action for that step.
- Skill contents are not kept in the main context after the branch ends. If you need the same skill again later, request it again.

Available skills for this task:
{available_skills}

Important rules:
- Use `pyautogui` only for GUI actions.
- Do NOT use `pyautogui.locateCenterOnScreen`.
- Do NOT use `pyautogui.screenshot()`.
- Each response must be self-contained; do not rely on variables from previous steps.
- When a click does not work, revise the target based on the new screenshot.
- Prefer short, direct actions over long speculative scripts.
- Strictly avoid repetitive, unproductive action loops. If recent steps already tried the same action sequence without progress, choose a meaningfully different grounded action instead of repeating it.

Output format:
- Return ONLY one code block.
- The code block must contain exactly one of the following:
  1. Python code using `pyautogui` (this code may contain multiple sequential `pyautogui` statements for the same immediate step)
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

Incorrect skill request example:
LOAD_SKILL("Example_Skill_Name")

Correct Python action example:
```python
# Open the relevant settings page so I can change the requested option.
pyautogui.hotkey('ctrl', 'l')
pyautogui.write('chrome://settings')
pyautogui.press('enter')
```

Special codes:
- ```WAIT``` when the UI is still loading.
- ```DONE``` when the task is complete.
- ```FAIL``` only when the task is truly impossible.

Coordinate system:
- When the prompt says the screen resolution is 1000x1000, use that normalized coordinate space in your `pyautogui` calls.
- When the prompt says the screen resolution is WxH, use that exact resolution.

The computer password is '{self.client_password}', use it when needed.
You are asked to complete the following task: {instruction}
""".strip()

    def _build_branch_system_message(self, instruction: str, loaded_skill_names: List[str]) -> str:
        loaded_skills = ", ".join(loaded_skill_names) if loaded_skill_names else "None"
        return f"""
You are inside a temporary skill-consultation branch for a single desktop step.
Your job is to produce the next immediate action sequence only.

The loaded skills are supplemental references, not ground truth.
- This branch must not request another skill. Nested `LOAD_SKILL(...)` is forbidden.
- The loaded skills are procedural references only. They help reduce guessing, but they never override the current screenshot, previous steps, or task instruction.
- Use the loaded skills together with the current state to choose the next action sequence. Do not blindly replay a skill.
- If the current state conflicts with a skill description, trust the current state.
- If the currently loaded skill is incomplete or insufficient, still return the best next immediate action from the available evidence.
- Strictly avoid repetitive, unproductive action loops. If recent steps already tried the same action sequence without progress, choose a meaningfully different grounded action.

Currently loaded branch skills:
{loaded_skills}

Output format:
- Return ONLY one code block.
- The code block must contain exactly one of the following:
  1. Python code using `pyautogui` (this code may contain multiple sequential `pyautogui` statements for the same immediate step)
  2. `WAIT`
  3. `DONE`
  4. `FAIL`
- Do not return prose outside the code block.
- Do not request any additional skill in this branch.
- If you return Python code, include concise `#` comments that explain the purpose of the step or sub-step.

Correct Python action example:
```python
# Open the relevant menu so I can continue the requested workflow.
pyautogui.click(120, 54)
```

The computer password is '{self.client_password}', use it when needed.
You are asked to complete the following task: {instruction}
""".strip()

    def _extract_load_skill(self, response: str) -> Optional[str]:
        if not response:
            return None
        match = re.search(r"LOAD_SKILL\(\s*['\"]([^'\"]+)['\"]\s*\)", response)
        if not match:
            return None
        return match.group(1).strip() or None

    def _extract_bare_load_skill(self, response: str) -> Optional[str]:
        if not response:
            return None
        if self._count_code_blocks(response) != 0:
            return None
        stripped = self._normalize_non_codeblock_response(response)
        match = re.fullmatch(r'LOAD_SKILL\(\s*[\'"]([^\'"]+)[\'"]\s*\)\s*;?', stripped)
        if not match:
            return None
        return match.group(1).strip() or None

    def _count_code_blocks(self, response: str) -> int:
        return len(re.findall(r"```.*?```", response, re.DOTALL))

    def _build_main_user_text(
        self,
        instruction: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        extra_feedback: Optional[List[str]] = None,
    ) -> str:
        previous_steps = self._build_previous_steps_text()
        env_feedback_parts = [self._extract_env_feedback(obs)]
        if extra_feedback:
            env_feedback_parts.extend(item for item in extra_feedback if item)
        env_feedback = "\n\n".join(part for part in env_feedback_parts if part and part != "None") or "None"
        text_sections = [
            "Please generate the next move according to the CURRENT UI screenshot, instruction, environment feedback, and previous steps.",
            "Task skills are extra procedural references only. Use `LOAD_SKILL(\"<exact_skill_name>\")` only when you genuinely need external procedural guidance for the next step.",
            "Skills never replace grounding in the CURRENT screenshot and previous steps.",
            f"Instruction: {instruction}",
            "Available skills (skill name - brief description):\n" + self._available_skills_text(),
            f"Previously consulted skills in earlier temporary branches (not currently loaded): {self._consulted_skills_text()}",
            "Environment feedback from the previous step:\n" + env_feedback,
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Make sure clicks target the center of UI elements when possible.",
            "If a previous action failed, adjust based on the new screenshot instead of repeating the same coordinates.",
            "If you return Python code, include concise `#` comments that explain the purpose of the step or sub-step.",
            "Do not enter a repetitive action loop. If recent steps already tried the same action sequence without progress, choose a meaningfully different grounded action.",
        ]
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text_sections.append("Loop warning:\n" + repetition_warning)
        return "\n\n".join(text_sections)

    def _build_main_contents(
        self,
        instruction: str,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        extra_feedback: Optional[List[str]] = None,
    ) -> List[dict]:
        return super()._build_main_contents(
            instruction=instruction,
            current_image=processed_image,
            processed_width=processed_width,
            processed_height=processed_height,
            obs=obs,
            extra_feedback=extra_feedback,
        )

    def _skill_parts_for_mode(self, skill_name: str, full_skill: Dict) -> List[dict]:
        content = full_skill["content"]
        parts: List[dict] = [
            {
                "text": (
                    f"# Branch Skill Reference: {content.name} ({skill_name})\n\n"
                    "The material below is supplemental reference only. "
                    "Decide the next action from the current state, not from the skill alone.\n\n"
                    f"{content.text}"
                )
            }
        ]
        if self.skill_mode == "multimodal":
            for filename, b64_data, mime_type in full_skill.get("images", []):
                parts.append({"text": f"[Branch Skill Visual Reference - {skill_name}/{filename}]"})
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
                        "Skill reference package for this temporary branch.",
                        "The materials below are supplemental workflow references only.",
                        f"Requested skill in the main context: LOAD_SKILL(\"{trigger_skill_name}\")",
                        f"Loaded skills in this branch: {loaded_skill_names}",
                        "Use the following skill materials only as procedural guidance. The CURRENT screenshot and previous steps remain authoritative.",
                    ]
                )
            }
        ]
        for skill_name, full_skill in branch_skill_payloads:
            parts.extend(self._skill_parts_for_mode(skill_name, full_skill))
        return {"role": "user", "parts": parts}

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
            "Please generate the next move according to the CURRENT UI screenshot, instruction, and previous steps.",
            "The skill references provided earlier are procedural references only. They should help reduce guessing, but the final action must still be decided from the CURRENT screenshot, previous steps, and task instruction.",
            f"Instruction: {instruction}",
            "Previous steps (full model responses, including any action comments):\n" + previous_steps,
            self._screen_resolution_prompt(processed_width, processed_height),
            "Return the next action sequence only. Do not request another skill in this branch. Nested `LOAD_SKILL(...)` is invalid.",
            "The loaded skill is only a procedural reference. Do not blindly replay it; ground your action in the CURRENT screenshot.",
            "If you return Python code, include concise `#` comments that explain the purpose of the step or sub-step.",
            "Avoid repetitive action loops. If recent steps already tried the same action sequence without progress, choose a meaningfully different grounded action.",
        ]
        repetition_warning = self._build_repetition_warning_text()
        if repetition_warning:
            text_sections.append("Loop warning:\n" + repetition_warning)
        if round_feedback:
            feedback_lines = "\n".join(f"- {item}" for item in round_feedback if item)
            if feedback_lines:
                text_sections.append("Additional feedback for this branch round:\n" + feedback_lines)
        return "\n\n".join(text_sections)

    def _build_branch_contents(
        self,
        instruction: str,
        trigger_skill_name: str,
        main_trigger_response: str,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        branch_skill_payloads: List[Tuple[str, Dict]],
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
            }
        )
        return contents

    def _record_consulted_skill(self, skill_name: str, image_count: int):
        self._consulted_skills.add(skill_name)
        consulted = sorted(self._consulted_skills)
        images_per_skill = dict(self._skill_usage_summary.get("images_per_skill", {}))
        if self.skill_mode == "multimodal":
            images_per_skill[skill_name] = image_count
        self._skill_usage_summary.update(
            {
                "loaded_skill_names": consulted,
                "consulted_skill_names": consulted,
                "total_loaded_skills": len(consulted),
                "total_loaded_images": sum(images_per_skill.values()) if self.skill_mode == "multimodal" else 0,
                "images_per_skill": images_per_skill if self.skill_mode == "multimodal" else {},
                "load_skill_successes": int(self._skill_usage_summary.get("load_skill_successes", 0)) + 1,
            }
        )

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
            return None, 0, f"Skill '{skill_name}' is already loaded in this branch. Request another skill or return a GUI action."

        full_skill = self._skill_loader.load_full_skill(skill_name)
        if not full_skill:
            return None, 0, f"Failed to load skill '{skill_name}'."

        image_count = len(full_skill.get("images", [])) if self.skill_mode == "multimodal" else 0
        self._record_consulted_skill(skill_name, image_count)
        return full_skill, image_count, None

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

    def _save_conversation_json(self):
        if not self._conversation_log or not self._result_dir:
            return
        output_path = os.path.join(self._result_dir, "conversation.json")
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self._conversation_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._runtime_logger().error("[Skills/V2] Failed to save conversation.json: %s", str(e))

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
            self._runtime_logger().error("[Skills/V2] Failed to save skill_invocations.json: %s", str(e))

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
            }
        )
        output_path = os.path.join(self._result_dir, "skill_usage_summary.json")
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._runtime_logger().error("[Skills/V2] Failed to save skill_usage_summary.json: %s", str(e))

    def _finalize_step(self, processed_image: str, response: str, actions: List[str]) -> Tuple[str, List[str]]:
        self.screenshots.append(processed_image)
        self.responses.append(response)
        self.actions.append(" | ".join(actions) if actions else "No valid action")
        self._save_skill_usage_summary()
        self._save_skill_invocation_log()
        self._save_conversation_json()
        return response, actions

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
        final_actions: List[str] = []
        success = False

        for round_idx in range(MAX_SKILL_LOAD_ROUNDS):
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
                "[MMSkill/V2][Branch %d] Step %d round %d",
                branch_id,
                step_idx,
                round_idx + 1,
            )
            self._runtime_logger().info("[MMSkill/V2][Branch %d] System message:\n%s", branch_id, system_message)
            self._runtime_logger().info(
                "[MMSkill/V2][Branch %d] Contents:\n%s",
                branch_id,
                self._format_contents_for_log(contents),
            )

            try:
                response = self.call_llm(system_text=system_message, contents=contents)
            except Exception as e:
                self._runtime_logger().error(
                    "[MMSkill/V2][Branch %d] Failed to call model %s: %s",
                    branch_id,
                    self.model,
                    str(e),
                )
                response = ""

            final_response = response or ""
            self._runtime_logger().info("[MMSkill/V2][Branch %d] Response: %s", branch_id, final_response)

            round_record = {
                "round": round_idx + 1,
                "timestamp": time.time(),
                "loaded_skills_before_response": sorted(branch_loaded_names),
                "load_event_before_prompt": load_event,
                "system_message": system_message,
                "contents": self._serialize_contents_for_json(contents),
                "response": final_response,
            }

            bare_requested_skill = self._extract_bare_load_skill(final_response)
            parsed_actions = self.parse_actions(
                final_response,
                original_width=original_width,
                original_height=original_height,
                processed_width=processed_width,
                processed_height=processed_height,
            )

            if self._count_code_blocks(final_response) != 1 and bare_requested_skill is None and not parsed_actions:
                error = (
                    "The branch response must contain exactly one code block containing Python, WAIT, DONE, or FAIL. "
                    "If you return Python, include concise '#' comments explaining the action."
                )
                round_feedback.append(error)
                round_record["status"] = "invalid_code_block"
                round_record["error"] = error
                branch_rounds.append(round_record)
                continue

            requested_skill = bare_requested_skill or self._extract_load_skill(final_response)
            if requested_skill is not None:
                round_record["requested_skill"] = requested_skill
                error = (
                    "Nested LOAD_SKILL is not allowed inside a skill branch. "
                    "Use the current screenshot, previous steps, and the already loaded skill "
                    "to return the next immediate GUI action."
                )
                round_feedback.append(error)
                round_record["status"] = "nested_skill_request_forbidden"
                round_record["error"] = error
                branch_rounds.append(round_record)
                continue

            actions = parsed_actions
            round_record["parsed_actions"] = list(actions)
            if actions:
                success = True
                final_actions = actions
                round_record["status"] = "action_returned"
                branch_rounds.append(round_record)
                break

            error = (
                "The branch response did not contain a valid GUI action. Output exactly one code block. "
                "If you return Python, include concise '#' comments explaining the action."
            )
            round_feedback.append(error)
            round_record["status"] = "invalid_action"
            round_record["error"] = error
            branch_rounds.append(round_record)

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
            "final_actions": list(final_actions),
            "final_feedback": round_feedback[-1] if round_feedback else None,
        }
        return {
            "success": success,
            "response": final_response,
            "actions": final_actions,
            "feedback": round_feedback[-1] if round_feedback else "Skill branch did not produce a valid action.",
            "log": branch_log,
        }

    def predict(self, instruction: str, obs: Dict) -> List:
        screenshot_bytes = obs["screenshot"]
        image = Image.open(BytesIO(screenshot_bytes))
        original_width, original_height = image.size

        processed_image, processed_width, processed_height = base_agent_mod.process_image(screenshot_bytes)
        system_message = self._build_main_system_message(instruction)

        round_feedback: List[str] = []
        final_response = ""
        step_idx = len(self.actions)

        for round_idx in range(MAX_SKILL_LOAD_ROUNDS):
            contents = self._build_main_contents(
                instruction=instruction,
                processed_image=processed_image,
                processed_width=processed_width,
                processed_height=processed_height,
                obs=obs,
                extra_feedback=round_feedback,
            )

            self._runtime_logger().info("=" * 80)
            self._runtime_logger().info("[MMSkill/V2] Step %d main round %d", step_idx, round_idx + 1)
            self._runtime_logger().info("[MMSkill/V2] System message:\n%s", system_message)
            self._runtime_logger().info("[MMSkill/V2] Contents:\n%s", self._format_contents_for_log(contents))

            try:
                response = self.call_llm(system_text=system_message, contents=contents)
            except Exception as e:
                self._runtime_logger().error("Failed to call skill v2 model %s: %s", self.model, str(e))
                response = ""

            final_response = response or ""
            self._runtime_logger().info("[MMSkill/V2] Main response: %s", final_response)
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
                if branch_result["success"] and branch_result["actions"]:
                    history_response = self._build_skill_step_history_response(
                        skill_name=skill_name,
                        branch_response=branch_result["response"],
                        actions=branch_result["actions"],
                    )
                    return self._finalize_step(processed_image, history_response, branch_result["actions"])
                round_feedback.append(branch_result["feedback"])
                continue

            actions = parsed_actions
            if actions:
                return self._finalize_step(processed_image, final_response, actions)

            round_feedback.append(
                "The previous response did not contain a valid GUI action or LOAD_SKILL call. Output exactly one code block. "
                "If you return Python, include concise '#' comments explaining the action."
            )

        fallback_response = final_response or "No valid action"
        self.screenshots.append(processed_image)
        self.responses.append(fallback_response)
        self.actions.append("No valid action")
        self._save_skill_usage_summary()
        self._save_skill_invocation_log()
        self._save_conversation_json()
        return fallback_response, []
