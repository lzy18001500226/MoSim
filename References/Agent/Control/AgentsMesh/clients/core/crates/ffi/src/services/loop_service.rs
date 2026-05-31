use agentsmesh_types::proto_loop_v1 as lp_proto;

use crate::core::AgentsMeshCore;
use crate::dto::{
    CreateLoopRequestDto, LoopDataDto, LoopListResponseDto, LoopRunDataDto,
    LoopRunListResponseDto, UpdateLoopRequestDto,
};
use crate::error::CoreError;
use crate::services::automation_proto_convert::{
    loop_list_from_proto, loop_run_from_proto, loop_run_list_from_proto,
};

#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    pub async fn list_loops(
        &self,
        status: Option<String>,
        limit: Option<u32>,
        offset: Option<u32>,
    ) -> Result<LoopListResponseDto, CoreError> {
        let req = lp_proto::ListLoopsRequest {
            org_slug: self.org_slug()?,
            status: status.unwrap_or_default(),
            execution_mode: String::new(),
            cron_enabled: None,
            query: String::new(),
            offset: offset.map(|v| v as i32),
            limit: limit.map(|v| v as i32),
        };
        let resp = self.api.list_loops_connect(&req).await?;
        Ok(loop_list_from_proto(resp))
    }

    pub async fn get_loop(&self, slug: String) -> Result<LoopDataDto, CoreError> {
        let req = lp_proto::GetLoopRequest { org_slug: self.org_slug()?, loop_slug: slug };
        let l = self.api.get_loop_connect(&req).await?;
        Ok(l.into())
    }

    pub async fn create_loop(&self, req: CreateLoopRequestDto) -> Result<LoopDataDto, CoreError> {
        let proto_req = lp_proto::CreateLoopRequest {
            org_slug: self.org_slug()?,
            name: req.name,
            slug: req.slug.unwrap_or_default(),
            description: req.description.unwrap_or_default(),
            agent_slug: req.agent_slug.or(req.custom_agent_slug).unwrap_or_default(),
            permission_mode: req.permission_mode.unwrap_or_default(),
            prompt_template: req.prompt_template.unwrap_or_default(),
            prompt_variables_json: req.prompt_variables_json.unwrap_or_default(),
            config_overrides_json: req.config_overrides_json.unwrap_or_default(),
            autopilot_config_json: req.autopilot_config_json.unwrap_or_default(),
            repository_id: req.repository_id,
            runner_id: req.runner_id,
            branch_name: req.branch_name.unwrap_or_default(),
            ticket_id: req.ticket_id.and_then(|s| s.parse::<i64>().ok()),
            credential_profile_id: req.credential_profile_id,
            execution_mode: req.execution_mode.unwrap_or_default(),
            cron_expression: req.cron_expression.unwrap_or_default(),
            callback_url: req.callback_url.unwrap_or_default(),
            sandbox_strategy: req.sandbox_strategy.unwrap_or_default(),
            // Legacy DTO ships session_persistence as Option<String>; preserve
            // any truthy textual value (matches the prior REST request shape).
            session_persistence: req
                .session_persistence
                .map(|s| matches!(s.as_str(), "true" | "1" | "yes")),
            concurrency_policy: req.concurrency_policy.unwrap_or_default(),
            max_concurrent_runs: req.max_concurrent_runs.map(|v| v as i32),
            max_retained_runs: req.max_retained_runs.map(|v| v as i32),
            timeout_minutes: req.timeout_minutes.map(|v| v as i32),
            idle_timeout_sec: None,
            used_env_bundles: vec![],
        };
        let l = self.api.create_loop_connect(&proto_req).await?;
        Ok(l.into())
    }

    pub async fn update_loop(
        &self,
        slug: String,
        req: UpdateLoopRequestDto,
    ) -> Result<LoopDataDto, CoreError> {
        let proto_req = lp_proto::UpdateLoopRequest {
            org_slug: self.org_slug()?,
            loop_slug: slug,
            name: req.name,
            description: req.description,
            agent_slug: req.agent_slug.unwrap_or_default(),
            permission_mode: None,
            prompt_template: req.prompt_template,
            prompt_variables_json: req.prompt_variables_json.unwrap_or_default(),
            config_overrides_json: String::new(),
            autopilot_config_json: req.autopilot_config_json.unwrap_or_default(),
            repository_id: req.repository_id,
            runner_id: req.runner_id,
            branch_name: req.branch_name,
            ticket_id: None,
            credential_profile_id: None,
            execution_mode: None,
            cron_expression: req.cron_expression,
            callback_url: None,
            sandbox_strategy: req.sandbox_strategy,
            session_persistence: req
                .session_persistence
                .map(|s| matches!(s.as_str(), "true" | "1" | "yes")),
            concurrency_policy: req.concurrency_policy,
            max_concurrent_runs: req.max_concurrent_runs.map(|v| v as i32),
            max_retained_runs: req.max_retained_runs.map(|v| v as i32),
            timeout_minutes: req.timeout_minutes.map(|v| v as i32),
            idle_timeout_sec: None,
            used_env_bundles: None,
        };
        let l = self.api.update_loop_connect(&proto_req).await?;
        Ok(l.into())
    }

    pub async fn delete_loop(&self, slug: String) -> Result<(), CoreError> {
        let req = lp_proto::DeleteLoopRequest { org_slug: self.org_slug()?, loop_slug: slug };
        self.api.delete_loop_connect(&req).await?;
        Ok(())
    }

    pub async fn enable_loop(&self, slug: String) -> Result<(), CoreError> {
        let req = lp_proto::LoopActionRequest { org_slug: self.org_slug()?, loop_slug: slug };
        self.api.enable_loop_connect(&req).await?;
        Ok(())
    }

    pub async fn disable_loop(&self, slug: String) -> Result<(), CoreError> {
        let req = lp_proto::LoopActionRequest { org_slug: self.org_slug()?, loop_slug: slug };
        self.api.disable_loop_connect(&req).await?;
        Ok(())
    }

    pub async fn trigger_loop(&self, slug: String) -> Result<LoopRunDataDto, CoreError> {
        let req = lp_proto::TriggerLoopRequest {
            org_slug: self.org_slug()?,
            loop_slug: slug.clone(),
            variables_json: String::new(),
        };
        let resp = self.api.trigger_loop_connect(&req).await?;
        // Concurrency-policy=skip surfaces as a synthetic empty run; the
        // legacy REST flow returned 200 with the (possibly null) run, so we
        // map skipped → a placeholder run to keep the FFI type stable.
        let run = resp.run.unwrap_or_default();
        Ok(loop_run_from_proto(run, slug))
    }

    pub async fn list_loop_runs(
        &self,
        slug: String,
        status: Option<String>,
        limit: Option<u32>,
        offset: Option<u32>,
    ) -> Result<LoopRunListResponseDto, CoreError> {
        let req = lp_proto::ListRunsRequest {
            org_slug: self.org_slug()?,
            loop_slug: slug.clone(),
            status: status.unwrap_or_default(),
            offset: offset.map(|v| v as i32),
            limit: limit.map(|v| v as i32),
        };
        let resp = self.api.list_loop_runs_connect(&req).await?;
        Ok(loop_run_list_from_proto(resp, slug))
    }

    pub async fn cancel_loop_run(&self, slug: String, run_id: i64) -> Result<(), CoreError> {
        let req = lp_proto::CancelRunRequest {
            org_slug: self.org_slug()?,
            loop_slug: slug,
            run_id,
        };
        self.api.cancel_loop_run_connect(&req).await?;
        Ok(())
    }
}

// Carve-out: `get_loop_run` (single-run fetch) is intentionally **not**
// exposed here. proto.loop.v1.LoopService has no GetRun RPC — only
// ListRuns / CancelRun. Callers that need a specific run should filter
// `list_loop_runs` client-side until the proto surface grows.
