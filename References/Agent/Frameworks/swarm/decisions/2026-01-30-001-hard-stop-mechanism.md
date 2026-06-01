# Decision: Swarm Hard Stop Mechanism

**Date:** 2026-01-30
**Status:** Implemented

## Context

SwarmSDK needed a way to hard-stop all execution. Users need to cancel running swarms from event callbacks, other threads, or signal handlers.

## Decision

Implemented `swarm.stop` using IO.pipe for thread-safe signaling + Async::Barrier for task cancellation.

### Key Design Decisions

1. **IO.pipe for cross-thread signaling** - `barrier.stop` is NOT thread-safe across threads. IO.pipe wakes the Async scheduler from any thread, then a listener task calls `barrier.stop` within the reactor.

2. **Always wrap execution in a barrier** - Even without timeout, so `swarm.stop` has something to cancel.

3. **Explicit `rescue Async::Stop` in `execute_in_task`** - Sets `interrupted` flag before ensure block runs (cleaner than checking `$!`).

4. **Active agent tracking on Swarm** - `mark_agent_active/inactive` called from `Agent::Chat#execute_ask`, used to emit `agent_stop` events for interrupted agents.

5. **Single cooperative check** - In `execution_loop` before starting a new iteration, to prevent unnecessary LLM calls after stop is requested.

6. **`finish_reason` on events** - Both `swarm_stop` and `agent_stop` events include `finish_reason` for consistency. Values: "finished", "interrupted", "timeout", "error".

## API

```ruby
# Blocking with event-based stop
swarm.execute("Build auth") do |event|
  swarm.stop if event[:type] == "tool_call" && event[:tool] == "Dangerous"
end

# Non-blocking with cancellation
Sync do
  task = swarm.execute("Build auth", wait: false) { |event| puts event }
  sleep 5
  swarm.stop
  result = task.wait
  result.interrupted?  # => true
  result.finish_reason # => "interrupted"
end

# Cross-thread stop
Thread.new { result = swarm.execute("Build auth") }
sleep 10
swarm.stop  # Thread-safe via IO.pipe
```

## Files Modified

- `lib/swarm_sdk.rb` - Added `InterruptedError`
- `lib/swarm_sdk/swarm.rb` - Added stop API and active agent tracking
- `lib/swarm_sdk/swarm/executor.rb` - Barrier + stop listener + interrupted handling
- `lib/swarm_sdk/swarm/hook_triggers.rb` - Added `finish_reason` to context
- `lib/swarm_sdk/swarm/logging_callbacks.rb` - Added `finish_reason` to event
- `lib/swarm_sdk/result.rb` - Added `interrupted?` and `finish_reason`
- `lib/swarm_sdk/agent/chat.rb` - Active agent tracking in `execute_ask`
- `lib/swarm_sdk/observer/manager.rb` - Added `stop` method
- `lib/swarm_sdk/concerns/cleanupable.rb` - Added SwarmRegistry shutdown
- `test/swarm_sdk/hard_stop_test.rb` - 21 tests covering all scenarios
