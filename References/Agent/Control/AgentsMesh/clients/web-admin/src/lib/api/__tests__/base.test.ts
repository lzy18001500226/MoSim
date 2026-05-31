import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock auth store
const mockGetState = vi.fn();
vi.mock("@/stores/auth", () => ({
  useAuthStore: {
    getState: () => mockGetState(),
  },
  getAuthToken: () => mockGetState().token,
}));

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Must import after mocks are set up
const { apiClient } = await import("../base");

describe("ApiClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetState.mockReturnValue({
      token: "test-token",
      logout: vi.fn(),
    });
  });

  describe("get", () => {
    it("should make a GET request with auth header", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: "test" }),
      });

      const result = await apiClient.get("/users");

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/users"),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer test-token",
            "Content-Type": "application/json",
          }),
        })
      );
      expect(result).toEqual({ data: "test" });
    });

    it("should append query params", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: [] }),
      });

      await apiClient.get("/users", { search: "admin", page: 1 });

      const calledUrl = mockFetch.mock.calls[0][0] as string;
      expect(calledUrl).toContain("search=admin");
      expect(calledUrl).toContain("page=1");
    });

    it("should skip undefined query params", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: [] }),
      });

      await apiClient.get("/users", {
        search: "test",
        status: undefined,
      });

      const calledUrl = mockFetch.mock.calls[0][0] as string;
      expect(calledUrl).toContain("search=test");
      expect(calledUrl).not.toContain("status");
    });

    it("should not include auth header when no token", async () => {
      mockGetState.mockReturnValue({ token: null, logout: vi.fn() });

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({}),
      });

      await apiClient.get("/public");

      const headers = mockFetch.mock.calls[0][1].headers;
      expect(headers["Authorization"]).toBeUndefined();
    });
  });

  describe("post", () => {
    it("should make a POST request with JSON body", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ id: 1 }),
      });

      const body = { email: "admin@test.com", password: "pass" };
      await apiClient.post("/auth/login", body);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/auth/login"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify(body),
        })
      );
    });

    it("should handle POST without body", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ message: "ok" }),
      });

      await apiClient.post("/users/1/disable");

      expect(mockFetch).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          method: "POST",
          body: undefined,
        })
      );
    });
  });

  describe("put", () => {
    it("should make a PUT request", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ id: 1, name: "Updated" }),
      });

      await apiClient.put("/users/1", { name: "Updated" });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/users/1"),
        expect.objectContaining({
          method: "PUT",
          body: JSON.stringify({ name: "Updated" }),
        })
      );
    });
  });

  describe("patch", () => {
    it("should make a PATCH request", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ message: "ok" }),
      });

      await apiClient.patch("/tickets/1/status", { status: "resolved" });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/tickets/1/status"),
        expect.objectContaining({
          method: "PATCH",
          body: JSON.stringify({ status: "resolved" }),
        })
      );
    });
  });

  describe("delete", () => {
    it("should make a DELETE request", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ message: "deleted" }),
      });

      await apiClient.delete("/organizations/1");

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/organizations/1"),
        expect.objectContaining({ method: "DELETE" })
      );
    });

    it("should support DELETE with body", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      });

      await apiClient.delete("/relays/relay-1", {
        migrate_sessions: true,
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          method: "DELETE",
          body: JSON.stringify({ migrate_sessions: true }),
        })
      );
    });
  });

  describe("postFormData", () => {
    it("should send FormData without Content-Type header", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ id: 1 }),
      });

      const formData = new FormData();
      formData.append("content", "hello");

      await apiClient.postFormData("/tickets/1/reply", formData);

      const [, options] = mockFetch.mock.calls[0];
      expect(options.method).toBe("POST");
      expect(options.body).toBe(formData);
      // Should NOT set Content-Type (browser sets multipart boundary)
      expect(options.headers["Content-Type"]).toBeUndefined();
    });

    it("should include auth header when token exists", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ id: 1 }),
      });

      const formData = new FormData();
      await apiClient.postFormData("/upload", formData);

      const [, options] = mockFetch.mock.calls[0];
      expect(options.headers["Authorization"]).toBe("Bearer test-token");
    });

    it("should not include auth header when no token", async () => {
      mockGetState.mockReturnValue({ token: null, logout: vi.fn() });
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ id: 1 }),
      });

      const formData = new FormData();
      await apiClient.postFormData("/upload", formData);

      const [, options] = mockFetch.mock.calls[0];
      expect(options.headers["Authorization"]).toBeUndefined();
    });

    it("should call logout on 401 response", async () => {
      const mockLogout = vi.fn();
      mockGetState.mockReturnValue({
        token: "expired-token",
        logout: mockLogout,
      });

      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ error: "unauthorized" }),
      });

      const formData = new FormData();
      await expect(
        apiClient.postFormData("/upload", formData)
      ).rejects.toEqual(expect.objectContaining({ status: 401 }));
      expect(mockLogout).toHaveBeenCalled();
    });

    it("should throw ApiError on non-ok response", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ error: "Bad request" }),
      });

      const formData = new FormData();
      await expect(
        apiClient.postFormData("/upload", formData)
      ).rejects.toEqual({
        error: "Bad request",
        status: 400,
      });
    });

    it("should fall back to HTTP status on JSON parse failure", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error("invalid")),
      });

      const formData = new FormData();
      await expect(
        apiClient.postFormData("/upload", formData)
      ).rejects.toEqual({
        error: "HTTP 500",
        status: 500,
      });
    });
  });

  describe("error handling", () => {
    it("should throw ApiError on non-ok response", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ error: "Not found" }),
      });

      await expect(apiClient.get("/missing")).rejects.toEqual({
        error: "Not found",
        status: 404,
      });
    });

    it("should fall back to HTTP status text on JSON parse failure", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error("invalid json")),
      });

      await expect(apiClient.get("/error")).rejects.toEqual({
        error: "HTTP 500",
        status: 500,
      });
    });

    it("should call logout on 401 response", async () => {
      const mockLogout = vi.fn();
      mockGetState.mockReturnValue({
        token: "expired-token",
        logout: mockLogout,
      });

      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ error: "unauthorized" }),
      });

      await expect(apiClient.get("/protected")).rejects.toEqual(
        expect.objectContaining({ status: 401 })
      );
      expect(mockLogout).toHaveBeenCalled();
    });
  });
});
