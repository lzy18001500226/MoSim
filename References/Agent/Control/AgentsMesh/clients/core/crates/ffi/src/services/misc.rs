use agentsmesh_types::proto_file_v1 as file_proto;
use agentsmesh_types::proto_grant_v1 as grant_proto;
use agentsmesh_types::proto_invitation_v1 as inv_proto;

use crate::core::AgentsMeshCore;
use crate::dto::{
    invitation_list_from_proto, pending_invitation_list_from_proto, resource_grant_list_from_proto,
    InvitationDto, InvitationListResponseDto, PresignRequestDto, PresignResponseDto,
    ResourceGrantListResponseDto, ResourceGrantResponseDto,
};
use crate::error::CoreError;

#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    // ── Invitations ───────────────────────────────────────

    pub async fn list_invitations(&self) -> Result<InvitationListResponseDto, CoreError> {
        let req = inv_proto::ListInvitationsRequest {
            org_slug: self.org_slug()?,
            offset: None,
            limit: None,
        };
        let resp = self.api.list_invitations_connect(&req).await?;
        Ok(invitation_list_from_proto(resp))
    }

    pub async fn create_invitation(
        &self,
        email: String,
        role: String,
    ) -> Result<InvitationDto, CoreError> {
        let req = inv_proto::CreateInvitationRequest {
            org_slug: self.org_slug()?,
            email,
            role,
        };
        let inv = self.api.create_invitation_connect(&req).await?;
        Ok(inv.into())
    }

    pub async fn revoke_invitation(&self, id: i64) -> Result<(), CoreError> {
        let req = inv_proto::RevokeInvitationRequest { org_slug: self.org_slug()?, id };
        self.api.revoke_invitation_connect(&req).await?;
        Ok(())
    }

    pub async fn resend_invitation(&self, id: i64) -> Result<(), CoreError> {
        let req = inv_proto::ResendInvitationRequest { org_slug: self.org_slug()?, id };
        self.api.resend_invitation_connect(&req).await?;
        Ok(())
    }

    pub async fn get_invitation_by_token(&self, token: String) -> Result<InvitationDto, CoreError> {
        let req = inv_proto::GetInvitationByTokenRequest { token };
        let info = self.api.get_invitation_by_token_connect(&req).await?;
        Ok(info.into())
    }

    pub async fn accept_invitation(&self, token: String) -> Result<(), CoreError> {
        let req = inv_proto::AcceptInvitationRequest { token };
        self.api.accept_invitation_connect(&req).await?;
        Ok(())
    }

    pub async fn list_pending_invitations(
        &self,
    ) -> Result<InvitationListResponseDto, CoreError> {
        let req = inv_proto::ListPendingInvitationsRequest {};
        let resp = self.api.list_pending_invitations_connect(&req).await?;
        Ok(pending_invitation_list_from_proto(resp))
    }

    // ── File presign ──────────────────────────────────────

    pub async fn presign_file_upload(
        &self,
        req: PresignRequestDto,
    ) -> Result<PresignResponseDto, CoreError> {
        let proto_req = file_proto::PresignUploadRequest {
            org_slug: self.org_slug()?,
            filename: req.filename,
            content_type: req.content_type,
            size: req.size,
        };
        let resp = self.api.presign_upload_connect(&proto_req).await?;
        Ok(resp.into())
    }

    // ── Resource Grants ───────────────────────────────────

    pub async fn list_resource_grants(
        &self,
        resource_type: String,
        resource_id: String,
    ) -> Result<ResourceGrantListResponseDto, CoreError> {
        let req = grant_proto::ListGrantsRequest {
            org_slug: self.org_slug()?,
            resource_type,
            resource_id,
        };
        let resp = self.api.list_grants_connect(&req).await?;
        Ok(resource_grant_list_from_proto(resp))
    }

    pub async fn grant_resource_access(
        &self,
        resource_type: String,
        resource_id: String,
        user_id: i64,
    ) -> Result<ResourceGrantResponseDto, CoreError> {
        let req = grant_proto::CreateGrantRequest {
            org_slug: self.org_slug()?,
            resource_type,
            resource_id,
            user_id,
        };
        let grant = self.api.create_grant_connect(&req).await?;
        Ok(grant.into())
    }

    pub async fn revoke_resource_grant(
        &self,
        resource_type: String,
        resource_id: String,
        grant_id: i64,
    ) -> Result<(), CoreError> {
        let req = grant_proto::DeleteGrantRequest {
            org_slug: self.org_slug()?,
            resource_type,
            resource_id,
            grant_id,
        };
        self.api.delete_grant_connect(&req).await?;
        Ok(())
    }
}
