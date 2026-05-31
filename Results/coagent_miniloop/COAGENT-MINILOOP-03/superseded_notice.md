# COAGENT-MINILOOP-03 Superseded Notice

Date: 2026-05-29

Status: superseded_not_visible

## Correction

The previous conclusion was too strong.

`COAGENT-MINILOOP-03` proved that a historical rollout file on disk could be
resumed by `codex exec resume`. It did **not** prove communication with a
currently visible department conversation.

The user confirmed that old department conversations had already been deleted
from the UI. Therefore historical rollout files must not be treated as active
department conversations.

## New Rule

Department dispatch requires:

```text
department_threads.json status == active_visible
```

Any department marked `inactive_ui_deleted` must reject transport dispatch even
if an old rollout file exists on disk.

## Current Registry Meaning

```text
MainAgent:
  status: active_visible
  meaning: current primary project conversation

DispatchCenter / TaskSecretary / ProjectOwner / TestOwner / SecurityOfficer /
GitIntegrator:
  status: inactive_ui_deleted
  meaning: previous UI conversations were deleted; old rollout files are
  diagnostic artifacts only, not valid communication targets
```

## Consequence

`COAGENT-MINILOOP-03` is useful as a negative lesson and transport hardening
case, but it is no longer accepted as the visible multi-conversation proof.

The next valid proof must create or use a user-confirmed currently visible
conversation and then register it as `active_visible`.
