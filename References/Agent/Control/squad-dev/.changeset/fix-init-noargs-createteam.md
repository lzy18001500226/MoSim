---
"@bradygaster/squad-cli": patch
---

fix: `/init` with no args now accepts follow-up message as cast prompt, and `createTeam` correctly creates `team.md`/`routing.md` in fresh projects

Two related bugs in the TUI init flow:

1. After `/init` (no args) showed guidance text, the user's follow-up message hit the "No Squad team found" guard instead of starting team casting. Fixed by tracking `awaitingInitPrompt` state in `App.tsx` and bypassing the team-file guard in `handleDispatch` when `skipCastConfirmation` is explicitly set.

2. After confirming a team proposal, `createTeam` silently skipped creating `team.md` and `routing.md` in a fresh project (no `.squad/` directory), causing the coordinator to immediately say "no team yet" after showing "Team hired!". Fixed with else-branches that create both files from scratch when they don't exist.
