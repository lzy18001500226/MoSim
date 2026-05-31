import { test, expect } from "../../fixtures/index";
import { clearAuthRateLimit } from "../../helpers/redis";
import { CLEANUP } from "../../helpers/test-data";
import { TEST_ORG_SLUG } from "../../helpers/env";

/**
 * CRUD supplement tests — filling gaps in existing modules.
 */
test.describe("CRUD Supplements", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * EnvBundle update via Connect EnvBundleService. Replaces the legacy
   * /users/agent-credentials/profiles/:id endpoint.
   */
  test("update env bundle name", async ({ api, db }) => {
    // env_bundles has UNIQUE(owner_scope, owner_id, name); a residue from a
    // prior failed run would make POST return ALREADY_EXISTS and silently
    // skip. Pre-clean.
    db.cleanup(
      `DELETE FROM env_bundles WHERE name IN ('E2E Update Bundle', 'E2E Updated Bundle')`
    );
    const cc = await api.connect();
    const created = await cc.envBundle.createEnvBundle({
      agentSlug: "claude-code",
      name: "E2E Update Bundle",
      kind: "credential",
      data: { ANTHROPIC_API_KEY: "sk-test" },
    }) as { id: bigint };
    expect(created.id, "env-bundle create response must include an id").toBeTruthy();

    await cc.envBundle.updateEnvBundle({ id: created.id, name: "E2E Updated Bundle" });

    db.cleanup(
      `DELETE FROM env_bundles WHERE name IN ('E2E Update Bundle', 'E2E Updated Bundle')`
    );
  });

  /**
   * Promote a bundle to primary within its (agent, kind) group.
   */
  test("set env bundle as primary", async ({ api, db }) => {
    db.cleanup(`DELETE FROM env_bundles WHERE name = 'E2E Primary Bundle'`);
    const cc = await api.connect();
    const created = await cc.envBundle.createEnvBundle({
      agentSlug: "claude-code",
      name: "E2E Primary Bundle",
      kind: "credential",
      data: { ANTHROPIC_API_KEY: "sk-test" },
    }) as { id: bigint };
    expect(created.id, "env-bundle create response must include an id").toBeTruthy();

    await cc.envBundle.setPrimaryEnvBundle({ id: created.id });
    const after = await cc.envBundle.getEnvBundle({ id: created.id }) as { kindPrimary: boolean };
    expect(after.kindPrimary).toBe(true);

    db.cleanup(`DELETE FROM env_bundles WHERE name = 'E2E Primary Bundle'`);
  });

  /**
   * TC-MEMBER-005: Change member role
   */
  test("change organization member role", async ({ api, db }) => {
    const email = "role-change-e2e@test.local";
    try { db.cleanup(CLEANUP.userByEmail(email)); } catch { /* */ }

    // REST /api/v1/auth/register is dead; use Connect AuthService/Register.
    const cc = await api.connect();
    await cc.auth.register({
      email, username: "rolechangee2e", password: "TestPass123!", name: "Role Change",
    });

    const orgId = db.queryValue(
      `SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}'`
    );
    const userId = db.queryValue(`SELECT id FROM users WHERE email = '${email}'`);
    expect(orgId, "dev seed must have the test org").toBeTruthy();
    expect(userId, "registered user must exist in users table").toBeTruthy();

    db.setup(
      `INSERT INTO organization_members (organization_id, user_id, role) VALUES (${orgId}, ${userId}, 'member') ON CONFLICT DO NOTHING`
    );

    await cc.org.updateMemberRole({
      orgSlug: TEST_ORG_SLUG,
      userId: BigInt(userId as string),
      role: "admin",
    });

    db.cleanup(CLEANUP.userByEmail(email));
  });

  /**
   * TC-REPOPROV-005: Set default repository provider
   */
  test("set repository provider as default", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: "E2E Default Provider " + Date.now(),
      baseUrl: "https://api.github.com",
      botToken: "ghp_default_test",
    }) as { id: number };
    expect(created.id, "create must return a provider id").toBeTruthy();

    await cc.userRepositoryProvider.setDefaultRepositoryProvider({ id: created.id });

    await cc.userRepositoryProvider.deleteRepositoryProvider({ id: created.id });
  });

  /**
   * TC-MEMBER-007: Accept invitation (API)
   */
  test("accept organization invitation via API", async ({ api, db }) => {
    const email = "invite-accept-e2e@test.local";
    try { db.cleanup(CLEANUP.userByEmail(email)); } catch { /* */ }
    try { db.cleanup(`DELETE FROM invitations WHERE email = '${email}'`); } catch { /* */ }

    // Register invitee via Connect (REST /api/v1/auth/register is dead).
    const adminClient = await api.connect();
    await adminClient.auth.register({
      email, username: "inviteaccepte2e", password: "TestPass123!", name: "Invite Accept",
    });

    // Create invitation via Connect InvitationService/CreateInvitation.
    const inv = await adminClient.invitation.createInvitation({
      orgSlug: TEST_ORG_SLUG, email, role: "member",
    }) as { id: bigint };
    expect(inv.id, "create invitation must succeed").toBeTruthy();

    const token = db.queryValue(
      `SELECT token FROM invitations WHERE email = '${email}' AND accepted_at IS NULL LIMIT 1`
    );
    expect(token, "invitation must have been persisted with a token").toBeTruthy();

    // Accept as invitee via UserInvitationService/AcceptInvitation.
    const inviteeToken = await api.loginAs(email, "TestPass123!");
    const inviteeClient = api.connectWithToken(inviteeToken);
    await inviteeClient.userInvitation.acceptInvitation({ token: String(token) });

    try { db.cleanup(`DELETE FROM invitations WHERE email = '${email}'`); } catch { /* */ }
    try { db.cleanup(CLEANUP.userByEmail(email)); } catch { /* */ }
  });

  /**
   * TC-POD-002: Create pod with repository
   */
  test("create pod with repository association", async ({ api }) => {
    const cc = await api.connect();
    const { items: runners } = await cc.runner.listAvailableRunners({
      orgSlug: TEST_ORG_SLUG,
    }) as { items: { id: bigint }[] };
    expect(runners.length, "dev env must have an online runner").toBeGreaterThan(0);

    const { builtinAgents: agents } = await cc.agent.listAgents({
      orgSlug: TEST_ORG_SLUG,
    }) as { builtinAgents: { slug: string }[] };
    expect(agents.length, "dev env must have a builtin agent").toBeGreaterThan(0);

    const { items: repos } = await cc.repository.listRepositories({
      orgSlug: TEST_ORG_SLUG,
    }) as { items: { id: bigint }[] };

    const req: Record<string, unknown> = {
      orgSlug: TEST_ORG_SLUG,
      runnerId: runners[0].id,
      agentSlug: agents[0].slug,
    };
    if (repos?.length) {
      req.repositoryId = repos[0].id;
    }

    const created = await cc.pod.createPod(req) as { pod: { podKey: string } };
    const podKey = created.pod?.podKey;
    expect(podKey).toBeTruthy();

    if (podKey) {
      await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey });
    }
  });
});
