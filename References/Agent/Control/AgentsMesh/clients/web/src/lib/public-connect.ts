// Plain-fetch Connect-RPC client for marketing pages. Mirrors the
// web-admin transport (clients/web-admin/src/lib/connect/transport.ts):
// no wasm, no @/lib/wasm-core import — only @bufbuild/protobuf + fetch.
//
// Why a separate transport: the dashboard / auth / popout layouts mount
// WasmProvider and call Connect through the wasm bridge (binary in/out via
// wasm-bindgen). Marketing routes (`/`, `/docs`, ...) MUST stay wasm-free
// (see CLAUDE.md §"Wasm 加载边界") — they reach the backend through this
// module instead.
//
// Wire format: HTTP POST to /<service>/<method> with application/proto
// body. Auth header is omitted because every consumer here calls a public
// (no-auth) RPC.
import {
  create,
  toBinary,
  fromBinary,
  type DescMessage,
  type MessageInitShape,
  type MessageShape,
} from "@bufbuild/protobuf";

import { getApiBaseUrl } from "./env";

function resolveBase(): string {
  const cfg = getApiBaseUrl();
  if (cfg) return cfg;
  if (typeof window !== "undefined") return window.location.origin;
  return "";
}

export class PublicConnectError extends Error {
  readonly code: string;
  readonly status: number;
  constructor(message: string, code: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

export async function callPublicConnect<I extends DescMessage, O extends DescMessage>(
  service: string,
  method: string,
  inputSchema: I,
  outputSchema: O,
  input: MessageInitShape<I>,
): Promise<MessageShape<O>> {
  const msg = create(inputSchema, input);
  const body = toBinary(inputSchema, msg);

  const url = `${resolveBase()}/${service}/${method}`;
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/proto" },
    body,
    cache: "no-store",
  });

  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`;
    let code = "unknown";
    try {
      const err = (await resp.json()) as { code?: string; message?: string };
      detail = err.message || detail;
      code = err.code || code;
    } catch {
      // body wasn't JSON — keep default detail
    }
    throw new PublicConnectError(detail, code, resp.status);
  }

  const buf = new Uint8Array(await resp.arrayBuffer());
  return fromBinary(outputSchema, buf);
}
