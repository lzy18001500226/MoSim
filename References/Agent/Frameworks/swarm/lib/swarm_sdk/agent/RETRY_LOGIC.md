# LLM Call Retry Logic

## Feature

SwarmSDK automatically retries failed LLM API calls to handle transient failures.

## Configuration

**Defaults:**
- Max retries: 10
- Delay: 10 seconds (fixed, no exponential backoff)
- Retries ALL StandardError exceptions

## Implementation

**Location:** `lib/swarm_sdk/agent/chat.rb`

The retry logic handles two categories of errors:

1. **Transient failures** - Network issues, timeouts, rate limits
2. **Orphan tool call errors** - Special recovery for malformed conversation history

## Error Types Handled

- `Faraday::ConnectionFailed` - Network connection issues
- `Faraday::TimeoutError` - Request timeouts
- `RubyLLM::APIError` - API errors (500s, etc.)
- `RubyLLM::RateLimitError` - Rate limit errors
- `RubyLLM::BadRequestError` - With special handling for orphan tool calls
- Any other `StandardError` - Catches proxy issues, DNS failures, etc.

## Orphan Tool Call Recovery

**What are orphan tool calls?**

Orphan tool calls occur when an assistant message contains `tool_use` blocks but the conversation lacks corresponding `tool_result` messages. This can happen when:
- Tool execution is interrupted mid-stream
- Session state restoration is incomplete
- Network issues cause partial message delivery

**How recovery works:**

When a `RubyLLM::BadRequestError` (400) is received with tool-related error messages:

1. Clears stale ephemeral content from the failed call
2. The system scans message history for orphan tool calls
3. For each assistant message with `tool_calls`:
   - Checks if all `tool_call_id`s have matching `tool_result` messages
   - Any missing results indicate orphan tool calls
4. Orphan tool calls are pruned:
   - If assistant message has content, keeps content but removes `tool_calls`
   - If assistant message is empty, removes the entire message
5. **System reminder is added** to inform the agent:
   - Lists which tool calls were interrupted
   - Tells agent they were never executed
   - Suggests re-running them if still needed
6. Retries the LLM call immediately (doesn't count as a retry)
7. If no orphans found, falls through to normal retry logic

**Tool-related error patterns detected:**
- `tool_use`, `tool_result`, `tool_use_id`
- `corresponding tool_result`
- `must immediately follow`

**Logging:**

When orphan pruning occurs, emits `orphan_tool_calls_pruned` event:
```json
{
  "type": "orphan_tool_calls_pruned",
  "agent": "agent_name",
  "pruned_count": 1,
  "original_error": "tool_use block must have corresponding tool_result"
}
```

**System Reminder Format:**

The agent receives a system reminder about the pruned tool calls:
```
<system-reminder>
The following tool calls were interrupted and removed from conversation history:

- Read(file_path: "/important/file.rb")
- Write(file_path: "/output.txt", content: "Hello...")

These tools were never executed. If you still need their results, please run them again.
</system-reminder>
```

## Usage

**Automatic - No Configuration Needed:**

```ruby
swarm = SwarmSDK.build do
  agent :my_agent do
    model "gpt-4"
    base_url "http://proxy.example.com/v1"  # Can fail
  end
end

# Automatically retries on failure and recovers from orphan tool calls
response = swarm.execute("Do something")
```

## Logging

**On Retry:**
```
WARN: SwarmSDK: LLM call failed (attempt 1/10): Faraday::ConnectionFailed: Connection failed
WARN: SwarmSDK: Retrying in 10 seconds...
```

**On Max Retries:**
```
ERROR: SwarmSDK: LLM call failed after 10 attempts: Faraday::ConnectionFailed: Connection failed
```

## Behavior

**Scenario 1: Transient failure**
```
Attempt 1: ConnectionFailed
  → Wait 10s
Attempt 2: ConnectionFailed
  → Wait 10s
Attempt 3: Success
  → Returns response
```

**Scenario 2: Persistent failure**
```
Attempt 1-10: All fail
  → Raises original error after attempt 10
```

**Scenario 3: Immediate success**
```
Attempt 1: Success
  → Returns response (no retry needed)
```

**Scenario 4: Orphan tool call recovery**
```
Attempt 1: BadRequestError (tool_use without tool_result)
  → Detect orphan tool calls
  → Prune orphan tool calls from message history
  → Retry immediately (doesn't count as retry)
Attempt 1: Success
  → Returns response
```

## Why No Exponential Backoff

**Design Decision:** Fixed 10-second delay

**Rationale:**
- Simpler implementation
- Predictable retry duration (max 100 seconds)
- Transient proxy/network issues typically resolve within seconds
- Rate limit errors are caught by provider-specific handling
- User explicitly requested fixed delays

**Total max time:** 10 retries × 10 seconds = 100 seconds maximum

## Future Enhancements (If Needed)

- [ ] Configurable retry count per agent
- [ ] Configurable delay per agent
- [ ] Selective retry based on error type
- [ ] Exponential backoff option
- [ ] Circuit breaker pattern

**Current State:** Production-ready with sensible defaults for proxy/network resilience and automatic orphan tool call recovery.
