from agently import Agently
from agently.types.data import OutputValidateResult

agent = Agently.create_agent()

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## .validate() — semantic output validation with auto-retry
#
# .output() enforces structure (types, required keys).
# .validate() enforces meaning — your Python code decides whether the content is acceptable.
# If the handler returns False (or {"ok": False}), Agently retries the request automatically.
# Return {"ok": False, "reason": "..."} to inject the reason into the retry prompt,
# giving the model a targeted correction instead of just re-rolling blindly.


def validate_simple():
    # Simple bool return: True = accept, False = retry.
    def has_enough_items(result, context) -> OutputValidateResult:
        tips = result.get("tips", [])
        if len(tips) >= 3:
            return True
        print(f"  [validate] Only {len(tips)} tip(s) — need at least 3, retrying...")
        return False

    result = (
        agent.input("Give me tips for writing clean Python code.")
        .output({"tips": [(str, "One actionable tip")]})
        .validate(has_enough_items)
        .start(max_retries=3, raise_ensure_failure=False)
    )
    print(result)


# validate_simple()


def validate_with_reason():
    # Returning {"ok": False, "reason": "..."} injects the reason into the retry prompt.
    # The model sees why it failed and can correct the specific issue rather than guessing.
    def check_word_count(result, context) -> OutputValidateResult:
        text = result.get("description", "")
        word_count = len(text.split())
        if 20 <= word_count <= 40:
            return True
        direction = "too short" if word_count < 20 else "too long"
        reason = f"Description is {direction} ({word_count} words). Target: 20–40 words."
        print(f"  [validate attempt {context.attempt_index}] {reason}")
        return {"ok": False, "reason": reason}

    result = (
        agent.input("Describe what a REST API is.")
        .output({"description": (str, "Clear explanation in 20–40 words", True)})
        .validate(check_word_count)
        .start(max_retries=3, raise_ensure_failure=False)
    )
    print(result)


# validate_with_reason()


def validate_with_payload():
    # Return {"ok": True, "payload": {...}} to replace the result with a modified version.
    # The original model output is used for validation logic but the payload is what
    # .start() / .get_data() ultimately returns — useful for normalisation.
    def normalise_tags(result, context) -> OutputValidateResult:
        tags = result.get("tags", [])
        normalised = [t.strip().lower() for t in tags if isinstance(t, str) and t.strip()]
        if not normalised:
            return {"ok": False, "reason": "No tags were generated."}
        # Accept but swap in the normalised tags instead of the raw model output.
        return {"ok": True, "payload": {**result, "tags": normalised}}

    result = (
        agent.input("Categorise the blog post: 'Getting started with async Python'.")
        .output({
            "title": (str, "Blog post title"),
            "tags": [(str, "Relevant tag")],
        })
        .validate(normalise_tags)
        .start(max_retries=2, raise_ensure_failure=False)
    )
    print(result)


# validate_with_payload()


# All functions are commented out — uncomment one to run with a local Ollama model.
# Model output is non-deterministic text, but the returned dict keys are stable.
#
# How it works:
# .validate(handler) adds semantic validation on top of .output()'s schema enforcement.
# handler(result, context) -> OutputValidateResult, where OutputValidateResult is:
#
#   True                               — accept the result as-is
#   False                              — reject; retry up to max_retries times
#   {"ok": False, "reason": "..."}     — reject with a targeted correction message
#                                        injected into the retry prompt so the model
#                                        knows what to fix (better than blind re-roll)
#   {"ok": True,  "payload": {...}}    — accept but substitute a modified result dict,
#                                        useful for normalisation (e.g. lowercasing tags)
#                                        without triggering another generation round
#
# context provides: attempt_index, retry_count, max_retries, response_text, prompt.
#
# Retry flow:
#   attempt 0 → model generates → validate() called
#     if ok: return result
#     if not ok: inject reason into prompt → attempt 1 → ... → attempt max_retries
#   if max_retries exhausted and raise_ensure_failure=True: raise exception
#   if raise_ensure_failure=False: return last result regardless
#
# validate_simple():
#   has_enough_items checks len(tips) >= 3; returns False if not
#   Expected: result["tips"] contains 3+ items after at most 3 attempts
#
# validate_with_reason():
#   check_word_count measures word count; returns {"ok": False, "reason": "..."} if out of range
#   Expected: result["description"] is 20–40 words; retry message names the exact issue
#
# validate_with_payload():
#   normalise_tags lowercases and strips tags; returns {"ok": True, "payload": ...}
#   Expected: result["tags"] are all lowercase/stripped; no extra model call needed
