-- Migration: Restore Team concept (rollback)
-- WARNING: This will restore the table structure but NOT the data

-- Step 1: Recreate teams table
CREATE TABLE teams (
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id, name)
);

CREATE INDEX idx_teams_organization ON teams(organization_id);

-- Step 2: Recreate team_members table
CREATE TABLE team_members (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);

-- Step 3: Add team_id column back to resource tables
ALTER TABLE repositories ADD COLUMN team_id BIGINT REFERENCES teams(id) ON DELETE SET NULL;
ALTER TABLE pods ADD COLUMN team_id BIGINT REFERENCES teams(id) ON DELETE SET NULL;
ALTER TABLE channels ADD COLUMN team_id BIGINT REFERENCES teams(id) ON DELETE SET NULL;
ALTER TABLE tickets ADD COLUMN team_id BIGINT REFERENCES teams(id) ON DELETE SET NULL;

CREATE INDEX idx_repositories_team ON repositories(team_id);
CREATE INDEX idx_pods_team ON pods(team_id);
CREATE INDEX idx_channels_team ON channels(team_id);
CREATE INDEX idx_tickets_team ON tickets(team_id);

-- Step 4: Recreate trigger
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
