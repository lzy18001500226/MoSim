import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agently import Agently


# DynamicTask smoke example with a submitted TaskDAG.
# It does not model-plan the graph; callers pass an already typed graph and
# can still validate it before running.
# Expected key output from one local run:
# topological_order=extract_terms,extract_dates,final_review
# final_review=final_review(extract_dates=extract_dates:policy,extract_terms=extract_terms:policy)
# semantic_final_task=final_review


async def run_local_task(context):
    if context.dependency_results:
        deps = ",".join(
            f"{ task_id }={ result }"
            for task_id, result in sorted(context.dependency_results.items())
        )
        return f"{ context.task.id }({ deps })"
    return f"{ context.task.id }:{ context.graph_input['doc'] }"


async def main():
    graph = {
        "graph_id": "policy-review",
        "tasks": [
            {"id": "extract_terms", "kind": "local", "binding": "local_handler"},
            {"id": "extract_dates", "kind": "local", "binding": "local_handler"},
            {
                "id": "final_review",
                "kind": "local",
                "binding": "local_handler",
                "depends_on": ["extract_terms", "extract_dates"],
            },
        ],
        "semantic_outputs": {"final": "final_review"},
    }

    task = Agently.create_dynamic_task(
        target="review policy",
        plan=graph,
        handlers={"local_handler": run_local_task},
    )
    validation = task.validate(graph)
    snapshot = await task.async_run(graph_input={"doc": "policy"}, timeout=1)

    print(f"topological_order={ ','.join(validation.topological_task_ids) }")
    print(f"final_review={ snapshot['task_results']['final_review'] }")
    print(f"semantic_final_task={ snapshot['semantic_outputs']['final']['task_id'] }")


if __name__ == "__main__":
    asyncio.run(main())
