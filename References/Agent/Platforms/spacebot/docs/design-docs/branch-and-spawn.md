# Branch-and-Spawn

A combined tool that branches for memory recall, then programmatically spawns a worker with the enriched task. The branch thinks, the worker does, and the handoff is guaranteed — not dependent on the branch LLM calling a tool.

## Problem

Today, branching and worker spawning are independent. The channel can branch (think), or spawn a worker (do). If a task would benefit from memory context — "refactor the auth module" when there are 15 memories about auth decisions, coding preferences, and past refactors — the channel has two options:

1. **Spawn a worker directly.** The worker gets a bare task description. No memory context. It works blind.
2. **Branch first, hope it spawns a worker.** The branch has memory tools and conversation context. It can recall relevant memories and synthesize them into a richer task. But relying on the branch LLM to call `spawn_worker` is fragile — it might not, or it might pass a degraded version of what it learned.

Neither path is great. The first wastes memory context. The second has an unreliable handoff.

## Solution

A new tool: `branch_and_spawn`. One tool call from the channel. Two phases, connected programmatically.

```
Channel calls branch_and_spawn(task, worker_args)
  → Branch spawns with memory tools + enrichment-focused prompt
  → Branch recalls memories, synthesizes context, returns enriched task
  → Branch exits
  → Channel receives BranchResult
  → Channel programmatically spawns worker with the enriched task (not LLM-driven)
  → Worker runs with full context
```

The branch never needs to call `spawn_worker`. It just thinks and concludes. The conclusion becomes the worker's task. The handoff is code, not LLM behavior.

## Tool Interface

```rust
pub struct BranchAndSpawnArgs {
    /// What the worker should accomplish. The branch will enrich this
    /// with relevant memories before passing it to the worker.
    pub task: String,
    /// Whether this is an interactive worker.
    pub interactive: bool,
    /// Optional skill name for the worker.
    pub skill: Option<String>,
    /// Worker type: "builtin" or "opencode".
    pub worker_type: Option<String>,
    /// Working directory (required for opencode workers).
    pub directory: Option<String>,
}
```

The channel LLM sees this as a single tool. It provides the task and worker config. The branch and worker are implementation details.

## Branch Behavior

The branch in this flow gets a specialized system prompt — not the standard branch prompt. It knows:

- Its job is to enrich a worker task, not to answer a question
- It should recall memories relevant to the task domain
- Its conclusion will be forwarded directly to a worker as the task description
- It should synthesize, not dump — the worker needs actionable context, not 50 raw memories

The prompt should instruct the branch to structure its output as a complete worker task: what to do, relevant context from memory, constraints, preferences, prior decisions. Everything the worker needs to work independently.

## Programmatic Handoff

The key design choice: the branch-to-worker handoff happens in Rust, not in the LLM.

When the channel creates a `branch_and_spawn` branch, it stores the worker args alongside the branch tracking state. When `handle_event` receives the `BranchResult`:

1. Check if this branch ID is a `branch_and_spawn` branch
2. If yes: spawn a worker using the stored args, with the branch conclusion as the task
3. The branch result is NOT injected into channel history (the worker result will be)
4. The worker runs normally and reports back via `WorkerComplete`

This is similar to how memory persistence branches are handled — they complete silently without injecting into history. The difference is that `branch_and_spawn` branches trigger a worker on completion instead of just disappearing.

```rust
// In Channel, alongside memory_persistence_branches
branch_and_spawn_branches: HashMap<BranchId, PendingWorkerArgs>,
```

```rust
// In handle_event, BranchResult arm
if let Some(worker_args) = self.branch_and_spawn_branches.remove(branch_id) {
    // Spawn worker with branch conclusion as the enriched task
    spawn_worker_from_state(&self.state, &conclusion, worker_args.interactive, worker_args.skill.as_deref())
        .await?;
} else if self.memory_persistence_branches.remove(branch_id) {
    // existing silent completion
} else {
    // existing: inject into history + retrigger
}
```

## Coexistence with Direct Spawn

Both tools exist simultaneously by default:

- `spawn_worker` — direct dispatch, no memory enrichment. Good for quick tasks where context isn't needed. "Run the tests." "Read this file."
- `branch_and_spawn` — branch first for memory context, then dispatch. Good for tasks where domain knowledge matters. "Refactor the auth module." "Debug the payment flow."

The channel LLM chooses which path based on the system prompt guidance.

## Config: Forcing Branch-First Workers

Some operators may want all workers to go through memory enrichment. A config option disables direct `spawn_worker` on the channel, leaving only `branch_and_spawn`.

```toml
[defaults]
require_branch_before_worker = false
```

When `true`:
- `spawn_worker` is not registered as a channel tool
- Only `branch_and_spawn` is available
- The channel prompt reflects this (no mention of direct worker spawning)

When `false` (default):
- Both tools are available
- The channel prompt explains when to use each

This is a per-agent setting, resolved via the standard `agent override > defaults > hardcoded` chain.

## System Prompt Changes

### Channel Prompt

The delegation section gets updated based on config:

**Both tools available (default):**

```markdown
**Worker (direct)** — for quick tasks where memory context isn't needed. "Run the tests."
"Check the build." The worker gets exactly what you tell it, nothing more.

**Worker (with context)** — use `branch_and_spawn` when the task benefits from memory.
"Refactor the auth module" — a branch will recall relevant memories (past decisions,
preferences, prior work) and enrich the task before the worker starts. Prefer this
for domain-specific work where history matters.
```

**Only branch_and_spawn (forced):**

```markdown
**Worker** — all workers go through a branch first. You call `branch_and_spawn` with the
task, a branch recalls relevant memories, and the enriched task is forwarded to a worker.
This ensures workers always have the best available context.
```

These are Jinja conditionals in `channel.md.j2`, driven by a `require_branch_before_worker` template variable.

### Branch-and-Spawn Branch Prompt

A new prompt template: `branch_and_spawn.md.j2`. Distinct from the standard branch prompt.

```markdown
You are a preparation branch. Your job is to enrich a worker task with relevant context
from memory.

## The Task

{{ task }}

## Your Job

1. Recall memories relevant to this task — decisions, preferences, prior work, constraints.
2. Synthesize what you find into actionable context for the worker.
3. Return a complete, enriched task description that includes:
   - The original task objective
   - Relevant context from memory (decisions, preferences, patterns)
   - Any constraints or considerations the worker should know
   - Specific instructions informed by what you recalled

The worker will receive your conclusion as its entire task. It has no conversation history
and no memory access. Everything it needs must be in your output.

Do not include metadata about your search process. The worker doesn't need to know you
searched 12 memories and found 5 relevant ones. Just give it the enriched task.
```

## What the Channel Sees

From the channel's perspective, `branch_and_spawn` is a single async operation. The channel calls it, gets a confirmation ("Branch started, will spawn worker when ready"), and moves on. Eventually it gets a `WorkerComplete` event — same as a direct `spawn_worker`.

The status block shows both phases:

```
Active:
  Branch b-1234: preparing worker task (enriching with memory context)
```

Then when the branch completes and the worker starts:

```
Active:
  Worker w-5678: refactor auth module (enriched from memory)
```

## Implementation Phases

### Phase 1: Core Flow

1. Add `PendingWorkerArgs` struct to hold spawn config during branch execution
2. Add `branch_and_spawn_branches: HashMap<BranchId, PendingWorkerArgs>` to `Channel`
3. Create `branch_and_spawn.md.j2` prompt template
4. Create `BranchAndSpawnTool` in `tools/branch_and_spawn.rs`
5. Add `spawn_branch_and_spawn_from_state()` to `channel.rs`
6. Update `handle_event` to detect `branch_and_spawn` branches and spawn workers
7. Register the tool in `add_channel_tools` / `remove_channel_tools`
8. Add to `tools.rs` module declarations and re-exports

### Phase 2: Config

1. Add `require_branch_before_worker` to `DefaultsConfig`, `AgentConfig`, `ResolvedAgentConfig`
2. Add TOML deserialization support
3. Add to `RuntimeConfig` as an `ArcSwap<bool>`
4. Wire into `add_channel_tools` — conditionally skip `SpawnWorkerTool` registration
5. Wire into `render_channel_prompt` as a template variable
6. Support hot-reload in `reload_config`

### Phase 3: Prompt Updates

1. Update `channel.md.j2` with conditional delegation guidance
2. Create `branch_and_spawn.md.j2`
3. Register template in `PromptEngine`
4. Add `render_branch_and_spawn_prompt()` convenience method
5. Wire the `require_branch_before_worker` flag into template context

## Edge Cases

**Branch fails.** If the enrichment branch errors out or hits max turns, the worker should still spawn with the original (unenriched) task. The branch failure is logged but doesn't block the work. Partial conclusions from max-turns branches are usable — they'll have whatever the branch managed to recall.

**Empty memory recall.** If the branch finds no relevant memories, it should still return a clean task description (essentially passing through the original task with a note that no additional context was found). The worker spawns regardless.

**Branch cancelled.** If the user cancels the branch (via the cancel tool), the pending worker args are cleaned up. No worker spawns. The channel gets a cancellation event and can inform the user.

**Interactive workers.** `branch_and_spawn` supports interactive workers. The branch enriches the initial task, the worker starts as interactive, and the channel can route follow-ups to it normally.

## What This Doesn't Change

- Workers still have no memory access. The branch does the recall; the worker gets the result.
- The standard `branch` tool is unchanged. Branches for thinking (not worker prep) work exactly as before.
- Worker tool sets are unchanged. The enriched task is just a better prompt, not a different tool configuration.
- The compactor, cortex, and memory persistence flows are unaffected.
