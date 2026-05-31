import type { Locator, Page } from "@playwright/test";

/**
 * Page Object Model for the Channels page.
 * Based on: web/src/app/(dashboard)/[org]/channels/page.tsx
 *           web/src/components/ide/sidebar/ChannelsSidebarContent.tsx
 *           web/src/components/channel/ChannelHeader.tsx
 *           web/src/components/channel/ChannelChatPanel.tsx
 */
export class ChannelsPage {
  // Sidebar
  readonly searchInput: Locator;
  readonly createButton: Locator;
  readonly archiveToggle: Locator;
  readonly refreshButton: Locator;
  readonly emptyState: Locator;

  // Create dialog
  readonly dialogTitle: Locator;
  readonly nameInput: Locator;
  readonly descriptionInput: Locator;
  readonly publicButton: Locator;
  readonly privateButton: Locator;
  readonly dialogSubmit: Locator;
  readonly dialogCancel: Locator;

  // Chat panel
  readonly channelTitle: Locator;
  readonly messageInput: Locator;
  readonly sendButton: Locator;
  readonly joinButton: Locator;
  readonly joinPrompt: Locator;

  // Header buttons
  readonly memberManagerButton: Locator;
  readonly podManagerButton: Locator;

  constructor(
    private page: Page,
    private orgSlug: string
  ) {
    // Sidebar
    this.searchInput = page.getByPlaceholder(/搜索频道|Search channels/i);
    this.createButton = page.getByRole("button", { name: /新建频道|New Channel/i });
    this.archiveToggle = page.getByTitle(/归档|archived/i);
    this.refreshButton = page.getByTitle(/刷新|Refresh/i);
    this.emptyState = page.getByText(/暂无频道|No channels/i);

    // Create dialog
    this.dialogTitle = page.getByRole("heading", { name: /创建频道|Create Channel/i });
    this.nameInput = page.locator("#channel-name");
    this.descriptionInput = page.locator("#channel-description");
    // Scope visibility-toggle buttons to the open dialog overlay so we don't
    // match sidebar channel rows whose names contain "Public" / "公开".
    // The project's custom Dialog doesn't set role="dialog"; instead the
    // overlay carries data-dialog-overlay.
    const dialog = page.locator("[data-dialog-overlay]");
    this.publicButton = dialog.getByRole("button", { name: /公开|Public/i });
    this.privateButton = dialog.getByRole("button", { name: /私有|Private/i });
    this.dialogSubmit = page.getByRole("button", { name: /新建频道|New Channel/i }).last();
    this.dialogCancel = page.getByRole("button", { name: /取消|Cancel/i });

    // Chat panel
    this.channelTitle = page.locator("h3");
    this.messageInput = page.locator('[data-testid="message-input-textarea"]');
    // Send button has aria-label "发送" / "Send" (exact). Channel-name buttons in
    // the sidebar may contain the substring "send" (e.g. "e2e-send-xxx"), so we
    // anchor on exact match.
    this.sendButton = page.locator('button[aria-label="发送"], button[aria-label="Send"]');
    this.joinButton = page.getByRole("button", { name: /加入|Join/i });
    this.joinPrompt = page.getByText(/加入此频道|Join this channel/i);

    // Header
    this.memberManagerButton = page.locator("button:has(svg)");
    this.podManagerButton = page.locator("button:has(svg)");
  }

  async goto(): Promise<void> {
    await this.page.goto(`/${this.orgSlug}/channels`);
    await this.page.waitForLoadState("load");
  }

  async createChannel(name: string, options?: {
    description?: string;
    visibility?: "public" | "private";
  }): Promise<void> {
    await this.createButton.click();
    await this.dialogTitle.waitFor({ state: "visible" });
    await this.nameInput.fill(name);
    if (options?.description) {
      await this.descriptionInput.fill(options.description);
    }
    if (options?.visibility === "private") {
      await this.privateButton.click();
    }
    await this.dialogSubmit.click();
    // Wait for dialog to close
    await this.dialogTitle.waitFor({ state: "hidden", timeout: 5000 });
  }

  getChannelItem(name: string): Locator {
    return this.page.getByText(name, { exact: true }).first();
  }

  async selectChannel(name: string): Promise<void> {
    await this.getChannelItem(name).click();
    await this.page.waitForTimeout(500);
  }

  async sendMessage(text: string): Promise<void> {
    await this.messageInput.fill(text);
    await this.page.keyboard.press("Enter");
    await this.page.waitForTimeout(300);
  }

  /** Check if the lock icon is visible for a channel in sidebar */
  async hasLockIcon(name: string): Promise<boolean> {
    const item = this.getChannelItem(name).locator("..");
    const lock = item.locator("svg").first();
    return lock.isVisible();
  }
}
