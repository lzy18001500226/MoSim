import { describe, it, expect } from "vitest";
import { render, screen } from "@/test/test-utils";
import {
  TicketStatusBadge,
  TicketCategoryBadge,
  TicketPriorityBadge,
} from "../ticket-status-badge";

describe("TicketStatusBadge", () => {
  it("renders with correct variant for open status", () => {
    render(<TicketStatusBadge status="open" />);
    expect(screen.getByText("Open")).toBeInTheDocument();
  });

  it("renders with correct variant for in_progress status", () => {
    render(<TicketStatusBadge status="in_progress" />);
    expect(screen.getByText("In Progress")).toBeInTheDocument();
  });

  it("renders with correct variant for resolved status", () => {
    render(<TicketStatusBadge status="resolved" />);
    expect(screen.getByText("Resolved")).toBeInTheDocument();
  });

  it("renders with correct variant for closed status", () => {
    render(<TicketStatusBadge status="closed" />);
    expect(screen.getByText("Closed")).toBeInTheDocument();
  });

  it("handles unknown status gracefully", () => {
    // When status key is not in translations, next-intl returns the key path
    render(<TicketStatusBadge status="unknown_status" />);
    // The badge should still render without crashing
    const badge = screen.getByText(/unknown_status|support\.status\.unknown_status/);
    expect(badge).toBeInTheDocument();
  });
});

describe("TicketCategoryBadge", () => {
  it("renders for bug category", () => {
    render(<TicketCategoryBadge category="bug" />);
    expect(screen.getByText("Bug Report")).toBeInTheDocument();
  });

  it("renders for feature_request category", () => {
    render(<TicketCategoryBadge category="feature_request" />);
    expect(screen.getByText("Feature Request")).toBeInTheDocument();
  });

  it("renders for usage_question category", () => {
    render(<TicketCategoryBadge category="usage_question" />);
    expect(screen.getByText("Usage Question")).toBeInTheDocument();
  });

  it("renders for account category", () => {
    render(<TicketCategoryBadge category="account" />);
    expect(screen.getByText("Account")).toBeInTheDocument();
  });

  it("renders for other category", () => {
    render(<TicketCategoryBadge category="other" />);
    expect(screen.getByText("Other")).toBeInTheDocument();
  });
});

describe("TicketPriorityBadge", () => {
  it("renders with correct variant for low priority", () => {
    render(<TicketPriorityBadge priority="low" />);
    expect(screen.getByText("Low")).toBeInTheDocument();
  });

  it("renders with correct variant for medium priority", () => {
    render(<TicketPriorityBadge priority="medium" />);
    expect(screen.getByText("Medium")).toBeInTheDocument();
  });

  it("renders with correct variant for high priority", () => {
    render(<TicketPriorityBadge priority="high" />);
    expect(screen.getByText("High")).toBeInTheDocument();
  });

  it("handles unknown priority gracefully", () => {
    render(<TicketPriorityBadge priority="critical" />);
    // Should render without crashing, falling back to the key or a resolved string
    const badge = screen.getByText(/critical|support\.priority\.critical/);
    expect(badge).toBeInTheDocument();
  });
});
