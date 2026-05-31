// Migrated R5+: Connect-RPC only (no REST middle layer).
//
// This file historically asserted the REST JSON envelope shapes (e.g. `tickets`
// vs `items` key naming, `pod` wrapper, list pagination keys). The REST
// envelopes are gone, but the same shape contracts now ride on the Connect
// proto messages — list responses still expose `total`/`limit`/`offset`,
// CreatePod still returns the `pod` field, loop runs list still paginates.
// Re-validate those at the Connect layer here so a regression on the proto
// descriptor (e.g., someone renaming `total` to `count` on the wire) gets
// caught at the e2e seam.
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Backend wrapper envelope contracts", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("ticket list keeps total/limit/offset", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.ticket.listTickets({ orgSlug: TEST_ORG_SLUG }) as {
      items: unknown[];
      total?: number | bigint;
      limit?: number;
      offset?: number;
    };
    expect(Array.isArray(res.items)).toBe(true);
    // Pagination fields exist on the proto descriptor even when zero. The
    // contract is: the response is shaped { items, total, limit, offset }.
    expect(typeof res.total).toMatch(/number|bigint/);
    expect(typeof res.limit).toBe("number");
    expect(typeof res.offset).toBe("number");
  });

  test("pod create response carries pod envelope", async ({ api }) => {
    const cc = await api.connect();
    const runners = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as {
      items: { id: bigint }[];
    };
    expect(runners.items.length, "dev env must have an online runner").toBeGreaterThan(0);
    const agents = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as {
      builtinAgents: { slug: string }[];
    };
    expect(agents.builtinAgents.length, "dev env must have a builtin agent").toBeGreaterThan(0);

    const resp = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      runnerId: runners.items[0].id,
      agentSlug: agents.builtinAgents[0].slug,
    }) as { pod?: { podKey?: string } };
    // The legacy REST `{ "pod": {...} }` envelope is now the proto Pod field.
    expect(resp.pod).toBeDefined();
    expect(typeof resp.pod?.podKey).toBe("string");

    // Cleanup
    if (resp.pod?.podKey) {
      await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey: resp.pod.podKey }).catch(() => {});
    }
  });

  test("loop runs list keeps pagination shape", async ({ api }) => {
    const cc = await api.connect();
    // Seed a loop if the org has none so we always exercise the runs envelope.
    let loops = await cc.loop.listLoops({ orgSlug: TEST_ORG_SLUG }) as {
      items: { slug: string }[];
    };
    let createdSlug: string | undefined;
    if (!loops.items?.length) {
      const created = await cc.loop.createLoop({
        orgSlug: TEST_ORG_SLUG,
        name: "E2E LoopRuns Envelope " + Date.now(),
        agentSlug: "claude-code",
        promptTemplate: "noop",
      }) as { slug: string };
      createdSlug = created.slug;
      loops = { items: [{ slug: created.slug }] };
    }
    const runs = await cc.loop.listRuns({
      orgSlug: TEST_ORG_SLUG,
      loopSlug: loops.items[0].slug,
    }) as { items: unknown[]; total?: number | bigint; limit?: number; offset?: number };
    expect(Array.isArray(runs.items)).toBe(true);
    expect(typeof runs.total).toMatch(/number|bigint/);
    expect(typeof runs.limit).toBe("number");
    expect(typeof runs.offset).toBe("number");

    if (createdSlug) {
      await cc.loop.deleteLoop({ orgSlug: TEST_ORG_SLUG, loopSlug: createdSlug }).catch(() => undefined);
    }
  });
});
