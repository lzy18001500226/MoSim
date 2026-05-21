# Configure Prompt Guide（YAML/JSON 模板化，通用）

目标：把 prompt 从“散落在代码字符串”提升为“可版本管理、可 diff、可运维”的模板资产。

来源：
- `agently-exmaples/step_by_step/04-configure_prompt.py`

---

## 1) 为什么要用 YAML/JSON Prompt

适用场景（通用）：
- 多 agent / 多工作流：需要统一管理 prompt 结构。
- 线上迭代：需要灰度、回滚、对比差异。
- 团队协作：PR review 更容易审查 prompt 改动。

---

## 2) Prompt 结构：`.agent` 与 `.request`

通用映射规则（概念层面）：
- `.agent.*`：agent 级 prompt（更持久、更像“配置”）
- `.request.*`（或某些实现的顶层 request keys）：单次请求 prompt（更像“调用参数”）

建议：
- 角色/长期约束放 `.agent.system`
- 每次输入/输出 schema 放 `.request.input/.request.output`

---

## 3) 从文件加载（推荐）

```py
from agently import Agently

agent = Agently.create_agent()
agent.load_yaml_prompt("path/to/prompt.yaml")
result = agent.set_request_prompt("input", "Explain recursion.").start()
```

JSON 同理：
```py
agent.load_json_prompt("path/to/prompt.json")
```

---

## 4) 多 prompt 一个文件：`prompt_key_path`

当你需要把多个 prompt 按用途归档在同一个文件里（例如 `demo.output_control`、`demo.qa`）：

```py
agent.load_yaml_prompt("prompts.yaml", prompt_key_path="demo.output_control")
```

建议：
- 一个文件多 prompt 时，命名要稳定（避免频繁改 key 导致引用断裂）。

---

## 5) 从字符串加载（适合配置中心/数据库）

```py
yaml_prompt_text = """
.agent:
  system: You are an Agently enhanced agent.
.request:
  output:
    reply:
      $type: str
"""
agent.load_yaml_prompt(yaml_prompt_text)
```

注意：
- 字符串加载被视为“原始内容”，不是路径。
- 如果你保留 `${...}` 占位符，建议明确 mappings 的注入时机，避免在不同环境解析结果不一致。

---

## 6) roundtrip（把代码 prompt 导出成 YAML/JSON，再导入）

用途：
- 从“可运行代码样例”生成可运维模板；
- 把已稳定的 prompt 固化为文件资产。

```py
req = (
  agent.role("...", always=True)
  .info({"k": "v"}, always=True)
  .input("Say hello.")
  .instruct(["Reply politely."])
  .output({"reply": (str,)})
)
yaml_prompt = req.get_yaml_prompt()
agent2 = Agently.create_agent()
agent2.load_yaml_prompt(yaml_prompt)
```

---

## 7) 最佳实践（通用 checklist）

- Prompt 资产与代码同 repo：`prompts/` 目录集中管理。
- 为关键 prompt 增加离线回归测试：确保 output schema/ensure_keys 的稳定性。
- 避免把环境相关信息写死在 prompt（例如 base_url、API key），统一放 env 或 settings。

