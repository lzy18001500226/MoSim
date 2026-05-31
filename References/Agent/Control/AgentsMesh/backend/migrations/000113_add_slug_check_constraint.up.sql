-- Add CHECK constraints enforcing slug format at the database layer.
--
-- IMPORTANT: Uses NOT VALID to skip validation of existing rows.
-- Historical slugs that violated the new pattern (e.g. containing consecutive
-- hyphens "foo--bar" allowed by the prior regex, or single-character slugs)
-- are preserved as-is. Only NEW inserts and updates are checked.
--
-- This guarantees:
--   1. Production data is never broken by this migration.
--   2. Application reads/queries on legacy slugs continue to work.
--   3. New writes from any code path (including future SQL or migrations)
--      cannot bypass the new format rule.
--
-- Rule (matches backend/pkg/slug/rules.go pattern):
--   ^[a-z0-9]+(-[a-z0-9]+)*$ AND length BETWEEN 2 AND 100
--
-- Repositories are intentionally excluded — their slug uses 'org/repo' format.
--
-- After deployment, audit legacy violators with:
--   SELECT id, slug FROM organizations
--   WHERE slug !~ '^[a-z0-9]+(-[a-z0-9]+)*$' OR length(slug) NOT BETWEEN 2 AND 100;
--   SELECT id, slug FROM loops
--   WHERE slug !~ '^[a-z0-9]+(-[a-z0-9]+)*$' OR length(slug) NOT BETWEEN 2 AND 100;
--
-- A future cleanup migration may rename violators and then run:
--   ALTER TABLE organizations VALIDATE CONSTRAINT organizations_slug_format;
--   ALTER TABLE loops VALIDATE CONSTRAINT loops_slug_format;

ALTER TABLE organizations
  ADD CONSTRAINT organizations_slug_format
  CHECK (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$' AND length(slug) BETWEEN 2 AND 100)
  NOT VALID;

ALTER TABLE loops
  ADD CONSTRAINT loops_slug_format
  CHECK (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$' AND length(slug) BETWEEN 2 AND 100)
  NOT VALID;
