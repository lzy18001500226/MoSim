import { test } from "../../fixtures";
import { WorkspacePage } from "../../pages/workspace.page";

test.describe("Workspace · navigation", () => {
  test("workspace route opens and shows the pod sidebar area", async ({ page }) => {
    const ws = new WorkspacePage(page);
    await ws.goto();
    await ws.expectOnPage();
  });
});
