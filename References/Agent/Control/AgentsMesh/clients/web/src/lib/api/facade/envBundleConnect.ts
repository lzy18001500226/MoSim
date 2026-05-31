// Facade re-export of the env-bundle Connect-RPC adapter. Business code
// imports from here (or from the `@/lib/api` barrel) so the wire-shape
// layer stays internal to the facade boundary. Tests mock this path.

export {
  listEnvBundles,
  getEnvBundle,
  createEnvBundle,
  updateEnvBundle,
  deleteEnvBundle,
  setPrimaryEnvBundle,
  type EnvBundle,
  type UpdateEnvBundleInput,
} from "../connect/envBundleConnect";
