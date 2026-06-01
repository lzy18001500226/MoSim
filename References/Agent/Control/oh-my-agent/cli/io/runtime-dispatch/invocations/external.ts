import {
  splitArgs,
  type VendorConfig,
} from "../../../platform/agent-config.js";
import type { Invocation } from "../types.js";

/**
 * Cursor headless prompt with a plain trailing prompt — used by the external-invocation builder
 * (no @{agentId} preamble).
 */
function buildExternalCursorInvocation(
  vendorConfig: VendorConfig,
  promptContent: string,
): Invocation {
  const command = vendorConfig.command || "cursor";
  const args: string[] = ["agent", "-p"];

  if (vendorConfig.output_format_flag && vendorConfig.output_format) {
    args.push(vendorConfig.output_format_flag, vendorConfig.output_format);
  } else if (vendorConfig.output_format_flag) {
    args.push(vendorConfig.output_format_flag);
  }
  if (vendorConfig.auto_approve_flag) {
    args.push(vendorConfig.auto_approve_flag);
  } else {
    args.push("--yolo");
  }
  args.push("--trust");

  if (vendorConfig.model_flag && vendorConfig.default_model) {
    args.push(vendorConfig.model_flag, vendorConfig.default_model);
  }

  args.push(promptContent);

  return { command, args, env: { ...process.env } };
}

export function buildExternalInvocation(
  vendor: string,
  vendorConfig: VendorConfig,
  promptFlag: string | null,
  promptContent: string,
): Invocation {
  // Cursor Agent: `-p`/`--print` is a boolean flag; prompt must be a trailing positional argv.
  // The generic branch always pairs `promptFlag` with prompt as two args, which is wrong here.
  if (vendor === "cursor") {
    return buildExternalCursorInvocation(vendorConfig, promptContent);
  }

  // Vendors whose CLI binary name differs from the vendor identifier.
  const binaryByVendor: Record<string, string> = {
    antigravity: "agy",
  };
  const command = vendorConfig.command || binaryByVendor[vendor] || vendor;
  const args: string[] = [];
  const optionArgs: string[] = [];

  if (vendorConfig.subcommand) {
    args.push(vendorConfig.subcommand);
  }

  if (vendorConfig.output_format_flag && vendorConfig.output_format) {
    optionArgs.push(
      vendorConfig.output_format_flag,
      vendorConfig.output_format,
    );
  } else if (vendorConfig.output_format_flag) {
    optionArgs.push(vendorConfig.output_format_flag);
  }

  // agy 1.0 has no `--model` flag — defensively skip emitting one for the
  // antigravity vendor even when a stale vendorConfig carries it.
  if (
    vendor !== "antigravity" &&
    vendorConfig.model_flag &&
    vendorConfig.default_model
  ) {
    optionArgs.push(vendorConfig.model_flag, vendorConfig.default_model);
  }

  if (vendorConfig.isolation_flags) {
    optionArgs.push(...splitArgs(vendorConfig.isolation_flags));
  }

  if (vendorConfig.auto_approve_flag) {
    optionArgs.push(vendorConfig.auto_approve_flag);
  } else {
    const defaultAutoApprove: Record<string, string> = {
      gemini: "--approval-mode=yolo",
      codex: "--full-auto",
      qwen: "--yolo",
      antigravity: "--dangerously-skip-permissions",
    };
    const fallbackFlag = defaultAutoApprove[vendor];
    if (fallbackFlag) {
      optionArgs.push(fallbackFlag);
    }
  }

  if (promptFlag) {
    optionArgs.push(promptFlag, promptContent);
  }

  args.push(...optionArgs);
  if (!promptFlag) {
    args.push(promptContent);
  }

  const env = { ...process.env };
  if (vendorConfig.isolation_env) {
    const [key, ...rest] = vendorConfig.isolation_env.split("=");
    const rawValue = rest.join("=");
    if (key && rawValue) {
      env[key] = rawValue.replace("$$", String(process.pid));
    }
  }

  return { command, args, env };
}
