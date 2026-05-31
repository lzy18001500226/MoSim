-- Rollback Payment System Migration

-- Drop tables
DROP TABLE IF EXISTS licenses CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS payment_transactions CASCADE;
DROP TABLE IF EXISTS payment_orders CASCADE;

-- Remove columns from subscription_plans
ALTER TABLE subscription_plans DROP COLUMN IF EXISTS price_per_seat_yearly;
ALTER TABLE subscription_plans DROP COLUMN IF EXISTS stripe_price_id_monthly;
ALTER TABLE subscription_plans DROP COLUMN IF EXISTS stripe_price_id_yearly;

-- Remove columns from subscriptions
ALTER TABLE subscriptions DROP COLUMN IF EXISTS payment_provider;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS payment_method;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS auto_renew;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS seat_count;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS canceled_at;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS cancel_at_period_end;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS frozen_at;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS downgrade_to_plan;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS next_billing_cycle;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS alipay_agreement_no;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS wechat_contract_id;
