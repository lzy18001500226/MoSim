# Copyright 2023-2026 AgentEra(Agently.Tech)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import json5
from typing import Literal, Any, Mapping, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from agently.types.data import PromptOutputStructure


class DataLocator:
    @staticmethod
    def _is_structure_sequence(value: Any) -> bool:
        return not isinstance(value, str) and isinstance(value, Sequence)

    @staticmethod
    def _matches_output_schema_shape(parsed_json: Any, output_prompt: "PromptOutputStructure") -> bool:
        if isinstance(output_prompt, Mapping):
            return isinstance(parsed_json, Mapping) and (
                len(output_prompt) == 0 or any(key in parsed_json for key in output_prompt.keys())
            )
        if DataLocator._is_structure_sequence(output_prompt):
            return DataLocator._is_structure_sequence(parsed_json)
        return False

    @staticmethod
    def _score_output_schema_match(parsed_json: Any, output_prompt: "PromptOutputStructure") -> int:
        if not DataLocator._matches_output_schema_shape(parsed_json, output_prompt):
            return -1

        from agently.utils.DataPathBuilder import DataPathBuilder

        try:
            schema_paths = DataPathBuilder.extract_possible_paths(output_prompt, style="dot")
        except Exception:
            return 0

        empty = object()
        score = 0
        for path in schema_paths:
            if not path:
                continue
            if DataLocator.locate_path_in_dict(parsed_json, path, style="dot", default=empty) is not empty:
                score += 1
        return score

    @staticmethod
    def _locate_path_parts(
        result: Any,
        path_parts: list[str],
        *,
        style: Literal["dot", "slash"],
        default: Any,
    ):
        if not path_parts:
            return result
        path_part = path_parts[0]
        remaining = path_parts[1:]
        if style == "dot":
            if "[" in path_part:
                path_key_and_index = path_part.split("[", 1)
                path_key = path_key_and_index[0]
                path_index = path_key_and_index[1][:-1]
                if path_key:
                    if isinstance(result, Mapping):
                        result = result.get(path_key, default)
                    else:
                        return default
                elif not DataLocator._is_structure_sequence(result):
                    return default
                if path_index in ("*", ""):
                    if DataLocator._is_structure_sequence(result):
                        values = []
                        for item in result:
                            value = DataLocator._locate_path_parts(
                                item,
                                remaining,
                                style=style,
                                default=default,
                            )
                            if value is default:
                                return default
                            values.append(value)
                        return values
                    return default
                try:
                    index = int(path_index)
                except Exception:
                    return default
                if DataLocator._is_structure_sequence(result):
                    try:
                        return DataLocator._locate_path_parts(
                            result[index],
                            remaining,
                            style=style,
                            default=default,
                        )
                    except Exception:
                        return default
                return default
            else:
                if isinstance(result, Mapping):
                    return DataLocator._locate_path_parts(
                        result.get(path_part, default),
                        remaining,
                        style=style,
                        default=default,
                    )
                return default
        else:
            if path_part.startswith("[") and path_part.endswith("]"):
                path_part = path_part[1:-1]

            if path_part in ("*", ""):
                if DataLocator._is_structure_sequence(result):
                    values = []
                    for item in result:
                        value = DataLocator._locate_path_parts(
                            item,
                            remaining,
                            style=style,
                            default=default,
                        )
                        if value is default:
                            return default
                        values.append(value)
                    return values
                return default
            if isinstance(result, Mapping):
                return DataLocator._locate_path_parts(
                    result.get(path_part, default),
                    remaining,
                    style=style,
                    default=default,
                )
            if DataLocator._is_structure_sequence(result):
                try:
                    return DataLocator._locate_path_parts(
                        result[int(path_part)],
                        remaining,
                        style=style,
                        default=default,
                    )
                except Exception:
                    return default
            return default

    @staticmethod
    def locate_path_in_dict(
        original_dict: Mapping[str, Any] | Sequence[Any],
        path: str,
        style: Literal["dot", "slash"] = "dot",
        *,
        default: Any = None,
    ):
        if path == "" or not isinstance(path, str):
            return original_dict
        match style:
            case "dot":
                try:
                    path_parts = path.split(".")
                    return DataLocator._locate_path_parts(
                        original_dict,
                        path_parts,
                        style="dot",
                        default=default,
                    )
                except Exception:
                    return default
            case "slash":
                try:
                    path_parts = [part for part in path.split("/") if part]
                    return DataLocator._locate_path_parts(
                        original_dict,
                        path_parts,
                        style="slash",
                        default=default,
                    )
                except Exception:
                    return default

    @staticmethod
    def locate_all_json(original_text: str) -> list[str]:
        pattern = r'"""(.*?)"""'
        original_text = re.sub(pattern, lambda match: json5.dumps(match.group(1)), original_text, flags=re.DOTALL)
        original_text = original_text.replace("\"\"\"", "\"").replace("[OUTPUT]", "$<<OUTPUT>>")
        stage = 1
        json_blocks = []
        block_num = 0
        layer = 0
        skip_next = False
        in_quote = False
        for index, char in enumerate(original_text):
            if skip_next:
                skip_next = False
                continue
            if stage == 1:
                if char == "\\":
                    skip_next = True
                    continue
                if char == "[" or char == "{":
                    json_blocks.append(char)
                    stage = 2
                    layer += 1
                    continue
            elif stage == 2:
                if not in_quote:
                    if char == "\\":
                        skip_next = True
                        if original_text[index + 1] == "\"":
                            char = "\""
                        else:
                            continue
                    if char == "\"":
                        in_quote = True
                    if char == "[" or char == "{":
                        layer += 1
                    elif char == "]" or char == "}":
                        layer -= 1
                    # elif char in ("\t", " ", "\n"):
                    # char = ""
                    json_blocks[block_num] += char
                else:
                    if char == "\\":
                        char += original_text[index + 1]
                        skip_next = True
                    elif char == "\n":
                        char = "\\n"
                    elif char == "\t":
                        char = "\\t"
                    elif char == "\"":
                        in_quote = not in_quote
                    json_blocks[block_num] += char
                if layer == 0:
                    json_blocks[block_num] = json_blocks[block_num].replace("$<<OUTPUT>>", "[OUTPUT]")
                    block_num += 1
                    stage = 1
        return json_blocks

    @staticmethod
    def locate_output_json(original_text: str, output_prompt_dict: "PromptOutputStructure"):
        all_json = DataLocator.locate_all_json(original_text)
        if len(all_json) == 0:
            return None
        if len(all_json) == 1:
            return all_json[0]
        else:
            best_json = None
            best_score = -1
            for json_string in all_json:
                try:
                    parsed_json = json5.loads(json_string)
                    score = DataLocator._score_output_schema_match(parsed_json, output_prompt_dict)
                    if score >= best_score:
                        best_score = score
                        best_json = json_string
                except Exception:
                    continue
            if best_json is not None and best_score >= 0:
                return best_json
            return all_json[-1]

    @staticmethod
    def _next_non_whitespace_char(original_text: str, start_index: int) -> str | None:
        for index in range(start_index, len(original_text)):
            if not original_text[index].isspace():
                return original_text[index]
        return None

    @staticmethod
    def _is_quote_variant(char: str, delimiter: str) -> bool:
        if delimiter == '"':
            return char in {'"', '“', '”', '＂'}
        return char in {"'", '‘', '’', '＇'}

    @staticmethod
    def _can_close_repaired_string(original_text: str, index: int, role: Literal["key", "value"]) -> bool:
        next_char = DataLocator._next_non_whitespace_char(original_text, index + 1)
        if next_char is None:
            return role == "value"
        if role == "key":
            return next_char in {':', '：'}
        return next_char in {',', '，', '}', ']', '｝', '］'}

    @staticmethod
    def repair_json_fragment(original_text: str) -> str:
        """Repair structural quote and punctuation issues without rewriting string contents."""

        structural_translations = {
            '：': ':',
            '，': ',',
            '｛': '{',
            '｝': '}',
            '［': '[',
            '］': ']',
        }

        contexts: list[dict[str, str]] = [{"type": "root", "state": "value_or_end"}]
        repaired_chars: list[str] = []
        in_string = False
        string_delimiter = '"'
        string_role: Literal["key", "value"] = "value"
        escape = False
        in_primitive = False
        primitive_role: Literal["key", "value"] = "value"
        index = 0

        def current_context() -> dict[str, str]:
            return contexts[-1]

        def mark_value_completed() -> None:
            context = current_context()
            if context["type"] in ("object", "array"):
                context["state"] = "comma_or_end"
            else:
                context["state"] = "done"

        while index < len(original_text):
            char = original_text[index]
            normalized_char = structural_translations.get(char, char)

            if in_string:
                if escape:
                    repaired_chars.append(char)
                    escape = False
                    index += 1
                    continue

                if char == "\\":
                    repaired_chars.append(char)
                    escape = True
                    index += 1
                    continue

                if DataLocator._is_quote_variant(char, string_delimiter):
                    if DataLocator._can_close_repaired_string(original_text, index, string_role):
                        repaired_chars.append(string_delimiter)
                        in_string = False
                        if string_role == "key":
                            current_context()["state"] = "colon"
                        else:
                            mark_value_completed()
                    else:
                        repaired_chars.append(char)
                    index += 1
                    continue

                repaired_chars.append(char)
                index += 1
                continue

            if in_primitive:
                if primitive_role == "key":
                    if normalized_char == ':':
                        repaired_chars.append(':')
                        current_context()["state"] = "value"
                        in_primitive = False
                        index += 1
                        continue

                    repaired_chars.append(char)
                    index += 1
                    continue

                if char.isspace():
                    repaired_chars.append(char)
                    mark_value_completed()
                    in_primitive = False
                    index += 1
                    continue

                if normalized_char in {',', '}', ']'}:
                    mark_value_completed()
                    in_primitive = False
                    continue

                repaired_chars.append(char)
                index += 1
                continue

            if char.isspace():
                repaired_chars.append(char)
                index += 1
                continue

            context = current_context()
            state = context["state"]

            if state in ("key_or_end", "value", "value_or_end") and DataLocator._is_quote_variant(char, '"'):
                in_string = True
                string_delimiter = '"'
                string_role = "key" if state == "key_or_end" else "value"
                repaired_chars.append('"')
                index += 1
                continue

            if state in ("key_or_end", "value", "value_or_end") and DataLocator._is_quote_variant(char, "'"):
                in_string = True
                string_delimiter = "'"
                string_role = "key" if state == "key_or_end" else "value"
                repaired_chars.append("'")
                index += 1
                continue

            if normalized_char in {'{', '['} and state in ("value", "value_or_end"):
                repaired_chars.append(normalized_char)
                if normalized_char == '{':
                    contexts.append({"type": "object", "state": "key_or_end"})
                else:
                    contexts.append({"type": "array", "state": "value_or_end"})
                index += 1
                continue

            if normalized_char == '}' and context["type"] == "object" and state in ("key_or_end", "comma_or_end"):
                repaired_chars.append('}')
                contexts.pop()
                mark_value_completed()
                index += 1
                continue

            if normalized_char == ']' and context["type"] == "array" and state in ("value_or_end", "comma_or_end"):
                repaired_chars.append(']')
                contexts.pop()
                mark_value_completed()
                index += 1
                continue

            if normalized_char == ':' and context["type"] == "object" and state == "colon":
                repaired_chars.append(':')
                context["state"] = "value"
                index += 1
                continue

            if normalized_char == ',' and state == "comma_or_end":
                repaired_chars.append(',')
                if context["type"] == "object":
                    context["state"] = "key_or_end"
                elif context["type"] == "array":
                    context["state"] = "value_or_end"
                else:
                    context["state"] = "done"
                index += 1
                continue

            if state == "key_or_end":
                in_primitive = True
                primitive_role = "key"
                repaired_chars.append(char)
                index += 1
                continue

            if state in ("value", "value_or_end"):
                in_primitive = True
                primitive_role = "value"
                repaired_chars.append(char)
                index += 1
                continue

            repaired_chars.append(char)
            index += 1

        return "".join(repaired_chars)

    @staticmethod
    def repair_text(original_text: str) -> str:
        """Backward-compatible wrapper for structure-aware JSON fragment repair."""
        try:
            return DataLocator.repair_json_fragment(original_text)
        except Exception:
            return original_text
