// Migrated R6+: Connect-RPC for user/credentials/providers/env-bundles.
// Mirror tests/account/git-credentials.spec.ts + repo-providers.api.spec.ts +
// profile.api.spec.ts conventions: typed clients, optional id-from-existing-row
// fallback, no REST when a Connect method exists.
import { test, expect } from "../../fixtures/index";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("User Credential Management API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list git credentials", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.userGitCredential.listGitCredentials({}) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("get default git credential", async ({ api }) => {
    const cc = await api.connect();
    // Connect throws non-2xx; success-only is the assertion here.
    await cc.userGitCredential.getDefaultGitCredential({});
  });

  test("list repository providers", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.userRepositoryProvider.listRepositoryProviders({}) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list env bundles", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.envBundle.listEnvBundles({}) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("get user profile", async ({ api }) => {
    const cc = await api.connect();
    const user = await cc.user.getMe({}) as { id: string | number; email: string };
    expect(user.id).toBeTruthy();
    expect(user.email).toBeTruthy();
  });

  test("create and delete git credential", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.userGitCredential.createGitCredential({
      name: "E2E PAT Credential " + Date.now(),
      credentialType: "pat",
      pat: "ghp_test123456789",
    }) as { id: number };
    expect(created.id).toBeTruthy();
    await cc.userGitCredential.deleteGitCredential({ id: created.id });
  });

  test("test repository provider connection", async ({ api, db }) => {
    const cc = await api.connect();
    // Seed a provider if none exists so the test never silently skips.
    let id = db.queryValue("SELECT id FROM user_repository_providers LIMIT 1");
    let createdId: number | null = null;
    if (!id) {
      const created = await cc.userRepositoryProvider.createRepositoryProvider({
        providerType: "github",
        name: "E2E Connection Seed " + Date.now(),
        baseUrl: "https://api.github.com",
        botToken: "ghp_seed_for_connection_test",
      }) as { id: number };
      createdId = created.id;
      id = String(createdId);
    }
    // Tolerates success or failure due to potentially invalid stored token.
    await cc.userRepositoryProvider
      .testRepositoryProviderConnection({ id: Number(id) })
      .catch((e) => e);
    if (createdId) {
      await cc.userRepositoryProvider.deleteRepositoryProvider({ id: createdId });
    }
  });
});
