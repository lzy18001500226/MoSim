DROP INDEX IF EXISTS idx_channel_members_user_channels;
DROP INDEX IF EXISTS idx_channels_org_visibility;
ALTER TABLE channel_members DROP COLUMN IF EXISTS role;
ALTER TABLE channels DROP COLUMN IF EXISTS visibility;
