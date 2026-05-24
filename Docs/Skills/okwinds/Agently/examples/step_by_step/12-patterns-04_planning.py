from agently import Agently, TriggerFlow, TriggerFlowRuntimeData

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## Planning Pattern — generate a plan first, then execute based on risk policy
#
# Pattern (two-stage):
#   Stage 1 — PLAN: the model produces a structured execution plan with a risk
#             assessment (low / medium / high) and reversibility flag.
#   Stage 2 — EXECUTE: a TriggerFlow policy decides whether to auto-execute
#             (low risk or reversible medium) or require human confirmation
#             (high risk or irreversible medium).
#
# Separating planning from execution provides two key benefits:
#   • The plan can be inspected and rejected before any side effects occur.
#   • Risk-based routing ensures dangerous operations are never silently automated.


def generate_plan(task: str) -> dict:
    """Ask the model to plan the task — output only, no execution."""
    response = (
        Agently.create_agent()
        .input(task)
        .instruct([
            "Generate a step-by-step execution plan for the task.",
            "Do NOT execute anything — only plan.",
            "For each step, explain what it changes.",
            "Assess the overall risk level and whether changes can be undone.",
        ])
        .output({
            "steps": [{
                "step": (int, "Step number starting at 1"),
                "action": (str, "What to do in this step"),
                "impact": (str, "What this step changes or creates"),
            }],
            "risk_level": (
                "'low' | 'medium' | 'high'",
                "Overall risk: low=safe, medium=notable, high=potentially destructive",
            ),
            "risk_reason": (str, "Why this risk level was assigned"),
            "reversible": (bool, "True if all changes can be fully undone"),
        })
        .get_response()
    )
    return response.result.get_data()


def build_plan_executor() -> TriggerFlow:
    """
    TriggerFlow that generates a plan, applies risk policy, then executes.
    Policy:
      low risk              -> auto-execute
      medium + reversible   -> auto-execute (warning logged)
      medium + irreversible
      or high risk          -> require manual confirmation
    """
    flow = TriggerFlow(name="safe-plan-executor")

    async def plan_and_assess(data: TriggerFlowRuntimeData):
        task = data.input
        plan = generate_plan(task)
        await data.async_set_state("plan", plan, emit=False)
        await data.async_set_state("task", task, emit=False)

        risk = plan.get("risk_level", "high")
        reversible = plan.get("reversible", False)

        print(f"\nTask: {task}")
        print(f"Risk: {risk.upper()} | Reversible: {'yes' if reversible else 'no'}")
        print(f"Why:  {plan.get('risk_reason', '')}")
        print("Steps:")
        for s in plan.get("steps", []):
            print(f"  {s['step']}. {s['action']}")
            print(f"     Impact: {s['impact']}")

        if risk == "low":
            auto = True
            print("\n[Policy] Low risk — auto-approving.")
        elif risk == "medium" and reversible:
            auto = True
            print("\n[Policy] Medium risk, reversible — auto-approving (logged).")
        else:
            auto = False
            print("\n[Policy] High risk or irreversible — manual confirmation required.")

        await data.async_set_state("auto_approved", auto, emit=False)

    async def auto_execute(data: TriggerFlowRuntimeData):
        plan = data.get_state("plan", {})
        steps = plan.get("steps", [])
        print("\nAuto-executing:")
        for s in steps:
            print(f"  Step {s['step']}: {s['action']} [simulated]")
        await data.async_set_state(
            "outcome", f"Auto-executed {len(steps)} step(s) successfully."
        )

    async def confirm_and_execute(data: TriggerFlowRuntimeData):
        task = data.get_state("task", "")
        plan = data.get_state("plan", {})
        steps = plan.get("steps", [])
        print(f"\nManual approval required for: {task}")
        confirm = input("Type 'yes' to proceed, anything else to cancel: ").strip().lower()
        if confirm == "yes":
            print("Confirmed — executing:")
            for s in steps:
                print(f"  Step {s['step']}: {s['action']} [simulated]")
            await data.async_set_state(
                "outcome", f"Manually approved and executed {len(steps)} step(s)."
            )
        else:
            print("Cancelled.")
            await data.async_set_state("outcome", "Execution cancelled by user.")

    (
        flow.to(plan_and_assess)
        .if_condition(lambda data: data.get_state("auto_approved", False))
        .to(auto_execute)
        .else_condition()
        .to(confirm_and_execute)
        .end_condition()
    )

    return flow


if __name__ == "__main__":
    executor = build_plan_executor()

    tasks = [
        "Add a 'Contributing' section to the project README with guidelines for pull requests.",
        "Drop the legacy_sessions table from the production database and delete the S3 backup files.",
    ]

    for task in tasks:
        print(f"\n{'=' * 60}")
        state = executor.start(task)
        print(f"\nOutcome: {state.get('outcome', '')}")


# Expected output (risk levels assigned by model — should be stable for these inputs):
#
# ============================================================
# Task: Add a 'Contributing' section to the project README ...
# Risk: LOW | Reversible: yes
# Why:  Editing a README is a minor documentation change, easily reverted with git.
# Steps:
#   1. Open README.md  ->  Impact: File opened for editing
#   2. Append Contributing section  ->  Impact: New section added
#   3. Commit the change  ->  Impact: Git history updated (revertable)
# [Policy] Low risk — auto-approving.
# Auto-executing:
#   Step 1: Open README.md [simulated]
#   Step 2: Append Contributing section [simulated]
#   Step 3: Commit the change [simulated]
# Outcome: Auto-executed 3 step(s) successfully.
#
# ============================================================
# Task: Drop the legacy_sessions table from the production database ...
# Risk: HIGH | Reversible: no
# Why:  Dropping a production table and deleting S3 backups is permanent data loss.
# Steps: ...
# [Policy] High risk or irreversible — manual confirmation required.
# Manual approval required for: Drop the legacy_sessions table ...
# Type 'yes' to proceed, anything else to cancel: no
# Cancelled.
# Outcome: Execution cancelled by user.
#
# How it works:
# generate_plan() returns a structured plan with risk_level and reversible fields;
# the model reasons about risk before any code runs.
# The TriggerFlow plan_and_assess chunk stores auto_approved in state.
# if_condition() routes to auto_execute when auto_approved is True,
# or to confirm_and_execute when False — no side effects happen without a policy check.
# In production, replace the simulated print statements with real shell commands,
# database calls, or API requests; the policy routing stays the same.
#
# Flow:
# task (string)
#   |
#   v
# plan_and_assess: generate_plan(task) -> {risk_level, reversible, steps}
#   policy: low or medium+reversible -> auto_approved=True, else False
#   |
#   v
# if_condition(auto_approved)
#   True  -> auto_execute: simulate each step, set outcome
#   False -> confirm_and_execute: prompt user, simulate or cancel
#   |
#   v
# flow.start() returns state with "outcome" key
