use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_user_v1 as user_proto;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================
//
// UserService (proto.user.v1):
//   * GetMe / UpdateMe / ChangePassword — caller's profile
//   * ListIdentities / DeleteIdentity — caller's OAuth identities
//   * SearchUsers — query users by name / email / username
//
// All RPCs are user-scoped — auth interceptor supplies the user ID
// server-side; no org_slug in any request (conventions §3.5 exception #1).
// Procedure paths derive from `proto.user.v1.UserService/<Method>`
// (conventions §12). connect_call enforces application/proto + Connect
// protocol headers; auth bearer is added when token is present.

impl ApiClient {
    pub async fn get_me_connect(
        &self,
        req: &user_proto::GetMeRequest,
    ) -> Result<user_proto::User, ApiError> {
        connect_call(self, "/proto.user.v1.UserService/GetMe", req).await
    }

    pub async fn update_me_connect(
        &self,
        req: &user_proto::UpdateMeRequest,
    ) -> Result<user_proto::User, ApiError> {
        connect_call(self, "/proto.user.v1.UserService/UpdateMe", req).await
    }

    pub async fn change_password_connect(
        &self,
        req: &user_proto::ChangePasswordRequest,
    ) -> Result<user_proto::ChangePasswordResponse, ApiError> {
        connect_call(self, "/proto.user.v1.UserService/ChangePassword", req).await
    }

    pub async fn list_identities_connect(
        &self,
        req: &user_proto::ListIdentitiesRequest,
    ) -> Result<user_proto::ListIdentitiesResponse, ApiError> {
        connect_call(self, "/proto.user.v1.UserService/ListIdentities", req).await
    }

    pub async fn delete_identity_connect(
        &self,
        req: &user_proto::DeleteIdentityRequest,
    ) -> Result<user_proto::DeleteIdentityResponse, ApiError> {
        connect_call(self, "/proto.user.v1.UserService/DeleteIdentity", req).await
    }

    pub async fn search_users_connect(
        &self,
        req: &user_proto::SearchUsersRequest,
    ) -> Result<user_proto::SearchUsersResponse, ApiError> {
        connect_call(self, "/proto.user.v1.UserService/SearchUsers", req).await
    }
}
