import json
import re
from typing import List


def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_repetitive(text: str, window: int = 512) -> bool:
    """Detect if the tail of the text is repetitive (model degeneration)."""
    if len(text) < window * 2:
        return False
    return text[-window:] == text[-window * 2 : -window]


def extract_boxed_answer(text: str) -> str:
    """Extract the last \\boxed{...} content from text."""
    pattern = r"\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}"
    matches = re.findall(pattern, text)
    return matches[-1] if matches else ""


def extract_code_block(text: str) -> str:
    """Extract the last code block from text."""
    pattern = r"```(?:\w+)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[-1].strip() if matches else ""


def estimate_token_count(text: str) -> int:
    """Rough token count estimate (words * 1.3 for English, chars / 1.5 for CJK mixed)."""
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]", text))
    if cjk_chars > len(text) * 0.3:
        return int(len(text) / 1.5)
    return int(len(text.split()) * 1.3)


def split_thinking_content(
    response: str, think_start_tag: str = "<think>", think_end_tag: str = "</think>"
) -> tuple:
    """Split a response into thinking content and answer content."""
    if think_end_tag in response:
        parts = response.split(think_end_tag)
        think_content = think_end_tag.join(parts[:-1]).replace(think_start_tag, "").strip()
        answer_content = parts[-1].strip()
    else:
        think_content = response.replace(think_start_tag, "").strip()
        answer_content = ""
    return think_content, answer_content


def clip_trajectories(
    trajectories: List[str],
    max_total_tokens: int,
    estimate_fn=None,
) -> List[str]:
    """Clip trajectories from the beginning if total tokens exceed the budget."""
    if estimate_fn is None:
        estimate_fn = estimate_token_count

    token_counts = [estimate_fn(t) for t in trajectories]
    total = sum(token_counts)

    if total <= max_total_tokens:
        return trajectories

    excess = total - max_total_tokens
    cut_per_trajectory = excess // len(trajectories) + 1

    clipped = []
    for text, count in zip(trajectories, token_counts):
        if count <= cut_per_trajectory:
            clipped.append(text)
            continue
        ratio = cut_per_trajectory / count
        char_cut = int(len(text) * ratio)
        clipped.append(text[char_cut:])

    return clipped
