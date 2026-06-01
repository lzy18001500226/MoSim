import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  resolveDecisionVerifierSid,
  verifyRequiredDecisions,
} from "./decision-verifier.js";
import {
  activateWorkflowSession,
  emitEvent,
  readEvents,
  setActiveSession,
} from "./events.js";

describe("required decision verifier", () => {
  let projectDir: string;

  beforeEach(() => {
    projectDir = mkdtempSync(join(tmpdir(), "oma-decision-verifier-"));
  });

  afterEach(() => {
    rmSync(projectDir, { recursive: true, force: true });
  });

  it("passes when the required decision.made subject exists", async () => {
    activateWorkflowSession({
      projectDir,
      sid: "oma-ultra",
      workflow: "ultrawork",
    });
    emitEvent(projectDir, "oma-ultra", {
      kind: "decision.made",
      payload: {
        subject: "ultrawork.plan-approved",
        decision: "Proceed with the scoped plan.",
        rationale: "PLAN_GATE checklist passed with user approval.",
      },
    });

    const result = await verifyRequiredDecisions({
      projectDir,
      sid: "oma-ultra",
      workflow: "ultrawork",
      checkpoint: "plan-approved",
    });

    expect(result.ok).toBe(true);
    expect(result.missing).toEqual([]);
  });

  it("emits decision.missing when a required decision is absent", async () => {
    activateWorkflowSession({
      projectDir,
      sid: "oma-work",
      workflow: "work",
    });

    const result = await verifyRequiredDecisions({
      projectDir,
      sid: "oma-work",
      workflow: "work",
      checkpoint: "remediation-choice",
    });

    expect(result.ok).toBe(false);
    expect(result.missing).toMatchObject([
      { subject: "work.remediation-choice" },
    ]);
    const missingEvent = readEvents(projectDir, "oma-work").find(
      (event) => event.kind === "decision.missing",
    );
    expect(missingEvent).toMatchObject({
      kind: "decision.missing",
      payload: {
        workflow: "work",
        checkpoint: "remediation-choice",
      },
    });
  });

  it("can resolve the active sid by category", () => {
    activateWorkflowSession({
      projectDir,
      sid: "oma-main",
      workflow: "orchestrate",
    });
    setActiveSession(projectDir, "qa", "oma-qa");

    expect(resolveDecisionVerifierSid({ projectDir, category: "qa" })).toBe(
      "oma-qa",
    );
    expect(resolveDecisionVerifierSid({ projectDir })).toBe("oma-main");
  });

  it("rejects unknown checkpoints", async () => {
    await expect(
      verifyRequiredDecisions({
        projectDir,
        sid: "oma-unknown",
        workflow: "ultrawork",
        checkpoint: "unknown",
      }),
    ).rejects.toThrow(/Unknown required decision checkpoint/);
  });
});
