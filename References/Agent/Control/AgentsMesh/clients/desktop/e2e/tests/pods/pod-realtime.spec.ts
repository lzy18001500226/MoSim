import { test, expect } from "../../fixtures";
import { invokeIpc } from "../../helpers/ipc";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { gotoHash } from "../../helpers/nav";

/**
 * Regression coverage for two desktop-only bugs that hit prod on PR #305:
 *
 *  A) WS 403 storm. Electron loads `out/renderer/index.html` over `file://`,
 *     so the `Origin` header on the `/ws/events` upgrade is the literal
 *     "null". Backend's `gin-contrib/cors` did exact-string match against
 *     the configured allowlist, never matched "null", and 403'd every
 *     reconnect → console flooded with "WebSocket handshake: Unexpected
 *     response code: 403" / "Connection state: disconnected". Real-time
 *     pod status events were silently lost.
 *
 *  B) Pod cache field-name mismatch. `electron-adapter` cached pod JSON
 *     came from backend in snake_case (`pod_key`), but `get_pod_json` /
 *     `upsert_pod` / `update_pod_status` looked it up by `podKey` (camel).
 *     Result: `usePod()` always returned undefined → terminal pane stuck
 *     at "Status: unknown" + sidebar render duplicated React keys (all
 *     undefined) so selecting a pod hid the row.
 *
 * Both bugs were invisible to existing CI: web e2e runs in a real browser
 * (different origin behavior); desktop e2e never registered console
 * listeners or asserted that `usePod` resolved a non-empty status.
 */
test.describe("Desktop pod realtime", () => {
  test("WS connects without 403 / reconnect storm", async ({ page }) => {
    // Register listeners up front — the page is already past
    // domcontentloaded by the time we run, but auth restore + reload may
    // re-trigger ws connect logic.
    const wsErrors: string[] = [];
    const pageErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() !== "error") return;
      const text = msg.text();
      if (
        text.includes("403") ||
        text.includes("Connection state: disconnected") ||
        text.includes("Max reconnect attempts")
      ) {
        wsErrors.push(text);
      }
    });
    page.on("pageerror", (err) => pageErrors.push(`${err.name}: ${err.message}`));

    // Visit workspace; EventSubscriptionManager attaches as soon as the
    // dashboard shell mounts.
    await gotoHash(page, `/${TEST_ORG_SLUG}/workspace`);
    await page.waitForTimeout(5_000); // window for any reconnect storm to surface

    expect(
      wsErrors,
      `WS error storm in console (Origin "null" probably 403'd): ${wsErrors.slice(0, 3).join(" | ")}`
    ).toEqual([]);
    expect(pageErrors, `pageerror: ${pageErrors.join(" | ")}`).toEqual([]);
  });

  test("opening a pod from sidebar keeps it listed and shows non-unknown status", async ({ page }) => {
    // Assert prerequisites — same gate as pod-lifecycle.spec, but as a hard
    // fail rather than a silent skip. The dev env contract is "at least one
    // online runner + one builtin agent".
    const runners = await invokeIpc<string>(page, "runnerFetchRunners");
    const runnerList = JSON.parse(runners) as { runners?: { id: number; status: string }[] } | { id: number; status: string }[];
    const onlineRunner = (Array.isArray(runnerList) ? runnerList : runnerList.runners ?? [])
      .find((r) => r.status === "online");
    expect(onlineRunner, "dev env must have an online runner").toBeTruthy();

    const agentsJson = await invokeIpc<string>(page, "agentListAgents");
    const agents = JSON.parse(agentsJson) as { builtin_agents?: { slug: string }[] };
    const agent = agents.builtin_agents?.[0];
    expect(agent, "dev env must have a builtin agent").toBeTruthy();

    // Seed a running pod via the same IPC the renderer uses.
    const created = await invokeIpc<string>(page, "podCreatePod", JSON.stringify({
      agent_slug: agent!.slug,
      runner_id: onlineRunner!.id,
      cols: 142,
      rows: 34,
    }));
    const resp = JSON.parse(created) as { pod: { pod_key: string; status: string }; warning?: string };
    const pod = resp.pod;
    expect(pod.pod_key, "podCreatePod returned a pod_key").toBeTruthy();
    expect(pod.status, "newly-created pod has a real status, not 'unknown'").not.toBe("unknown");

    try {
      await gotoHash(page, `/${TEST_ORG_SLUG}/workspace`);

      // Desktop's electron-adapter ships a `NoopEventsManager` (see
      // packages/electron-adapter/src/provider.ts): realtime `pod:created`
      // events are not delivered to the renderer until a main-process
      // Connect ServerStream bridge lands. The seed `podCreatePod` above
      // bypasses the renderer entirely (direct IPC → Connect → DB), so
      // there is no event to dispatch and no React handler to flush.
      // After auth restore the renderer's hash is already at
      // `/{org}/workspace`, so `gotoHash` does not remount the sidebar
      // either (the useEffect's `[currentOrg, ...]` deps stay stable).
      // Reload the page so WorkspaceSidebarContent mounts fresh and
      // `fetchSidebarPods` runs against the post-create DB state.
      await page.reload();
      await page.waitForLoadState("domcontentloaded");
      await invokeIpc(page, "authBootstrap");
      await gotoHash(page, `/${TEST_ORG_SLUG}/workspace`);

      // DEBUG: inspect what pods the sidebar fetched + which DOM nodes contain "1-standa".
      await page.waitForTimeout(3000);
      const dbg = await page.evaluate(() => {
        try {
          const html = document.body.innerText.slice(0, 2000);
          return { html };
        } catch { return { html: "(eval failed)" }; }
      });
      console.log("DEBUG body text head:", dbg.html);

      // Sidebar should render the new pod entry. PodListItem renders the
      // display name through `getPodDisplayName`, which truncates pod_key
      // to the first 8 chars (`getShortPodKey`) when no alias / ticket /
      // loop / OSC title is set. Match on the prefix to track the actual
      // UX and stay resilient to pod_key tweaks.
      const podPrefix = pod.pod_key.slice(0, 8);
      const sidebarPod = page.getByText(podPrefix, { exact: false }).first();
      await expect(sidebarPod, "new pod must appear in sidebar").toBeVisible({ timeout: 15_000 });

      // Click to open terminal pane. Pre-fix: the click made the pod
      // disappear from the sidebar (camel/snake mismatch made React keys
      // collide → row hidden).
      await sidebarPod.click();

      // Regression assertion #1: row is still in the sidebar after click.
      await expect(sidebarPod, "pod must remain visible after selection").toBeVisible({ timeout: 5_000 });

      // Regression assertion #2: terminal pane status text is not "unknown".
      // The PaneLoadingState renders `Status: <podStatus>`. If the
      // electron-adapter cache lookup is broken, pod store returns
      // undefined → "unknown" fallback in usePodStatus.
      const statusUnknown = page.getByText(/Status:\s*unknown/i);
      await expect(
        statusUnknown,
        "Status: unknown indicates electron-adapter cache key mismatch is back"
      ).toHaveCount(0, { timeout: 10_000 });
    } finally {
      await invokeIpc<void>(page, "podTerminatePod", pod.pod_key).catch(() => undefined);
    }
  });
});
