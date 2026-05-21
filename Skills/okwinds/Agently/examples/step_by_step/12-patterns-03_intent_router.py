from agently import Agently, TriggerFlow, TriggerFlowRuntimeData

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## Intent Router — classify user intent, then route to a specialized handler
#
# Pattern:
#   1. A classifier agent reads the user message and outputs a routing category
#      along with a confidence level.
#   2. A TriggerFlow dispatcher picks the right handler based on the category.
#   3. Each handler is a separate agent with its own system prompt and focus area.
#   4. Low-confidence results fall back to a safe general-purpose handler.
#
# This separates routing logic from handling logic, making it easy to add
# new categories or swap handler implementations independently.


def classify_intent(user_input: str) -> dict:
    """Classify the user message into a support category."""
    response = (
        Agently.create_agent()
        .input(user_input)
        .instruct(["Classify the user's support request into the most appropriate category."])
        .output({
            "reasoning": (str, "Brief analysis of the user's intent"),
            "category": (
                "'billing' | 'technical' | 'feedback' | 'general'",
                "Routing category",
            ),
            "confidence": ("'high' | 'medium' | 'low'", "Classification confidence"),
        })
        .get_response()
    )
    return response.result.get_data()


def build_support_router() -> TriggerFlow:
    flow = TriggerFlow(name="support-router")

    async def classify(data: TriggerFlowRuntimeData):
        user_input = data.input
        result = classify_intent(user_input)
        category = result.get("category", "general")
        confidence = result.get("confidence", "low")
        print(f"  Category: {category} (confidence: {confidence})")
        print(f"  Reasoning: {result.get('reasoning', '')[:100]}")
        await data.async_set_state("user_input", user_input, emit=False)
        await data.async_set_state("intent", result, emit=False)

    async def handle_billing(data: TriggerFlowRuntimeData):
        reply = (
            Agently.create_agent()
            .input(data.get_state("user_input"))
            .instruct([
                "You are a billing support agent.",
                "Help with payment issues, invoices, refunds, and subscriptions.",
                "Be precise about amounts and timelines.",
            ])
            .start()
        )
        await data.async_set_state("reply", reply)
        await data.async_set_state("handler", "billing")

    async def handle_technical(data: TriggerFlowRuntimeData):
        reply = (
            Agently.create_agent()
            .input(data.get_state("user_input"))
            .instruct([
                "You are a technical support agent.",
                "Help with installation, configuration, and bug troubleshooting.",
                "Ask clarifying questions about the environment when needed.",
            ])
            .start()
        )
        await data.async_set_state("reply", reply)
        await data.async_set_state("handler", "technical")

    async def handle_feedback(data: TriggerFlowRuntimeData):
        reply = (
            Agently.create_agent()
            .input(data.get_state("user_input"))
            .instruct([
                "You are collecting product feedback.",
                "Acknowledge what was shared, show it was understood, and thank the user.",
                "Do not make promises about implementation.",
            ])
            .start()
        )
        await data.async_set_state("reply", reply)
        await data.async_set_state("handler", "feedback")

    async def handle_general(data: TriggerFlowRuntimeData):
        reply = (
            Agently.create_agent()
            .input(data.get_state("user_input"))
            .instruct("Answer the user's question helpfully and concisely.")
            .start()
        )
        await data.async_set_state("reply", reply)
        await data.async_set_state("handler", "general")

    async def dispatch(data: TriggerFlowRuntimeData):
        intent = data.get_state("intent", {})
        category = intent.get("category", "general")
        confidence = intent.get("confidence", "low")

        # Low confidence falls back to the general handler to avoid mis-routing.
        if confidence == "low":
            print("  Low confidence — using general handler")
            await handle_general(data)
            return

        handlers = {
            "billing":   handle_billing,
            "technical": handle_technical,
            "feedback":  handle_feedback,
            "general":   handle_general,
        }
        await handlers.get(category, handle_general)(data)

    flow.to(classify).to(dispatch)
    return flow


if __name__ == "__main__":
    router = build_support_router()

    test_inputs = [
        "I was charged twice this month — how do I get a refund?",
        "The app crashes whenever I try to upload a file larger than 10 MB.",
        "The redesigned dashboard is much cleaner — great work on the update!",
        "What time zones does your calendar scheduling feature support?",
    ]

    for user_input in test_inputs:
        print(f"\n{'─' * 60}")
        print(f"User: {user_input}")
        state = router.start(user_input)
        print(f"Handler: {state.get('handler', 'unknown')}")
        print(f"Reply:   {state.get('reply', '')[:200]}")


# Expected output (content varies — category and handler are deterministic for these inputs):
# ────────────────────────────────────────────────────────────
# User: I was charged twice this month — how do I get a refund?
#   Category: billing (confidence: high)
#   Reasoning: User reports a duplicate charge and requests a refund — billing issue.
#   Handler: billing
#   Reply:   I'm sorry to hear about the duplicate charge. Please contact our billing
#            team with your invoice number and we'll issue a refund within 3–5 business days...
#
# ────────────────────────────────────────────────────────────
# User: The app crashes whenever I try to upload a file larger than 10 MB.
#   Category: technical (confidence: high)
#   Handler: technical
#   Reply:   This sounds like a file size limit issue. Could you share your OS version
#            and the exact error message? Common fixes include...
#
# How it works:
# classify_intent() uses a structured output with an enumerated category field —
# the model cannot hallucinate a category outside the declared set.
# The confidence field lets the dispatcher degrade gracefully: low-confidence
# results always fall back to the general handler rather than risking a wrong route.
# Each handler is an independent agent with its own focused system prompt,
# making it easy to add new categories (e.g., 'legal', 'sales') by adding a
# new handler function and extending the handlers dict.
#
# Flow:
# user_input
#   |
#   v
# classify (TriggerFlow chunk)
#   model outputs: category="billing", confidence="high"
#   |
#   v
# dispatch (TriggerFlow chunk)
#   confidence=="high" -> pick handlers["billing"]
#   await handle_billing(data)
#     -> billing agent writes reply
#   state["reply"] = "..." state["handler"] = "billing"
#   |
#   v
# flow.start() returns final state dict
