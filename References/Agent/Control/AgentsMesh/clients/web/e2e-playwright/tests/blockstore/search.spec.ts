// Migrated R5+: Connect-RPC only (no REST middle layer).
import { randomUUID } from "crypto";

import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Verifies the semantic search path end-to-end inside a pristine workspace:
//   1. Create two paragraph blocks with very different content
//   2. Wait for async embeddings (HashEmbedder in dev) to flush
//   3. Search for distinctive text in each — expect the right block to rank
//      above the other.
//
// Using `isolatedWorkspace` means the corpus contains only our two blocks,
// so top_k=10 is plenty and rank-based assertions stay stable. The earlier
// version of this spec shared the default workspace and accumulated
// hundreds of stale kiwi/rocket blocks over many runs, eventually pushing
// our freshly-written block out of the top hits.
test("semantic search ranks paragraphs by query relevance", async ({
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;

  const kiwiMarker = `kiwi-fruit-unique-${Date.now()}`;
  const rocketMarker = `rocket-engine-unique-${Date.now()}`;
  const kiwiID = randomUUID();
  const rocketID = randomUUID();

  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({
          id: kiwiID,
          type: "paragraph",
          data: { text: kiwiMarker },
          text: `${kiwiMarker} ripe green fruit with fuzzy skin from new zealand orchard`,
        }),
      },
      {
        op: "addRef",
        payloadJson: JSON.stringify({ from: rootID, to: kiwiID, rel: "nest", order_key: `zzz${Date.now().toString(36)}1` }),
      },
      {
        op: "createBlock",
        payloadJson: JSON.stringify({
          id: rocketID,
          type: "paragraph",
          data: { text: rocketMarker },
          text: `${rocketMarker} liquid hydrogen thrust chamber combustion nozzle stage`,
        }),
      },
      {
        op: "addRef",
        payloadJson: JSON.stringify({ from: rootID, to: rocketID, rel: "nest", order_key: `zzz${Date.now().toString(36)}2` }),
      },
    ],
    idempotencyKey: `e2e-search-${kiwiID}`,
  });

  // Wait until both IDs are indexed. Embeddings ride a 256-buffered channel;
  // on an idle dev stack that normally flushes within a couple of ticks.
  await expect
    .poll(
      async () => {
        const res = await cc.blockstore.semanticSearch({
          orgSlug,
          workspaceId: workspaceID,
          query: "kiwi fruit orchard zealand",
          topK: 20,
        }) as { hits: Array<{ blockId: string }> };
        return res.hits.some((h) => h.blockId === kiwiID);
      },
      { timeout: 15_000, message: "kiwi block should be indexed" },
    )
    .toBe(true);

  // Ranking check: the fruit query should surface kiwi strictly above rocket.
  const kiwiHits = await cc.blockstore.semanticSearch({
    orgSlug,
    workspaceId: workspaceID,
    query: "kiwi fruit orchard zealand",
    topK: 10,
  }) as { hits: Array<{ blockId: string; score: number }> };
  const kiwiRank = kiwiHits.hits.findIndex((h) => h.blockId === kiwiID);
  const rocketRankInKiwiQuery = kiwiHits.hits.findIndex((h) => h.blockId === rocketID);
  expect(kiwiRank).toBeGreaterThanOrEqual(0);
  if (rocketRankInKiwiQuery >= 0) expect(kiwiRank).toBeLessThan(rocketRankInKiwiQuery);

  const rocketHits = await cc.blockstore.semanticSearch({
    orgSlug,
    workspaceId: workspaceID,
    query: "rocket thrust combustion nozzle engine",
    topK: 10,
  }) as { hits: Array<{ blockId: string; score: number }> };
  const rocketRank = rocketHits.hits.findIndex((h) => h.blockId === rocketID);
  const kiwiRankInRocketQuery = rocketHits.hits.findIndex((h) => h.blockId === kiwiID);
  expect(rocketRank).toBeGreaterThanOrEqual(0);
  if (kiwiRankInRocketQuery >= 0) expect(rocketRank).toBeLessThan(kiwiRankInRocketQuery);
});
