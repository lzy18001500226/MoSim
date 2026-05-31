// Facade re-export of the support-ticket Connect-RPC adapter. Business code
// imports from here (or from the `@/lib/api` barrel) so the wire-shape
// layer stays internal to the facade boundary. Tests mock this path.

export {
  listSupportTickets,
  getSupportTicketDetail,
  getSupportTicketAttachmentUrl,
  createSupportTicketConnect,
  addSupportTicketMessageConnect,
  presignAttachmentUploadConnect,
  associateAttachmentsConnect,
  type SupportTicket,
  type SupportTicketDetail,
  type SupportTicketMessage,
  type SupportTicketAttachment,
  type SupportTicketListResponse,
  type SupportTicketListParams,
} from "../connect/supportTicketConnect";
