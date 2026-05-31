import { invoke } from "./invoke";
import type { IAgentService } from "@agentsmesh/service-interface";

export class ElectronAgentService implements IAgentService {
  // Renderer hooks (AgentConfigPage etc.) still call .list_agents() and
  // JSON.parse the result. We forward through a legacy IPC alias in
  // main/index.ts that calls proto.agent.v1.AgentService/ListAgents and
  // remaps the proto camelCase envelope to the snake_case shape callers
  // expect (builtin_agents / custom_agents).
  async list_agents(): Promise<string> {
    return invoke<string>("agentListAgents");
  }

  async list_providers(): Promise<string> {
    return invoke<string>("agentListProviders");
  }

  async create_provider(json: string): Promise<string> {
    return invoke<string>("agentCreateProvider", json);
  }

  async update_provider(id: bigint, json: string): Promise<string> {
    return invoke<string>("agentUpdateProvider", Number(id), json);
  }

  async delete_provider(id: bigint): Promise<void> {
    await invoke<void>("agentDeleteProvider", Number(id));
  }

  async set_default_provider(id: bigint): Promise<void> {
    await invoke<void>("agentSetDefaultProvider", Number(id));
  }

  async get_agentpod_settings(): Promise<string> {
    return invoke<string>("agentGetAgentpodSettings");
  }

  async update_agentpod_settings(json: string): Promise<string> {
    return invoke<string>("agentUpdateAgentpodSettings", json);
  }
}
