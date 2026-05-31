declare global {
  interface Window {
    electronAPI?: {
      invoke: (channel: string, ...args: unknown[]) => Promise<unknown>;
    };
  }
}

export async function invoke<T = unknown>(channel: string, ...args: unknown[]): Promise<T> {
  const api = (globalThis as any).window?.electronAPI;
  if (!api) {
    throw new Error("electronAPI not available — running outside Electron?");
  }
  return api.invoke(channel, ...args) as Promise<T>;
}
