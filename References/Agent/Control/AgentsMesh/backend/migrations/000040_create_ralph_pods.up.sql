-- Create ralph_pods table for event-driven automation controller
CREATE TABLE IF NOT EXISTS ralph_pods (
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Key identifiers
    ralph_pod_key VARCHAR(100) NOT NULL,
    worker_pod_key VARCHAR(100) NOT NULL,
    worker_pod_id BIGINT NOT NULL REFERENCES pods(id) ON DELETE CASCADE,
    runner_id BIGINT NOT NULL REFERENCES runners(id) ON DELETE CASCADE,

    -- Task
    initial_prompt TEXT,

    -- Status
    phase VARCHAR(50) NOT NULL DEFAULT 'initializing',
    current_iteration INTEGER NOT NULL DEFAULT 0,
    max_iterations INTEGER NOT NULL DEFAULT 10,
    iteration_timeout_sec INTEGER NOT NULL DEFAULT 300,

    -- Circuit breaker
    circuit_breaker_state VARCHAR(50) NOT NULL DEFAULT 'closed',
    circuit_breaker_reason VARCHAR(500),
    no_progress_threshold INTEGER NOT NULL DEFAULT 3,
    same_error_threshold INTEGER NOT NULL DEFAULT 5,
    approval_timeout_min INTEGER NOT NULL DEFAULT 30,

    -- Control agent configuration
    control_agent_type VARCHAR(50),
    control_prompt_template TEXT,
    mcp_config_json TEXT,

    -- User takeover
    user_takeover BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    started_at TIMESTAMPTZ,
    last_iteration_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    approval_request_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for ralph_pods
CREATE UNIQUE INDEX IF NOT EXISTS idx_ralph_pods_ralph_pod_key ON ralph_pods(ralph_pod_key);
CREATE INDEX IF NOT EXISTS idx_ralph_pods_worker_pod_key ON ralph_pods(worker_pod_key);
CREATE INDEX IF NOT EXISTS idx_ralph_pods_worker_pod_id ON ralph_pods(worker_pod_id);
CREATE INDEX IF NOT EXISTS idx_ralph_pods_runner_id ON ralph_pods(runner_id);
CREATE INDEX IF NOT EXISTS idx_ralph_pods_organization_id ON ralph_pods(organization_id);
CREATE INDEX IF NOT EXISTS idx_ralph_pods_phase ON ralph_pods(phase);

-- Create ralph_iterations table for iteration history
CREATE TABLE IF NOT EXISTS ralph_iterations (
    id BIGSERIAL PRIMARY KEY,
    ralph_pod_id BIGINT NOT NULL REFERENCES ralph_pods(id) ON DELETE CASCADE,
    iteration INTEGER NOT NULL,

    -- Phase progression
    phase VARCHAR(50) NOT NULL,

    -- Decision details
    summary TEXT,
    files_changed TEXT, -- JSON array of file paths
    error_message TEXT,

    -- Timing
    duration_ms BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for ralph_iterations
CREATE INDEX IF NOT EXISTS idx_ralph_iterations_ralph_pod_id ON ralph_iterations(ralph_pod_id);
CREATE INDEX IF NOT EXISTS idx_ralph_iterations_iteration ON ralph_iterations(ralph_pod_id, iteration);

-- Add comment
COMMENT ON TABLE ralph_pods IS 'Event-driven automation controller for WorkerPod orchestration';
COMMENT ON TABLE ralph_iterations IS 'Iteration history for RalphPod execution tracking';
