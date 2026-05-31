use agentsmesh_types::proto_runner_api_v1 as runner_proto;

use crate::core::AgentsMeshCore;
use crate::dto::{
    runner_list_from_proto, runner_log_list_from_proto, runner_token_list_from_proto, AuthorizeRunnerRequestDto,
    CreateRunnerTokenRequestDto, GrpcRegistrationTokenDto, PodListResponseDto, RunnerAuthStatusDto, RunnerDto,
    RunnerListResponseDto, RunnerLogListResponseDto, RunnerTokenListResponseDto, UpdateRunnerRequestDto,
    UpgradeRunnerRequestDto,
};
use crate::error::CoreError;

#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    pub async fn list_runners(
        &self,
        status: Option<String>,
    ) -> Result<RunnerListResponseDto, CoreError> {
        let req = runner_proto::ListRunnersRequest {
            org_slug: self.org_slug()?,
            status,
            offset: None,
            limit: None,
        };
        let resp = self.api.list_runners_connect(&req).await?;
        Ok(runner_list_from_proto(resp))
    }

    pub async fn list_available_runners(&self) -> Result<RunnerListResponseDto, CoreError> {
        let req = runner_proto::ListAvailableRunnersRequest { org_slug: self.org_slug()? };
        let resp = self.api.list_available_runners_connect(&req).await?;
        Ok(RunnerListResponseDto {
            runners: resp.items.into_iter().map(RunnerDto::from).collect(),
            latest_runner_version: None,
        })
    }

    pub async fn get_runner(&self, id: i64) -> Result<RunnerDto, CoreError> {
        let req = runner_proto::GetRunnerRequest { org_slug: self.org_slug()?, id };
        let resp = self.api.get_runner_connect(&req).await?;
        let runner = resp.runner.ok_or_else(|| CoreError::Unknown {
            message: "GetRunner returned no runner".into(),
        })?;
        Ok(runner.into())
    }

    pub async fn update_runner(
        &self,
        id: i64,
        req: UpdateRunnerRequestDto,
    ) -> Result<RunnerDto, CoreError> {
        let proto_req = runner_proto::UpdateRunnerRequest {
            org_slug: self.org_slug()?,
            id,
            description: req.description,
            max_concurrent_pods: req.max_concurrent_pods,
            is_enabled: req.is_enabled,
            visibility: req.visibility,
            tags: None,
        };
        let runner = self.api.update_runner_connect(&proto_req).await?;
        Ok(runner.into())
    }

    pub async fn delete_runner(&self, id: i64) -> Result<(), CoreError> {
        let req = runner_proto::DeleteRunnerRequest { org_slug: self.org_slug()?, id };
        self.api.delete_runner_connect(&req).await?;
        Ok(())
    }

    pub async fn create_runner_token(
        &self,
        req: CreateRunnerTokenRequestDto,
    ) -> Result<GrpcRegistrationTokenDto, CoreError> {
        let proto_req = runner_proto::CreateRunnerTokenRequest {
            org_slug: self.org_slug()?,
            name: req.name,
            labels: req.labels.unwrap_or_default(),
            max_uses: req.max_uses,
            expires_in_days: req.expires_in_days,
        };
        let tok = self.api.create_runner_token_connect(&proto_req).await?;
        Ok(tok.into())
    }

    pub async fn list_runner_tokens(&self) -> Result<RunnerTokenListResponseDto, CoreError> {
        let req = runner_proto::ListRunnerTokensRequest { org_slug: self.org_slug()? };
        let resp = self.api.list_runner_tokens_connect(&req).await?;
        Ok(runner_token_list_from_proto(resp))
    }

    pub async fn delete_runner_token(&self, id: i64) -> Result<(), CoreError> {
        let req = runner_proto::DeleteRunnerTokenRequest { org_slug: self.org_slug()?, id };
        self.api.delete_runner_token_connect(&req).await?;
        Ok(())
    }

    // Proto RunnerService has no ListRunnerPods — staying on REST until the
    // pod service grows a runner_id filter (proto.pod.v1.ListPodsRequest has
    // no runner_id today).
    pub async fn list_runner_pods(
        &self,
        id: i64,
        status: Option<String>,
        limit: Option<u32>,
        offset: Option<u32>,
    ) -> Result<PodListResponseDto, CoreError> {
        let resp = self
            .api
            .list_runner_pods(id, status.as_deref(), limit, offset)
            .await?;
        Ok(resp.into())
    }

    pub async fn upgrade_runner(
        &self,
        id: i64,
        req: UpgradeRunnerRequestDto,
    ) -> Result<(), CoreError> {
        let proto_req = runner_proto::UpgradeRunnerRequest {
            org_slug: self.org_slug()?,
            id,
            target_version: req.target_version.unwrap_or_default(),
            force: req.force.unwrap_or(false),
        };
        self.api.upgrade_runner_connect(&proto_req).await?;
        Ok(())
    }

    pub async fn request_runner_log_upload(&self, id: i64) -> Result<(), CoreError> {
        let req = runner_proto::RequestLogUploadRequest { org_slug: self.org_slug()?, id };
        self.api.request_log_upload_connect(&req).await?;
        Ok(())
    }

    pub async fn list_runner_logs(&self, id: i64) -> Result<RunnerLogListResponseDto, CoreError> {
        let req = runner_proto::ListRunnerLogsRequest {
            org_slug: self.org_slug()?,
            id,
            offset: None,
            limit: None,
        };
        let resp = self.api.list_runner_logs_connect(&req).await?;
        Ok(runner_log_list_from_proto(resp))
    }

    // Public registration / authorization flow — no proto Connect surface
    // (the user-facing /runners/auth/* lives outside the org-scoped Runner
    // service). REST stays.
    pub async fn get_runner_auth_status(
        &self,
        auth_key: String,
    ) -> Result<RunnerAuthStatusDto, CoreError> {
        let status = self.api.get_runner_auth_status(&auth_key).await?;
        Ok(status.into())
    }

    pub async fn authorize_runner(
        &self,
        req: AuthorizeRunnerRequestDto,
    ) -> Result<(), CoreError> {
        self.api.authorize_runner(&req.into()).await?;
        Ok(())
    }
}
