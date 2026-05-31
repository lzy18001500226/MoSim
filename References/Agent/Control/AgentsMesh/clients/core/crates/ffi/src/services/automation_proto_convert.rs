use agentsmesh_types::proto_autopilot_v1 as ap_proto;
use agentsmesh_types::proto_loop_v1 as lp_proto;

use crate::dto::{
    AutopilotControllerDto, AutopilotIterationDto, AutopilotIterationListResponseDto,
    AutopilotListResponseDto, AutopilotStatusDto, LoopDataDto, LoopListResponseDto,
    LoopRunDataDto, LoopRunListResponseDto, LoopRunStatusDto,
};

fn empty_to_none(s: String) -> Option<String> {
    if s.is_empty() {
        None
    } else {
        Some(s)
    }
}

fn json_to_opt(s: String) -> Option<String> {
    if s.is_empty() || s == "{}" {
        None
    } else {
        Some(s)
    }
}

fn parse_autopilot_phase(phase: &str) -> AutopilotStatusDto {
    match phase {
        "idle" => AutopilotStatusDto::Idle,
        "running" => AutopilotStatusDto::Running,
        "paused" => AutopilotStatusDto::Paused,
        "waiting_approval" => AutopilotStatusDto::WaitingApproval,
        "completed" => AutopilotStatusDto::Completed,
        "failed" => AutopilotStatusDto::Failed,
        "terminated" => AutopilotStatusDto::Terminated,
        _ => AutopilotStatusDto::Unknown,
    }
}

fn parse_loop_run_status(status: &str) -> LoopRunStatusDto {
    match status {
        "pending" => LoopRunStatusDto::Pending,
        "running" => LoopRunStatusDto::Running,
        "completed" => LoopRunStatusDto::Completed,
        "failed" => LoopRunStatusDto::Failed,
        "cancelled" => LoopRunStatusDto::Cancelled,
        _ => LoopRunStatusDto::Unknown,
    }
}

impl From<ap_proto::AutopilotController> for AutopilotControllerDto {
    fn from(c: ap_proto::AutopilotController) -> Self {
        let (cb_state, cb_reason) = match c.circuit_breaker {
            Some(cb) => (empty_to_none(cb.state), empty_to_none(cb.reason)),
            None => (None, None),
        };
        Self {
            autopilot_controller_key: c.autopilot_controller_key,
            pod_key: c.pod_key,
            status: Some(parse_autopilot_phase(&c.phase)),
            phase: empty_to_none(c.phase),
            prompt: empty_to_none(c.prompt),
            max_iterations: Some(c.max_iterations as i64),
            iteration_timeout_sec: None,
            no_progress_threshold: None,
            same_error_threshold: None,
            approval_timeout_min: None,
            current_iteration: Some(c.current_iteration as i64),
            control_agent_slug: None,
            circuit_breaker_state: cb_state,
            circuit_breaker_reason: cb_reason,
            created_at: empty_to_none(c.created_at),
            updated_at: None,
        }
    }
}

pub(crate) fn autopilot_list_from_proto(
    resp: ap_proto::ListAutopilotControllersResponse,
) -> AutopilotListResponseDto {
    AutopilotListResponseDto {
        controllers: resp
            .items
            .into_iter()
            .map(AutopilotControllerDto::from)
            .collect(),
    }
}

impl From<ap_proto::AutopilotIteration> for AutopilotIterationDto {
    fn from(i: ap_proto::AutopilotIteration) -> Self {
        Self {
            id: i.id,
            controller_key: i.controller_key,
            iteration_number: Some(i.iteration_number),
            status: empty_to_none(i.status),
            result: empty_to_none(i.result),
            started_at: i.started_at,
            completed_at: i.completed_at,
        }
    }
}

pub(crate) fn autopilot_iterations_from_proto(
    resp: ap_proto::GetIterationsResponse,
) -> AutopilotIterationListResponseDto {
    AutopilotIterationListResponseDto {
        iterations: resp.items.into_iter().map(AutopilotIterationDto::from).collect(),
    }
}

impl From<lp_proto::Loop> for LoopDataDto {
    fn from(l: lp_proto::Loop) -> Self {
        Self {
            id: l.id,
            slug: l.slug,
            name: l.name,
            description: l.description,
            // Legacy DTO field; proto exposes the cron expression directly.
            schedule: l.cron_expression,
            is_enabled: l.status == "enabled",
            status: Some(l.status),
            agent_slug: Some(l.agent_slug),
            permission_mode: Some(l.permission_mode),
            prompt_template: Some(l.prompt_template),
            config_overrides_json: json_to_opt(l.config_overrides_json),
            prompt_variables_json: json_to_opt(l.prompt_variables_json),
            execution_mode: empty_to_none(l.execution_mode),
            autopilot_config_json: json_to_opt(l.autopilot_config_json),
            sandbox_strategy: empty_to_none(l.sandbox_strategy),
            session_persistence: Some(l.session_persistence),
            concurrency_policy: empty_to_none(l.concurrency_policy),
            max_concurrent_runs: Some(l.max_concurrent_runs),
            max_retained_runs: Some(l.max_retained_runs),
            timeout_minutes: Some(l.timeout_minutes),
            idle_timeout_sec: Some(l.idle_timeout_sec),
            total_runs: Some(l.total_runs),
            successful_runs: Some(l.successful_runs),
            failed_runs: Some(l.failed_runs),
            active_run_count: Some(l.active_run_count),
            last_run_at: l.last_run_at,
            created_at: empty_to_none(l.created_at),
            updated_at: empty_to_none(l.updated_at),
        }
    }
}

pub(crate) fn loop_list_from_proto(resp: lp_proto::ListLoopsResponse) -> LoopListResponseDto {
    LoopListResponseDto {
        loops: resp.items.into_iter().map(LoopDataDto::from).collect(),
        total: Some(resp.total),
    }
}

pub(crate) fn loop_run_from_proto(r: lp_proto::LoopRun, loop_slug: String) -> LoopRunDataDto {
    LoopRunDataDto {
        id: r.id,
        loop_slug,
        run_number: Some(r.run_number),
        status: parse_loop_run_status(&r.status),
        pod_key: r.pod_key,
        started_at: r.started_at,
        completed_at: r.completed_at,
        error_message: r.error_message,
        created_at: empty_to_none(r.created_at),
    }
}

pub(crate) fn loop_run_list_from_proto(
    resp: lp_proto::ListRunsResponse,
    loop_slug: String,
) -> LoopRunListResponseDto {
    LoopRunListResponseDto {
        runs: resp
            .items
            .into_iter()
            .map(|r| loop_run_from_proto(r, loop_slug.clone()))
            .collect(),
        total: Some(resp.total),
        limit: Some(resp.limit as i64),
        offset: Some(resp.offset as i64),
    }
}
