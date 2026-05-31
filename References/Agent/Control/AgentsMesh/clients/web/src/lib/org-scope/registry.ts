type Reset = () => void;

const handlers: Set<Reset> = new Set();

export function registerOrgScopedReset(fn: Reset): () => void {
  handlers.add(fn);
  return () => handlers.delete(fn);
}

export function resetOrgScopedServices(): void {
  for (const fn of handlers) {
    try { fn(); } catch (e) { console.error("org-scope reset handler failed:", e); }
  }
}
