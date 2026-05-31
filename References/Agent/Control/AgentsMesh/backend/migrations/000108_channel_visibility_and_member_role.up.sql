ALTER TABLE channels ADD COLUMN visibility VARCHAR(10) NOT NULL DEFAULT 'public';
ALTER TABLE channel_members ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'member';

CREATE INDEX idx_channels_org_visibility ON channels(organization_id, visibility);
CREATE INDEX idx_channel_members_user_channels ON channel_members(user_id, channel_id);
