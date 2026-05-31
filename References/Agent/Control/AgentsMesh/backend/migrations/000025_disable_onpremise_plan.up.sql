-- Migration: 000025_disable_onpremise_plan
-- Description: Disable onpremise plan for SAAS deployment (it's only for private deployment)

UPDATE subscription_plans SET is_active = false WHERE name = 'onpremise';
