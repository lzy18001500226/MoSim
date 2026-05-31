import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

// Mock sonner toast
const mockToastSuccess = vi.fn();
const mockToastError = vi.fn();
vi.mock("sonner", () => ({
  toast: {
    success: (...args: unknown[]) => mockToastSuccess(...args),
    error: (...args: unknown[]) => mockToastError(...args),
  },
}));

// Mock admin API
const mockListUsers = vi.fn();
const mockDisableUser = vi.fn();
const mockEnableUser = vi.fn();
const mockGrantAdmin = vi.fn();
const mockRevokeAdmin = vi.fn();
const mockVerifyUserEmail = vi.fn();
const mockUnverifyUserEmail = vi.fn();

vi.mock("@/lib/api/admin", () => ({
  listUsers: (...args: unknown[]) => mockListUsers(...args),
  disableUser: (...args: unknown[]) => mockDisableUser(...args),
  enableUser: (...args: unknown[]) => mockEnableUser(...args),
  grantAdmin: (...args: unknown[]) => mockGrantAdmin(...args),
  revokeAdmin: (...args: unknown[]) => mockRevokeAdmin(...args),
  verifyUserEmail: (...args: unknown[]) => mockVerifyUserEmail(...args),
  unverifyUserEmail: (...args: unknown[]) => mockUnverifyUserEmail(...args),
}));

import UsersPage from "../page";

const mockUsersResponse = {
  data: [
    {
      id: 1,
      email: "alice@test.com",
      username: "alice",
      name: "Alice Admin",
      avatar_url: null,
      is_active: true,
      is_system_admin: true,
      is_email_verified: true,
      last_login_at: "2024-06-15T10:00:00Z",
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-06-15T10:00:00Z",
    },
    {
      id: 2,
      email: "bob@test.com",
      username: "bob",
      name: null,
      avatar_url: "https://example.com/bob.png",
      is_active: false,
      is_system_admin: false,
      is_email_verified: false,
      last_login_at: null,
      created_at: "2024-02-01T00:00:00Z",
      updated_at: "2024-02-01T00:00:00Z",
    },
  ],
  total: 2,
  page: 1,
  page_size: 20,
  total_pages: 1,
};

describe("UsersPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListUsers.mockResolvedValue(mockUsersResponse);
    mockDisableUser.mockResolvedValue({ id: 1, is_active: false });
    mockEnableUser.mockResolvedValue({ id: 2, is_active: true });
    mockGrantAdmin.mockResolvedValue({ id: 2, is_system_admin: true });
    mockRevokeAdmin.mockResolvedValue({ id: 1, is_system_admin: false });
  });

  it("should render search input", async () => {
    render(<UsersPage />);
    expect(
      screen.getByPlaceholderText("Search users...")
    ).toBeInTheDocument();
  });

  it("should display user list after loading", async () => {
    render(<UsersPage />);
    await screen.findByText("Alice Admin");
    expect(screen.getByText("Alice Admin")).toBeInTheDocument();
    expect(screen.getByText("alice@test.com")).toBeInTheDocument();
  });

  it("should display user initial for users without avatar", async () => {
    render(<UsersPage />);
    await screen.findByText("Alice Admin");
    // Alice has no avatar, should show "A"
    expect(screen.getByText("A")).toBeInTheDocument();
  });

  it("should display avatar image when available", async () => {
    render(<UsersPage />);
    await screen.findByText("Alice Admin");
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("src", "https://example.com/bob.png");
  });

  it("should show username when name is null", async () => {
    render(<UsersPage />);
    await screen.findByText("bob");
    expect(screen.getByText("bob")).toBeInTheDocument();
  });

  it("should show Admin badge for admin users", async () => {
    render(<UsersPage />);
    await screen.findByText("Admin");
    expect(screen.getByText("Admin")).toBeInTheDocument();
  });

  it("should show Disabled badge for inactive users", async () => {
    render(<UsersPage />);
    await screen.findByText("Disabled");
    expect(screen.getByText("Disabled")).toBeInTheDocument();
  });

  it("should show Unverified badge for unverified users", async () => {
    render(<UsersPage />);
    await screen.findByText("Unverified");
    expect(screen.getByText("Unverified")).toBeInTheDocument();
  });

  it("should show total user count", async () => {
    render(<UsersPage />);
    await screen.findByText("Users (2)");
    expect(screen.getByText("Users (2)")).toBeInTheDocument();
  });

  it("should show empty state when no users found", async () => {
    mockListUsers.mockResolvedValue({
      data: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    });
    render(<UsersPage />);
    await screen.findByText("No users found");
    expect(screen.getByText("No users found")).toBeInTheDocument();
  });

  it("should show loading skeleton initially", () => {
    mockListUsers.mockReturnValue(new Promise(() => {}));
    render(<UsersPage />);
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("should call listUsers with search param when searching", async () => {
    render(<UsersPage />);
    await screen.findByText("Alice Admin");

    const searchInput = screen.getByPlaceholderText("Search users...");
    fireEvent.change(searchInput, { target: { value: "alice" } });

    await waitFor(() => {
      expect(mockListUsers).toHaveBeenCalledWith(
        expect.objectContaining({ search: "alice", page: 1 })
      );
    });
  });

  it("should disable user and show success toast", async () => {
    render(<UsersPage />);
    await screen.findByText("Alice Admin");

    // Alice is active, so she should have a "Disable user" button
    const disableBtn = screen.getByTitle("Disable user");
    fireEvent.click(disableBtn);

    await waitFor(() => {
      expect(mockDisableUser).toHaveBeenCalledWith(1);
      expect(mockToastSuccess).toHaveBeenCalledWith(
        "User disabled successfully"
      );
    });
  });

  it("should enable user and show success toast", async () => {
    render(<UsersPage />);
    await screen.findByText("Alice Admin");

    // Bob is inactive, so he should have an "Enable user" button
    const enableBtn = screen.getByTitle("Enable user");
    fireEvent.click(enableBtn);

    await waitFor(() => {
      expect(mockEnableUser).toHaveBeenCalledWith(2);
      expect(mockToastSuccess).toHaveBeenCalledWith(
        "User enabled successfully"
      );
    });
  });

  it("should grant admin and show success toast", async () => {
    render(<UsersPage />);
    await screen.findByText("Alice Admin");

    // Bob is not admin, so he should have a "Grant admin" button
    const grantBtn = screen.getByTitle("Grant admin");
    fireEvent.click(grantBtn);

    await waitFor(() => {
      expect(mockGrantAdmin).toHaveBeenCalledWith(2);
      expect(mockToastSuccess).toHaveBeenCalledWith(
        "Admin privileges granted"
      );
    });
  });

  it("should revoke admin and show success toast", async () => {
    render(<UsersPage />);
    await screen.findByText("Alice Admin");

    // Alice is admin, so she should have a "Revoke admin" button
    const revokeBtn = screen.getByTitle("Revoke admin");
    fireEvent.click(revokeBtn);

    await waitFor(() => {
      expect(mockRevokeAdmin).toHaveBeenCalledWith(1);
      expect(mockToastSuccess).toHaveBeenCalledWith(
        "Admin privileges revoked"
      );
    });
  });

  it("should show error toast when action fails", async () => {
    mockDisableUser.mockRejectedValue({ error: "Permission denied" });
    render(<UsersPage />);
    await screen.findByText("Alice Admin");

    fireEvent.click(screen.getByTitle("Disable user"));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith("Permission denied");
    });
  });

  it("should show generic error when error has no message", async () => {
    mockDisableUser.mockRejectedValue({});
    render(<UsersPage />);
    await screen.findByText("Alice Admin");

    fireEvent.click(screen.getByTitle("Disable user"));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith("Failed to disable user");
    });
  });
});
