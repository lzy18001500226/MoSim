import { describe, it, expect, vi, beforeEach } from "vitest";

// Users / Organizations / Runners / Dashboard / Audit Logs migrated to Connect-RPC —
// see the per-service tests. Only Auth (login / getCurrentAdmin) still routes
// through REST apiClient.
const mockGet = vi.fn();
const mockPost = vi.fn();
const mockDelete = vi.fn();

vi.mock("../base", () => ({
  apiClient: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
    put: (...args: unknown[]) => vi.fn()(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}));

const mockCallConnect = vi.fn();
vi.mock("@/lib/connect/transport", () => ({
  callConnect: (...args: unknown[]) => mockCallConnect(...args),
  ConnectError: class ConnectError extends Error {},
}));

import {
  getDashboardStats,
  listAuditLogs,
  login,
  getCurrentAdmin,
} from "../admin";

describe("Admin API - REST surface", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Dashboard (Connect-RPC)", () => {
    it("getDashboardStats calls AdminService.GetDashboardStats and converts bigint", async () => {
      mockCallConnect.mockResolvedValue({
        totalUsers: 100n,
        activeUsers: 80n,
        totalOrganizations: 10n,
        totalRunners: 5n,
        onlineRunners: 4n,
        totalPods: 20n,
        activePods: 12n,
        totalSubscriptions: 8n,
        activeSubscriptions: 6n,
        newUsersToday: 3n,
        newUsersThisWeek: 15n,
        newUsersThisMonth: 50n,
      });
      const result = await getDashboardStats();
      expect(mockCallConnect.mock.calls[0][0]).toBe("proto.admin.v1.AdminService");
      expect(mockCallConnect.mock.calls[0][1]).toBe("GetDashboardStats");
      expect(result.total_users).toBe(100);
      expect(result.active_users).toBe(80);
      expect(result.new_users_this_month).toBe(50);
    });
  });

  describe("Audit Logs (Connect-RPC)", () => {
    it("listAuditLogs calls AdminService.ListAuditLogs with mapped params", async () => {
      mockCallConnect.mockResolvedValue({
        items: [],
        total: 0n,
        page: 1,
        pageSize: 50,
        totalPages: 0,
      });
      await listAuditLogs({ target_type: "user", page: 1, page_size: 50 });
      expect(mockCallConnect).toHaveBeenCalledWith(
        "proto.admin.v1.AdminService",
        "ListAuditLogs",
        expect.anything(),
        expect.anything(),
        expect.objectContaining({ targetType: "user", page: 1, pageSize: 50 }),
      );
    });

    it("listAuditLogs maps bigint target_id and admin_user_id", async () => {
      mockCallConnect.mockResolvedValue({
        items: [
          {
            id: 7n,
            adminUserId: 3n,
            action: "user.disable",
            targetType: "user",
            targetId: 42n,
            oldData: undefined,
            newData: undefined,
            ipAddress: "10.0.0.1",
            userAgent: undefined,
            createdAt: "2026-05-01T00:00:00Z",
            adminUser: {
              id: 3n,
              email: "a@b.com",
              username: "admin",
              name: undefined,
              avatarUrl: undefined,
            },
          },
        ],
        total: 1n,
        page: 1,
        pageSize: 20,
        totalPages: 1,
      });
      const result = await listAuditLogs({ admin_user_id: 3, target_id: 42 });
      expect(mockCallConnect.mock.calls[0][4]).toEqual(
        expect.objectContaining({ adminUserId: 3n, targetId: 42n }),
      );
      expect(result.data[0].id).toBe(7);
      expect(result.data[0].target_id).toBe(42);
      expect(result.data[0].admin_user?.id).toBe(3);
      expect(result.total).toBe(1);
    });
  });

  describe("Auth", () => {
    it("login calls AdminAuthService.Login via Connect-RPC", async () => {
      mockCallConnect.mockResolvedValue({
        token: "t",
        refreshToken: "rt",
        user: { id: 1n, email: "admin@test.com", username: "admin", isSystemAdmin: true },
      });
      await login({ email: "admin@test.com", password: "pass" });
      expect(mockCallConnect.mock.calls[0][0]).toBe("proto.admin.v1.AdminAuthService");
      expect(mockCallConnect.mock.calls[0][1]).toBe("Login");
      expect(mockCallConnect.mock.calls[0][4]).toEqual(
        expect.objectContaining({ email: "admin@test.com", password: "pass" }),
      );
    });

    it("getCurrentAdmin calls AdminSessionService.GetMe via Connect-RPC", async () => {
      mockCallConnect.mockResolvedValue({ id: 1n, isSystemAdmin: true });
      await getCurrentAdmin();
      expect(mockCallConnect.mock.calls[0][0]).toBe("proto.admin.v1.AdminAuthSessionService");
      expect(mockCallConnect.mock.calls[0][1]).toBe("GetMe");
    });
  });
});
