-- Fix organizations that are missing subscription records.
-- This was caused by a bug where billing service was not injected into organization service,
-- so CreateTrialSubscription was silently skipped during organization creation.
INSERT INTO subscriptions (organization_id, plan_id, status, billing_cycle, current_period_start, current_period_end, seat_count, created_at, updated_at)
SELECT
    o.id,
    (SELECT id FROM subscription_plans WHERE name = 'based' LIMIT 1),
    'trialing',
    'monthly',
    NOW(),
    NOW() + INTERVAL '30 days',
    1,
    NOW(),
    NOW()
FROM organizations o
WHERE NOT EXISTS (
    SELECT 1 FROM subscriptions s WHERE s.organization_id = o.id
)
AND EXISTS (
    SELECT 1 FROM subscription_plans WHERE name = 'based'
);
