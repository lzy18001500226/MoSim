// Migrated R5+: Connect-RPC only (no REST middle layer).
//
// Realtime channel-message broadcast verification. R5-11 moved the
// transport from `/ws/events` (WebSocket) to a Connect server-stream
// (EventsService.Subscribe). The production browser client consumes
// the stream via wasm (see clients/core/crates/api-client/src/
// connect_stream_wasm.rs); this Node spec opens the same Connect
// server-stream directly and asserts the backend fans the message
// out to every subscriber.
//
// We intentionally do not drive the channels page UI here — that path
// is exercised by channel-detail / channel-ui specs. The contract this
// spec owns is the wire-level event broadcast.
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { streamConnect } from "../../helpers/connect-stream";
import {
  SubscribeRequestSchema,
  EventSchema,
} from "../../../../../proto/gen/ts/events/v1/events_pb";

test.describe("Channel realtime delivery", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("posting a message broadcasts channel:message to a Connect subscriber", async ({ api }) => {
    const cc = await api.connect();
    const token = api.getToken();
    if (!token) throw new Error("api fixture has no token after connect()");

    // Pick any channel the test user is a member of. The dev seed leaves
    // multiple #-channels in dev-org, so this is normally non-empty;
    // create one if the slate is bare (e.g., post-reset) so we never silently skip.
    const listed = (await cc.channel.listChannels({ orgSlug: TEST_ORG_SLUG })) as {
      items: Array<{ id: bigint | number }>;
    };
    let channelId: bigint | number;
    let createdId: bigint | number | undefined;
    if (listed.items.length) {
      channelId = listed.items[0].id;
    } else {
      const ch = await cc.channel.createChannel({
        orgSlug: TEST_ORG_SLUG,
        name: "E2E Realtime Seed " + Date.now(),
      }) as { id: bigint | number };
      channelId = ch.id;
      createdId = ch.id;
    }

    const marker = `E2E-REALTIME-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
    const ctrl = new AbortController();
    let seen = false;

    // Consume the stream in the background — break out the moment we see
    // a channel:message frame that carries our unique marker.
    const drain = (async () => {
      try {
        for await (const ev of streamConnect(
          "proto.events.v1.EventsService",
          "Subscribe",
          SubscribeRequestSchema,
          EventSchema,
          { orgSlug: TEST_ORG_SLUG },
          { token, signal: ctrl.signal },
        )) {
          if (ev.type === "channel:message" && ev.dataJson.includes(marker)) {
            seen = true;
            ctrl.abort();
            return;
          }
        }
      } catch {
        /* abort or graceful close */
      }
    })();

    // Brief settle window so the backend hub registers the subscriber
    // before we publish. Without this the message can fan out before
    // the stream's subscribe call has been recorded → flaky miss.
    await new Promise((r) => setTimeout(r, 500));

    await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId,
      source: marker,
    });

    const winner = await Promise.race([
      drain.then(() => "drained" as const),
      new Promise<"timeout">((r) => setTimeout(() => r("timeout"), 10_000)),
    ]);
    ctrl.abort();
    expect(winner, `timed out waiting for channel:message with marker ${marker}`).toBe("drained");
    expect(seen).toBe(true);

    if (createdId !== undefined) {
      await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: createdId }).catch(() => undefined);
    }
  });
});
