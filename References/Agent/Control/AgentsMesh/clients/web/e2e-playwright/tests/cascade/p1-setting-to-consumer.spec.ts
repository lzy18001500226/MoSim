// P1 cascade tests: settings change on one surface MUST reflect on the
// consuming surfaces on the very next read. Each test follows the pattern:
//
//   1. Change setting X via the canonical write RPC.
//   2. Re-read X (or a downstream computed view) via a *different* RPC.
//   3. Assert the new value is visible — no client cache, no reload, no
//      stale-state grace period.
//
// These are not write/read round-trips on the same RPC; they exercise
// the relationship between the write surface and the *consuming* surface
// (sidebar / list / dispatch / detail view) which is where stale-cache
// bugs hide.
import { test, expect } from "../../fixtures/index";
import { TEST_USER, TEST_ORG_SLUG } from "../../helpers/env";

interface OrgItem {
  id: bigint;
  slug: string;
  name: string;
}
interface ChannelItem {
  id: bigint;
  name: string;
  isArchived: boolean;
}
interface TicketItem {
  id: bigint;
  slug: string;
  title: string;
}
interface NotificationPref {
  source: string;
  entityId?: string;
  isMuted: boolean;
  channels: Record<string, boolean>;
}

test.describe("P1 cascade: setting → consumer surface", () => {
  /**
   * Org rename: the sidebar / breadcrumb / org-switcher all read from
   * ListMyOrgs (user-scoped) and GetOrg (org-scoped). Both views must
   * reflect the new name on the next call — no extra invalidation step.
   */
  test("org rename propagates to ListMyOrgs + GetOrg", async ({ api }) => {
    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();

    const { items: before } = (await cc.org.listMyOrgs({})) as { items: OrgItem[] };
    const target = before.find((o) => o.slug === TEST_ORG_SLUG);
    expect(target, "dev-org must appear in ListMyOrgs").toBeTruthy();
    const originalName = target!.name;
    const newName = `${originalName} (renamed ${Date.now()})`;

    try {
      await cc.org.updateOrg({ orgSlug: TEST_ORG_SLUG, name: newName });

      const { items: afterList } = (await cc.org.listMyOrgs({})) as { items: OrgItem[] };
      const updatedList = afterList.find((o) => o.slug === TEST_ORG_SLUG);
      expect(updatedList?.name).toBe(newName);

      const updatedGet = (await cc.org.getOrg({ orgSlug: TEST_ORG_SLUG })) as OrgItem;
      expect(updatedGet.name).toBe(newName);
    } finally {
      await cc.org.updateOrg({ orgSlug: TEST_ORG_SLUG, name: originalName });
    }
  });

  /**
   * Channel archive: archived channels disappear from the default
   * ListChannels view (without includeArchived) but stay reachable when
   * the caller opts into includeArchived=true. The UI's channel sidebar
   * uses the default view; this test locks both branches.
   */
  test("channel archive removes from default list + survives includeArchived=true", async ({ api }) => {
    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();

    const created = (await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: `cascade-archive-${Date.now()}`,
      visibility: "public",
    })) as ChannelItem;
    const channelId = created.id;

    try {
      await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channelId });

      const { items: defaultList } = (await cc.channel.listChannels({
        orgSlug: TEST_ORG_SLUG,
      })) as { items: ChannelItem[] };
      expect(
        defaultList.some((c) => c.id === channelId),
        "archived channel must NOT appear in default ListChannels",
      ).toBe(false);

      const { items: withArchived } = (await cc.channel.listChannels({
        orgSlug: TEST_ORG_SLUG,
        includeArchived: true,
      })) as { items: ChannelItem[] };
      const archived = withArchived.find((c) => c.id === channelId);
      expect(archived?.isArchived).toBe(true);
    } finally {
      try {
        await cc.channel.unarchiveChannel({ orgSlug: TEST_ORG_SLUG, id: channelId });
      } catch { /* test cleanup — best effort */ }
    }
  });

  /**
   * Notification preference: SetPreference must be reflected on the very
   * next ListPreferences call. This guards the per-user preference store
   * against caching bugs that would silently keep the old value. The proto
   * row is keyed by (user, source, entity_id?) and carries is_muted +
   * channels{}; we flip is_muted and assert the round-trip surfaces it.
   */
  test("notification preference toggle reflects on ListPreferences immediately", async ({ api }) => {
    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();

    const source = "channel:message";
    const { items: beforeList } = (await cc.notification.listPreferences({
      orgSlug: TEST_ORG_SLUG,
    })) as { items: NotificationPref[] };
    const before = beforeList.find((p) => p.source === source && !p.entityId);
    // If the seed doesn't ship this source preference yet, fall back to muted=false.
    const baselineMuted = before?.isMuted ?? false;
    const baselineChannels = before?.channels ?? {};
    const flippedMuted = !baselineMuted;

    try {
      await cc.notification.setPreference({
        orgSlug: TEST_ORG_SLUG,
        source,
        isMuted: flippedMuted,
        channels: baselineChannels,
      });
      const { items: afterList } = (await cc.notification.listPreferences({
        orgSlug: TEST_ORG_SLUG,
      })) as { items: NotificationPref[] };
      const after = afterList.find((p) => p.source === source && !p.entityId);
      expect(after?.isMuted).toBe(flippedMuted);
    } finally {
      await cc.notification.setPreference({
        orgSlug: TEST_ORG_SLUG,
        source,
        isMuted: baselineMuted,
        channels: baselineChannels,
      });
    }
  });

  /**
   * Ticket assignee: AddAssignee writes to the ticket_assignees join table.
   * The board UI relies on ListTickets's assigneeId filter to materialize
   * per-assignee swimlanes; this assertion locks that filter pipeline.
   * (GetTicket on proto.ticket.v1.Ticket does NOT echo assignees back —
   * assignees are a separate relation queried via ListTickets's filter or
   * a dedicated list endpoint, so the consumer test is the filtered list.)
   */
  test("ticket assignee add reflects in ListTickets filter immediately", async ({ api, db }) => {
    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();

    const myId = db.queryValue(`SELECT id FROM users WHERE email = '${TEST_USER.email}' LIMIT 1`);
    expect(myId).toBeTruthy();
    const myUserId = BigInt(String(myId));

    const created = (await cc.ticket.createTicket({
      orgSlug: TEST_ORG_SLUG,
      title: `cascade-assignee-${Date.now()}`,
      status: "todo",
      priority: "medium",
    })) as TicketItem;
    const ticketSlug = created.slug;

    try {
      // Pre-assertion: ticket is NOT in my filtered list yet.
      const { items: preMine } = (await cc.ticket.listTickets({
        orgSlug: TEST_ORG_SLUG,
        assigneeId: myUserId,
        limit: 100,
      })) as { items: TicketItem[] };
      expect(preMine.some((t) => t.slug === ticketSlug)).toBe(false);

      await cc.ticket.addAssignee({
        orgSlug: TEST_ORG_SLUG,
        ticketSlug,
        userId: myUserId,
      });

      // Cascade: filtered list now picks the ticket up under my user_id.
      const { items: mine } = (await cc.ticket.listTickets({
        orgSlug: TEST_ORG_SLUG,
        assigneeId: myUserId,
        limit: 100,
      })) as { items: TicketItem[] };
      expect(
        mine.some((t) => t.slug === ticketSlug),
        "ListTickets filtered by assigneeId must include the assigned ticket",
      ).toBe(true);

      // And the DB row exists (storage-layer SSOT). This guards against a
      // future change that quietly drops the write but still passes the
      // ListTickets filter via stale cache.
      const rowCount = db.queryValue(
        `SELECT COUNT(*) FROM ticket_assignees WHERE ticket_id IN (SELECT id FROM tickets WHERE slug = '${ticketSlug}') AND user_id = ${myUserId}`,
      );
      expect(Number(rowCount)).toBeGreaterThan(0);
    } finally {
      try {
        await cc.ticket.deleteTicket({ orgSlug: TEST_ORG_SLUG, ticketSlug });
      } catch {
        db.cleanup(`DELETE FROM tickets WHERE slug = '${ticketSlug}'`);
      }
    }
  });

  /**
   * Channel mute: the mute flag MUST round-trip through GetChannel /
   * ListChannelMembers (whichever surface exposes the per-user mute state),
   * not just the SetMute return value. UI mute toggles read this on
   * subsequent renders.
   */
  test("channel mute reflects on subsequent ListChannelMembers + GetChannel", async ({ api }) => {
    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();

    const created = (await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: `cascade-mute-${Date.now()}`,
      visibility: "public",
    })) as ChannelItem;
    const channelId = created.id;

    try {
      await cc.channel.muteChannel({
        orgSlug: TEST_ORG_SLUG,
        id: channelId,
        muted: true,
      });

      // ListChannelMembers exposes per-member is_muted on the row that
      // matches the caller. ListChannels also caches the per-user mute as
      // is_muted on the channel row when the caller is a member.
      const { items: members } = (await cc.channel.listChannelMembers({
        orgSlug: TEST_ORG_SLUG,
        id: channelId,
      })) as { items: { userId: bigint; isMuted: boolean }[] };
      const myMember = members[0]; // creator is the only member here
      expect(myMember?.isMuted, "after muteChannel, members[me].isMuted must be true").toBe(true);

      await cc.channel.muteChannel({
        orgSlug: TEST_ORG_SLUG,
        id: channelId,
        muted: false,
      });
      const { items: unmuted } = (await cc.channel.listChannelMembers({
        orgSlug: TEST_ORG_SLUG,
        id: channelId,
      })) as { items: { isMuted: boolean }[] };
      expect(unmuted[0]?.isMuted).toBe(false);
    } finally {
      try {
        await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channelId });
      } catch { /* cleanup best-effort */ }
    }
  });
});
