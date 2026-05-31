-- Migration: 000011_update_subscription_plans
-- Description: Add max_concurrent_pods field and update plan configurations for new pricing

-- Add max_concurrent_pods column
ALTER TABLE subscription_plans ADD COLUMN max_concurrent_pods INT NOT NULL DEFAULT 0;

-- Update Free plan
UPDATE subscription_plans SET
    price_per_seat_monthly = 0,
    max_users = 1,
    max_runners = 1,
    max_concurrent_pods = 2,
    max_repositories = 3,
    included_pod_minutes = 0
WHERE name = 'free';

-- Update Pro plan
UPDATE subscription_plans SET
    price_per_seat_monthly = 20,
    max_users = 5,
    max_runners = 10,
    max_concurrent_pods = 10,
    max_repositories = 10,
    included_pod_minutes = 0
WHERE name = 'pro';

-- Update Enterprise plan
UPDATE subscription_plans SET
    price_per_seat_monthly = 40,
    max_users = 50,
    max_runners = 100,
    max_concurrent_pods = 50,
    max_repositories = -1,
    included_pod_minutes = 0
WHERE name = 'enterprise';

-- Insert OnPremise plan (if not exists)
INSERT INTO subscription_plans (name, display_name, price_per_seat_monthly, max_users, max_runners, max_concurrent_pods, max_repositories, included_pod_minutes)
VALUES ('onpremise', 'OnPremise', 0, -1, -1, -1, -1, 0)
ON CONFLICT (name) DO UPDATE SET
    display_name = 'OnPremise',
    price_per_seat_monthly = 0,
    max_users = -1,
    max_runners = -1,
    max_concurrent_pods = -1,
    max_repositories = -1,
    included_pod_minutes = 0;
