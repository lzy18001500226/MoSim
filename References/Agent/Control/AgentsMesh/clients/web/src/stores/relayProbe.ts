export async function probeRelayOpen(relayUrl: string, token: string, timeoutMs: number): Promise<boolean> {
  if (typeof WebSocket === "undefined") return false;
  const url = `${relayUrl}/browser/relay?token=${encodeURIComponent(token)}`;
  return new Promise((resolve) => {
    let settled = false;
    const ws = new WebSocket(url);
    const finish = (ok: boolean) => {
      if (settled) return;
      settled = true;
      try { ws.close(); } catch { /* noop */ }
      resolve(ok);
    };
    const timer = setTimeout(() => finish(false), timeoutMs);
    ws.onopen = () => { clearTimeout(timer); finish(true); };
    ws.onerror = () => { clearTimeout(timer); finish(false); };
    ws.onclose = () => { clearTimeout(timer); finish(false); };
  });
}
