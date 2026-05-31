// Facade re-export of the repository Connect-RPC adapter. Business code
// imports from here (or from the `@/lib/api` barrel) so the wire-shape
// layer stays internal to the facade boundary. Tests mock this path.

export {
  listRepositories,
  getRepository,
  createRepository,
  updateRepository,
  deleteRepository,
  listRepositoryBranches,
  syncRepositoryBranches,
  listRepositoryMergeRequests,
  registerRepositoryWebhook,
  deleteRepositoryWebhook,
  getRepositoryWebhookStatus,
  getRepositoryWebhookSecret,
  markRepositoryWebhookConfigured,
  type CreateRepositoryInput,
  type UpdateRepositoryInput,
} from "../connect/repositoryConnect";
