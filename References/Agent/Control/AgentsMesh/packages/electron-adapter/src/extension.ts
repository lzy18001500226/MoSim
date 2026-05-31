import { invoke } from "./invoke";
import type { IExtensionService } from "@agentsmesh/service-interface";

export class ElectronExtensionService implements IExtensionService {
  async list_repo_skills(repoId: bigint, scope?: string | null): Promise<string> {
    return invoke<string>("extensionListRepoSkills", Number(repoId), scope);
  }

  async list_repo_mcp_servers(repoId: bigint, scope?: string | null): Promise<string> {
    return invoke<string>("extensionListRepoMcpServers", Number(repoId), scope);
  }

  async list_market_skills(query?: string | null, category?: string | null): Promise<string> {
    return invoke<string>("extensionListMarketSkills", query, category);
  }

  async list_market_mcp_servers(query?: string | null, limit?: number | null, offset?: number | null): Promise<string> {
    return invoke<string>("extensionListMarketMcpServers", query, limit, offset);
  }

  async install_skill_from_market(repoId: bigint, json: string): Promise<string> {
    return invoke<string>("extensionInstallSkillFromMarket", Number(repoId), json);
  }

  async install_skill_from_github(repoId: bigint, json: string): Promise<string> {
    return invoke<string>("extensionInstallSkillFromGithub", Number(repoId), json);
  }

  async presignSkillUploadConnect(request: Uint8Array): Promise<Uint8Array> {
    const result = await invoke<number[]>("extensionPresignSkillUploadConnect", Array.from(request));
    return new Uint8Array(result);
  }

  async installSkillFromUploadedFileConnect(request: Uint8Array): Promise<Uint8Array> {
    const result = await invoke<number[]>("extensionInstallSkillFromUploadedFileConnect", Array.from(request));
    return new Uint8Array(result);
  }

  async install_mcp_from_market(repoId: bigint, json: string): Promise<string> {
    return invoke<string>("extensionInstallMcpFromMarket", Number(repoId), json);
  }

  async install_custom_mcp_server(repoId: bigint, json: string): Promise<string> {
    return invoke<string>("extensionInstallCustomMcpServer", Number(repoId), json);
  }

  async uninstall_skill(repoId: bigint, installId: bigint): Promise<void> {
    await invoke<void>("extensionUninstallSkill", Number(repoId), Number(installId));
  }

  async uninstall_mcp_server(repoId: bigint, installId: bigint): Promise<void> {
    await invoke<void>("extensionUninstallMcpServer", Number(repoId), Number(installId));
  }

  async update_skill(repoId: bigint, installId: bigint, json: string): Promise<string> {
    return invoke<string>("extensionUpdateSkill", Number(repoId), Number(installId), json);
  }

  async update_mcp_server(repoId: bigint, installId: bigint, json: string): Promise<string> {
    return invoke<string>("extensionUpdateMcpServer", Number(repoId), Number(installId), json);
  }

  async list_skill_registries(): Promise<string> {
    return invoke<string>("extensionListSkillRegistries");
  }

  async list_skill_registry_overrides(): Promise<string> {
    return invoke<string>("extensionListSkillRegistryOverrides");
  }

  async create_skill_registry(json: string): Promise<string> {
    return invoke<string>("extensionCreateSkillRegistry", json);
  }

  async sync_skill_registry(id: bigint): Promise<void> {
    await invoke<void>("extensionSyncSkillRegistry", Number(id));
  }

  async toggle_skill_registry(id: bigint, json: string): Promise<string> {
    return invoke<string>("extensionToggleSkillRegistry", Number(id), json);
  }

  async delete_skill_registry(id: bigint): Promise<void> {
    await invoke<void>("extensionDeleteSkillRegistry", Number(id));
  }
}
