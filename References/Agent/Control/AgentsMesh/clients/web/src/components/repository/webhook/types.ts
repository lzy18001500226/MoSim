import type { WebhookStatus, WebhookSecretResponse } from "@/lib/viewModels/repository";

export type WebhookState = "loading" | "registered" | "needs_manual_setup" | "not_registered" | "error";

export interface WebhookSettingsState {
  state: WebhookState;
  status: WebhookStatus | null;
  secretData: WebhookSecretResponse | null;
  error: string | null;
  loading: boolean;
}

export interface WebhookSettingsActions {
  handleRegister: () => Promise<void>;
  handleDelete: () => Promise<void>;
  handleMarkConfigured: () => Promise<void>;
  loadStatus: () => Promise<void>;
}
