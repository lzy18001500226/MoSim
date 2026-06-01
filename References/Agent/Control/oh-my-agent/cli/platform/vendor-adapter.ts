import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import type { VendorType } from "../types/index.js";
import { installVendorAgents } from "./agent-composer.js";
import { type HookVariant, installHooksFromVariant } from "./hooks-composer.js";
import { generateClaudeRules } from "./rules.js";
import { installUnifiedWorkflowSkills } from "./workflow-skills.js";

/**
 * Generate workflow router SKILL.md files for Claude Code.
 *
 * @deprecated The unified installer writes canonical
 * `.agents/skills/<workflow>/SKILL.md`; per-vendor surfacing happens via
 * `createVendorSymlinks` downstream.  This shim keeps the existing call-site
 * signature intact while delegating all work to `installUnifiedWorkflowSkills`.
 */
export function installClaudeWorkflowRouters(
  workflowsDir: string,
  installRoot: string,
): void {
  // workflowsDir is `<sourceDir>/.agents/workflows`; resolve two levels up to
  // obtain sourceDir for the unified installer.
  const sourceDir = resolve(workflowsDir, "..", "..");
  installUnifiedWorkflowSkills(sourceDir, installRoot);
}

/**
 * Install vendor-specific agent and workflow adaptations.
 * Hooks are installed from variant configs in .agents/hooks/variants/.
 */
export function installVendorAdaptations(
  sourceDir: string,
  installRoot: string,
  vendors: VendorType[],
): void {
  const workflowsDir = join(sourceDir, ".agents", "workflows");
  const hookVariantsDir = join(sourceDir, ".agents", "hooks", "variants");

  for (const vendor of vendors) {
    // 1. Install agents from variant (composer design)
    installVendorAgents(sourceDir, installRoot, vendor);

    // 2. Install hooks from variant config
    const variantPath = join(hookVariantsDir, `${vendor}.json`);
    if (existsSync(variantPath)) {
      const variant: HookVariant = JSON.parse(
        readFileSync(variantPath, "utf-8"),
      );
      installHooksFromVariant(sourceDir, installRoot, variant);
    }

    // 3. Claude-specific non-hook adaptations (routers, rules)
    if (vendor === "claude") {
      installClaudeWorkflowRouters(workflowsDir, installRoot);
      generateClaudeRules(installRoot);
    }
  }
}
