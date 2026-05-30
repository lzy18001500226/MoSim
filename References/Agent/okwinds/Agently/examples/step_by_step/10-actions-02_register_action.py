import re

from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)

agent = Agently.create_agent()
agent.set_action_loop(max_rounds=4)


## agent.action.register_action() — explicit schema registration
#
# Use this when you need custom action IDs, precise argument descriptions,
# or when the function you want to register is not decorated at definition time.


def slugify(text: str) -> str:
    """Convert a title to a lowercase URL-safe slug (spaces -> hyphens, no special chars)."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def count_words(text: str) -> int:
    """Count the number of whitespace-separated words in a string."""
    return len(text.split())


def truncate(text: str, max_length: int) -> str:
    """Truncate text to max_length characters, appending '...' if cut."""
    return text[:max_length] + "..." if len(text) > max_length else text


# Register each function with an explicit id, description, and argument schema.
agent.action.register_action(
    action_id="slugify",
    desc="Convert a blog post title or phrase to a URL-safe slug.",
    kwargs={"text": (str, "The title or phrase to slugify.")},
    func=slugify,
    expose_to_model=True,
)

agent.action.register_action(
    action_id="count_words",
    desc="Count the number of words in a piece of text.",
    kwargs={"text": (str, "Text to count words in.")},
    func=count_words,
    expose_to_model=True,
)

agent.action.register_action(
    action_id="truncate",
    desc="Truncate text to a character limit, appending '...' if it was cut.",
    kwargs={
        "text": (str, "The text to truncate."),
        "max_length": (int, "Maximum number of characters to keep."),
    },
    func=truncate,
    expose_to_model=True,
)


def demo_register_action():
    # Activate by action ID string — useful when IDs are determined at runtime.
    agent.use_actions(["slugify", "count_words", "truncate"])
    agent.input(
        "Process this blog post title: 'Building Scalable AI Agents: A Practical Guide for 2025'. "
        "1) Generate a URL slug. "
        "2) Count the words in the original title. "
        "3) Truncate the title to 40 characters."
    )
    records = agent.get_action_result()
    print("[action records]", records)
    response = agent.get_response()
    print(response.result.get_text())


# demo_register_action()


# Expected output (example — text phrasing varies):
# [action records] [ActionResult(action_id='slugify',      result='building-scalable-ai-agents-a-practical-guide-for-2025', ...),
#                   ActionResult(action_id='count_words',  result=9, ...),
#                   ActionResult(action_id='truncate',     result='Building Scalable AI Agents: A ...', ...)]
# Slug: building-scalable-ai-agents-a-practical-guide-for-2025
# Word count: 9
# Truncated: "Building Scalable AI Agents: A ..."
#
# How it works:
# agent.action.register_action() registers a function with an explicit action_id,
# a desc the model reads to understand what the action does, and a kwargs dict that
# maps argument names to (type, description) tuples for schema generation.
# expose_to_model=True makes the action visible in the model's tool list.
# agent.use_actions(["slugify", ...]) activates specific registered actions by ID.
# Multiple actions are planned and executed in the order the model decides.
#
# Flow:
# register_action("slugify", ...) / register_action("count_words", ...) / register_action("truncate", ...)
#   | (registration, no model call yet)
#   v
# agent.use_actions(["slugify", "count_words", "truncate"])
# agent.input("Process this title...")
# agent.get_action_result()
#   model plans: slugify("Building Scalable AI Agents: A Practical Guide for 2025")
#                count_words("Building Scalable AI Agents: A Practical Guide for 2025")
#                truncate("Building Scalable AI Agents: A Practical Guide for 2025", 40)
#   FunctionActionExecutor runs each -> slug, 9, truncated string
#   |
#   v
# agent.get_response()
#   model summarizes all three results in one reply
