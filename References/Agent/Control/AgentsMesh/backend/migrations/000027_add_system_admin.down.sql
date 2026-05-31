-- Drop system admin audit logs table
DROP TABLE IF EXISTS system_admin_audit_logs;

-- Drop index
DROP INDEX IF EXISTS idx_users_is_system_admin;

-- Remove system admin flag from users table
ALTER TABLE users DROP COLUMN IF EXISTS is_system_admin;
