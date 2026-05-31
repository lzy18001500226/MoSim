// ── Enums ─────────────────────────────────────────────────

#[derive(Clone, Copy, Debug, uniffi::Enum)]
pub enum AutopilotStatusDto {
    Idle,
    Running,
    Paused,
    WaitingApproval,
    Completed,
    Failed,
    Terminated,
    Unknown,
}

#[derive(Clone, Copy, Debug, uniffi::Enum)]
pub enum LoopRunStatusDto {
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
    Unknown,
}

// ── Autopilot ─────────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct AutopilotControllerDto {
    pub autopilot_controller_key: String,
    pub pod_key: String,
    pub status: Option<AutopilotStatusDto>,
    pub phase: Option<String>,
    pub prompt: Option<String>,
    pub max_iterations: Option<i64>,
    pub iteration_timeout_sec: Option<i64>,
    pub no_progress_threshold: Option<i64>,
    pub same_error_threshold: Option<i64>,
    pub approval_timeout_min: Option<i64>,
    pub current_iteration: Option<i64>,
    pub control_agent_slug: Option<String>,
    pub circuit_breaker_state: Option<String>,
    pub circuit_breaker_reason: Option<String>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct AutopilotListResponseDto {
    pub controllers: Vec<AutopilotControllerDto>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct AutopilotIterationDto {
    pub id: i64,
    pub controller_key: String,
    pub iteration_number: Option<i64>,
    pub status: Option<String>,
    pub result: Option<String>,
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct AutopilotIterationListResponseDto {
    pub iterations: Vec<AutopilotIterationDto>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct CreateAutopilotRequestDto {
    pub pod_key: String,
    pub prompt: Option<String>,
    pub max_iterations: Option<i64>,
    pub iteration_timeout_sec: Option<i64>,
    pub no_progress_threshold: Option<i64>,
    pub same_error_threshold: Option<i64>,
    pub approval_timeout_min: Option<i64>,
    pub control_agent_slug: Option<String>,
    pub control_prompt_template: Option<String>,
    pub mcp_config_json: Option<String>,
}

// ── Loop ──────────────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct LoopDataDto {
    pub id: i64,
    pub slug: String,
    pub name: String,
    pub description: Option<String>,
    pub schedule: Option<String>,
    pub is_enabled: bool,
    pub status: Option<String>,
    pub agent_slug: Option<String>,
    pub permission_mode: Option<String>,
    pub prompt_template: Option<String>,
    /// Opaque JSON — per-agent config overrides.
    pub config_overrides_json: Option<String>,
    /// Opaque JSON — prompt template variable bindings.
    pub prompt_variables_json: Option<String>,
    pub execution_mode: Option<String>,
    /// Opaque JSON — nested autopilot controller config.
    pub autopilot_config_json: Option<String>,
    pub sandbox_strategy: Option<String>,
    pub session_persistence: Option<bool>,
    pub concurrency_policy: Option<String>,
    pub max_concurrent_runs: Option<i32>,
    pub max_retained_runs: Option<i32>,
    pub timeout_minutes: Option<i32>,
    pub idle_timeout_sec: Option<i32>,
    pub total_runs: Option<i64>,
    pub successful_runs: Option<i64>,
    pub failed_runs: Option<i64>,
    pub active_run_count: Option<i64>,
    pub last_run_at: Option<String>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct LoopListResponseDto {
    pub loops: Vec<LoopDataDto>,
    pub total: Option<i64>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct LoopRunDataDto {
    pub id: i64,
    pub loop_slug: String,
    pub run_number: Option<i64>,
    pub status: LoopRunStatusDto,
    pub pod_key: Option<String>,
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
    pub error_message: Option<String>,
    pub created_at: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct LoopRunListResponseDto {
    pub runs: Vec<LoopRunDataDto>,
    pub total: Option<i64>,
    pub limit: Option<i64>,
    pub offset: Option<i64>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct CreateLoopRequestDto {
    pub name: String,
    pub slug: Option<String>,
    pub description: Option<String>,
    pub agent_slug: Option<String>,
    pub custom_agent_slug: Option<String>,
    pub permission_mode: Option<String>,
    pub prompt_template: Option<String>,
    pub prompt_variables_json: Option<String>,
    pub repository_id: Option<i64>,
    pub runner_id: Option<i64>,
    pub branch_name: Option<String>,
    pub ticket_id: Option<String>,
    pub credential_profile_id: Option<i64>,
    pub config_overrides_json: Option<String>,
    pub execution_mode: Option<String>,
    pub cron_expression: Option<String>,
    pub autopilot_config_json: Option<String>,
    pub callback_url: Option<String>,
    pub sandbox_strategy: Option<String>,
    pub session_persistence: Option<String>,
    pub concurrency_policy: Option<String>,
    pub max_concurrent_runs: Option<i64>,
    pub max_retained_runs: Option<i64>,
    pub timeout_minutes: Option<i64>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct UpdateLoopRequestDto {
    pub name: Option<String>,
    pub description: Option<String>,
    pub agent_slug: Option<String>,
    pub prompt_template: Option<String>,
    pub prompt_variables_json: Option<String>,
    pub repository_id: Option<i64>,
    pub runner_id: Option<i64>,
    pub branch_name: Option<String>,
    pub cron_expression: Option<String>,
    pub autopilot_config_json: Option<String>,
    pub sandbox_strategy: Option<String>,
    pub session_persistence: Option<String>,
    pub concurrency_policy: Option<String>,
    pub max_concurrent_runs: Option<i64>,
    pub max_retained_runs: Option<i64>,
    pub timeout_minutes: Option<i64>,
}
