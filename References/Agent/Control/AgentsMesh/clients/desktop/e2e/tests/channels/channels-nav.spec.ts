import { test } from "../../fixtures";
import { ChannelsPage } from "../../pages/channels.page";

test("Channels · route opens", async ({ page }) => {
  const channels = new ChannelsPage(page);
  await channels.goto();
  await channels.expectOnPage();
});
