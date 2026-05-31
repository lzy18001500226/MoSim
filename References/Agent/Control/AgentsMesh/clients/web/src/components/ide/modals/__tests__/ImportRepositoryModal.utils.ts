import { vi } from "vitest";
import type { RepositoryProviderData, ProviderRepositoryData } from "@/lib/viewModels/repositoryProvider";
import type { RepositoryData } from "@/lib/viewModels/repository";
import { getUserCredentialService, getRepositoryService } from "@/lib/wasm-core";

export const mockProvider: RepositoryProviderData = {
  id: 1,
  name: "My GitHub",
  provider_type: "github",
  base_url: "https://github.com",
  has_client_id: false,
  has_bot_token: false,
  has_identity: true,
  is_default: true,
  is_active: true,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

export const mockGitLabProvider: RepositoryProviderData = {
  id: 2,
  name: "My GitLab",
  provider_type: "gitlab",
  base_url: "https://gitlab.com",
  has_client_id: false,
  has_bot_token: true,
  has_identity: false,
  is_default: false,
  is_active: true,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

export const mockRepository: ProviderRepositoryData = {
  id: "repo-1",
  name: "my-project",
  slug: "org/my-project",
  description: "A test project",
  default_branch: "main",
  visibility: "private",
  http_clone_url: "https://github.com/org/my-project.git",
  ssh_clone_url: "git@github.com:org/my-project.git",
  web_url: "https://github.com/org/my-project",
};

export const mockCreatedRepository: RepositoryData = {
  id: 1,
  organization_id: 1,
  name: "my-project",
  slug: "org/my-project",
  provider_type: "github",
  provider_base_url: "https://github.com",
  http_clone_url: "https://github.com/org/my-project.git",
  external_id: "repo-1",
  default_branch: "main",
  visibility: "organization",
  is_active: true,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

export const createMockOnClose = () => vi.fn<() => void>();
export const createMockOnImported = () => vi.fn<() => void>();

// useImportWizard calls getUserCredentialService() / getRepositoryService()
// directly on each render — the global wasm-core mock creates a fresh
// service object every call. Lock the return value to a stable singleton
// so per-test method overrides survive across invocations.
export const stableCredSvc = {
  list_repo_providers: vi.fn(),
  list_provider_repositories: vi.fn(),
};

export const stableRepoSvc = {
  create: vi.fn(),
};

function applyMocks() {
  vi.mocked(getUserCredentialService).mockReturnValue(stableCredSvc as never);
  vi.mocked(getRepositoryService).mockReturnValue(stableRepoSvc as never);
}

export function setupProviderMocks(providers: RepositoryProviderData[] = [mockProvider, mockGitLabProvider]) {
  applyMocks();
  stableCredSvc.list_repo_providers.mockResolvedValue(
    JSON.stringify({ providers })
  );
  stableCredSvc.list_provider_repositories.mockResolvedValue(
    JSON.stringify({ repositories: [mockRepository] })
  );
}

export function mockRepositoryCreate(response?: RepositoryData) {
  applyMocks();
  stableRepoSvc.create.mockResolvedValue(
    JSON.stringify(response ?? mockCreatedRepository)
  );
  return stableRepoSvc;
}

export const createRepositoryResponse = (r: RepositoryData): RepositoryData => r;
