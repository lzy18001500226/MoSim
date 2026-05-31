use agentsmesh_types::proto_autopilot_v1 as ap_proto;

use crate::core::AgentsMeshCore;
use crate::dto::{
    AutopilotControllerDto, AutopilotIterationListResponseDto, AutopilotListResponseDto,
    CreateAutopilotRequestDto,
};
use crate::error::CoreError;
use crate::services::automation_proto_convert::{
    autopilot_iterations_from_proto, autopilot_list_from_proto,
};

#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    pub async fn list_autopilots(&self) -> Result<AutopilotListResponseDto, CoreError> {
        let req = ap_proto::ListAutopilotControllersRequest { org_slug: self.org_slug()? };
        let resp = self.api.list_autopilots_connect(&req).await?;
        Ok(autopilot_list_from_proto(resp))
    }

    pub async fn get_autopilot(&self, key: String) -> Result<AutopilotControllerDto, CoreError> {
        let req = ap_proto::GetAutopilotControllerRequest { org_slug: self.org_slug()?, key };
        let c = self.api.get_autopilot_connect(&req).await?;
        Ok(c.into())
    }

    pub async fn create_autopilot(
        &self,
        req: CreateAutopilotRequestDto,
    ) -> Result<AutopilotControllerDto, CoreError> {
        let proto_req = ap_proto::CreateAutopilotControllerRequest {
            org_slug: self.org_slug()?,
            pod_key: req.pod_key,
            prompt: req.prompt.unwrap_or_default(),
            max_iterations: req.max_iterations.unwrap_or(0) as i32,
            iteration_timeout_sec: req.iteration_timeout_sec.unwrap_or(0) as i32,
            no_progress_threshold: req.no_progress_threshold.unwrap_or(0) as i32,
            same_error_threshold: req.same_error_threshold.unwrap_or(0) as i32,
            approval_timeout_min: req.approval_timeout_min.unwrap_or(0) as i32,
            control_agent_slug: req.control_agent_slug.unwrap_or_default(),
            control_prompt_template: req.control_prompt_template.unwrap_or_default(),
            mcp_config_json: req.mcp_config_json.unwrap_or_default(),
        };
        let c = self.api.create_autopilot_connect(&proto_req).await?;
        Ok(c.into())
    }

    pub async fn pause_autopilot(&self, key: String) -> Result<(), CoreError> {
        let req = ap_proto::ActionRequest { org_slug: self.org_slug()?, key };
        self.api.pause_autopilot_connect(&req).await?;
        Ok(())
    }

    pub async fn resume_autopilot(&self, key: String) -> Result<(), CoreError> {
        let req = ap_proto::ActionRequest { org_slug: self.org_slug()?, key };
        self.api.resume_autopilot_connect(&req).await?;
        Ok(())
    }

    pub async fn stop_autopilot(&self, key: String) -> Result<(), CoreError> {
        let req = ap_proto::ActionRequest { org_slug: self.org_slug()?, key };
        self.api.stop_autopilot_connect(&req).await?;
        Ok(())
    }

    pub async fn approve_autopilot(
        &self,
        key: String,
        continue_execution: Option<bool>,
        additional_iterations: Option<i64>,
    ) -> Result<(), CoreError> {
        let req = ap_proto::ApproveRequest {
            org_slug: self.org_slug()?,
            key,
            continue_execution,
            additional_iterations: additional_iterations.unwrap_or(0) as i32,
        };
        self.api.approve_autopilot_connect(&req).await?;
        Ok(())
    }

    pub async fn takeover_autopilot(&self, key: String) -> Result<(), CoreError> {
        let req = ap_proto::ActionRequest { org_slug: self.org_slug()?, key };
        self.api.takeover_autopilot_connect(&req).await?;
        Ok(())
    }

    pub async fn handback_autopilot(&self, key: String) -> Result<(), CoreError> {
        let req = ap_proto::ActionRequest { org_slug: self.org_slug()?, key };
        self.api.handback_autopilot_connect(&req).await?;
        Ok(())
    }

    pub async fn get_autopilot_iterations(
        &self,
        key: String,
    ) -> Result<AutopilotIterationListResponseDto, CoreError> {
        let req = ap_proto::GetIterationsRequest { org_slug: self.org_slug()?, key };
        let resp = self.api.get_autopilot_iterations_connect(&req).await?;
        Ok(autopilot_iterations_from_proto(resp))
    }
}
