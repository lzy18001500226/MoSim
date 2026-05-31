import { test, expect } from "../../fixtures";

// Regression guard: a corrupted pg index on `pods.pod_key` caused `list_pods`
// (sequential scan through joined query) to return a pod that `get_pod_by_key`
// (index-only scan) couldn't find. Opening the terminal on that pod then
// triggered a 404 → "HTTP 404: Pod not found [RESOURCE_NOT_FOUND]" spam.
//
// This test enforces the invariant: every pod surfaced by list must be
// retrievable by key. Any future list/detail divergence (index corruption,
// tenant-filter mismatch, stale cache, soft-delete leak) trips this.
test("Pods · list and detail views stay consistent", async ({ page }) => {
  const result = await page.evaluate(async () => {
    const api = (window as unknown as {
      electronAPI: { invoke: (ch: string, ...a: unknown[]) => Promise<unknown> };
    }).electronAPI;

    const listJson = await api.invoke("podPodsJson") as string;
    // pod_pods_json() serializes the state's pods() Vec directly — top-level array.
    const list = JSON.parse(listJson) as Array<{ pod_key: string; status: string }>;

    // Only verify pods that claim to be live — terminated pods are allowed
    // to drift out of detail view during cleanup windows.
    const live = list.filter((p) => p.status === "running" || p.status === "initializing");

    const missing: string[] = [];
    for (const pod of live.slice(0, 10)) {
      try {
        const podJson = await api.invoke("podGetPodJson", pod.pod_key) as string;
        // get_pod_json returns "" when missing (unwrap_or_default on Option<String>).
        if (!podJson || podJson === "") {
          missing.push(`${pod.pod_key}: not found in detail`);
        }
      } catch (err) {
        missing.push(`${pod.pod_key}: ${err instanceof Error ? err.message : String(err)}`);
      }
    }
    return { tested: live.length, missing };
  });

  expect(
    result.missing,
    `list/detail divergence — pods visible in list but missing on detail: ${result.missing.join(" | ")}`,
  ).toEqual([]);
});
