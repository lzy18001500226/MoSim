-- Migration: Remove Team concept from the system
-- This simplifies the architecture to User + Organization two-layer model
-- All resources are now directly owned by Organization

-- Step 1: Drop indexes on team_id columns
DROP INDEX IF EXISTS idx_repositories_team;
DROP INDEX IF EXISTS idx_pods_team;
DROP INDEX IF EXISTS idx_channels_team;
DROP INDEX IF EXISTS idx_tickets_team;

-- Step 2: Remove team_id column from resource tables
ALTER TABLE repositories DROP COLUMN IF EXISTS team_id;
ALTER TABLE pods DROP COLUMN IF EXISTS team_id;
ALTER TABLE channels DROP COLUMN IF EXISTS team_id;
ALTER TABLE tickets DROP COLUMN IF EXISTS team_id;

-- Step 3: Drop triggers related to teams
DROP TRIGGER IF EXISTS update_teams_updated_at ON teams;

-- Step 4: Drop team-related indexes
DROP INDEX IF EXISTS idx_team_members_team;
DROP INDEX IF EXISTS idx_team_members_user;
DROP INDEX IF EXISTS idx_teams_organization;

-- Step 5: Drop team_members table (must be dropped before teams due to FK)
DROP TABLE IF EXISTS team_members;

-- Step 6: Drop teams table
DROP TABLE IF EXISTS teams;
