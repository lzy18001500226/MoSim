# Changelog

All notable changes to SwarmCLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.13]

### Changed

- **Simplified Ctrl+C cancellation in Interactive REPL**: Replaced the `Async::Condition`-based cancellation with `swarm.stop` (new SwarmSDK hard stop mechanism). The REPL now calls `@swarm.stop` directly from the INT trap handler, which is safe from signal context (IO.pipe write). Removed `Async::Condition`, monitor task, and nested `Async` block — `execute_with_cancellation` is now a simple `trap` + `@swarm.execute` + `trap restore`. Cancelled results are detected via `result.interrupted?` instead of a local `cancelled` flag.
  - **Files**: `lib/swarm_cli/interactive_repl.rb`

## [2.1.12] - 2025-12-12

### Changed

- **Dependencies**: Updated to `swarm_sdk ~> 2.7.1` for streaming functionality
  - Compatible with new `streaming` configuration option
  - Compatible with new `content_chunk` events (formatters handle gracefully)
  - HumanFormatter silently ignores `content_chunk` events (no else clause in case statement)
  - JsonFormatter passes all `content_chunk` events through to JSON output
  - Ready for future real-time streaming display enhancements

### Notes

- **Future Enhancement**: Real-time streaming display in interactive mode
  - Current behavior: Formatters handle `content_chunk` events gracefully (ignore or pass through)
  - Future: HumanFormatter could display chunks in real-time with spinner coordination
  - No breaking changes - current behavior is forward-compatible

## [2.1.11] - 2025-12-04

### Changed

- **Dependencies**: Updated to `swarm_sdk ~> 2.6.0` for execution timeout support
  - Supports new `execution_timeout` configuration in YAML/DSL
  - Handles new `execution_timeout` and `turn_timeout` events
  - Compatible with breaking change: `timeout` → `request_timeout` rename

## [2.1.10] - 2025-12-03

### Added

- **LLM Request Failed Event Handler**: New display support for `llm_request_failed` events in human-readable output
  - **Event type**: `llm_request_failed` - Emitted by SwarmSDK for non-retryable errors (401, 403, 422, etc.)
  - **Display**: Red error panel with status code, error class, and message
  - **Spinner handling**: Automatically stops agent thinking spinner when error occurs
  - **Message format**:
    ```
    ╔═══ REQUEST FAILED [agent_name] ═══╗
    │ LLM request failed (401)          │
    │ Error: UnauthorizedError: Invalid API key │
    │ This error cannot be automatically recovered │
    ╚════════════════════════════════════╝
    ```
  - **Integration**: Works with SwarmSDK v2.5.5 smart retry strategy
  - **Files**: `lib/swarm_cli/formatters/human_formatter.rb`

### Changed

- **Dependencies**: Updated to `swarm_sdk ~> 2.5.5` for smart retry strategy support

### Fixed

- **JSON Formatter Tests**: Updated tests to reflect current `on_error` behavior
  - Tests now correctly expect error emissions in JSON format
  - Fixed pre-existing test failures from commit 7451bd0
  - Files: `test/swarm_cli/formatters/json_formatter_test.rb`

## [2.1.9]

### Fixed

- **JSON Formatter Error Handling** - Fixed silent failures when using `--output-format json`
  - **Issue**: Errors during initialization or configuration were not emitted in JSON output format
  - **Root cause**: `JsonFormatter#on_error` was a no-op, assuming SwarmSDK would always emit `swarm_stop` events
  - **Problem**: Errors before swarm execution starts (e.g., configuration errors, missing API keys) had no output
  - **Fix**: `JsonFormatter#on_error` now emits proper JSON error events with:
    - `type: "error"`
    - `error_class`: Full class name (e.g., `"SwarmSDK::ConfigurationError"`)
    - `error_message`: Error message
    - `timestamp`: ISO 8601 timestamp
    - `duration`: Execution duration (if available)
    - `backtrace`: Full backtrace array
  - **Impact**: JSON output mode now properly reports all errors, making CLI suitable for automation/scripting
  - **Files**: `lib/swarm_cli/formatters/json_formatter.rb`

## [2.1.8]
- Add reline as dependency

## [2.1.7]

### Dependencies

- Updated `swarm_sdk` to `~> 2.5.1`

## [2.1.6]
- Bump SDK and memory gem versions

## [2.1.5]
- Bump SDK gem version

## [2.1.4]

### Changed

- `ConfigLoader` now accepts both `SwarmSDK::Swarm` and `SwarmSDK::Workflow` instances from Ruby DSL files
  - Updated error messages to reference `Workflow` instead of `NodeOrchestrator`
  - Both swarms and workflows work seamlessly with CLI commands

## [2.1.3]

### Fixed

- **Interactive REPL spinner cleanup** - Fixed spinners not stopping properly
  - Bug: Spinners continued animating after swarm execution completed or on errors
  - Bug: REPL prompt would overlap with spinner animation, causing terminal corruption
  - Fix: Added `spinner_manager.stop_all()` after `execute_with_cancellation()` in all paths
  - Fix: Added defensive cleanup in `on_success()`, `on_error()`, and `run()` ensure block
  - Fix: Ensures spinners stop before displaying results, errors, or REPL prompt
  - Impact: Fixes 100% of interactive mode sessions

### Added

- **LLM API Error and Retry Event Handlers** - CLI now shows LLM API errors and retries
  - Added handler for `llm_retry_attempt` - Shows warning panel during retry attempts
  - Added handler for `llm_retry_exhausted` - Shows error panel when retries are exhausted
  - Added handler for `response_parse_error` - Shows error panel when response parsing fails
  - Displays attempt numbers (e.g., "attempt 2/3"), retry delays, error messages
  - Properly manages spinners during error display (stops "thinking" spinner, restarts "retrying" spinner)
  - Provides clear visibility into API rate limits, timeouts, and parsing errors

## [2.1.2]

### Changed

- **Internal: Updated to use new SwarmSDK loading API**
  - `ConfigLoader` now uses `SwarmSDK.load_file` instead of `SwarmSDK::Swarm.load`
  - `mcp serve` command updated to use `SwarmSDK.load_file`
  - No user-facing changes - all CLI commands work identically
  - Benefits from improved SDK separation (SDK handles strings, CLI handles files)

## [2.1.1]

### Fixed
- **`swarm mcp tools` command initialization** - Fixed crash on startup
  - Bug: Used non-existent `SwarmSDK::Scratchpad` class
  - Fix: Changed to `SwarmSDK::Tools::Stores::ScratchpadStorage` (correct class)
  - Added comprehensive test suite to prevent similar initialization bugs
  - Tests verify command initializes without errors

## [2.1.0]
- Bump gem version with the rest of the gems.

## [2.0.3] - 2025-10-26

### Added
- **`/defrag` Slash Command** - Automated memory defragmentation workflow
  - Discovers semantically related memory entries (60-85% similarity)
  - Creates bidirectional links to build knowledge graph
  - Runs `MemoryDefrag(action: "find_related")` then `MemoryDefrag(action: "link_related")`
  - Accessible via `/defrag` in interactive REPL

## [2.0.2]

### Added
- **Multi-line Input Support** - Interactive REPL now supports multi-line input
  - Press Option+Enter (or ESC then Enter) to add newlines without submitting
  - Press Enter to submit your message
  - Updated help documentation with input tips
- **Request Cancellation** - Press Ctrl+C to cancel an ongoing LLM request
  - Cancels the current request and returns to the prompt
  - Ctrl+C at the prompt still exits the REPL (existing behavior preserved)
  - Uses Async task cancellation for clean interruption

## [2.0.1] - Fri, Oct 17 2025

### Fixed

- Fixed interactive REPL file completion dropdown not closing after typing space following a Tab completion
- Fixed navigation mode not exiting when regular keys are typed after Tab completion

## [2.0.0] - Fri, Oct 17 2025

Initial release of SwarmCLI.

See https://github.com/parruda/claude-swarm/pull/137
