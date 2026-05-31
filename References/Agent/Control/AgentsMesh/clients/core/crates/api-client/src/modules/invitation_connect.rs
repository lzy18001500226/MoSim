use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_invitation_v1 as inv_proto;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================
//
// Three services in proto.invitation.v1:
//   * InvitationService          — org-scoped admin (list/create/revoke/resend)
//   * UserInvitationService      — auth-required, no org_slug (accept, list_pending)
//   * PublicInvitationService    — unauthenticated (get_by_token)
//
// Procedure paths derive from `proto.invitation.v1.<Service>/<Method>`
// (conventions §12). connect_call enforces application/proto and Connect
// protocol headers; the public endpoint uses the same helper because it
// just skips the Authorization header when no token is in the store.

impl ApiClient {
    // -------- InvitationService (org-scoped) --------

    pub async fn list_invitations_connect(
        &self,
        req: &inv_proto::ListInvitationsRequest,
    ) -> Result<inv_proto::ListInvitationsResponse, ApiError> {
        connect_call(
            self,
            "/proto.invitation.v1.InvitationService/ListInvitations",
            req,
        )
        .await
    }

    pub async fn create_invitation_connect(
        &self,
        req: &inv_proto::CreateInvitationRequest,
    ) -> Result<inv_proto::Invitation, ApiError> {
        connect_call(
            self,
            "/proto.invitation.v1.InvitationService/CreateInvitation",
            req,
        )
        .await
    }

    pub async fn revoke_invitation_connect(
        &self,
        req: &inv_proto::RevokeInvitationRequest,
    ) -> Result<inv_proto::RevokeInvitationResponse, ApiError> {
        connect_call(
            self,
            "/proto.invitation.v1.InvitationService/RevokeInvitation",
            req,
        )
        .await
    }

    pub async fn resend_invitation_connect(
        &self,
        req: &inv_proto::ResendInvitationRequest,
    ) -> Result<inv_proto::ResendInvitationResponse, ApiError> {
        connect_call(
            self,
            "/proto.invitation.v1.InvitationService/ResendInvitation",
            req,
        )
        .await
    }

    // -------- UserInvitationService (auth, no org_slug) --------

    pub async fn accept_invitation_connect(
        &self,
        req: &inv_proto::AcceptInvitationRequest,
    ) -> Result<inv_proto::AcceptInvitationResponse, ApiError> {
        connect_call(
            self,
            "/proto.invitation.v1.UserInvitationService/AcceptInvitation",
            req,
        )
        .await
    }

    pub async fn list_pending_invitations_connect(
        &self,
        req: &inv_proto::ListPendingInvitationsRequest,
    ) -> Result<inv_proto::ListPendingInvitationsResponse, ApiError> {
        connect_call(
            self,
            "/proto.invitation.v1.UserInvitationService/ListPendingInvitations",
            req,
        )
        .await
    }

    // -------- PublicInvitationService (no auth) --------

    pub async fn get_invitation_by_token_connect(
        &self,
        req: &inv_proto::GetInvitationByTokenRequest,
    ) -> Result<inv_proto::InvitationInfo, ApiError> {
        connect_call(
            self,
            "/proto.invitation.v1.PublicInvitationService/GetInvitationByToken",
            req,
        )
        .await
    }
}
