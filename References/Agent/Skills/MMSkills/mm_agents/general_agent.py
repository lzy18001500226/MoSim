"""
General desktop VLM agent for OSWorld.

The agent uses a model-agnostic "return Python code" interaction style, but
borrows a few robustness ideas from Qwen3VLAgent:
- image preprocessing via smart_resize
- richer instruction text with explicit screen resolution / history
- optional relative-coordinate output that is scaled back to the real screen
"""

import ast
import base64
import json
import logging
import os
import time
from io import BytesIO
from typing import Callable, Dict, List, Optional, Tuple

import backoff
import openai
import requests
from PIL import Image
from requests.exceptions import SSLError

from mm_agents.agent import parse_code_from_string
from mm_agents.utils.qwen_vl_utils import preprocess_image_for_vlm

logger = None

MAX_RETRY_TIMES = 5
OPENAI_RATE_LIMIT_RETRY_SLEEP_SECONDS = 1
RELATIVE_COORDINATE_MAX = 999


def encode_image(image_content: bytes) -> str:
    return base64.b64encode(image_content).decode("utf-8")


def process_image(image_bytes: bytes) -> Tuple[str, int, int]:
    """
    Resize screenshots using the same heuristic as Qwen3VLAgent so the model sees
    a similar visual input distribution during evaluation.
    """
    return preprocess_image_for_vlm(image_bytes)


class _CoordinateTransformer(ast.NodeTransformer):
    """
    Scale model-emitted pyautogui coordinates into the real screen space.
    Only constant numeric coordinates are transformed; everything else is kept.
    """

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
        accept_unit_interval_coordinates: bool = False,
        accept_absolute_pixel_coordinates_when_relative: bool = False,
        force_absolute_pixel_coordinates_when_relative: bool = False,
    ) -> None:
        self.coordinate_type = coordinate_type
        self.original_width = original_width
        self.original_height = original_height
        self.processed_width = processed_width
        self.processed_height = processed_height
        self.accept_unit_interval_coordinates = accept_unit_interval_coordinates
        self.accept_absolute_pixel_coordinates_when_relative = accept_absolute_pixel_coordinates_when_relative
        self.force_absolute_pixel_coordinates_when_relative = force_absolute_pixel_coordinates_when_relative

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

        keyword_nodes = {keyword.arg: keyword.value for keyword in node.keywords if keyword.arg in {"x", "y"}}
        x_node = None
        y_node = None
        if x_idx is not None:
            x_node = node.args[x_idx] if len(node.args) > x_idx else keyword_nodes.get("x")
            y_node = node.args[y_idx] if y_idx is not None and len(node.args) > y_idx else keyword_nodes.get("y")
        force_absolute_pair = self._should_treat_pair_as_absolute_pixels(x_node, y_node)

        if x_idx is not None and len(node.args) > x_idx:
            node.args[x_idx] = self._transform_coord(
                node.args[x_idx],
                axis="x",
                force_absolute_pixel=force_absolute_pair,
            )
        if y_idx is not None and len(node.args) > y_idx:
            node.args[y_idx] = self._transform_coord(
                node.args[y_idx],
                axis="y",
                force_absolute_pixel=force_absolute_pair,
            )

        for keyword in node.keywords:
            if keyword.arg == "x":
                keyword.value = self._transform_coord(
                    keyword.value,
                    axis="x",
                    force_absolute_pixel=force_absolute_pair,
                )
            elif keyword.arg == "y":
                keyword.value = self._transform_coord(
                    keyword.value,
                    axis="y",
                    force_absolute_pixel=force_absolute_pair,
                )

        return node

    @staticmethod
    def _get_func_name(func: ast.expr) -> str | None:
        if isinstance(func, ast.Attribute):
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
        return None

    def _transform_coord(
        self,
        node: ast.expr,
        axis: str,
        force_absolute_pixel: bool = False,
    ) -> ast.expr:
        value = self._get_numeric_value(node)
        if value is None:
            return node

        if force_absolute_pixel:
            scaled = self._clamp_absolute_pixel(value, axis=axis)
        else:
            scaled = self._scale(value, axis=axis)
        return ast.copy_location(ast.Constant(value=scaled), node)

    @staticmethod
    def _get_numeric_value(node: ast.expr) -> float | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            inner = _CoordinateTransformer._get_numeric_value(node.operand)
            return -inner if inner is not None else None
        return None

    def _should_treat_pair_as_absolute_pixels(
        self,
        x_node: ast.expr | None,
        y_node: ast.expr | None,
    ) -> bool:
        if (
            self.coordinate_type != "relative"
            or not self.original_width
            or not self.original_height
        ):
            return False

        if self.force_absolute_pixel_coordinates_when_relative:
            return True

        if not self.accept_absolute_pixel_coordinates_when_relative:
            return False

        values = []
        for node in (x_node, y_node):
            if node is None:
                continue
            value = self._get_numeric_value(node)
            if value is not None:
                values.append(value)
        return any(value > RELATIVE_COORDINATE_MAX for value in values)

    def _clamp_absolute_pixel(self, value: float, axis: str) -> int:
        dimension = self.original_width if axis == "x" else self.original_height
        if not dimension:
            return int(round(value))
        return max(0, min(int(round(value)), dimension - 1))

    def _scale(self, value: float, axis: str) -> int:
        if not self.original_width or not self.original_height:
            return int(round(value))

        if self.coordinate_type == "relative":
            dimension = self.original_width if axis == "x" else self.original_height
            if self.accept_unit_interval_coordinates and 0 <= value <= 1:
                return max(0, min(int(round(value * dimension)), dimension - 1))
            limit = RELATIVE_COORDINATE_MAX
            scaled = value * dimension / limit
            return max(0, min(int(round(scaled)), dimension - 1))

        processed_dimension = self.processed_width if axis == "x" else self.processed_height
        original_dimension = self.original_width if axis == "x" else self.original_height

        if not processed_dimension:
            return max(0, min(int(round(value)), original_dimension - 1))

        scaled = value * original_dimension / processed_dimension
        return max(0, min(int(round(scaled)), original_dimension - 1))


GENERAL_SYSTEM_PROMPT = """
Follow the instruction to perform desktop computer tasks.
You control the computer using Python code with `pyautogui`.

For each step, you will receive the current screenshot and a short summary of previous actions.
Use the screenshot to decide the next action. Do not assume that previous clicks succeeded.
If an earlier action failed, adjust based on the CURRENT screenshot instead of repeating the same guess.

Important rules:
- Use `pyautogui` only.
- Do NOT use `pyautogui.locateCenterOnScreen`.
- Do NOT use `pyautogui.screenshot()`.
- Each response must be self-contained; do not rely on variables from previous steps.
- When a click does not work, revise the target based on the new screenshot.
- Prefer short, direct actions over long speculative scripts.

Output format:
- Return ONLY one code block with Python code, or one special code block containing `WAIT`, `DONE`, or `FAIL`.
- If you return Python code, the code block may contain multiple sequential `pyautogui` statements when they belong to the same immediate step.
- Do not return prose outside the code block.

Special codes:
- ```WAIT``` when the UI is still loading.
- ```DONE``` when the task is complete.
- ```FAIL``` only when the task is truly impossible.

Coordinate system:
- When the prompt says the screen resolution is 1000x1000, use that normalized coordinate space in your `pyautogui` calls.
- When the prompt says the screen resolution is WxH, use that exact resolution.

The computer password is '{CLIENT_PASSWORD}', use it when needed.
""".strip()


class GeneralAgent:
    def __init__(
        self,
        platform: str = "ubuntu",
        model: str = "gpt-4o",
        max_tokens: int = 32768,
        top_p: float = 0.9,
        temperature: float = 0.0,
        action_space: str = "pyautogui",
        observation_type: str = "screenshot",
        max_trajectory_length: int = 3,
        a11y_tree_max_tokens: int = 10000,
        client_password: str = "password",
        api_key: str | None = None,
        base_url: str | None = None,
        api_backend: str = "openai",
        api_model: str | None = None,
        thinking_level: str = "NONE",
        include_thoughts: bool = False,
        thinking_mode: str = "auto",
        coordinate_type: str = "relative",
        save_conversation_json: bool = False,
        llm_request_timeout: int = 300,
        llm_max_retries: int = MAX_RETRY_TIMES,
    ):
        self.platform = platform
        self.model = model
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.temperature = temperature
        self.action_space = action_space
        self.observation_type = observation_type
        self.max_trajectory_length = max_trajectory_length
        self.a11y_tree_max_tokens = a11y_tree_max_tokens
        self.client_password = client_password
        self.coordinate_type = coordinate_type
        self.api_backend = api_backend
        self.api_model = api_model or model
        self.thinking_mode = thinking_mode
        self.save_conversation_json = save_conversation_json
        self.llm_request_timeout = max(1, int(llm_request_timeout))
        self.llm_max_retries = max(1, int(llm_max_retries))
        self._progress_callback: Optional[Callable[..., None]] = None

        if self.api_backend == "gemini":
            self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
            self.base_url = (base_url or os.environ.get("GEMINI_BASE_URL", "")).rstrip("/")
        elif self.api_backend == "openai":
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
            self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "")).rstrip("/")
        else:
            raise ValueError("api_backend must be 'gemini' or 'openai'")
        self.thinking_level = thinking_level
        self.include_thoughts = include_thoughts if thinking_level != "NONE" else False

        assert action_space == "pyautogui", "GeneralAgent only supports 'pyautogui'"
        assert observation_type == "screenshot", "GeneralAgent only supports 'screenshot'"
        assert coordinate_type in {"absolute", "relative"}, "coordinate_type must be absolute or relative"
        assert self.thinking_mode in {"auto", "on", "off"}, "thinking_mode must be auto, on, or off"

        self.system_message = GENERAL_SYSTEM_PROMPT.format(
            CLIENT_PASSWORD=self.client_password
        )
        self.responses: List[str] = []
        self.actions: List[str] = []
        self.screenshots: List[str] = []
        self.vm_ip = None
        self._conversation_log: List[dict] = []
        self._result_dir: Optional[str] = None

    def set_progress_callback(self, callback: Optional[Callable[..., None]]) -> None:
        self._progress_callback = callback

    def _report_progress(self, stage: str, detail: Optional[str] = None, **extra) -> None:
        callback = self._progress_callback
        if not callable(callback):
            return
        try:
            callback(stage=stage, detail=detail, **extra)
        except Exception:
            if logger:
                logger.exception("[GeneralAgent] Failed to report progress: stage=%s detail=%s", stage, detail)

    @staticmethod
    def _extract_env_feedback(obs: Dict) -> str:
        if not isinstance(obs, dict):
            return "None"
        feedback_candidates: List[str] = []
        for key in ("env_feedback", "last_action_feedback", "feedback", "error_message"):
            value = obs.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                feedback_candidates.append(text)
        if not feedback_candidates:
            return "None"
        return "\n\n".join(feedback_candidates)

    def _screen_resolution_prompt(self, processed_width: int, processed_height: int) -> str:
        if self.coordinate_type == "relative":
            return (
                "The screen resolution for your coordinate outputs is 1000x1000. "
                "All x/y coordinates in your `pyautogui` code must use this normalized space."
            )
        return (
            f"The screen resolution for your coordinate outputs is {processed_width}x{processed_height}. "
            "Use this exact resolution in your `pyautogui` coordinates."
        )

    def _build_main_system_message(self, instruction: str) -> str:
        return self.system_message + "\nYou are asked to complete the following task: " + instruction

    def _build_main_user_text(
        self,
        instruction: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        extra_feedback: Optional[List[str]] = None,
    ) -> str:
        current_step = len(self.actions)
        history_action_start = max(0, current_step - self.max_trajectory_length)
        history_actions = self.actions[history_action_start:current_step]
        previous_actions = (
            "\n".join(
                f"Step {history_action_start + idx + 1}: {action}"
                for idx, action in enumerate(history_actions)
            )
            if history_actions
            else "None"
        )
        env_feedback_parts = [self._extract_env_feedback(obs)]
        if extra_feedback:
            env_feedback_parts.extend(item for item in extra_feedback if item)
        env_feedback = "\n\n".join(part for part in env_feedback_parts if part and part != "None") or "None"
        guidance = [
            "Please generate the next move according to the UI screenshot, instruction, environment feedback, and previous actions.",
            f"Instruction: {instruction}",
            f"Environment feedback from the previous step:\n{env_feedback}",
            f"Previous actions:\n{previous_actions}",
            self._screen_resolution_prompt(processed_width, processed_height),
            "Make sure clicks target the center of UI elements when possible.",
            "If a previous action failed, adjust based on the new screenshot instead of repeating the same coordinates.",
        ]
        return "\n\n".join(guidance)

    def _build_main_user_content(
        self,
        instruction: str,
        processed_image: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        extra_feedback: Optional[List[str]] = None,
    ) -> dict:
        return {
            "role": "user",
            "parts": [
                {
                    "text": self._build_main_user_text(
                        instruction=instruction,
                        processed_width=processed_width,
                        processed_height=processed_height,
                        obs=obs,
                        extra_feedback=extra_feedback,
                    )
                },
                self._image_part(processed_image),
            ],
        }

    @staticmethod
    def _image_part(image_b64: str) -> dict:
        return {
            "inlineData": {
                "mimeType": "image/png",
                "data": image_b64,
            }
        }

    def _build_main_contents(
        self,
        instruction: str,
        current_image: str,
        processed_width: int,
        processed_height: int,
        obs: Dict,
        extra_feedback: Optional[List[str]] = None,
    ) -> list:
        contents = []

        history_len = min(self.max_trajectory_length, len(self.responses), len(self.screenshots))
        if history_len > 0:
            history_responses = self.responses[-history_len:]
            history_screenshots = self.screenshots[-history_len:]

            for idx in range(history_len):
                contents.append({"role": "user", "parts": [self._image_part(history_screenshots[idx])]})
                contents.append(
                    {
                        "role": "model",
                        "parts": [{"text": history_responses[idx] or "No valid action"}],
                    }
                )

        contents.append(
            self._build_main_user_content(
                instruction=instruction,
                processed_image=current_image,
                processed_width=processed_width,
                processed_height=processed_height,
                obs=obs,
                extra_feedback=extra_feedback,
            )
        )

        return contents

    @staticmethod
    def _normalize_non_codeblock_response(response: str) -> str:
        if not response:
            return ""
        normalized = response.strip()
        normalized = normalized.replace("<|begin_of_box|>", "")
        normalized = normalized.replace("<|end_of_box|>", "")
        return normalized.strip()

    def _extract_bare_actions(self, response: str) -> List[str]:
        normalized = self._normalize_non_codeblock_response(response)
        if not normalized or "```" in normalized:
            return []

        if normalized in {"WAIT", "DONE", "FAIL"}:
            return [normalized]

        bare_code = normalized
        if bare_code.lower().startswith("python\n"):
            bare_code = bare_code.split("\n", 1)[1].strip()

        if "pyautogui" not in bare_code:
            return []

        try:
            ast.parse(bare_code)
        except Exception:
            return []

        if logger:
            logger.info("[GeneralAgent] Parsed bare executable response without code block.")
        return [bare_code]

    def _finalize_step(
        self,
        processed_image: str,
        response: str,
        actions: List[str],
    ) -> Tuple[str, List[str]]:
        self.screenshots.append(processed_image)
        self.responses.append(response)
        action_summary = " | ".join(actions) if actions else "No valid action"
        self.actions.append(action_summary)
        self._save_conversation_json()
        return response, actions

    def predict(self, instruction: str, obs: Dict) -> List:
        screenshot_bytes = obs["screenshot"]
        image = Image.open(BytesIO(screenshot_bytes))
        original_width, original_height = image.size

        processed_image, processed_width, processed_height = process_image(screenshot_bytes)
        system_message = self._build_main_system_message(instruction)
        contents = self._build_main_contents(
            instruction=instruction,
            current_image=processed_image,
            processed_width=processed_width,
            processed_height=processed_height,
            obs=obs,
        )

        if logger:
            logger.info("=" * 80)
            logger.info("[GeneralAgent Prompt] Step %d sending request to %s", len(self.actions), self.api_model)
            logger.info("-" * 80)
            logger.info("[GeneralAgent Prompt] System message:\n%s", system_message)
            logger.info("-" * 80)
            logger.info("[GeneralAgent Prompt] Contents:\n%s", self._format_contents_for_log(contents))
            logger.info("-" * 80)

        try:
            response = self.call_llm(system_text=system_message, contents=contents)
        except Exception as e:
            logger.error("Failed to call model %s, Error: %s", self.model, str(e))
            response = ""

        logger.info("RESPONSE: %s", response)
        if self.save_conversation_json:
            self._conversation_log.append(
                {
                    "step": len(self.actions),
                    "timestamp": time.time(),
                    "system_message": system_message,
                    "contents": self._serialize_contents_for_json(contents),
                    "response": response,
                }
            )
        actions = self.parse_actions(
            response,
            original_width=original_width,
            original_height=original_height,
            processed_width=processed_width,
            processed_height=processed_height,
        )
        return self._finalize_step(processed_image, response, actions)

    @staticmethod
    def _format_contents_for_log(contents: List[dict]) -> str:
        lines: List[str] = []
        for idx, item in enumerate(contents):
            role = item.get("role", "unknown")
            lines.append(f"  [{idx}] role={role}")
            for part_idx, part in enumerate(item.get("parts", [])):
                if "text" in part:
                    text = part.get("text", "")
                    lines.append(f"       [{part_idx}] type=text, len={len(text)}")
                    for tl in text.split("\n"):
                        lines.append(f"            | {tl}")
                elif "inlineData" in part:
                    inline_data = part["inlineData"]
                    mime = inline_data.get("mimeType", "application/octet-stream")
                    data = inline_data.get("data", "")
                    approx_bytes = int(len(data) * 0.75)
                    size_str = f"{approx_bytes / 1024:.1f} KB" if approx_bytes > 1024 else f"{approx_bytes} bytes"
                    lines.append(f"       [{part_idx}] type=image, mime={mime}, ~{size_str}")
                else:
                    lines.append(f"       [{part_idx}] type=unknown")
        return "\n".join(lines)

    @staticmethod
    def _serialize_contents_for_json(contents: List[dict]) -> List[dict]:
        serialized: List[dict] = []
        for item in contents:
            parts = []
            for part in item.get("parts", []):
                if "text" in part:
                    parts.append({"type": "text", "text": part.get("text", "")})
                elif "inlineData" in part:
                    inline_data = part["inlineData"]
                    mime = inline_data.get("mimeType", "application/octet-stream")
                    data = inline_data.get("data", "")
                    approx_bytes = int(len(data) * 0.75)
                    parts.append(
                        {
                            "type": "image",
                            "mimeType": mime,
                            "placeholder": f"[base64 image ~{approx_bytes} bytes]",
                        }
                    )
            serialized.append({"role": item.get("role", "unknown"), "parts": parts})
        return serialized

    def _save_conversation_json(self):
        if not self.save_conversation_json or not self._conversation_log or not self._result_dir:
            return
        output_path = os.path.join(self._result_dir, "conversation.json")
        try:
            os.makedirs(self._result_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self._conversation_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            if logger:
                logger.error("[GeneralAgent] Failed to save conversation.json: %s", str(e))

    def _build_native_gemini_payload(self, system_text: str, contents: list) -> dict:
        generation_config = {
            "temperature": self.temperature,
            "maxOutputTokens": self.max_tokens,
            "topP": self.top_p,
            "seed": 0,
        }
        if self.thinking_level != "NONE":
            generation_config["thinkingConfig"] = {
                "thinkingLevel": self.thinking_level,
                "includeThoughts": self.include_thoughts,
            }

        return {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_text}]},
            "generationConfig": generation_config,
        }

    @staticmethod
    def _content_part_to_openai_part(part: dict) -> dict | None:
        if "text" in part:
            return {"type": "text", "text": part["text"]}

        inline_data = part.get("inlineData") or {}
        mime_type = inline_data.get("mimeType")
        data = inline_data.get("data")
        if mime_type and data:
            return {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{data}"},
            }

        return None

    def _build_openai_messages(self, system_text: str, contents: list) -> list[dict]:
        messages: list[dict] = [{"role": "system", "content": system_text}]

        role_map = {"user": "user", "model": "assistant"}
        for item in contents:
            role = role_map.get(item.get("role", "user"), "user")
            parts = []
            for part in item.get("parts", []):
                converted = self._content_part_to_openai_part(part)
                if converted is not None:
                    parts.append(converted)
            if not parts:
                continue
            messages.append({"role": role, "content": parts})

        return messages

    def _is_openrouter_backend(self) -> bool:
        return self.api_backend == "openai" and "openrouter.ai" in (self.base_url or "")

    def _is_qwen_openai_backend(self) -> bool:
        model_name = (self.api_model or "").lower()
        return self.api_backend == "openai" and "qwen" in model_name

    def _uses_kimi_unit_interval_coordinates(self) -> bool:
        model_name = f"{self.api_model or ''} {self.model or ''}".lower()
        return self.api_backend == "openai" and ("kimi" in model_name or "moonshot" in model_name)

    def _accepts_absolute_pixels_in_relative_mode(self) -> bool:
        model_name = f"{self.api_model or ''} {self.model or ''}".lower()
        if self.api_backend != "openai":
            return False
        return "gpt-5.4" in model_name

    def _forces_absolute_pixels_in_relative_mode(self) -> bool:
        model_name = f"{self.api_model or ''} {self.model or ''}".lower()
        if self.api_backend != "openai":
            return False
        return "gpt-5.4" in model_name

    def _build_openai_extra_body(self) -> dict | None:
        """
        Some OpenAI-compatible providers require provider-specific controls.
        Qwen3-VL uses `enable_thinking` in `extra_body`, as verified in
        test_qwen3vl.py.
        """
        if not self._is_qwen_openai_backend():
            return None
        if self.thinking_mode == "on":
            return {"enable_thinking": True}
        if self.thinking_mode == "off":
            return {"enable_thinking": False}
        return None

    @staticmethod
    def _extract_openai_message_text(message) -> str:
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_chunks = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text")
                    if isinstance(text, str):
                        text_chunks.append(text)
                else:
                    text = getattr(item, "text", None)
                    if isinstance(text, str):
                        text_chunks.append(text)
            return "\n".join(chunk for chunk in text_chunks if chunk).strip()
        return ""

    def _build_openrouter_headers(self) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # OpenRouter accepts X-Title as an optional attribution header.
            "X-Title": os.environ.get("OPENROUTER_APP_NAME", "OSWorld"),
        }
        referer = os.environ.get("OPENROUTER_HTTP_REFERER") or os.environ.get("OR_SITE_URL")
        if referer:
            headers["HTTP-Referer"] = referer
        return headers

    def _build_openrouter_payload(self, system_text: str, contents: list) -> dict:
        payload = {
            "model": self.api_model,
            "messages": self._build_openai_messages(system_text, contents),
            "max_tokens": self.max_tokens,
        }

        # GPT-5.4 Mini on OpenRouter does not advertise temperature/top_p support.
        if not self.api_model.startswith("openai/gpt-5"):
            payload["temperature"] = self.temperature
            payload["top_p"] = self.top_p

        if self.thinking_mode == "on":
            payload["include_reasoning"] = True
        elif self.thinking_mode == "off":
            payload["include_reasoning"] = False

        return payload

    @staticmethod
    def _extract_openrouter_text(result: dict) -> str:
        try:
            choices = result.get("choices", [])
            if not choices:
                logger.error(
                    "[GeneralAgent/OpenRouter] No choices in response: %s",
                    json.dumps(result, ensure_ascii=False)[:500],
                )
                return ""

            message = choices[0].get("message", {}) or {}
            content = message.get("content", "")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text_parts: list[str] = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                return "".join(text_parts)
            return str(content or "")
        except Exception:
            logger.exception("[GeneralAgent/OpenRouter] Failed to extract text from response")
            return ""

    @backoff.on_exception(
        backoff.constant,
        (
            SSLError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ),
        interval=30,
        max_tries=5,
    )
    def call_llm(self, system_text: str, contents: list) -> str:
        self._report_progress(
            "llm_call_start",
            f"backend={self.api_backend} model={self.api_model}",
        )
        if self._is_openrouter_backend():
            return self._call_llm_openrouter(system_text=system_text, contents=contents)
        if self.api_backend == "openai":
            return self._call_llm_openai(system_text=system_text, contents=contents)
        return self._call_llm_native_gemini(system_text=system_text, contents=contents)

    def _call_llm_native_gemini(self, system_text: str, contents: list) -> str:
        url = f"{self.base_url}/v1:generateContent"
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = self._build_native_gemini_payload(system_text, contents)

        last_error = None
        for attempt in range(1, self.llm_max_retries + 1):
            self._report_progress(
                "llm_request_attempt_start",
                f"backend=gemini attempt={attempt}/{self.llm_max_retries} timeout={self.llm_request_timeout}s",
            )
            logger.info(
                "[GeneralAgent] Generating content with model %s (attempt %d/%d), url: %s",
                self.model,
                attempt,
                self.llm_max_retries,
                url,
            )
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.llm_request_timeout,
                )
                if response.status_code != 200:
                    error_body = response.text[:1000]
                    self._report_progress(
                        "llm_request_attempt_error",
                        f"backend=gemini attempt={attempt}/{self.llm_max_retries} status={response.status_code}",
                    )
                    logger.error(
                        "[GeneralAgent] HTTP %d error (attempt %d/%d): %s",
                        response.status_code,
                        attempt,
                        self.llm_max_retries,
                        error_body,
                    )

                    if response.status_code == 429:
                        time.sleep(10 * attempt)
                        continue
                    if response.status_code >= 500:
                        time.sleep(5 * attempt)
                        continue
                    if response.status_code == 400 and len(contents) > 1:
                        logger.warning(
                            "[GeneralAgent] 400 Bad Request, truncating history from %d to 1 message",
                            len(contents),
                        )
                        contents = [contents[-1]]
                        payload = self._build_native_gemini_payload(system_text, contents)
                        self._report_progress(
                            "llm_request_attempt_retry",
                            f"backend=gemini attempt={attempt}/{self.llm_max_retries} truncated_history=1",
                        )
                        time.sleep(2)
                        continue

                    last_error = requests.exceptions.HTTPError(
                        f"HTTP {response.status_code}: {error_body}",
                        response=response,
                    )
                    break

                result = response.json()
                text = self._extract_text_from_response(result)
                if text:
                    self._report_progress(
                        "llm_request_attempt_success",
                        f"backend=gemini attempt={attempt}/{self.llm_max_retries}",
                    )
                    return text

                logger.warning(
                    "[GeneralAgent] Empty text extracted from response (attempt %d/%d), raw: %s",
                    attempt,
                    self.llm_max_retries,
                    json.dumps(result, ensure_ascii=False)[:500],
                )
                self._report_progress(
                    "llm_request_attempt_empty",
                    f"backend=gemini attempt={attempt}/{self.llm_max_retries}",
                )
                last_error = ValueError("Empty text in native Gemini response")
                time.sleep(3)
            except requests.exceptions.Timeout as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_timeout",
                    f"backend=gemini attempt={attempt}/{self.llm_max_retries} timeout={self.llm_request_timeout}s",
                )
                logger.error(
                    "[GeneralAgent] Request timeout (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                time.sleep(5 * attempt)
            except requests.exceptions.ConnectionError as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_connection_error",
                    f"backend=gemini attempt={attempt}/{self.llm_max_retries}",
                )
                logger.error(
                    "[GeneralAgent] Connection error (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                time.sleep(5 * attempt)
            except Exception as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_exception",
                    f"backend=gemini attempt={attempt}/{self.llm_max_retries} error={type(e).__name__}",
                )
                logger.error(
                    "[GeneralAgent] Unexpected error (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                if attempt < self.llm_max_retries:
                    time.sleep(5 * attempt)

        self._report_progress(
            "llm_call_failed",
            f"backend=gemini retries_exhausted={self.llm_max_retries} last_error={type(last_error).__name__ if last_error else 'None'}",
        )
        logger.error("[GeneralAgent] All %d attempts failed. Last error: %s", self.llm_max_retries, str(last_error))
        return ""

    def _call_llm_openai(self, system_text: str, contents: list) -> str:
        client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.llm_request_timeout,
            max_retries=0,
        )
        contents_to_send = contents
        last_error = None

        for attempt in range(1, self.llm_max_retries + 1):
            messages = self._build_openai_messages(system_text, contents_to_send)
            request_kwargs = {
                "model": self.api_model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": self.top_p,
                "timeout": self.llm_request_timeout,
            }
            extra_body = self._build_openai_extra_body()
            if extra_body:
                request_kwargs["extra_body"] = extra_body

            self._report_progress(
                "llm_request_attempt_start",
                f"backend=openai attempt={attempt}/{self.llm_max_retries} timeout={self.llm_request_timeout}s",
            )
            logger.info(
                "[GeneralAgent/OpenAI] Generating content with model %s (attempt %d/%d), base_url: %s, thinking_mode=%s",
                self.api_model,
                attempt,
                self.llm_max_retries,
                self.base_url,
                self.thinking_mode,
            )
            try:
                response = client.chat.completions.create(**request_kwargs)
                message = response.choices[0].message
                content = self._extract_openai_message_text(message)
                if content:
                    self._report_progress(
                        "llm_request_attempt_success",
                        f"backend=openai attempt={attempt}/{self.llm_max_retries}",
                    )
                    return content

                logger.warning(
                    "[GeneralAgent/OpenAI] Empty content extracted from response (attempt %d/%d)",
                    attempt,
                    self.llm_max_retries,
                )
                self._report_progress(
                    "llm_request_attempt_empty",
                    f"backend=openai attempt={attempt}/{self.llm_max_retries}",
                )
                last_error = ValueError("Empty text in OpenAI-compatible response")
                time.sleep(3)
            except openai.RateLimitError as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_rate_limit",
                    f"backend=openai attempt={attempt}/{self.llm_max_retries}",
                )
                logger.error(
                    "[GeneralAgent/OpenAI] Rate limit (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                if attempt < self.llm_max_retries:
                    time.sleep(OPENAI_RATE_LIMIT_RETRY_SLEEP_SECONDS)
            except (openai.APITimeoutError, openai.APIConnectionError) as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_timeout",
                    f"backend=openai attempt={attempt}/{self.llm_max_retries} timeout={self.llm_request_timeout}s",
                )
                logger.error(
                    "[GeneralAgent/OpenAI] Connection/timeout error (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                time.sleep(5 * attempt)
            except openai.BadRequestError as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_error",
                    f"backend=openai attempt={attempt}/{self.llm_max_retries} error=BadRequest",
                )
                logger.error(
                    "[GeneralAgent/OpenAI] Bad request (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                if len(contents_to_send) > 1:
                    logger.warning(
                        "[GeneralAgent/OpenAI] Truncating history from %d to 1 message after bad request",
                        len(contents_to_send),
                    )
                    contents_to_send = [contents_to_send[-1]]
                    self._report_progress(
                        "llm_request_attempt_retry",
                        f"backend=openai attempt={attempt}/{self.llm_max_retries} truncated_history=1",
                    )
                    time.sleep(2)
                    continue
                break
            except openai.InternalServerError as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_exception",
                    f"backend=openai attempt={attempt}/{self.llm_max_retries} error=InternalServerError",
                )
                logger.error(
                    "[GeneralAgent/OpenAI] Internal server error (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                time.sleep(5 * attempt)
            except Exception as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_exception",
                    f"backend=openai attempt={attempt}/{self.llm_max_retries} error={type(e).__name__}",
                )
                logger.error(
                    "[GeneralAgent/OpenAI] Unexpected error (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                if attempt < self.llm_max_retries:
                    time.sleep(5 * attempt)

        self._report_progress(
            "llm_call_failed",
            f"backend=openai retries_exhausted={self.llm_max_retries} last_error={type(last_error).__name__ if last_error else 'None'}",
        )
        logger.error("[GeneralAgent/OpenAI] All %d attempts failed. Last error: %s", self.llm_max_retries, str(last_error))
        return ""

    def _call_llm_openrouter(self, system_text: str, contents: list) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = self._build_openrouter_headers()
        contents_to_send = contents
        last_error = None

        for attempt in range(1, self.llm_max_retries + 1):
            payload = self._build_openrouter_payload(system_text, contents_to_send)
            self._report_progress(
                "llm_request_attempt_start",
                f"backend=openrouter attempt={attempt}/{self.llm_max_retries} timeout={self.llm_request_timeout}s",
            )
            logger.info(
                "[GeneralAgent/OpenRouter] Generating content with model %s (attempt %d/%d), base_url: %s, thinking_mode=%s",
                self.api_model,
                attempt,
                self.llm_max_retries,
                self.base_url,
                self.thinking_mode,
            )
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.llm_request_timeout,
                )
                if response.status_code != 200:
                    error_body = response.text[:1000]
                    self._report_progress(
                        "llm_request_attempt_error",
                        f"backend=openrouter attempt={attempt}/{self.llm_max_retries} status={response.status_code}",
                    )
                    logger.error(
                        "[GeneralAgent/OpenRouter] HTTP %d error (attempt %d/%d): %s",
                        response.status_code,
                        attempt,
                        self.llm_max_retries,
                        error_body,
                    )
                    if response.status_code == 429:
                        time.sleep(10 * attempt)
                        continue
                    if response.status_code >= 500:
                        time.sleep(5 * attempt)
                        continue
                    if response.status_code == 400 and len(contents_to_send) > 1:
                        logger.warning(
                            "[GeneralAgent/OpenRouter] 400 Bad Request, truncating history from %d to 1 message",
                            len(contents_to_send),
                        )
                        contents_to_send = [contents_to_send[-1]]
                        self._report_progress(
                            "llm_request_attempt_retry",
                            f"backend=openrouter attempt={attempt}/{self.llm_max_retries} truncated_history=1",
                        )
                        time.sleep(2)
                        continue
                    last_error = requests.exceptions.HTTPError(
                        f"HTTP {response.status_code}: {error_body}",
                        response=response,
                    )
                    break

                result = response.json()
                content = self._extract_openrouter_text(result)
                if content:
                    self._report_progress(
                        "llm_request_attempt_success",
                        f"backend=openrouter attempt={attempt}/{self.llm_max_retries}",
                    )
                    return content

                logger.warning(
                    "[GeneralAgent/OpenRouter] Empty content extracted from response (attempt %d/%d), raw: %s",
                    attempt,
                    self.llm_max_retries,
                    json.dumps(result, ensure_ascii=False)[:500],
                )
                self._report_progress(
                    "llm_request_attempt_empty",
                    f"backend=openrouter attempt={attempt}/{self.llm_max_retries}",
                )
                last_error = ValueError("Empty text in OpenRouter response")
                time.sleep(3)
            except requests.exceptions.Timeout as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_timeout",
                    f"backend=openrouter attempt={attempt}/{self.llm_max_retries} timeout={self.llm_request_timeout}s",
                )
                logger.error(
                    "[GeneralAgent/OpenRouter] Request timeout (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                time.sleep(5 * attempt)
            except requests.exceptions.ConnectionError as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_connection_error",
                    f"backend=openrouter attempt={attempt}/{self.llm_max_retries}",
                )
                logger.error(
                    "[GeneralAgent/OpenRouter] Connection error (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                time.sleep(5 * attempt)
            except Exception as e:
                last_error = e
                self._report_progress(
                    "llm_request_attempt_exception",
                    f"backend=openrouter attempt={attempt}/{self.llm_max_retries} error={type(e).__name__}",
                )
                logger.error(
                    "[GeneralAgent/OpenRouter] Unexpected error (attempt %d/%d): %s",
                    attempt,
                    self.llm_max_retries,
                    str(e),
                )
                if attempt < self.llm_max_retries:
                    time.sleep(5 * attempt)

        self._report_progress(
            "llm_call_failed",
            f"backend=openrouter retries_exhausted={self.llm_max_retries} last_error={type(last_error).__name__ if last_error else 'None'}",
        )
        logger.error(
            "[GeneralAgent/OpenRouter] All %d attempts failed. Last error: %s",
            self.llm_max_retries,
            str(last_error),
        )
        return ""

    def _extract_text_from_response(self, result: dict) -> str:
        try:
            candidates = result.get("candidates", [])
            if not candidates:
                logger.error("[GeneralAgent] No candidates in response: %s", json.dumps(result, ensure_ascii=False)[:500])
                return ""

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                logger.error("[GeneralAgent] No parts in response candidate")
                return ""

            text_parts = []
            for part in parts:
                if part.get("thought", False):
                    continue
                if "text" in part:
                    text_parts.append(part["text"])

            if text_parts:
                return "\n".join(text_parts)

            for part in reversed(parts):
                if "text" in part:
                    return part["text"]
            return ""
        except (KeyError, IndexError, TypeError) as e:
            logger.error("[GeneralAgent] Failed to extract text from response: %s", str(e))
            return ""

    def _scale_code_coordinates(
        self,
        code: str,
        original_width: int | None,
        original_height: int | None,
        processed_width: int | None,
        processed_height: int | None,
    ) -> str:
        try:
            tree = ast.parse(code)
            transformer = _CoordinateTransformer(
                coordinate_type=self.coordinate_type,
                original_width=original_width,
                original_height=original_height,
                processed_width=processed_width,
                processed_height=processed_height,
                accept_unit_interval_coordinates=self._uses_kimi_unit_interval_coordinates(),
                accept_absolute_pixel_coordinates_when_relative=self._accepts_absolute_pixels_in_relative_mode(),
                force_absolute_pixel_coordinates_when_relative=self._forces_absolute_pixels_in_relative_mode(),
            )
            tree = transformer.visit(tree)
            ast.fix_missing_locations(tree)
            return ast.unparse(tree)
        except Exception as e:
            logger.debug("Failed to scale model code coordinates: %s", str(e))
            return code

    def parse_actions(
        self,
        response: str,
        original_width: int | None = None,
        original_height: int | None = None,
        processed_width: int | None = None,
        processed_height: int | None = None,
    ) -> List[str]:
        if not response:
            return []

        actions = parse_code_from_string(response)
        if not actions:
            actions = self._extract_bare_actions(response)
        scaled_actions = []
        for action in actions:
            if action in {"WAIT", "DONE", "FAIL"}:
                scaled_actions.append(action)
                continue

            scaled_actions.append(
                self._scale_code_coordinates(
                    action,
                    original_width=original_width,
                    original_height=original_height,
                    processed_width=processed_width,
                    processed_height=processed_height,
                )
            )

        return scaled_actions

    def reset(self, _logger=None, vm_ip=None, **kwargs):
        global logger
        logger = _logger if _logger is not None else logging.getLogger("desktopenv.general_agent")
        self.vm_ip = vm_ip
        self._result_dir = kwargs.get("result_dir")
        self.responses = []
        self.actions = []
        self.screenshots = []
        self._conversation_log = []
