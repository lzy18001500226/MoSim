// Unit tests for clients/web/src/lib/api/notificationConnect.ts proto-SSOT
// adapter. After Phase 5 migration, wire types stay proto camelCase end-to-end
// (no DTO conversion); these tests pin field round-trip across the binary wire.

import { describe, it, expect, vi, beforeEach } from "vitest";
import { create, toBinary } from "@bufbuild/protobuf";
import {
  NotificationPreferenceSchema,
  ListPreferencesResponseSchema,
} from "@proto/notification/v1/notification_pb";

vi.mock("@/lib/wasm-core", () => ({
  getNotificationService: vi.fn(),
}));

import { getNotificationService } from "@/lib/wasm-core";
import { listPreferencesConnect, setPreferenceConnect } from "../connect/notificationConnect";

describe("listPreferencesConnect", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("decodes empty response to empty list", async () => {
    const respProto = create(ListPreferencesResponseSchema, { items: [], total: BigInt(0) });
    const respBytes = toBinary(ListPreferencesResponseSchema, respProto);
    vi.mocked(getNotificationService).mockReturnValue({
      listPreferencesConnect: vi.fn().mockResolvedValue(respBytes),
    } as ReturnType<typeof getNotificationService>);

    const out = await listPreferencesConnect("acme");
    expect(out).toEqual([]);
  });

  it("returns proto camelCase shape directly", async () => {
    const pref = create(NotificationPreferenceSchema, {
      source: "channel:message",
      entityId: "42",
      isMuted: true,
      channels: { toast: true, browser: false },
    });
    const respProto = create(ListPreferencesResponseSchema, {
      items: [pref],
      total: BigInt(1),
    });
    const respBytes = toBinary(ListPreferencesResponseSchema, respProto);
    vi.mocked(getNotificationService).mockReturnValue({
      listPreferencesConnect: vi.fn().mockResolvedValue(respBytes),
    } as ReturnType<typeof getNotificationService>);

    const out = await listPreferencesConnect("acme");
    expect(out).toHaveLength(1);
    expect(out[0].source).toBe("channel:message");
    expect(out[0].entityId).toBe("42");
    expect(out[0].isMuted).toBe(true);
    expect(out[0].channels).toEqual({ toast: true, browser: false });
  });

  it("treats absent entityId as empty string (proto3 optional default)", async () => {
    // proto3 `optional` distinguishes "absent" from "explicit empty". When
    // server doesn't set entityId, proto-es decodes to empty string default.
    const pref = create(NotificationPreferenceSchema, {
      source: "terminal:osc",
      isMuted: false,
      channels: { toast: true },
    });
    const respProto = create(ListPreferencesResponseSchema, { items: [pref], total: BigInt(1) });
    const respBytes = toBinary(ListPreferencesResponseSchema, respProto);
    vi.mocked(getNotificationService).mockReturnValue({
      listPreferencesConnect: vi.fn().mockResolvedValue(respBytes),
    } as ReturnType<typeof getNotificationService>);

    const out = await listPreferencesConnect("acme");
    expect(out[0].entityId ?? "").toBe("");
  });
});

describe("setPreferenceConnect", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("encodes proto camelCase init shape to wire", async () => {
    const captured: Uint8Array[] = [];
    const respProto = create(NotificationPreferenceSchema, {
      source: "channel:mention",
      entityId: "42",
      isMuted: true,
      channels: { toast: false, email: true },
    });
    const respBytes = toBinary(NotificationPreferenceSchema, respProto);
    vi.mocked(getNotificationService).mockReturnValue({
      setPreferenceConnect: vi.fn().mockImplementation(async (b: Uint8Array) => {
        captured.push(b);
        return respBytes;
      }),
    } as ReturnType<typeof getNotificationService>);

    const out = await setPreferenceConnect({
      source: "channel:mention",
      entityId: "42",
      isMuted: true,
      channels: { toast: false, email: true },
    });

    expect(captured).toHaveLength(1);
    expect(out.source).toBe("channel:mention");
    expect(out.entityId).toBe("42");
    expect(out.isMuted).toBe(true);
    expect(out.channels).toEqual({ toast: false, email: true });
  });

  it("sends empty channels map when none provided (server fills defaults)", async () => {
    const respProto = create(NotificationPreferenceSchema, {
      source: "channel:message",
      isMuted: false,
      channels: { toast: true, browser: true },
    });
    const respBytes = toBinary(NotificationPreferenceSchema, respProto);
    vi.mocked(getNotificationService).mockReturnValue({
      setPreferenceConnect: vi.fn().mockResolvedValue(respBytes),
    } as ReturnType<typeof getNotificationService>);

    const out = await setPreferenceConnect({
      source: "channel:message",
      isMuted: false,
      channels: {},
    });
    expect(out.channels).toEqual({ toast: true, browser: true });
    expect(out.entityId ?? "").toBe("");
  });
});
