import { vi } from "vitest";
import type { RepositoryData, WebhookStatus, WebhookSecretResponse, WebhookResult } from "@/lib/api";

vi.mock("@/lib/api/facade/repositoryConnect", () => ({
  getRepositoryWebhookStatus: vi.fn(),
  getRepositoryWebhookSecret: vi.fn(),
  registerRepositoryWebhook: vi.fn(),
  deleteRepositoryWebhook: vi.fn(),
  markRepositoryWebhookConfigured: vi.fn(),
}));

vi.mock("@/stores/auth", () => ({
  useCurrentOrg: () => ({ id: 1, name: "TestOrg", slug: "test-org" }),
  readCurrentOrg: () => ({ id: 1, name: "TestOrg", slug: "test-org" }),
}));

import {
  getRepositoryWebhookStatus,
  getRepositoryWebhookSecret,
  registerRepositoryWebhook,
  deleteRepositoryWebhook,
  markRepositoryWebhookConfigured,
} from "@/lib/api/facade/repositoryConnect";

// Each helper is the vi.fn() bound to the connect adapter symbol the
// component-under-test imports. Tests can .mockResolvedValue(WebhookStatus)
// directly — no JSON wrapping, no double parse — matching the real adapter
// surface (binary-in / parsed-snake_case-out).
export const mockGetWebhookStatus = vi.mocked(getRepositoryWebhookStatus);
export const mockGetWebhookSecret = vi.mocked(getRepositoryWebhookSecret);
export const mockRegisterWebhook = vi.mocked(registerRepositoryWebhook);
export const mockDeleteWebhook = vi.mocked(deleteRepositoryWebhook);
export const mockMarkWebhookConfigured = vi.mocked(markRepositoryWebhookConfigured);

export const mockClipboardWriteText = vi.fn();
Object.assign(navigator, {
  clipboard: {
    writeText: mockClipboardWriteText,
  },
});

export const mockRepository: RepositoryData = {
  id: 1,
  organization_id: 100,
  provider_type: "gitlab",
  provider_base_url: "https://gitlab.com",
  http_clone_url: "https://gitlab.com/org/repo.git",
  external_id: "123",
  name: "test-repo",
  slug: "org/test-repo",
  default_branch: "main",
  visibility: "organization",
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-01T00:00:00Z",
};

export const registeredStatus: WebhookStatus = {
  registered: true,
  webhook_id: "wh_123",
  webhook_url: "https://example.com/webhooks/org/gitlab/1",
  events: ["merge_request", "pipeline"],
  is_active: true,
  needs_manual_setup: false,
  registered_at: "2025-01-01T00:00:00Z",
};

export const manualSetupStatus: WebhookStatus = {
  registered: true,
  webhook_url: "https://example.com/webhooks/org/gitlab/1",
  events: ["merge_request", "pipeline"],
  is_active: false,
  needs_manual_setup: true,
  last_error: "OAuth token not available",
};

export const notRegisteredStatus: WebhookStatus = {
  registered: false,
  is_active: false,
  needs_manual_setup: false,
};

export const secretResponse: WebhookSecretResponse = {
  webhook_url: "https://example.com/webhooks/org/gitlab/1",
  webhook_secret: "super_secret_value",
  events: ["merge_request", "pipeline"],
};

export const registeredWebhookResult: WebhookResult = {
  repo_id: 1,
  registered: true,
  webhook_id: "wh_new",
  needs_manual_setup: false,
};

export const manualSetupWebhookResult: WebhookResult = {
  repo_id: 1,
  registered: false,
  needs_manual_setup: true,
  manual_webhook_url: "https://example.com/webhooks/org/gitlab/1",
  manual_webhook_secret: "new_secret",
  error: "OAuth token not available",
};

export function setupWebhookMocks() {
  mockGetWebhookStatus.mockReset();
  mockGetWebhookSecret.mockReset();
  mockRegisterWebhook.mockReset();
  mockDeleteWebhook.mockReset();
  mockMarkWebhookConfigured.mockReset();
}

export function resetAllMocks() {
  setupWebhookMocks();
  mockClipboardWriteText.mockReset();
  mockClipboardWriteText.mockResolvedValue(undefined);
}
