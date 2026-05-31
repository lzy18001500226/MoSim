import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => {
    const translations: Record<string, string> = {
      "title": "Webhook Settings",
      "loading": "Loading...",
      "status.registered": "Registered",
      "events": "Events",
      "reregister": "Re-register",
      "delete": "Delete",
      "error.delete": "Failed to delete webhook",
    };
    return translations[key] || key;
  },
}));

import {
  mockGetWebhookStatus,
  mockRegisterWebhook,
  mockDeleteWebhook,
} from "./testSetup";

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { WebhookSettings } from "../../webhook";
import {
  mockRepository,
  registeredStatus,
  resetAllMocks,
} from "./testSetup";

describe("WebhookSettings - Registered State", () => {
  const mockOnUpdate = vi.fn();

  beforeEach(() => {
    resetAllMocks();
    mockGetWebhookStatus.mockResolvedValue(registeredStatus);
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("should display registered status with webhook info", async () => {
    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Registered")).toBeInTheDocument();
    });

    expect(screen.getByText(/https:\/\/example\.com\/webhooks\/org\/gitlab\/1/)).toBeInTheDocument();
    expect(screen.getByText(/merge_request, pipeline/)).toBeInTheDocument();
  });

  it("should show re-register and delete buttons", async () => {
    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Re-register")).toBeInTheDocument();
    });

    expect(screen.getByText("Delete")).toBeInTheDocument();
  });

  it("should handle re-register click", async () => {
    const newStatus = {
      ...registeredStatus,
      webhook_id: "wh_456",
    };
    mockRegisterWebhook.mockResolvedValue({
      repo_id: 1,
      registered: true,
      webhook_id: "wh_456",
      needs_manual_setup: false,
    });
    mockGetWebhookStatus
      .mockResolvedValueOnce(registeredStatus)
      .mockResolvedValue(newStatus);

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Re-register")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Re-register"));

    await waitFor(() => {
      expect(mockRegisterWebhook).toHaveBeenCalled();
    });

    expect(mockOnUpdate).toHaveBeenCalled();
  });

  it("should handle delete click", async () => {
    mockDeleteWebhook.mockResolvedValue(undefined);

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Delete")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Delete"));

    await waitFor(() => {
      expect(mockDeleteWebhook).toHaveBeenCalled();
    });

    expect(mockOnUpdate).toHaveBeenCalled();
  });

  it("should show error when delete fails", async () => {
    mockDeleteWebhook.mockRejectedValue(new Error("Failed to delete"));

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Delete")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Delete"));

    await waitFor(() => {
      expect(screen.getByText("Failed to delete webhook")).toBeInTheDocument();
    });
  });
});
