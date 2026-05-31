import { test } from "../../fixtures";
import { MeshPage } from "../../pages/mesh.page";

test("Mesh · route opens", async ({ page }) => {
  const mesh = new MeshPage(page);
  await mesh.goto();
  await mesh.expectOnPage();
});
