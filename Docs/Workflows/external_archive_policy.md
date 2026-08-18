# External Archive Policy

> Use this workflow when moving a completed or frozen MoSim artifact out of
> the working repository or documenting an external archive receipt.

## Canonical Root

The only allowed destination for new MoSim archive batches is:

```text
E:\刘致远18001500226\MoSim_Archive\<archive-id>\
```

`C:\Users\HP\Desktop\MoSim_Archive` is a retired historical source/archive
location. It is not a destination for new batches and must not be recreated.
Historical audit records may retain it as a source identity.

## Required Preconditions

1. Identify one candidate batch and its repository-relative source paths.
2. Complete the applicable dependency/reference audit before moving anything.
3. Copy only to one new, uniquely named direct child of the E: root above.
   Active archivers reject all other external roots and nested destinations.
4. Write `ARCHIVE_README.md`, `ARCHIVE_MANIFEST.json`, and `SHA256SUMS.txt` in
   the destination batch.
5. Verify every destination file against the source SHA-256 values.
6. Record whether source deletion is authorized. It is `false` by default.

An approved removal is a separate task after successful copy verification,
consumer audit, and an original-location tombstone where applicable. Never
infer that approval from a batch name, a prior copy, free disk space, or a
source directory that happens to exist on C:.

## Scope Boundaries

- Do not archive active model roots, runtime configuration, UI/UE assets, or
  evidence required by an active task without the owning task's explicit
  approval and dependency audit.
- An external copy is a recovery point, not proof of controller, planner,
  simulation, runtime, or release acceptance.
- Preserve historical receipt paths as historical facts, but label them as
  legacy locations rather than resolving them as the current default root.

## Current Reconciliation Receipt

The 2026-08-10 desktop-archive reconciliation is a verified copy from the C:
legacy root to:

```text
E:\刘致远18001500226\MoSim_Archive\20260810_desktop_archive_reconciliation\
```

Its `ARCHIVE_MANIFEST.json` records `349` verified files,
`1,605,933,452` source bytes, zero missing files, zero source or target hash
mismatches, and `source_deletion_authorized: true`. After the completed
revalidation, the C: source was removed under the recorded user authorization.
