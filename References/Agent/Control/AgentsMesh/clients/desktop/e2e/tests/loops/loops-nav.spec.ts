import { test } from "../../fixtures";
import { LoopsPage } from "../../pages/loops.page";

test("Loops · route opens", async ({ page }) => {
  const loops = new LoopsPage(page);
  await loops.goto();
  await loops.expectOnPage();
});
