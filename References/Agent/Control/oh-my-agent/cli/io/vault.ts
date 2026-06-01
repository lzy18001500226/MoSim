/**
 * vault.ts
 *
 * OS-native credential storage for oma. Backed by @napi-rs/keyring,
 * which delegates to macOS Keychain, Linux Secret Service, or Windows
 * Credential Manager. A small index file under ${HOME}/.config/oma/
 * tracks the key names that have been stored (values stay in the OS
 * keychain) so `oma vault list` can enumerate without ever exposing
 * secret values.
 *
 * Native module load failures are surfaced explicitly rather than
 * silently falling back, so users notice when the platform credential
 * store is unavailable (e.g. headless Linux without Secret Service).
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";

const SERVICE = "oh-my-agent";

export interface VaultIndexEntry {
  name: string;
  createdAt: string;
}

interface VaultIndex {
  version: 1;
  entries: VaultIndexEntry[];
}

function indexDir(): string {
  return path.join(homedir(), ".config", "oma");
}

function indexPath(): string {
  return path.join(indexDir(), "vault-index.json");
}

function readIndex(): VaultIndex {
  const p = indexPath();
  if (!existsSync(p)) return { version: 1, entries: [] };
  try {
    const raw = JSON.parse(readFileSync(p, "utf-8"));
    if (raw && raw.version === 1 && Array.isArray(raw.entries)) return raw;
  } catch {
    // Corrupted index: surface as empty so the user can re-add keys.
  }
  return { version: 1, entries: [] };
}

function writeIndex(idx: VaultIndex): void {
  const dir = indexDir();
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true, mode: 0o700 });
  writeFileSync(indexPath(), JSON.stringify(idx, null, 2), {
    encoding: "utf-8",
    mode: 0o600,
  });
}

// Lazy-load the native module so a missing platform credential store
// produces a clear error at call time, not at import time.
type KeyringEntry = {
  getPassword(): string | null;
  setPassword(value: string): void;
  deletePassword(): boolean;
};

async function makeEntry(name: string): Promise<KeyringEntry> {
  try {
    const mod = await import("@napi-rs/keyring");
    return new mod.Entry(SERVICE, name);
  } catch (err) {
    throw new Error(
      `oma vault requires @napi-rs/keyring and an OS credential store. ` +
        `On headless Linux, install and start libsecret/gnome-keyring. ` +
        `Underlying error: ${String(err)}`,
    );
  }
}

export function isValidKeyName(name: string): boolean {
  return /^[A-Za-z0-9._-]{1,64}$/.test(name);
}

function assertValidKeyName(name: string): void {
  if (!isValidKeyName(name)) {
    throw new Error(
      `Invalid vault key name ${JSON.stringify(name)}. ` +
        `Must be 1-64 chars of alphanumeric, dot, underscore, or hyphen.`,
    );
  }
}

export async function storeSecret(
  name: string,
  value: string,
): Promise<{ overwrote: boolean }> {
  assertValidKeyName(name);
  if (value.length === 0) {
    throw new Error("Refusing to store empty value in vault.");
  }
  const entry = await makeEntry(name);
  const existing = entry.getPassword();
  entry.setPassword(value);

  const idx = readIndex();
  const wasIndexed = idx.entries.some((e) => e.name === name);
  if (!wasIndexed) {
    idx.entries.push({ name, createdAt: new Date().toISOString() });
    writeIndex(idx);
  }

  return { overwrote: existing !== null };
}

export async function getSecret(name: string): Promise<string | null> {
  assertValidKeyName(name);
  const entry = await makeEntry(name);
  return entry.getPassword();
}

export async function removeSecret(name: string): Promise<boolean> {
  assertValidKeyName(name);
  const entry = await makeEntry(name);
  const removed = entry.deletePassword();

  const idx = readIndex();
  const filtered = idx.entries.filter((e) => e.name !== name);
  if (filtered.length !== idx.entries.length) {
    idx.entries = filtered;
    writeIndex(idx);
  }

  return removed;
}

export function listSecrets(): VaultIndexEntry[] {
  return readIndex()
    .entries.slice()
    .sort((a, b) => a.name.localeCompare(b.name));
}
