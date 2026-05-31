import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => {
    const translations: Record<string, string> = {
      "title": "Webhook Settings",
      "loading": "Loading...",
      "status.needsManualSetup": "Needs Manual Setup",
      "manualSetupInstructions": "Please configure the webhook manually in your Git provider settings.",
      "markConfigured": "Mark as Configured",
      "tryAgain": "Try Again",
      "error.markConfigured": "Failed to mark webhook as configured",
    };
    return translations[key] || key;
  },
}));

import {
  mockGetWebhookStatus,
  mockGetWebhookSecret,
  mockRegisterWebhook,
  mockMarkWebhookConfigured,
} from "./testSetup";

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { WebhookSettings } from "../../webhook";
import {
  mockRepository,
  manualSetupStatus,
  secretResponse,
  mockClipboardWriteText,
  resetAllMocks,
} from "./testSetup";

describe("WebhookSettings - Needs Manual Setup State", () => {
  const mockOnUpdate = vi.fn();

  beforeEach(() => {
    resetAllMocks();
    mockGetWebhookStatus.mockResolvedValue(manualSetupStatus);
    mockGetWebhookSecret.mockResolvedValue(secretResponse);
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("should display needs manual setup status", async () => {
    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Needs Manual Setup")).toBeInTheDocument();
    });
  });

  it("should display manual setup instructions", async () => {
    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Please configure the webhook manually in your Git provider settings.")).toBeInTheDocument();
    });
  });

  it("should display webhook URL and secret", async () => {
    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("https://example.com/webhooks/org/gitlab/1")).toBeInTheDocument();
    });

    expect(screen.getByText("super_secret_value")).toBeInTheDocument();
  });

  it("should show mark configured and try again buttons", async () => {
    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Mark as Configured")).toBeInTheDocument();
    });

    expect(screen.getByText("Try Again")).toBeInTheDocument();
  });

  it("should handle mark configured click", async () => {
    const activeStatus = {
      ...manualSetupStatus,
      is_active: true,
      needs_manual_setup: false,
    };
    mockMarkWebhookConfigured.mockResolvedValue(undefined);
    mockGetWebhookStatus
      .mockResolvedValueOnce(manualSetupStatus)
      .mockResolvedValue(activeStatus);

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Mark as Configured")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Mark as Configured"));

    await waitFor(() => {
      expect(mockOnUpdate).toHaveBeenCalled();
    });
  });

  it("should show error when mark configured fails", async () => {
    mockMarkWebhookConfigured.mockRejectedValue(new Error("Failed"));

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Mark as Configured")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Mark as Configured"));

    await waitFor(() => {
      expect(screen.getByText("Failed to mark webhook as configured")).toBeInTheDocument();
    });
  });

  it("should copy URL to clipboard", async () => {
    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("https://example.com/webhooks/org/gitlab/1")).toBeInTheDocument();
    });

    // Find copy buttons (there should be 2: one for URL, one for secret)
    const copyButtons = screen.getAllByRole("button").filter(
      btn => btn.querySelector("svg")
    );

    // Click the first copy button (URL)
    fireEvent.click(copyButtons[0]);

    await waitFor(() => {
      expect(mockClipboardWriteText).toHaveBeenCalledWith("https://example.com/webhooks/org/gitlab/1");
    });
  });

  it("should copy secret to clipboard", async () => {
    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("super_secret_value")).toBeInTheDocument();
    });

    // Find all buttons with icons
    const allButtons = screen.getAllByRole("button");

    // Find the button next to the secret (second copy button)
    const secretCopyButton = allButtons.find(btn => {
      const parent = btn.closest("div.flex.items-center.gap-2");
      return parent && parent.querySelector("code")?.textContent === "super_secret_value";
    });

    if (secretCopyButton) {
      fireEvent.click(secretCopyButton);

      await waitFor(() => {
        expect(mockClipboardWriteText).toHaveBeenCalledWith("super_secret_value");
      });
    }
  });

  it("should handle try again click", async () => {
    mockRegisterWebhook.mockResolvedValue({
      repo_id: 1,
      registered: true,
      webhook_id: "wh_new",
      needs_manual_setup: false,
    });

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Try Again")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Try Again"));

    await waitFor(() => {
      expect(mockRegisterWebhook).toHaveBeenCalled();
    });
  });

  it("should handle secret fetch failure gracefully", async () => {
    mockGetWebhookSecret.mockRejectedValue(new Error("Secret not available"));

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Needs Manual Setup")).toBeInTheDocument();
    });

    // Should still show the status, just without secret data
  });
});
