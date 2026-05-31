// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

/**
 * Runner registration token tests.
 * The registration tokens use the gRPC tokens API.
 */
test.describe("Runner Registration Tokens", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list registration tokens", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.runner.listRunnerTokens({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("create registration token", async ({ api, db }) => {
    const cc = await api.connect();
    const created = await cc.runner.createRunnerToken({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E reg token test",
    }) as { token?: string };
    expect(created.token).toBeTruthy();

    db.cleanup(
      `DELETE FROM runner_grpc_registration_tokens WHERE name = 'E2E reg token test'`
    );
  });

  test("revoke registration token", async ({ api }) => {
    const cc = await api.connect();
    await cc.runner.createRunnerToken({ orgSlug: TEST_ORG_SLUG, name: "E2E revoke test" });

    const list = await cc.runner.listRunnerTokens({ orgSlug: TEST_ORG_SLUG }) as { items: Array<{ id: number; name?: string }> };
    const token = list.items.find((t) => t.name === "E2E revoke test");
    expect(token).toBeTruthy();

    await cc.runner.deleteRunnerToken({ orgSlug: TEST_ORG_SLUG, id: Number(token!.id) });
  });
});
