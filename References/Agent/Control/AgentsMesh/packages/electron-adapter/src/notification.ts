import { invoke } from "./invoke";
import type { INotificationService } from "@agentsmesh/service-interface";

export class ElectronNotificationService implements INotificationService {
  async get_preferences(): Promise<string> {
    return invoke<string>("notificationGetPreferences");
  }

  async set_preference(json: string): Promise<string> {
    return invoke<string>("notificationSetPreference", json);
  }
}
