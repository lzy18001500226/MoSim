import { test, expect } from "../../fixtures";
import { invokeIpc } from "../../helpers/ipc";
import { gotoHash } from "../../helpers/nav";
import { TEST_ORG_SLUG } from "../../helpers/env";

// Desktop counterpart of clients/web/e2e-playwright/tests/mesh/channel-pod-membership.spec.ts.
// Exercises the same regression (issue #400) through the Electron bridge:
//   - Channel created via IPC (channel_create_channel)
//   - Pod joined via IPC (channel_join_channel)
//   - RightRail rendered by the same React tree the web app uses
// Pod setup/teardown via Connect-RPC (REST endpoints removed in R6).

const RAIL = '[data-testid="channel-right-rail"]';

interface CreatedPod { podKey: string }

async function createPodViaApi(
  api: import("../../../../web/e2e-playwright/fixtures/api.fixture").ApiFixture,
  prompt: string,
): Promise<CreatedPod> {
  const cc = await api.connect();
  const runnersResp = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items?: Array<{ id: bigint | number }> };
  const runners = runnersResp.items ?? [];
  expect(runners.length, "dev env must have an online runner").toBeGreaterThan(0);
  const agentsResp = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents?: Array<{ slug: string }> };
  const agents = agentsResp.builtinAgents ?? [];
  expect(agents.length, "dev env must have a builtin agent").toBeGreaterThan(0);
  const agent = agents.find((a) => a.slug === "e2e-echo") ?? agents[0];
  const resp = await cc.pod.createPod({
    orgSlug: TEST_ORG_SLUG,
    runnerId: typeof runners[0].id === "bigint" ? runners[0].id : BigInt(runners[0].id),
    agentSlug: agent.slug,
    agentfileLayer: `PROMPT ${JSON.stringify(prompt)}\n`,
  }) as { pod?: { podKey?: string }; podKey?: string };
  const podKey = resp.pod?.podKey ?? resp.podKey;
  expect(podKey, "createPod must return a pod_key").toBeTruthy();
  return { podKey: podKey! };
}

async function archiveChannel(
  api: import("../../../../web/e2e-playwright/fixtures/api.fixture").ApiFixture,
  id: number | bigint,
): Promise<void> {
  const cc = await api.connect();
  await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, channelId: typeof id === "bigint" ? id : BigInt(id) }).catch(() => undefined);
}

async function terminatePod(
  api: import("../../../../web/e2e-playwright/fixtures/api.fixture").ApiFixture,
  podKey: string,
): Promise<void> {
  const cc = await api.connect();
  await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey }).catch(() => undefined);
}

test.describe("Channel × Pod membership (Electron IPC, issue #400)", () => {
  test("D-001 channel_join_channel → RightRail renders pod row", async ({ page, api }) => {
    const pod = await createPodViaApi(api, "desktop-d001");

    // Create channel via IPC (exercises the bridge end-to-end).
    const name = `e2e-desktop-d001-${Date.now()}`;
    const createJson = await invokeIpc<string>(page, "channelCreateChannel",
      JSON.stringify({ name, visibility: "public" }));
    const channel = JSON.parse(createJson) as { id: number; agent_count: number };
    expect(channel.id).toBeGreaterThan(0);
    expect(channel.agent_count).toBe(0);

    try {
      // Join via IPC. Returns updated Channel JSON with agent_count refreshed.
      const joinedJson = await invokeIpc<string>(page, "channelJoinChannel", channel.id, pod.podKey);
      const joined = JSON.parse(joinedJson) as { agent_count?: number };
      expect(joined.agent_count).toBe(1);

      // Verify Rust core's pods_by_channel cache is populated (set by join_channel).
      const cachedJson = await invokeIpc<string>(page, "channelChannelPodsJson", channel.id);
      const cached = JSON.parse(cachedJson) as Array<{ pod_key: string }>;
      expect(cached.length, "pods_by_channel cache after channelJoinChannel").toBe(1);
      expect(cached[0]?.pod_key).toBe(pod.podKey);

      // Navigate and verify UI surfaces the new pod row + count.
      await gotoHash(page, `/${TEST_ORG_SLUG}/channels/${channel.id}`);
      const rail = page.locator(RAIL);
      await rail.waitFor({ timeout: 15_000 });
      await expect(rail).toContainText("1");
      await expect(rail.locator("ul li")).toHaveCount(1);
    } finally {
      await invokeIpc(page, "channelLeaveChannel", channel.id, pod.podKey).catch(() => undefined);
      await terminatePod(api, pod.podKey);
      await archiveChannel(api, channel.id);
    }
  });

  test("D-002 channel_leave_channel → pod row removed from RightRail", async ({ page, api }) => {
    const p1 = await createPodViaApi(api, "desktop-d002-a");
    const p2 = await createPodViaApi(api, "desktop-d002-b");

    const name = `e2e-desktop-d002-${Date.now()}`;
    const createJson = await invokeIpc<string>(page, "channelCreateChannel",
      JSON.stringify({ name, visibility: "public" }));
    const channel = JSON.parse(createJson) as { id: number };

    try {
      await invokeIpc<string>(page, "channelJoinChannel", channel.id, p1.podKey);
      await invokeIpc<string>(page, "channelJoinChannel", channel.id, p2.podKey);

      await gotoHash(page, `/${TEST_ORG_SLUG}/channels/${channel.id}`);
      const rail = page.locator(RAIL);
      await rail.waitFor({ timeout: 15_000 });
      await expect(rail.locator("ul li")).toHaveCount(2);

      // Leave one pod via IPC — RightRail must drop to 1 row.
      const leftJson = await invokeIpc<string>(page, "channelLeaveChannel", channel.id, p1.podKey);
      const left = JSON.parse(leftJson) as { agent_count?: number };
      expect(left.agent_count).toBe(1);

      // Verify the renderer-side pod cache reflects the leave. This catches a
      // common failure mode: backend dropped the pod but ChannelLocalState's
      // _podsByChannel still mirrors the pre-leave list (no notify).
      const afterLeaveCache = await page.evaluate(async ({ id }) => {
        const svc = (window as unknown as { electronAPI: { invoke: (m: string, ...a: unknown[]) => Promise<unknown> } }).electronAPI;
        // Trigger an explicit refresh through ElectronChannelService.get_channel_pods,
        // which mirrors the backend response into _podsByChannel.
        await svc.invoke("channelGetChannelPods", id);
        return svc.invoke("channelChannelPodsJson", id) as Promise<string>;
      }, { id: channel.id });
      const cachedAfterLeave = JSON.parse(afterLeaveCache) as Array<{ pod_key: string }>;
      expect(cachedAfterLeave.length, "channel_pods_json after leave").toBe(1);

      // Re-navigate (different route then back) to force RightRail unmount/remount.
      await gotoHash(page, `/${TEST_ORG_SLUG}/workspace`);
      await gotoHash(page, `/${TEST_ORG_SLUG}/channels/${channel.id}`);
      await rail.waitFor({ timeout: 15_000 });
      await expect(rail.locator("ul li")).toHaveCount(1);
      await expect(rail).not.toContainText(p1.podKey);
    } finally {
      for (const k of [p1.podKey, p2.podKey]) {
        await invokeIpc(page, "channelLeaveChannel", channel.id, k).catch(() => undefined);
        await terminatePod(api, k);
      }
      await archiveChannel(api, channel.id);
    }
  });
});
