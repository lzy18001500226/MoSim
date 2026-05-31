-- Migration: 000013_add_promo_codes.down.sql
-- Description: Rollback promo codes tables

DROP TRIGGER IF EXISTS update_promo_codes_updated_at ON promo_codes;
DROP INDEX IF EXISTS idx_promo_redemptions_org_code_unique;
DROP INDEX IF EXISTS idx_promo_redemptions_created_at;
DROP INDEX IF EXISTS idx_promo_redemptions_user_id;
DROP INDEX IF EXISTS idx_promo_redemptions_org_id;
DROP INDEX IF EXISTS idx_promo_redemptions_code_id;
DROP TABLE IF EXISTS promo_code_redemptions;
DROP INDEX IF EXISTS idx_promo_codes_is_active;
DROP INDEX IF EXISTS idx_promo_codes_plan_name;
DROP INDEX IF EXISTS idx_promo_codes_type;
DROP INDEX IF EXISTS idx_promo_codes_code;
DROP TABLE IF EXISTS promo_codes;
