from agently import Agently

agent = Agently.create_agent()

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## Configure Prompt: YAML / JSON as Prompt Templates
def load_yaml_prompt():
    # YAML Prompt is a declarative form of the same prompt structure used in code.
    # Mapping rules:
    # - .agent.* -> agent-level prompt (persistent)
    # - .request.* or top-level keys -> request-level prompt (per request)
    # - $role / $system is shorthand for agent system role
    # See demo_docs/CONFIGURE_PROMPT_RELATION.md for details.
    #
    # YAML example (examples/configure_prompt/yaml_prompt.yaml):
    # $ensure_all_keys: true
    # .agent:
    #   system: You are an Agently enhanced agent.
    #   info:
    #     Agently: "Speed up your AI application development. Official website: https://Agently.tech."
    # .request:
    #   input: Say hello.
    #   output:
    #     thinking:
    #       $type:
    #         - $type: str
    #           $desc: one step of plan
    #       $desc: plans to response
    #       $ensure: true
    #     reply:
    #       $type: str
    #       $ensure: true
    #     extra:
    #       $type:
    #         worth_to_remember:
    #           $type: bool
    #           $desc: is {input} and {reply} worth to be remembered that not a normal daily chat?
    #         user_emotion_guess:
    #           $type: str
    #           $desc: how do you thinking user's emotion is going to be after {reply}?
    #       $desc: extra info you need to collect and analysis
    # .alias:
    #   set_request_prompt:
    #     .args:
    #       - instruct
    #       - Reply {input} politely
    # $extra_info: This is an extra information for agent prompt.
    # extra_request_info: This is an extra information for next request.
    # in_value_placeholder_test: "in_value_placeholder: ${in_value_placeholder}"
    # $${key_name_placeholder}: This agent key name should be replaced.
    # ${key_name_placeholder}: This request key name should be replaced too.
    # only_value_placeholder_test": ${ only_value_placeholder }
    # If you want placeholder substitution while loading, pass mappings=... explicitly.
    # You can load YAML prompt from file path or raw string content.
    result = (
        agent.load_yaml_prompt("examples/configure_prompt/yaml_prompt.yaml")
        .set_request_prompt("input", "Explain recursion in one paragraph.")
        .start()
    )
    print(result)


# load_yaml_prompt()


def load_json_prompt():
    # JSON Prompt follows the same schema as YAML Prompt.
    #
    # JSON example (examples/configure_prompt/json_prompt.json):
    # {
    #   "$ensure_all_keys": true,
    #   ".agent": {
    #     "system": "You are an Agently enhanced agent.",
    #     "info": {
    #       "Agently": "Speed up your AI application development. Official website: https://Agently.tech."
    #     }
    #   },
    #   ".request": {
    #     "input": "Say hello.",
    #     "output": {
    #       "thinking": {
    #         "$type": [{"$type": "str", "$desc": "one step of plan"}],
    #         "$desc": "plans to response",
    #         "$ensure": true
    #       },
    #       "reply": {"$type": "str", "$ensure": true},
    #       "extra": {
    #         "$type": {
    #           "worth_to_remember": {
    #             "$type": "bool",
    #             "$desc": "is {input} and {reply} worth to be remembered that not a normal daily chat?"
    #           },
    #           "user_emotion_guess": {
    #             "$type": "str",
    #             "$desc": "how do you thinking user's emotion is going to be after {reply}?"
    #           }
    #         },
    #         "$desc": "extra info you need to collect and analysis"
    #       }
    #     }
    #   },
    #   ".alias": {"set_request_prompt": {".args": ["instruct", "Reply {input} politely."]}},
    #   "$extra_info": "This is an extra information for agent prompt.",
    #   "extra_request_info": "This is an extra information for next request.",
    #   "in_value_placeholder_test": "in_value_placeholder: ${in_value_placeholder}",
    #   "$${key_name_placeholder}": "This agent key name should be replaced.",
    #   "${key_name_placeholder}": "This request key name should be replaced too.",
    #   "only_value_placeholder_test": "${ only_value_placeholder }"
    # }
    # If you want placeholder substitution while loading, pass mappings=... explicitly.
    # You can load JSON prompt from file path or raw string content.
    result = (
        agent.load_json_prompt("examples/configure_prompt/json_prompt.json")
        .set_request_prompt("input", "Explain recursion with a short example.")
        .start()
    )
    print(result)


# load_json_prompt()


def load_multiple_prompts():
    # Load multiple prompts from a single YAML file and pick one by key path.
    result = (
        agent.load_yaml_prompt(
            "examples/configure_prompt/multiple_yaml_prompts.yaml",
            prompt_key_path="demo.output_control",
        )
        .set_request_prompt("input", "Explain recursion.")
        .start()
    )
    print(result)


def load_from_string():
    # String-based loading is useful for large projects that manage prompts in code,
    # databases, or remote config centers.
    # Notice:
    # - String loading is treated as raw prompt content, not a file path.
    # - If you keep placeholders like ${...}, they are resolved at load time
    #   only when explicit mappings=... are provided.
    yaml_prompt_text = """
$ensure_all_keys: true
.agent:
  system: You are an Agently enhanced agent.
.request:
  input: Say hello.
  output:
    reply:
      $type: str
      $ensure: true
"""
    json_prompt_text = """
{
  "$ensure_all_keys": true,
  ".agent": { "system": "You are an Agently enhanced agent." },
  ".request": {
    "input": "Say hello.",
    "output": { "reply": { "$type": "str", "$ensure": true } }
  }
}
"""
    agent.load_yaml_prompt(yaml_prompt_text)
    agent.load_json_prompt(json_prompt_text)
    print(agent.get_prompt_text())


# load_multiple_prompts()


def roundtrip_configure_prompt():
    # Convert native prompt -> YAML/JSON -> load again.
    result = (
        agent.role("You are an Agently enhanced agent.", always=True)
        .info({"Agently": "Speed up your AI application development."}, always=True)
        .input("Say hello.")
        .instruct(["Reply {input} politely."])
        .set_agent_prompt("ensure_all_keys", True)  # outermost strict guarantee
        .output(
            {
                "reply": (str, "reply", True),
            }
        )
    )
    yaml_prompt = result.get_yaml_prompt()
    json_prompt = result.get_json_prompt()
    print("[YAML PROMPT]")
    print(yaml_prompt)
    print("[JSON PROMPT]")
    print(json_prompt)

    agent_2 = Agently.create_agent()
    agent_2.load_yaml_prompt(yaml_prompt)
    print("[AGENT 2 PROMPT]")
    print(agent_2.get_prompt_text())


# roundtrip_configure_prompt()
# load_from_string()

# All functions are commented out — uncomment one to run with a local Ollama model.
# roundtrip_configure_prompt() and load_from_string() print prompt text (no model call needed).
#
# How it works:
# YAML and JSON prompt files are a declarative form of the same prompt structure used in code.
# Key rules in the file schema:
#   .agent.*   keys  -> agent-level prompts (persistent across requests)
#   .request.* keys  -> request-level prompts (single request only)
#   top-level keys without dots -> also request-level
#   $ensure_all_keys: true -> require all output keys to be present
#   .alias.set_request_prompt -> shorthand to call set_request_prompt() via config
#
# get_yaml_prompt() / get_json_prompt() serialize the current agent prompt config back to
# string; load_yaml_prompt(string) / load_json_prompt(string) accept both file paths and
# raw content strings (detected automatically).
# roundtrip_configure_prompt() shows that prompt configs built in code can be exported and
# re-loaded on a new agent instance, producing the same merged prompt text.
