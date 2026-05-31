import { test } from "../../fixtures";
import { TicketsBoardPage } from "../../pages/tickets-board.page";

test.describe("Tickets · list", () => {
  test("tickets route opens successfully", async ({ page }) => {
    const tickets = new TicketsBoardPage(page);
    await tickets.goto();
    await tickets.expectOnPage();
  });
});
