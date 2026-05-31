import { describe, expect, it, vi, beforeEach, afterEach, type Mock } from "vitest";

vi.mock("@/lib/wasm-core", () => import("@/test/__mocks__/wasm-core"));
vi.mock("@/lib/api/facade/podConnect", () => ({
  getPodConnection: vi.fn().mockResolvedValue({
    relay_url: "wss://relay.example.com",
    token: "test-token",
    pod_key: "pod-1",
  }),
}));

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type MockSend = Mock<(...args: any[]) => any>;

let lastCreatedWs: MockWebSocket | null = null;

class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  url: string;
  readyState: number = MockWebSocket.CONNECTING;
  binaryType: string = "blob";
  onopen: (() => void) | null = null;
  onclose: ((e: { code: number; reason: string }) => void) | null = null;
  onerror: ((e: unknown) => void) | null = null;
  onmessage: ((e: { data: unknown }) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    const self = this;
    lastCreatedWs = self;
    setTimeout(() => {
      self.readyState = MockWebSocket.OPEN;
      self.onopen?.();
    }, 0);
  }

  send = vi.fn();
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED;
  });
}

global.WebSocket = MockWebSocket as unknown as typeof WebSocket;

describe("relayConnection - resize", () => {
  let pool: typeof import("@/stores/relayConnection").relayPool;

  beforeEach(async () => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    vi.resetModules();
    lastCreatedWs = null;
    const importedModule = await import("@/stores/relayConnection");
    pool = importedModule.relayPool;
  });

  afterEach(() => {
    pool?.disconnectAll();
    vi.useRealTimers();
  });

  function getWsSend(): MockSend {
    return lastCreatedWs!.send as MockSend;
  }

  describe("sendResize", () => {
    it("should not throw for invalid dimensions", async () => {
      const onMessage = vi.fn();
      await pool.subscribe("pod-1", "sub-1", onMessage);
      await vi.runAllTimersAsync();

      expect(() => pool.sendResize("pod-1", 0, 0)).not.toThrow();
      expect(() => pool.sendResize("pod-1", -1, 24)).not.toThrow();
    });

    it("should send resize message when connection is open", async () => {
      const onMessage = vi.fn();
      await pool.subscribe("pod-1", "sub-1", onMessage);
      await vi.runAllTimersAsync();

      const conn = pool.getConnection("pod-1");
      expect(conn).toBeDefined();
      expect(conn!.transport.isOpen).toBe(true);

      pool.sendResize("pod-1", 120, 40);
      await vi.advanceTimersByTimeAsync(200);

      const send = getWsSend();
      expect(send).toHaveBeenCalled();
      const lastCall = send.mock.calls[send.mock.calls.length - 1];
      const sentData = lastCall[0] as Uint8Array;

      expect(sentData[0]).toBe(0x04); // MsgType.Resize
      expect((sentData[1] << 8) | sentData[2]).toBe(120);
      expect((sentData[3] << 8) | sentData[4]).toBe(40);
    });

    it("should not send resize for non-existent connection", async () => {
      pool.sendResize("unknown-pod", 80, 24);
      await vi.advanceTimersByTimeAsync(200);

      expect(pool.getConnection("unknown-pod")).toBeUndefined();
    });
  });

  describe("forceResize", () => {
    it("should send resize immediately when connection is open", async () => {
      const onMessage = vi.fn();
      await pool.subscribe("pod-1", "sub-1", onMessage);
      await vi.runAllTimersAsync();

      const conn = pool.getConnection("pod-1");
      expect(conn).toBeDefined();
      const send = getWsSend();
      const sendCallsBefore = send.mock.calls.length;

      pool.forceResize("pod-1", 100, 30);

      expect(send.mock.calls.length).toBe(sendCallsBefore + 1);
      const lastCall = send.mock.calls[send.mock.calls.length - 1];
      const sentData = lastCall[0] as Uint8Array;

      expect(sentData[0]).toBe(0x04);
      expect((sentData[1] << 8) | sentData[2]).toBe(100);
      expect((sentData[3] << 8) | sentData[4]).toBe(30);
    });

    it("should queue pendingResize when connection is connecting", async () => {
      const onMessage = vi.fn();

      const subscribePromise = pool.subscribe("pod-1", "sub-1", onMessage);
      await Promise.resolve();

      const conn = pool.getConnection("pod-1");
      expect(conn).toBeDefined();
      expect(conn!.transport.isOpen).toBe(false);
      expect(conn!.transport.isClosed).toBe(false);

      pool.forceResize("pod-1", 80, 24);

      expect(conn!.pendingResize).toEqual({ rows: 24, cols: 80 });

      await vi.runAllTimersAsync();
      await subscribePromise;

      expect(conn!.pendingResize).toBeUndefined();

      const send = getWsSend();
      const resizeCalls = send.mock.calls.filter((call: unknown[]) => {
        const data = call[0] as Uint8Array;
        return data[0] === 0x04;
      });
      expect(resizeCalls.length).toBeGreaterThan(0);
    });

    it("should not throw for non-existent connection", () => {
      expect(() => pool.forceResize("unknown-pod", 80, 24)).not.toThrow();
    });

    it("should not send resize for invalid dimensions", async () => {
      const onMessage = vi.fn();
      await pool.subscribe("pod-1", "sub-1", onMessage);
      await vi.runAllTimersAsync();

      const send = getWsSend();
      const sendCallsBefore = send.mock.calls.length;

      pool.forceResize("pod-1", 0, 24);
      pool.forceResize("pod-1", 80, 0);
      pool.forceResize("pod-1", -1, 24);
      pool.forceResize("pod-1", 80, -1);

      expect(send.mock.calls.length).toBe(sendCallsBefore);
    });

    it("should send resize after reconnection", async () => {
      const onMessage1 = vi.fn();
      const onMessage2 = vi.fn();

      await pool.subscribe("pod-1", "sub-1", onMessage1);
      await vi.runAllTimersAsync();

      await pool.subscribe("pod-1", "sub-2", onMessage2);
      await vi.runAllTimersAsync();

      const conn = pool.getConnection("pod-1");
      expect(conn).toBeDefined();
      expect(conn!.transport.isOpen).toBe(true);

      const send = getWsSend();
      const sendCallsBefore = send.mock.calls.length;

      pool.forceResize("pod-1", 120, 40);

      expect(send.mock.calls.length).toBe(sendCallsBefore + 1);
      const lastCall = send.mock.calls[send.mock.calls.length - 1];
      const sentData = lastCall[0] as Uint8Array;
      expect(sentData[0]).toBe(0x04);
    });
  });

  describe("getPodSize", () => {
    it("should return undefined for unknown pod", () => {
      expect(pool.getPodSize("unknown")).toBeUndefined();
    });
  });
});
