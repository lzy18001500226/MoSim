import asyncio
import time

from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## ToDo + Concurrent Execution — model plans, asyncio executes in parallel
#
# Pattern:
#   1. Model decomposes a goal into a task list with explicit dependency annotations.
#   2. Classify tasks: independent (no deps) vs dependent (must wait for others).
#   3. Run independent tasks concurrently with asyncio.gather().
#   4. Run dependent tasks sequentially after their prerequisites complete.
#
# This pattern is useful when sub-tasks are I/O-bound (API calls, file ops, DB queries)
# and can safely run in parallel without interfering with each other.

SIMULATED_DURATIONS = {
    "t1": 1.0, "t2": 0.8, "t3": 1.2,
    "t4": 0.6, "t5": 0.9, "t6": 0.7,
    "_default": 0.8,
}


def plan_tasks(goal: str) -> dict:
    """Ask the model to break a goal into a task graph with dependency annotations."""
    response = (
        Agently.create_agent()
        .input(goal)
        .instruct([
            "Decompose the goal into 4–6 concrete, independently executable sub-tasks.",
            "Assign each task a short ID (t1, t2, ...).",
            "In depends_on, list the IDs of tasks that must finish before this one starts.",
            "Tasks with no prerequisites should have an empty depends_on list.",
        ])
        .output({
            "tasks": [{
                "id": (str, "Task ID, e.g. 't1'"),
                "title": (str, "Short task title"),
                "description": (str, "What this task does"),
                "depends_on": ([str], "IDs of tasks that must complete first; [] for none"),
            }],
            "summary": (str, "Brief rationale for how the goal was decomposed"),
        })
        .get_response()
    )
    return response.result.get_data()


async def execute_task(task: dict) -> dict:
    """Simulate executing a task (replace with real API calls, file writes, etc.)."""
    task_id = task["id"]
    delay = SIMULATED_DURATIONS.get(task_id, SIMULATED_DURATIONS["_default"])
    print(f"  [{task_id}] Starting: {task['title']} (simulated {delay}s)")
    await asyncio.sleep(delay)
    print(f"  [{task_id}] Done")
    return {"id": task_id, "title": task["title"], "status": "done", "duration": delay}


async def run_with_concurrency(goal: str):
    # Phase 1: model generates the task graph
    print("=== Phase 1: Planning ===")
    plan = plan_tasks(goal)
    tasks = plan.get("tasks", [])
    print(f"Summary: {plan.get('summary', '')}")
    for t in tasks:
        dep_label = f" (after: {t.get('depends_on')})" if t.get("depends_on") else ""
        print(f"  [{t['id']}] {t['title']}{dep_label}")

    # Phase 2: classify by dependency
    print("\n=== Phase 2: Dependency Analysis ===")
    independent = [t for t in tasks if not t.get("depends_on")]
    dependent = [t for t in tasks if t.get("depends_on")]
    print(f"  Independent (parallel): {[t['id'] for t in independent]}")
    print(f"  Dependent  (serial):    {[t['id'] for t in dependent]}")

    results = []

    # Phase 3: run independent tasks concurrently and measure speedup
    if independent:
        print(f"\n=== Phase 3: Concurrent Execution ({len(independent)} tasks) ===")
        serial_estimate = sum(
            SIMULATED_DURATIONS.get(t["id"], SIMULATED_DURATIONS["_default"])
            for t in independent
        )
        t0 = time.perf_counter()
        concurrent_results = await asyncio.gather(*[execute_task(t) for t in independent])
        elapsed = time.perf_counter() - t0
        results.extend(concurrent_results)
        print(f"  Concurrent: {elapsed:.2f}s  (serial estimate: {serial_estimate:.1f}s, "
              f"speedup: {serial_estimate / elapsed:.1f}x)")

    # Phase 4: run dependent tasks sequentially after prerequisites
    if dependent:
        print(f"\n=== Phase 4: Sequential Execution ({len(dependent)} dependent tasks) ===")
        for t in dependent:
            result = await execute_task(t)
            results.append(result)

    return results


if __name__ == "__main__":
    goal = (
        "Set up a new open-source project: create the GitHub repository, "
        "add a CI workflow, write a README, configure linting, and set up "
        "branch protection rules on the main branch."
    )
    all_results = asyncio.run(run_with_concurrency(goal))
    print(f"\n=== All Tasks Completed ===")
    for r in all_results:
        print(f"  [{r['id']}] {r['title']} — {r['status']}")


# Expected output (task breakdown varies by model; speedup depends on concurrency):
# === Phase 1: Planning ===
# Summary: The repository must be created first; CI, README, and linting can run in parallel ...
#   [t1] Create GitHub repository
#   [t2] Add CI workflow (after: ['t1'])
#   [t3] Write README
#   [t4] Configure linting
#   [t5] Set up branch protection (after: ['t1'])
#
# === Phase 2: Dependency Analysis ===
#   Independent (parallel): ['t3', 't4']
#   Dependent   (serial):   ['t1', 't2', 't5']
#
# === Phase 3: Concurrent Execution (2 tasks) ===
#   [t3] Starting: Write README (simulated 1.2s)
#   [t4] Starting: Configure linting (simulated 0.6s)
#   [t4] Done
#   [t3] Done
#   Concurrent: 1.21s  (serial estimate: 1.8s, speedup: 1.5x)
#
# === Phase 4: Sequential Execution (3 dependent tasks) ===
#   ...
#
# How it works:
# The model outputs a JSON task graph where each task lists the IDs it depends on.
# Tasks with an empty depends_on list can safely run concurrently.
# asyncio.gather() launches all independent tasks simultaneously; each awaits a
# simulated delay (replace with real async I/O such as aiohttp, asyncpg, or aiofiles).
# Dependent tasks are then executed sequentially, respecting ordering constraints.
# The speedup ratio shows how much time concurrency saves versus serial execution.
#
# Flow:
# plan_tasks(goal)
#   model outputs task graph: [t1 (no deps), t2 (deps: t1), t3 (no deps), ...]
#   |
#   v
# classify: independent=[t1, t3], dependent=[t2, ...]
#   |
#   v
# asyncio.gather(execute_task(t1), execute_task(t3))  <- run in parallel
#   |
#   v
# execute_task(t2)  <- waits until this point (t1 is done)
#   |
#   v
# all results collected and printed
