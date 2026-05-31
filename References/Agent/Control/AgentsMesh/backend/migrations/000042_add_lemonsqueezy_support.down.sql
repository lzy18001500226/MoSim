-- Rollback LemonSqueezy support

-- Remove indexes
DROP INDEX IF EXISTS idx_subscriptions_lemonsqueezy_subscription;
DROP INDEX IF EXISTS idx_subscriptions_lemonsqueezy_customer;

-- Remove LemonSqueezy fields from plan_prices table
ALTER TABLE plan_prices DROP COLUMN IF EXISTS lemonsqueezy_variant_id_monthly;
ALTER TABLE plan_prices DROP COLUMN IF EXISTS lemonsqueezy_variant_id_yearly;

-- Remove LemonSqueezy fields from subscriptions table
ALTER TABLE subscriptions DROP COLUMN IF EXISTS lemonsqueezy_customer_id;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS lemonsqueezy_subscription_id;
