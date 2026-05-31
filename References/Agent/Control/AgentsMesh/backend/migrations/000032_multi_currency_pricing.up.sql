-- Multi-currency pricing support and pricing strategy update
-- Phase 1: Create plan_prices table for multi-currency support

-- 1. Create plan_prices table
CREATE TABLE IF NOT EXISTS plan_prices (
    id BIGSERIAL PRIMARY KEY,
    plan_id BIGINT NOT NULL REFERENCES subscription_plans(id) ON DELETE CASCADE,
    currency VARCHAR(3) NOT NULL,  -- USD, CNY
    price_monthly DECIMAL(10, 2) NOT NULL,
    price_yearly DECIMAL(10, 2) NOT NULL,

    -- Stripe Price IDs (USD only)
    stripe_price_id_monthly VARCHAR(255),
    stripe_price_id_yearly VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(plan_id, currency)
);

CREATE INDEX idx_plan_prices_plan ON plan_prices(plan_id);
CREATE INDEX idx_plan_prices_currency ON plan_prices(currency);

COMMENT ON TABLE plan_prices IS 'Multi-currency pricing for subscription plans';

-- 2. Rename Free plan to Based
UPDATE subscription_plans SET
    name = 'based',
    display_name = 'Based',
    price_per_seat_monthly = 9.9,
    price_per_seat_yearly = 99,
    max_users = 1,
    max_runners = 1,
    max_concurrent_pods = 5,
    max_repositories = 5
WHERE name = 'free';

-- 3. Update Pro plan quotas and pricing
UPDATE subscription_plans SET
    price_per_seat_monthly = 39,
    price_per_seat_yearly = 390,
    max_users = 5,
    max_runners = 10,
    max_concurrent_pods = 10,
    max_repositories = 10
WHERE name = 'pro';

-- 4. Update Enterprise plan quotas and pricing
UPDATE subscription_plans SET
    price_per_seat_monthly = 99,
    price_per_seat_yearly = 990,
    max_users = 50,
    max_runners = 100,
    max_concurrent_pods = 50,
    max_repositories = -1
WHERE name = 'enterprise';

-- 5. Insert USD prices
INSERT INTO plan_prices (plan_id, currency, price_monthly, price_yearly)
SELECT id, 'USD', 9.9, 99 FROM subscription_plans WHERE name = 'based'
ON CONFLICT (plan_id, currency) DO UPDATE SET price_monthly = 9.9, price_yearly = 99;

INSERT INTO plan_prices (plan_id, currency, price_monthly, price_yearly)
SELECT id, 'USD', 39, 390 FROM subscription_plans WHERE name = 'pro'
ON CONFLICT (plan_id, currency) DO UPDATE SET price_monthly = 39, price_yearly = 390;

INSERT INTO plan_prices (plan_id, currency, price_monthly, price_yearly)
SELECT id, 'USD', 99, 990 FROM subscription_plans WHERE name = 'enterprise'
ON CONFLICT (plan_id, currency) DO UPDATE SET price_monthly = 99, price_yearly = 990;

-- 6. Insert CNY prices
INSERT INTO plan_prices (plan_id, currency, price_monthly, price_yearly)
SELECT id, 'CNY', 69, 690 FROM subscription_plans WHERE name = 'based'
ON CONFLICT (plan_id, currency) DO UPDATE SET price_monthly = 69, price_yearly = 690;

INSERT INTO plan_prices (plan_id, currency, price_monthly, price_yearly)
SELECT id, 'CNY', 269, 2690 FROM subscription_plans WHERE name = 'pro'
ON CONFLICT (plan_id, currency) DO UPDATE SET price_monthly = 269, price_yearly = 2690;

INSERT INTO plan_prices (plan_id, currency, price_monthly, price_yearly)
SELECT id, 'CNY', 690, 6900 FROM subscription_plans WHERE name = 'enterprise'
ON CONFLICT (plan_id, currency) DO UPDATE SET price_monthly = 690, price_yearly = 6900;

-- 7. Add subscription expiry index for efficient queries
CREATE INDEX IF NOT EXISTS idx_subscriptions_period_end
ON subscriptions(current_period_end)
WHERE status IN ('active', 'trialing');
