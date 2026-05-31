use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_notification_v1 as np;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================

impl ApiClient {
    pub async fn list_notification_preferences_connect(
        &self,
        req: &np::ListPreferencesRequest,
    ) -> Result<np::ListPreferencesResponse, ApiError> {
        connect_call(
            self,
            "/proto.notification.v1.NotificationService/ListPreferences",
            req,
        )
        .await
    }

    pub async fn set_notification_preference_connect(
        &self,
        req: &np::SetPreferenceRequest,
    ) -> Result<np::NotificationPreference, ApiError> {
        connect_call(
            self,
            "/proto.notification.v1.NotificationService/SetPreference",
            req,
        )
        .await
    }
}
