系统出现了问题，让我直接用文本方式给你完整内容，你来保存到文件：

---

# **文件1: MoSim Agent架构设计文档**

保存到：`Docs/Workflows/MoSim_Agent_Architecture_Design.md`

```markdown
# MoSim Agent架构设计文档

> **版本**：v1.0
> **日期**：2026-07-31
> **目标**：初赛Demo - Model Studio内嵌MWORKS仿真分析Agent

---

## 一、总体架构

### 1.1 系统架构图
```

┌─────────────────────────────────────────────────────────────┐
│                    Model Studio (Julia APP)                  │
│  ┌────────────┬────────────┬────────────┬─────────────────┐ │
│  │   建模     │   仿真     │  结果查看  │  AI助手(第4栏) │ │
│  │  Sysplorer │  Runner    │  Viewer    │                 │ │
│  │            │            │            │  ┌────────────┐ │ │
│  │            │            │            │  │用户输入框  │ │ │
│  │            │            │            │  ├────────────┤ │ │
│  │            │            │            │  │对话历史    │ │ │
│  │            │            │            │  │(工具调用)  │ │ │
│  │            │            │            │  └────────────┘ │ │
│  └────────────┴────────────┴────────────┴─────────────────┘ │
│                              │ HTTP                          │
└──────────────────────────────┼───────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Agent Backend      │
                    │  (FastAPI Python)   │
                    │  localhost:8765     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
         ┌────▼─────┐    ┌────▼─────┐    ┌────▼─────┐
         │ Claude   │    │   MCP    │    │   Doc    │
         │   API    │    │  Tools   │    │  Index   │
         │ (Codex)  │    │  (30个)  │    │ (19文档) │
         └──────────┘    └──────────┘    └──────────┘

```

### 1.2 核心组件

**前端（Julia）**：
- `apps/model_studio/src/agent_panel.jl` — 第4栏UI组件
- `apps/model_studio/src/agent_integration.jl` — Agent服务调用层

**后端（Python）**：
- `Scripts/agent/mworks_analysis_agent_server.py` — FastAPI服务
- `Scripts/agent/mcp_tools/` — 30个MCP工具实现
- `Scripts/agent/doc_index.py` — 文档索引构建

**知识库**：
- `Docs/MworksDocs/converted/` — 19个转换后的MWORKS文档
- `Docs/Skills/Mworks/` — 8个Skills（作为工具封装层）
- `Docs/Workflows/` — 50个工作流（作为知识库的一部分）

---

## 二、技术选型

### 2.1 确认的技术栈

| 组件 | 技术选型 | 原因 |
|------|---------|------|
| **LLM** | Claude 3.5 Sonnet (Codex API) | 用户提供API key，支持function calling |
| **Agent框架** | 纯手写（无LangChain/AutoGen） | 轻量、可控、与Codex架构一致 |
| **工具协议** | MCP (Model Context Protocol) | 复用现有MCP工具集，与Codex统一 |
| **后端框架** | FastAPI | 异步、高性能、自动生成API文档 |
| **前端框架** | Julia + Web组件 | Model Studio原生技术栈 |
| **文档检索** | 结构化索引 + 按需读取 | 模仿Codex，不用RAG（初赛） |
| **服务管理** | Model Studio自动启动Agent | 用户体验好，无需手动操作 |

### 2.2 不采用的方案（留给复赛）

- ❌ RAG向量检索（初赛用全文检索）
- ❌ 多轮对话历史（初赛单轮问答）
- ❌ Workflow自动执行（初赛只推荐）
- ❌ QGC Agent（初赛只做MWORKS Agent）

---

## 三、30个MCP工具设计

### 3.1 工具分类

**仿真结果分析类（8个）**：
1. `parse_simulation_csv` — 解析CSV结果文件
2. `compute_controller_metrics` — 计算性能指标（RMSE/超调/调节时间）
3. `compare_controllers` — 多控制器横向对比
4. `extract_simulation_metrics` — 从Result.msr提取指标（via simulation-evidence Skill）
5. `validate_gate_status` — 检查G3门禁状态（via simulation-evidence Skill）
6. `locate_run_record` — 定位RUN_RECORD.json（via simulation-evidence Skill）
7. `diagnose_solver_stall` — 诊断求解器卡死（via runtime-diagnostics Skill）
8. `analyze_mcp_timeout` — 分析MCP超时（via runtime-diagnostics Skill）

**可视化与报告类（6个）**：
9. `generate_trajectory_plot` — 生成轨迹图（via report-visualization Skill）
10. `generate_comparison_chart` — 生成对比图（via report-visualization Skill）
11. `export_report_figure` — 导出图表到Docs/figures/（via report-visualization Skill）
12. `plot_trajectory` — 调用plot_results.py生成4子图
13. `plot_error_curve` — 绘制误差曲线
14. `create_performance_heatmap` — 创建性能热力图

**文档与知识库类（5个）**：
15. `read_mworks_doc_section` — 按需读取MWORKS文档章节
16. `search_doc_index` — 搜索文档索引（返回相关章节列表）
17. `search_modelica_syntax` — Modelica语法查询
18. `search_control_theory` — 控制理论文档查询
19. `list_available_skills` — 列出可用的8个Skills

**模型与配置类（5个）**：
20. `list_available_models` — 列出可用模型（via model-context Skill）
21. `get_model_dependencies` — 查询模型依赖（via model-context Skill）
22. `list_available_profiles` — 列出实验Profile
23. `load_profile_config` — 加载Profile配置
24. `validate_sysblock_connections` — 校验Sysblock连接（via sysblock-graphical-modeling Skill）

**Workflow与测试类（4个）**：
25. `list_workflows` — 列出可用的50个Workflows
26. `recommend_workflow` — 推荐适合的Workflow
27. `run_unit_tests` — 运行单元测试（via test-quality Skill）
28. `validate_golden_reference` — 对比golden（via test-quality Skill）

**系统与辅助类（2个）**：
29. `check_mcp_health` — MCP健康检查（via mcp-operations Skill）
30. `open_file_in_editor` — 在编辑器中打开文件

### 3.2 工具定义示例

```python
# Scripts/agent/mcp_tools/parse_simulation_csv.py

from typing import Dict, List
import pandas as pd

def parse_simulation_csv(csv_path: str, metrics: List[str] = None) -> Dict:
    """
    解析MWORKS仿真结果CSV文件

    Args:
        csv_path: CSV文件路径（相对或绝对）
        metrics: 需要提取的指标列表，如 ["time", "x", "y", "z"]

    Returns:
        {
            "row_count": int,
            "duration_s": float,
            "columns": List[str],
            "data_preview": Dict[str, List[float]],  # 前10行数据
            "statistics": Dict[str, Dict]  # 每列的统计信息
        }
    """
    df = pd.read_csv(csv_path)

    if metrics:
        missing = [m for m in metrics if m not in df.columns]
        if missing:
            raise ValueError(f"CSV缺少必需列: {missing}")

    duration = df['time'].max() - df['time'].min() if 'time' in df.columns else None

    return {
        "row_count": len(df),
        "duration_s": duration,
        "columns": df.columns.tolist(),
        "data_preview": {col: df[col].head(10).tolist() for col in df.columns[:5]},
        "statistics": {
            col: {
                "mean": df[col].mean(),
                "std": df[col].std(),
                "min": df[col].min(),
                "max": df[col].max()
            }
            for col in df.select_dtypes(include='number').columns
        }
    }

# MCP工具注册格式
TOOL_DEFINITION = {
    "name": "parse_simulation_csv",
    "description": "解析MWORKS仿真结果CSV文件，提取数据统计信息",
    "input_schema": {
        "type": "object",
        "properties": {
            "csv_path": {
                "type": "string",
                "description": "CSV文件路径，例如：Results/.../raw/result.csv"
            },
            "metrics": {
                "type": "array",
                "items": {"type": "string"},
                "description": "可选：需要提取的列名列表"
            }
        },
        "required": ["csv_path"]
    }
}
```

---

## 四、文档索引机制

### 4.1 索引结构

**索引文件**：`Docs/MworksDocs/doc_index.json`

```json
{
  "docs": [
    {
      "doc_name": "MWORKS.Syslab控制系统工具箱",
      "doc_path": "Docs/MworksDocs/converted/syslab/MWORKS.Syslab控制系统工具箱.md",
      "category": "syslab",
      "topics": ["控制系统", "PID", "状态反馈", "频域分析"],
      "sections": [
        {
          "title": "1. 控制系统工具箱功能概述",
          "line_start": 48,
          "line_end": 124
        },
        {
          "title": "2. 线性控制系统的数学模型",
          "line_start": 125,
          "line_end": 250
        }
      ]
    },
    ...  // 其余18个文档
  ]
}
```

### 4.2 索引构建脚本

```python
# Scripts/agent/build_doc_index.py

import json
from pathlib import Path
import re

MWORKS_DOCS_DIR = Path("Docs/MworksDocs/converted")

def extract_markdown_sections(md_path: Path):
    """提取Markdown文档的所有二级标题"""
    content = md_path.read_text(encoding='utf-8')
    sections = []

    for match in re.finditer(r'^## (.+)$', content, re.MULTILINE):
        title = match.group(1).strip()
        line_num = content[:match.start()].count('\n') + 1
        sections.append({
            "title": title,
            "line_start": line_num
        })

    # 计算每个section的结束行
    for i in range(len(sections) - 1):
        sections[i]["line_end"] = sections[i+1]["line_start"] - 1
    if sections:
        sections[-1]["line_end"] = content.count('\n')

    return sections

def build_doc_index():
    """构建完整的文档索引"""
    index = {"docs": []}

    for category in ["syslab", "sysplorer", "control", "api", "optimization", "matlab_compat", "challenge"]:
        category_dir = MWORKS_DOCS_DIR / category
        if not category_dir.exists():
            continue

        for md_file in category_dir.glob("*.md"):
            doc_name = md_file.stem
            sections = extract_markdown_sections(md_file)

            index["docs"].append({
                "doc_name": doc_name,
                "doc_path": str(md_file.relative_to(Path.cwd())),
                "category": category,
                "sections": sections
            })

    output_path = Path("Docs/MworksDocs/doc_index.json")
    output_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ 文档索引已生成: {output_path}")
    print(f"📊 共索引 {len(index['docs'])} 个文档")

if __name__ == "__main__":
    build_doc_index()
```

### 4.3 按需读取工具

```python
# Scripts/agent/mcp_tools/read_mworks_doc_section.py

def read_mworks_doc_section(doc_name: str, section_title: str = None) -> str:
    """
    按需读取MWORKS文档的某个章节

    Args:
        doc_name: 文档名称（不含扩展名）
        section_title: 可选：章节标题（如果不指定则返回全文档）

    Returns:
        str: 章节内容（Markdown格式）
    """
    # 1. 从索引中查找文档路径
    index = json.load(open("Docs/MworksDocs/doc_index.json", encoding='utf-8'))
    doc_info = next((d for d in index["docs"] if d["doc_name"] == doc_name), None)

    if not doc_info:
        raise FileNotFoundError(f"未找到文档: {doc_name}")

    doc_path = Path(doc_info["doc_path"])
    content = doc_path.read_text(encoding='utf-8')

    # 2. 如果指定了章节，提取该章节内容
    if section_title:
        section_info = next((s for s in doc_info["sections"] if section_title in s["title"]), None)
        if not section_info:
            available = [s["title"] for s in doc_info["sections"]]
            raise ValueError(f"未找到章节: {section_title}\n可用章节:\n" + "\n".join(available))

        lines = content.splitlines()
        section_content = "\n".join(lines[section_info["line_start"]-1:section_info["line_end"]])
        return section_content

    # 3. 否则返回全文档（但限制长度，避免超context）
    if len(content) > 50000:  # 如果文档过大，返回目录
        sections_list = "\n".join([f"- {s['title']}" for s in doc_info["sections"]])
        return f"# {doc_name}\n\n文档过大，请指定章节标题。可用章节:\n\n{sections_list}"

    return content

# MCP工具注册
TOOL_DEFINITION = {
    "name": "read_mworks_doc_section",
    "description": "按需读取MWORKS官方文档的某个章节（共19个文档）",
    "input_schema": {
        "type": "object",
        "properties": {
            "doc_name": {
                "type": "string",
                "description": "文档名称，例如：MWORKS.Syslab控制系统工具箱"
            },
            "section_title": {
                "type": "string",
                "description": "可选：章节标题，例如：线性控制系统的数学模型"
            }
        },
        "required": ["doc_name"]
    }
}
```

---

## 五、Agent后端服务设计

### 5.1 FastAPI服务结构

```python
# Scripts/agent/mworks_analysis_agent_server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import anthropic
import json
from pathlib import Path

app = FastAPI(title="MoSim MWORKS Analysis Agent")

# CORS配置（允许Model Studio前端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Claude客户端（API key由用户在启动时通过环境变量提供）
claude_client = None

# 加载30个MCP工具定义
def load_mcp_tools():
    tools = []
    tools_dir = Path(__file__).parent / "mcp_tools"
    for tool_file in tools_dir.glob("*.py"):
        module = __import__(f"mcp_tools.{tool_file.stem}", fromlist=["TOOL_DEFINITION"])
        if hasattr(module, "TOOL_DEFINITION"):
            tools.append(module.TOOL_DEFINITION)
    return tools

MCP_TOOLS = load_mcp_tools()

# 系统提示词（完整版本）
SYSTEM_PROMPT = """
你是MWORKS仿真分析专家，精通以下领域：
- MWORKS Sysplorer (Modelica建模)
- MWORKS Syslab (Julia脚本、控制工具箱)
- 控制理论 (PID/LQR/MPC/滑模控制等)
- 四旋翼无人机动力学与控制

## 你的职责

1. 回答用户关于仿真结果的分析问题
2. 调用工具提取数据、计算指标、生成图表
3. 提供专业的控制系统分析建议
4. 采用引导式对话，避免误解用户意图

## 可用工具

你有30个MCP工具可用，按类别分为：
- 仿真结果分析类（8个）：parse_simulation_csv, compute_controller_metrics, compare_controllers, ...
- 可视化与报告类（6个）：generate_trajectory_plot, generate_comparison_chart, ...
- 文档与知识库类（5个）：read_mworks_doc_section, search_doc_index, ...
- 模型与配置类（5个）：list_available_models, list_available_profiles, ...
- Workflow与测试类（4个）：list_workflows, recommend_workflow, ...
- 系统与辅助类（2个）：check_mcp_health, open_file_in_editor

完整工具列表见 Docs/MworksDocs/doc_index.json

## 工作流程

1. **理解用户意图** — 如果问题模糊，先用引导式对话澄清：
   - "你想分析哪个控制器？"
   - "使用哪个场景的结果？"
   - "需要生成图表吗？"

2. **选择合适的工具调用** — 根据用户需求选择1~5个工具

3. **解析工具返回结果** — 提取关键数据

4. **用清晰的语言回答**，包含：
   - 量化指标（RMSE/超调量/调节时间等）
   - 原因分析（为什么这个控制器更好）
   - 改进建议（如何优化参数）
   - 相关工作流（如果有对应的Workflow，在末尾注明）

## 当前上下文

工作空间：{workspace_dir}
当前打开的结果：{current_result_path}
可用的控制器：{available_controllers}

## 注意事项

- ❌ 不要修改模型文件或配置文件
- ❌ 不要启动仿真（check_model/simulate）
- ✅ 只进行只读分析
- ✅ 如果工具调用失败，提供友好的错误提示和建议操作
- ✅ 优先使用引导式对话，确保理解用户真实需求
"""

# 请求模型
class QueryRequest(BaseModel):
    question: str
    context: Optional[Dict] = {}

class QueryResponse(BaseModel):
    answer: str
    tools_used: List[str]
    conversation_history: List[Dict]

@app.on_event("startup")
async def startup():
    global claude_client
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  警告：未设置ANTHROPIC_API_KEY环境变量")
    else:
        claude_client = anthropic.Anthropic(api_key=api_key)
        print("✅ Claude客户端初始化成功")

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "tools_count": len(MCP_TOOLS),
        "claude_ready": claude_client is not None
    }

@app.post("/mworks/query", response_model=QueryResponse)
async def query_agent(req: QueryRequest):
    """
    MWORKS仿真分析查询接口
    """
    if not claude_client:
        raise HTTPException(500, "Claude API未初始化，请检查API key")

    # 构造完整的系统提示词（注入当前上下文）
    system_prompt = SYSTEM_PROMPT.format(
        workspace_dir=req.context.get("workspace_dir", "未知"),
        current_result_path=req.context.get("current_result_path", "未打开"),
        available_controllers=req.context.get("available_controllers", "未扫描")
    )

    # 初始消息
    messages = [{"role": "user", "content": req.question}]
    tools_used = []
    max_turns = 5  # 最多5轮工具调用（防止无限循环）

    for turn in range(max_turns):
        # 调用Claude API（带工具调用）
        try:
            response = claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=system_prompt,
                tools=MCP_TOOLS,
                messages=messages
            )
        except anthropic.APITimeoutError:
            # 自动重试3次（指数退避）
            for attempt in range(3):
                try:
                    import time
                    time.sleep(2 ** attempt)
                    response = claude_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=4096,
                        system=system_prompt,
                        tools=MCP_TOOLS,
                        messages=messages
                    )
                    break
                except anthropic.APITimeoutError:
                    if attempt == 2:
                        return QueryResponse(
                            answer="抱歉，服务暂时不可用（网络超时），请稍后重试。",
                            tools_used=[],
                            conversation_history=messages
                        )

        # 如果Claude直接回答（没有工具调用）
        if response.stop_reason != "tool_use":
            final_answer = next((block.text for block in response.content if block.type == "text"), "")
            return QueryResponse(
                answer=final_answer,
                tools_used=tools_used,
                conversation_history=messages
            )

        # 提取工具调用
        tool_calls = [block for block in response.content if block.type == "tool_use"]

        # 执行工具调用
        tool_results = []
        for tool_call in tool_calls:
            tool_name = tool_call.name
            tool_input = tool_call.input
            tools_used.append(tool_name)

            try:
                # 动态加载并执行工具
                module = __import__(f"mcp_tools.{tool_name}", fromlist=[tool_name])
                tool_func = getattr(module, tool_name)
                result = tool_func(**tool_input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            except FileNotFoundError as e:
                # 友好的错误提示
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": json.dumps({
                        "error": "文件不存在",
                        "message": str(e),
                        "suggestion": "请检查路径是否正确，或运行 list_available_controllers 查看可用结果"
                    }, ensure_ascii=False)
                })
            except Exception as e:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": json.dumps({
                        "error": type(e).__name__,
                        "message": str(e)
                    }, ensure_ascii=False)
                })

        # 将工具结果加入对话历史
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    # 如果达到最大轮数，返回最后一次回答
    return QueryResponse(
        answer="对话已达到最大轮数限制，请重新提问",
        tools_used=tools_used,
        conversation_history=messages
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
```

---

## 六、Model Studio前端集成

### 6.1 Agent服务自动管理

```julia
# apps/model_studio/src/agent_integration.jl

using HTTP, JSON3
using Sockets  # 用于端口检查

const AGENT_PORT = 8765
const AGENT_URL = "http://localhost:$AGENT_PORT"

global agent_process = nothing

"""检查Agent服务是否健康"""
function check_agent_service_health()
    try
        response = HTTP.get("$AGENT_URL/health", retry=false, readtimeout=2)
        health = JSON3.read(response.body)
        return health.status == "ok" && health.claude_ready
    catch
        return false
    end
end

"""启动Agent后端服务"""
function start_agent_service()
    global agent_process

    @info "正在启动MWORKS Analysis Agent服务..."

    # 获取Python路径
    python_exe = get(ENV, "PYTHON", "python")

    # 启动FastAPI服务（后台运行）
    agent_script = joinpath(pwd(), "Scripts", "agent", "mworks_analysis_agent_server.py")
    agent_process = run(`$python_exe $agent_script --port $AGENT_PORT`, wait=false)

    # 等待服务就绪（最多30秒）
    for i in 1:30
        sleep(1)
        if check_agent_service_health()
            @info "✅ Agent服务启动成功 (端口: $AGENT_PORT)"
            return true
        end
    end

    @error "❌ Agent服务启动失败（超时30秒）"
    return false
end

"""停止Agent服务"""
function stop_agent_service()
    global agent_process
    if agent_process !== nothing
        kill(agent_process)
        @info "Agent服务已停止"
    end
end

"""确保Agent服务运行中"""
function ensure_agent_service()
    if !check_agent_service_health()
        start_agent_service()
    end
end

"""查询Agent"""
function query_mworks_agent(question::String; context::Dict=Dict())
    ensure_agent_service()

    try
        response = HTTP.post(
            "$AGENT_URL/mworks/query",
            ["Content-Type" => "application/json"],
            body=JSON3.write(Dict(
                "question" => question,
                "context" => context
            ))
        )

        return JSON3.read(response.body)
    catch e
        @error "Agent查询失败" exception=e
        return Dict(
            "answer" => "抱歉，查询失败：$(sprint(showerror, e))",
            "tools_used" => [],
            "conversation_history" => []
        )
    end
end

# 注册退出钩子
atexit(stop_agent_service)
```

### 6.2 第4栏UI组件

```julia
# apps/model_studio/src/agent_panel.jl

using Genie, Stipple, StippleUI
using Dates

@reactive mutable struct AgentPanelModel <: ReactiveModel
    user_input::R{String} = ""
    chat_history::R{Vector{Dict}} = []
    is_loading::R{Bool} = false
    current_workspace::R{Dict} = Dict()
end

function render_agent_panel(workspace_state)
    model = Ag
```
