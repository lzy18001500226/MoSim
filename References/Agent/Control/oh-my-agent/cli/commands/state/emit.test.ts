import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  activateWorkflowSession,
  readEvents,
  setActiveSession,
} from "../../state/events.js";
import { parsePayload, resolveEmitSid } from "./emit.js";

describe("emit command helpers", () => {
  let projectDir: string;

  beforeEach(() => {
    projectDir = mkdtempSync(join(tmpdir(), "oma-emit-command-"));
  });

  afterEach(() => {
    rmSync(projectDir, { recursive: true, force: true });
  });

  it("parses JSON object payloads only", () => {
    expect(parsePayload('{"phase":"verify"}')).toEqual({ phase: "verify" });
    expect(() => parsePayload('"bad"')).toThrow(
      /payload must be a JSON object/,
    );
    expect(() => parsePayload("[1,2]")).toThrow(
      /payload must be a JSON object/,
    );
  });

  it("resolves explicit sid before active index lookup", () => {
    setActiveSession(projectDir, "main", "oma-active");
    expect(resolveEmitSid(projectDir, { sid: "oma-explicit" })).toBe(
      "oma-explicit",
    );
  });

  it("resolves active sid by category", () => {
    activateWorkflowSession({
      projectDir,
      sid: "oma-main",
      workflow: "work",
    });
    setActiveSession(projectDir, "qa", "oma-qa");

    expect(resolveEmitSid(projectDir, { category: "qa" })).toBe("oma-qa");
    expect(resolveEmitSid(projectDir, { category: "missing" })).toBe(
      "oma-main",
    );
  });

  it("fails loudly when no sid can be resolved", () => {
    expect(() => resolveEmitSid(projectDir, {})).toThrow(
      /No active L1 session found/,
    );
  });

  it("keeps emitted events on the state library contract", () => {
    activateWorkflowSession({
      projectDir,
      sid: "oma-emit",
      workflow: "debug",
    });
    const sid = resolveEmitSid(projectDir, {});
    expect(sid).toBe("oma-emit");

    const events = readEvents(projectDir, "oma-emit");
    expect(events.map((event) => event.kind)).toEqual(["session.created"]);
  });
});
