import { describe, it, expect, vi, beforeEach } from "vitest";
import { useAuthStore, getAuthToken } from "../auth";

describe("useAuthStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      token: null,
      refreshToken: null,
      user: null,
      isLoading: false,
      error: null,
    });
  });

  describe("initial state", () => {
    it("should have null token", () => {
      expect(useAuthStore.getState().token).toBeNull();
    });

    it("should have null user", () => {
      expect(useAuthStore.getState().user).toBeNull();
    });

    it("should have isLoading false", () => {
      expect(useAuthStore.getState().isLoading).toBe(false);
    });

    it("should have null error", () => {
      expect(useAuthStore.getState().error).toBeNull();
    });
  });

  describe("setAuth", () => {
    it("should set token, refreshToken, and user", () => {
      const user = {
        id: 1,
        email: "admin@test.com",
        username: "admin",
        name: "Admin User",
        avatar_url: null,
        is_system_admin: true,
      };

      useAuthStore.getState().setAuth("token-123", "refresh-456", user);

      const state = useAuthStore.getState();
      expect(state.token).toBe("token-123");
      expect(state.refreshToken).toBe("refresh-456");
      expect(state.user).toEqual(user);
    });

    it("should clear error on setAuth", () => {
      useAuthStore.setState({ error: "some error" });
      useAuthStore.getState().setAuth("t", "r", {
        id: 1,
        email: "a@b.com",
        username: "a",
        name: null,
        avatar_url: null,
        is_system_admin: false,
      });

      expect(useAuthStore.getState().error).toBeNull();
    });
  });

  describe("setUser", () => {
    it("should update user without affecting token", () => {
      useAuthStore.setState({ token: "existing-token" });

      useAuthStore.getState().setUser({
        id: 2,
        email: "updated@test.com",
        username: "updated",
        name: "Updated",
        avatar_url: "https://example.com/avatar.png",
        is_system_admin: true,
      });

      const state = useAuthStore.getState();
      expect(state.token).toBe("existing-token");
      expect(state.user?.email).toBe("updated@test.com");
    });
  });

  describe("logout", () => {
    it("should clear all auth state", () => {
      useAuthStore.setState({
        token: "token-123",
        refreshToken: "refresh-456",
        user: {
          id: 1,
          email: "a@b.com",
          username: "a",
          name: null,
          avatar_url: null,
          is_system_admin: true,
        },
        error: "some error",
      });

      useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.token).toBeNull();
      expect(state.refreshToken).toBeNull();
      expect(state.user).toBeNull();
      expect(state.error).toBeNull();
    });
  });

  describe("setLoading", () => {
    it("should set isLoading to true", () => {
      useAuthStore.getState().setLoading(true);
      expect(useAuthStore.getState().isLoading).toBe(true);
    });

    it("should set isLoading to false", () => {
      useAuthStore.setState({ isLoading: true });
      useAuthStore.getState().setLoading(false);
      expect(useAuthStore.getState().isLoading).toBe(false);
    });
  });

  describe("setError", () => {
    it("should set error message", () => {
      useAuthStore.getState().setError("Login failed");
      expect(useAuthStore.getState().error).toBe("Login failed");
    });

    it("should clear error with null", () => {
      useAuthStore.setState({ error: "previous error" });
      useAuthStore.getState().setError(null);
      expect(useAuthStore.getState().error).toBeNull();
    });
  });
});

describe("getAuthToken", () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null });
  });

  it("should return null when no token", () => {
    expect(getAuthToken()).toBeNull();
  });

  it("should return token from store", () => {
    useAuthStore.setState({ token: "test-token" });
    expect(getAuthToken()).toBe("test-token");
  });
});
