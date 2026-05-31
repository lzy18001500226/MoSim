/**
 * Test mock for @/lib/wasm-core.
 * Provides pure-JS implementations of the relay protocol functions
 * so tests don't need real WASM initialization.
 */
import { vi } from "vitest";

function encodeU16(val: number): [number, number] {
  return [(val >> 8) & 0xff, val & 0xff];
}

export function relay_encode_input(data: Uint8Array): Uint8Array {
  const msg = new Uint8Array(1 + data.length);
  msg[0] = 0x03; // MsgType.Input
  msg.set(data, 1);
  return msg;
}

export function relay_encode_resize(cols: number, rows: number): Uint8Array {
  const [ch, cl] = encodeU16(cols);
  const [rh, rl] = encodeU16(rows);
  return new Uint8Array([0x04, ch, cl, rh, rl]); // MsgType.Resize
}

export function relay_encode_ping(): Uint8Array {
  return new Uint8Array([0x05]); // MsgType.Ping
}

export function relay_encode_control(data: Uint8Array): Uint8Array {
  const msg = new Uint8Array(1 + data.length);
  msg[0] = 0x07; // MsgType.Control
  msg.set(data, 1);
  return msg;
}

export function relay_encode_resync(): Uint8Array {
  return new Uint8Array([0x0a]); // MsgType.Resync
}

export function relay_encode_acp_command(data: Uint8Array): Uint8Array {
  const msg = new Uint8Array(1 + data.length);
  msg[0] = 0x0c; // MsgType.AcpCommand
  msg.set(data, 1);
  return msg;
}

export function relay_decode_message(
  data: Uint8Array,
): { type: number; payload: Uint8Array } | null {
  if (!data || data.length === 0) return null;
  return { type: data[0], payload: data.slice(1) };
}

export const initWasmCore = vi.fn().mockResolvedValue(undefined);
export const getApiClient = vi.fn().mockReturnValue({});
export const getAuthManager = vi.fn().mockReturnValue({
  get_token: vi.fn().mockReturnValue("mock-token"),
});
export const getPodService = vi.fn().mockReturnValue({
  get_pod_connection: vi.fn().mockResolvedValue(
    JSON.stringify({
      relay_url: "wss://relay.example.com",
      token: "test-token",
      pod_key: "pod-1",
    })
  ),
});
export const getRelayManager = vi.fn().mockReturnValue({
  subscribe: vi.fn().mockResolvedValue(undefined),
  unsubscribe: vi.fn().mockResolvedValue(undefined),
  send: vi.fn().mockResolvedValue(undefined),
  send_resize: vi.fn().mockResolvedValue(undefined),
  force_resize: vi.fn().mockResolvedValue(undefined),
  send_acp_command: vi.fn().mockResolvedValue(undefined),
  on_status_change: vi.fn().mockResolvedValue(undefined),
  on_acp_message: vi.fn().mockResolvedValue(undefined),
  get_status: vi.fn().mockResolvedValue("disconnected"),
  is_runner_disconnected: vi.fn().mockResolvedValue(false),
  get_pod_size: vi.fn().mockResolvedValue(null),
  disconnect: vi.fn().mockResolvedValue(undefined),
  disconnect_all: vi.fn().mockResolvedValue(undefined),
});

export class WasmEventsManager {
  constructor() {}
  connect = vi.fn().mockResolvedValue(undefined);
  disconnect = vi.fn().mockResolvedValue(undefined);
  subscribe = vi.fn().mockResolvedValue(0);
  subscribe_all = vi.fn().mockResolvedValue(0);
  unsubscribe = vi.fn().mockResolvedValue(undefined);
  on_connection_state_change = vi.fn().mockResolvedValue(0);
  get_connection_state = vi.fn().mockResolvedValue("disconnected");
}

export class WasmWebSocket {
  static connect = vi.fn().mockReturnValue({
    send_binary: vi.fn(),
    send_text: vi.fn(),
    close: vi.fn(),
    is_open: vi.fn().mockReturnValue(false),
    is_closed: vi.fn().mockReturnValue(true),
  });
}
