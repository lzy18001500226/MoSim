import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => {
    const translations: Record<string, string> = {
      "title": "Webhook Settings",
      "loading": "Loading...",
    };
    return translations[key] || key;
  },
}));

import {
  mockGetWebhookStatus,
} from "./testSetup";

import { render, screen } from "@testing-library/react";
import { WebhookSettings } from "../../webhook";
import {
  mockRepository,
  resetAllMocks,
} from "./testSetup";

describe("WebhookSettings - Loading State", () => {
  const mockOnUpdate = vi.fn();

  beforeEach(() => {
    resetAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("should show loading state initially", () => {
    mockGetWebhookStatus.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<WebhookSettings repository={mockRepository} onUpdate={mockOnUpdate} />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });
});
