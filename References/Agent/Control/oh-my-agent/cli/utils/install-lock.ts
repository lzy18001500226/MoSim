import {
  closeSync,
  constants,
  existsSync,
  mkdirSync,
  openSync,
  readFileSync,
  unlinkSync,
  writeSync,
} from "node:fs";
import { hostname } from "node:os";
import { join } from "node:path";

export type LockMeta = {
  pid: number;
  hostname: string;
  startedAt: string; // ISO
  uid: number;
};

export type AcquireResult =
  | { ok: true; release: () => void }
  | { ok: false; held: LockMeta; reason: "active" | "stale-but-uncleared" };

const STALE_AFTER_MS = 10 * 60 * 1000; // 10 minutes

/** Lock path: <installRoot>/.agents/_install.lock (transient runtime lock) */
export function lockPath(installRoot: string): string {
  return join(installRoot, ".agents", "_install.lock");
}

function isPidAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (err) {
    const code = (err as NodeJS.ErrnoException).code;
    // ESRCH: no process found — pid is dead
    // EPERM: process exists but we can't signal it — treat as alive
    if (code === "ESRCH") return false;
    return true;
  }
}

function writeLockFile(path: string): void {
  const meta: LockMeta = {
    pid: process.pid,
    hostname: hostname(),
    startedAt: new Date().toISOString(),
    uid: typeof process.getuid === "function" ? process.getuid() : 0,
  };

  const dir = join(path, "..");
  mkdirSync(dir, { recursive: true });

  // Atomic create via O_EXCL — throws EEXIST if already present
  const fd = openSync(
    path,
    constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL,
    0o600,
  );
  try {
    const payload = JSON.stringify(meta, null, 2);
    writeSync(fd, payload);
  } finally {
    closeSync(fd);
  }
}

function readLockFile(path: string): LockMeta | null {
  try {
    const content = readFileSync(path, "utf-8");
    const parsed = JSON.parse(content) as unknown;
    if (
      parsed &&
      typeof parsed === "object" &&
      !Array.isArray(parsed) &&
      typeof (parsed as Record<string, unknown>).pid === "number" &&
      typeof (parsed as Record<string, unknown>).hostname === "string" &&
      typeof (parsed as Record<string, unknown>).startedAt === "string" &&
      typeof (parsed as Record<string, unknown>).uid === "number"
    ) {
      return parsed as LockMeta;
    }
    return null;
  } catch {
    return null;
  }
}

/** Try to acquire the install lock. Atomic via O_EXCL; auto-clears stale locks where pid is dead. */
export function acquireLock(installRoot: string): AcquireResult {
  const path = lockPath(installRoot);

  const attemptAcquire = (): AcquireResult => {
    try {
      writeLockFile(path);
      return {
        ok: true,
        release: () => {
          try {
            unlinkSync(path);
          } catch {
            // best-effort
          }
        },
      };
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code !== "EEXIST") {
        throw err;
      }

      // Lock file already exists — inspect it
      const existing = readLockFile(path);
      if (!existing) {
        // Can't read/parse — treat as active (safety-first)
        const fallbackMeta: LockMeta = {
          pid: -1,
          hostname: "unknown",
          startedAt: new Date().toISOString(),
          uid: 0,
        };
        return { ok: false, held: fallbackMeta, reason: "active" };
      }

      // Different hostname → could be a real concurrent run on shared FS.
      // Never auto-clear.
      if (existing.hostname !== hostname()) {
        return { ok: false, held: existing, reason: "active" };
      }

      const pidAlive = isPidAlive(existing.pid);
      const ageMs = Date.now() - new Date(existing.startedAt).getTime();
      const isStale = !pidAlive && ageMs > STALE_AFTER_MS;

      if (isStale) {
        // Auto-clear stale lock and retry once
        try {
          unlinkSync(path);
        } catch {
          // If we can't unlink, give up
          return { ok: false, held: existing, reason: "stale-but-uncleared" };
        }

        // Retry acquisition once after clearing
        try {
          writeLockFile(path);
          return {
            ok: true,
            release: () => {
              try {
                unlinkSync(path);
              } catch {
                // best-effort
              }
            },
          };
        } catch {
          return { ok: false, held: existing, reason: "stale-but-uncleared" };
        }
      }

      // Pid is alive (or recently started but not stale) — lock is active
      return { ok: false, held: existing, reason: "active" };
    }
  };

  return attemptAcquire();
}

const INSTALL_LOCK_SIGNALS = ["SIGINT", "SIGTERM"] as const;
type InstallLockSignal = (typeof INSTALL_LOCK_SIGNALS)[number];

const SIGNAL_EXIT_CODE: Record<InstallLockSignal, number> = {
  SIGINT: 130,
  SIGTERM: 143,
};

/**
 * Wrap a lock release so it is idempotent and runs on SIGINT/SIGTERM before exit.
 * Call the returned function from a `finally` block for normal completion paths.
 */
export function bindInstallLockRelease(release: () => void): () => void {
  let released = false;
  const handlers = new Map<InstallLockSignal, () => void>();

  const releaseOnce = (): void => {
    if (released) return;
    released = true;
    for (const signal of INSTALL_LOCK_SIGNALS) {
      const handler = handlers.get(signal);
      if (handler) process.removeListener(signal, handler);
    }
    handlers.clear();
    release();
  };

  for (const signal of INSTALL_LOCK_SIGNALS) {
    const handler = (): void => {
      releaseOnce();
      process.exit(SIGNAL_EXIT_CODE[signal]);
    };
    handlers.set(signal, handler);
    process.once(signal, handler);
  }

  return releaseOnce;
}

/** Test-only: forcibly remove the lock file (used in fixtures). */
export function _forceReleaseLock(installRoot: string): void {
  const path = lockPath(installRoot);
  if (existsSync(path)) {
    unlinkSync(path);
  }
}
