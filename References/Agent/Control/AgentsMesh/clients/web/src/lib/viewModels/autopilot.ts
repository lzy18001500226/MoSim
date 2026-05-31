/**
 * Autopilot ViewModels — UI-side projections of `proto.autopilot.v1.*`.
 *
 * Snake_case + `number` ids stay for the existing autopilot store/selector
 * paths. Wire-layer adapters translate to/from `proto.AutopilotController`.
 * New components should consume the proto types directly.
 */
export type AutopilotPhase =
  | "initializing"
  | "running"
  | "paused"
  | "user_takeover"
  | "waiting_approval"
  | "completed"
  | "failed"
  | "stopped"
  | "max_iterations";

export type CircuitBreakerState = "closed" | "half_open" | "open";

export interface AutopilotControllerData {
  id: number;
  autopilot_controller_key: string;
  pod_key: string;
  phase: AutopilotPhase;
  current_iteration: number;
  max_iterations: number;
  circuit_breaker: {
    state: CircuitBreakerState;
    reason?: string;
  };
  user_takeover: boolean;
  prompt?: string;
  started_at?: string;
  last_iteration_at?: string;
  created_at: string;
}

export interface AutopilotIterationData {
  id: number;
  autopilot_controller_id: number;
  iteration: number;
  phase: string;
  summary?: string;
  files_changed?: string[];
  duration_ms?: number;
  created_at: string;
}

export interface CreateAutopilotControllerRequest {
  pod_key: string;
  prompt?: string;
  max_iterations?: number;
  iteration_timeout_sec?: number;
  no_progress_threshold?: number;
  same_error_threshold?: number;
  approval_timeout_min?: number;
  control_agent_slug?: string;
  control_prompt_template?: string;
  mcp_config_json?: string;
}

export interface ApproveRequest {
  continue_execution?: boolean;
  additional_iterations?: number;
}
