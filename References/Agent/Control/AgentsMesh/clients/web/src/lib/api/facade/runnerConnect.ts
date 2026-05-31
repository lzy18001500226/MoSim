// Facade re-export of the runner Connect-RPC adapter. Business code imports
// from here (or from the `@/lib/api` barrel) so the wire-shape layer stays
// internal to the facade boundary. Tests mock this path.

export {
  listRunners,
  listAvailableRunners,
  getRunner,
  updateRunner,
  deleteRunner,
  upgradeRunner,
  requestLogUpload,
  listRunnerLogs,
  querySandboxes,
  createRunnerToken,
  listRunnerTokens,
  deleteRunnerToken,
  type UpdateRunnerInput,
} from "../connect/runnerConnect";
