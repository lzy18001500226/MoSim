import type { Locator, Page } from "@playwright/test";
import { TEST_ORG_SLUG } from "../helpers/env";
import { gotoHash, expectHashMatches } from "../helpers/nav";

/**
 * Page Object for Channels (multi-agent collaboration).
 * Route: #/:org/channels, #/:org/channels/:id
 */
export class ChannelsPage {
  readonly channelList: Locator;
  readonly messageInput: Locator;
  readonly sendButton: Locator;
  readonly messagesContainer: Locator;
  readonly invitePodButton: Locator;

  constructor(private page: Page) {
    this.channelList = page.locator('[data-section="channel-list"]');
    this.messageInput = page.locator('[data-testid="message-input-textarea"]');
    // Send button has aria-label "发送"/"Send" (exact). Sidebar channel rows
    // may contain "send" in their button names, so use exact aria-label.
    this.sendButton = page.locator('button[aria-label="发送"], button[aria-label="Send"]');
    this.messagesContainer = page.locator('[data-section="messages"], [class*="messages-list"]').first();
    this.invitePodButton = page.getByRole("button", { name: /invite pod|邀请 pod/i });
  }

  async goto(): Promise<void> {
    await gotoHash(this.page, `/${TEST_ORG_SLUG}/channels`);
  }

  async expectOnPage(): Promise<void> {
    await expectHashMatches(this.page, /\/channels/);
  }

  async openChannel(id: string): Promise<void> {
    await gotoHash(this.page, `/${TEST_ORG_SLUG}/channels/${id}`);
  }

  async sendMessage(text: string): Promise<void> {
    await this.messageInput.fill(text);
    await this.sendButton.click();
  }
}
