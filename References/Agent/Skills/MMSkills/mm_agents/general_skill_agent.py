import json
import logging
import os
import re
import time
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from PIL import Image

from mm_agents import general_agent as base_agent_mod


MAX_SKILL_LOAD_ROUNDS = 8


class GeneralSkillAgent(base_agent_mod.GeneralAgent):
    """GeneralAgent variant with on-demand LOAD_SKILL blocks."""

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
        self._fully_loaded_skills: Set[str] = set()
        self._skill_context_messages: List[dict] = []
        self._skill_usage_summary: Dict[str, object] = {}

    def _init_skill_loader(self):
        if self._skill_loader is None:
            from mm_agents.skill_loader import SkillLoader

            self._skill_loader = SkillLoader(skills_library_dir=self.skills_library_dir)
            if base_agent_mod.logger:
                base_agent_mod.logger.info("[Skills] SkillLoader initialized with library: %s", self.skills_library_dir)

    def reset(self, _logger=None, vm_ip=None, **kwargs):
        runtime_logger = _logger if _logger is not None else logging.getLogger("desktopenv.general_skill_agent")
        super().reset(_logger=runtime_logger, vm_ip=vm_ip, **kwargs)
        self._task_skill_names = []
        self._task_skill_metadatas = []
        self._fully_loaded_skills = set()
        self._skill_context_messages = []
        self._skill_usage_summary = {
            "skill_mode": self.skill_mode,
            "task_skill_names": [],
            "loaded_skill_names": [],
            "total_loaded_skills": 0,
            "total_loaded_images": 0,
            "images_per_skill": {},
            "load_skill_calls": 0,
            "load_skill_successes": 0,
        }

    def set_task_skills(self, skill_names: List[str]):
        self._init_skill_loader()
        self._task_skill_names = list(skill_names or [])
        all_metadata = self._skill_loader.discover_all_skills()
        meta_map = {Path(meta.directory).name: meta for meta in all_metadata}
        self._task_skill_metadatas = [meta_map[name] for name in self._task_skill_names if name in meta_map]
        self._fully_loaded_skills = set()
        self._skill_context_messages = []
        self._skill_usage_summary = {
            "skill_mode": self.skill_mode,
            "task_skill_names": list(self._task_skill_names),
            "loaded_skill_names": [],
            "total_loaded_skills": 0,
            "total_loaded_images": 0,
            "images_per_skill": {},
            "load_skill_calls": 0,
            "load_skill_successes": 0,
        }
        if base_agent_mod.logger:
            base_agent_mod.logger.info("[Skills] General task skills resolved: %s", self._task_skill_names)

    def _build_skill_system_message(self, instruction: str) -> str:
        available_skills = "\n".join(
            f"- {Path(meta.directory).name}: {(meta.description or '').strip() or '(no description)'}"
            for meta in self._task_skill_metadatas
        ) or "- None"
        return f"""
Follow the instruction to perform desktop computer tasks.
You control the computer using Python code with `pyautogui`.

For each step, you will receive the current screenshot and a short summary of previous actions.
Use the screenshot to decide the next action. Do not assume that previous clicks succeeded.
If an earlier action failed, adjust based on the CURRENT screenshot instead of repeating the same guess.

Before every step, first decide whether you already have enough procedural knowledge to act correctly.
If the workflow is uncertain, task-specific, or would benefit from explicit procedural guidance, load the appropriate skill before acting.
If the needed procedure is already known and loaded, produce the next concrete `pyautogui` action directly.

Available skills for this task:
{available_skills}

Important rules:
- Use `pyautogui` only for GUI actions.
- Do NOT use `pyautogui.locateCenterOnScreen`.
- Do NOT use `pyautogui.screenshot()`.
- Each response must be self-contained; do not rely on variables from previous steps.
- When a click does not work, revise the target based on the new screenshot.
- Prefer short, direct actions over long speculative scripts.

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

Special codes:
- ```WAIT``` when the UI is still loading.
- ```DONE``` when the task is complete.
- ```FAIL``` only when the task is truly impossible.

Skill loading:
- Use ```LOAD_SKILL("<exact_skill_name>")``` when you need additional procedural knowledge before acting.
- In `text_only` mode, the loaded skill will provide textual instructions.
- In `multimodal` mode, the loaded skill will provide textual instructions and all reference images for that skill.
- Do not call `LOAD_SKILL(...)` for a skill that is already loaded unless the environment feedback explicitly indicates that procedural guidance is still missing.

Coordinate system:
- When the prompt says the screen resolution is 1000x1000, use that normalized coordinate space in your `pyautogui` calls.
- When the prompt says the screen resolution is WxH, use that exact resolution.

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

    def _count_code_blocks(self, response: str) -> int:
        return len(re.findall(r"```.*?```", response, re.DOTALL))

    def _build_current_user_message(
        self,
        instruction: str,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        extra_feedback: Optional[List[str]] = None,
    ) -> dict:
        previous_actions = "\n".join(
            f"Step {idx + 1}: {action}" for idx, action in enumerate(self.actions[-self.max_trajectory_length :])
        ) or "None"
        env_feedback_parts = [self._extract_env_feedback(obs)]
        if extra_feedback:
            env_feedback_parts.extend(item for item in extra_feedback if item)
        env_feedback = "\n\n".join(part for part in env_feedback_parts if part and part != "None") or "None"
        loaded_skills = ", ".join(sorted(self._fully_loaded_skills)) if self._fully_loaded_skills else "None"
        available_skill_lines = [
            f"- {Path(meta.directory).name}: {(meta.description or '').strip() or '(no description)'}"
            for meta in self._task_skill_metadatas
        ]
        available_skills = "\n".join(available_skill_lines) if available_skill_lines else "None"
        text = "\n\n".join(
            [
                "Please generate the next move according to the UI screenshot, instruction, loaded skills, environment feedback, and previous actions.",
                "Before taking a GUI action, explicitly consider whether additional procedural knowledge is needed now. "
                "If yes, output `LOAD_SKILL(\"<exact_skill_name>\")`. Otherwise output the next `pyautogui` action.",
                f"Instruction: {instruction}",
                "Available skills (skill name - brief description):\n" + available_skills,
                f"Loaded skills: {loaded_skills}",
                "Environment feedback from the previous step:\n" + env_feedback,
                "Previous actions:\n" + previous_actions,
                self._screen_resolution_prompt(processed_width, processed_height),
                "Make sure clicks target the center of UI elements when possible.",
                "If a previous action failed, adjust based on the new screenshot instead of repeating the same coordinates.",
            ]
        )
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
        contents: List[dict] = []
        contents.extend(self._skill_context_messages)

        history_len = min(self.max_trajectory_length, len(self.responses))
        if history_len > 0:
            history_responses = self.responses[-history_len:]
            history_screenshots = self.screenshots[-history_len:]
            for idx in range(history_len):
                user_parts = [self._image_part(history_screenshots[idx])]
                if idx == 0:
                    user_parts.insert(
                        0,
                        self._build_current_user_message(
                            instruction,
                            processed_image,
                            processed_width,
                            processed_height,
                            obs,
                            extra_feedback,
                        )["parts"][0],
                    )
                contents.append({"role": "user", "parts": user_parts})
                contents.append({"role": "model", "parts": [{"text": history_responses[idx] or "No valid action"}]})
            contents.append({"role": "user", "parts": [self._image_part(processed_image)]})
            return contents

        contents.append(
            self._build_current_user_message(
                instruction,
                processed_image,
                processed_width,
                processed_height,
                obs,
                extra_feedback,
            )
        )
        return contents

    def _skill_parts_for_mode(self, skill_name: str, full_skill: Dict) -> Tuple[List[dict], int]:
        content = full_skill["content"]
        parts: List[dict] = [
            {
                "text": (
                    f"# Skill Loaded: {content.name} ({skill_name})\n\n"
                    f"{content.text}\n\n"
                    "Use the procedural instructions above when deciding the next immediate action."
                )
            }
        ]
        image_count = 0
        if self.skill_mode == "multimodal":
            for filename, b64_data, mime_type in full_skill.get("images", []):
                parts.append({"text": f"[Skill Visual Reference - {skill_name}/{filename}]"})
                parts.append({"inlineData": {"mimeType": mime_type, "data": b64_data}})
                image_count += 1
        return parts, image_count

    def _record_loaded_skill(self, skill_name: str, image_count: int):
        self._fully_loaded_skills.add(skill_name)
        loaded = sorted(self._fully_loaded_skills)
        images_per_skill = dict(self._skill_usage_summary.get("images_per_skill", {}))
        if self.skill_mode == "multimodal":
            images_per_skill[skill_name] = image_count
        self._skill_usage_summary.update(
            {
                "loaded_skill_names": loaded,
                "total_loaded_skills": len(loaded),
                "total_loaded_images": sum(images_per_skill.values()) if self.skill_mode == "multimodal" else 0,
                "images_per_skill": images_per_skill if self.skill_mode == "multimodal" else {},
                "load_skill_successes": int(self._skill_usage_summary.get("load_skill_successes", 0)) + 1,
            }
        )

    def _handle_load_skill(self, skill_name: str) -> Tuple[bool, Optional[str]]:
        self._skill_usage_summary["load_skill_calls"] = int(self._skill_usage_summary.get("load_skill_calls", 0)) + 1
        if not skill_name:
            return False, "Missing skill name in LOAD_SKILL(...)."
        if skill_name not in self._task_skill_names:
            return False, f"Unknown skill '{skill_name}'. Use only a skill from the available skill list."
        if skill_name in self._fully_loaded_skills:
            return False, f"Skill '{skill_name}' is already loaded. Produce a GUI action unless another unloaded skill is required."

        full_skill = self._skill_loader.load_full_skill(skill_name)
        if not full_skill:
            return False, f"Failed to load skill '{skill_name}'."

        skill_parts, image_count = self._skill_parts_for_mode(skill_name, full_skill)
        self._record_loaded_skill(skill_name, image_count)
        self._skill_context_messages.extend(
            [
                {"role": "model", "parts": [{"text": f"```LOAD_SKILL(\"{skill_name}\")```"}]},
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                "The requested skill has been loaded. "
                                + (
                                    "The text and all reference images for this skill are now available."
                                    if self.skill_mode == "multimodal"
                                    else "This skill was loaded in text-only mode."
                                )
                            )
                        },
                        *skill_parts,
                    ],
                },
            ]
        )
        return True, None

    def _save_skill_usage_summary(self):
        if not self._result_dir:
            return
        output_path = os.path.join(self._result_dir, "skill_usage_summary.json")
        payload = dict(self._skill_usage_summary)
        payload["steps_recorded"] = len(self.actions)
        payload["final_actions"] = list(self.actions)
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            if base_agent_mod.logger:
                base_agent_mod.logger.error("[Skills] Failed to save general skill_usage_summary.json: %s", str(e))

    def predict(self, instruction: str, obs: Dict) -> List:
        screenshot_bytes = obs["screenshot"]
        image = Image.open(BytesIO(screenshot_bytes))
        original_width, original_height = image.size

        processed_image, processed_width, processed_height = base_agent_mod.process_image(screenshot_bytes)
        system_message = self._build_skill_system_message(instruction)

        round_feedback: List[str] = []
        final_response = ""

        for round_idx in range(MAX_SKILL_LOAD_ROUNDS):
            contents = self._build_contents(
                instruction,
                processed_image,
                processed_width,
                processed_height,
                obs,
                round_feedback,
            )

            if base_agent_mod.logger:
                base_agent_mod.logger.info("=" * 80)
                base_agent_mod.logger.info("[GeneralSkill Prompt] Step %d round %d", len(self.actions), round_idx + 1)
                base_agent_mod.logger.info("[GeneralSkill Prompt] System message:\n%s", system_message)
                base_agent_mod.logger.info("-" * 80)
                base_agent_mod.logger.info("[GeneralSkill Prompt] Contents:\n%s", self._format_contents_for_log(contents))
                base_agent_mod.logger.info("-" * 80)

            try:
                response = self.call_llm(system_text=system_message, contents=contents)
            except Exception as e:
                base_agent_mod.logger.error("Failed to call skill model %s, Error: %s", self.model, str(e))
                response = ""

            final_response = response or ""
            if base_agent_mod.logger:
                base_agent_mod.logger.info("[GeneralSkill Response] %s", final_response)

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

            if self._count_code_blocks(final_response) != 1:
                round_feedback.append(
                    "The previous response must contain exactly one code block. Output only one code block containing Python, WAIT, DONE, FAIL, or LOAD_SKILL(\"<exact_skill_name>\")."
                )
                continue

            skill_name = self._extract_load_skill(final_response)
            if skill_name is not None:
                ok, err = self._handle_load_skill(skill_name)
                if ok:
                    continue
                round_feedback.append(err or "Skill load failed.")
                continue

            actions = self.parse_actions(
                final_response,
                original_width=original_width,
                original_height=original_height,
                processed_width=processed_width,
                processed_height=processed_height,
            )
            if actions:
                self.screenshots.append(processed_image)
                self.responses.append(final_response)
                self.actions.append(" | ".join(actions))
                self._save_skill_usage_summary()
                self._save_conversation_json()
                return final_response, actions

            round_feedback.append(
                "The previous response did not contain a valid GUI action or LOAD_SKILL call. Output exactly one code block."
            )

        self.screenshots.append(processed_image)
        self.responses.append(final_response or "No valid action")
        self.actions.append("No valid action")
        self._save_skill_usage_summary()
        self._save_conversation_json()
        return final_response or "No valid action", []
