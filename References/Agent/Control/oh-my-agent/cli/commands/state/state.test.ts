import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  activateWorkflowSession,
  emitEvent,
  readIndex,
  sessionDir,
} from "../../state/events.js";
import {
  activateStateSession,
  collectState,
  parseOlderThan,
  purgeStateSessions,
  renderPurgeResult,
  renderSessionView,
  renderStateList,
  viewSession,
} from "./state.js";

describe("state command helpers", () => {
  let projectDir: string;

  beforeEach(() => {
    projectDir = mkdtempSync(join(tmpdir(), "oma-state-command-"));
  });

  afterEach(() => {
    rmSync(projectDir, { recursive: true, force: true });
  });

  it("collects sessions with active markers", () => {
    activateWorkflowSession({
      projectDir,
      sid: "oma-main",
      workflow: "work",
      vendor: "codex",
      vendorSid: "codex-1",
    });
    emitEvent(projectDir, "oma-main", {
      eventId: "phase-1",
      ts: "2026-05-25T00:00:01.000Z",
      kind: "workflow.phase",
      payload: { phase: "implement" },
    });
    activateStateSession("oma-main", "qa", projectDir);

    const state = collectState(projectDir);
    expect(state.index.active).toMatchObject({
      main: "oma-main",
      qa: "oma-main",
    });
    expect(state.sessions).toHaveLength(1);
    expect(state.sessions[0]).toMatchObject({
      sid: "oma-main",
      workflow: "work",
      currentPhase: "implement",
    });
  });

  it("renders list and session views without requiring color-aware assertions", () => {
    activateWorkflowSession({
      projectDir,
      sid: "oma-view",
      workflow: "debug",
    });

    const list = renderStateList(collectState(projectDir));
    expect(list).toContain("OMA state sessions");
    expect(list).toContain("oma-view");
    expect(list).toContain("debug");

    const session = viewSession("oma-view", projectDir);
    const detail = renderSessionView("oma-view", session.meta, session.events);
    expect(detail).toContain("OMA session oma-view");
    expect(detail).toContain("workflow: debug");
    expect(detail).toContain("session.created");
  });

  it("renders decisions and missing decisions in session detail", () => {
    activateWorkflowSession({
      projectDir,
      sid: "oma-decisions",
      workflow: "work",
    });
    emitEvent(projectDir, "oma-decisions", {
      kind: "decision.made",
      payload: {
        subject: "work.remediation-choice",
        decision: "Fix the critical issue.",
        rationale: "QA confirmed it blocks completion.",
      },
    });
    emitEvent(projectDir, "oma-decisions", {
      kind: "decision.missing",
      payload: {
        workflow: "work",
        checkpoint: "remediation-choice",
      },
    });

    const session = viewSession("oma-decisions", projectDir);
    const detail = renderSessionView(
      "oma-decisions",
      session.meta,
      session.events,
    );
    expect(detail).toContain("Decisions");
    expect(detail).toContain("work.remediation-choice");
    expect(detail).toContain("Missing Decisions");
    expect(detail).toContain("work/remediation-choice");
  });

  it("purges inactive sessions older than the explicit threshold", () => {
    emitEvent(projectDir, "oma-old", {
      eventId: "old-created",
      ts: "2026-01-01T00:00:00.000Z",
      kind: "session.created",
      payload: { workflow: "work", category: "main" },
    });
    activateWorkflowSession({
      projectDir,
      sid: "oma-active-old",
      workflow: "debug",
    });
    emitEvent(projectDir, "oma-active-old", {
      eventId: "active-created",
      ts: "2026-01-01T00:00:00.000Z",
      kind: "session.created",
      payload: { workflow: "debug", category: "main" },
    });
    emitEvent(projectDir, "oma-recent", {
      eventId: "recent-created",
      ts: "2026-05-20T00:00:00.000Z",
      kind: "session.created",
      payload: { workflow: "review", category: "main" },
    });

    const result = purgeStateSessions({
      projectDir,
      olderThan: "90d",
      now: new Date("2026-05-26T00:00:00.000Z"),
    });

    expect(result.purged).toEqual(["oma-old"]);
    expect(result.skippedActive).toContain("oma-active-old");
    expect(result.skippedRecent).toContain("oma-recent");
    expect(existsSync(sessionDir(projectDir, "oma-old"))).toBe(false);
    expect(existsSync(sessionDir(projectDir, "oma-active-old"))).toBe(true);
    expect(readIndex(projectDir).active.main).toBe("oma-active-old");
  });

  it("supports purge dry-run and duration parsing", () => {
    emitEvent(projectDir, "oma-old", {
      eventId: "old-created",
      ts: "2026-01-01T00:00:00.000Z",
      kind: "session.created",
      payload: { workflow: "work", category: "main" },
    });

    const result = purgeStateSessions({
      projectDir,
      olderThan: "24h",
      dryRun: true,
      now: new Date("2026-01-03T00:00:00.000Z"),
    });

    expect(parseOlderThan("30m")).toBe(30 * 60 * 1000);
    expect(result.purged).toEqual(["oma-old"]);
    expect(existsSync(sessionDir(projectDir, "oma-old"))).toBe(true);
    expect(renderPurgeResult(result)).toContain("purge preview");
  });
});
