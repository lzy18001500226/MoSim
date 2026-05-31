-- Migration: 000025_disable_onpremise_plan (rollback)
-- Description: Re-enable onpremise plan

UPDATE subscription_plans SET is_active = true WHERE name = 'onpremise';
