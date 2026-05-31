// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Ticket Labels & Relations API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list labels", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.ticket.listLabels({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("create and delete label", async ({ api }) => {
    const cc = await api.connect();
    const label = await cc.ticket.createLabel({
      orgSlug: TEST_ORG_SLUG,
      name: "e2e-label-" + Date.now(),
      color: "#ff0000",
    }) as { id: string | number };
    expect(label.id).toBeTruthy();
    await cc.ticket.deleteLabel({ orgSlug: TEST_ORG_SLUG, id: label.id });
  });

  test("get ticket relations", async ({ api }) => {
    const cc = await api.connect();
    const list = await cc.ticket.listTickets({ orgSlug: TEST_ORG_SLUG, limit: 1 }) as { items: Array<{ slug: string }> };
    if (list.items.length === 0) return;

    const ticketSlug = list.items[0].slug;
    const relations = await cc.ticketRelations.listRelations({
      orgSlug: TEST_ORG_SLUG,
      ticketSlug,
    }) as Record<string, unknown>;
    expect(relations).toBeTruthy();
  });

  test("get ticket commits", async ({ api }) => {
    const cc = await api.connect();
    const list = await cc.ticket.listTickets({ orgSlug: TEST_ORG_SLUG, limit: 1 }) as { items: Array<{ slug: string }> };
    if (list.items.length === 0) return;

    const ticketSlug = list.items[0].slug;
    const commits = await cc.ticketRelations.listCommits({
      orgSlug: TEST_ORG_SLUG,
      ticketSlug,
    }) as Record<string, unknown>;
    expect(commits).toBeTruthy();
  });

  test("delete ticket", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.ticket.createTicket({
      orgSlug: TEST_ORG_SLUG,
      title: "E2E Delete Test",
    }) as { slug: string };
    if (!created.slug) return;

    await cc.ticket.deleteTicket({ orgSlug: TEST_ORG_SLUG, ticketSlug: created.slug });
  });

  // Migrated R5+: the legacy batch-pods REST endpoint (returning pods
  // grouped by ticket_id) collapsed into PodService.ListPodsByTicket on
  // Connect. The single-ticket call is the replacement contract — invoke
  // it once with an existing ticket_id and assert envelope shape; callers
  // that need multiple tickets fan out client-side.
  test("get ticket pods via ListPodsByTicket", async ({ api }) => {
    const cc = await api.connect();
    let list = await cc.ticket.listTickets({ orgSlug: TEST_ORG_SLUG, limit: 1 }) as {
      items: Array<{ id: bigint | number; slug: string }>;
    };
    // Seed a ticket if the org has none so the listPodsByTicket envelope is
    // always exercised.
    let createdSlug: string | undefined;
    if (list.items.length === 0) {
      const t = await cc.ticket.createTicket({
        orgSlug: TEST_ORG_SLUG,
        title: "E2E ListPodsByTicket Seed " + Date.now(),
      }) as { slug: string; id: bigint | number };
      createdSlug = t.slug;
      list = { items: [{ id: t.id, slug: t.slug }] };
    }
    const ticketId = list.items[0].id;
    const res = await cc.pod.listPodsByTicket({
      orgSlug: TEST_ORG_SLUG,
      ticketId,
    }) as { items: unknown[]; total?: number | bigint };
    expect(Array.isArray(res.items)).toBe(true);
    // total may be 0 (no pods linked) — just assert envelope is well-typed.
    expect(typeof res.total).toMatch(/number|bigint/);

    if (createdSlug) {
      await cc.ticket.deleteTicket({ orgSlug: TEST_ORG_SLUG, ticketSlug: createdSlug }).catch(() => undefined);
    }
  });
});
