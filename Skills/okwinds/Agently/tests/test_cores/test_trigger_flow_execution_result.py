from typing import Any, cast
import asyncio

import pytest
from pydantic import BaseModel

from agently import TriggerFlow
from agently.types.trigger_flow import TriggerFlowRuntimeData


@pytest.mark.asyncio
async def test_execution_result_state_reads_closed_snapshot_from_execution_close():
    flow = TriggerFlow(name="result-close-state")

    async def worker(data: TriggerFlowRuntimeData):
        await data.async_set_state("answer", data.value.upper())

    flow.to(worker)
    execution = flow.create_execution(auto_close=False)
    await execution.async_start("ok")

    snapshot = await execution.async_close()

    assert snapshot == {"answer": "OK"}
    assert execution.result.get_state("answer") == "OK"
    assert not hasattr(execution.result, "async_get_snapshot")
    assert not hasattr(execution.result, "get_snapshot")


@pytest.mark.asyncio
async def test_execution_result_state_reads_live_then_frozen_snapshot():
    flow = TriggerFlow(name="result-state")

    async def worker(data: TriggerFlowRuntimeData):
        await data.async_set_state("report", {"version": 1})

    flow.to(worker)
    execution = flow.create_execution(auto_close=False)
    await execution.async_start(None)

    assert execution.result.get_state("report.version") == 1
    snapshot = await execution.async_close()

    await execution.async_set_state("report.version", 2)

    assert snapshot == {"report": {"version": 1}}
    assert execution.result.get_state("report.version") == 1
    assert execution.result.get_state() == {"report": {"version": 1}}


@pytest.mark.asyncio
async def test_execution_result_final_result_preserves_compat_precedence():
    flow = TriggerFlow(name="result-precedence")

    async def worker(data: TriggerFlowRuntimeData):
        data.execution._system_runtime_data.set("result", {"answer": "internal"})
        data.execution._runtime_data.set("$final_result", {"answer": "compat"})

    flow.to(worker)
    execution = flow.create_execution(auto_close=False)
    await execution.async_start(None)

    assert await execution.result.async_get_final_result(timeout=1) == {"answer": "compat"}
    assert await execution.async_get_result(timeout=1) == {"answer": "compat"}


@pytest.mark.asyncio
async def test_execution_result_final_result_reads_explicit_internal_result():
    flow = TriggerFlow(name="result-internal")

    async def worker(data: TriggerFlowRuntimeData):
        data.execution._system_runtime_data.set("result", {"answer": data.value})
        result_ready = data.execution._system_runtime_data.get("result_ready")
        assert isinstance(result_ready, asyncio.Event)
        result_ready.set()

    flow.to(worker)
    execution = flow.create_execution(auto_close=False)
    await execution.async_start("ready")

    assert await execution.result.async_get_final_result(timeout=1) == {"answer": "ready"}


class FinalResult(BaseModel):
    answer: str


def test_execution_result_keeps_set_result_contract_validation():
    flow = TriggerFlow(name="result-contract").set_contract(result=FinalResult)
    execution = flow.create_execution()

    with pytest.raises(ValueError, match="result"):
        execution.set_result(cast(Any, {"wrong": "shape"}))


@pytest.mark.asyncio
async def test_execution_result_sub_flow_write_back_uses_compat_then_snapshot():
    compat_child = TriggerFlow(name="compat-child")
    compat_child.to(lambda data: data.set_result({"report": "compat"}))

    snapshot_child = TriggerFlow(name="snapshot-child")

    async def snapshot_worker(data: TriggerFlowRuntimeData):
        await data.async_set_state("report", "snapshot")

    snapshot_child.to(snapshot_worker)

    async def build_parent(child: TriggerFlow):
        parent = TriggerFlow(name=f"parent-{ child.name }")

        async def finalize(data: TriggerFlowRuntimeData):
            await data.async_set_state("value", data.value)

        parent.to(lambda data: data.value).to_sub_flow(child, write_back={"value": "result.report"}).to(finalize)
        execution = parent.create_execution(auto_close=False)
        await execution.async_start("input")
        return await execution.async_close()

    assert await build_parent(compat_child) == {"value": "compat"}
    assert await build_parent(snapshot_child) == {"value": "snapshot"}


@pytest.mark.asyncio
async def test_execution_result_intervention_readers_filter_without_consuming():
    flow = TriggerFlow(name="result-interventions")
    execution = flow.create_execution(auto_close=False)
    execution._system_runtime_data.set(
        "interventions",
        [
            {"id": "a", "status": "inserted", "target": "review", "consumed_by": ["planner"]},
            {"id": "b", "status": "expired", "target": "review", "consumed_by": []},
        ],
    )

    expired = execution.result.get_interventions(status="expired")

    assert expired == [{"id": "b", "status": "expired", "target": "review", "consumed_by": []}]
    assert execution.result.get_latest_intervention(target="review")["id"] == "b"
    assert execution.result.get_interventions(consumed_by="planner")[0]["id"] == "a"
    assert execution.result.get_interventions(status="expired") == expired


@pytest.mark.asyncio
async def test_execution_result_meta_and_restore_reflect_execution_state():
    flow = TriggerFlow(name="result-restore")

    async def worker(data: TriggerFlowRuntimeData):
        await data.async_set_state("answer", "ok")
        data.set_result({"legacy": True})

    flow.to(worker)
    execution = flow.create_execution(auto_close=False)
    await execution.async_start(None)
    snapshot = await execution.async_close()
    saved = execution.save()

    restored = flow.create_execution(auto_close=False)
    restored.load(saved)

    assert snapshot == {"answer": "ok", "$final_result": {"legacy": True}}
    assert restored.result.get_state("answer") == "ok"
    assert await restored.result.async_get_final_result(timeout=1) == {"legacy": True}
    meta = restored.result.get_meta()
    assert meta["execution_id"] == execution.id
    assert meta["flow_name"] == "result-restore"
    assert meta["lifecycle_state"] == "closed"
    assert meta["status"] == "completed"
    assert meta["close_reason"] == "manual"
