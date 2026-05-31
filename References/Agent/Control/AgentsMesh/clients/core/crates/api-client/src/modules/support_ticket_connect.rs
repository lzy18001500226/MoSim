use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_support_ticket_v1 as st_proto;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================
//
// User-scoped SupportTicketService (conventions §3.5 exception #1) —
// requests carry no org_slug. The auth interceptor injects UserID;
// ownership / access checks live in the Go service layer.
//
// Procedure paths derive from `proto.support_ticket.v1.SupportTicketService/<Method>`
// (conventions §12). connect_call enforces application/proto and Connect
// protocol headers.

impl ApiClient {
    pub async fn list_support_tickets_connect(
        &self,
        req: &st_proto::ListSupportTicketsRequest,
    ) -> Result<st_proto::ListSupportTicketsResponse, ApiError> {
        connect_call(
            self,
            "/proto.support_ticket.v1.SupportTicketService/ListSupportTickets",
            req,
        )
        .await
    }

    pub async fn get_support_ticket_connect(
        &self,
        req: &st_proto::GetSupportTicketRequest,
    ) -> Result<st_proto::SupportTicketDetail, ApiError> {
        connect_call(
            self,
            "/proto.support_ticket.v1.SupportTicketService/GetSupportTicket",
            req,
        )
        .await
    }

    pub async fn get_support_ticket_attachment_url_connect(
        &self,
        req: &st_proto::GetAttachmentUrlRequest,
    ) -> Result<st_proto::GetAttachmentUrlResponse, ApiError> {
        connect_call(
            self,
            "/proto.support_ticket.v1.SupportTicketService/GetAttachmentUrl",
            req,
        )
        .await
    }

    pub async fn create_support_ticket_connect(
        &self,
        req: &st_proto::CreateSupportTicketRequest,
    ) -> Result<st_proto::SupportTicket, ApiError> {
        connect_call(
            self,
            "/proto.support_ticket.v1.SupportTicketService/CreateSupportTicket",
            req,
        )
        .await
    }

    pub async fn add_support_ticket_message_connect(
        &self,
        req: &st_proto::AddSupportTicketMessageRequest,
    ) -> Result<st_proto::SupportTicketMessage, ApiError> {
        connect_call(
            self,
            "/proto.support_ticket.v1.SupportTicketService/AddSupportTicketMessage",
            req,
        )
        .await
    }

    pub async fn presign_support_ticket_attachment_connect(
        &self,
        req: &st_proto::PresignAttachmentUploadRequest,
    ) -> Result<st_proto::PresignAttachmentUploadResponse, ApiError> {
        connect_call(
            self,
            "/proto.support_ticket.v1.SupportTicketService/PresignAttachmentUpload",
            req,
        )
        .await
    }

    pub async fn associate_support_ticket_attachments_connect(
        &self,
        req: &st_proto::AssociateAttachmentsRequest,
    ) -> Result<st_proto::AssociateAttachmentsResponse, ApiError> {
        connect_call(
            self,
            "/proto.support_ticket.v1.SupportTicketService/AssociateAttachments",
            req,
        )
        .await
    }
}
