import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { checkClosure, parseExpectedOutputs } from "./skill-outputs.js";

describe("parseExpectedOutputs", () => {
  it("returns empty when no structured block exists", () => {
    const body = `### Expected outputs\n- A markdown report\n- A JSON summary\n`;
    expect(parseExpectedOutputs(body)).toEqual([]);
  });

  it("parses outputs: list when present", () => {
    const body = `### Expected outputs

Some prose.

\`\`\`yaml
outputs:
  - name: plan
    description: PM breakdown
    artifact: ".agents/results/plan-*.json"
    required: true
  - name: tests
    artifact: "**/test_*.py"
\`\`\`
`;
    const declared = parseExpectedOutputs(body);
    expect(declared).toHaveLength(2);
    expect(declared[0]?.name).toBe("plan");
    expect(declared[0]?.required).toBe(true);
    expect(declared[1]?.required).toBe(false);
  });

  it("stops at the next ### heading", () => {
    const body = `### Expected outputs
- nothing structured

### Dependencies

\`\`\`yaml
outputs:
  - name: should-not-parse
    artifact: anywhere
\`\`\`
`;
    expect(parseExpectedOutputs(body)).toEqual([]);
  });
});

describe("checkClosure", () => {
  let workspace: string;

  beforeEach(() => {
    workspace = mkdtempSync(join(tmpdir(), "oma-closure-"));
  });

  afterEach(() => {
    rmSync(workspace, { recursive: true, force: true });
  });

  function writeSkill(agentType: string, expectedOutputsSection: string) {
    const dir = join(workspace, ".agents", "skills", `oma-${agentType}`);
    mkdirSync(dir, { recursive: true });
    writeFileSync(
      join(dir, "SKILL.md"),
      `---\nname: oma-${agentType}\ndescription: test\n---\n\n## Scheduling\n\n${expectedOutputsSection}\n\n## End\n`,
    );
  }

  it("returns hasStructuredOutputs:false when SKILL.md is missing", () => {
    const result = checkClosure(workspace, "ghost");
    expect(result.hasStructuredOutputs).toBe(false);
    expect(result.missingRequired).toEqual([]);
  });

  it("flags missing required artifacts", () => {
    writeSkill(
      "pm",
      `### Expected outputs

\`\`\`yaml
outputs:
  - name: plan
    artifact: ".agents/results/plan-*.json"
    required: true
\`\`\``,
    );
    const result = checkClosure(workspace, "pm");
    expect(result.hasStructuredOutputs).toBe(true);
    expect(result.missingRequired).toHaveLength(1);
    expect(result.missingRequired[0]?.name).toBe("plan");
  });

  it("passes when required artifact exists", () => {
    writeSkill(
      "pm",
      `### Expected outputs

\`\`\`yaml
outputs:
  - name: plan
    artifact: ".agents/results/plan-*.json"
    required: true
\`\`\``,
    );
    mkdirSync(join(workspace, ".agents", "results"), { recursive: true });
    writeFileSync(join(workspace, ".agents", "results", "plan-001.json"), "{}");
    const result = checkClosure(workspace, "pm");
    expect(result.hasStructuredOutputs).toBe(true);
    expect(result.missingRequired).toHaveLength(0);
  });

  it("does not fail when optional artifact is missing", () => {
    writeSkill(
      "pm",
      `### Expected outputs

\`\`\`yaml
outputs:
  - name: optional-report
    artifact: ".agents/results/report.md"
\`\`\``,
    );
    const result = checkClosure(workspace, "pm");
    expect(result.hasStructuredOutputs).toBe(true);
    expect(result.missingRequired).toHaveLength(0);
  });
});
