from agently import Agently

# By default, version > 4.0.7.1 will add current time to prompt automatically
agent = Agently.create_agent()

agent.input("hello")

print("Default:\n", agent.get_prompt_text())


# You can turn off this feature by change settings
agent.set_settings("prompt.add_current_time", False)

print("Turn off:\n", agent.get_prompt_text())
# <Console Logs>
# Default:
#  [current time]: 2026-02-02 23:24:37 Monday

# [INPUT]:
# hello

# [OUTPUT]:
# Turn off:
#  [INPUT]:
# hello

# [OUTPUT]:

# Expected output (deterministic — no model call, only prompt inspection):
# Default:
#  [current time]: 2026-02-02 23:24:37 Monday
#
#  [INPUT]:
#  hello
#
#  [OUTPUT]:
# Turn off:
#  [INPUT]:
#  hello
#
#  [OUTPUT]:
#
# How it works:
# Agently automatically prepends a "[current time]: <timestamp>" line to every
# prompt by default (v > 4.0.7.1).  get_prompt_text() serializes the assembled
# prompt without sending it to a model, so the output is deterministic.
# set_settings("prompt.add_current_time", False) removes the timestamp line;
# subsequent get_prompt_text() calls return the prompt without it.
