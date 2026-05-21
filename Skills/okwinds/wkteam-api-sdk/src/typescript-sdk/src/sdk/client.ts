import { type WkteamApi, createApi } from "../generated/api.js";
import type { WkteamClientConfig } from "./config.js";
import { WkteamCoreClient } from "./core-client.js";

/**
 * 对外 Client：在 Core Client 基础上挂载全量 API wrapper（由离线文档 codegen）。
 */
export class WkteamClient extends WkteamCoreClient {
  public readonly api: WkteamApi;

  constructor(config: WkteamClientConfig) {
    super(config);
    this.api = createApi(this);
  }
}

export function createClient(config: WkteamClientConfig): WkteamClient {
  return new WkteamClient(config);
}
