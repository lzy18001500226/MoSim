-- =============================================================================
-- LemonSqueezy Variant IDs Configuration for Development
-- =============================================================================
--
-- These Variant IDs are specific to the AgentsMesh development LemonSqueezy account.
-- Store ID: 282541 (agentsmeshai.lemonsqueezy.com)
--
-- Product Structure:
--   Based Monthly (Product 800605) -> Variant 1262536 ($9.90/month)
--   Based Yearly  (Product 800606) -> Variant 1262537 ($99/year)
--   Pro Monthly   (Product 800601) -> Variant 1262532 ($39/month)
--   Pro Yearly    (Product 800604) -> Variant 1262535 ($390/year)
--   Enterprise Monthly (Product 800600) -> Variant 1262531 ($99/month)
--   Enterprise Yearly  (Product 800589) -> Variant 1262517 ($990/year)
--
-- NOTE: These are TEST MODE products. Update with production Variant IDs for production.
-- =============================================================================

-- Based plan (plan_id = 1)
UPDATE plan_prices SET
    lemonsqueezy_variant_id_monthly = '1262536',
    lemonsqueezy_variant_id_yearly = '1262537'
WHERE plan_id = (SELECT id FROM subscription_plans WHERE name = 'based') AND currency = 'USD';

-- Pro plan (plan_id = 2)
UPDATE plan_prices SET
    lemonsqueezy_variant_id_monthly = '1262532',
    lemonsqueezy_variant_id_yearly = '1262535'
WHERE plan_id = (SELECT id FROM subscription_plans WHERE name = 'pro') AND currency = 'USD';

-- Enterprise plan (plan_id = 3)
UPDATE plan_prices SET
    lemonsqueezy_variant_id_monthly = '1262531',
    lemonsqueezy_variant_id_yearly = '1262517'
WHERE plan_id = (SELECT id FROM subscription_plans WHERE name = 'enterprise') AND currency = 'USD';

-- Verify the configuration
DO $$
BEGIN
    RAISE NOTICE 'LemonSqueezy Variant IDs configured for USD prices:';
    RAISE NOTICE '  Based: Monthly=1262536, Yearly=1262537';
    RAISE NOTICE '  Pro: Monthly=1262532, Yearly=1262535';
    RAISE NOTICE '  Enterprise: Monthly=1262531, Yearly=1262517';
END $$;
