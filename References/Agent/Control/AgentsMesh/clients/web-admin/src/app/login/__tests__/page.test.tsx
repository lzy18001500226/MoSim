import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

// Mock next/navigation
const mockReplace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: mockReplace }),
}));

// Mock sonner toast
const mockToastSuccess = vi.fn();
const mockToastError = vi.fn();
vi.mock("sonner", () => ({
  toast: {
    success: (...args: unknown[]) => mockToastSuccess(...args),
    error: (...args: unknown[]) => mockToastError(...args),
  },
}));

// Mock auth store
const mockSetAuth = vi.fn();
const mockAuthState = { token: null as string | null, setAuth: mockSetAuth };
vi.mock("@/stores/auth", () => ({
  useAuthStore: () => mockAuthState,
}));

// Mock login API
const mockLogin = vi.fn();
vi.mock("@/lib/api/admin", () => ({
  login: (req: unknown) => mockLogin(req),
}));

import LoginPage from "../page";

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthState.token = null;
  });

  it("should render login form", () => {
    render(<LoginPage />);
    expect(screen.getByText("Admin Console")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign In" })).toBeInTheDocument();
  });

  it("should render description text", () => {
    render(<LoginPage />);
    expect(
      screen.getByText(/Sign in with your administrator account/)
    ).toBeInTheDocument();
  });

  it("should render admin-only notice", () => {
    render(<LoginPage />);
    expect(
      screen.getByText(/Only users with system administrator privileges/)
    ).toBeInTheDocument();
  });

  it("should redirect to / if already authenticated", async () => {
    mockAuthState.token = "existing-token";
    render(<LoginPage />);
    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith("/");
    });
  });

  it("should show error toast when submitting empty form", async () => {
    render(<LoginPage />);
    fireEvent.click(screen.getByRole("button", { name: "Sign In" }));
    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith(
        "Please enter email and password"
      );
    });
  });

  it("should call login API on valid submit", async () => {
    mockLogin.mockResolvedValue({
      token: "new-token",
      refresh_token: "new-refresh",
      user: {
        id: 1,
        email: "admin@test.com",
        username: "admin",
        name: "Admin",
        avatar_url: null,
        is_system_admin: true,
      },
    });

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "admin@test.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign In" }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: "admin@test.com",
        password: "password123",
      });
    });
  });

  it("should call setAuth and redirect on successful login", async () => {
    const mockUser = {
      id: 1,
      email: "admin@test.com",
      username: "admin",
      name: "Admin",
      avatar_url: null,
      is_system_admin: true,
    };
    mockLogin.mockResolvedValue({
      token: "new-token",
      refresh_token: "new-refresh",
      user: mockUser,
    });

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "admin@test.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "pass" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign In" }));

    await waitFor(() => {
      expect(mockSetAuth).toHaveBeenCalledWith(
        "new-token",
        "new-refresh",
        mockUser
      );
      expect(mockToastSuccess).toHaveBeenCalledWith("Welcome back, Admin!");
      expect(mockReplace).toHaveBeenCalledWith("/");
    });
  });

  it("should show error toast on login failure", async () => {
    mockLogin.mockRejectedValue({ error: "Invalid credentials" });

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "admin@test.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "wrong" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign In" }));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith("Invalid credentials");
    });
  });

  it("should show generic error when error object has no message", async () => {
    mockLogin.mockRejectedValue({});

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "a@b.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "x" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign In" }));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith(
        "Login failed. Please check your credentials."
      );
    });
  });

  it("should show loading state during submission", async () => {
    // Never resolve to keep loading state
    mockLogin.mockReturnValue(new Promise(() => {}));

    render(<LoginPage />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "a@b.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "x" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign In" }));

    await waitFor(() => {
      expect(screen.getByText("Signing in...")).toBeInTheDocument();
    });
  });
});
