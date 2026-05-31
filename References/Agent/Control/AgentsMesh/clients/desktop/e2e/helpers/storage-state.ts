import { mkdirSync, writeFileSync, readFileSync, existsSync } from "node:fs";
import { dirname } from "node:path";
import type { Page } from "@playwright/test";

export interface StorageSnapshot {
  localStorage: Record<string, string>;
  sessionStorage: Record<string, string>;
}

/** Capture renderer-side storage. Electron does NOT use Playwright's browser context storageState
 * for persistence because the renderer runs in a Chromium instance that re-reads the
 * on-disk Local Storage every launch. Reading & re-injecting is more reliable. */
export async function captureStorage(page: Page): Promise<StorageSnapshot> {
  return page.evaluate(() => {
    const dump = (s: Storage): Record<string, string> => {
      const out: Record<string, string> = {};
      for (let i = 0; i < s.length; i++) {
        const k = s.key(i);
        if (k !== null) out[k] = s.getItem(k) ?? "";
      }
      return out;
    };
    return {
      localStorage: dump(window.localStorage),
      sessionStorage: dump(window.sessionStorage),
    };
  });
}

export async function restoreStorage(page: Page, snap: StorageSnapshot): Promise<void> {
  await page.evaluate((s) => {
    Object.entries(s.localStorage).forEach(([k, v]) => window.localStorage.setItem(k, v));
    Object.entries(s.sessionStorage).forEach(([k, v]) => window.sessionStorage.setItem(k, v));
  }, snap);
}

export function saveStorageFile(path: string, snap: StorageSnapshot): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(snap, null, 2), "utf-8");
}

export function loadStorageFile(path: string): StorageSnapshot | null {
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, "utf-8")) as StorageSnapshot;
}
