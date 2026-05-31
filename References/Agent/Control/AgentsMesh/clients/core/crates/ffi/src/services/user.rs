use agentsmesh_types::proto_user_v1 as user_proto;

use crate::core::AgentsMeshCore;
use crate::dto::UserDto;
use crate::error::CoreError;

/// Strongly-typed `User` API — Connect-RPC proto.user.v1.UserService.
/// REST `GET /me` remains alive only until AuthManager bootstrap migrates
/// off it (tracked at the call site in clients/core/crates/auth).
#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    /// Fetch the current authenticated user from the server. Useful after
    /// `restore_session` to confirm the token is still valid before routing
    /// the app past the login gate.
    pub async fn fetch_me(&self) -> Result<UserDto, CoreError> {
        let req = user_proto::GetMeRequest {};
        let user = self.api.get_me_connect(&req).await?;
        Ok(user.into())
    }
}
