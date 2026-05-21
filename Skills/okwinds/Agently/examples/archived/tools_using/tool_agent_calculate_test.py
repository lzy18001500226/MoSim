import asyncio

from agently import Agently

(
    Agently.set_settings(
        "OpenAICompatible",
        {
            "base_url": "http://localhost:11434/v1",
            "model": "qwen2.5:7b",
            "model_type": "chat",
        },
    ).set_settings(
        "debug", False
    )  # Turn on/off debug logs
)

agent = Agently.create_agent()


@agent.action_func
async def add(a: int, b: int) -> int:
    """
    Get result of `a(int)` add `b(int)`
    """
    await asyncio.sleep(1)
    print(a, "+", b, "=", a + b)
    return a + b


response = agent.input("34643523+52131231=? Use action to calculate!").use_actions(add).get_response()
result = response.get_data()
print("[Response]:", result)

action_call = agent.input("34643523+52131231=? Use action to calculate!").use_actions(add).generate_action_call()
print("[Only Action Call]:", action_call)
