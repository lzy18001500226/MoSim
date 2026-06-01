import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  diffArtifacts,
  hasArtifactChanges,
  readArtifactDescription,
  readSkillDescription,
  readWorkflowDescription,
  snapshotArtifacts,
} from "./manifest.js";

const tempRoots: string[] = [];

afterEach(() => {
  for (const root of tempRoots) {
    rmSync(root, { recursive: true, force: true });
  }
  tempRoots.length = 0;
});

function makeProject(skills: string[], workflows: string[]): string {
  const root = mkdtempSync(join(tmpdir(), "oma-artifacts-"));
  tempRoots.push(root);

  const skillsDir = join(root, ".agents", "skills");
  mkdirSync(skillsDir, { recursive: true });
  for (const s of skills) {
    mkdirSync(join(skillsDir, s), { recursive: true });
  }
  // ignored entries
  mkdirSync(join(skillsDir, "_shared"), { recursive: true });
  writeFileSync(join(skillsDir, "_version.json"), "{}");

  const workflowsDir = join(root, ".agents", "workflows");
  mkdirSync(workflowsDir, { recursive: true });
  for (const w of workflows) {
    writeFileSync(join(workflowsDir, `${w}.md`), "# wf");
  }
  // composite workflow dir: should be ignored
  mkdirSync(join(workflowsDir, "ralph"), { recursive: true });

  return root;
}

describe("snapshotArtifacts", () => {
  it("lists oma-* skill dirs and *.md workflows, ignoring internal entries", () => {
    const root = makeProject(
      ["oma-frontend", "oma-backend"],
      ["plan", "review"],
    );
    const snap = snapshotArtifacts(root);

    expect(snap.skills).toEqual(["oma-backend", "oma-frontend"]);
    expect(snap.workflows).toEqual(["plan", "review"]);
  });

  it("returns empty arrays when directories do not exist", () => {
    const root = mkdtempSync(join(tmpdir(), "oma-artifacts-empty-"));
    tempRoots.push(root);

    const snap = snapshotArtifacts(root);
    expect(snap.skills).toEqual([]);
    expect(snap.workflows).toEqual([]);
  });
});

describe("diffArtifacts", () => {
  it("computes added and removed for skills and workflows", () => {
    const before = {
      skills: ["oma-backend", "oma-old"],
      workflows: ["plan", "ralph"],
    };
    const after = {
      skills: ["oma-backend", "oma-new"],
      workflows: ["plan", "deepsec"],
    };

    const diff = diffArtifacts(before, after);
    expect(diff.addedSkills).toEqual(["oma-new"]);
    expect(diff.removedSkills).toEqual(["oma-old"]);
    expect(diff.addedWorkflows).toEqual(["deepsec"]);
    expect(diff.removedWorkflows).toEqual(["ralph"]);
    expect(hasArtifactChanges(diff)).toBe(true);
  });

  it("hasArtifactChanges returns false when snapshots match", () => {
    const snap = { skills: ["oma-backend"], workflows: ["plan"] };
    expect(hasArtifactChanges(diffArtifacts(snap, snap))).toBe(false);
  });
});

describe("readArtifactDescription", () => {
  it("extracts the first sentence from frontmatter description", () => {
    const root = mkdtempSync(join(tmpdir(), "oma-desc-"));
    tempRoots.push(root);

    const file = join(root, "SKILL.md");
    writeFileSync(
      file,
      "---\nname: oma-foo\ndescription: First sentence here. Second sentence ignored.\n---\n\n# body\n",
    );

    expect(readArtifactDescription(file)).toBe("First sentence here.");
  });

  it("truncates very long single-sentence descriptions", () => {
    const root = mkdtempSync(join(tmpdir(), "oma-desc-"));
    tempRoots.push(root);

    const file = join(root, "SKILL.md");
    const long = "a".repeat(150);
    writeFileSync(file, `---\ndescription: ${long}\n---\n`);

    const out = readArtifactDescription(file);
    expect(out.length).toBeLessThanOrEqual(100);
    expect(out.endsWith("...")).toBe(true);
  });

  it("returns empty string when file or frontmatter is missing", () => {
    expect(readArtifactDescription("/nonexistent/path.md")).toBe("");

    const root = mkdtempSync(join(tmpdir(), "oma-desc-"));
    tempRoots.push(root);
    const file = join(root, "SKILL.md");
    writeFileSync(file, "# no frontmatter\n");
    expect(readArtifactDescription(file)).toBe("");
  });

  it("readSkillDescription resolves the SKILL.md path under .agents/skills", () => {
    const root = mkdtempSync(join(tmpdir(), "oma-desc-"));
    tempRoots.push(root);

    const skillDir = join(root, ".agents", "skills", "oma-test");
    mkdirSync(skillDir, { recursive: true });
    writeFileSync(
      join(skillDir, "SKILL.md"),
      "---\ndescription: Skill summary.\n---\n",
    );

    expect(readSkillDescription(root, "oma-test")).toBe("Skill summary.");
  });

  it("readWorkflowDescription resolves the workflow .md path", () => {
    const root = mkdtempSync(join(tmpdir(), "oma-desc-"));
    tempRoots.push(root);

    const wfDir = join(root, ".agents", "workflows");
    mkdirSync(wfDir, { recursive: true });
    writeFileSync(
      join(wfDir, "plan.md"),
      "---\ndescription: Plan workflow summary.\n---\n",
    );

    expect(readWorkflowDescription(root, "plan")).toBe(
      "Plan workflow summary.",
    );
  });
});
