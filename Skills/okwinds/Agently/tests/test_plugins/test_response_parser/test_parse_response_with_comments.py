import pytest
import json5
from typing import Any, cast
from agently.utils import DataFormatter, DataLocator, StreamingJSONCompleter


def run_complete_and_parse(json_str: str, expected_keys: list[str]):
    completer = StreamingJSONCompleter()
    completer.append(json_str)
    completed = completer.complete()
    print("Completed JSON:", completed)
    parsed = json5.loads(completed)
    for key in expected_keys:
        assert key in parsed  # type: ignore
        print("Key:", key, "Value:", parsed[key])  # type: ignore


def test_normal_model_output_extraction_and_completion():
    model_output = '''
    Here is the data you asked:

    ```json
    {
      "name": "Alice",
      "age": 30,
      "skills": ["python", "ML"]
    }
    ```

    Let me know if you want more.
    '''

    json_blocks = DataLocator.locate_all_json(model_output)
    assert len(json_blocks) > 0

    output_prompt_dict = {"name": None, "age": None}
    chosen_json = DataLocator.locate_output_json(model_output, output_prompt_dict)  # type: ignore
    assert chosen_json is not None

    run_complete_and_parse(chosen_json, ["name", "age", "skills"])


def test_edge_cases_multiple_json_and_text():
    model_output = '''
    Some explanation before JSON:

    ```json
    {"incomplete": true,
    '''

    model_output += '''
    "list": [1, 2, 3],
    '''

    model_output += '''
    }
    ```

    And some unrelated text.

    {"other": "object", "number": 42}
    '''

    json_blocks = DataLocator.locate_all_json(model_output)
    assert len(json_blocks) >= 2

    # output_prompt_dict = {"incomplete": None, "list": None}
    output_prompt_dict = {"other": None, "number": None}
    chosen_json = DataLocator.locate_output_json(model_output, output_prompt_dict)  # type: ignore
    assert chosen_json is not None

    # run_complete_and_parse(chosen_json, ["incomplete", "list"])
    run_complete_and_parse(chosen_json, ["other", "number"])

    # Also test last json block separately
    # run_complete_and_parse(json_blocks[-1], ["other", "number"])
    run_complete_and_parse(json_blocks[0], ["incomplete", "list"])


def test_no_json_in_text():
    text = "This is a plain text without any JSON or braces."
    json_blocks = DataLocator.locate_all_json(text)
    assert json_blocks == []

    chosen_json = DataLocator.locate_output_json(text, {"any": None})
    assert chosen_json is None


def test_json_with_nested_and_comments():
    model_output = '''
    Here is nested JSON with comments:

    {
        "user": "Bob", // user name
        "data": {
            /* data start here */
            "scores": [10, 20, 30], /* array of scores */
            "active": true
            /* -*-data end here-*- */
        }
    }
    '''

    json_blocks = DataLocator.locate_all_json(model_output)
    assert len(json_blocks) == 1

    chosen_json = DataLocator.locate_output_json(model_output, {"user": None, "data": None})
    assert chosen_json is not None

    run_complete_and_parse(chosen_json, ["user", "data"])


def test_locate_output_json_with_root_list_schema():
    model_output = """
    Here is an object:
    {"meta": {"count": 1}}

    Here is the actual result:
    [
      {"title": "A"},
      {"title": "B"}
    ]
    """

    chosen_json = DataLocator.locate_output_json(model_output, [{"title": None}])
    assert chosen_json is not None

    parsed = json5.loads(chosen_json)
    assert isinstance(parsed, list)
    parsed = cast(list[dict[str, str]], parsed)
    assert parsed[0]["title"] == "A"


def test_locate_output_json_prefers_best_schema_match_over_think_draft():
    model_output = '''
    <think>
    先草拟一个结构：
    {"summary": "draft", "action_items": [{"owner": "张经理"}]}
    </think>

    最终结果：
    {
      "summary": "启动用户反馈系统开发，暂缓数据导出功能；微服务改造需评估；4月底完成原型，6月底上线；下周提交项目计划。",
      "action_items": [
        {"task": "提交详细项目计划", "owner": "张经理", "deadline": "2024-03-22"},
        {"task": "评估微服务改造可行性", "owner": "张经理", "deadline": "2024-03-29"}
      ]
    }
    '''

    chosen_json = DataLocator.locate_output_json(
        model_output,
        {
            "summary": (str, "会议核心结论，100字以内"),
            "action_items": [
                {
                    "task": (str, "待办事项描述"),
                    "owner": (str, "负责人"),
                    "deadline": (str, "截止日期"),
                }
            ],
        },
    )

    assert chosen_json is not None
    parsed = cast(dict[str, Any], json5.loads(chosen_json))
    assert parsed["action_items"][0]["task"] == "提交详细项目计划"
