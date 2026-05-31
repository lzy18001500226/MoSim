use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_org_v1 as org_proto;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================
//
// These methods call the Connect handlers in
// backend/internal/api/connect/org/. Procedure paths derive from
// `proto.org.v1.OrgService.<Method>` (conventions §12).

impl ApiClient {
    pub async fn list_my_orgs_connect(
        &self,
        req: &org_proto::ListMyOrgsRequest,
    ) -> Result<org_proto::ListMyOrgsResponse, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/ListMyOrgs", req).await
    }

    pub async fn create_org_connect(
        &self,
        req: &org_proto::CreateOrgRequest,
    ) -> Result<org_proto::Organization, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/CreateOrg", req).await
    }

    pub async fn create_personal_org_connect(
        &self,
        req: &org_proto::CreatePersonalOrgRequest,
    ) -> Result<org_proto::Organization, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/CreatePersonalOrg", req).await
    }

    pub async fn get_org_connect(
        &self,
        req: &org_proto::GetOrgRequest,
    ) -> Result<org_proto::Organization, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/GetOrg", req).await
    }

    pub async fn update_org_connect(
        &self,
        req: &org_proto::UpdateOrgRequest,
    ) -> Result<org_proto::Organization, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/UpdateOrg", req).await
    }

    pub async fn delete_org_connect(
        &self,
        req: &org_proto::DeleteOrgRequest,
    ) -> Result<org_proto::DeleteOrgResponse, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/DeleteOrg", req).await
    }

    pub async fn list_members_connect(
        &self,
        req: &org_proto::ListMembersRequest,
    ) -> Result<org_proto::ListMembersResponse, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/ListMembers", req).await
    }

    pub async fn invite_member_connect(
        &self,
        req: &org_proto::InviteMemberRequest,
    ) -> Result<org_proto::InviteMemberResponse, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/InviteMember", req).await
    }

    pub async fn remove_member_connect(
        &self,
        req: &org_proto::RemoveMemberRequest,
    ) -> Result<org_proto::RemoveMemberResponse, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/RemoveMember", req).await
    }

    pub async fn update_member_role_connect(
        &self,
        req: &org_proto::UpdateMemberRoleRequest,
    ) -> Result<org_proto::UpdateMemberRoleResponse, ApiError> {
        connect_call(self, "/proto.org.v1.OrgService/UpdateMemberRole", req).await
    }
}
