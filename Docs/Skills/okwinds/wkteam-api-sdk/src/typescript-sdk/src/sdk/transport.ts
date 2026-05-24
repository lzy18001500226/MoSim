export type TransportRequest = {
  url: string;
  method: string;
  headers: Record<string, string>;
  bodyText?: string;
  timeoutMs: number;
};

export type TransportResponse = {
  status: number;
  headers: Record<string, string>;
  bodyText: string;
};

/**
 * 可注入传输层：便于 mock、代理、替换 fetch/axios 等。
 */
export type Transport = (req: TransportRequest) => Promise<TransportResponse>;

export function createFetchTransport(): Transport {
  return async (req) => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), req.timeoutMs);
    try {
      const resp = await fetch(req.url, {
        method: req.method,
        headers: req.headers,
        body: req.bodyText,
        signal: controller.signal,
      });
      const bodyText = await resp.text();
      const headers: Record<string, string> = {};
      resp.headers.forEach((value, key) => {
        headers[key.toLowerCase()] = value;
      });
      return { status: resp.status, headers, bodyText };
    } finally {
      clearTimeout(timeout);
    }
  };
}
