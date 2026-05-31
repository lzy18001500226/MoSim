use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_token_usage_v1 as tup;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================

impl ApiClient {
    pub async fn get_token_usage_dashboard_connect(
        &self,
        req: &tup::GetDashboardRequest,
    ) -> Result<tup::GetDashboardResponse, ApiError> {
        connect_call(
            self,
            "/proto.token_usage.v1.TokenUsageService/GetDashboard",
            req,
        )
        .await
    }
}
