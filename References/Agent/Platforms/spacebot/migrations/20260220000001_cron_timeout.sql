-- Add optional per-job timeout to cron_jobs.
-- NULL means "use the default" (120 seconds).
ALTER TABLE cron_jobs ADD COLUMN timeout_secs INTEGER;
