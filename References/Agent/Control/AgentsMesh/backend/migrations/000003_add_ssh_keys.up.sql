-- Migration: 000003_add_ssh_keys
-- Add SSH Keys table and ssh_key_id column to git_providers

-- SSH Keys (Organization level)
CREATE TABLE IF NOT EXISTS ssh_keys (
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    name VARCHAR(100) NOT NULL,
    public_key TEXT NOT NULL,
    private_key_encrypted TEXT NOT NULL,
    fingerprint VARCHAR(255) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(organization_id, name),
    UNIQUE(organization_id, fingerprint)
);

CREATE INDEX IF NOT EXISTS idx_ssh_keys_org ON ssh_keys(organization_id);

-- Add ssh_key_id column to git_providers for SSH type providers
ALTER TABLE git_providers ADD COLUMN IF NOT EXISTS ssh_key_id BIGINT REFERENCES ssh_keys(id) ON DELETE SET NULL;

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_ssh_keys_updated_at ON ssh_keys;
CREATE TRIGGER update_ssh_keys_updated_at
    BEFORE UPDATE ON ssh_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
