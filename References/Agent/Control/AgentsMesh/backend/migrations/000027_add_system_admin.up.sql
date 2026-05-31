-- Add system admin flag to users table
ALTER TABLE users ADD COLUMN is_system_admin BOOLEAN NOT NULL DEFAULT false;

-- Create index for quick admin lookup
CREATE INDEX idx_users_is_system_admin ON users(is_system_admin) WHERE is_system_admin = true;

-- Create system admin audit logs table
CREATE TABLE system_admin_audit_logs (
    id BIGSERIAL PRIMARY KEY,
    admin_user_id BIGINT NOT NULL REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id BIGINT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX idx_admin_audit_admin_user ON system_admin_audit_logs(admin_user_id);
CREATE INDEX idx_admin_audit_target ON system_admin_audit_logs(target_type, target_id);
CREATE INDEX idx_admin_audit_created ON system_admin_audit_logs(created_at);
CREATE INDEX idx_admin_audit_action ON system_admin_audit_logs(action);

-- Add comment for documentation
COMMENT ON TABLE system_admin_audit_logs IS 'Audit log for all system administrator actions';
COMMENT ON COLUMN users.is_system_admin IS 'Whether the user is a system administrator with full platform access';
