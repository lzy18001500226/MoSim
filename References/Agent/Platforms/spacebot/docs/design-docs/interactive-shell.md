# Interactive Shell

Live-streamed shell output and interactive process detection for worker tool calls. Replaces the current fire-and-forget `cmd.output()` model with spawned processes that stream output line-by-line to the frontend and detect when a command is waiting for interactive input.

## Problem

The shell tool spawns a fresh `sh -c` process per call with `Stdio::piped()` for stdout/stderr and implicit `Stdio::null()` for stdin (via `cmd.output()`). The tool blocks until the process exits or the timeout fires, then returns the full output.

This causes two failures:

1. **Interactive commands hang.** Tools like `npm create vite`, `apt install`, or `npx` prompt for input (`Ok to proceed? (y)`). The process reads EOF from stdin and either hangs or loops waiting. The 60s timeout kills it, the LLM sees "Command timed out", retries with a different invocation, and hits the same wall.

2. **No live output visibility.** The LLM and the user both see nothing until the command finishes. Long-running builds, test suites, and installs are black boxes. The dashboard shows a spinning "Running..." indicator with no content. If something fails at minute 4 of a 5-minute build, nobody knows until the timeout or completion.

### What the LLM sees today

```
✗ Shell: npm create vite@latest myapp -- --template react
  Toolset error: ToolCallError: Shell command failed: Command timed out

✗ Shell: npx create-vite@latest myapp --template react
  Toolset error: ToolCallError: Shell command failed: Command timed out
```

The LLM has no way to know _why_ the command timed out — it can't see the "Ok to proceed?" prompt. So it keeps retrying with variations that all hit the same interactive prompt.

### What the user sees today

A green checkmark (now fixed to red X) with the raw JSON blob `{"success":false,"exit_code":-1,"stdout":"","stderr":"","summary":"..."}`. No partial output, no indication that the command was waiting for input.

## Design

Two independent improvements that build on each other:

### Part 1: Live output streaming

Replace `cmd.output()` (batch collect) with `cmd.spawn()` + line-by-line reading. As each line arrives from stdout/stderr, broadcast it through the existing `ProcessEvent` system to the frontend SSE stream. The dashboard renders lines in real-time as the command runs.

### Part 2: Interactive detection + LLM guidance

When the shell tool detects that a process is likely waiting for interactive input (output has quiesced but process hasn't exited), return early with the partial output and a `waiting_for_input: true` flag. The LLM sees the prompt text (e.g. "Ok to proceed? (y)") and can make an informed decision — either retry with `--yes` flags, use a different command, or pipe input via `echo y | command`.

The LLM is **not** given a way to send stdin to the running process. The approach is detection and retry, not interactive I/O. The process is killed when `waiting_for_input` is detected, and the LLM's next shell call starts a fresh process with the right flags.

### Future: PTY-based interactive sessions

A follow-up phase could add true bidirectional PTY sessions where the LLM can send input to a running process across multiple tool calls. This doc covers the groundwork (live streaming, quiesce detection) that makes PTY sessions possible later. See "Future: PTY Sessions" at the bottom.

## Part 1: Live Output Streaming

### Event Model

New `ProcessEvent` variant for incremental tool output:

```rust
ProcessEvent::ToolOutput {
    agent_id: AgentId,
    process_id: ProcessId,
    channel_id: Option<ChannelId>,
    tool_name: String,    // "shell" or "exec"
    line: String,         // one line of output
    stream: String,       // "stdout" or "stderr"
}
```

Corresponding `ApiEvent::ToolOutput` for the SSE stream, same fields plus `process_type`.

### Shell Tool Changes

**File:** `src/tools/shell.rs`

Replace the execution core. The tool gains two new fields:

```rust
pub struct ShellTool {
    workspace: PathBuf,
    sandbox: Arc<Sandbox>,
    event_tx: Option<broadcast::Sender<ProcessEvent>>,  // NEW
    process_id: Option<ProcessId>,                       // NEW
    channel_id: Option<ChannelId>,                       // NEW
    agent_id: Option<AgentId>,                           // NEW
}
```

These are populated when the tool is created for a worker (via `create_worker_tool_server`). For system-internal `shell()` calls and cortex chat, they're `None` and streaming is skipped.

The `call()` method changes from:

```rust
// Before: batch collect
cmd.stdout(Stdio::piped()).stderr(Stdio::piped());
let output = tokio::time::timeout(timeout, cmd.output()).await??;
```

To:

```rust
// After: spawn + stream
cmd.stdout(Stdio::piped()).stderr(Stdio::piped());
let mut child = cmd.spawn()?;

let stdout = BufReader::new(child.stdout.take().unwrap());
let stderr = BufReader::new(child.stderr.take().unwrap());

// Read both streams concurrently, broadcasting each line
let (stdout_lines, stderr_lines) = tokio::join!(
    stream_lines(stdout, "stdout", &self.event_tx, ...),
    stream_lines(stderr, "stderr", &self.event_tx, ...),
);

let status = child.wait().await?;
```

The `stream_lines` helper reads lines via `tokio::io::AsyncBufReadExt::lines()`, emits a `ProcessEvent::ToolOutput` for each line, and collects lines into a `String` buffer. After the process exits, the full collected output is returned as `ShellOutput` — same as today, so the LLM's view doesn't change.

The overall execution is still wrapped in `tokio::time::timeout(timeout, ...)`.

### Threading Into Tool Constructors

**File:** `src/tools.rs`

`create_worker_tool_server()` already receives most of what we need. Add `event_tx`, `agent_id`, `channel_id`, and `worker_id` to the `ShellTool` constructor:

```rust
.tool(ShellTool::new(workspace.clone(), sandbox.clone())
    .with_streaming(
        deps.event_tx.clone(),
        ProcessId::Worker(worker_id),
        channel_id.clone(),
        deps.agent_id.clone(),
    ))
```

Builder pattern — `with_streaming()` returns `Self` with the optional fields populated. The tool works without streaming (fields are `None`) for cortex chat and system-internal calls.

### API Layer

**File:** `src/api/state.rs`

In `register_agent_events()`, handle the new variant:

```rust
ProcessEvent::ToolOutput { agent_id, process_id, channel_id, tool_name, line, stream } => {
    api_tx.send(ApiEvent::ToolOutput {
        agent_id,
        channel_id,
        process_type,
        process_id: id_str,
        tool_name,
        line,
        stream,
    }).ok();
}
```

No accumulation into `live_worker_transcripts` — the lines are ephemeral for live display only. The full output is captured in `ToolCompleted` as before.

### Frontend

**File:** `interface/src/api/client.ts`

```typescript
export interface ToolOutputEvent {
    type: "tool_output";
    agent_id: string;
    channel_id: string | null;
    process_type: ProcessType;
    process_id: string;
    tool_name: string;
    line: string;
    stream: "stdout" | "stderr";
}
```

**File:** `interface/src/hooks/useLiveContext.tsx`

Handle `tool_output` events: append lines to a per-worker output buffer keyed by `process_id`. When a `tool_completed` event arrives for the same process, clear the buffer (the completed result replaces it).

```typescript
const liveToolOutput = useRef<Record<string, string[]>>({});

handlers.tool_output = (event: ToolOutputEvent) => {
    const key = event.process_id;
    if (!liveToolOutput.current[key]) {
        liveToolOutput.current[key] = [];
    }
    liveToolOutput.current[key].push(event.line);
    // trigger re-render for the relevant ToolCall component
};
```

**File:** `interface/src/components/ToolCall.tsx`

When a shell/exec/bash tool is in `"running"` status, render accumulated output lines in a scrollable `<pre>` that auto-scrolls to the bottom. Replace the current "Running..." spinner with the live output view:

```tsx
{pair.status === "running" && liveOutput.length > 0 && (
    <pre className="max-h-60 overflow-auto whitespace-pre-wrap px-3 py-2 font-mono text-tiny text-ink-dull">
        {liveOutput.join("\n")}
    </pre>
)}
```

When no output has arrived yet, keep showing the spinner. Once lines start flowing, show them.

## Part 2: Interactive Detection

### Quiesce Detection

After spawning the process and starting to read output, track the time since the last output line. If no new output arrives for a configurable period (default 5 seconds) and the process is still alive, the command is likely waiting for interactive input.

```rust
const QUIESCE_TIMEOUT: Duration = Duration::from_secs(5);

loop {
    tokio::select! {
        line = stdout_reader.next_line() => {
            match line {
                Ok(Some(text)) => { /* append, broadcast, reset quiesce timer */ }
                Ok(None) => break, // EOF, process closing stdout
                Err(e) => break,
            }
        }
        _ = tokio::time::sleep(QUIESCE_TIMEOUT) => {
            if child.try_wait()?.is_none() {
                // Process alive but silent — likely waiting for input
                interactive_detected = true;
                child.kill().await.ok();
                break;
            }
        }
        _ = tokio::time::sleep(overall_timeout) => {
            // Hard timeout — kill regardless
            child.kill().await.ok();
            break;
        }
    }
}
```

The 5 second quiesce timeout is deliberately longer than typical build pauses (compiler thinking, package resolution) but short enough to catch interactive prompts without wasting too much time. For comparison, the overall timeout is 60s by default.

### Extended ShellOutput

```rust
pub struct ShellOutput {
    pub success: bool,
    pub exit_code: i32,
    pub stdout: String,
    pub stderr: String,
    pub summary: String,
    pub waiting_for_input: bool,  // NEW
}
```

When `waiting_for_input` is true:
- `success` is `false`
- `exit_code` is `-2` (distinct from `-1` for timeout)
- `stdout` contains whatever output was captured before the quiesce
- `summary` includes the hint: "Command appears to be waiting for interactive input. The last output was: ..."

### LLM Guidance

The summary message is the key mechanism. When the LLM sees:

```json
{
  "success": false,
  "exit_code": -2,
  "stdout": "Need to install the following packages:\n  create-vite@8.3.0\nOk to proceed? (y) ",
  "waiting_for_input": true,
  "summary": "Command appears to be waiting for interactive input. The last output was:\n  Ok to proceed? (y) \n\nRetry with --yes, -y, or pipe input (echo y | command) to avoid interactive prompts. Most tools also respect CI=true in the environment."
}
```

It can now make an informed decision. It sees the actual prompt text and knows to retry with `echo y | npm create vite@latest ...` or use a different approach.

### Prompt Updates

**File:** `prompts/en/tools/shell_description.md.j2`

Add after the existing text:

```
Commands run without stdin — interactive prompts that require user input will cause the command to be killed after output stops for 5 seconds. When this happens, the result includes `waiting_for_input: true` and the captured output showing what the command was asking for. Retry with non-interactive flags (--yes, -y, --non-interactive) or pipe input (echo y | command). Setting CI=true also works for most tools — it's already set in the environment.
```

**File:** `prompts/en/worker.md.j2`

Add under the `### shell` section:

```
Commands have no stdin. If a command prompts for input, it will be killed and the result will show `waiting_for_input: true` with the prompt text. Use `--yes` / `-y` flags or pipe input (`echo y | command`) to handle known prompts.
```

### CI=true in Sandbox

**File:** `src/sandbox.rs`

In the environment setup logic shared by `wrap_bubblewrap`, `wrap_sandbox_exec`, and `wrap_passthrough`, add `CI=true` to the hardcoded variables alongside `PATH`, `HOME`, and `TMPDIR`:

```rust
cmd.env("CI", "true");
cmd.env("DEBIAN_FRONTEND", "noninteractive");
```

This is a one-line change that prevents most npm/npx/apt/brew prompts from appearing in the first place. The interactive detection handles the remaining cases.

## Implementation Order

```
Phase 1a  CI=true in sandbox env             src/sandbox.rs (1 line)
Phase 1b  Prompt updates                     prompts/ (2 files)
Phase 2a  ProcessEvent::ToolOutput variant    src/lib.rs
Phase 2b  Spawn-based shell execution         src/tools/shell.rs
Phase 2c  Thread event_tx into ShellTool      src/tools.rs
Phase 2d  ApiEvent::ToolOutput + SSE          src/api/state.rs
Phase 3a  Quiesce detection + kill            src/tools/shell.rs
Phase 3b  waiting_for_input in ShellOutput    src/tools/shell.rs
Phase 4a  Frontend: ToolOutputEvent type      interface/src/api/client.ts
Phase 4b  Frontend: SSE handler               interface/src/hooks/useLiveContext.tsx
Phase 4c  Frontend: live output rendering     interface/src/components/ToolCall.tsx
```

Phase 1 is a quick win — CI=true + prompt updates solve most interactive issues immediately with minimal code change. Phase 2 adds live streaming. Phase 3 adds interactive detection. Phase 4 is the frontend.

## File Changes

**Modified files:**
- `src/lib.rs` — add `ProcessEvent::ToolOutput` variant
- `src/sandbox.rs` — add `CI=true` and `DEBIAN_FRONTEND=noninteractive` to env
- `src/tools/shell.rs` — spawn-based execution, streaming, quiesce detection, `waiting_for_input`
- `src/tools/exec.rs` — same streaming treatment (no quiesce detection, exec is for structured args)
- `src/tools.rs` — pass `event_tx` / process metadata to ShellTool/ExecTool constructors
- `src/api/state.rs` — translate `ProcessEvent::ToolOutput` to `ApiEvent::ToolOutput`
- `prompts/en/tools/shell_description.md.j2` — interactive command guidance
- `prompts/en/worker.md.j2` — interactive shell note
- `interface/src/api/client.ts` — `ToolOutputEvent` type
- `interface/src/hooks/useLiveContext.tsx` — handle `tool_output` SSE events
- `interface/src/components/ToolCall.tsx` — live output rendering for running tools

## Future: PTY Sessions

The streaming + quiesce infrastructure laid here is the foundation for true bidirectional PTY sessions. The extension would:

1. **Add `portable-pty` dependency** — cross-platform PTY allocation
2. **`Sandbox::wrap_pty()`** — returns a `portable_pty::CommandBuilder` with the same env sanitization
3. **`ShellSession` struct** — holds the PTY child, reader, writer; persisted across tool calls within a worker
4. **Input mode** — when the LLM calls `shell` and an active session exists, write to the PTY instead of spawning a new process
5. **PTY merges stdout+stderr** — simplifies stream handling (single output stream)

The key difference from the current design: instead of killing the process on quiesce and telling the LLM to retry, the process stays alive and the LLM sends input. This eliminates wasted work (the first attempt's partial progress is preserved).

This is deferred because:
- The detect-and-retry approach handles most real-world cases (npm, apt, git)
- PTY adds complexity: session lifecycle, cleanup on worker teardown, sandbox integration
- `portable-pty` doesn't accept a pre-built `tokio::process::Command`, so sandbox wrapping needs a parallel code path
- The streaming infrastructure from this design carries over directly

## Notes

- **Quiesce timeout of 5s** is a balance. Too short (1-2s) would false-positive during compilation pauses. Too long (10s+) wastes time when the command is genuinely stuck on a prompt. 5s works for the common cases (npm prompts appear immediately, builds produce output continuously).
- **Exit code -2** for interactive detection is an internal convention. Real exit codes are non-negative. -1 is already used for "failed to execute" and timeout.
- **Stream lines vs chunks:** Broadcasting individual lines (not raw byte chunks) keeps events clean and makes frontend rendering straightforward. Lines are the natural unit for terminal output.
- **Exec tool** gets streaming but not quiesce detection. Exec is for structured program invocation where interactivity is less likely. If needed, quiesce can be added later.
- **Secret scrubbing** still happens on the final `ToolCompleted` event. The per-line `ToolOutput` events should also be scrubbed before broadcast. The scrubber is fast (regex scan) so per-line cost is negligible.
