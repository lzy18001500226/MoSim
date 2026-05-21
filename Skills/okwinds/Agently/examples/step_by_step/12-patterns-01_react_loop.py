from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## ReAct Loop — Reasoning + Acting in an explicit model-driven loop
#
# Pattern:
#   1. Show the model: the question, available tools, and steps completed so far.
#   2. Model outputs: call a tool (type='tool') OR give a final answer (type='final').
#   3. If 'tool': execute it, append the result to history, repeat from step 1.
#   4. If 'final': return the answer.
#
# Unlike agent.get_action_result() (which delegates planning to Agently internals),
# this loop makes each reasoning step explicit and observable — useful when you
# want to inspect or control the plan-act-observe cycle directly.

# --- Mock data (no external API required) ---

CATALOG = {
    "laptop":  {"price": 1299.99, "stock": 45, "category": "electronics"},
    "mouse":   {"price":   29.99, "stock": 200, "category": "electronics"},
    "desk":    {"price":  459.00, "stock": 12,  "category": "furniture"},
    "chair":   {"price":  349.00, "stock": 8,   "category": "furniture"},
    "monitor": {"price":  649.99, "stock": 30,  "category": "electronics"},
}

SHIPPING = {
    "electronics": {"standard": 9.99,  "express": 24.99},
    "furniture":   {"standard": 29.99, "express": 59.99},
}


def get_product(name: str) -> dict:
    """Look up a product in the catalog by name."""
    info = CATALOG.get(name.lower())
    return info if info else {"error": f"Product '{name}' not found"}


def get_shipping_cost(name: str, method: str = "standard") -> dict:
    """Return the shipping cost for a product (method: 'standard' or 'express')."""
    product = CATALOG.get(name.lower(), {})
    category = product.get("category")
    if not category:
        return {"error": f"Unknown product: {name}"}
    cost = SHIPPING.get(category, {}).get(method, 0)
    return {"product": name, "method": method, "cost": cost}


def calculate_order_total(unit_price: float, quantity: int, shipping: float) -> dict:
    """Compute subtotal, 8% tax, and final order total."""
    subtotal = round(unit_price * quantity, 2)
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + tax + shipping, 2)
    return {"subtotal": subtotal, "tax": tax, "shipping": shipping, "total": total}


TOOLS = {
    "get_product": {
        "desc": "Look up price, stock, and category for a product by name.",
        "args": {"name": "Product name (e.g., 'laptop', 'desk', 'mouse')"},
        "func": get_product,
    },
    "get_shipping_cost": {
        "desc": "Get the shipping cost for a product. method is 'standard' or 'express'.",
        "args": {"name": "Product name", "method": "'standard' or 'express'"},
        "func": get_shipping_cost,
    },
    "calculate_order_total": {
        "desc": "Compute the final order total with 8% tax and shipping included.",
        "args": {
            "unit_price": "Unit price as a float",
            "quantity": "Number of units as an integer",
            "shipping": "Shipping cost as a float",
        },
        "func": calculate_order_total,
    },
}


def react_loop(question: str, max_steps: int = 6) -> str:
    completed = []
    tools_desc = [{"name": k, "desc": v["desc"], "args": v["args"]} for k, v in TOOLS.items()]

    for step in range(max_steps):
        print(f"\n[Step {step + 1}]")
        response = (
            Agently.create_agent()
            .input(question)
            .info({"available_tools": tools_desc, "completed_steps": completed})
            .instruct([
                "Review the question and all completed steps.",
                "Decide: do you need a tool to get more information, or do you already have enough?",
                "If you need a tool: output type='tool' with the tool name and its arguments.",
                "If you have all the information needed: output type='final' with the answer.",
            ])
            .output({
                "type": ("'tool' | 'final'", "Next action"),
                "reasoning": (str, "What you know and what you still need"),
                "tool_name": ("str | null", "Tool name when type=='tool'"),
                "tool_args": ("dict | null", "Tool arguments when type=='tool'"),
                "answer": ("str | null", "Final answer when type=='final'"),
            })
            .get_response()
        )
        d = response.result.get_data()
        if not d:
            break

        reasoning = d.get("reasoning", "")
        print(f"  Reasoning: {reasoning[:120]}")
        print(f"  Decision:  {d.get('type')}")

        if d.get("type") == "final":
            return d.get("answer", "No answer returned.")

        tool_name = d.get("tool_name")
        tool_args = d.get("tool_args") or {}
        if tool_name not in TOOLS:
            print(f"  Unknown tool '{tool_name}', stopping.")
            break

        print(f"  Calling:   {tool_name}({tool_args})")
        result = TOOLS[tool_name]["func"](**tool_args)
        print(f"  Result:    {result}")
        completed.append({"tool": tool_name, "args": tool_args, "result": result})

    return "Reached maximum steps without a final answer."


if __name__ == "__main__":
    answer = react_loop(
        "I want to order 2 laptops with express shipping. "
        "What is the total cost including tax?"
    )
    print(f"\n=== Final Answer ===\n{answer}")


# Expected output (step count and phrasing vary by model):
# [Step 1]
#   Reasoning: I need the laptop price first before I can compute shipping and total.
#   Decision:  tool
#   Calling:   get_product({'name': 'laptop'})
#   Result:    {'price': 1299.99, 'stock': 45, 'category': 'electronics'}
#
# [Step 2]
#   Reasoning: I have the price. Now I need express shipping cost for a laptop.
#   Decision:  tool
#   Calling:   get_shipping_cost({'name': 'laptop', 'method': 'express'})
#   Result:    {'product': 'laptop', 'method': 'express', 'cost': 24.99}
#
# [Step 3]
#   Reasoning: I have price (1299.99) and shipping (24.99). Now I can compute the total.
#   Decision:  tool
#   Calling:   calculate_order_total({'unit_price': 1299.99, 'quantity': 2, 'shipping': 24.99})
#   Result:    {'subtotal': 2599.98, 'tax': 207.998, 'shipping': 24.99, 'total': 2832.97}
#
# [Step 4]
#   Decision:  final
#
# === Final Answer ===
# For 2 laptops with express shipping: subtotal $2599.98, tax $208.00, shipping $24.99 → total $2832.97.
#
# How it works:
# At each step a fresh agent instance is created and given the question plus completed_steps.
# The model outputs a structured decision: either call a specific tool with arguments,
# or declare the answer final.  The loop executes the tool locally (no model involvement)
# and appends the result to completed_steps so the next step can build on it.
# The loop is capped at max_steps to prevent runaway execution.
# This explicit loop lets you inspect every reasoning step; the built-in
# agent.get_action_result() provides a more concise API when observability is not needed.
#
# Flow:
# question + [] -> model plans get_product("laptop")
#   |
#   v
# result appended -> question + [product_info] -> model plans get_shipping_cost(...)
#   |
#   v
# result appended -> question + [product, shipping] -> model plans calculate_order_total(...)
#   |
#   v
# result appended -> question + [all data] -> model outputs type='final', returns answer
