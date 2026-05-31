-- Add LemonSqueezy support for subscriptions and plan prices
-- LemonSqueezy is the primary payment provider for US/Global users

-- Add LemonSqueezy fields to subscriptions table
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS lemonsqueezy_customer_id VARCHAR(255);
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS lemonsqueezy_subscription_id VARCHAR(255);

-- Add LemonSqueezy Variant ID fields to plan_prices table
-- In LemonSqueezy, each price point is a "Variant" of a Product
ALTER TABLE plan_prices ADD COLUMN IF NOT EXISTS lemonsqueezy_variant_id_monthly VARCHAR(255);
ALTER TABLE plan_prices ADD COLUMN IF NOT EXISTS lemonsqueezy_variant_id_yearly VARCHAR(255);

-- Create index for finding subscriptions by LemonSqueezy subscription ID
CREATE INDEX IF NOT EXISTS idx_subscriptions_lemonsqueezy_subscription
ON subscriptions(lemonsqueezy_subscription_id)
WHERE lemonsqueezy_subscription_id IS NOT NULL;

-- Create index for finding subscriptions by LemonSqueezy customer ID
CREATE INDEX IF NOT EXISTS idx_subscriptions_lemonsqueezy_customer
ON subscriptions(lemonsqueezy_customer_id)
WHERE lemonsqueezy_customer_id IS NOT NULL;

-- Add comments for documentation
COMMENT ON COLUMN subscriptions.lemonsqueezy_customer_id IS 'LemonSqueezy customer ID';
COMMENT ON COLUMN subscriptions.lemonsqueezy_subscription_id IS 'LemonSqueezy subscription ID';
COMMENT ON COLUMN plan_prices.lemonsqueezy_variant_id_monthly IS 'LemonSqueezy Variant ID for monthly billing';
COMMENT ON COLUMN plan_prices.lemonsqueezy_variant_id_yearly IS 'LemonSqueezy Variant ID for yearly billing';

-- NOTE: LemonSqueezy Variant IDs must be configured manually after setting up products in your
-- LemonSqueezy dashboard. Each product variant maps to a specific plan and billing cycle.
-- Example configuration (update with your actual Variant IDs from LemonSqueezy):
--
-- UPDATE plan_prices SET
--     lemonsqueezy_variant_id_monthly = 'YOUR_BASED_MONTHLY_VARIANT_ID',
--     lemonsqueezy_variant_id_yearly = 'YOUR_BASED_YEARLY_VARIANT_ID'
-- WHERE plan_id = (SELECT id FROM subscription_plans WHERE name = 'based') AND currency = 'USD';
--
-- UPDATE plan_prices SET
--     lemonsqueezy_variant_id_monthly = 'YOUR_PRO_MONTHLY_VARIANT_ID',
--     lemonsqueezy_variant_id_yearly = 'YOUR_PRO_YEARLY_VARIANT_ID'
-- WHERE plan_id = (SELECT id FROM subscription_plans WHERE name = 'pro') AND currency = 'USD';
--
-- UPDATE plan_prices SET
--     lemonsqueezy_variant_id_monthly = 'YOUR_ENTERPRISE_MONTHLY_VARIANT_ID',
--     lemonsqueezy_variant_id_yearly = 'YOUR_ENTERPRISE_YEARLY_VARIANT_ID'
-- WHERE plan_id = (SELECT id FROM subscription_plans WHERE name = 'enterprise') AND currency = 'USD';
