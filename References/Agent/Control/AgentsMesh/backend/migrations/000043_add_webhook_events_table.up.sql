-- Create webhook_events table for idempotency checking
-- This table stores processed webhook event IDs to prevent duplicate processing

CREATE TABLE IF NOT EXISTS webhook_events (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Unique constraint on event_id + provider to prevent duplicates
    CONSTRAINT uq_webhook_events_event_provider UNIQUE (event_id, provider)
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_webhook_events_event_id ON webhook_events(event_id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_provider ON webhook_events(provider);

-- Create index for cleanup (older events can be pruned)
CREATE INDEX IF NOT EXISTS idx_webhook_events_processed_at ON webhook_events(processed_at);

COMMENT ON TABLE webhook_events IS 'Stores processed webhook event IDs for idempotency';
COMMENT ON COLUMN webhook_events.event_id IS 'Unique event ID from the payment provider';
COMMENT ON COLUMN webhook_events.provider IS 'Payment provider name (stripe, lemonsqueezy, etc.)';
COMMENT ON COLUMN webhook_events.event_type IS 'Type of webhook event';
COMMENT ON COLUMN webhook_events.processed_at IS 'When the event was processed';
