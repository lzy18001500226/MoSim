# COAGENT-MINILOOP-02 Retrospective

## What Worked

- The separate Codex CLI execution surface followed the scoped packet.
- It respected the intended file boundary and wrote only the result packet.
- The result router accepted the packet with no warnings.
- Runtime state moved to `done`.

## What Did Not Get Proven

- The proof used Codex CLI `exec`, not Codex App visible thread UI.
- The proof did not use the existing department `codex exec resume` transport.
- The proof did not test App/VSCode live session listing or synchronization.

## Process Risks

- A CLI-created session may not satisfy the user's preferred UI visibility
  requirement if the next objective is Codex App review surface.
- The scoped worker used `apply_patch`; that is acceptable here because the
  only write target was the declared result packet, but future workers need
  strict write-scope checks.

## Improvement For Next Loop

`COAGENT-MINILOOP-03` should prove one of:

1. dispatch into an existing visible department conversation via
   `codex exec resume`; or
2. Codex App / VSCode visibility of a newly created scoped conversation.
