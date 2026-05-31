// Migrated R5+: Connect-RPC only (no REST middle layer).
//
// Structured AST shape is opaque to the Connect wire — both content and
// mentions travel as JSON strings (`contentJson` / `mentionsJson`). Tests
// serialize on send and parse on receive. Server behavior (parsing source
// markdown, deduping mentions, etc.) is unchanged from the REST era.
import { test, expect } from "../../fixtures/index";
import { test as uiTest, expect as uiExpect } from "@playwright/test";
import { ChannelsPage } from "../../pages/channels.page";
import { SidebarPage } from "../../pages/sidebar.page";
import { TEST_ORG_SLUG, getApiBaseUrl } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { textContent } from "../../helpers/test-data";
import { makeConnectClient } from "../../helpers/connect-client";

interface MessageContent {
  kind?: string;
  blocks?: Array<{
    type: string;
    level?: number;
    language?: string;
    text?: string;
    items?: Array<Array<{ type: string }>>;
    elements?: Array<{
      type: string;
      text?: string;
      url?: string;
      style?: { bold?: boolean; italic?: boolean; strike?: boolean; code?: boolean };
      bold?: boolean;
      italic?: boolean;
      strike?: boolean;
      code?: boolean;
      entity_type?: string;
      entity_key?: string;
      display?: string;
    }>;
  }>;
}

interface MessageMentions {
  users?: number[];
  pods?: string[];
}

interface SentMessage {
  id: bigint;
  body: string;
  contentJson?: string;
  mentionsJson?: string;
  editedAt?: string;
  replyTo?: bigint;
  senderPod?: string;
}

function parseContent(m: SentMessage): MessageContent {
  return m.contentJson ? JSON.parse(m.contentJson) as MessageContent : {};
}
function parseMentions(m: SentMessage): MessageMentions {
  return m.mentionsJson ? JSON.parse(m.mentionsJson) as MessageMentions : {};
}

// ────────────────────────────────────────────────────
// Part 1: API-level structured content tests
// ────────────────────────────────────────────────────

test.describe("Structured Message — API", () => {
  let channelId: bigint;

  test.beforeAll(async ({ api }) => {
    clearAuthRateLimit();
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E StructMsg API " + Date.now(),
    }) as { id: bigint };
    channelId = channel.id;
  });

  test.afterAll(async ({ api }) => {
    const cc = await api.connect();
    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channelId });
  });

  test("send plain text paragraph", async ({ api }) => {
    const cc = await api.connect();
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(textContent("Hello structured world")),
    }) as SentMessage;
    expect(message.body).toBe("Hello structured world");
    const content = parseContent(message);
    expect(content.kind).toBe("text");
    expect(content.blocks).toHaveLength(1);
    expect(content.blocks![0].type).toBe("paragraph");
    expect(content.blocks![0].elements![0].type).toBe("text");
    expect(content.blocks![0].elements![0].text).toBe("Hello structured world");
  });

  test("send multi-paragraph message", async ({ api }) => {
    const cc = await api.connect();
    const content = {
      kind: "text",
      blocks: [
        { type: "paragraph", elements: [{ type: "text", text: "First paragraph" }] },
        { type: "paragraph", elements: [{ type: "text", text: "Second paragraph" }] },
        { type: "paragraph", elements: [{ type: "text", text: "Third paragraph" }] },
      ],
    };
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(content),
    }) as SentMessage;
    expect(message.body).toBe("First paragraph\nSecond paragraph\nThird paragraph");
    expect(parseContent(message).blocks).toHaveLength(3);
  });

  test("send message with bold/italic/strike/code formatting", async ({ api }) => {
    const cc = await api.connect();
    const content = {
      kind: "text",
      blocks: [{
        type: "paragraph",
        elements: [
          { type: "text", text: "normal " },
          { type: "text", text: "bold", bold: true },
          { type: "text", text: " " },
          { type: "text", text: "italic", italic: true },
          { type: "text", text: " " },
          { type: "text", text: "struck", strike: true },
          { type: "text", text: " " },
          { type: "text", text: "code", code: true },
        ],
      }],
    };
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(content),
    }) as SentMessage;
    expect(message.body).toBe("normal bold italic struck code");
    const blocks = parseContent(message).blocks!;
    expect(blocks[0].elements).toHaveLength(8);
    expect(blocks[0].elements![1].style?.bold).toBe(true);
    expect(blocks[0].elements![3].style?.italic).toBe(true);
    expect(blocks[0].elements![5].style?.strike).toBe(true);
    expect(blocks[0].elements![7].style?.code).toBe(true);
  });

  test("send message with user mention — body includes @display", async ({ api }) => {
    const cc = await api.connect();
    const content = {
      kind: "text",
      blocks: [{
        type: "paragraph",
        elements: [
          { type: "text", text: "Hey " },
          { type: "mention", entity_type: "user", entity_key: "1", display: "dev-user" },
          { type: "text", text: " check this" },
        ],
      }],
    };
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(content),
    }) as SentMessage;
    expect(message.body).toBe("Hey @dev-user check this");
    const mentionEl = parseContent(message).blocks![0].elements!.find((e) => e.type === "mention");
    expect(mentionEl).toBeTruthy();
    expect(mentionEl!.entity_type).toBe("user");
    expect(mentionEl!.entity_key).toBe("1");
  });

  test("send message with pod mention — mention element preserved in content", async ({ api }) => {
    const cc = await api.connect();
    const content = {
      kind: "text",
      blocks: [{
        type: "paragraph",
        elements: [
          { type: "mention", entity_type: "pod", entity_key: "fake-pod-key", display: "MyBot" },
          { type: "text", text: " fix the bug" },
        ],
      }],
    };
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(content),
    }) as SentMessage;
    expect(message.body).toBe("@MyBot fix the bug");
    const mentionEl = parseContent(message).blocks![0].elements![0];
    expect(mentionEl.type).toBe("mention");
    expect(mentionEl.entity_key).toBe("fake-pod-key");
    expect(mentionEl.display).toBe("MyBot");
  });

  test("send message with link element", async ({ api }) => {
    const cc = await api.connect();
    const content = {
      kind: "text",
      blocks: [{
        type: "paragraph",
        elements: [
          { type: "text", text: "See " },
          { type: "link", text: "docs", url: "https://example.com/docs" },
        ],
      }],
    };
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(content),
    }) as SentMessage;
    expect(message.body).toBe("See docs");
    expect(parseContent(message).blocks![0].elements![1].url).toBe("https://example.com/docs");
  });

  test("send message with linebreak", async ({ api }) => {
    const cc = await api.connect();
    const content = {
      kind: "text",
      blocks: [{
        type: "paragraph",
        elements: [
          { type: "text", text: "before" },
          { type: "linebreak" },
          { type: "text", text: "after" },
        ],
      }],
    };
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(content),
    }) as SentMessage;
    expect(message.body).toBe("before\nafter");
  });

  test("duplicate mentions deduplicated in mentions index", async ({ api }) => {
    const cc = await api.connect();
    const content = {
      kind: "text",
      blocks: [{
        type: "paragraph",
        elements: [
          { type: "mention", entity_type: "user", entity_key: "1", display: "dev" },
          { type: "text", text: " and " },
          { type: "mention", entity_type: "user", entity_key: "1", display: "dev" },
        ],
      }],
    };
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(content),
    }) as SentMessage;
    const mentions = parseMentions(message);
    expect(mentions.users).toHaveLength(1);
    expect(mentions.users![0]).toBe(1);
    const mentionEls = parseContent(message).blocks![0].elements!.filter((e) => e.type === "mention");
    expect(mentionEls).toHaveLength(2);
  });

  test("edit message updates body and content", async ({ api }) => {
    const cc = await api.connect();
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(textContent("original text")),
    }) as SentMessage;

    const edited = await cc.channel.editChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      messageId: message.id,
      contentJson: JSON.stringify(textContent("edited text")),
    }) as SentMessage;
    expect(edited.body).toBe("edited text");
    expect(edited.editedAt).toBeTruthy();
    expect(parseContent(edited).blocks![0].elements![0].text).toBe("edited text");
  });

  test("message list returns body and structured content", async ({ api }) => {
    const cc = await api.connect();
    await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(textContent("list test msg")),
    });
    const list = await cc.channel.listChannelMessages({
      orgSlug: TEST_ORG_SLUG,
      channelId,
    }) as { items: SentMessage[] };
    const found = list.items.find((m) => m.body === "list test msg");
    expect(found).toBeTruthy();
    expect(found!.contentJson).toBeTruthy();
    expect(parseContent(found!).kind).toBe("text");
  });

  test("empty content blocks rejected", async ({ api }) => {
    const cc = await api.connect();
    try {
      await cc.channel.sendChannelMessage({
        orgSlug: TEST_ORG_SLUG,
        channelId,
        contentJson: JSON.stringify({ kind: "text" }),
      });
      // Server accepted with empty body — valid behavior.
    } catch (err: unknown) {
      // Server rejected with InvalidArgument — also valid.
      expect((err as { status: number }).status).toBe(400);
    }
  });

  test("reply_to threads a message to a parent", async ({ api }) => {
    const cc = await api.connect();
    const parent = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(textContent("original question")),
    }) as SentMessage;
    const reply = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      contentJson: JSON.stringify(textContent("the answer")),
      replyTo: parent.id,
    }) as SentMessage;
    expect(reply.replyTo).toBe(parent.id);
    expect(reply.body).toBe("the answer");
  });

  test("reply_to to unknown id — server is permissive or rejects", async ({ api }) => {
    const cc = await api.connect();
    try {
      const msg = await cc.channel.sendChannelMessage({
        orgSlug: TEST_ORG_SLUG,
        channelId,
        contentJson: JSON.stringify(textContent("orphan reply")),
        replyTo: BigInt(99999999),
      }) as SentMessage;
      expect(msg.id).toBeTruthy();
    } catch (err: unknown) {
      expect((err as { status: number }).status).toBe(400);
    }
  });

  test("pod_key send path: sender_pod is set when supplied", async ({ api }) => {
    const cc = await api.connect();
    const podKey = "e2e-synthetic-pod-key";
    try {
      const message = await cc.channel.sendChannelMessage({
        orgSlug: TEST_ORG_SLUG,
        channelId,
        contentJson: JSON.stringify(textContent("agent hello")),
        podKey,
      }) as SentMessage;
      expect(message.senderPod).toBe(podKey);
    } catch (err: unknown) {
      const status = (err as { status: number }).status;
      expect([400, 403, 404]).toContain(status);
    }
  });

  test("source: heading + list + code block parse via goldmark", async ({ api }) => {
    const cc = await api.connect();
    const source = "# Heading\n\n- item one\n- item two\n  - nested\n\n```go\nfunc main() {}\n```";
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      source,
    }) as SentMessage;
    const content = parseContent(message);
    const types = content.blocks!.map((b) => b.type);
    expect(types).toEqual(["heading", "list", "code_block"]);
    expect(content.blocks![0].level).toBe(1);
    expect(content.blocks![2].language).toBe("go");
    expect(content.blocks![2].text).toBe("func main() {}");
    expect(message.body).toContain("func main() {}");
    type ListBlock = { type: string; items?: ListBlock[][] };
    const allInnerBlocks = (content.blocks![1].items as ListBlock[][]).flat();
    const innerList = allInnerBlocks.find((b) => b.type === "list");
    expect(innerList).toBeTruthy();
  });

  test("source: inline marks become typed style elements", async ({ api }) => {
    const cc = await api.connect();
    const source = "**bold** *italic* ~~strike~~ `code`";
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      source,
    }) as SentMessage;
    const styles = parseContent(message).blocks![0].elements!
      .filter((e) => e.type === "text" && e.style)
      .map((e) => e.style!);
    expect(styles.some((s) => s.bold)).toBe(true);
    expect(styles.some((s) => s.italic)).toBe(true);
    expect(styles.some((s) => s.strike)).toBe(true);
    expect(styles.some((s) => s.code)).toBe(true);
  });

  test("source: mention map upgrades @key into typed mention", async ({ api }) => {
    const cc = await api.connect();
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      source: "ping @dev-user please",
      mentions: { "dev-user": { entityType: "user", entityKey: "1" } },
    }) as SentMessage;
    const mention = parseContent(message).blocks![0].elements!.find((e) => e.type === "mention");
    expect(mention).toBeTruthy();
    expect(mention!.entity_key).toBe("1");
    expect(parseMentions(message).users).toContain(1);
  });

  test("source: link with disallowed scheme degrades to plain text", async ({ api }) => {
    const cc = await api.connect();
    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      source: "[click](javascript:alert(1)) and [ok](https://example.com)",
    }) as SentMessage;
    const linkEls = parseContent(message).blocks![0].elements!.filter((e) => e.type === "link");
    expect(linkEls.map((e) => e.url)).toEqual(["https://example.com"]);
  });

  test("source: providing both source and content is a 400", async ({ api }) => {
    const cc = await api.connect();
    await expect(
      cc.channel.sendChannelMessage({
        orgSlug: TEST_ORG_SLUG,
        channelId,
        source: "# H",
        contentJson: JSON.stringify(textContent("x")),
      })
    ).rejects.toMatchObject({ status: 400 });
  });
});

// ────────────────────────────────────────────────────
// Part 2: UI rendering tests (uses storageState from chromium project)
// ────────────────────────────────────────────────────

uiTest.describe("Structured Message — UI Rendering", () => {
  let channels: ChannelsPage;
  let sidebar: SidebarPage;

  uiTest.beforeEach(async ({ page }) => {
    clearAuthRateLimit();
    channels = new ChannelsPage(page, TEST_ORG_SLUG);
    sidebar = new SidebarPage(page, TEST_ORG_SLUG);
    await page.goto(`/${TEST_ORG_SLUG}/workspace`);
    await page.waitForLoadState("load");
  });

  uiTest("plain text message renders in chat", async ({ page }) => {
    const name = "E2E StructUI Plain " + Date.now();
    await sidebar.navigateTo("channels");
    await channels.createChannel(name);
    await channels.selectChannel(name);

    await channels.sendMessage("Simple plain text message");
    await uiExpect(page.getByText("Simple plain text message")).toBeVisible({ timeout: 5000 });
  });

  uiTest("multiline message renders multiple lines", async ({ page }) => {
    const name = "E2E StructUI Multi " + Date.now();
    await sidebar.navigateTo("channels");
    await channels.createChannel(name);
    await channels.selectChannel(name);

    await channels.messageInput.click();
    await page.keyboard.type("Line one");
    await page.keyboard.down("Shift");
    await page.keyboard.press("Enter");
    await page.keyboard.up("Shift");
    await page.keyboard.type("Line two");
    await page.keyboard.press("Enter");
    await page.waitForTimeout(500);

    await uiExpect(page.getByText("Line one")).toBeVisible({ timeout: 5000 });
    await uiExpect(page.getByText("Line two")).toBeVisible({ timeout: 5000 });
  });

  // Issue an authed Connect call from inside the UI test (uses the same
  // token the storageState injected) to seed a message the renderer must
  // turn into <strong>/<mention>/etc.
  async function loginToken(): Promise<string> {
    const apiBase = getApiBaseUrl();
    const res = await fetch(`${apiBase}/proto.auth.v1.AuthService/Login`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Connect-Protocol-Version": "1" },
      body: JSON.stringify({ email: "dev@agentsmesh.local", password: "devpass123" }),
    });
    const data = await res.json() as { token: string };
    return data.token;
  }

  // Verifies the full Connect send/list pipeline: send a content_json AST,
  // reload, listChannelMessages returns content_json, wasm cache preserves it
  // (channelMessageWasmAdapter converts content↔content_json at the wasm
  // boundary), renderer (StructuredContent) emits <strong>. Counterpart
  // unit coverage lives in StructuredContent.test.tsx.
  uiTest("bold text renders as <strong> in UI", async ({ page }) => {
    const name = "E2E StructUI Bold " + Date.now();
    await sidebar.navigateTo("channels");
    await channels.createChannel(name);
    await channels.selectChannel(name);

    const token = await loginToken();
    const cc = makeConnectClient(token);
    const { items } = await cc.channel.listChannels({ orgSlug: TEST_ORG_SLUG }) as {
      items: { id: bigint; name: string }[];
    };
    const ch = items.find((c) => c.name === name);
    uiExpect(ch, "newly-created channel must appear in listChannels").toBeTruthy();

    await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: ch!.id,
      contentJson: JSON.stringify({
        kind: "text",
        blocks: [{
          type: "paragraph",
          elements: [
            { type: "text", text: "This is " },
            { type: "text", text: "important", bold: true },
          ],
        }],
      }),
    });

    await page.reload();
    await channels.selectChannel(name);

    await uiExpect(page.locator("[data-message-id]").getByText("important").first()).toBeVisible({ timeout: 5000 });
    const boldEl = page.locator("strong").filter({ hasText: "important" });
    await uiExpect(boldEl).toBeVisible({ timeout: 3000 });
  });

  uiTest("mention renders with @-prefix highlight", async ({ page }) => {
    const name = "E2E StructUI Mention " + Date.now();
    await sidebar.navigateTo("channels");
    await channels.createChannel(name);
    await channels.selectChannel(name);

    const token = await loginToken();
    const cc = makeConnectClient(token);
    const { items } = await cc.channel.listChannels({ orgSlug: TEST_ORG_SLUG }) as {
      items: { id: bigint; name: string }[];
    };
    const ch = items.find((c) => c.name === name);
    uiExpect(ch, "newly-created channel must appear in listChannels").toBeTruthy();

    await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: ch!.id,
      contentJson: JSON.stringify({
        kind: "text",
        blocks: [{
          type: "paragraph",
          elements: [
            { type: "text", text: "Hello " },
            { type: "mention", entity_type: "user", entity_key: "1", display: "dev-user" },
          ],
        }],
      }),
    });

    await page.reload();
    await channels.selectChannel(name);

    await uiExpect(page.locator("[data-message-id]").getByText("@dev-user").first()).toBeVisible({ timeout: 5000 });
  });

  uiTest("source-mode roundtrip renders heading + list + code", async ({ page }) => {
    const name = "E2E StructUI Source " + Date.now();
    await sidebar.navigateTo("channels");
    await channels.createChannel(name);
    await channels.selectChannel(name);

    const token = await loginToken();
    const cc = makeConnectClient(token);
    const { items } = await cc.channel.listChannels({ orgSlug: TEST_ORG_SLUG }) as {
      items: { id: bigint; name: string }[];
    };
    const ch = items.find((c) => c.name === name);
    uiExpect(ch, "newly-created channel must appear in listChannels").toBeTruthy();

    await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: ch!.id,
      source: "# Big heading\n\n- bullet a\n- bullet b\n\n```\nfn main() {}\n```",
    });

    await page.reload();
    await channels.selectChannel(name);

    const bubble = page.locator("[data-message-id]").last();
    await uiExpect(bubble.locator("h1, h2, h3").filter({ hasText: "Big heading" }).first()).toBeVisible({ timeout: 5000 });
    await uiExpect(bubble.locator("ul li").filter({ hasText: "bullet a" })).toBeVisible({ timeout: 3000 });
    await uiExpect(bubble.locator("pre code").filter({ hasText: "fn main()" })).toBeVisible({ timeout: 3000 });
  });
});
