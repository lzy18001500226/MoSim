import { invoke } from "./invoke";
import type { IUserCredentialService } from "@agentsmesh/service-interface";

export class ElectronUserCredentialService implements IUserCredentialService {
  async list_git_credentials(): Promise<string> {
    return invoke<string>("userCredentialListGitCredentials");
  }

  async get_git_credential(id: bigint): Promise<string> {
    return invoke<string>("userCredentialGetGitCredential", Number(id));
  }

  async create_git_credential(json: string): Promise<string> {
    return invoke<string>("userCredentialCreateGitCredential", json);
  }

  async update_git_credential(id: bigint, json: string): Promise<string> {
    return invoke<string>("userCredentialUpdateGitCredential", Number(id), json);
  }

  async delete_git_credential(id: bigint): Promise<void> {
    await invoke<void>("userCredentialDeleteGitCredential", Number(id));
  }

  async get_default_git_credential(): Promise<string> {
    return invoke<string>("userCredentialGetDefaultGitCredential");
  }

  async set_default_git_credential(json: string): Promise<void> {
    await invoke<void>("userCredentialSetDefaultGitCredential", json);
  }

  async clear_default_git_credential(): Promise<void> {
    await invoke<void>("userCredentialClearDefaultGitCredential");
  }

  async list_agent_credentials(): Promise<string> {
    return invoke<string>("userCredentialListAgentCredentials");
  }

  async list_agent_credentials_for_agent(agentSlug: string): Promise<string> {
    return invoke<string>("userCredentialListAgentCredentialsForAgent", agentSlug);
  }

  async get_agent_credential(id: bigint): Promise<string> {
    return invoke<string>("userCredentialGetAgentCredential", Number(id));
  }

  async create_agent_credential(agentSlug: string, json: string): Promise<string> {
    return invoke<string>("userCredentialCreateAgentCredential", agentSlug, json);
  }

  async update_agent_credential(id: bigint, json: string): Promise<string> {
    return invoke<string>("userCredentialUpdateAgentCredential", Number(id), json);
  }

  async delete_agent_credential(id: bigint): Promise<void> {
    await invoke<void>("userCredentialDeleteAgentCredential", Number(id));
  }

  async set_default_agent_credential(id: bigint): Promise<void> {
    await invoke<void>("userCredentialSetDefaultAgentCredential", Number(id));
  }

  async list_repo_providers(): Promise<string> {
    return invoke<string>("userCredentialListRepoProviders");
  }

  async get_repo_provider(id: bigint): Promise<string> {
    return invoke<string>("userCredentialGetRepoProvider", Number(id));
  }

  async create_repo_provider(json: string): Promise<string> {
    return invoke<string>("userCredentialCreateRepoProvider", json);
  }

  async update_repo_provider(id: bigint, json: string): Promise<string> {
    return invoke<string>("userCredentialUpdateRepoProvider", Number(id), json);
  }

  async delete_repo_provider(id: bigint): Promise<void> {
    await invoke<void>("userCredentialDeleteRepoProvider", Number(id));
  }

  async set_default_repo_provider(id: bigint): Promise<void> {
    await invoke<void>("userCredentialSetDefaultRepoProvider", Number(id));
  }

  async test_repo_provider(id: bigint): Promise<void> {
    await invoke<void>("userCredentialTestRepoProvider", Number(id));
  }

  async list_provider_repositories(id: bigint, page?: number | null, perPage?: number | null, search?: string | null): Promise<string> {
    return invoke<string>("userCredentialListProviderRepositories", Number(id), page, perPage, search);
  }
}
