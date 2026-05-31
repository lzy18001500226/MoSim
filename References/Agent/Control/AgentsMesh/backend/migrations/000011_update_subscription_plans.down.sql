-- Migration: 000011_update_subscription_plans (rollback)
-- Description: Revert max_concurrent_pods field and plan configurations

-- Delete OnPremise plan
DELETE FROM subscription_plans WHERE name = 'onpremise';

-- Restore original Free plan
UPDATE subscription_plans SET
    price_per_seat_monthly = 0,
    max_users = 3,
    max_runners = 1,
    max_repositories = 3,
    included_pod_minutes = 100
WHERE name = 'free';

-- Restore original Pro plan
UPDATE subscription_plans SET
    price_per_seat_monthly = 0,
    max_users = 10,
    max_runners = 5,
    max_repositories = 20,
    included_pod_minutes = 1000
WHERE name = 'pro';

-- Restore original Enterprise plan
UPDATE subscription_plans SET
    price_per_seat_monthly = 0,
    max_users = -1,
    max_runners = -1,
    max_repositories = -1,
    included_pod_minutes = -1
WHERE name = 'enterprise';

-- Remove max_concurrent_pods column
ALTER TABLE subscription_plans DROP COLUMN max_concurrent_pods;
