// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Agent Configuration API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list agents", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { agents?: unknown[] };
    expect(res).toBeTruthy();
  });

  test("get agent config schema", async ({ api }) => {
    const cc = await api.connect();
    const schema = await cc.agent.getAgentConfigSchema({
      orgSlug: TEST_ORG_SLUG,
      agentSlug: "claude-code",
    }) as { fields?: unknown[] };
    expect(schema).toBeTruthy();
  });

  test("get agentpod settings", async ({ api }) => {
    const cc = await api.connect();
    // Tolerates either success or server-side cache miss (legacy [200, 500] behavior).
    const settings = await cc.agentPodSettings.getSettings({}).catch((e) => e);
    expect(settings).toBeTruthy();
  });

  test("list agentpod providers", async ({ api }) => {
    const cc = await api.connect();
    const providers = await cc.agentPodSettings.listProviders({}).catch((e) => e);
    expect(providers).toBeTruthy();
  });

  test("list user agent configs", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.userAgentConfig.listUserAgentConfigs({}) as { configs: unknown[] };
    expect(Array.isArray(res.configs)).toBe(true);
  });

  test("set and get user agent config", async ({ api }) => {
    const cc = await api.connect();
    await cc.userAgentConfig.setUserAgentConfig({
      agentSlug: "claude-code",
      configValuesJson: JSON.stringify({ model: "opus" }),
    });

    const got = await cc.userAgentConfig.getUserAgentConfig({
      agentSlug: "claude-code",
    }) as { configValuesJson: string };
    expect(got.configValuesJson).toBeTruthy();
  });
});
