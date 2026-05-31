import type { Page } from "@playwright/test";

/**
 * Invoke an IPC handler exposed through `window.electronAPI.invoke`.
 * Each IPC handler corresponds to a method on the Rust AppState
 * (auto-registered in desktop/src/main/index.ts via reflection).
 */
export async function invokeIpc<T = unknown>(
  page: Page,
  method: string,
  ...args: unknown[]
): Promise<T> {
  return page.evaluate(
    async ({ m, a }) => {
      const api = (window as unknown as { electronAPI: { invoke: (c: string, ...a: unknown[]) => Promise<unknown> } }).electronAPI;
      return api.invoke(m, ...a) as Promise<unknown>;
    },
    { m: method, a: args }
  ) as Promise<T>;
}

/** Assert the IPC call rejects; returns the error message. */
export async function invokeIpcExpectError(
  page: Page,
  method: string,
  ...args: unknown[]
): Promise<string> {
  return page.evaluate(
    async ({ m, a }) => {
      const api = (window as unknown as { electronAPI: { invoke: (c: string, ...a: unknown[]) => Promise<unknown> } }).electronAPI;
      try {
        await api.invoke(m, ...a);
        return "__IPC_CALL_UNEXPECTEDLY_SUCCEEDED__";
      } catch (err) {
        return err instanceof Error ? err.message : String(err);
      }
    },
    { m: method, a: args }
  );
}
