import json
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime

from copilot_tools.parser_0920_summary_adv import (
    Parser0920SummaryAdv,
    default_skill,
    instruction_prompt,
    task_define_prompt,
)


COMPRESSED_STATE_START = "<<<STATE_COMPRESSION>>>"
COMPRESSED_STATE_END = "<<<END_STATE_COMPRESSION>>>"
COMPRESSED_STATE_FIELDS = [
    "covered_steps",
    "task",
    "important_user_inputs",
    "important_observations",
    "completed_progress",
    "current_subgoal",
    "pending_risks",
    "last_effective_state",
]


class Parser0920SummaryAdvStateCompress(Parser0920SummaryAdv):
    """Parser with rolling compressed-history support."""

    def _stringify_field_value(self, value):
        if value is None:
            return "none"
        if isinstance(value, str):
            value = value.strip()
            return value if len(value) > 0 else "none"
        if isinstance(value, (list, tuple)):
            cleaned_items = []
            for item in value:
                item = str(item).strip()
                if len(item) > 0:
                    if not item.startswith("- "):
                        item = f"- {item}"
                    cleaned_items.append(item)
            return "\n".join(cleaned_items) if len(cleaned_items) > 0 else "- none"
        value = str(value).strip()
        return value if len(value) > 0 else "none"

    def compressed_state_dict2text(self, compressed_state_dict):
        assert isinstance(
            compressed_state_dict, dict
        ), f"compressed_state_dict should be dict, got {type(compressed_state_dict)}"

        lines = [COMPRESSED_STATE_START]
        for field_name in COMPRESSED_STATE_FIELDS:
            field_value = self._stringify_field_value(compressed_state_dict.get(field_name, "none"))
            if "\n" in field_value:
                lines.append(f"{field_name}:")
                lines.extend(field_value.splitlines())
            else:
                lines.append(f"{field_name}: {field_value}")
        lines.append(COMPRESSED_STATE_END)
        return "\n".join(lines)

    def compressed_state_text2dict(self, compressed_state_text):
        assert isinstance(
            compressed_state_text, str
        ), f"compressed_state_text should be str, got {type(compressed_state_text)}"

        normalized_text = compressed_state_text.strip()
        assert (
            COMPRESSED_STATE_START in normalized_text and COMPRESSED_STATE_END in normalized_text
        ), "compressed_state_text should contain state compression boundary markers"

        body = normalized_text.split(COMPRESSED_STATE_START, 1)[1].split(COMPRESSED_STATE_END, 1)[0].strip()
        lines = body.splitlines()

        parsed = OrderedDict()
        current_field = None
        current_lines = []

        def flush_current_field():
            nonlocal current_field, current_lines
            if current_field is None:
                return
            value = "\n".join(current_lines).strip()
            parsed[current_field] = value if len(value) > 0 else "none"
            current_field = None
            current_lines = []

        for line in lines:
            stripped = line.strip()
            if len(stripped) == 0:
                continue

            matched_field = None
            for field_name in COMPRESSED_STATE_FIELDS:
                prefix = f"{field_name}:"
                if stripped.startswith(prefix):
                    matched_field = field_name
                    flush_current_field()
                    remaining = stripped[len(prefix) :].strip()
                    current_field = field_name
                    if len(remaining) > 0:
                        current_lines = [remaining]
                    else:
                        current_lines = []
                    break

            if matched_field is None and current_field is not None:
                current_lines.append(stripped)

        flush_current_field()

        missing_fields = [field_name for field_name in COMPRESSED_STATE_FIELDS if field_name not in parsed]
        assert len(missing_fields) == 0, f"compressed_state_text missing fields: {missing_fields}"
        return parsed

    def normalize_compressed_state(self, compressed_state, fallback_task="", fallback_covered_steps="unknown"):
        if compressed_state is None:
            return None

        if isinstance(compressed_state, dict):
            normalized_dict = OrderedDict()
            for field_name in COMPRESSED_STATE_FIELDS:
                if field_name == "task":
                    normalized_dict[field_name] = compressed_state.get(field_name, fallback_task or "none")
                elif field_name == "covered_steps":
                    normalized_dict[field_name] = compressed_state.get(
                        field_name, fallback_covered_steps or "unknown"
                    )
                else:
                    normalized_dict[field_name] = compressed_state.get(field_name, "none")
            return self.compressed_state_dict2text(normalized_dict)

        if isinstance(compressed_state, str):
            text = compressed_state.strip()
            if len(text) == 0:
                return None

            if COMPRESSED_STATE_START not in text or COMPRESSED_STATE_END not in text:
                wrapped_dict = OrderedDict(
                    {
                        "covered_steps": fallback_covered_steps or "unknown",
                        "task": fallback_task or "none",
                        "important_user_inputs": "none",
                        "important_observations": text,
                        "completed_progress": "none",
                        "current_subgoal": "none",
                        "pending_risks": "none",
                        "last_effective_state": text,
                    }
                )
                text = self.compressed_state_dict2text(wrapped_dict)

            normalized_dict = self.compressed_state_text2dict(text)
            if normalized_dict.get("task", "none") == "none" and len(fallback_task.strip()) > 0:
                normalized_dict["task"] = fallback_task
            if normalized_dict.get("covered_steps", "unknown") == "unknown" and len(
                str(fallback_covered_steps).strip()
            ) > 0:
                normalized_dict["covered_steps"] = fallback_covered_steps
            return self.compressed_state_dict2text(normalized_dict)

        raise TypeError(f"Unsupported compressed_state type: {type(compressed_state)}")

    def build_compressed_state_message(self, compressed_state, task, compressed_upto_step):
        covered_steps = f"1-{compressed_upto_step}" if compressed_upto_step > 0 else "none"
        normalized_state = self.normalize_compressed_state(
            compressed_state=compressed_state,
            fallback_task=task,
            fallback_covered_steps=covered_steps,
        )
        if normalized_state is None:
            return None

        return {
            "type": "text",
            "text": (
                "以下是对更早历史状态的一轮压缩结果。它保留了更早步骤中的关键用户输入、页面信息、"
                "关键进展和风险点。若其与当前截图冲突，始终以当前截图为准。\n"
                f"{normalized_state}\n"
                "以上压缩内容只出现这一轮，不要要求系统再次展开旧历史。"
            ),
        }

    def env2messages4ask(
        self,
        task,
        environments,
        actions,
        skill=default_skill,
        keep_last_k_images=1,
        extra_skill="",
        compressed_state=None,
        compressed_upto_step=0,
        history_step_offset=0,
    ):
        assert len(environments) > 0, f"environments {environments} should not be empty"
        assert (
            len(environments) - 1 == len(actions)
        ), f"environments {environments} should be one more than actions {actions}"

        if compressed_state is None and history_step_offset == 0:
            return super().env2messages4ask(
                task=task,
                environments=environments,
                actions=actions,
                skill=skill,
                keep_last_k_images=keep_last_k_images,
                extra_skill=extra_skill,
            )

        system_skill = self._compose_system_skill(skill, extra_skill)

        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": system_skill}],
            }
        ]

        history_content = [
            {
                "type": "text",
                "text": (
                    task_define_prompt.format(task=task, current_time=datetime.now().strftime("%Y年%m月%d日"))
                    + "\n\n以下是你之前的操作历史回顾："
                ),
            }
        ]

        compressed_message = self.build_compressed_state_message(
            compressed_state=compressed_state,
            task=task,
            compressed_upto_step=compressed_upto_step,
        )
        if compressed_message is not None:
            history_content.append(compressed_message)
            raw_history_start = history_step_offset + 1
            history_content.append(
                {
                    "type": "text",
                    "text": (
                        f"下面保留的是压缩之后仍需逐步回顾的原始步骤，起始于原始第{raw_history_start}步。"
                        "请把压缩内容和这些原始步骤一起用于决策。"
                    ),
                }
            )

        for idx, (env, act) in enumerate(zip(environments, actions + [None])):
            step_idx = history_step_offset + idx + 1

            act_to_show = deepcopy(act)
            if act_to_show is not None:
                if "cot" in act_to_show:
                    del act_to_show["cot"]
                if "point" in act_to_show:
                    del act_to_show["point"]
                if "point1" in act_to_show:
                    del act_to_show["point1"]
                if "point2" in act_to_show:
                    del act_to_show["point2"]
                if "action_type" in act_to_show:
                    del act_to_show["action_type"]

            user_comment = env.get("user_comment", "").strip()
            if len(user_comment) > 0:
                user_comment = f"用户回复说：\n---------\n{user_comment}\n---------\n用户回复结束\n\n"
            else:
                user_comment = ""

            pic_comment = (
                f"根据协议，第{step_idx}步有截图：\n"
                if idx >= len(environments) - keep_last_k_images
                else f"根据协议，第{step_idx}步截图不展示\n\n"
            )

            history_content.append(
                {
                    "type": "text",
                    "text": f"这是原始第{step_idx}步的环境信息：\n" + user_comment + pic_comment,
                }
            )

            if idx == len(environments) - keep_last_k_images:
                history_content.append(
                    {
                        "type": "text",
                        "text": f"<-------------------从这里开始是最近原始第{step_idx}步起的环境信息------------------->\n\n",
                    }
                )

            if idx >= len(environments) - keep_last_k_images:
                history_content.append({"type": "text", "text": f"<-----原始第{step_idx}步截图----->"})
                history_content.append({"type": "image_url", "image_url": {"url": env["image"]}})
                history_content.append({"type": "text", "text": f"<-----原始第{step_idx}步截图重复一遍----->"})
                history_content.append({"type": "image_url", "image_url": {"url": env["image"]}})
                history_content.append({"type": "text", "text": f"<-----原始第{step_idx}步截图结束----->"})

            if act_to_show is not None:
                action_comment = f"这一步的动作是：{json.dumps(act_to_show, ensure_ascii=False)}\n\n"
            else:
                action_comment = "\n\n"

            history_content.append(
                {
                    "type": "text",
                    "text": f"这是原始第{step_idx}步的环境信息结束。{action_comment}",
                }
            )

        target_step = history_step_offset + len(environments)
        history_content.append(
            {
                "type": "text",
                "text": (
                    f"你需要根据原始第<-----{target_step}----->步的环境信息，预测原始第{target_step}步的动作。\n\n"
                    "一个潜伏在屏幕后的观察者指出：当前屏幕出现了新的变化。请在think过程中详细描述出来！\n\n"
                ),
            }
        )
        history_content.append({"type": "text", "text": instruction_prompt})

        messages.append({"role": "user", "content": history_content})
        return messages
