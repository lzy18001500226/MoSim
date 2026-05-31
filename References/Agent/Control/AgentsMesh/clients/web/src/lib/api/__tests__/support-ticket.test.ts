import { describe, it, expect, vi, beforeEach } from "vitest";

if (!File.prototype.arrayBuffer) {
  File.prototype.arrayBuffer = function () {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as ArrayBuffer);
      reader.readAsArrayBuffer(this);
    });
  };
}

const {
  listMock, getDetailMock, getAttUrlMock,
  createMock, addMsgMock, presignMock, associateMock,
} = vi.hoisted(() => ({
  listMock: vi.fn(),
  getDetailMock: vi.fn(),
  getAttUrlMock: vi.fn(),
  createMock: vi.fn(),
  addMsgMock: vi.fn(),
  presignMock: vi.fn(),
  associateMock: vi.fn(),
}));

vi.mock("../connect/supportTicketConnect", () => ({
  listSupportTickets: listMock,
  getSupportTicketDetail: getDetailMock,
  getSupportTicketAttachmentUrl: getAttUrlMock,
  createSupportTicketConnect: createMock,
  addSupportTicketMessageConnect: addMsgMock,
  presignAttachmentUploadConnect: presignMock,
  associateAttachmentsConnect: associateMock,
}));

import {
  listSupportTickets, getSupportTicketDetail, addSupportTicketMessage,
  createSupportTicket, getSupportTicketAttachmentUrl,
} from "../facade/support-ticket";

describe("support-ticket API (Connect-only)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({
      data: [], total: 0, page: 1, page_size: 20, total_pages: 0,
    });
    getDetailMock.mockResolvedValue({
      ticket: {
        id: 42, user_id: 7, title: "x", category: "bug",
        status: "open", priority: "medium",
        created_at: "", updated_at: "",
      },
      messages: [],
    });
    getAttUrlMock.mockResolvedValue({ url: "https://example.com/f.png" });
    createMock.mockResolvedValue({
      id: 10, user_id: 1, title: "Bug", category: "bug",
      status: "open", priority: "high", created_at: "", updated_at: "",
    });
    addMsgMock.mockResolvedValue({
      id: 100, ticket_id: 5, user_id: 1, content: "hello",
      is_admin_reply: false, created_at: "", attachments: [],
    });
    presignMock.mockResolvedValue({
      putUrl: "https://example.com/put",
      storageKey: "support-tickets/1/2026/05/abc.png",
    });
    associateMock.mockResolvedValue([]);
    global.fetch = vi.fn().mockResolvedValue({ ok: true, status: 200 } as Response);
  });

  it("listSupportTickets delegates to Connect adapter", async () => {
    await listSupportTickets({ status: "open", page: 2, pageSize: 10 });
    expect(listMock).toHaveBeenCalledWith({ status: "open", page: 2, pageSize: 10 });
  });

  it("getSupportTicketDetail delegates to Connect adapter", async () => {
    await getSupportTicketDetail(42);
    expect(getDetailMock).toHaveBeenCalledWith(42);
  });

  it("getSupportTicketAttachmentUrl delegates to Connect adapter", async () => {
    const result = await getSupportTicketAttachmentUrl(99);
    expect(getAttUrlMock).toHaveBeenCalledWith(99);
    expect(result).toEqual({ url: "https://example.com/f.png" });
  });

  it("createSupportTicket without files calls only createSupportTicketConnect", async () => {
    await createSupportTicket({ title: "Q", category: "q", content: "How?" });
    expect(createMock).toHaveBeenCalledWith({
      title: "Q", category: "q", content: "How?", priority: undefined,
    });
    expect(presignMock).not.toHaveBeenCalled();
    expect(associateMock).not.toHaveBeenCalled();
  });

  it("createSupportTicket with files runs presign + PUT + associate per file", async () => {
    const file = new File(["screenshot"], "shot.png", { type: "image/png" });
    await createSupportTicket({
      title: "Bug", category: "bug", content: "Broke", priority: "high", files: [file],
    });
    expect(createMock).toHaveBeenCalledWith({
      title: "Bug", category: "bug", content: "Broke", priority: "high",
    });
    expect(presignMock).toHaveBeenCalledWith({
      ticketId: 10, messageId: undefined,
      filename: "shot.png", contentType: "image/png", size: file.size,
    });
    expect(global.fetch).toHaveBeenCalledWith(
      "https://example.com/put",
      expect.objectContaining({ method: "PUT" }),
    );
    expect(associateMock).toHaveBeenCalledWith(10, [{
      storageKey: "support-tickets/1/2026/05/abc.png",
      filename: "shot.png", contentType: "image/png", size: file.size,
      messageId: undefined,
    }]);
  });

  it("addSupportTicketMessage without files calls only addSupportTicketMessageConnect", async () => {
    await addSupportTicketMessage(5, "hello");
    expect(addMsgMock).toHaveBeenCalledWith(5, "hello");
    expect(presignMock).not.toHaveBeenCalled();
  });

  it("addSupportTicketMessage with files runs presign + PUT + associate per file", async () => {
    const file = new File(["data"], "f.txt", { type: "text/plain" });
    await addSupportTicketMessage(5, "hello", [file]);
    expect(addMsgMock).toHaveBeenCalledWith(5, "hello");
    expect(presignMock).toHaveBeenCalledWith({
      ticketId: 5, messageId: 100,
      filename: "f.txt", contentType: "text/plain", size: file.size,
    });
    expect(associateMock).toHaveBeenCalledWith(5, [{
      storageKey: "support-tickets/1/2026/05/abc.png",
      filename: "f.txt", contentType: "text/plain", size: file.size,
      messageId: 100,
    }]);
  });
});
