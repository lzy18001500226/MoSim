-- Payment System Migration
-- Adds payment orders, invoices, licenses tables and extends subscriptions

-- ===========================================
-- Extend subscriptions table
-- ===========================================

-- Add new columns to subscriptions
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS payment_provider VARCHAR(50);
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS auto_renew BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS seat_count INT NOT NULL DEFAULT 1;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS canceled_at TIMESTAMPTZ;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS frozen_at TIMESTAMPTZ;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS downgrade_to_plan VARCHAR(50);
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS next_billing_cycle VARCHAR(20);
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS alipay_agreement_no VARCHAR(255);
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS wechat_contract_id VARCHAR(255);

-- Add comments
COMMENT ON COLUMN subscriptions.payment_provider IS 'Payment provider: stripe, alipay, wechat, license';
COMMENT ON COLUMN subscriptions.payment_method IS 'Payment method: card, alipay_qr, wechat_native, alipay_agreement, wechat_contract';
COMMENT ON COLUMN subscriptions.auto_renew IS 'Whether subscription auto-renews';
COMMENT ON COLUMN subscriptions.seat_count IS 'Number of seats purchased';
COMMENT ON COLUMN subscriptions.canceled_at IS 'When subscription was canceled';
COMMENT ON COLUMN subscriptions.cancel_at_period_end IS 'Cancel at end of current period';
COMMENT ON COLUMN subscriptions.frozen_at IS 'When subscription was frozen due to non-payment';
COMMENT ON COLUMN subscriptions.downgrade_to_plan IS 'Plan to downgrade to at period end';
COMMENT ON COLUMN subscriptions.next_billing_cycle IS 'Billing cycle for next period (if changing)';

-- ===========================================
-- Extend subscription_plans table
-- ===========================================

ALTER TABLE subscription_plans ADD COLUMN IF NOT EXISTS price_per_seat_yearly DECIMAL(10, 2) DEFAULT 0;
ALTER TABLE subscription_plans ADD COLUMN IF NOT EXISTS stripe_price_id_monthly VARCHAR(255);
ALTER TABLE subscription_plans ADD COLUMN IF NOT EXISTS stripe_price_id_yearly VARCHAR(255);

-- Update yearly prices (10 months = 2 months free)
UPDATE subscription_plans SET price_per_seat_yearly = price_per_seat_monthly * 10 WHERE price_per_seat_yearly = 0 OR price_per_seat_yearly IS NULL;

-- ===========================================
-- Payment Orders Table
-- ===========================================

CREATE TABLE payment_orders (
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Order identification
    order_no VARCHAR(64) NOT NULL UNIQUE,
    external_order_no VARCHAR(255),

    -- Order type and relation
    order_type VARCHAR(50) NOT NULL,  -- subscription, seat_purchase, plan_upgrade, renewal
    plan_id BIGINT REFERENCES subscription_plans(id),
    billing_cycle VARCHAR(20),
    seats INT DEFAULT 1,

    -- Amount information
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    actual_amount DECIMAL(10, 2) NOT NULL,

    -- Payment information
    payment_provider VARCHAR(50) NOT NULL,  -- stripe, alipay, wechat
    payment_method VARCHAR(50),

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, processing, succeeded, failed, canceled, refunded

    -- Metadata
    metadata JSONB DEFAULT '{}',
    failure_reason TEXT,

    -- Idempotency
    idempotency_key VARCHAR(64) UNIQUE,

    -- Timestamps
    expires_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_id BIGINT NOT NULL REFERENCES users(id)
);

CREATE INDEX idx_payment_orders_org ON payment_orders(organization_id);
CREATE INDEX idx_payment_orders_status ON payment_orders(status);
CREATE INDEX idx_payment_orders_order_no ON payment_orders(order_no);
CREATE INDEX idx_payment_orders_created ON payment_orders(created_at);
CREATE INDEX idx_payment_orders_external ON payment_orders(external_order_no);

COMMENT ON TABLE payment_orders IS 'Payment orders for subscriptions, seat purchases, and upgrades';

-- ===========================================
-- Payment Transactions Table
-- ===========================================

CREATE TABLE payment_transactions (
    id BIGSERIAL PRIMARY KEY,
    payment_order_id BIGINT NOT NULL REFERENCES payment_orders(id) ON DELETE CASCADE,

    -- Transaction information
    transaction_type VARCHAR(50) NOT NULL,  -- payment, refund, chargeback
    external_transaction_id VARCHAR(255),

    -- Amount
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',

    -- Status
    status VARCHAR(50) NOT NULL,  -- pending, succeeded, failed

    -- Webhook related
    webhook_event_id VARCHAR(255),
    webhook_event_type VARCHAR(100),
    raw_payload JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payment_transactions_order ON payment_transactions(payment_order_id);
CREATE INDEX idx_payment_transactions_external ON payment_transactions(external_transaction_id);
CREATE INDEX idx_payment_transactions_webhook ON payment_transactions(webhook_event_id);

COMMENT ON TABLE payment_transactions IS 'Payment transaction history and webhook events';

-- ===========================================
-- Invoices Table
-- ===========================================

CREATE TABLE invoices (
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    payment_order_id BIGINT REFERENCES payment_orders(id),

    -- Invoice information
    invoice_no VARCHAR(64) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',  -- draft, issued, paid, void

    -- Amount
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    subtotal DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total DECIMAL(10, 2) NOT NULL,

    -- Billing information
    billing_name VARCHAR(255),
    billing_email VARCHAR(255),
    billing_address JSONB,

    -- Invoice period
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Line items
    line_items JSONB NOT NULL DEFAULT '[]',

    -- PDF
    pdf_url TEXT,

    -- Timestamps
    issued_at TIMESTAMPTZ,
    due_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_invoices_org ON invoices(organization_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_invoice_no ON invoices(invoice_no);

COMMENT ON TABLE invoices IS 'Invoice records for billing history';

-- ===========================================
-- Licenses Table (OnPremise)
-- ===========================================

CREATE TABLE licenses (
    id BIGSERIAL PRIMARY KEY,

    -- License identification
    license_key VARCHAR(255) NOT NULL UNIQUE,

    -- License information
    organization_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,

    -- License scope
    plan_name VARCHAR(50) NOT NULL,
    max_users INT NOT NULL DEFAULT -1,
    max_runners INT NOT NULL DEFAULT -1,
    max_repositories INT NOT NULL DEFAULT -1,
    max_concurrent_pods INT NOT NULL DEFAULT -1,
    features JSONB DEFAULT '{}',

    -- Validity
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,

    -- Signature verification
    signature TEXT NOT NULL,
    public_key_fingerprint VARCHAR(64),

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    revoked_at TIMESTAMPTZ,
    revocation_reason TEXT,

    -- Activation tracking
    activated_at TIMESTAMPTZ,
    activated_org_id BIGINT REFERENCES organizations(id),
    last_verified_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_licenses_key ON licenses(license_key);
CREATE INDEX idx_licenses_org ON licenses(activated_org_id);

COMMENT ON TABLE licenses IS 'License keys for OnPremise deployments';

-- ===========================================
-- Update existing data
-- ===========================================

-- Set default seat_count based on current member count
UPDATE subscriptions s
SET seat_count = GREATEST(1, (
    SELECT COUNT(*) FROM organization_members om
    WHERE om.organization_id = s.organization_id
))
WHERE seat_count = 1;

-- Set default payment_provider for existing subscriptions
UPDATE subscriptions
SET payment_provider = 'stripe'
WHERE payment_provider IS NULL AND stripe_subscription_id IS NOT NULL;
