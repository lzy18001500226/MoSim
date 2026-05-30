from agently import Agently

agent = Agently.create_agent()

agent.set_settings(
    "prompt.prompt_title_mapping",
    {
        "system": "通用提示",
        "developer": "开发者指令",
        "chat_history": "对话记录",
        "info": "相关信息",
        "tools": "工具信息",
        "action_results": "行动结果记录",
        "instruct": "处理规则",
        "examples": "举例",
        "input": "输入",
        "output": "输出",
        "output_requirement": "输出要求",
    },
)

user_input = "Hello"
welcome_words = {
    "Hello": "Welcome word in English",
    "你好": "Welcome word in Chinese",
    "こんにちは": "Welcome word in Japanese",
    "Bonjour": "Welcome word in French",
    "Hola": "Welcome word in Spanish",
}

(
    agent.input({"user_input": user_input})
    .info(welcome_words)
    .instruct(
        [
            "Judge user's region according {user_input}",
            "Use {info} to help",
        ]
    )
    .output(
        {
            "why": (str, "explanation"),
            "user_region": (str,),
        }
    )
)

print(agent.prompt.to_messages()[0]["content"])
print("==================")
print(agent.prompt.to_text())

# Expected output (deterministic — no model call):
# The serialized system message and prompt text with Chinese section headers instead
# of the default English ones (通用提示, 相关信息, 处理规则, 举例, 输入, 输出, etc.)
#
# How it works:
# set_settings("prompt.prompt_title_mapping", {...}) remaps the default English section
# headers to custom strings globally for this agent.  The mapping covers all prompt
# slots: system, developer, info, instruct, examples, input, output, etc.
# Useful for non-English user interfaces or custom prompt labeling conventions.
