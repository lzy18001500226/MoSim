// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_USER } from "../../helpers/env";
import { CLEANUP } from "../../helpers/test-data";

test.describe("User Profile API", () => {
  /**
   * TC-PROF-001: Get current user
   */
  test("get current user returns user info", async ({ api }) => {
    const cc = await api.connect();
    const user = await cc.user.getMe({}) as { id: string | number; email: string };
    expect(user.email).toBe(TEST_USER.email);
    expect(user.id).toBeTruthy();
  });

  test("get current user without auth returns unauthenticated", async ({ api }) => {
    const cc = api.connectWithToken("invalid-token");
    await expect(cc.user.getMe({})).rejects.toMatchObject({ status: 401 });
  });

  /**
   * TC-PROF-002: Update user name
   */
  test("update user name", async ({ api, db }) => {
    const email = "profile-e2e@test.local";
    const password = "TestPass123!";
    db.cleanup(CLEANUP.userByEmail(email));

    const publicCc = api.connectWithToken("");
    await publicCc.auth.register({
      email,
      username: "profilee2e",
      password,
      name: "Original Name",
    });

    await api.loginAs(email, password);
    const cc = await api.connect();
    const updated = await cc.user.updateMe({ name: "Updated Name E2E" }) as { name: string };
    expect(updated.name).toBe("Updated Name E2E");

    db.cleanup(CLEANUP.userByEmail(email));
  });

  /**
   * TC-PROF-003: Change password
   */
  test("change password with correct current password", async ({ api, db }) => {
    const email = "pwchange-e2e@test.local";
    const password = "TestPass123!";
    db.cleanup(CLEANUP.userByEmail(email));

    const publicCc = api.connectWithToken("");
    await publicCc.auth.register({
      email,
      username: "pwchangee2e",
      password,
      name: "PW Change User",
    });

    await api.loginAs(email, password);
    const cc = await api.connect();
    await cc.user.changePassword({
      currentPassword: password,
      newPassword: "NewPassword456!",
    });

    // Verify login with new password
    const loginRes = await publicCc.auth.login({
      email,
      password: "NewPassword456!",
    }) as { token: string };
    expect(loginRes.token).toBeTruthy();

    db.cleanup(CLEANUP.userByEmail(email));
  });

  /**
   * TC-PROF-004: Change password with wrong current password
   */
  test("change password with wrong current password fails", async ({ api }) => {
    const cc = await api.connect();
    await expect(
      cc.user.changePassword({
        currentPassword: "wrongpassword",
        newPassword: "NewPassword456!",
      })
    ).rejects.toMatchObject({ status: 401 });
  });

  /**
   * TC-PROF-005: List organizations
   */
  test("list user organizations returns org list", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.org.listMyOrgs({}) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
    expect(res.items.length).toBeGreaterThan(0);
  });
});
