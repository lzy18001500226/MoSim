import { describe, it, expect, vi, beforeEach } from "vitest";

const mockCallConnect = vi.fn();
vi.mock("@/lib/connect/transport", () => ({
  callConnect: (...args: unknown[]) => mockCallConnect(...args),
}));

import {
  listPromoCodes,
  getPromoCode,
  createPromoCode,
  updatePromoCode,
  activatePromoCode,
  deactivatePromoCode,
  deletePromoCode,
  listPromoCodeRedemptions,
} from "../adminPromoCodes";

const SERVICE = "proto.promocode.v1.PromoCodeAdminService";

function protoPromoCode(overrides: Record<string, unknown> = {}) {
  return {
    id: BigInt(1),
    code: "TEST50",
    name: "Test Promo",
    description: "desc",
    type: "campaign",
    planName: "pro",
    durationMonths: 3,
    maxUses: 100,
    usedCount: 5,
    maxUsesPerOrg: 1,
    startsAt: "2026-01-01T00:00:00Z",
    expiresAt: "2026-06-01T00:00:00Z",
    isActive: true,
    createdById: BigInt(42),
    createdAt: "2026-01-01T00:00:00Z",
    updatedAt: "2026-01-02T00:00:00Z",
    ...overrides,
  };
}

describe("adminPromoCodes (Connect-RPC)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("listPromoCodes", () => {
    it("invokes ListPromoCodes with camelCase params and normalizes paging", async () => {
      mockCallConnect.mockResolvedValue({
        data: [protoPromoCode()],
        total: BigInt(1),
        page: 2,
        pageSize: 25,
        totalPages: 1,
      });
      const out = await listPromoCodes({
        search: "TEST",
        type: "campaign",
        plan_name: "pro",
        is_active: true,
        page: 2,
        page_size: 25,
      });
      expect(mockCallConnect.mock.calls[0][0]).toBe(SERVICE);
      expect(mockCallConnect.mock.calls[0][1]).toBe("ListPromoCodes");
      expect(mockCallConnect.mock.calls[0][4]).toEqual({
        type: "campaign",
        planName: "pro",
        isActive: true,
        search: "TEST",
        page: 2,
        pageSize: 25,
      });
      expect(out.total).toBe(1);
      expect(out.page).toBe(2);
      expect(out.page_size).toBe(25);
      expect(out.total_pages).toBe(1);
      expect(out.data[0]).toMatchObject({
        id: 1,
        code: "TEST50",
        plan_name: "pro",
        duration_months: 3,
        max_uses: 100,
        used_count: 5,
        max_uses_per_org: 1,
        is_active: true,
        created_by_id: 42,
      });
    });

    it("passes undefined for omitted params", async () => {
      mockCallConnect.mockResolvedValue({
        data: [],
        total: BigInt(0),
        page: 1,
        pageSize: 0,
        totalPages: 0,
      });
      await listPromoCodes();
      expect(mockCallConnect.mock.calls[0][4]).toEqual({
        type: undefined,
        planName: undefined,
        isActive: undefined,
        search: undefined,
        page: undefined,
        pageSize: undefined,
      });
    });
  });

  describe("getPromoCode", () => {
    it("invokes GetPromoCode with bigint id and converts response", async () => {
      mockCallConnect.mockResolvedValue(protoPromoCode({ id: BigInt(10) }));
      const out = await getPromoCode(10);
      expect(mockCallConnect.mock.calls[0][1]).toBe("GetPromoCode");
      expect(mockCallConnect.mock.calls[0][4]).toEqual({ id: BigInt(10) });
      expect(out.id).toBe(10);
      expect(out.code).toBe("TEST50");
    });
  });

  describe("createPromoCode", () => {
    it("invokes CreatePromoCode with camelCase + defaults", async () => {
      mockCallConnect.mockResolvedValue(protoPromoCode({ id: BigInt(7) }));
      await createPromoCode({
        code: "NEW10",
        name: "Hello",
        type: "campaign",
        plan_name: "starter",
        duration_months: 1,
        max_uses: 50,
        starts_at: "2026-01-01T00:00:00Z",
        expires_at: "2026-12-31T00:00:00Z",
      });
      expect(mockCallConnect.mock.calls[0][1]).toBe("CreatePromoCode");
      expect(mockCallConnect.mock.calls[0][4]).toEqual({
        code: "NEW10",
        name: "Hello",
        description: "",
        type: "campaign",
        planName: "starter",
        durationMonths: 1,
        maxUses: 50,
        maxUsesPerOrg: 0,
        startsAt: "2026-01-01T00:00:00Z",
        expiresAt: "2026-12-31T00:00:00Z",
      });
    });

    it("preserves provided description and max_uses_per_org", async () => {
      mockCallConnect.mockResolvedValue(protoPromoCode());
      await createPromoCode({
        code: "X",
        name: "Y",
        description: "explicit",
        type: "individual",
        plan_name: "pro",
        duration_months: 2,
        max_uses: 1,
        max_uses_per_org: 9,
        starts_at: "2026-01-01T00:00:00Z",
        expires_at: "",
      });
      const req = mockCallConnect.mock.calls[0][4];
      expect(req.description).toBe("explicit");
      expect(req.maxUsesPerOrg).toBe(9);
    });
  });

  describe("updatePromoCode", () => {
    it("emits clearExpiresAt=true when expires_at is empty string", async () => {
      mockCallConnect.mockResolvedValue(protoPromoCode({ id: BigInt(5) }));
      await updatePromoCode(5, { name: "Renamed", expires_at: "" });
      expect(mockCallConnect.mock.calls[0][1]).toBe("UpdatePromoCode");
      const req = mockCallConnect.mock.calls[0][4];
      expect(req).toMatchObject({
        id: BigInt(5),
        name: "Renamed",
        clearExpiresAt: true,
      });
      expect(req.expiresAt).toBeUndefined();
    });

    it("forwards new expires_at when non-empty and clearExpiresAt=false", async () => {
      mockCallConnect.mockResolvedValue(protoPromoCode());
      await updatePromoCode(5, { expires_at: "2027-01-01T00:00:00Z" });
      const req = mockCallConnect.mock.calls[0][4];
      expect(req.expiresAt).toBe("2027-01-01T00:00:00Z");
      expect(req.clearExpiresAt).toBe(false);
    });

    it("leaves clearExpiresAt=false when expires_at is omitted", async () => {
      mockCallConnect.mockResolvedValue(protoPromoCode());
      await updatePromoCode(5, { name: "Just renamed" });
      const req = mockCallConnect.mock.calls[0][4];
      expect(req.clearExpiresAt).toBe(false);
      expect(req.expiresAt).toBeUndefined();
    });
  });

  describe("lifecycle endpoints", () => {
    it("activatePromoCode invokes ActivatePromoCode and returns {message}", async () => {
      mockCallConnect.mockResolvedValue({ message: "activated" });
      const out = await activatePromoCode(8);
      expect(mockCallConnect.mock.calls[0][1]).toBe("ActivatePromoCode");
      expect(mockCallConnect.mock.calls[0][4]).toEqual({ id: BigInt(8) });
      expect(out).toEqual({ message: "activated" });
    });

    it("deactivatePromoCode invokes DeactivatePromoCode and returns {message}", async () => {
      mockCallConnect.mockResolvedValue({ message: "deactivated" });
      const out = await deactivatePromoCode(8);
      expect(mockCallConnect.mock.calls[0][1]).toBe("DeactivatePromoCode");
      expect(mockCallConnect.mock.calls[0][4]).toEqual({ id: BigInt(8) });
      expect(out).toEqual({ message: "deactivated" });
    });

    it("deletePromoCode invokes DeletePromoCode and returns {message}", async () => {
      mockCallConnect.mockResolvedValue({ message: "deleted" });
      const out = await deletePromoCode(8);
      expect(mockCallConnect.mock.calls[0][1]).toBe("DeletePromoCode");
      expect(mockCallConnect.mock.calls[0][4]).toEqual({ id: BigInt(8) });
      expect(out).toEqual({ message: "deleted" });
    });
  });

  describe("listPromoCodeRedemptions", () => {
    it("invokes ListPromoCodeRedemptions and maps redemption rows", async () => {
      mockCallConnect.mockResolvedValue({
        data: [
          {
            id: BigInt(101),
            promoCodeId: BigInt(5),
            organizationId: BigInt(7),
            userId: BigInt(42),
            planName: "pro",
            durationMonths: 3,
            newPeriodEnd: "2026-09-01T00:00:00Z",
            ipAddress: "10.0.0.1",
            createdAt: "2026-03-01T00:00:00Z",
            userEmail: "u@example.com",
            userUsername: "uname",
            organizationName: "Acme",
            organizationSlug: "acme",
          },
        ],
        total: BigInt(1),
        page: 1,
        pageSize: 20,
        totalPages: 1,
      });
      const out = await listPromoCodeRedemptions(5, { page: 1, page_size: 20 });
      expect(mockCallConnect.mock.calls[0][1]).toBe("ListPromoCodeRedemptions");
      expect(mockCallConnect.mock.calls[0][4]).toEqual({
        id: BigInt(5),
        page: 1,
        pageSize: 20,
      });
      expect(out.total).toBe(1);
      expect(out.data[0]).toMatchObject({
        id: 101,
        promo_code_id: 5,
        organization_id: 7,
        user_id: 42,
        plan_name: "pro",
        ip_address: "10.0.0.1",
      });
      expect(out.data[0].user).toMatchObject({
        id: 42,
        email: "u@example.com",
        username: "uname",
      });
      expect(out.data[0].organization).toMatchObject({
        id: 7,
        name: "Acme",
        slug: "acme",
      });
    });

    it("omits user/org when display fields are absent", async () => {
      mockCallConnect.mockResolvedValue({
        data: [
          {
            id: BigInt(1),
            promoCodeId: BigInt(5),
            organizationId: BigInt(7),
            userId: BigInt(42),
            planName: "pro",
            durationMonths: 3,
            newPeriodEnd: "2026-09-01T00:00:00Z",
            createdAt: "2026-03-01T00:00:00Z",
          },
        ],
        total: BigInt(1),
        page: 1,
        pageSize: 10,
        totalPages: 1,
      });
      const out = await listPromoCodeRedemptions(5);
      expect(out.data[0].user).toBeUndefined();
      expect(out.data[0].organization).toBeUndefined();
      expect(out.data[0].ip_address).toBeNull();
    });
  });
});
