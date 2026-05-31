-- Add webhook_config column to repositories table
-- Stores webhook configuration as JSONB for automatic webhook registration

ALTER TABLE repositories ADD COLUMN IF NOT EXISTS webhook_config JSONB;

COMMENT ON COLUMN repositories.webhook_config IS 'Webhook configuration stored as JSONB (id, url, secret, events, is_active, needs_manual_setup, last_error, created_at)';
