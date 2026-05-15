# MCP Modeling Toolkit

本文件给出 NPSLibrary 建模各阶段推荐的 MCP 工具映射。

---

## 1. 会话与库

| Task | Preferred Tool |
|------|----------------|
| 检查/确保 Sysplorer 就绪 | `session_manager(action="ensure")` |
| 查看状态 | `session_manager(action="health")` |
| 加载 NPSLibrary | `load_library(library_name="NPSLibrary")` |

---

## 2. 模型生命周期

| Task | Preferred Tool |
|------|----------------|
| 新建模型 | `model_manager(action="new")` |
| 加载 `.mo` 文件 | `model_manager(action="load_file")` |
| 打开模型 | `model_manager(action="open")` |
| 保存模型 | `model_manager(action="save")` |
| 获取组件/端口/文本 | `model_manager(action="get_components" / "get_component_ports" / "get_model_text")` |

---

## 3. 建模与布局

优先顺序：

1. 能用官方 MCP 工具直接完成的，先用 MCP 工具
2. 需要较复杂的批量建模操作时，再用 `call_code(mode="run_script")`
3. 图面布局需要自动整理时，使用 `smart_layout`

注意：

- `run_script` 内必须先显式 `import mworks.sysplorer as ModelingPy`
- 不要假定脚本环境中天然存在 `ModelingPy`
- 推荐调用形式为 `call_code(mode="run_script", payload={"python_source": "...", "capture_stdout": true, "capture_stderr": true})`
- `payload.python_source` 不能为空；若为空，必须提供有效的 `payload.script_path`
- 若出现 `python_source is empty`、payload 格式错误或 JSON 编码失败，应先修 `call_code` 调用本身，不得直接改走整段文本注入建模
- 图形建模场景下，`call_code` 失败后应继续修 GUI 路径相关调用，如 `AddComponent` / `ConnectPort`，而不是跳到 `SetModelText`
- 在最小 `run_script` 验证通过前，不要改走 `SetModelText`、`SetModelCode` 或 `load_file` 后修 `.mo` 文本的补锅路径

推荐排障顺序：

1. 先用最小 `run_script` 验证调用链路是否通
2. 再提交真正的建模脚本
3. 若报 `python_source is empty`，优先检查 `payload.python_source`
4. 若报 JSON 相关错误，先缩短脚本、减少转义和嵌套
5. 最小脚本未通过前，不要提交 `AddComponent` / `ConnectPort` 大脚本

最小正确示例：

```text
call_code(
  mode="run_script",
  payload={
    "python_source": "import mworks.sysplorer as ModelingPy\nRUN_SCRIPT_RESULT = {'ok': True}",
    "capture_stdout": true,
    "capture_stderr": true
  }
)
```

---

## 4. 检查、翻译、仿真

| Step | Preferred Tool | Typical Purpose |
|------|----------------|-----------------|
| Check | `check_model` | 结构、参数、电气一致性检查 |
| Translate | `translate_model` | 翻译数学模型 |
| Simulate | `simulate_model` | 运行仿真 |
| Result Readback | `result_manager` | 读变量、时序、时刻值 |
| Plot | `plot_manager` | 绘图与动画 |

---

## 5. 推荐调用节奏

```text
session_manager ensure
-> load_library(NPSLibrary)
-> model_manager new/open/load
-> 建模/连线/参数写入
-> check_model
-> translate_model
-> simulate_model
-> result_manager / plot_manager
```

---

## 6. 什么时候进入修复闭环

- `check_model` 返回不通过
- `translate_model` 失败
- `simulate_model` 失败或结果异常
- `result verify` 结论不通过
- `LoadFlowBus` / `Powergui` 初始化不一致
- `PLL`、PWM、采样周期或高频开关导致结果异常
