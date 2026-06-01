import * as fs from "node:fs";
import * as path from "node:path";
import { clearNonDirectory } from "../utils/fs-utils.js";

const WORKFLOW_SKILL_MARKER = "<!-- oma:generated -->";

function extractWorkflowDescription(filePath: string): string | null {
  let content: string;
  try {
    content = fs.readFileSync(filePath, "utf-8");
  } catch {
    return null;
  }
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!match?.[1]) return null;
  const descMatch = match[1].match(/^description:\s*(.+?)\s*$/m);
  return descMatch?.[1]?.trim() ?? null;
}

function listWorkflowNames(workflowsDir: string): string[] {
  if (!fs.existsSync(workflowsDir)) return [];
  return fs
    .readdirSync(workflowsDir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => entry.name.slice(0, -".md".length));
}

/**
 * Install `.agents/workflows/*.md` as canonical skills under
 * `<installRoot>/.agents/skills/<workflow>/SKILL.md`. The unified target is
 * vendor-agnostic; per-vendor symlinks (Claude/Codex/Copilot/Qwen) are
 * created by the symlink layer downstream.
 *
 * Each generated SKILL.md:
 *   - includes <!-- oma:generated --> marker
 *   - includes a `disable-model-invocation` frontmatter flag (so skills are
 *     only invoked via explicit slash command, not auto-suggested)
 *   - body delegates: "Read and follow .agents/workflows/<name>.md step by step."
 *
 * Prunes stale entries whose workflow no longer exists in SSOT.
 * Never touches user-authored skills (those lack the marker).
 */
export function installUnifiedWorkflowSkills(
  sourceDir: string,
  installRoot: string,
): void {
  const workflowsDir = path.join(sourceDir, ".agents", "workflows");
  const skillsRoot = path.join(installRoot, ".agents", "skills");
  const names = listWorkflowNames(workflowsDir);

  if (fs.existsSync(skillsRoot)) {
    for (const entry of fs.readdirSync(skillsRoot, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const skillDir = path.join(skillsRoot, entry.name);
      const skillFile = path.join(skillDir, "SKILL.md");
      if (!fs.existsSync(skillFile)) continue;
      let existing: string;
      try {
        existing = fs.readFileSync(skillFile, "utf-8");
      } catch {
        continue;
      }
      if (!existing.includes(WORKFLOW_SKILL_MARKER)) continue;
      if (!names.includes(entry.name)) {
        fs.rmSync(skillDir, { recursive: true, force: true });
      }
    }
  }

  if (names.length === 0) return;

  fs.mkdirSync(skillsRoot, { recursive: true });
  for (const name of names) {
    const description =
      extractWorkflowDescription(path.join(workflowsDir, `${name}.md`)) ??
      `Workflow: ${name}`;
    const skillDir = path.join(skillsRoot, name);
    const skillFile = path.join(skillDir, "SKILL.md");
    clearNonDirectory(skillDir);
    fs.mkdirSync(skillDir, { recursive: true });
    const body = `---\nname: ${name}\ndescription: ${description}\ndisable-model-invocation: true\n---\n${WORKFLOW_SKILL_MARKER}\n\nRead and follow \`.agents/workflows/${name}.md\` step by step.\n`;
    fs.writeFileSync(skillFile, body);
  }
}
