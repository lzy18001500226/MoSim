import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

// Mock usePathname
const mockPathname = vi.fn(() => "/");
vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname(),
}));

import { Header } from "../header";

describe("Header", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPathname.mockReturnValue("/");
  });

  describe("page titles", () => {
    it("should show 'Dashboard' for '/'", () => {
      mockPathname.mockReturnValue("/");
      render(<Header />);
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });

    it("should show 'Users' for '/users'", () => {
      mockPathname.mockReturnValue("/users");
      render(<Header />);
      expect(screen.getByText("Users")).toBeInTheDocument();
    });

    it("should show 'Organizations' for '/organizations'", () => {
      mockPathname.mockReturnValue("/organizations");
      render(<Header />);
      expect(screen.getByText("Organizations")).toBeInTheDocument();
    });

    it("should show 'Runners' for '/runners'", () => {
      mockPathname.mockReturnValue("/runners");
      render(<Header />);
      expect(screen.getByText("Runners")).toBeInTheDocument();
    });

    it("should show 'Relays' for '/relays'", () => {
      mockPathname.mockReturnValue("/relays");
      render(<Header />);
      expect(screen.getByText("Relays")).toBeInTheDocument();
    });

    it("should show 'Skill Registries' for '/skill-registries'", () => {
      mockPathname.mockReturnValue("/skill-registries");
      render(<Header />);
      expect(screen.getByText("Skill Registries")).toBeInTheDocument();
    });

    it("should show 'Promo Codes' for '/promo-codes'", () => {
      mockPathname.mockReturnValue("/promo-codes");
      render(<Header />);
      expect(screen.getByText("Promo Codes")).toBeInTheDocument();
    });

    it("should show 'Support Tickets' for '/support-tickets'", () => {
      mockPathname.mockReturnValue("/support-tickets");
      render(<Header />);
      expect(screen.getByText("Support Tickets")).toBeInTheDocument();
    });

    it("should show 'Audit Logs' for '/audit-logs'", () => {
      mockPathname.mockReturnValue("/audit-logs");
      render(<Header />);
      expect(screen.getByText("Audit Logs")).toBeInTheDocument();
    });
  });

  describe("dynamic route titles", () => {
    it("should show 'User Details' for '/users/123'", () => {
      mockPathname.mockReturnValue("/users/123");
      render(<Header />);
      expect(screen.getByText("User Details")).toBeInTheDocument();
    });

    it("should show 'Organization Details' for '/organizations/5'", () => {
      mockPathname.mockReturnValue("/organizations/5");
      render(<Header />);
      expect(screen.getByText("Organization Details")).toBeInTheDocument();
    });

    it("should show 'Runner Details' for '/runners/10'", () => {
      mockPathname.mockReturnValue("/runners/10");
      render(<Header />);
      expect(screen.getByText("Runner Details")).toBeInTheDocument();
    });

    it("should show 'Relay Details' for '/relays/abc'", () => {
      mockPathname.mockReturnValue("/relays/abc");
      render(<Header />);
      expect(screen.getByText("Relay Details")).toBeInTheDocument();
    });

    it("should show 'Create Promo Code' for '/promo-codes/new'", () => {
      mockPathname.mockReturnValue("/promo-codes/new");
      render(<Header />);
      expect(screen.getByText("Create Promo Code")).toBeInTheDocument();
    });

    it("should show 'Promo Code Details' for '/promo-codes/5'", () => {
      mockPathname.mockReturnValue("/promo-codes/5");
      render(<Header />);
      expect(screen.getByText("Promo Code Details")).toBeInTheDocument();
    });

    it("should show 'Ticket Details' for '/support-tickets/7'", () => {
      mockPathname.mockReturnValue("/support-tickets/7");
      render(<Header />);
      expect(screen.getByText("Ticket Details")).toBeInTheDocument();
    });

    it("should show 'Skill Registry Details' for '/skill-registries/3'", () => {
      mockPathname.mockReturnValue("/skill-registries/3");
      render(<Header />);
      expect(screen.getByText("Skill Registry Details")).toBeInTheDocument();
    });

    it("should fall back to 'Admin Console' for unknown paths", () => {
      mockPathname.mockReturnValue("/unknown/deep/path");
      render(<Header />);
      expect(screen.getByText("Admin Console")).toBeInTheDocument();
    });
  });

  describe("hamburger menu", () => {
    it("should not render menu button when onMenuClick is not provided", () => {
      render(<Header />);
      expect(screen.queryByText("Open menu")).not.toBeInTheDocument();
    });

    it("should render menu button when onMenuClick is provided", () => {
      render(<Header onMenuClick={() => {}} />);
      expect(screen.getByText("Open menu")).toBeInTheDocument();
    });

    it("should call onMenuClick when menu button is clicked", () => {
      const handleMenuClick = vi.fn();
      render(<Header onMenuClick={handleMenuClick} />);
      fireEvent.click(screen.getByText("Open menu").closest("button")!);
      expect(handleMenuClick).toHaveBeenCalledTimes(1);
    });
  });

  describe("notification bell", () => {
    it("should always render notification button", () => {
      render(<Header />);
      const buttons = screen.getAllByRole("button");
      expect(buttons.length).toBeGreaterThanOrEqual(1);
    });
  });
});
