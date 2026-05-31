-- Rollback multi-currency pricing support

-- Drop plan_prices table
DROP TABLE IF EXISTS plan_prices;

-- Restore Free plan from Based
UPDATE subscription_plans SET
    name = 'free',
    display_name = 'Free',
    price_per_seat_monthly = 0,
    price_per_seat_yearly = 0,
    max_users = 1,
    max_runners = 1,
    max_concurrent_pods = 2,
    max_repositories = 3
WHERE name = 'based';

-- Restore Pro plan pricing
UPDATE subscription_plans SET
    price_per_seat_monthly = 20,
    price_per_seat_yearly = 200
WHERE name = 'pro';

-- Restore Enterprise plan pricing
UPDATE subscription_plans SET
    price_per_seat_monthly = 40,
    price_per_seat_yearly = 400
WHERE name = 'enterprise';

-- Drop index
DROP INDEX IF EXISTS idx_subscriptions_period_end;
