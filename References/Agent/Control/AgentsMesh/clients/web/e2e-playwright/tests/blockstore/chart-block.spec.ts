// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Chart block smoke test: confirms the full add-chart flow is wired.
// - Slash menu shows the "Chart / Bar" entry
// - Clicking it dispatches a createBlock op for type=chart with bar seed data
// - The backend persists the block with data.type === "bar" and a non-empty
//   series array (matches ChartPreview's expectations)
// - The DOM lands a chart block id, so BlockRenderer dispatched to ChartRenderer
//
// Phase E (wasm Connect ServerStream bridge) is now real-impl'd, so the
// realtime broadcast path is healthy. The page-side `_tick`-driven
// rerender chain (`stores/blockstore.ts` ↔ `useBlock`) hydrates root
// blocks via the normal flow.
test("Chart / Bar option creates a chart block and renders it", async ({
  authenticatedPage,
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  await authenticatedPage.goto(`/${orgSlug}/blocks?ws=${workspaceID}`);
  const addBtn = authenticatedPage.getByRole("button", { name: "+ Add block" });
  await expect(addBtn).toBeVisible({ timeout: 15_000 });
  await addBtn.click();

  const barOption = authenticatedPage.getByRole("button", { name: "Chart / Bar" });
  await expect(barOption).toBeVisible();
  const opsPromise = authenticatedPage.waitForResponse(
    (r) => r.url().includes("BlockstoreService/ApplyOps") && r.request().method() === "POST",
    { timeout: 15_000 },
  );
  await barOption.click();
  const opsRes = await opsPromise;
  expect(opsRes.status(), `ApplyOps failed: ${await opsRes.text()}`).toBeLessThan(300);

  const latest = await pollForLatestChart(cc, workspaceID, rootID);
  expect(latest.data.type).toBe("bar");
  expect(Array.isArray(latest.data.series)).toBe(true);
  expect((latest.data.series as unknown[]).length).toBeGreaterThan(0);

  await expect(authenticatedPage.getByText(/Sample bar chart/).last()).toBeVisible({
    timeout: 10_000,
  });
});

interface ChartBlock {
  id: string;
  type: string;
  data: Record<string, unknown>;
}

async function pollForLatestChart(
  cc: ReturnType<typeof makeConnectClient>,
  workspaceID: string,
  rootID: string,
): Promise<ChartBlock> {
  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline) {
    const res = await cc.blockstore.getSubtree({
      orgSlug,
      workspaceId: workspaceID,
      rootId: rootID,
    }) as { blocks: Array<{ id: string; type: string; dataJson: string }> };
    const charts = res.blocks
      .filter((b) => b.type === "chart")
      .map((b) => ({ id: b.id, type: b.type, data: JSON.parse(b.dataJson) as Record<string, unknown> }));
    if (charts.length > 0) return charts[charts.length - 1];
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error("chart block did not appear in subtree within 10s");
}
