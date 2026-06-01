import * as p from "@clack/prompts";
import pc from "picocolors";
import {
  getSecret,
  isValidKeyName,
  listSecrets,
  removeSecret,
  storeSecret,
} from "../../io/vault.js";

export async function vaultStore(name: string, valueFlag?: string) {
  if (!isValidKeyName(name)) {
    console.error(
      pc.red(
        `✘ Invalid key name. Use 1-64 chars of [A-Za-z0-9._-] (e.g. anthropic, github-pat).`,
      ),
    );
    process.exit(1);
  }

  let value = valueFlag;
  if (value === undefined) {
    const answer = await p.password({
      message: `Value for ${pc.bold(name)} (input hidden)`,
      mask: "*",
    });
    if (p.isCancel(answer)) {
      p.cancel("Cancelled.");
      process.exit(130);
    }
    value = answer;
  }
  if (!value || value.length === 0) {
    console.error(pc.red("✘ Refusing to store empty value."));
    process.exit(1);
  }

  const { overwrote } = await storeSecret(name, value);
  console.log(
    overwrote
      ? pc.yellow(`✓ Updated existing entry: ${name}`)
      : pc.green(`✓ Stored new entry: ${name}`),
  );
}

export async function vaultGet(name: string) {
  if (!isValidKeyName(name)) {
    console.error(pc.red(`✘ Invalid key name.`));
    process.exit(1);
  }
  const value = await getSecret(name);
  if (value === null) {
    console.error(pc.red(`✘ No such entry: ${name}`));
    process.exit(2);
  }
  // Print raw value with no decoration so it can be used in:
  //   export ANTHROPIC_API_KEY=$(oma vault get anthropic)
  process.stdout.write(value);
}

export async function vaultRm(name: string) {
  if (!isValidKeyName(name)) {
    console.error(pc.red(`✘ Invalid key name.`));
    process.exit(1);
  }
  const removed = await removeSecret(name);
  if (removed) {
    console.log(pc.green(`✓ Removed: ${name}`));
  } else {
    console.log(pc.yellow(`(no entry to remove for ${name})`));
  }
}

export function vaultList(jsonMode: boolean) {
  const entries = listSecrets();
  if (jsonMode) {
    console.log(JSON.stringify({ entries }, null, 2));
    return;
  }
  if (entries.length === 0) {
    console.log(pc.dim("(no entries — use `oma vault store <name>` to add)"));
    return;
  }
  console.log(pc.bold("🔐 oma vault entries"));
  for (const e of entries) {
    console.log(`  ${e.name.padEnd(24)} ${pc.dim(`stored ${e.createdAt}`)}`);
  }
  console.log(
    pc.dim("Values are stored in your OS keychain; only names listed here."),
  );
}
