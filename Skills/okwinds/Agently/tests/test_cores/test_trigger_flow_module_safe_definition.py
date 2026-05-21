import pytest

from agently import TriggerFlow, TriggerFlowRuntimeData


def _operators(flow: TriggerFlow):
    return flow.get_flow_config(validate_serializable=False)["operators"]


def _operators_by_kind(flow: TriggerFlow, kind: str):
    return [operator for operator in _operators(flow) if operator["kind"] == kind]


@pytest.mark.asyncio
async def test_trigger_flow_replayed_named_chain_is_module_safe():
    flow = TriggerFlow(name="module-safe-chain")

    async def analyze(data: TriggerFlowRuntimeData):
        count = data.get_state("analyze_count", 0) or 0
        await data.async_set_state("analyze_count", count + 1, emit=False)
        return data.value + 1

    async def answer(data: TriggerFlowRuntimeData):
        count = data.get_state("answer_count", 0) or 0
        await data.async_set_state("answer_count", count + 1, emit=False)
        return data.value * 2

    def assemble():
        flow.to(analyze).to(answer)

    assemble()
    operator_count = len(_operators(flow))
    assemble()

    assert len(_operators(flow)) == operator_count
    assert len(_operators_by_kind(flow, "chunk")) == 2

    result = await flow.async_start(3, auto_close_timeout=0.01)
    assert result["analyze_count"] == 1
    assert result["answer_count"] == 1


@pytest.mark.asyncio
async def test_trigger_flow_same_callable_can_be_named_as_distinct_stages():
    flow = TriggerFlow(name="named-distinct-stages")

    async def step(data: TriggerFlowRuntimeData):
        values = list(data.get_state("values", []) or [])
        values.append(data.value)
        await data.async_set_state("values", values, emit=False)
        return data.value + 1

    flow.to(step, name="first_step").to(step, name="second_step")

    chunk_operators = _operators_by_kind(flow, "chunk")
    assert len(chunk_operators) == 2
    assert {operator["name"] for operator in chunk_operators} == {"first_step", "second_step"}

    result = await flow.async_start(1, auto_close_timeout=0.01)
    assert result["values"] == [1, 2]


def test_trigger_flow_anonymous_append_only_but_named_lambda_is_idempotent():
    anonymous_flow = TriggerFlow(name="anonymous-append")
    anonymous_flow.to(lambda data: data.value)
    anonymous_flow.to(lambda data: data.value)
    assert len(_operators_by_kind(anonymous_flow, "chunk")) == 2

    named_flow = TriggerFlow(name="named-lambda-idempotent")
    handler = lambda data: data.value
    named_flow.to(handler, name="identity")
    named_count = len(_operators(named_flow))
    named_flow.to(handler, name="identity")
    assert len(_operators(named_flow)) == named_count


def test_trigger_flow_same_name_with_different_callable_fails_fast():
    flow = TriggerFlow(name="named-conflict")

    async def first(data: TriggerFlowRuntimeData):
        return data.value

    async def second(data: TriggerFlowRuntimeData):
        return data.value

    flow.to(first, name="stage")
    with pytest.raises(ValueError, match="already registered to another callable"):
        flow.to(second, name="stage")


@pytest.mark.asyncio
async def test_trigger_flow_existing_execution_is_not_polluted_by_later_definition_replay():
    flow = TriggerFlow(name="execution-snapshot-definition-replay")

    async def remember(data: TriggerFlowRuntimeData):
        count = data.get_state("count", 0) or 0
        await data.async_set_state("count", count + 1, emit=False)
        return data.value

    flow.to(remember)
    execution = flow.create_execution(auto_close=False)
    flow.to(remember)

    await execution.async_start("ok")
    result = await execution.async_close()

    assert result["count"] == 1


@pytest.mark.asyncio
async def test_trigger_flow_replayed_when_edge_does_not_dedupe_runtime_emit_nowait():
    flow = TriggerFlow(name="when-runtime-events")

    async def kick(data: TriggerFlowRuntimeData):
        data.emit_nowait("Tick", 1)
        data.emit_nowait("Tick", 2)
        data.emit_nowait("Tick", 3)

    async def on_tick(data: TriggerFlowRuntimeData):
        values = list(data.get_state("ticks", []) or [])
        values.append(data.value)
        await data.async_set_state("ticks", values, emit=False)

    flow.to(kick)
    flow.when("Tick").to(on_tick)
    operator_count = len(_operators(flow))
    flow.when("Tick").to(on_tick)

    assert len(_operators(flow)) == operator_count

    result = await flow.async_start(None, auto_close_timeout=0.03)
    assert result["ticks"] == [1, 2, 3]


@pytest.mark.asyncio
async def test_trigger_flow_replayed_when_and_join_is_module_safe_and_execution_local():
    flow = TriggerFlow(name="when-and-module-safe")

    async def joined(data: TriggerFlowRuntimeData):
        await data.async_set_state("joined", data.value, emit=False)
        return data.value

    flow.when({"event": ["A", "B"]}, mode="and").to(joined)
    operator_count = len(_operators(flow))
    flow.when({"event": ["A", "B"]}, mode="and").to(joined)

    assert len(_operators(flow)) == operator_count
    assert len(_operators_by_kind(flow, "signal_gate")) == 1

    execution_1 = flow.create_execution(auto_close=False)
    execution_2 = flow.create_execution(auto_close=False)

    await execution_1.async_emit("A", "a1")
    await execution_2.async_emit("A", "a2")
    assert execution_1.get_state("joined") is None
    assert execution_2.get_state("joined") is None

    await execution_1.async_emit("B", "b1")
    assert execution_1.get_state("joined") == {"event": {"A": "a1", "B": "b1"}}
    assert execution_2.get_state("joined") is None

    await execution_2.async_emit("B", "b2")
    assert execution_2.get_state("joined") == {"event": {"A": "a2", "B": "b2"}}

    await execution_1.async_close()
    await execution_2.async_close()


def test_trigger_flow_load_flow_config_replay_is_idempotent_and_conflicts_fail_fast():
    flow = TriggerFlow(name="config-replay")

    async def worker(data: TriggerFlowRuntimeData):
        return data.value

    flow.to(worker)
    config = flow.get_flow_config()

    restored = TriggerFlow()
    restored.register_chunk_handler(worker)
    restored.load_flow_config(config, replace=False)
    operator_count = len(_operators(restored))
    restored.load_flow_config(config, replace=False)

    assert len(_operators(restored)) == operator_count

    conflict_config = {
        **config,
        "operators": [
            {
                **config["operators"][0],
                "name": "conflicting-worker",
            },
            *config["operators"][1:],
        ],
    }
    with pytest.raises(ValueError, match="different definition"):
        restored.load_flow_config(conflict_config, replace=False)


@pytest.mark.asyncio
async def test_trigger_flow_dynamic_todo_dag_executor_uses_task_id_identities():
    extract_template = TriggerFlow(name="extract-template")
    analyze_template = TriggerFlow(name="analyze-template")

    async def extract(data: TriggerFlowRuntimeData):
        return f"extract:{ data.value['task_id'] }:{ data.value['doc'] }"

    async def analyze(data: TriggerFlowRuntimeData):
        deps = ",".join(f"{ key }={ value }" for key, value in sorted(data.value["deps"].items()))
        return f"analyze:{ data.value['task_id'] }:{ deps }"

    extract_template.to(extract).end()
    analyze_template.to(analyze).end()
    extract_template_operator_count = len(_operators(extract_template))
    analyze_template_operator_count = len(_operators(analyze_template))

    plan = {
        "tasks": [
            {"id": "extract_terms", "kind": "extract", "depends_on": []},
            {"id": "analyze_risk", "kind": "analyze", "depends_on": ["extract_terms"]},
            {
                "id": "final_review",
                "kind": "analyze",
                "depends_on": ["extract_terms", "analyze_risk"],
            },
        ]
    }
    kickoff_cache = {}
    collector_cache = {}
    emitter_cache = {}

    def template_for(task):
        return extract_template if task["kind"] == "extract" else analyze_template

    def collector_for(task):
        if task["id"] not in collector_cache:

            async def collect(data: TriggerFlowRuntimeData, *, task=task):
                results = data.get_state("results", {}) or {}
                return {
                    "task_id": task["id"],
                    "doc": data.get_state("doc"),
                    "deps": {dep: results[dep] for dep in task["depends_on"]},
                }

            collector_cache[task["id"]] = collect
        return collector_cache[task["id"]]

    def emitter_for(task, total_count):
        if task["id"] not in emitter_cache:

            async def emit_done(data: TriggerFlowRuntimeData, *, task=task, total_count=total_count):
                results = dict(data.get_state("results", {}) or {})
                results[task["id"]] = data.value
                await data.async_set_state("results", results, emit=False)
                data.emit_nowait(f"done:{ task['id'] }", {"task_id": task["id"], "result": data.value})
                if len(results) == total_count:
                    data.emit_nowait("done:all", results)
                return data.value

            emitter_cache[task["id"]] = emit_done
        return emitter_cache[task["id"]]

    async def finalize(data: TriggerFlowRuntimeData):
        await data.async_set_state("final", dict(data.value), emit=False)
        return data.value

    def assemble_executor(executor: TriggerFlow, selected_plan: dict):
        tasks = selected_plan["tasks"]

        kickoff_key = tuple(task["id"] for task in tasks)
        if kickoff_key not in kickoff_cache:

            async def kickoff(data: TriggerFlowRuntimeData, *, kickoff_tasks=tuple(tasks)):
                await data.async_set_state("doc", data.value["doc"], emit=False)
                await data.async_set_state("results", {}, emit=False)
                for task in kickoff_tasks:
                    if not task["depends_on"]:
                        data.emit_nowait(f"start:{ task['id'] }", {"task_id": task["id"]})

            kickoff_cache[kickoff_key] = kickoff

        executor.to(kickoff_cache[kickoff_key], name=f"kickoff:{ ','.join(kickoff_key) }")
        for task in tasks:
            dependencies = task["depends_on"]
            if not dependencies:
                trigger = executor.when(f"start:{ task['id'] }")
            elif len(dependencies) == 1:
                trigger = executor.when(f"done:{ dependencies[0] }")
            else:
                trigger = executor.when(
                    {"event": [f"done:{ dependency }" for dependency in dependencies]},
                    mode="and",
                )
            (
                trigger
                .to(collector_for(task), name=f"collect:{ task['id'] }")
                .to_sub_flow(template_for(task), name=f"run:{ task['id'] }")
                .to(emitter_for(task, len(tasks)), name=f"emit:{ task['id'] }")
            )
        executor.when("done:all").to(finalize, name="finalize")
        return executor

    executor = TriggerFlow(name="todo-executor")
    assemble_executor(executor, plan)
    operator_count = len(_operators(executor))
    assemble_executor(executor, plan)

    assert len(_operators(executor)) == operator_count
    assert len(_operators_by_kind(executor, "sub_flow")) == len(plan["tasks"])

    different_plan = {"tasks": [*plan["tasks"], {"id": "extra_check", "kind": "analyze", "depends_on": ["final_review"]}]}
    different_executor = assemble_executor(TriggerFlow(name="todo-executor-different"), different_plan)
    assert len(_operators_by_kind(different_executor, "sub_flow")) == len(different_plan["tasks"])
    assert any(operator["name"] == "run:extra_check" for operator in _operators_by_kind(different_executor, "sub_flow"))

    execution = assemble_executor(TriggerFlow(name="todo-executor-run"), plan).create_execution(auto_close=False)
    await execution.async_start({"doc": "policy"})
    result = await execution.async_close(timeout=1)

    assert result["results"]["extract_terms"] == "extract:extract_terms:policy"
    assert result["results"]["analyze_risk"] == "analyze:analyze_risk:extract_terms=extract:extract_terms:policy"
    assert result["results"]["final_review"] == (
        "analyze:final_review:"
        "analyze_risk=analyze:analyze_risk:extract_terms=extract:extract_terms:policy,"
        "extract_terms=extract:extract_terms:policy"
    )
    assert result["final"] == result["results"]
    assert len(_operators(extract_template)) == extract_template_operator_count
    assert len(_operators(analyze_template)) == analyze_template_operator_count
