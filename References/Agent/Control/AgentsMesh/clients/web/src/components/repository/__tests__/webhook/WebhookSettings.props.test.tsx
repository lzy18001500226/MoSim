import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => {
    const translations: Record<string, string> = {
      "title": "Webhook Settings",
      "loading": "Loading...",
      "status.registered": "Registered",
      "delete": "Delete",
    };
    return translations[key] || key;
  },
}));

import {
  mockGetWebhookStatus,
  mockDeleteWebhook,
} from "./testSetup";

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { WebhookSettings } from "../../webhook";
import {
  mockRepository,
  registeredStatus,
  resetAllMocks,
} from "./testSetup";

describe("WebhookSettings - Props", () => {
  const mockOnUpdate = vi.fn();

  beforeEach(() => {
    resetAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("should work without onUpdate callback", async () => {
    mockGetWebhookStatus.mockResolvedValue(registeredStatus);
    mockDeleteWebhook.mockResolvedValue(undefined);

    render(<WebhookSettings repository={mockRepository} />);

    await waitFor(() => {
      expect(screen.getByText("Delete")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Delete"));

    await waitFor(() => {
      expect(mockDeleteWebhook).toHaveBeenCalled();
    });

    // Should not throw even without onUpdate
  });

  it("should reload status when repository id changes", async () => {
    mockGetWebhookStatus.mockResolvedValue(registeredStatus);

    const { rerender } = render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(screen.getByText("Registered")).toBeInTheDocument();
    });

    expect(mockGetWebhookStatus).toHaveBeenCalledTimes(1);

    // Change repository
    const newRepo = { ...mockRepository, id: 2 };
    rerender(<WebhookSettings repository={newRepo} onUpdate={mockOnUpdate} />);

    await waitFor(() => {
      expect(mockGetWebhookStatus).toHaveBeenCalledTimes(2);
    });
  });
});
