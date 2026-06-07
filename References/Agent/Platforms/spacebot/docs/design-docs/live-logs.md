# Live Logs

A real-time log viewer in the interface that streams tracing output from the running instance. Accessible from the sidebar as a top-level page. Captures info/warn/error events into an in-memory ring buffer and streams them to the browser via SSE.

## Concept

Hosted users have no shell access to their Fly VM. Self-hosted users running in daemon mode have logs in rotating files they'd need to SSH or tail manually. The logs page gives both audiences a live tail + recent history without leaving the dashboard.

Key properties:
- **In-memory ring buffer** — last 1,000 tracing events, no disk persistence beyond what the existing `tracing-appender` already does
- **SSE streaming** — new log entries pushed to the browser as they happen, same pattern as `/api/events`
- **Client-side filtering** — level dropdown (all/info/warn/error) + free-text search over target and message
- **No debug/trace** — only captures info, warn, error to keep the buffer useful and the noise low
- **Both modes** — the buffer layer is active in foreground and background (daemon) mode

## Data Model

No database tables. The buffer lives in memory and resets on restart.

```rust
pub struct LogEntry {
    pub timestamp: String,     // ISO 8601
    pub level: String,         // "INFO" | "WARN" | "ERROR"
    pub target: String,        // tracing target (module path)
    pub message: String,       // formatted event message
}
```

## Phase 1: Tracing Buffer Layer

### 1a. `LogBufferLayer`

New custom `tracing_subscriber::Layer` in `src/api/logs.rs`:

- Implements `on_event()` to capture events at INFO level and above
- Extracts: timestamp (chrono::Utc::now), level, target, and the formatted message field from the event visitor
- Pushes each `LogEntry` into a bounded `VecDeque` (cap 1,000, drop oldest on overflow)
- Also sends each entry through a `broadcast::Sender<LogEntry>` for SSE subscribers
- Storage: `Arc<Mutex<VecDeque<LogEntry>>>` — mutex contention is negligible since writes are fast pushes and reads are infrequent (page load only)

### 1b. `LogBuffer` Handle

Opaque struct returned from tracing init:

```rust
pub struct LogBuffer {
    entries: Arc<Mutex<VecDeque<LogEntry>>>,
    tx: broadcast::Sender<LogEntry>,
}
```

Methods:
- `snapshot(limit: usize) -> Vec<LogEntry>` — clone the last N entries from the buffer
- `subscribe() -> broadcast::Receiver<LogEntry>` — get a receiver for the SSE stream

### 1c. Tracing Init Changes

Both `init_foreground_tracing()` and `init_background_tracing()` change from:

```rust
tracing_subscriber::fmt()
    .with_env_filter(filter)
    .init();
```

To composing a `Registry` with two layers:

```rust
use tracing_subscriber::prelude::*;

let log_buffer = LogBuffer::new();
let buffer_layer = LogBufferLayer::new(log_buffer.clone());

tracing_subscriber::registry()
    .with(filter)
    .with(fmt_layer)
    .with(buffer_layer)
    .init();

// return log_buffer
```

Both functions return `LogBuffer`. The `"registry"` feature needs to be added to `tracing-subscriber` in `Cargo.toml`.

## Phase 2: API Endpoints

### 2a. `GET /api/logs`

Returns the current buffer contents. Query params:
- `limit` (optional, default 1000) — max entries to return

Response:
```json
{
  "entries": [
    {
      "timestamp": "2026-02-19T10:30:45.123Z",
      "level": "INFO",
      "target": "spacebot::agent::channel",
      "message": "processing inbound message"
    }
  ]
}
```

### 2b. `GET /api/logs/stream`

SSE endpoint. Each event:

```
event: log
data: {"timestamp":"2026-02-19T10:30:45.123Z","level":"WARN","target":"spacebot::llm::model","message":"retrying after rate limit"}
```

Uses `broadcast::subscribe()` + `async_stream` with 15s keepalive, identical pattern to `events_sse`.

### 2c. State Wiring

`ApiState` gets a new field:
```rust
pub log_buffer: Option<LogBuffer>,
```

Optional because `ApiState` is constructed before tracing init returns the buffer. Set via a new `set_log_buffer()` method after init, or passed through construction. The handlers return empty results if the buffer isn't set.

Alternatively — since tracing init happens before `ApiState::new()` in `main.rs`, the `LogBuffer` can be passed directly into a new constructor variant or set immediately after construction.

## Phase 3: Frontend

### 3a. API Client

New types in `interface/src/api/client.ts`:

```typescript
interface LogEntry {
    timestamp: string;
    level: "INFO" | "WARN" | "ERROR";
    target: string;
    message: string;
}

interface LogsResponse {
    entries: LogEntry[];
}
```

New methods on the `api` object:
```typescript
logs: (limit?: number) =>
    fetchJson<LogsResponse>(`/logs${limit ? `?limit=${limit}` : ""}`),
logsStreamUrl: `${API_BASE}/logs/stream`,
```

### 3b. Logs Page Component

New file `interface/src/routes/Logs.tsx`. Top-level page following the same layout as Overview/Settings:

**Header bar:**
- "Logs" title
- Level filter dropdown (All / Info / Warn / Error)
- Text search input (filters target + message)
- Auto-scroll toggle
- Pause/resume streaming toggle

**Log display:**
- `overflow-y-auto` container, auto-scrolls to bottom when new entries arrive (unless user has scrolled up)
- "New logs below" indicator when scrolled up and new entries arrive
- Each entry rendered as a single row:
  - Monospace timestamp (`HH:MM:SS.mmm`)
  - Level badge — color-coded (info: blue/cyan, warn: amber, error: red)
  - Target — dimmed, truncated to last 2-3 segments
  - Message text

**Data flow:**
1. On mount, fetch `GET /api/logs` for buffer catch-up
2. Connect to `/api/logs/stream` SSE via `useEventSource` hook
3. Append new entries to local state array
4. Client-side filter by level + search text (applied to the local array, not re-fetched)
5. Cap frontend array at 2,000 entries to avoid browser memory bloat

### 3c. Router Update

Replace the inline "Logs coming soon" placeholder in `router.tsx` with the `Logs` component:

```tsx
import { Logs } from "@/routes/Logs";

const logsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/logs",
    component: function LogsPage() {
        return <Logs />;
    },
});
```

### 3d. Sidebar Link

Add "Logs" to the sidebar between Settings and the Agents divider, in both collapsed and expanded modes:

- Expanded: text link matching the Dashboard/Settings pattern
- Collapsed: icon-only link using the `LeftToRightListBulletIcon` (already imported in Sidebar.tsx)
- Active state: highlight when route matches `/logs`

## Build Order

```
Phase 1a-1c  Tracing buffer layer    Rust, no API dependency
Phase 2a-2c  API endpoints           depends on Phase 1
Phase 3a     API client types        depends on Phase 2
Phase 3b-3d  UI components           depends on Phase 3a
```

Phase 1 and Phase 2 can be implemented together since they're in the same files. Phase 3 is entirely frontend.

## File Changes

**New files:**
- `src/api/logs.rs` — `LogBufferLayer`, `LogBuffer`, `LogEntry`, handler functions

**Modified files:**
- `Cargo.toml` — add `"registry"` feature to `tracing-subscriber`
- `src/api.rs` — add `mod logs` + re-export `LogBuffer`
- `src/api/state.rs` — add `log_buffer` field to `ApiState`
- `src/api/server.rs` — register `/logs` and `/logs/stream` routes
- `src/daemon.rs` — return `LogBuffer` from both tracing init functions
- `src/main.rs` — capture `LogBuffer`, pass to `ApiState`
- `interface/src/api/client.ts` — `LogEntry` type, `LogsResponse`, api methods
- `interface/src/routes/Logs.tsx` — log viewer page
- `interface/src/router.tsx` — replace placeholder with `Logs` component
- `interface/src/components/Sidebar.tsx` — add Logs nav link

## Notes

- The ring buffer resets on instance restart. This is fine — users needing historical logs can check the rolling log files on disk (daemon mode) or stdout (foreground mode). The UI is for live observation.
- `broadcast::channel(256)` for the log stream is sufficient. Log events are small and SSE clients that lag will get a `Lagged` error and can reconnect.
- The `Mutex` on the ring buffer is standard `std::sync::Mutex`, not `tokio::sync::Mutex`. The critical section is a `push_back` + conditional `pop_front` — sub-microsecond, no async work inside.
- Filtering happens client-side to keep the backend simple. The buffer is small enough (1k entries) that sending everything and filtering in JS is fine.
