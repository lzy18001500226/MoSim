-- Add run_once flag to cron_jobs.
-- 0 = recurring (default), 1 = one-time job that auto-disables after first run.
ALTER TABLE cron_jobs ADD COLUMN run_once INTEGER NOT NULL DEFAULT 0;
