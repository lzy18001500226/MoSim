// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Git Credentials API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-GITCRED-001: List git credentials
   */
  test("list git credentials", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.userGitCredential.listGitCredentials({}) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list git credentials without auth returns unauthenticated", async ({ api }) => {
    const cc = api.connectWithToken("bad");
    await expect(
      cc.userGitCredential.listGitCredentials({})
    ).rejects.toMatchObject({ status: 401 });
  });

  /**
   * TC-GITCRED-002: Create PAT credential
   */
  test("create PAT credential", async ({ api, db }) => {
    db.cleanup(`DELETE FROM user_git_credentials WHERE name = 'E2E Test PAT'`);
    const cc = await api.connect();
    const created = await cc.userGitCredential.createGitCredential({
      name: "E2E Test PAT",
      credentialType: "pat",
      pat: "ghp_test_token_12345",
      hostPattern: "github.com",
    }) as { id: number };
    expect(created.id).toBeTruthy();

    db.cleanup(`DELETE FROM user_git_credentials WHERE name = 'E2E Test PAT'`);
  });

  /**
   * TC-GITCRED-003: Update git credential
   */
  test("update git credential name", async ({ api, db }) => {
    // Drop any leftover from a previous failed run — the table has
    // UNIQUE(user_id, name), so a stray row would make POST return
    // ALREADY_EXISTS and the test would skip silently forever.
    db.cleanup(
      `DELETE FROM user_git_credentials WHERE name IN ('E2E Update Target', 'E2E Updated Name')`
    );
    const cc = await api.connect();
    const created = await cc.userGitCredential.createGitCredential({
      name: "E2E Update Target",
      credentialType: "pat",
      pat: "ghp_update_test",
      hostPattern: "github.com",
    }) as { id: number };
    expect(created.id, "create must return a credential id").toBeTruthy();

    const updated = await cc.userGitCredential.updateGitCredential({
      id: created.id,
      name: "E2E Updated Name",
    }) as { name: string };
    expect(updated.name).toBe("E2E Updated Name");

    db.cleanup(`DELETE FROM user_git_credentials WHERE name = 'E2E Updated Name'`);
  });

  /**
   * TC-GITCRED-004: Delete git credential
   */
  test("delete git credential", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.userGitCredential.createGitCredential({
      name: "E2E Delete Target " + Date.now(),
      credentialType: "pat",
      pat: "ghp_delete_test",
      hostPattern: "github.com",
    }) as { id: number };
    expect(created.id, "create must return a credential id").toBeTruthy();

    await cc.userGitCredential.deleteGitCredential({ id: created.id });
  });

  /**
   * TC-GITCRED-005: Set default credential
   */
  test("set and get default credential", async ({ api, db }) => {
    db.cleanup(
      `DELETE FROM user_git_credentials WHERE name = 'E2E Default Target'`
    );
    const cc = await api.connect();
    const created = await cc.userGitCredential.createGitCredential({
      name: "E2E Default Target",
      credentialType: "pat",
      pat: "ghp_default_test",
      hostPattern: "github.com",
    }) as { id: number };
    expect(created.id, "create must return a credential id").toBeTruthy();

    // Set default
    await cc.userGitCredential.setDefaultGitCredential({ credentialId: created.id });

    // Get default
    const dflt = await cc.userGitCredential.getDefaultGitCredential({}) as Record<string, unknown>;
    expect(dflt).toBeTruthy();

    // Clear and cleanup
    await cc.userGitCredential.clearDefaultGitCredential({});
    db.cleanup(`DELETE FROM user_git_credentials WHERE name = 'E2E Default Target'`);
  });
});
