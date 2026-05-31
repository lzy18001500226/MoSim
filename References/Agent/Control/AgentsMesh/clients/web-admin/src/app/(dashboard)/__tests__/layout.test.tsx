import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";

// Mock next/navigation
const mockReplace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: mockReplace }),
  usePathname: () => "/",
}));

// Mock layout dependencies - simplified stubs
vi.mock("@/components/layout/sidebar", () => ({
  Sidebar: () => <aside data-testid="sidebar">Sidebar</aside>,
  MobileSidebar: ({ open }: { open: boolean }) =>
    open ? <div data-testid="mobile-sidebar">MobileSidebar</div> : null,
}));

vi.mock("@/components/layout/header", () => ({
  Header: ({ onMenuClick }: { onMenuClick?: () => void }) => (
    <header data-testid="header">
      {onMenuClick && (
        <button data-testid="menu-btn" onClick={onMenuClick}>
          Menu
        </button>
      )}
      Header
    </header>
  ),
}));

// Mock auth store — use a mutable ref so tests can adjust
const mockAuthState = { token: "test-token" as string | null, isLoading: false };
vi.mock("@/stores/auth", () => ({
  useAuthStore: () => mockAuthState,
}));

import DashboardLayout from "../layout";

describe("DashboardLayout", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthState.token = "test-token";
    mockAuthState.isLoading = false;
  });

  it("should render sidebar, header and children when authenticated", () => {
    render(
      <DashboardLayout>
        <div data-testid="content">Page Content</div>
      </DashboardLayout>
    );
    expect(screen.getByTestId("sidebar")).toBeInTheDocument();
    expect(screen.getByTestId("header")).toBeInTheDocument();
    expect(screen.getByTestId("content")).toBeInTheDocument();
  });

  it("should render nothing when not authenticated", () => {
    mockAuthState.token = null;
    const { container } = render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );
    expect(container.innerHTML).toBe("");
  });

  it("should redirect to /login when no token and not loading", async () => {
    mockAuthState.token = null;
    mockAuthState.isLoading = false;
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );
    // useEffect runs asynchronously
    await vi.waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith("/login");
    });
  });

  it("should not redirect while loading", () => {
    mockAuthState.token = null;
    mockAuthState.isLoading = true;
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );
    expect(mockReplace).not.toHaveBeenCalled();
  });

  it("should open mobile sidebar when header menu button is clicked", async () => {
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );
    // Initially mobile sidebar is closed
    expect(screen.queryByTestId("mobile-sidebar")).not.toBeInTheDocument();

    // Click menu button
    const menuBtn = screen.getByTestId("menu-btn");
    menuBtn.click();

    await vi.waitFor(() => {
      expect(screen.getByTestId("mobile-sidebar")).toBeInTheDocument();
    });
  });
});
