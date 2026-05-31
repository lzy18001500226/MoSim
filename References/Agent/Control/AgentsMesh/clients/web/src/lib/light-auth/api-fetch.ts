// Pure fetch wrapper for the (auth) route group — no wasm, no agentsmesh-wasm.
// Throws @/lib/api/api-types::ApiError on 4xx/5xx so existing UI code that
// matches `err instanceof ApiError && err.hasCode(...)` keeps working
// unchanged. Bearer tokens are pulled lazily from localStorage via
// readLightAuthToken so callers don't need to thread them through.
//
// Two transport surfaces:
//   - lightFetch — legacy REST (still used by /runners/grpc/auth-url and
//     a couple of public read endpoints that the runner CLI hits).
//   - lightConnect — Connect-RPC JSON. The bulk of auth + org + user
//     surfaces migrated to Connect in R5/R6; light-auth talks to them over
//     application/json without pulling the wasm protobuf runtime.

import { ApiError } from "@/lib/api/api-types";
import { readLightAuthToken, resolveLightBaseUrl } from "@/lib/light-session";

type Method = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

export interface LightFetchOptions {
  method?: Method;
  body?: unknown;
  authenticated?: boolean;
  signal?: AbortSignal;
  query?: Record<string, string | number | boolean | undefined | null>;
  baseUrl?: string;
}

function appendQuery(path: string, query?: LightFetchOptions["query"]): string {
  if (!query) return path;
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (v === undefined || v === null) continue;
    params.set(k, String(v));
  }
  const qs = params.toString();
  if (!qs) return path;
  return path.includes("?") ? `${path}&${qs}` : `${path}?${qs}`;
}

export async function lightFetch<T = unknown>(
  path: string,
  options: LightFetchOptions = {},
): Promise<T> {
  const baseUrl = options.baseUrl ?? resolveLightBaseUrl();
  const url = `${baseUrl}${appendQuery(path, options.query)}`;
  const headers: Record<string, string> = { Accept: "application/json" };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (options.authenticated) {
    const token = readLightAuthToken(baseUrl);
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const resp = await fetch(url, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    signal: options.signal,
    credentials: "include",
  });

  if (!resp.ok) {
    let data: unknown = null;
    try { data = await resp.json(); } catch { /* ignore */ }
    throw new ApiError(resp.status, resp.statusText, data);
  }

  if (resp.status === 204) return undefined as T;
  const text = await resp.text();
  if (!text) return undefined as T;
  try { return JSON.parse(text) as T; } catch { return undefined as T; }
}

export interface LightConnectOptions {
  authenticated?: boolean;
  signal?: AbortSignal;
  baseUrl?: string;
}

interface ConnectErrorPayload {
  code?: string;
  message?: string;
}

// Calls a Connect-RPC unary method over JSON. `service` is the fully-qualified
// proto path (e.g. "proto.auth.v1.AuthService"), `method` is the RPC's
// PascalCase name. Connect rejects 4xx/5xx with a JSON body shaped
// `{code,message}` — surface that via ApiError so callers can pattern-match
// on `.hasCode("SSO_REQUIRED")` etc.
export async function lightConnect<TReq, TResp = unknown>(
  service: string,
  method: string,
  body: TReq,
  options: LightConnectOptions = {},
): Promise<TResp> {
  const baseUrl = options.baseUrl ?? resolveLightBaseUrl();
  const url = `${baseUrl}/${service}/${method}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Connect-Protocol-Version": "1",
  };
  if (options.authenticated) {
    const token = readLightAuthToken(baseUrl);
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const resp = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(body ?? {}),
    signal: options.signal,
    credentials: "include",
  });

  if (!resp.ok) {
    let payload: ConnectErrorPayload | null = null;
    try { payload = (await resp.json()) as ConnectErrorPayload; } catch { /* ignore */ }
    const code = payload?.code ? String(payload.code).toUpperCase() : undefined;
    const message = payload?.message ?? resp.statusText;
    // Mirror REST error shape so ApiError.serverMessage / hasCode keep
    // working — handlers across the (auth) group key off `data.error` and
    // `data.code` already.
    throw new ApiError(resp.status, message, { code, error: message });
  }

  if (resp.status === 204) return undefined as TResp;
  const text = await resp.text();
  if (!text) return undefined as TResp;
  try { return JSON.parse(text) as TResp; } catch { return undefined as TResp; }
}
