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
import { afterEach, describe, expect, it } from "vitest";
import { installUnifiedWorkflowSkills } from "./workflow-skills.js";

function setupSource(root: string, workflows: Record<string, string>): void {
  const dir = join(root, ".agents", "workflows");
  mkdirSync(dir, { recursive: true });
  for (const [name, content] of Object.entries(workflows)) {
    writeFileSync(join(dir, `${name}.md`), content);
  }
}

describe("installUnifiedWorkflowSkills", () => {
  const tempRoots: string[] = [];

  afterEach(() => {
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

  it("writes correct SKILL.md with marker, disable-model-invocation, and delegate body", () => {
    const sourceDir = mkTemp("oma-wfs-src-");
    const targetDir = mkTemp("oma-wfs-dst-");
    setupSource(sourceDir, {
      orchestrate: "---\ndescription: Parallel subagents\n---\n\n# body",
      work: "---\ndescription: Step-by-step work\n---\n\n# body",
    });

    installUnifiedWorkflowSkills(sourceDir, targetDir);

    const orchestrateFile = join(
      targetDir,
      ".agents",
      "skills",
      "orchestrate",
      "SKILL.md",
    );
    const workFile = join(targetDir, ".agents", "skills", "work", "SKILL.md");
    expect(existsSync(orchestrateFile)).toBe(true);
    expect(existsSync(workFile)).toBe(true);

    const orchestrateBody = readFileSync(orchestrateFile, "utf-8");
    expect(orchestrateBody).toContain("name: orchestrate");
    expect(orchestrateBody).toContain("description: Parallel subagents");
    expect(orchestrateBody).toContain("disable-model-invocation: true");
    expect(orchestrateBody).toContain("<!-- oma:generated -->");
    expect(orchestrateBody).toContain(
      "Read and follow `.agents/workflows/orchestrate.md` step by step.",
    );
  });

  it("falls back to a default description when frontmatter is missing", () => {
    const sourceDir = mkTemp("oma-wfs-src-");
    const targetDir = mkTemp("oma-wfs-dst-");
    setupSource(sourceDir, {
      bare: "# no frontmatter here\n",
    });

    installUnifiedWorkflowSkills(sourceDir, targetDir);

    const body = readFileSync(
      join(targetDir, ".agents", "skills", "bare", "SKILL.md"),
      "utf-8",
    );
    expect(body).toContain("description: Workflow: bare");
    expect(body).toContain("disable-model-invocation: true");
    expect(body).toContain("<!-- oma:generated -->");
  });

  it("is idempotent: running twice produces no diff", () => {
    const sourceDir = mkTemp("oma-wfs-src-");
    const targetDir = mkTemp("oma-wfs-dst-");
    setupSource(sourceDir, {
      plan: "---\ndescription: PM task breakdown\n---\n",
    });

    installUnifiedWorkflowSkills(sourceDir, targetDir);
    const first = readFileSync(
      join(targetDir, ".agents", "skills", "plan", "SKILL.md"),
      "utf-8",
    );
    installUnifiedWorkflowSkills(sourceDir, targetDir);
    const second = readFileSync(
      join(targetDir, ".agents", "skills", "plan", "SKILL.md"),
      "utf-8",
    );
    expect(second).toBe(first);
  });

  it("prunes stale marker-gated skill whose workflow no longer exists", () => {
    const sourceDir = mkTemp("oma-wfs-src-");
    const targetDir = mkTemp("oma-wfs-dst-");
    setupSource(sourceDir, { debug: "---\ndescription: Bug diagnosis\n---\n" });

    const staleDir = join(targetDir, ".agents", "skills", "oldworkflow");
    mkdirSync(staleDir, { recursive: true });
    writeFileSync(
      join(staleDir, "SKILL.md"),
      "---\nname: oldworkflow\ndescription: old\ndisable-model-invocation: true\n---\n<!-- oma:generated -->\n\nRead and follow `.agents/workflows/oldworkflow.md` step by step.\n",
    );

    installUnifiedWorkflowSkills(sourceDir, targetDir);

    expect(existsSync(staleDir)).toBe(false);
    expect(
      existsSync(join(targetDir, ".agents", "skills", "debug", "SKILL.md")),
    ).toBe(true);
  });

  it("does not touch user-authored skills without the oma marker", () => {
    const sourceDir = mkTemp("oma-wfs-src-");
    const targetDir = mkTemp("oma-wfs-dst-");
    setupSource(sourceDir, { debug: "---\ndescription: Bug diagnosis\n---\n" });

    const userDir = join(targetDir, ".agents", "skills", "my-custom");
    mkdirSync(userDir, { recursive: true });
    const userSkill =
      "---\nname: my-custom\ndescription: User-authored skill\n---\nDo my thing.\n";
    writeFileSync(join(userDir, "SKILL.md"), userSkill);

    installUnifiedWorkflowSkills(sourceDir, targetDir);

    expect(readFileSync(join(userDir, "SKILL.md"), "utf-8")).toBe(userSkill);
  });

  it("skips subdirectories under workflows/", () => {
    const sourceDir = mkTemp("oma-wfs-src-");
    const targetDir = mkTemp("oma-wfs-dst-");
    setupSource(sourceDir, {
      plan: "---\ndescription: Plan\n---\n",
    });
    mkdirSync(join(sourceDir, ".agents", "workflows", "plan", "resources"), {
      recursive: true,
    });
    writeFileSync(
      join(sourceDir, ".agents", "workflows", "plan", "resources", "guide.md"),
      "nested",
    );

    installUnifiedWorkflowSkills(sourceDir, targetDir);

    expect(existsSync(join(targetDir, ".agents", "skills", "resources"))).toBe(
      false,
    );
    expect(existsSync(join(targetDir, ".agents", "skills", "guide"))).toBe(
      false,
    );
  });

  it("does nothing when the workflows source does not exist", () => {
    const sourceDir = mkTemp("oma-wfs-src-");
    const targetDir = mkTemp("oma-wfs-dst-");

    installUnifiedWorkflowSkills(sourceDir, targetDir);

    expect(existsSync(join(targetDir, ".agents", "skills"))).toBe(false);
  });
});
