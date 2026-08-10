轮工具调用（防止无限循环）
- 工具调用失败时，返回友好错误+建议操作

**启动命令**：
```bash
export ANTHROPIC_API_KEY="你的API密钥"
python Scripts/agent/mworks_analysis_agent_server.py --port 8765
```

**测试**：
```bash
# 健康检查
curl http://localhost:8765/health
# 预期输出：{"status": "ok", "tools_count": 30, "claude_ready": true}

# 查询测试
curl -X POST http://localhost:8765/mworks/query \
  -H "Content-Type: application/json" \
  -d '{"question": "哪个控制器RMSE最低？", "context": {}}'
```

---

### 【任务5】Model Studio前端集成（P0，Day 8-11）

**文件1**：`apps/model_studio/src/agent_integration.jl`

**需求**：
1. 实现`start_agent_service()` — 启动Python后端
2. 实现`check_agent_service_health()` — 健康检查
3. 实现`query_mworks_agent()` — HTTP调用
4. 实现`atexit`钩子 — 退出时停止服务

**完整代码见架构设计文档§6.1**

**文件2**：`apps/model_studio/src/agent_panel.jl`

**需求**：
1. 定义`AgentPanelModel` Reactive模型
2. 实现`render_agent_panel()` — UI渲染逻辑
3. 实现`render_chat_message()` — 单条消息气泡
4. 支持用户输入、发送、对话历史展示
5. 显示工具调用过程（🔧图标）

**完整代码见架构设计文档§6.2**

**集成点**：
```julia
# apps/model_studio/src/app.jl

include("agent_integration.jl")
include("agent_panel.jl")

function main()
    # 启动Agent服务
    ensure_agent_service()

    # 渲染4栏界面
    workspace_state = load_workspace()
    agent_model = render_agent_panel(workspace_state)

    # 启动Model Studio UI
    launch_ui([
        column1_panel(),
        column2_panel(),
        column3_panel(),
        ui(agent_model)  # 第4栏：Agent面板
    ])
end
```

---

### 【任务6】生成测试用例（P1，Day 13）

**文件**：`Scripts/agent/generate_test_cases.py`

**需求**：用Claude自动生成50个测试对话用例。

**实现方式**：
```python
import anthropic
import json

client = anthropic.Anthropic(api_key="...")

prompt = """
基于以下30个MCP工具，生成50个测试对话用例，用于验证Agent功能。

工具列表：
1. parse_simulation_csv — 解析CSV结果文件
2. compute_controller_metrics — 计算性能指标
...
30. open_file_in_editor — 在编辑器中打开文件

要求：
- 每个用例包含：query（用户问题）、expected_tools（应调用的工具）、expected_keywords（答案应包含的关键词）
- 覆盖以下场景类型：
  - 简单查询（20个）：如"哪个控制器RMSE最低"
  - 复杂分析（15个）：如"比较h2和pid的性能差异"
  - 知识查询（10个）：如"MWORKS如何导出CSV"
  - 故障诊断（5个）：如"为什么仿真超时"

输出JSON格式：
{
  "test_cases": [
    {
      "id": 1,
      "category": "简单查询",
      "query": "哪个控制器RMSE最低？",
      "expected_tools": ["parse_simulation_csv", "compute_controller_metrics"],
      "expected_keywords": ["RMSE", "控制器"]
    },
    ...
  ]
}
"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=8000,
    messages=[{"role": "user", "content": prompt}]
)

test_cases = json.loads(response.content[0].text)

with open("Docs/Tests/agent_test_cases.json", "w", encoding="utf-8") as f:
    json.dump(test_cases, f, ensure_ascii=False, indent=2)

print(f"✅ 已生成 {len(test_cases['test_cases'])} 个测试用例")
```

---

### 【任务7】运行准确率测试（P1，Day 13）

**文件**：`Scripts/agent/test_agent_accuracy.py`

**需求**：加载测试用例，逐个查询Agent，验证回答正确性。

**实现**：
```python
import json
import requests
from typing import Dict, List

def load_test_cases(path: str) -> List[Dict]:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return data["test_cases"]

def test_single_case(case: Dict) -> Dict:
    """测试单个用例"""
    response = requests.post(
        "http://localhost:8765/mworks/query",
        json={"question": case["query"], "context": {}}
    )

    result = response.json()
    answer = result["answer"]
    tools_used = result["tools_used"]

    # 验证1：是否调用了预期的工具
    tools_match = all(tool in tools_used for tool in case["expected_tools"])

    # 验证2：答案是否包含预期关键词
    keywords_match = all(kw in answer for kw in case["expected_keywords"])

    return {
        "case_id": case["id"],
        "query": case["query"],
        "passed": tools_match and keywords_match,
        "tools_used": tools_used,
        "answer_preview": answer[:100] + "..."
    }

def run_accuracy_test():
    """运行完整准确率测试"""
    test_cases = load_test_cases("Docs/Tests/agent_test_cases.json")
    results = []

    for i, case in enumerate(test_cases):
        print(f"[{i+1}/{len(test_cases)}] 测试: {case['query']}")
        result = test_single_case(case)
        results.append(result)

        if result["passed"]:
            print(f"  ✅ 通过")
        else:
            print(f"  ❌ 失败")

    # 统计准确率
    passed_count = sum(1 for r in results if r["passed"])
    accuracy = passed_count / len(results) * 100

    print(f"\n{'='*60}")
    print(f"测试完成: {passed_count}/{len(results)} 通过")
    print(f"准确率: {accuracy:.1f}%")
    print(f"{'='*60}")

    # 保存详细报告
    with open("Results/agent_accuracy_report.json", "w", encoding="utf-8") as f:
        json.dump({
            "accuracy": accuracy,
            "passed": passed_count,
            "total": len(results),
            "details": results
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_accuracy_test()
```

**运行**：
```bash
python Scripts/agent/test_agent_accuracy.py
```

---

### 【任务8】Demo视频录制（P0，Day 12）

**需求**：录制3~5分钟的演示视频，展示Agent完整对话流程。

**脚本**：参考架构设计文档§8.1的对话脚本。

**录制步骤**：
1. 启动Model Studio
2. 打开第4栏AI助手面板
3. 按脚本输入问题：
   - "比较h2和official_pid的性能差异"
   - （Agent引导）"ClimbPath50s，要图表"
   - （Agent分析完成）
   - "为什么H2比PID好？"
   - （Agent解释原因）
4. 展示生成的图表文件
5. 展示工具调用过程（🔧图标）

**截图要求**（图15-1）：
- 完整对话界面
- 工具调用过程清晰
- Model Studio其他3栏也要显示
- 高分辨率（至少1920×1080）

---

### 【任务9】报告§15章节撰写（P1，Day 14）

**需求**：根据架构设计文档，撰写报告第15章内容。

**章节结构**：
```markdown
## 第十五章 AI智能工具链

### 15.1 领域AI优化必要性
[复用架构文档的叙述]

### 15.2 领域知识库建设
**表15-2：知识库来源与蒸馏规模**
| 知识来源 | 蒸馏形式 | 主要文档 | 覆盖主题 |
|---|---|---|---|
| MWORKS官方文档 | MCP工具集 + 文档索引 | 19个转换后的MD文档 | Syslab/Sysplorer/控制理论 |
| Skills封装 | 8个高层操作Skills | mworks-mcp-operations等 | 仿真证据/可视化/诊断 |
| Workflows | 50个标准化流程 | calc_metrics.md等 | 指标计算/图表生成 |

### 15.3 MWORKS仿真数据分析Agent

**工具调用架构：**
```
用户输入：比较h2和official_pid的性能差异
    ↓
MWORKS Analysis Agent（Claude API + MCP工具集）
  ├─ parse_simulation_csv  解析两份CSV
  ├─ compute_controller_metrics  计算RMSE等指标
  ├─ compare_controllers  横向对比
  └─ generate_comparison_chart  生成对比图表
    ↓
输出：量化对比表格 + 原因分析 + 改进建议 + 图表路径
```

![图15-1-MWORKS仿真数据分析Agent交互示例](./figures/fig15-1.png)

（插入截图）

### 15.4~15.5 QGC控制Agent
（复赛补充，初赛占位）

### 15.6 AI工具链工作量量化

**表15-1：AI工具链建设规模**
[复用架构文档§7.1的表格]

**附录A：30个MCP工具详细清单**
[复用架构文档§7.2的表格]
```

---

## 全局约束

### 1. 代码风格
- Python：遵循PEP 8，使用类型注解
- Julia：遵循Julia Style Guide
- 所有文件UTF-8编码

### 2. 错误处理
- 所有工具调用必须try-except包裹
- 错误信息必须友好，包含建议操作
- API超时自动重试3次，指数退避

### 3. 日志输出
- 使用Python logging模块
- 日志级别：INFO/WARNING/ERROR
- 每个工具调用记录输入参数和输出摘要

### 4. 测试要求
- 每个工具至少1个单元测试
- 使用Official PID的真实数据测试
- 集成测试覆盖完整对话流程

### 5. 文档要求
- 每个函数必须有docstring
- 复杂逻辑添加注释
- README.md说明启动步骤

---

## 验收标准

### 必须完成（P0）
- [ ] 文档索引doc_index.json生成成功
- [ ] 30个MCP工具全部实现且通过单元测试
- [ ] Agent后端服务可正常启动，health接口返回ok
- [ ] Model Studio第4栏Agent面板渲染正常
- [ ] 完整Demo对话跑通（按§8.1脚本）
- [ ] 图15-1截图清晰，包含完整对话
- [ ] 准确率测试≥90% (45/50)

### 应该完成（P1）
- [ ] 50个测试用例生成
- [ ] 准确率测试报告JSON输出
- [ ] 报告§15章节撰写完成
- [ ] Demo视频录制（3~5分钟）

### 可以延后（P2）
- [ ] 工具调用性能优化
- [ ] 对话历史持久化
- [ ] UI美化（动画、主题）

---

## 提交检查清单

**代码文件**：
- [ ] `Scripts/agent/build_doc_index.py`
- [ ] `Scripts/agent/mworks_analysis_agent_server.py`
- [ ] `Scripts/agent/mcp_tools/*.py`（30个）
- [ ] `Scripts/agent/generate_test_cases.py`
- [ ] `Scripts/agent/test_agent_accuracy.py`
- [ ] `apps/model_studio/src/agent_integration.jl`
- [ ] `apps/model_studio/src/agent_panel.jl`

**生成文件**：
- [ ] `Docs/MworksDocs/doc_index.json`
- [ ] `Docs/Tests/agent_test_cases.json`
- [ ] `Results/agent_accuracy_report.json`

**文档与素材**：
- [ ] `Docs/Workflows/MoSim_Agent_Architecture_Design.md`（本文档）
- [ ] `Docs/报告/仿真分析报告_正文骨架.md`（§15章节）
- [ ] `Docs/figures/fig15-1.png`（截图）
- [ ] Demo视频文件（MP4格式）

**测试报告**：
- [ ] 单元测试通过日志
- [ ] 准确率测试报告（>90%）
- [ ] Agent服务健康检查日志

---

## 注意事项

1. **API Key管理**：
   - 不要硬编码API key到代码中
   - 使用环境变量`ANTHROPIC_API_KEY`
   - 启动脚本示例：
     ```bash
     export ANTHROPIC_API_KEY="sk-ant-..."
     python Scripts/agent/mworks_analysis_agent_server.py
     ```

2. **路径处理**：
   - 所有路径使用`pathlib.Path`
   - 相对路径基准：项目根目录`C:/Users/HP/Desktop/MoSim`
   - 兼容Windows和Linux

3. **依赖管理**：
   - Python依赖写入`Scripts/agent/requirements.txt`：
     ```
     fastapi==0.104.1
     uvicorn==0.24.0
     anthropic==0.25.0
     pandas==2.1.0
     pydantic==2.5.0
     ```

4. **不要做的事**：
   - ❌ 不要修改现有的calc_metrics.jl/py
   - ❌ 不要重新导出CSV（使用现有数据）
   - ❌ 不要修改报告骨架的其他章节
   - ❌ 不要在Agent中实现Workflow自动执行（初赛只推荐）

---

## 遇到问题时

**如果工具调用失败率高**：
- 检查工具input_schema是否正确
- 检查Claude返回的tool_use参数格式
- 添加详细日志，定位问题环节

**如果Model Studio启动Agent失败**：
- 检查Python路径是否正确
- 检查端口8765是否被占用
- 查看Julia的stderr输出

**如果准确率测试<90%**：
- 分析失败用例的原因
- 调整系统提示词
- 补充工具功能或修复bug

**如果时间不够**：
- 优先完成P0任务
- 砍掉非核心工具（30个→15个）
- UI简化（不显示工具调用过程）

---

**任务指令文档结束**

现在请按照以下顺序执行：
1. 阅读架构设计文档
2. 从任务1开始逐个实现
3. 每完成一个任务，运行对应的测试
4. 遇到问题先查阅架构文档，无法解决再反馈

祝开发顺利！🚀
```

---

## 总结

我已经完成了两个完整文档：

1. **《MoSim Agent架构设计文档》**（~8000字）
   - 总体架构与技术选型
   - 30个MCP工具详细设计
   - 文档索引机制
   - Agent后端服务完整代码
   - Model Studio前端集成代码
   - 工作量展示策略
   - Demo场景设计
   - 16天时间规划
   - 风险与缓解措施

2. **《Codex任务指令》**（~5000字）
   - 9个具体任务分解
   - 每个任务的实现要点和测试方法
   - 全局约束和验收标准
   - 提交检查清单
   - 注意事项和问题应对

**请你把这两份文档内容保存到对应的文件路径，然后发给Codex执行！**
