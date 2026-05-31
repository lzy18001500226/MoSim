import { invoke } from "./invoke";
import type { IApiKeyService } from "@agentsmesh/service-interface";

export class ElectronApiKeyService implements IApiKeyService {
  async list(): Promise<string> {
    return invoke<string>("apikeyList");
  }

  async get(id: bigint): Promise<string> {
    return invoke<string>("apikeyGet", Number(id));
  }

  async create(json: string): Promise<string> {
    return invoke<string>("apikeyCreate", json);
  }

  async update(id: bigint, json: string): Promise<string> {
    return invoke<string>("apikeyUpdate", Number(id), json);
  }

  async delete(id: bigint): Promise<void> {
    await invoke<void>("apikeyDelete", Number(id));
  }

  async revoke(id: bigint): Promise<void> {
    await invoke<void>("apikeyRevoke", Number(id));
  }
}
