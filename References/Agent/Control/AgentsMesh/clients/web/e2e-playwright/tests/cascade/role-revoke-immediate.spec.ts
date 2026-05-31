// Cascade test (P0): revoking a member's admin role MUST immediately deny
// admin-only operations on the next call — no token re-issue, no session
// refresh, no cache-bust grace period. The auth interceptor reads role from
// the tenant context every request; if a stale-role bug were to creep in
// (e.g. caching role in a Rust core service / JWT claim that wasn't
// re-validated), this spec catches it.
//
// Sequence:
//   1. Register a fresh user X
//   2. dev (owner of dev-org) adds X as admin via InviteMember (direct add
//      since email→user lookup hits an existing account; the org-scoped
//      InviteMember in proto.org.v1 is the AddMember handler, not the
//      pending-invitation flow — that one is invitation.v1)
//   3. X logs in, confirms admin-only `inviteMember` works
//   4. dev demotes X to member via `updateMemberRole`
//   5. X immediately retries `inviteMember` → MUST fail with permission_denied
//
// Two assertions:
//   * Permission boundary is correct (member can't invite)
//   * Boundary takes effect on the very next request, not stale until re-login
import { test, expect } from "../../fixtures/index";
import { TEST_USER, TEST_ORG_SLUG } from "../../helpers/env";
import { uniqueEmail, CLEANUP } from "../../helpers/test-data";

test.describe("Cascade: org role revoke → admin ops denied immediately", () => {
  test("admin → member demotion blocks the very next inviteMember call", async ({ api, db }) => {
    const targetEmail = uniqueEmail("role-revoke");
    const targetPassword = "RoleRevokeTest123!";
    const probe1Email = uniqueEmail("probe1");
    const probe2Email = uniqueEmail("probe2");
    const probe1Password = "ProbePass123!";
    const probe2Password = "ProbePass123!";

    db.cleanup(CLEANUP.userByEmail(targetEmail));
    db.cleanup(CLEANUP.userByEmail(probe1Email));
    db.cleanup(CLEANUP.userByEmail(probe2Email));

    const publicCc = api.connectWithToken("");

    // Register the user that will be promoted-then-demoted.
    await publicCc.auth.register({
      email: targetEmail,
      username: `rolerev${Date.now()}`.slice(0, 18),
      password: targetPassword,
      name: "Role Revoke Target",
    });

    // Register two probe users; X will try to invite probe1 (as admin: should
    // succeed) and probe2 (after demotion: should fail). Pre-registering them
    // means the email→user lookup in InviteMember resolves; otherwise the
    // handler returns CodeNotFound and we can't distinguish that from
    // PermissionDenied.
    await publicCc.auth.register({
      email: probe1Email,
      username: `probe1${Date.now()}`.slice(0, 18),
      password: probe1Password,
      name: "Probe 1",
    });
    await publicCc.auth.register({
      email: probe2Email,
      username: `probe2${Date.now()}`.slice(0, 18),
      password: probe2Password,
      name: "Probe 2",
    });

    // dev owns dev-org — use it to drive the role-change flow.
    await api.login(TEST_USER.email, TEST_USER.password);
    const ownerCc = await api.connect();

    // Owner adds X as admin. InviteMember on org service is the AddMember
    // handler (proto.org.v1.OrgService.InviteMember) — when the email
    // resolves to an existing user it skips the pending-invitation token
    // flow and directly inserts an organization_members row.
    await ownerCc.org.inviteMember({
      orgSlug: TEST_ORG_SLUG,
      email: targetEmail,
      role: "admin",
    });

    // Sanity: X is now an admin member.
    const xUserId = db.queryValue(
      `SELECT id FROM users WHERE email = '${targetEmail}' LIMIT 1`,
    );
    expect(xUserId, "X must exist in users table").toBeTruthy();
    const xRole = db.queryValue(
      `SELECT role FROM organization_members WHERE user_id = ${xUserId} AND organization_id IN (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}')`,
    );
    expect(xRole).toBe("admin");

    // X logs in and confirms the admin grant lets them invite another user.
    const targetToken = await api.loginAs(targetEmail, targetPassword);
    const targetCc = api.connectWithToken(targetToken);
    await targetCc.org.inviteMember({
      orgSlug: TEST_ORG_SLUG,
      email: probe1Email,
      role: "member",
    });

    // Owner demotes X to member. Same token X is holding; no re-login here.
    await ownerCc.org.updateMemberRole({
      orgSlug: TEST_ORG_SLUG,
      userId: BigInt(String(xUserId)),
      role: "member",
    });

    // Cascade assertion: X's *next* inviteMember call MUST be denied. If this
    // passes, the server reads role fresh on every request (correct). If a
    // future change cached the role in the JWT or a Rust selector without
    // invalidation, this assertion turns red.
    let postDemotionDenied = false;
    let postDemotionDetail: unknown = null;
    try {
      await targetCc.org.inviteMember({
        orgSlug: TEST_ORG_SLUG,
        email: probe2Email,
        role: "member",
      });
    } catch (err) {
      postDemotionDetail = err;
      const code = (err as { code?: string }).code ?? "";
      const status = (err as { status?: number }).status;
      const message = String((err as { message?: string }).message ?? "");
      if (
        code === "permission_denied" ||
        status === 403 ||
        message.toLowerCase().includes("admin")
      ) {
        postDemotionDenied = true;
      }
    }
    expect(
      postDemotionDenied,
      `inviteMember must be denied immediately after role demotion; got: ${JSON.stringify(postDemotionDetail)}`,
    ).toBe(true);

    db.cleanup(CLEANUP.userByEmail(targetEmail));
    db.cleanup(CLEANUP.userByEmail(probe1Email));
    db.cleanup(CLEANUP.userByEmail(probe2Email));
  });
});
