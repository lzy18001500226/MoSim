import { invoke } from "./invoke";
import type { ITokenUsageService } from "@agentsmesh/service-interface";

export class ElectronTokenUsageService implements ITokenUsageService {
  async get_dashboard(
    startTime?: string | null,
    endTime?: string | null,
    agentSlug?: string | null,
    userId?: bigint | null,
    model?: string | null,
    granularity?: string | null,
  ): Promise<string> {
    return invoke<string>("tokenUsageGetDashboard", startTime, endTime, agentSlug, userId ? Number(userId) : null, model, granularity);
  }
}
