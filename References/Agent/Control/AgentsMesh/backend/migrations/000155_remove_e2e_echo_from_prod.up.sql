-- 000155_remove_e2e_echo_from_prod.up.sql
-- One-shot removal of the e2e-echo test fixture that the legacy
-- 000127/000150-154 migrations leaked into every environment, including
-- production. Going forward the agent is seeded via
-- deploy/dev/seed/e2e_echo.sql in dev/e2e only — production DBs never
-- receive test fixtures through the migration channel.
--
-- Why also delete dependent rows: pods.agent_slug FKs into agents.slug
-- (via supported_modes / agentfile resolution). On a clean prod DB no
-- pod will reference 'e2e-echo' since real users never create one; the
-- DELETE on pods is defensive in case a staging or shared-DB environment
-- has stray test runs leaked into it.
--
-- See: .claude/adr/2026-05-26-test-fixture-isolation.md
BEGIN;

DELETE FROM pods WHERE agent_slug = 'e2e-echo';
DELETE FROM agents WHERE slug = 'e2e-echo';

COMMIT;
