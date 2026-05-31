// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { textContent } from "../../helpers/test-data";

// Second user in the same org (from seed data)
const SECOND_USER = { email: "dev2@agentsmesh.local", password: "devpass123" };

test.describe("Channel IM Group Model", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  // ── Visibility & Membership ──

  test("create public channel — creator is auto-member", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Public " + Date.now(),
      visibility: "public",
    }) as { id: bigint; visibility: string; isMember: boolean; memberCount: bigint };
    expect(channel.visibility).toBe("public");
    expect(channel.isMember).toBe(true);
    expect(Number(channel.memberCount)).toBeGreaterThanOrEqual(1);

    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  test("create private channel with initial members", async ({ api }) => {
    const cc = await api.connect();
    const { items: members } = await cc.org.listMembers({ orgSlug: TEST_ORG_SLUG }) as {
      items: { userId: bigint; user?: { email: string } }[];
    };
    const otherUser = members?.find((m) => m.user?.email !== "dev@agentsmesh.local");

    const memberIds: bigint[] = otherUser?.userId ? [otherUser.userId] : [];
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Private " + Date.now(),
      visibility: "private",
      memberIds,
    }) as { id: bigint; visibility: string; isMember: boolean };
    expect(channel.visibility).toBe("private");
    expect(channel.isMember).toBe(true);

    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  test("private channel invisible to non-member", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Invisible " + Date.now(),
      visibility: "private",
    }) as { id: bigint };

    const adminToken = await api.loginAs(SECOND_USER.email, SECOND_USER.password);
    const adminCc = api.connectWithToken(adminToken);

    const { items: visible } = await adminCc.channel.listChannels({ orgSlug: TEST_ORG_SLUG }) as {
      items: { id: bigint }[];
    };
    const found = visible?.find((c) => c.id === channel.id);
    expect(found).toBeUndefined();

    // Direct access — Connect maps PermissionDenied → 403.
    await expect(
      adminCc.channel.getChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id })
    ).rejects.toMatchObject({ status: 403 });

    await api.login();
    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  // ── Join / Leave ──

  test("join public channel", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Join " + Date.now(),
      visibility: "public",
    }) as { id: bigint };

    const adminToken = await api.loginAs(SECOND_USER.email, SECOND_USER.password);
    const adminCc = api.connectWithToken(adminToken);

    await adminCc.channel.joinChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });

    const detail = await adminCc.channel.getChannel({
      orgSlug: TEST_ORG_SLUG,
      id: channel.id,
    }) as { isMember: boolean };
    expect(detail.isMember).toBe(true);

    await api.login();
    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  test("cannot join private channel", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E NoJoin " + Date.now(),
      visibility: "private",
    }) as { id: bigint };

    const adminToken = await api.loginAs(SECOND_USER.email, SECOND_USER.password);
    const adminCc = api.connectWithToken(adminToken);
    await expect(
      adminCc.channel.joinChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id })
    ).rejects.toMatchObject({ status: 403 });

    await api.login();
    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  test("leave channel", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Leave " + Date.now(),
      visibility: "public",
    }) as { id: bigint };

    const adminToken = await api.loginAs(SECOND_USER.email, SECOND_USER.password);
    const adminCc = api.connectWithToken(adminToken);
    await adminCc.channel.joinChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
    await adminCc.channel.leaveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });

    await api.login();
    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  test("creator cannot leave channel", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E CreatorLeave " + Date.now(),
    }) as { id: bigint };

    await expect(
      cc.channel.leaveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id })
    ).rejects.toMatchObject({ status: 403 });

    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  // ── Invite / Remove Members ──

  test("invite and remove member", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Invite " + Date.now(),
      visibility: "private",
    }) as { id: bigint };

    const { items: members } = await cc.org.listMembers({ orgSlug: TEST_ORG_SLUG }) as {
      items: { userId: bigint; user?: { email: string } }[];
    };
    const admin = members?.find((m) => m.user?.email === SECOND_USER.email);
    expect(admin?.userId, `seed second user ${SECOND_USER.email} must be an org member`).toBeTruthy();

    await cc.channel.inviteChannelMembers({
      orgSlug: TEST_ORG_SLUG,
      id: channel.id,
      userIds: [admin!.userId],
    });

    const adminToken = await api.loginAs(SECOND_USER.email, SECOND_USER.password);
    const adminCc = api.connectWithToken(adminToken);
    const detail = await adminCc.channel.getChannel({
      orgSlug: TEST_ORG_SLUG,
      id: channel.id,
    });
    expect(detail).toBeTruthy();

    await api.login();
    await cc.channel.removeChannelMember({
      orgSlug: TEST_ORG_SLUG,
      id: channel.id,
      userId: admin!.userId,
    });

    await expect(
      adminCc.channel.getChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id })
    ).rejects.toMatchObject({ status: 403 });

    await api.login();
    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  test("non-creator cannot remove members", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E NoRemove " + Date.now(),
      visibility: "public",
    }) as { id: bigint };

    const { items: chMembers } = await cc.channel.listChannelMembers({
      orgSlug: TEST_ORG_SLUG,
      id: channel.id,
    }) as { items: { userId: bigint }[] };
    const creatorId = chMembers?.[0]?.userId;
    expect(creatorId, "channel must have a creator listed in its member roster").toBeTruthy();

    const adminToken = await api.loginAs(SECOND_USER.email, SECOND_USER.password);
    const adminCc = api.connectWithToken(adminToken);
    await adminCc.channel.joinChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });

    // Admin (joined but not creator) tries to remove creator — should fail.
    await expect(
      adminCc.channel.removeChannelMember({
        orgSlug: TEST_ORG_SLUG,
        id: channel.id,
        userId: creatorId,
      })
    ).rejects.toMatchObject({ status: 403 });

    await api.login();
    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  // ── Messages in Private Channel ──

  test("non-member cannot send message to private channel", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E PrivMsg " + Date.now(),
      visibility: "private",
    }) as { id: bigint };

    const adminToken = await api.loginAs(SECOND_USER.email, SECOND_USER.password);
    const adminCc = api.connectWithToken(adminToken);
    await expect(
      adminCc.channel.sendChannelMessage({
        orgSlug: TEST_ORG_SLUG,
        channelId: channel.id,
        contentJson: JSON.stringify(textContent("should fail")),
      })
    ).rejects.toMatchObject({ status: 403 });

    await api.login();
    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  test("member can send and read messages", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E MemberMsg " + Date.now(),
    }) as { id: bigint };

    const sent = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: channel.id,
      contentJson: JSON.stringify(textContent("Hello from E2E")),
    }) as { id: bigint; body: string };
    expect(sent.body).toBe("Hello from E2E");

    const list = await cc.channel.listChannelMessages({
      orgSlug: TEST_ORG_SLUG,
      channelId: channel.id,
    }) as { items: unknown[] };
    expect(list.items.length).toBeGreaterThanOrEqual(1);

    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  // ── Edit / Delete Messages ──

  test("edit and delete own message", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E EditDel " + Date.now(),
    }) as { id: bigint };

    const message = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: channel.id,
      contentJson: JSON.stringify(textContent("original")),
    }) as { id: bigint };

    const edited = await cc.channel.editChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: channel.id,
      messageId: message.id,
      contentJson: JSON.stringify(textContent("edited")),
    }) as { body: string };
    expect(edited.body).toBe("edited");

    await cc.channel.deleteChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: channel.id,
      messageId: message.id,
    });

    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  // ── Unread Counts & Mark Read ──

  test("unread counts and mark read", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Unread " + Date.now(),
      visibility: "public",
    }) as { id: bigint };

    const adminToken = await api.loginAs(SECOND_USER.email, SECOND_USER.password);
    const adminCc = api.connectWithToken(adminToken);
    await adminCc.channel.joinChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });

    await api.login();
    const m1 = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: channel.id,
      contentJson: JSON.stringify(textContent("msg1")),
    }) as { id: bigint };
    await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: channel.id,
      contentJson: JSON.stringify(textContent("msg2")),
    });

    const counts = await adminCc.channel.getChannelUnreadCounts({ orgSlug: TEST_ORG_SLUG }) as {
      unread: Record<string, bigint>;
    };
    const count = Number(counts.unread?.[String(channel.id)] ?? BigInt(0));
    expect(count).toBeGreaterThanOrEqual(2);

    await adminCc.channel.markChannelRead({
      orgSlug: TEST_ORG_SLUG,
      channelId: channel.id,
      messageId: m1.id,
    });

    const counts2 = await adminCc.channel.getChannelUnreadCounts({ orgSlug: TEST_ORG_SLUG }) as {
      unread: Record<string, bigint>;
    };
    const count2 = Number(counts2.unread?.[String(channel.id)] ?? BigInt(0));
    expect(count2).toBeLessThan(count);

    await api.login();
    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });

  // ── ListChannels returns visibility + membership ──

  test("list channels includes visibility and is_member", async ({ api }) => {
    const cc = await api.connect();
    const name = "E2E ListVis " + Date.now();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name,
      visibility: "public",
    }) as { id: bigint };

    const { items } = await cc.channel.listChannels({ orgSlug: TEST_ORG_SLUG }) as {
      items: { id: bigint; visibility: string; isMember: boolean; memberCount: bigint }[];
    };
    const found = items?.find((c) => c.id === channel.id);
    expect(found).toBeTruthy();
    expect(found?.visibility).toBe("public");
    expect(found?.isMember).toBe(true);
    expect(typeof Number(found?.memberCount ?? BigInt(0))).toBe("number");

    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
  });
});
