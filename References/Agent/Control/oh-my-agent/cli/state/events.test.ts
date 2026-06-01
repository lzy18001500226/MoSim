import {
  existsSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  activateWorkflowSession,
  deriveMeta,
  emitEvent,
  emitEventWithMemory,
  eventsPath,
  getActiveSid,
  indexPath,
  metaPath,
  readEvents,
  readIndex,
  retryObservePath,
  setActiveSession,
  sortEvents,
} from "./events.js";

describe("L1 state events", () => {
  let projectDir: string;

  beforeEach(() => {
    projectDir = mkdtempSync(join(tmpdir(), "oma-l1-events-"));
  });

  afterEach(() => {
    rmSync(projectDir, { recursive: true, force: true });
  });

  it("sorts events by timestamp and then eventId", () => {
    const events = [
      {
        eventId: "b",
        ts: "2026-05-25T00:00:00.000Z",
        sid: "sid-1",
        kind: "workflow.phase",
        writerPid: 1,
      },
      {
        eventId: "a",
        ts: "2026-05-25T00:00:00.000Z",
        sid: "sid-1",
        kind: "session.created",
        writerPid: 1,
      },
      {
        eventId: "c",
        ts: "2026-05-25T00:00:01.000Z",
        sid: "sid-1",
        kind: "session.ended",
        writerPid: 1,
      },
    ];

    expect(sortEvents(events).map((event) => event.eventId)).toEqual([
      "a",
      "b",
      "c",
    ]);
  });

  it("appends durable JSONL events and reads them in canonical order", () => {
    emitEvent(projectDir, "oma-test", {
      eventId: "002",
      ts: "2026-05-25T00:00:01.000Z",
      kind: "workflow.phase",
      payload: { phase: "implement" },
    });
    emitEvent(projectDir, "oma-test", {
      eventId: "001",
      ts: "2026-05-25T00:00:00.000Z",
      kind: "session.created",
      vendor: "codex",
      vendorSid: "codex-1",
      payload: { workflow: "work", category: "main" },
    });

    const rawLines = readFileSync(eventsPath(projectDir, "oma-test"), "utf-8")
      .trim()
      .split("\n");
    expect(rawLines).toHaveLength(2);

    const events = readEvents(projectDir, "oma-test");
    expect(events.map((event) => event.eventId)).toEqual(["001", "002"]);
    expect(events[0]).toMatchObject({
      eventId: "001",
      sid: "oma-test",
      kind: "session.created",
      vendor: "codex",
      vendorSid: "codex-1",
    });
  });

  it("derives session metadata from event history", () => {
    const meta = deriveMeta("oma-test", [
      {
        eventId: "001",
        ts: "2026-05-25T00:00:00.000Z",
        sid: "oma-test",
        kind: "session.created",
        writerPid: 1,
        payload: { workflow: "ultrawork", category: "main" },
      },
      {
        eventId: "002",
        ts: "2026-05-25T00:00:01.000Z",
        sid: "oma-test",
        kind: "workflow.phase",
        writerPid: 1,
        payload: { phase: "review" },
      },
      {
        eventId: "003",
        ts: "2026-05-25T00:00:02.000Z",
        sid: "oma-test",
        kind: "gate.passed",
        writerPid: 1,
        payload: { gate: "peer-review", reviewer: "qa" },
      },
      {
        eventId: "004",
        ts: "2026-05-25T00:00:03.000Z",
        sid: "oma-test",
        kind: "session.ended",
        writerPid: 1,
        payload: { status: "failed" },
      },
    ]);

    expect(meta).toMatchObject({
      sid: "oma-test",
      workflow: "ultrawork",
      category: "main",
      status: "failed",
      currentPhase: "review",
    });
    expect(meta.gatesPassedBy).toEqual([
      {
        ts: "2026-05-25T00:00:02.000Z",
        gate: "peer-review",
        reviewer: "qa",
      },
    ]);
  });

  it("maintains active session index and writes meta on session activation", () => {
    activateWorkflowSession({
      projectDir,
      sid: "oma-active",
      workflow: "orchestrate",
      vendor: "claude",
      vendorSid: "claude-1",
    });
    setActiveSession(projectDir, "research", "oma-research");

    const index = readIndex(projectDir);
    expect(getActiveSid(index)).toBe("oma-active");
    expect(index.active).toEqual({
      main: "oma-active",
      research: "oma-research",
    });
    expect(existsSync(indexPath(projectDir))).toBe(true);

    const meta = JSON.parse(
      readFileSync(metaPath(projectDir, "oma-active"), "utf-8"),
    );
    expect(meta).toMatchObject({
      sid: "oma-active",
      workflow: "orchestrate",
      category: "main",
      status: "active",
    });
  });

  it("ignores malformed JSONL lines when reading events", () => {
    const path = eventsPath(projectDir, "oma-bad");
    emitEvent(projectDir, "oma-bad", {
      eventId: "001",
      ts: "2026-05-25T00:00:00.000Z",
      kind: "session.created",
    });
    writeFileSync(path, "{not json}\n", { flag: "a" });

    expect(readEvents(projectDir, "oma-bad")).toHaveLength(1);
  });

  it("observes semantic events through the optional memory provider", async () => {
    const observed: unknown[] = [];
    const event = await emitEventWithMemory(
      projectDir,
      "oma-memory",
      {
        kind: "decision.made",
        payload: { subject: "work.remediation-choice" },
      },
      {
        name: "agentmemory",
        async status() {
          return { provider: "agentmemory", reachable: true };
        },
        async observe(payload) {
          observed.push(payload);
          return true;
        },
      },
    );

    expect(event.kind).toBe("decision.made");
    expect(observed).toEqual([
      {
        sessionId: "oma-memory",
        content: `${JSON.stringify(event)}\n`,
        source: "oma-workflow",
      },
    ]);
    expect(existsSync(retryObservePath(projectDir))).toBe(false);
  });

  it("queues semantic event retry when memory observe fails", async () => {
    const event = await emitEventWithMemory(
      projectDir,
      "oma-retry",
      {
        eventId: "retry-event",
        ts: "2026-05-25T00:00:00.000Z",
        kind: "gate.passed",
      },
      {
        name: "agentmemory",
        async status() {
          return { provider: "agentmemory", reachable: false };
        },
        async observe() {
          return false;
        },
      },
    );

    expect(readFileSync(retryObservePath(projectDir), "utf-8")).toBe(
      `${JSON.stringify(event)}\n`,
    );
  });

  it("does not observe non-semantic events", async () => {
    let calls = 0;
    await emitEventWithMemory(
      projectDir,
      "oma-boundary",
      {
        kind: "boundary",
      },
      {
        name: "agentmemory",
        async status() {
          return { provider: "agentmemory", reachable: true };
        },
        async observe() {
          calls += 1;
          return true;
        },
      },
    );

    expect(calls).toBe(0);
    expect(existsSync(retryObservePath(projectDir))).toBe(false);
  });
});
