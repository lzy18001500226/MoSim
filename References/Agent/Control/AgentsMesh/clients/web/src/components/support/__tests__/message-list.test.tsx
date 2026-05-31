import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@/test/test-utils";
import { MessageList } from "../message-list";
import type { SupportTicketMessage } from "@/lib/api/facade/supportTicketConnect";
import { getSupportTicketAttachmentUrl } from "@/lib/api/facade/supportTicketConnect";

vi.mock("@/lib/api/facade/supportTicketConnect", () => ({
  getSupportTicketAttachmentUrl: vi.fn(),
}));

// Mock window.open
const mockWindowOpen = vi.fn();
Object.defineProperty(window, "open", {
  writable: true,
  value: mockWindowOpen,
});

const baseMessage: SupportTicketMessage = {
  $typeName: "proto.support_ticket.v1.SupportTicketMessage",
  id: BigInt(1),
  ticketId: BigInt(10),
  userId: BigInt(100),
  content: "Hello, I need help with my account.",
  isAdminReply: false,
  createdAt: new Date().toISOString(),
  user: {
    $typeName: "proto.support_ticket.v1.SupportTicketUser",
    id: BigInt(100), name: "John Doe", email: "john@example.com", avatarUrl: "",
  },
  attachments: [],
};

const adminMessage: SupportTicketMessage = {
  $typeName: "proto.support_ticket.v1.SupportTicketMessage",
  id: BigInt(2),
  ticketId: BigInt(10),
  userId: BigInt(200),
  content: "Sure, let me look into that.",
  isAdminReply: true,
  createdAt: new Date().toISOString(),
  user: {
    $typeName: "proto.support_ticket.v1.SupportTicketUser",
    id: BigInt(200), name: "Admin User", email: "admin@example.com", avatarUrl: "",
  },
  attachments: [],
};

const messageWithAttachments: SupportTicketMessage = {
  $typeName: "proto.support_ticket.v1.SupportTicketMessage",
  id: BigInt(3),
  ticketId: BigInt(10),
  userId: BigInt(100),
  content: "Here are the screenshots",
  isAdminReply: false,
  createdAt: new Date().toISOString(),
  user: {
    $typeName: "proto.support_ticket.v1.SupportTicketUser",
    id: BigInt(100), name: "John Doe", email: "john@example.com", avatarUrl: "",
  },
  attachments: [
    {
      $typeName: "proto.support_ticket.v1.SupportTicketAttachment",
      id: BigInt(101),
      ticketId: BigInt(10),
      messageId: BigInt(3),
      uploaderId: BigInt(100),
      originalName: "screenshot.png",
      mimeType: "image/png",
      size: BigInt(204800),
      createdAt: new Date().toISOString(),
    },
    {
      $typeName: "proto.support_ticket.v1.SupportTicketAttachment",
      id: BigInt(102),
      ticketId: BigInt(10),
      messageId: BigInt(3),
      uploaderId: BigInt(100),
      originalName: "log.txt",
      mimeType: "text/plain",
      size: BigInt(512),
      createdAt: new Date().toISOString(),
    },
  ],
};

describe("MessageList", () => {
  it("renders empty state when no messages", () => {
    render(<MessageList messages={[]} />);
    const emptyDiv = document.querySelector(".py-12.text-center");
    expect(emptyDiv).toBeInTheDocument();
    expect(emptyDiv?.textContent).toBeTruthy();
  });

  it("renders messages", () => {
    render(<MessageList messages={[baseMessage, adminMessage]} />);
    expect(
      screen.getByText("Hello, I need help with my account.")
    ).toBeInTheDocument();
    expect(
      screen.getByText("Sure, let me look into that.")
    ).toBeInTheDocument();
  });
});

describe("MessageBubble (via MessageList)", () => {
  beforeEach(() => {
    vi.mocked(getSupportTicketAttachmentUrl).mockResolvedValue({
      url: "https://example.com/download/file.png",
    });
  });
  it("renders user message correctly", () => {
    render(<MessageList messages={[baseMessage]} />);
    expect(
      screen.getByText("Hello, I need help with my account.")
    ).toBeInTheDocument();
    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });

  it("renders admin message with Admin badge", () => {
    render(<MessageList messages={[adminMessage]} />);
    expect(
      screen.getByText("Sure, let me look into that.")
    ).toBeInTheDocument();
    expect(screen.getByText("Admin")).toBeInTheDocument();
  });

  it("shows attachments with download buttons", () => {
    render(<MessageList messages={[messageWithAttachments]} />);
    expect(screen.getByText("screenshot.png")).toBeInTheDocument();
    expect(screen.getByText("log.txt")).toBeInTheDocument();
    expect(screen.getByText("(200.0 KB)")).toBeInTheDocument();
    expect(screen.getByText("(512 B)")).toBeInTheDocument();
  });

  it("calls download handler when attachment button is clicked", async () => {
    render(<MessageList messages={[messageWithAttachments]} />);
    const downloadBtn = screen.getByText("screenshot.png").closest("button");
    expect(downloadBtn).toBeInTheDocument();
    fireEvent.click(downloadBtn!);

    expect(getSupportTicketAttachmentUrl).toHaveBeenCalledWith(101);
  });

  it("shows user name when available", () => {
    render(<MessageList messages={[baseMessage]} />);
    expect(screen.getByText("John Doe")).toBeInTheDocument();
  });

  it("shows user email when name is not available", () => {
    const msgWithEmailOnly: SupportTicketMessage = {
      ...baseMessage,
      user: {
        $typeName: "proto.support_ticket.v1.SupportTicketUser",
        id: BigInt(100), name: "", email: "john@example.com", avatarUrl: "",
      },
    };
    render(<MessageList messages={[msgWithEmailOnly]} />);
    expect(screen.getByText("john@example.com")).toBeInTheDocument();
  });
});
