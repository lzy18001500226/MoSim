-- Migration: 000013_add_promo_codes.up.sql
-- Description: Add promo codes tables for promotional code management

-- Promo codes table
CREATE TABLE promo_codes (
    id BIGSERIAL PRIMARY KEY,

    -- Basic info
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Type: media, partner, campaign, internal, referral
    type VARCHAR(50) NOT NULL,

    -- Benefit
    plan_name VARCHAR(50) NOT NULL,
    duration_months INT NOT NULL,

    -- Usage limits
    max_uses INT,
    used_count INT NOT NULL DEFAULT 0,
    max_uses_per_org INT NOT NULL DEFAULT 1,

    -- Validity period
    starts_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Audit
    created_by_id BIGINT REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for promo_codes
CREATE INDEX idx_promo_codes_code ON promo_codes(code);
CREATE INDEX idx_promo_codes_type ON promo_codes(type);
CREATE INDEX idx_promo_codes_plan_name ON promo_codes(plan_name);
CREATE INDEX idx_promo_codes_is_active ON promo_codes(is_active) WHERE is_active = TRUE;

-- Promo code redemptions table
CREATE TABLE promo_code_redemptions (
    id BIGSERIAL PRIMARY KEY,

    -- References
    promo_code_id BIGINT NOT NULL REFERENCES promo_codes(id) ON DELETE RESTRICT,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id),

    -- Snapshot of redemption
    plan_name VARCHAR(50) NOT NULL,
    duration_months INT NOT NULL,

    -- Previous state
    previous_plan_name VARCHAR(50),
    previous_period_end TIMESTAMPTZ,

    -- New state
    new_period_end TIMESTAMPTZ NOT NULL,

    -- Audit info
    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for redemptions
CREATE INDEX idx_promo_redemptions_code_id ON promo_code_redemptions(promo_code_id);
CREATE INDEX idx_promo_redemptions_org_id ON promo_code_redemptions(organization_id);
CREATE INDEX idx_promo_redemptions_user_id ON promo_code_redemptions(user_id);
CREATE INDEX idx_promo_redemptions_created_at ON promo_code_redemptions(created_at);

-- Unique constraint: each org can only use a promo code once (per org limit)
CREATE UNIQUE INDEX idx_promo_redemptions_org_code_unique
    ON promo_code_redemptions(organization_id, promo_code_id);

-- Trigger for updated_at on promo_codes
CREATE TRIGGER update_promo_codes_updated_at
    BEFORE UPDATE ON promo_codes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
