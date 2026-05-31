import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => {
    const translations: Record<string, string> = {
      "title": "Webhook Settings",
      "loading": "Loading...",
      "status.registered": "Registered",
      "status.needsManualSetup": "Needs Manual Setup",
      "status.notRegistered": "Not Registered",
      "reregister": "Re-register",
    };
    return translations[key] || key;
  },
}));

import {
  mockGetWebhookStatus,
  mockGetWebhookSecret,
  mockRegisterWebhook,
} from "./testSetup";

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { WebhookSettings } from "../../webhook";
import { WebhookStatus, WebhookSecretResponse } from "@/lib/api";
import {
  mockRepository,
  registeredStatus,
  manualSetupStatus,
  mockClipboardWriteText,
  resetAllMocks,
} from "./testSetup";

describe("WebhookSettings - Edge Cases", () => {
  const mockOnUpdate = vi.fn();

  beforeEach(() => {
    resetAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("should handle empty events array", async () => {
    const statusWithNoEvents: WebhookStatus = {
      registered: true,
      webhook_id: "wh_123",
      webhook_url: "https://example.com/webhooks/org/gitlab/1",
      events: [],
      is_active: true,
      needs_manual_setup: false,
    };

    mockGetWebhookStatus.mockResolvedValue(statusWithNoEvents);

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Registered")).toBeInTheDocument();
    });
  });

  it("should handle undefined events", async () => {
    const statusWithUndefinedEvents: WebhookStatus = {
      registered: true,
      webhook_id: "wh_123",
      webhook_url: "https://example.com/webhooks/org/gitlab/1",
      is_active: true,
      needs_manual_setup: false,
    };

    mockGetWebhookStatus.mockResolvedValue(statusWithUndefinedEvents);

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Registered")).toBeInTheDocument();
    });
  });

  it("should handle registered but not active status", async () => {
    const inactiveStatus: WebhookStatus = {
      registered: true,
      webhook_id: "wh_123",
      webhook_url: "https://example.com/webhooks/org/gitlab/1",
      events: ["merge_request"],
      is_active: false,
      needs_manual_setup: false,
    };

    mockGetWebhookStatus.mockResolvedValue(inactiveStatus);

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      // Should show not_registered since registered && is_active is required
      expect(screen.getByText("Not Registered")).toBeInTheDocument();
    });
  });

  it("should handle clipboard write failure gracefully", async () => {
    mockClipboardWriteText.mockRejectedValue(new Error("Clipboard access denied"));

    const secretResponse: WebhookSecretResponse = {
      webhook_url: "https://example.com/webhooks/org/gitlab/1",
      webhook_secret: "secret",
      events: ["merge_request", "pipeline"],
    };

    mockGetWebhookStatus.mockResolvedValue(manualSetupStatus);
    mockGetWebhookSecret.mockResolvedValue(secretResponse);

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("https://example.com/webhooks/org/gitlab/1")).toBeInTheDocument();
    });

    const copyButtons = screen.getAllByRole("button").filter(
      btn => btn.querySelector("svg")
    );

    // Click copy button - should not throw
    fireEvent.click(copyButtons[0]);

    // Component should still be functional
    expect(screen.getByText("Needs Manual Setup")).toBeInTheDocument();
  });

  it("should handle rapid button clicks gracefully", async () => {
    let resolveRegister: () => void;
    const registerPromise = new Promise<void>((resolve) => {
      resolveRegister = resolve;
    });

    mockGetWebhookStatus.mockResolvedValue(registeredStatus);
    mockRegisterWebhook.mockImplementation(() => {
      return registerPromise.then(() => ({
        repo_id: 1,
        registered: true,
        webhook_id: "wh_new",
        needs_manual_setup: false,
      }));
    });

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Re-register")).toBeInTheDocument();
    });

    // Click multiple times rapidly
    fireEvent.click(screen.getByText("Re-register"));
    fireEvent.click(screen.getByText("Re-register"));
    fireEvent.click(screen.getByText("Re-register"));

    // Resolve the promise
    resolveRegister!();

    await waitFor(() => {
      expect(mockRegisterWebhook).toHaveBeenCalled();
    });
  });
});
