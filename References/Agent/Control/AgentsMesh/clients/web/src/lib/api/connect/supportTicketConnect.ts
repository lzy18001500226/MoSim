// Connect-RPC adapter for proto.support_ticket.v1.SupportTicketService.
//
// Wire layer is proto-SSOT: returns and consumes `@proto/support_ticket/v1`
// types directly. No adapter DTO layer.
//
// REST shape translation:
// - Proto list envelope is {items, total, limit, offset} (conventions §8);
//   the renderer reads {items, total, page, page_size, total_pages} for
//   pagination UI. This adapter remaps so existing code keeps working.
// - Page/page_size translate to offset/limit: offset = (page-1) * page_size.

import {
  AddSupportTicketMessageRequestSchema,
  AssociateAttachmentsRequestSchema,
  AssociateAttachmentsResponseSchema,
  CreateSupportTicketRequestSchema,
  GetAttachmentUrlRequestSchema,
  GetAttachmentUrlResponseSchema,
  GetSupportTicketRequestSchema,
  ListSupportTicketsRequestSchema,
  ListSupportTicketsResponseSchema,
  PresignAttachmentUploadRequestSchema,
  PresignAttachmentUploadResponseSchema,
  SupportTicketDetailSchema,
  SupportTicketMessageSchema,
  SupportTicketSchema,
  type SupportTicket,
  type SupportTicketAttachment,
  type SupportTicketDetail,
  type SupportTicketMessage,
} from "@proto/support_ticket/v1/support_ticket_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getSupportTicketService } from "@/lib/wasm-core";

export type {
  SupportTicket,
  SupportTicketAttachment,
  SupportTicketMessage,
  SupportTicketDetail,
} from "@proto/support_ticket/v1/support_ticket_pb";

export interface SupportTicketListResponse {
  items: SupportTicket[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface SupportTicketListParams {
  status?: string;
  page?: number;
  pageSize?: number;
}

export async function listSupportTickets(
  params?: SupportTicketListParams,
): Promise<SupportTicketListResponse> {
  const page = params?.page ?? 1;
  const pageSize = params?.pageSize ?? 20;
  const offset = (page - 1) * pageSize;
  const req = create(ListSupportTicketsRequestSchema, {
    status: params?.status ?? "",
    offset,
    limit: pageSize,
  });
  const bytes = toBinary(ListSupportTicketsRequestSchema, req);
  const respBytes = await getSupportTicketService().listSupportTicketsConnect(bytes);
  const resp = fromBinary(ListSupportTicketsResponseSchema, new Uint8Array(respBytes));

  const total = Number(resp.total);
  const totalPages = pageSize > 0 ? Math.ceil(total / pageSize) : 1;
  return {
    items: resp.items,
    total,
    page,
    pageSize,
    totalPages,
  };
}

export async function getSupportTicketDetail(id: number): Promise<SupportTicketDetail> {
  const req = create(GetSupportTicketRequestSchema, { id: BigInt(id) });
  const bytes = toBinary(GetSupportTicketRequestSchema, req);
  const respBytes = await getSupportTicketService().getSupportTicketConnect(bytes);
  const resp = fromBinary(SupportTicketDetailSchema, new Uint8Array(respBytes));
  if (!resp.ticket) {
    throw new Error("support ticket detail response missing ticket");
  }
  return resp;
}

export async function getSupportTicketAttachmentUrl(
  attachmentId: number,
): Promise<{ url: string }> {
  const req = create(GetAttachmentUrlRequestSchema, { attachmentId: BigInt(attachmentId) });
  const bytes = toBinary(GetAttachmentUrlRequestSchema, req);
  const respBytes = await getSupportTicketService().getAttachmentUrlConnect(bytes);
  const resp = fromBinary(GetAttachmentUrlResponseSchema, new Uint8Array(respBytes));
  return { url: resp.url };
}

export async function createSupportTicketConnect(input: {
  title: string;
  category: string;
  content: string;
  priority?: string;
}): Promise<SupportTicket> {
  const req = create(CreateSupportTicketRequestSchema, {
    title: input.title,
    category: input.category,
    content: input.content,
    priority: input.priority,
  });
  const bytes = toBinary(CreateSupportTicketRequestSchema, req);
  const respBytes = await getSupportTicketService().createSupportTicketConnect(bytes);
  return fromBinary(SupportTicketSchema, new Uint8Array(respBytes));
}

export async function addSupportTicketMessageConnect(
  ticketId: number,
  content: string,
): Promise<SupportTicketMessage> {
  const req = create(AddSupportTicketMessageRequestSchema, {
    ticketId: BigInt(ticketId),
    content,
  });
  const bytes = toBinary(AddSupportTicketMessageRequestSchema, req);
  const respBytes = await getSupportTicketService().addSupportTicketMessageConnect(bytes);
  return fromBinary(SupportTicketMessageSchema, new Uint8Array(respBytes));
}

export async function presignAttachmentUploadConnect(input: {
  ticketId: number;
  messageId?: number;
  filename: string;
  contentType: string;
  size: number;
}): Promise<{ putUrl: string; storageKey: string }> {
  const req = create(PresignAttachmentUploadRequestSchema, {
    ticketId: BigInt(input.ticketId),
    messageId: input.messageId !== undefined ? BigInt(input.messageId) : undefined,
    filename: input.filename,
    contentType: input.contentType,
    size: BigInt(input.size),
  });
  const bytes = toBinary(PresignAttachmentUploadRequestSchema, req);
  const respBytes = await getSupportTicketService().presignAttachmentUploadConnect(bytes);
  const resp = fromBinary(PresignAttachmentUploadResponseSchema, new Uint8Array(respBytes));
  return { putUrl: resp.putUrl, storageKey: resp.storageKey };
}

export async function associateAttachmentsConnect(
  ticketId: number,
  refs: Array<{
    storageKey: string;
    filename: string;
    contentType: string;
    size: number;
    messageId?: number;
  }>,
): Promise<SupportTicketAttachment[]> {
  const req = create(AssociateAttachmentsRequestSchema, {
    ticketId: BigInt(ticketId),
    attachments: refs.map((r) => ({
      storageKey: r.storageKey,
      filename: r.filename,
      contentType: r.contentType,
      size: BigInt(r.size),
      messageId: r.messageId !== undefined ? BigInt(r.messageId) : undefined,
    })),
  });
  const bytes = toBinary(AssociateAttachmentsRequestSchema, req);
  const respBytes = await getSupportTicketService().associateAttachmentsConnect(bytes);
  const resp = fromBinary(AssociateAttachmentsResponseSchema, new Uint8Array(respBytes));
  return resp.items;
}
