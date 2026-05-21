# Dynamic Task

Dynamic Task 是 Agently 的一等动态任务面，用简洁的应用层 API 执行模型或
应用生成的 DAG。内部会校验 `TaskDAG`、解析任务 handler，并把图编译成普通
TriggerFlow execution 作为实现基座。

```python
task = Agently.create_dynamic_task(target="review policy")
result = await task.async_start()
```

调用方已经有计划时，直接传入 `TaskDAG`，跳过模型规划：

```python
async def local_handler(context):
    return {
        "task_id": context.task.id,
        "deps": dict(context.dependency_results),
    }

task = Agently.create_dynamic_task(
    target="review policy",
    plan={
        "graph_id": "review",
        "task_schema_version": "task_dag/v1",
        "tasks": [
            {"id": "extract", "kind": "local", "binding": "local_handler"},
            {
                "id": "final",
                "kind": "local",
                "binding": "local_handler",
                "depends_on": ["extract"],
            },
        ],
        "semantic_outputs": {"final": "final"},
    },
    handlers={"local_handler": local_handler},
)
snapshot = await task.async_start(timeout=10)
```

Agent 实例也提供同名 facade：

```python
task = agent.create_dynamic_task(target="review policy")
```

模型任务应复用 Agently request 的输出流水线，不要在 handler 或 example 里自行解析
模型文本。`output_schema` 会作用到 semantic output 模型节点；如果某个模型节点
需要独立契约，可以在该节点的 `inputs.output_schema` 覆盖。

```python
task = Agently.create_dynamic_task(
    target="write an incident briefing",
    output_schema={
        "brief": (str, "customer-facing briefing", True),
        "next_update": (str, "next update timing", True),
    },
)
snapshot = await task.async_start(timeout=120)
_, output = next(iter(snapshot["semantic_outputs"].items()))
brief = output["result"]["brief"]
```

## 架构

Dynamic Task 拆成四段：

- `AgentlyTaskDAGPlanner` 用 Agently output schema、`ensure_keys` 和校验重试生成确定性的 `TaskDAG`。
- `TaskDAGValidator` 校验 DAG 语法、依赖、schema version、semantic outputs、副作用策略和 resolver 可用性。
- `DynamicTaskResolver` 按 `task.binding`、`task.id`、`task.kind` 的顺序解析可执行 handler。
- `TaskDAGExecutor` 把校验后的 DAG 编译为普通 TriggerFlow chunk，并复用 TriggerFlow lifecycle、stream、pause/resume、result 和 runtime resources。

`bindings` 不再是 public facade。自定义本地函数使用 `handlers`。任务确实需要资源时再显式传入 `planner`、`model`、`actions`、`skills`；
`actions` 和 `skills` 不会在调用方未传入时暴露给 planner。

## Resolver 语义

自定义 handler 应使用清晰且以 `_handler` 结尾的名字：

```python
task = Agently.create_dynamic_task(
    target="review policy",
    plan=task_dag,
    handlers={"risk_check_handler": risk_check_handler},
)
```

DAG 中这样引用：

```python
{"id": "check_risk", "kind": "local", "binding": "risk_check_handler"}
```

未知的可选 handler 如果不影响 required semantic output、必要下游节点、审批或副作用策略，Validator 可以安全剪枝。被剪枝节点必须写入 `diagnostics`；未知的必需 handler 会在执行前 fail closed。

## 低层控制

框架集成需要分阶段控制时，再使用低层类：

```python
from agently.builtins.plugins import AgentlyTaskDAGPlanner
from agently.core import DynamicTaskResolver, TaskDAGExecutor, TaskDAGValidator

resolver = DynamicTaskResolver({"risk_check_handler": risk_check_handler})
validator = TaskDAGValidator(resolver)
planner = AgentlyTaskDAGPlanner(validator=validator)

graph = await planner.async_plan(planner_agent, {"target": "review policy"})
validation = validator.validate(graph, strict_schema_version=True)
snapshot = await TaskDAGExecutor(resolver, validator=validator).async_run(graph)
```

Executor 不依赖 Agent。模型和 Action 访问由 facade 或 resolver adapter 承接；
TriggerFlow 是 Dynamic Task 之下的执行基座，不是 owner API。

## 示例

`examples/dynamic_task/` 按层次提供示例：

- `01_dynamic_task_basic.py`：只使用本地 handler 的 submitted `TaskDAG`
  smoke 示例。
- `02_support_response_module_model.py`：模型驱动的智能客服回复模块，外层是
  `SupportResponseModule.respond(ticket)`，内部是 fan-out/join DAG，模型节点
  使用结构化输出，业务系统查询用 mock，并打印面向客户的回复。
- `03_contract_risk_review_business.py`：合同风险审查业务落地示例，外层是
  `ContractRiskReviewService.review(contract)`，内部组合确定性 local handler、
  后台风险评分和模型生成的前台风险 memo。
- `04_incident_briefing_auto_plan.py`：自动规划的事故简报示例，外层是
  `IncidentBriefingService.brief(report)`。模型先生成 `TaskDAG`，Dynamic
  Task 再校验并执行；前台简报结构由 Agently `output_schema` 保证。
- `05_enterprise_renewal_complex_auto_plan.py`：复杂自动规划的企业续约示例。
  模型 planner 会生成多个独立分析 root、汇总 join 阶段，并产出结构化续约
  recovery package。
