# Decision: Convert complete ↔ handle_tool_calls Recursion to Trampoline Loop

**Date:** 2026-01-30
**Status:** Accepted
**Component:** SwarmSDK (RubyLLM patches)

## Context

`MultiSubscriberCallbacks#complete` and `handle_tool_calls` formed a mutual recursion:

```
complete → handle_tool_calls → complete → handle_tool_calls → ...
```

Each cycle added ~15-25 stack frames. With 30-50 tool-call rounds, that's 450-1250 frames.
Delegation compounds this — each level adds 20-30 frames. A 3-level delegation chain with
heavy tool usage could blow Ruby's fiber stack (which defaults to 128KB / ~4000 frames).

## Decision

Convert the mutual recursion to a **trampoline loop** in `complete()`. `handle_tool_calls()`
returns a value (`nil` to continue, or a `Tool::Halt` to stop) instead of recursing back
into `complete()`.

### Before

```ruby
def complete(&block)
  response = execute_llm_request(&block)
  # ... add_message, emit ...
  if response.tool_call?
    handle_tool_calls(response, &block)  # ← recurses via handle_tool_calls
  else
    response
  end
end

def handle_tool_calls(response, &block)
  # ... execute tools ...
  halt_result || complete(&block)  # ← mutual recursion
end
```

### After

```ruby
def complete(&block)
  loop do
    response = execute_llm_request(&block)
    # ... add_message, emit ...
    if response.tool_call?
      halt_result = handle_tool_calls(response, &block)
      return halt_result if halt_result
      # loop continues → next LLM call, zero stack growth
    else
      return response
    end
  end
end

def handle_tool_calls(response, &_block)
  # ... execute tools ...
  halt_result  # Return halt_result or nil; NO recursive complete() call
end
```

## Files Changed

- `lib/swarm_sdk/ruby_llm_patches/chat_callbacks_patch.rb` — `complete()` and `handle_tool_calls()`
- `lib/swarm_sdk/ruby_llm_patches/tool_concurrency_patch.rb` — `ConcurrentToolExecution#handle_tool_calls()`

## Consequences

- **Stack usage is O(1)** regardless of the number of tool-call rounds
- No behavioral change: same events emitted, same halt semantics, same tool execution order
- `ConcurrentToolExecution#handle_tool_calls` also updated to match (it overrides the base method)
- The `&block` parameter is still threaded through for `execute_llm_request` in the loop
