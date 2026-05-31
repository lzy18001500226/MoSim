-- Add reserved-word constraint to organizations.slug and loops.slug.
--
-- This complements the format CHECK from 000113 by guarding against
-- application-layer bypass: even if pkg/slugkit.IsReserved is skipped or
-- buggy, the DB rejects reserved values on write.
--
-- Reserved list MUST stay in sync with backend/pkg/slugkit/reserved.go and
-- web/src/lib/slug/reserved.ts. The Go test TestReservedListSyncAcrossSources
-- catches drift between Go, TS, and this file. The test auto-discovers the
-- latest *slug_reserved* migration via filepath.Glob.
--
-- NOT VALID skips checking existing rows (defense-in-depth, not retroactive).

ALTER TABLE organizations
  ADD CONSTRAINT organizations_slug_not_reserved
  CHECK (slug NOT IN (
    'about', 'admin', 'agents', 'api', 'app', 'auth',
    'billing', 'blog', 'careers', 'changelog', 'dashboard',
    'demo', 'docs', 'enterprise', 'false', 'forgot-password',
    'invite', 'login', 'logout', 'me', 'mock-checkout',
    'new', 'null', 'offline', 'onboarding', 'organizations',
    'orgs', 'personal', 'popout', 'privacy', 'register',
    'reset-password', 'runners', 'settings', 'support', 'terms',
    'true', 'undefined', 'verify-email', 'www'
  ))
  NOT VALID;

ALTER TABLE loops
  ADD CONSTRAINT loops_slug_not_reserved
  CHECK (slug NOT IN (
    'about', 'admin', 'agents', 'api', 'app', 'auth',
    'billing', 'blog', 'careers', 'changelog', 'dashboard',
    'demo', 'docs', 'enterprise', 'false', 'forgot-password',
    'invite', 'login', 'logout', 'me', 'mock-checkout',
    'new', 'null', 'offline', 'onboarding', 'organizations',
    'orgs', 'personal', 'popout', 'privacy', 'register',
    'reset-password', 'runners', 'settings', 'support', 'terms',
    'true', 'undefined', 'verify-email', 'www'
  ))
  NOT VALID;
