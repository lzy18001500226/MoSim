import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";

// Mock getDashboardStats
const mockGetDashboardStats = vi.fn();
vi.mock("@/lib/api/admin", () => ({
  getDashboardStats: () => mockGetDashboardStats(),
}));

import DashboardPage from "../page";

const mockStats = {
  total_users: 1200,
  active_users: 950,
  total_organizations: 85,
  total_runners: 42,
  online_runners: 38,
  total_pods: 250,
  active_pods: 120,
  total_subscriptions: 60,
  active_subscriptions: 45,
  new_users_today: 8,
  new_users_this_week: 35,
  new_users_this_month: 150,
};

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetDashboardStats.mockResolvedValue(mockStats);
  });

  it("should show loading skeleton initially", () => {
    // Never resolve the promise
    mockGetDashboardStats.mockReturnValue(new Promise(() => {}));
    render(<DashboardPage />);
    // Loading skeletons use animate-pulse class
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("should display stats after loading", async () => {
    render(<DashboardPage />);
    // Wait for stats to appear
    await screen.findByText("1,200");
    expect(screen.getByText("1,200")).toBeInTheDocument(); // total_users
    expect(screen.getByText("85")).toBeInTheDocument(); // total_organizations
    expect(screen.getByText("42")).toBeInTheDocument(); // total_runners
    expect(screen.getByText("120")).toBeInTheDocument(); // active_pods
  });

  it("should display stat card titles", async () => {
    render(<DashboardPage />);
    await screen.findByText("Total Users");
    expect(screen.getByText("Total Users")).toBeInTheDocument();
    expect(screen.getByText("Organizations")).toBeInTheDocument();
    expect(screen.getByText("Runners")).toBeInTheDocument();
    expect(screen.getByText("Active Pods")).toBeInTheDocument();
  });

  it("should display sub-values", async () => {
    render(<DashboardPage />);
    await screen.findByText("950 active");
    expect(screen.getByText("950 active")).toBeInTheDocument();
    expect(screen.getByText("38 online")).toBeInTheDocument();
    expect(screen.getByText("250 total")).toBeInTheDocument();
  });

  it("should display new users breakdown", async () => {
    render(<DashboardPage />);
    await screen.findByText("New Users");
    expect(screen.getByText("8")).toBeInTheDocument(); // today
    expect(screen.getByText("35")).toBeInTheDocument(); // this week
  });

  it("should display subscriptions section", async () => {
    render(<DashboardPage />);
    await screen.findByText("Subscriptions");
    expect(screen.getByText("45")).toBeInTheDocument(); // active
    expect(screen.getByText("60")).toBeInTheDocument(); // total
  });

  it("should display system health section", async () => {
    render(<DashboardPage />);
    await screen.findByText("System Health");
    expect(screen.getByText("All systems operational")).toBeInTheDocument();
    expect(
      screen.getByText("38 of 42 runners online")
    ).toBeInTheDocument();
  });

  it("should show error state when API fails", async () => {
    mockGetDashboardStats.mockRejectedValue(new Error("Network error"));
    render(<DashboardPage />);
    await screen.findByText("Failed to load dashboard stats");
    expect(
      screen.getByText("Failed to load dashboard stats")
    ).toBeInTheDocument();
  });
});
