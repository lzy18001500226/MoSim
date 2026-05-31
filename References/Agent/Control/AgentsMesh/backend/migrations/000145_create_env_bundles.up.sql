-- Migration 000134: Introduce env_bundles as the unified storage for credential
-- profiles AND future runtime/shared bundles. Existing user_agent_credential_profiles
-- rows are copied into env_bundles with kind='credential'. The legacy table is
-- preserved during the transition window so REST handlers can dual-read; it gets
-- dropped by migration 000135 once all callers are switched.
--
-- NOTE: Migration number 000136 was squashed into this file before any release;
-- the sequence intentionally jumps to 000137. The original 000136 added a
-- `pods.used_env_bundles` column that turned out to be unused — folding the
-- deletion in here keeps fresh deployments from creating-then-dropping the
-- column. golang-migrate tolerates non-contiguous serial numbers.

CREATE TABLE env_bundles (
    id BIGSERIAL PRIMARY KEY,
    owner_scope VARCHAR(16) NOT NULL,
    owner_id BIGINT NOT NULL,
    agent_slug VARCHAR(100),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    kind VARCHAR(32) NOT NULL,
    kind_primary BOOLEAN NOT NULL DEFAULT FALSE,
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (owner_scope, owner_id, name)
);

CREATE INDEX env_bundles_owner_kind ON env_bundles (owner_scope, owner_id, kind);
CREATE INDEX env_bundles_owner_agent ON env_bundles (owner_scope, owner_id, agent_slug);
CREATE INDEX env_bundles_kind ON env_bundles (kind);

-- At most one primary per (owner, agent_slug, kind). NULL agent_slug counts as
-- its own group thanks to the partial-index semantics.
CREATE UNIQUE INDEX env_bundles_primary_per_kind
    ON env_bundles (owner_scope, owner_id, agent_slug, kind)
    WHERE kind_primary = TRUE;

CREATE TRIGGER update_env_bundles_updated_at
    BEFORE UPDATE ON env_bundles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE env_bundles IS 'Named, owner-scoped sets of environment variables referenced from AgentFile via USE_ENV_BUNDLE. credential-kind values are encrypted at the service layer; other kinds are plaintext.';
COMMENT ON COLUMN env_bundles.kind IS 'String, code-layer defined (no enum constraint): credential / runtime / shared / etc.';
COMMENT ON COLUMN env_bundles.kind_primary IS 'True for the user''s default bundle in this (owner, agent_slug, kind) group. UI hint only — backend does NOT auto-mount based on this flag; AgentFile USE_ENV_BUNDLE controls injection.';

-- ============================================================================
-- One-shot copy: user_agent_credential_profiles → env_bundles
-- ============================================================================
INSERT INTO env_bundles (
    owner_scope, owner_id, agent_slug, name, description,
    kind, kind_primary, data, is_active, created_at, updated_at
)
SELECT
    'user',
    user_id,
    agent_slug,
    name,
    description,
    'credential',
    is_default,
    COALESCE(credentials_encrypted, '{}'::jsonb),
    is_active,
    created_at,
    updated_at
FROM user_agent_credential_profiles;
