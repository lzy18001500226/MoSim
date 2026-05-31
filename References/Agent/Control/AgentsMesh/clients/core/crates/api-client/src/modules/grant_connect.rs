use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_grant_v1 as gp;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================
//
// One service, three resource types — the REST split was policy-only;
// the wire was already unified.

impl ApiClient {
    pub async fn list_grants_connect(
        &self,
        req: &gp::ListGrantsRequest,
    ) -> Result<gp::ListGrantsResponse, ApiError> {
        connect_call(
            self,
            "/proto.grant.v1.GrantService/ListGrants",
            req,
        )
        .await
    }

    pub async fn create_grant_connect(
        &self,
        req: &gp::CreateGrantRequest,
    ) -> Result<gp::ResourceGrant, ApiError> {
        connect_call(
            self,
            "/proto.grant.v1.GrantService/CreateGrant",
            req,
        )
        .await
    }

    pub async fn delete_grant_connect(
        &self,
        req: &gp::DeleteGrantRequest,
    ) -> Result<gp::DeleteGrantResponse, ApiError> {
        connect_call(
            self,
            "/proto.grant.v1.GrantService/DeleteGrant",
            req,
        )
        .await
    }
}
