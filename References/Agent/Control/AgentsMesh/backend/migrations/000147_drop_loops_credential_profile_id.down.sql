-- Reverse of 000137: re-add the legacy column (BIGINT, nullable). Note that
-- after this column is restored, application code no longer writes to it —
-- this rollback is only for schema parity in dev/staging.
ALTER TABLE loops ADD COLUMN IF NOT EXISTS credential_profile_id BIGINT;
