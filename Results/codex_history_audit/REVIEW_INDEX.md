# Codex History Cleanup Review Index

Cleanup execution status: performed on 2026-06-05 00:31-00:40 CST after user
approval and correction in chat.

Actions performed:

- Deleted the one pre-existing archived user thread `019ddf78-e5f7-7b02-bcd9-35ddd016512e` (`你好`).
- Archived 262 DB-marked `thread_source=subagent` threads.
- Temporarily archived 20 additional CoAgent/department/task/test threads, then
  restored them after the user clarified that CoAgent records must not be
  archived.
- This intermediate archived-subagent state was later cancelled by the user;
  all archived subagent records were restored to active history for manual App
  review.
- CoAgent-like records are active and visible again.

Backups:

- `C:\Users\HP\.codex\backups\archive-subagents-delete-archived-20260605-003122`
- `C:\Users\HP\.codex\backups\archive-agentlike-user-threads-20260605-003515`
- `C:\Users\HP\.codex\backups\restore-coagent-visible-threads-20260605-004050`

Post-check summary after the later "unarchive all for manual review" request:

- Total DB rows: 304
- Active rows: 304
- Archived rows: 0
- Active subagent rows: 262
- Archived subagent rows: 0
- Active CoAgent-like rows: 20
- Archived CoAgent-like rows: 0
- Active rollout files present: 298
- Archived rollout files: 0
- SQLite `integrity_check`: `ok`
- SQLite `quick_check`: `ok`
- Backup for this unarchive operation:
  `C:\Users\HP\.codex\backups\unarchive-all-for-manual-review-20260605-005827`.
- App visibility note: if Codex App still does not show restored records, the
  data is already active in Windows `state_5.sqlite`; restart/reload Codex App
  so the patched Codex++ `market-codex-list-pagebuster.js` storage version
  `2026-06-05-unarchived-subagents-visible-v2` clears stale archived/hidden
  localStorage snapshots.
- Known residual: seven active DB rows point to missing rollout files after
  unarchive; these were already file-level gaps or missing archived files, not
  remaining archive flags. IDs:
  `019e0589-1fef-7d92-9b56-09e238ad8840`,
  `019e1aa8-5855-7c83-9db9-a97f1e1050e5`,
  `019e1156-f22f-7823-9e83-96f1506152e0`,
  `019e078b-9fcf-7650-9d05-205ac11d2b41`,
  `019e02b8-5613-74b1-8edb-1b01b8943b7e`,
  `019df629-ebd2-78d2-a031-b32e79d0ebbf`,
  `019de2ae-24e0-7d93-b2f7-bc85d3cafc85`.

Earlier audit files below remain for traceability.

## Review Files

- `archived_subagent_fine_group_review_latest.md`: compact reference sheet
  generated before unarchive. It groups the 262 subagent records into 11
  review groups (`F001` through `F011`) and can still be used as an App review
  guide.
- `archived_subagent_fine_groups_latest.csv`: sortable group table.
- `archived_subagent_fine_group_items_latest.csv`: item-level table with group
  IDs.
- `archived_subagent_group_review_latest.md`: broader 34-group review sheet
  kept for traceability.

Review command convention if group cleanup is requested later:

- `删除 F010 F011`: delete the DH/DHPA archived subagent groups after backup.
- `恢复 F001`: restore a group to active history.
- `保留 F001`: keep a group.

## Primary Files

- `codex_history_review_latest.md`: full categorized report.
- `codex_history_review_latest.csv`: full sortable table.
- `proposed_delete_after_user_review_ids.txt`: default deletion/hide candidates.
- `proposed_keep_after_user_review_ids.txt`: default keep candidates.

## Bucket Counts

- `candidate_delete_or_hide_subagent_ids.tsv`: 263
- `candidate_delete_non_mosim_ids.tsv`: 15
- `candidate_delete_scratch_greeting_ids.tsv`: 5
- `candidate_keep_mosim_user_main_ids.tsv`: 30
- `candidate_keep_codex_infra_user_ids.tsv`: 15
- `needs_manual_review_ids.tsv`: 1
- `proposed_delete_after_user_review_ids.txt`: 270
- `proposed_keep_after_user_review_ids.txt`: 40

## Suggested Policy

1. Delete or hide only after human review.
2. Prefer archiving first if the App supports it; hard delete only after a backup.
3. Keep MoSim user main sessions and Codex infrastructure repair sessions unless explicitly rejected.
