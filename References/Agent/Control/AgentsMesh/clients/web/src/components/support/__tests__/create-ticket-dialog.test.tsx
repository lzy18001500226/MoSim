import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@/test/test-utils";
import { CreateTicketDialog } from "../create-ticket-dialog";

// Mock next/navigation
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

// Mock createSupportTicket
const mockCreateSupportTicket = vi.fn();
vi.mock("@/lib/api/facade/support-ticket", () => ({
  createSupportTicket: (...args: unknown[]) => mockCreateSupportTicket(...args),
}));

describe("CreateTicketDialog", () => {
  const defaultProps = {
    open: true,
    onOpenChange: vi.fn(),
    onCreated: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockCreateSupportTicket.mockReset();
  });

  it("renders dialog when open", () => {
    render(<CreateTicketDialog {...defaultProps} />);
    // Dialog title from i18n: "New Ticket"
    expect(screen.getByText("New Ticket")).toBeInTheDocument();
    // Dialog description from i18n: "Describe your issue and we'll get back to you"
    expect(
      screen.getByText("Describe your issue and we'll get back to you")
    ).toBeInTheDocument();
  });

  it("does not render dialog when closed", () => {
    render(<CreateTicketDialog {...defaultProps} open={false} />);
    expect(screen.queryByText("New Ticket")).not.toBeInTheDocument();
  });

  it("shows all form fields (title, category, priority, content, attachments)", () => {
    render(<CreateTicketDialog {...defaultProps} />);
    // Title field label
    expect(screen.getByText("Title")).toBeInTheDocument();
    // Category field label
    expect(screen.getByText("Category")).toBeInTheDocument();
    // Priority field label
    expect(screen.getByText("Priority")).toBeInTheDocument();
    // Content/Description field label
    expect(screen.getByText("Description")).toBeInTheDocument();
    // Attachments field label
    expect(screen.getByText("Attachments")).toBeInTheDocument();
    // Add files text
    expect(screen.getByText("Add files")).toBeInTheDocument();
  });

  it("validates required fields", async () => {
    render(<CreateTicketDialog {...defaultProps} />);

    // Click submit without filling in required fields
    const submitButton = screen.getByText("Submit");
    fireEvent.click(submitButton);

    // Should show validation error
    await waitFor(() => {
      expect(
        screen.getByText("Title and description are required")
      ).toBeInTheDocument();
    });

    // API should not have been called
    expect(mockCreateSupportTicket).not.toHaveBeenCalled();
  });

  it("submits form with correct data", async () => {
    mockCreateSupportTicket.mockResolvedValue({ id: 42, title: "Test bug" });

    render(<CreateTicketDialog {...defaultProps} />);

    // Fill in title
    const titleInput = screen.getByPlaceholderText(
      "Brief summary of your issue"
    );
    fireEvent.change(titleInput, { target: { value: "Test bug" } });

    // Fill in content
    const contentInput = screen.getByPlaceholderText(
      "Describe your issue in detail..."
    );
    fireEvent.change(contentInput, {
      target: { value: "Something is broken" },
    });

    // Submit
    const submitButton = screen.getByText("Submit");
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockCreateSupportTicket).toHaveBeenCalledWith({
        title: "Test bug",
        category: "other", // default
        content: "Something is broken",
        priority: "medium", // default
        files: undefined,
      });
    });

    // Should navigate to the new ticket
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/support/42");
    });

    // Should close dialog
    expect(defaultProps.onOpenChange).toHaveBeenCalledWith(false);
    expect(defaultProps.onCreated).toHaveBeenCalled();
  });

  it("shows error on submit failure", async () => {
    mockCreateSupportTicket.mockRejectedValue(new Error("Server error"));

    render(<CreateTicketDialog {...defaultProps} />);

    // Fill in required fields
    const titleInput = screen.getByPlaceholderText(
      "Brief summary of your issue"
    );
    fireEvent.change(titleInput, { target: { value: "Test" } });

    const contentInput = screen.getByPlaceholderText(
      "Describe your issue in detail..."
    );
    fireEvent.change(contentInput, { target: { value: "Details" } });

    // Submit
    const submitButton = screen.getByText("Submit");
    fireEvent.click(submitButton);

    // Should show error message
    await waitFor(() => {
      expect(
        screen.getByText("Failed to create ticket. Please try again.")
      ).toBeInTheDocument();
    });

    // Should not navigate
    expect(mockPush).not.toHaveBeenCalled();
  });

  it("closes dialog on cancel", () => {
    render(<CreateTicketDialog {...defaultProps} />);

    const cancelButton = screen.getByText("Cancel");
    fireEvent.click(cancelButton);

    expect(defaultProps.onOpenChange).toHaveBeenCalledWith(false);
  });

  it("renders category options correctly", () => {
    render(<CreateTicketDialog {...defaultProps} />);

    // Check that category select has the expected options
    expect(screen.getByText("Bug Report")).toBeInTheDocument();
    expect(screen.getByText("Feature Request")).toBeInTheDocument();
    expect(screen.getByText("Usage Question")).toBeInTheDocument();
    // "Account" appears as category option
    expect(screen.getAllByText("Account").length).toBeGreaterThanOrEqual(1);
    // "Other" is the default selected, check option exists
    expect(screen.getAllByText("Other").length).toBeGreaterThanOrEqual(1);
  });

  it("renders priority options correctly", () => {
    render(<CreateTicketDialog {...defaultProps} />);

    // Check priority select options
    expect(screen.getByText("Low")).toBeInTheDocument();
    // "Medium" is the default selected
    expect(screen.getAllByText("Medium").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("High")).toBeInTheDocument();
  });
});
