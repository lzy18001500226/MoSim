-- 000156_agents_is_internal.down.sql
BEGIN;

ALTER TABLE agents DROP COLUMN IF EXISTS is_internal;

COMMIT;
