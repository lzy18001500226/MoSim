import type { Command } from "commander";
import { runAction } from "../../utils/cli-framework.js";
import { vaultGet, vaultList, vaultRm, vaultStore } from "./vault.js";

export function registerVault(program: Command): void {
  const vault = program
    .command("vault")
    .description(
      "Manage API keys + secrets in the OS keychain (macOS Keychain / Linux Secret Service / Windows Credential Manager)",
    );

  vault
    .command("store <name>")
    .description("Store a secret under <name> (interactive password prompt)")
    .option(
      "--value <value>",
      "Pass value non-interactively (WARNING: visible in shell history)",
    )
    .action(
      runAction(async (name, options) => {
        await vaultStore(name, options.value);
      }),
    );

  vault
    .command("get <name>")
    .description(
      "Print stored value to stdout (for: export KEY=$(oma vault get <name>))",
    )
    .action(
      runAction(async (name) => {
        await vaultGet(name);
      }),
    );

  vault
    .command("rm <name>")
    .description("Remove a secret from the keychain and the index")
    .action(
      runAction(async (name) => {
        await vaultRm(name);
      }),
    );

  vault
    .command("list")
    .description("List stored secret names (values never displayed)")
    .option("--json", "Output as JSON")
    .action(
      runAction(async (options) => {
        vaultList(Boolean(options.json));
      }),
    );
}
