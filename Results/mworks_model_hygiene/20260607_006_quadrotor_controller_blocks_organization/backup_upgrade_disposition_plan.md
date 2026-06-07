# Backup And Upgrade Disposition Plan

This is a read-only disposition plan. No backup or upgrade directory is moved, renamed, archived, or deleted in task 006.

## Observed Backup Roots

- `AWFF_AttitudeInnerLoop_Sysblock_backup`
- `AWFF_InnovationGraphicalControllers_backup`
- `AWFF_MotorMixer_Sysblock_backup`
- `AWFF_PID_Sysblock_Demo_backup`
- `AWFF_PositionOuterLoop_Sysblock_backup`

Each observed backup root contains an `upgrade/<timestamp>/...mo` history shape. These look like MWORKS/Sysplorer upgrade backups, not active public controller entries.

## Proposed First Package-Shell Treatment

- Exclude `*_backup` directories from `package.order` category display.
- Do not delete or archive them in the package-shell write gate.
- Record them as `backup_upgrade_history_candidate_preserve_until_manual_mworks_review`.
- Require manual/MWORKS review before any cleanup, because they may preserve pre-upgrade graphical metadata or recovery source.

## Manual Review Triggers

- A backup file differs materially from the active file in controller equations, ports, or graphical annotations.
- A current scenario, script, or result artifact references a backup path.
- Sysplorer load/check behavior depends on a backup file being present.
- PMO wants to archive or delete history directories.

## Future Cleanup Gate

A later cleanup task may propose moving backup history under a dedicated archive only after:

1. Static diff compares active versus backup `.mo` files.
2. No scenario/config/model references the backup paths.
3. PMO approves archive/delete scope explicitly.
4. A reversible backup manifest is written before any file move/delete.
