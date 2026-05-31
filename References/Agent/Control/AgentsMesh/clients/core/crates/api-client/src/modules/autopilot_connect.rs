use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_autopilot_v1 as ap;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================

impl ApiClient {
    pub async fn list_autopilots_connect(
        &self,
        req: &ap::ListAutopilotControllersRequest,
    ) -> Result<ap::ListAutopilotControllersResponse, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/ListAutopilotControllers",
            req,
        )
        .await
    }

    pub async fn get_autopilot_connect(
        &self,
        req: &ap::GetAutopilotControllerRequest,
    ) -> Result<ap::AutopilotController, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/GetAutopilotController",
            req,
        )
        .await
    }

    pub async fn create_autopilot_connect(
        &self,
        req: &ap::CreateAutopilotControllerRequest,
    ) -> Result<ap::AutopilotController, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/CreateAutopilotController",
            req,
        )
        .await
    }

    pub async fn pause_autopilot_connect(
        &self,
        req: &ap::ActionRequest,
    ) -> Result<ap::ActionResponse, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/PauseAutopilotController",
            req,
        )
        .await
    }

    pub async fn resume_autopilot_connect(
        &self,
        req: &ap::ActionRequest,
    ) -> Result<ap::ActionResponse, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/ResumeAutopilotController",
            req,
        )
        .await
    }

    pub async fn stop_autopilot_connect(
        &self,
        req: &ap::ActionRequest,
    ) -> Result<ap::ActionResponse, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/StopAutopilotController",
            req,
        )
        .await
    }

    pub async fn approve_autopilot_connect(
        &self,
        req: &ap::ApproveRequest,
    ) -> Result<ap::ActionResponse, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/ApproveAutopilotController",
            req,
        )
        .await
    }

    pub async fn takeover_autopilot_connect(
        &self,
        req: &ap::ActionRequest,
    ) -> Result<ap::ActionResponse, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/TakeoverAutopilotController",
            req,
        )
        .await
    }

    pub async fn handback_autopilot_connect(
        &self,
        req: &ap::ActionRequest,
    ) -> Result<ap::ActionResponse, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/HandbackAutopilotController",
            req,
        )
        .await
    }

    pub async fn get_autopilot_iterations_connect(
        &self,
        req: &ap::GetIterationsRequest,
    ) -> Result<ap::GetIterationsResponse, ApiError> {
        connect_call(
            self,
            "/proto.autopilot.v1.AutopilotControllerService/GetIterations",
            req,
        )
        .await
    }
}
