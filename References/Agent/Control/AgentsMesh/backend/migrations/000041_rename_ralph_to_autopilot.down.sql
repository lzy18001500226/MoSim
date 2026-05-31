-- Rename autopilot_iterations table back to ralph_iterations
ALTER TABLE autopilot_iterations RENAME TO ralph_iterations;

-- Rename column in ralph_iterations
ALTER TABLE ralph_iterations RENAME COLUMN autopilot_id TO ralph_pod_id;

-- Rename autopilot_controllers table back to ralph_pods
ALTER TABLE autopilot_controllers RENAME TO ralph_pods;

-- Rename columns in ralph_pods
ALTER TABLE ralph_pods RENAME COLUMN autopilot_controller_key TO ralph_pod_key;
ALTER TABLE ralph_pods RENAME COLUMN pod_id TO worker_pod_id;
ALTER TABLE ralph_pods RENAME COLUMN pod_key TO worker_pod_key;

-- Rename indexes for ralph_pods
ALTER INDEX IF EXISTS idx_autopilot_controllers_autopilot_controller_key RENAME TO idx_ralph_pods_ralph_pod_key;
ALTER INDEX IF EXISTS idx_autopilot_controllers_pod_key RENAME TO idx_ralph_pods_worker_pod_key;
ALTER INDEX IF EXISTS idx_autopilot_controllers_pod_id RENAME TO idx_ralph_pods_worker_pod_id;
ALTER INDEX IF EXISTS idx_autopilot_controllers_runner_id RENAME TO idx_ralph_pods_runner_id;
ALTER INDEX IF EXISTS idx_autopilot_controllers_organization_id RENAME TO idx_ralph_pods_organization_id;
ALTER INDEX IF EXISTS idx_autopilot_controllers_phase RENAME TO idx_ralph_pods_phase;

-- Rename indexes for ralph_iterations
ALTER INDEX IF EXISTS idx_autopilot_iterations_autopilot_id RENAME TO idx_ralph_iterations_ralph_pod_id;
ALTER INDEX IF EXISTS idx_autopilot_iterations_iteration RENAME TO idx_ralph_iterations_iteration;

-- Restore comments
COMMENT ON TABLE ralph_pods IS 'Event-driven automation controller for WorkerPod orchestration';
COMMENT ON TABLE ralph_iterations IS 'Iteration history for RalphPod execution tracking';
