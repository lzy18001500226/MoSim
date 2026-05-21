from agently import Agently, TriggerFlow, TriggerFlowRuntimeData

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## Reflection Pattern — Generate → Evaluate → Revise until criteria are met
#
# Pattern (signal-driven loop):
#   1. GENERATE: produce an initial draft.
#   2. EVALUATE: score the draft against explicit criteria; emit "Revise" if it fails.
#   3. REVISE: apply the critique to improve the draft; emit "Evaluate" to re-check.
#   4. Loop until the draft passes or max_rounds is reached (safety valve).
#
# TriggerFlow's flow.when("Signal") enables the cycle without a manual loop counter:
# evaluate emits "Revise", revise emits "Evaluate" — the flow self-terminates
# when evaluate stores final_result without emitting another signal.


def build_reflection_flow(max_rounds: int = 3) -> TriggerFlow:
    flow = TriggerFlow(name="reflection-loop")

    async def generate_draft(data: TriggerFlowRuntimeData):
        state = data.input  # {"task": str, "criteria": [str]}
        task = state.get("task", "")
        print("[Generate] Creating initial draft...")
        result = (
            Agently.create_agent()
            .input(task)
            .output({"content": (str, "Generated content matching the task requirements")})
            .get_response()
        )
        draft = result.result.get_data().get("content", "")
        print(f"  Draft: {len(draft)} characters")
        data.emit_nowait("Evaluate", {**state, "draft": draft, "round": 0})

    async def evaluate_draft(data: TriggerFlowRuntimeData):
        state = data.input
        round_num = state.get("round", 0) + 1
        draft = state.get("draft", "")
        task = state.get("task", "")
        criteria = state.get("criteria", [])

        if round_num > max_rounds:
            print(f"[Evaluate] Round {round_num}: reached max rounds — accepting draft.")
            await data.async_set_state("final_result", draft, emit=False)
            await data.async_set_state("rounds_used", max_rounds, emit=False)
            return

        print(f"[Evaluate] Round {round_num}/{max_rounds}")
        result = (
            Agently.create_agent()
            .input({"task": task, "current_draft": draft})
            .info({"evaluation_criteria": criteria})
            .instruct(["Check whether the draft meets every criterion. Be precise and strict."])
            .output({
                "passed": (bool, "True only if every criterion is satisfied"),
                "score": (float, "Quality score 0.0–1.0"),
                "issues": ([str], "Criteria that are not met; empty list if passed"),
                "suggestions": ([str], "Specific improvements for each issue; empty if passed"),
            })
            .get_response()
        )
        critique = result.result.get_data()
        passed = critique.get("passed", False)
        score = critique.get("score", 0.0)

        print(f"  Score: {score:.2f}  Passed: {passed}")
        for issue in critique.get("issues", []):
            print(f"  Issue: {issue}")

        if passed:
            print("  All criteria met — done.")
            await data.async_set_state("final_result", draft, emit=False)
            await data.async_set_state("rounds_used", round_num, emit=False)
            return

        # Not passing — send to Revise with critique attached
        data.emit_nowait("Revise", {**state, "round": round_num, "critique": critique})

    async def revise_draft(data: TriggerFlowRuntimeData):
        state = data.input
        task = state.get("task", "")
        draft = state.get("draft", "")
        suggestions = state.get("critique", {}).get("suggestions", [])
        round_num = state.get("round", 1)

        print(f"[Revise] Round {round_num}: applying {len(suggestions)} suggestion(s)...")
        result = (
            Agently.create_agent()
            .input({"original_task": task, "current_version": draft})
            .info({"improvements_needed": suggestions})
            .instruct([
                "Revise the draft to address every listed improvement.",
                "Keep parts that already satisfy the criteria unchanged.",
                "Do not introduce new issues while fixing existing ones.",
            ])
            .output({"content": (str, "Revised version of the content")})
            .get_response()
        )
        improved = result.result.get_data().get("content", draft)
        print(f"  Revised: {len(draft)} → {len(improved)} characters")

        # Send the improved draft back to evaluation
        data.emit_nowait("Evaluate", {**state, "draft": improved})

    flow.to(generate_draft)
    flow.when("Evaluate").to(evaluate_draft)
    flow.when("Revise").to(revise_draft)
    return flow


if __name__ == "__main__":
    flow = build_reflection_flow(max_rounds=3)

    state = flow.start({
        "task": (
            "Write a one-paragraph product description for a noise-cancelling "
            "travel headphone. Target: business travelers. Tone: professional, factual."
        ),
        "criteria": [
            "Length is between 60 and 100 words",
            "Mentions at least one specific technical feature (e.g., ANC hours, Bluetooth version)",
            "Tone is professional and factual — no marketing superlatives like 'best' or 'amazing'",
            "Clearly states who the product is designed for",
        ],
    })

    rounds = state.get("rounds_used", "?")
    final = state.get("final_result", "")
    print(f"\n{'=' * 60}")
    print(f"Completed in {rounds} round(s). Final version ({len(final)} chars):")
    print(final)


# Expected output (content varies — convergence typically takes 1–2 rounds):
# [Generate] Creating initial draft...
#   Draft: 87 characters
#
# [Evaluate] Round 1/3
#   Score: 0.60  Passed: False
#   Issue: Does not mention any specific technical feature
#   Issue: Audience ("business travelers") is implicit, not stated explicitly
#
# [Revise] Round 1: applying 2 suggestion(s)...
#   Revised: 87 → 112 characters
#
# [Evaluate] Round 2/3
#   Score: 0.95  Passed: True
#   All criteria met — done.
#
# ============================================================
# Completed in 2 round(s). Final version (112 chars):
# Designed for business travelers, the ProTravel NC headphone delivers 30 hours of
# active noise cancellation and Bluetooth 5.3 multipoint connectivity in a lightweight,
# foldable form factor for distraction-free work on the road.
#
# How it works:
# generate_draft produces an initial version without constraints feedback.
# evaluate_draft scores it against the explicit criteria list — strict scoring
# means a draft with even one unmet criterion will not pass.
# revise_draft receives the critique and suggestions, then emits back to Evaluate.
# The signal-driven loop (emit_nowait("Evaluate") / emit_nowait("Revise")) runs
# inside TriggerFlow without an explicit counter; max_rounds is the safety valve
# that forces termination if the model gets stuck.
#
# Flow:
# generate_draft -> emit("Evaluate", {draft, round=0})
#   |
#   v
# evaluate_draft (round 1): score < 1.0 -> emit("Revise", {draft, critique})
#   |
#   v
# revise_draft (round 1): emit("Evaluate", {improved_draft})
#   |
#   v
# evaluate_draft (round 2): passed=True -> async_set_state("final_result", draft)
#   (no emit -> loop terminates)
#   |
#   v
# flow.start() returns state with "final_result" and "rounds_used"
