// Node-side Connect-RPC server-stream consumer for the e2e suite.
//
// The unary client (`callConnect` in connect-client.ts) covers 99% of e2e
// needs — POST → JSON response. Realtime tests need the other 1%:
// `EventsService.Subscribe` returns `stream Event`, so we must keep the
// HTTP body open and decode framed messages until the stream closes.
//
// Wire format (Connect streaming, application/connect+proto):
//   per frame: <flags: u8><len: u32 BE><payload: len bytes>
//   flags bit 1 (0x02) set → "end-of-stream" trailer; payload is a small
//     JSON envelope `{ "error": { "code", "message" } }` or empty for a
//     clean close. NB: Connect uses 0x02 for end-stream, not 0x80 like
//     grpc-web — connect-go calls this `connectFlagEnvelopeEndStream`
//     in protocol_connect.go.
//   flags bit 0 (0x01) is reserved for compression (we don't use it).
//   flags bit 1 clear → payload is a proto-encoded response message.
//
// Production clients use the wasm/web-sys variant of this same protocol
// (see clients/core/crates/api-client/src/connect_stream_wasm.rs). The
// Node consumer here exists purely so backend-side broadcast paths can
// be asserted without spinning up two browser contexts.
import {
  create,
  toBinary,
  fromBinary,
  type DescMessage,
  type MessageInitShape,
  type MessageShape,
} from "@bufbuild/protobuf";

import { getApiBaseUrl } from "./env";

export interface StreamCallOpts {
  token?: string | null;
  signal?: AbortSignal;
}

/**
 * Open a Connect server-stream and yield decoded response messages until
 * the stream is closed by either side (clean trailer, network error, or
 * AbortSignal). The caller is responsible for breaking out of the loop
 * (or aborting via the provided signal) once it has seen enough.
 */
export async function* streamConnect<I extends DescMessage, O extends DescMessage>(
  service: string,
  method: string,
  inputSchema: I,
  outputSchema: O,
  input: MessageInitShape<I>,
  opts: StreamCallOpts = {},
): AsyncGenerator<MessageShape<O>> {
  const msg = create(inputSchema, input);
  const reqBody = toBinary(inputSchema, msg);
  // Connect streaming uses its own framing on top of HTTP/1.1 or HTTP/2;
  // requests still carry a single framed request message followed by an
  // EOS frame, but for unary-style server streams the first request is
  // identical to a buffered post. We send the request unframed (most
  // backends accept this for single-request server streams; the Go
  // connect-go server's handleStreaming path tolerates both shapes).
  const headers: Record<string, string> = {
    "Content-Type": "application/connect+proto",
    "Connect-Protocol-Version": "1",
  };
  if (opts.token) headers.Authorization = `Bearer ${opts.token}`;

  // Frame the request body per Connect streaming: <flags=0><len=BE><msg>.
  const framed = new Uint8Array(5 + reqBody.byteLength);
  framed[0] = 0;
  framed[1] = (reqBody.byteLength >>> 24) & 0xff;
  framed[2] = (reqBody.byteLength >>> 16) & 0xff;
  framed[3] = (reqBody.byteLength >>> 8) & 0xff;
  framed[4] = reqBody.byteLength & 0xff;
  framed.set(reqBody, 5);

  const res = await fetch(`${getApiBaseUrl()}/${service}/${method}`, {
    method: "POST",
    headers,
    body: new Blob([framed], { type: "application/connect+proto" }),
    signal: opts.signal,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${service}/${method} stream open failed: ${res.status} ${text}`);
  }
  if (!res.body) {
    throw new Error(`${service}/${method} stream returned empty body`);
  }
  const reader = res.body.getReader();
  let buf = new Uint8Array(0);
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) return;
      if (value && value.byteLength > 0) {
        const merged = new Uint8Array(buf.byteLength + value.byteLength);
        merged.set(buf, 0);
        merged.set(value, buf.byteLength);
        buf = merged;
      }
      while (buf.byteLength >= 5) {
        const flags = buf[0];
        const len =
          (buf[1] << 24) | (buf[2] << 16) | (buf[3] << 8) | buf[4];
        if (buf.byteLength < 5 + len) break;
        const payload = buf.slice(5, 5 + len);
        buf = buf.slice(5 + len);
        if ((flags & 0x02) !== 0) {
          // EOS trailer: JSON envelope or empty (= clean close).
          const text = new TextDecoder().decode(payload);
          if (text.trim().length > 0) {
            try {
              const env = JSON.parse(text) as { error?: { code?: string; message?: string } };
              if (env.error?.code) {
                throw new Error(
                  `${service}/${method} stream error: ${env.error.code}: ${env.error.message ?? ""}`,
                );
              }
            } catch (err) {
              if (err instanceof Error && err.message.startsWith(`${service}/${method} stream error`)) {
                throw err;
              }
              // Non-JSON trailer — treat as clean close.
            }
          }
          return;
        }
        yield fromBinary(outputSchema, payload);
      }
    }
  } finally {
    try { await reader.cancel(); } catch { /* idempotent */ }
  }
}
