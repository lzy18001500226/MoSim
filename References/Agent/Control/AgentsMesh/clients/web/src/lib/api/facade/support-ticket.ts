// support-ticket facade — all RPCs go through supportTicketConnect (binary
// Connect wire). Attachment uploads use the 3-step presigned-URL flow:
//   1. createSupportTicket / addSupportTicketMessage (Connect) — content only
//   2. for each file: presignAttachmentUploadConnect (Connect) → put_url +
//      opaque storage_key → browser PUTs bytes to put_url
//   3. associateAttachmentsConnect (Connect) — materializes DB rows
// Multipart REST is gone; all wire is binary protobuf per conventions §2.5.

import {
  addSupportTicketMessageConnect,
  associateAttachmentsConnect,
  createSupportTicketConnect,
  getSupportTicketAttachmentUrl as getAttachmentUrlConnect,
  getSupportTicketDetail as getDetailConnect,
  listSupportTickets as listConnect,
  presignAttachmentUploadConnect,
} from "../connect/supportTicketConnect";

export type {
  SupportTicket, SupportTicketMessage, SupportTicketAttachment,
  SupportTicketDetail,
} from "../connect/supportTicketConnect";
export type {
  SupportTicketListResponse, SupportTicketListParams,
} from "../connect/supportTicketConnect";

import type {
  SupportTicket, SupportTicketMessage, SupportTicketDetail,
} from "../connect/supportTicketConnect";
import type {
  SupportTicketListResponse, SupportTicketListParams,
} from "../connect/supportTicketConnect";

interface AttachmentTarget {
  ticketId: number;
  messageId?: number;
}

async function uploadAttachments(target: AttachmentTarget, files: File[]): Promise<void> {
  if (!files.length) return;
  const refs: Array<{
    storageKey: string;
    filename: string;
    contentType: string;
    size: number;
    messageId?: number;
  }> = [];
  for (const file of files) {
    const contentType = file.type || "application/octet-stream";
    const presign = await presignAttachmentUploadConnect({
      ticketId: target.ticketId,
      messageId: target.messageId,
      filename: file.name,
      contentType,
      size: file.size,
    });
    const putRes = await fetch(presign.putUrl, {
      method: "PUT",
      headers: { "Content-Type": contentType },
      body: file,
    });
    if (!putRes.ok) {
      throw new Error(`attachment upload failed for ${file.name}: ${putRes.status}`);
    }
    refs.push({
      storageKey: presign.storageKey,
      filename: file.name,
      contentType,
      size: file.size,
      messageId: target.messageId,
    });
  }
  if (refs.length) {
    await associateAttachmentsConnect(target.ticketId, refs);
  }
}

export async function createSupportTicket(data: {
  title: string; category: string; content: string; priority?: string; files?: File[];
}): Promise<SupportTicket> {
  const ticket = await createSupportTicketConnect({
    title: data.title,
    category: data.category,
    content: data.content,
    priority: data.priority,
  });
  if (data.files?.length) {
    await uploadAttachments({ ticketId: Number(ticket.id) }, data.files);
  }
  return ticket;
}

export async function listSupportTickets(
  params?: SupportTicketListParams,
): Promise<SupportTicketListResponse> {
  return listConnect(params);
}

export async function getSupportTicketDetail(id: number): Promise<SupportTicketDetail> {
  return getDetailConnect(id);
}

export async function addSupportTicketMessage(
  ticketId: number, content: string, files?: File[],
): Promise<SupportTicketMessage> {
  const msg = await addSupportTicketMessageConnect(ticketId, content);
  if (files?.length) {
    await uploadAttachments({ ticketId, messageId: Number(msg.id) }, files);
  }
  return msg;
}

export async function getSupportTicketAttachmentUrl(
  attachmentId: number,
): Promise<{ url: string }> {
  return getAttachmentUrlConnect(attachmentId);
}
