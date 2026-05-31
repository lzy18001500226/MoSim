import {
  relay_encode_input,
  relay_decode_message as wasmDecodeMessage,
  relay_encode_resize as wasmEncodeResize,
  relay_encode_ping,
  relay_encode_control,
  relay_encode_resync,
  relay_encode_acp_command,
} from "@/lib/wasm-core";

export const MsgType = {
  Snapshot: 0x01,
  Output: 0x02,
  Input: 0x03,
  Resize: 0x04,
  Ping: 0x05,
  Pong: 0x06,
  Control: 0x07,
  RunnerDisconnected: 0x08,
  RunnerReconnected: 0x09,
  Resync: 0x0a,
  AcpEvent: 0x0b,
  AcpCommand: 0x0c,
  AcpSnapshot: 0x0d,
} as const;

const encoder = new TextEncoder();

function toBytes(payload: Uint8Array | string): Uint8Array {
  return typeof payload === "string" ? encoder.encode(payload) : payload;
}

export function encodeMessage(msgType: number, payload: Uint8Array | string): Uint8Array {
  const data = toBytes(payload);
  switch (msgType) {
    case MsgType.Input:
      return relay_encode_input(data);
    case MsgType.Control:
      return relay_encode_control(data);
    case MsgType.AcpCommand:
      return relay_encode_acp_command(data);
    case MsgType.Ping:
      return relay_encode_ping();
    case MsgType.Resync:
      return relay_encode_resync();
    default: {
      const msg = new Uint8Array(1 + data.length);
      msg[0] = msgType;
      msg.set(data, 1);
      return msg;
    }
  }
}

export function decodeMessage(data: Uint8Array): { type: number; payload: Uint8Array } {
  const result = wasmDecodeMessage(data);
  if (!result) return { type: 0, payload: new Uint8Array(0) };
  return { type: result.type, payload: new Uint8Array(result.payload) };
}

export function encodeResize(cols: number, rows: number): Uint8Array {
  const full = wasmEncodeResize(cols, rows);
  return full.slice(1);
}

export function encodeJsonMessage(msgType: number, obj: unknown): Uint8Array {
  return encodeMessage(msgType, JSON.stringify(obj));
}

export function decodeJsonPayload<T = unknown>(payload: Uint8Array): T | null {
  try {
    return JSON.parse(new TextDecoder().decode(payload)) as T;
  } catch {
    return null;
  }
}
