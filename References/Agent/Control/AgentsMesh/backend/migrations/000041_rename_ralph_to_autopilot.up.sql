-- Rename ralph_pods table to autopilot_controllers
ALTER TABLE ralph_pods RENAME TO autopilot_controllers;

-- Rename columns in autopilot_controllers
ALTER TABLE autopilot_controllers RENAME COLUMN ralph_pod_key TO autopilot_controller_key;
ALTER TABLE autopilot_controllers RENAME COLUMN worker_pod_id TO pod_id;
ALTER TABLE autopilot_controllers RENAME COLUMN worker_pod_key TO pod_key;

-- Rename ralph_iterations table to autopilot_iterations
ALTER TABLE ralph_iterations RENAME TO autopilot_iterations;

-- Rename column in autopilot_iterations
ALTER TABLE autopilot_iterations RENAME COLUMN ralph_pod_id TO autopilot_id;

-- Rename indexes for autopilot_controllers
ALTER INDEX IF EXISTS idx_ralph_pods_ralph_pod_key RENAME TO idx_autopilot_controllers_autopilot_controller_key;
ALTER INDEX IF EXISTS idx_ralph_pods_worker_pod_key RENAME TO idx_autopilot_controllers_pod_key;
ALTER INDEX IF EXISTS idx_ralph_pods_worker_pod_id RENAME TO idx_autopilot_controllers_pod_id;
ALTER INDEX IF EXISTS idx_ralph_pods_runner_id RENAME TO idx_autopilot_controllers_runner_id;
ALTER INDEX IF EXISTS idx_ralph_pods_organization_id RENAME TO idx_autopilot_controllers_organization_id;
ALTER INDEX IF EXISTS idx_ralph_pods_phase RENAME TO idx_autopilot_controllers_phase;

-- Rename indexes for autopilot_iterations
ALTER INDEX IF EXISTS idx_ralph_iterations_ralph_pod_id RENAME TO idx_autopilot_iterations_autopilot_id;
ALTER INDEX IF EXISTS idx_ralph_iterations_iteration RENAME TO idx_autopilot_iterations_iteration;

-- Update comments
COMMENT ON TABLE autopilot_controllers IS 'Autopilot controllers for supervised Pod automation';
COMMENT ON TABLE autopilot_iterations IS 'Iteration history for Autopilot execution tracking';
