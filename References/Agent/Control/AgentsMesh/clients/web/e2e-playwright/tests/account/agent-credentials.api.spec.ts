import { test, expect } from "../../fixtures/index";
import { clearAuthRateLimit } from "../../helpers/redis";
import { makeConnectClient, ConnectError } from "../../helpers/connect-client";

/**
 * EnvBundle Connect-RPC regression: every legacy /users/agent-credentials
 * route was replaced by EnvBundleService with a unified payload (kind + data).
 * Tests verify the typed surface and 401/404 boundary cases.
 */
test.describe("EnvBundle API", () => {
  test.beforeEach(async () => {
    clearAuthRateLimit();
  });

  test("list env bundles", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.envBundle.listEnvBundles({}) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("list env bundles without auth returns 401", async ({ api: _api }) => {
    const cc = makeConnectClient("bad");
    await expect(cc.envBundle.listEnvBundles({})).rejects.toMatchObject({
      status: 401,
    });
  });

  test("create env bundle (credential kind)", async ({ api, db }) => {
    const name = `E2E Bundle ${Date.now()}`;
    db.cleanup(`DELETE FROM env_bundles WHERE name LIKE 'E2E Bundle%'`);

    const cc = await api.connect();
    const created = await cc.envBundle.createEnvBundle({
      agentSlug: "claude-code",
      name,
      description: "E2E test credential bundle",
      kind: "credential",
      data: { ANTHROPIC_API_KEY: "sk-ant-test-e2e" },
    }) as { kind: string; name: string; configuredFields: string[]; configuredValues: Record<string, string> };

    expect(created.kind).toBe("credential");
    expect(created.name).toBe(name);
    // credential kind never echoes values back, only field names
    expect(created.configuredFields).toContain("ANTHROPIC_API_KEY");
    expect(Object.keys(created.configuredValues ?? {})).toHaveLength(0);

    db.cleanup(`DELETE FROM env_bundles WHERE name LIKE 'E2E Bundle%'`);
  });

  test("create env bundle (runtime kind echoes values back)", async ({ api, db }) => {
    const name = `E2E Runtime ${Date.now()}`;
    db.cleanup(`DELETE FROM env_bundles WHERE name LIKE 'E2E Runtime%'`);

    const cc = await api.connect();
    const created = await cc.envBundle.createEnvBundle({
      name,
      kind: "runtime",
      data: { LOG_LEVEL: "debug" },
    }) as { kind: string; configuredValues: Record<string, string> };

    expect(created.kind).toBe("runtime");
    // Non-encrypted kinds round-trip plaintext values
    expect(created.configuredValues?.LOG_LEVEL).toBe("debug");

    db.cleanup(`DELETE FROM env_bundles WHERE name LIKE 'E2E Runtime%'`);
  });

  test("delete non-existent env bundle returns 404", async ({ api }) => {
    const cc = await api.connect();
    let caught: ConnectError | undefined;
    try {
      await cc.envBundle.deleteEnvBundle({ id: BigInt(999999) });
    } catch (err) {
      caught = err as ConnectError;
    }
    expect(caught?.status).toBe(404);
  });
});
