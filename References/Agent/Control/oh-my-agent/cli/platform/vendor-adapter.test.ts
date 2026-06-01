import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { installClaudeWorkflowRouters } from "./vendor-adapter.js";
import * as workflowSkillsModule from "./workflow-skills.js";

function setupSource(root: string, workflows: Record<string, string>): void {
  const dir = join(root, ".agents", "workflows");
  mkdirSync(dir, { recursive: true });
  for (const [name, content] of Object.entries(workflows)) {
    writeFileSync(join(dir, `${name}.md`), content);
  }
}

describe("installClaudeWorkflowRouters (shim)", () => {
  const tempRoots: string[] = [];

  afterEach(() => {
    vi.restoreAllMocks();
    for (const root of tempRoots) {
      rmSync(root, { recursive: true, force: true });
    }
    tempRoots.length = 0;
  });

  function mkTemp(prefix: string): string {
    const dir = mkdtempSync(join(tmpdir(), prefix));
    tempRoots.push(dir);
    return dir;
  }

  it("delegates to installUnifiedWorkflowSkills with the correct sourceDir", () => {
    const spy = vi.spyOn(workflowSkillsModule, "installUnifiedWorkflowSkills");
    const sourceDir = mkTemp("oma-va-src-");
    const targetDir = mkTemp("oma-va-dst-");
    setupSource(sourceDir, {
      orchestrate: "---\ndescription: Parallel subagents\n---\n",
    });

    const workflowsDir = join(sourceDir, ".agents", "workflows");
    installClaudeWorkflowRouters(workflowsDir, targetDir);

    expect(spy).toHaveBeenCalledOnce();
    // sourceDir derivation: resolve(workflowsDir, "..", "..") === sourceDir
    const firstCall = spy.mock.calls[0];
    expect(firstCall).toBeDefined();
    expect(firstCall?.[0]).toBe(sourceDir);
    expect(firstCall?.[1]).toBe(targetDir);
  });

  it("writes canonical .agents/skills/<name>/SKILL.md with oma:generated marker", () => {
    const sourceDir = mkTemp("oma-va-src-");
    const targetDir = mkTemp("oma-va-dst-");
    setupSource(sourceDir, {
      work: "---\ndescription: Step-by-step work\n---\n",
      plan: "---\ndescription: PM task breakdown\n---\n",
    });

    const workflowsDir = join(sourceDir, ".agents", "workflows");
    installClaudeWorkflowRouters(workflowsDir, targetDir);

    const workSkill = join(targetDir, ".agents", "skills", "work", "SKILL.md");
    const planSkill = join(targetDir, ".agents", "skills", "plan", "SKILL.md");
    expect(existsSync(workSkill)).toBe(true);
    expect(existsSync(planSkill)).toBe(true);

    const workBody = readFileSync(workSkill, "utf-8");
    expect(workBody).toContain("<!-- oma:generated -->");
    expect(workBody).toContain("disable-model-invocation: true");
    expect(workBody).toContain(
      "Read and follow `.agents/workflows/work.md` step by step.",
    );
  });

  it("is idempotent: running twice produces the same output", () => {
    const sourceDir = mkTemp("oma-va-src-");
    const targetDir = mkTemp("oma-va-dst-");
    setupSource(sourceDir, {
      debug: "---\ndescription: Bug diagnosis\n---\n",
    });

    const workflowsDir = join(sourceDir, ".agents", "workflows");
    installClaudeWorkflowRouters(workflowsDir, targetDir);
    const first = readFileSync(
      join(targetDir, ".agents", "skills", "debug", "SKILL.md"),
      "utf-8",
    );
    installClaudeWorkflowRouters(workflowsDir, targetDir);
    const second = readFileSync(
      join(targetDir, ".agents", "skills", "debug", "SKILL.md"),
      "utf-8",
    );
    expect(second).toBe(first);
  });

  it("does nothing when the workflows source does not exist", () => {
    const sourceDir = mkTemp("oma-va-src-");
    const targetDir = mkTemp("oma-va-dst-");
    // No workflows set up

    const workflowsDir = join(sourceDir, ".agents", "workflows");
    installClaudeWorkflowRouters(workflowsDir, targetDir);

    expect(existsSync(join(targetDir, ".agents", "skills"))).toBe(false);
  });
});
