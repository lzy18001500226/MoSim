// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("gRPC Registration Tokens", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list gRPC tokens returns array", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.runner.listRunnerTokens({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("create gRPC token returns token string", async ({ api, db }) => {
    const cc = await api.connect();
    const created = await cc.runner.createRunnerToken({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E gRPC test token",
    }) as { token?: string; id?: number };
    expect(created.token).toBeTruthy();

    db.cleanup(
      `DELETE FROM runner_grpc_registration_tokens WHERE name = 'E2E gRPC test token'`
    );
  });

  test("delete gRPC token", async ({ api }) => {
    const cc = await api.connect();
    await cc.runner.createRunnerToken({ orgSlug: TEST_ORG_SLUG, name: "E2E delete test token" });

    const list = await cc.runner.listRunnerTokens({ orgSlug: TEST_ORG_SLUG }) as { items: Array<{ id: number; name?: string }> };
    const token = list.items.find((t) => t.name === "E2E delete test token");
    expect(token).toBeTruthy();

    await cc.runner.deleteRunnerToken({ orgSlug: TEST_ORG_SLUG, id: Number(token!.id) });

    await expect(
      cc.runner.deleteRunnerToken({ orgSlug: TEST_ORG_SLUG, id: Number(token!.id) }),
    ).rejects.toMatchObject({ status: 404 });
  });

  test("gRPC tokens full CRUD flow", async ({ api }) => {
    const cc = await api.connect();
    const first = await cc.runner.listRunnerTokens({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    const initialCount = first.items.length;

    await cc.runner.createRunnerToken({ orgSlug: TEST_ORG_SLUG, name: "CRUD test token 1" });
    await cc.runner.createRunnerToken({ orgSlug: TEST_ORG_SLUG, name: "CRUD test token 2" });

    const second = await cc.runner.listRunnerTokens({ orgSlug: TEST_ORG_SLUG }) as { items: Array<{ id: number; name?: string }> };
    expect(second.items.length).toBe(initialCount + 2);

    const t1 = second.items.find((t) => t.name === "CRUD test token 1");
    const t2 = second.items.find((t) => t.name === "CRUD test token 2");
    if (t1) await cc.runner.deleteRunnerToken({ orgSlug: TEST_ORG_SLUG, id: Number(t1.id) });
    if (t2) await cc.runner.deleteRunnerToken({ orgSlug: TEST_ORG_SLUG, id: Number(t2.id) });

    const third = await cc.runner.listRunnerTokens({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(third.items.length).toBe(initialCount);
  });
});
