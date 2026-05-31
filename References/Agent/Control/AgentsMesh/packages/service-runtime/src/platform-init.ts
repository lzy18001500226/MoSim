let initPromise: Promise<void> | null = null;
let platformInitFn: (() => Promise<void>) | null = null;

export function setPlatformInit(fn: () => Promise<void>): void {
  platformInitFn = fn;
}

export async function ensurePlatformReady(): Promise<void> {
  if (!initPromise && platformInitFn) {
    initPromise = platformInitFn();
  }
  if (initPromise) await initPromise;
}
