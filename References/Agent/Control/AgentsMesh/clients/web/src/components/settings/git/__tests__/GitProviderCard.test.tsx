import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { GitProviderCard } from "../GitProviderCard";
import type { RepositoryProvider } from "@/lib/api/facade/userRepositoryProvider";

const mockT = vi.fn((key: string) => key);

const baseProvider: RepositoryProvider = {
  $typeName: "proto.user_credential.v1.RepositoryProvider",
  id: BigInt(1),
  providerType: "github",
  name: "GitHub",
  baseUrl: "https://github.com",
  hasClientId: false,
  hasBotToken: false,
  hasIdentity: true,
  isDefault: false,
  isActive: true,
  createdAt: "2026-05-06T00:00:00Z",
  updatedAt: "2026-05-06T00:00:00Z",
};

describe("GitProviderCard", () => {
  let onEdit: () => void;
  let onDelete: () => void;
  let onTestConnection: () => void;

  beforeEach(() => {
    vi.clearAllMocks();
    onEdit = vi.fn<() => void>();
    onDelete = vi.fn<() => void>();
    onTestConnection = vi.fn<() => void>();
  });

  function renderCard(provider: RepositoryProvider = baseProvider) {
    return render(
      <GitProviderCard
        provider={provider}
        onEdit={onEdit}
        onDelete={onDelete}
        onTestConnection={onTestConnection}
        t={mockT}
      />
    );
  }

  describe("disabled badge visibility", () => {
    it("should NOT show disabled badge when isActive=true", () => {
      renderCard({ ...baseProvider, isActive: true });
      expect(
        screen.queryByText("settings.gitSettings.providers.disabled")
      ).not.toBeInTheDocument();
    });

    it("should show disabled badge when isActive=false", () => {
      renderCard({ ...baseProvider, isActive: false });
      expect(
        screen.getByText("settings.gitSettings.providers.disabled")
      ).toBeInTheDocument();
    });
  });

  describe("regression — wasm-core field-stripping bug", () => {
    it("should NOT show disabled badge when isActive is undefined (defensive)", () => {
      renderCard({ ...baseProvider, isActive: undefined as unknown as boolean });
      expect(
        screen.queryByText("settings.gitSettings.providers.disabled")
      ).not.toBeInTheDocument();
    });
  });

  describe("default badge", () => {
    it("should show default badge when isDefault=true", () => {
      renderCard({ ...baseProvider, isDefault: true });
      expect(
        screen.getByText("settings.gitSettings.providers.default")
      ).toBeInTheDocument();
    });

    it("should not show default badge when isDefault=false", () => {
      renderCard({ ...baseProvider, isDefault: false });
      expect(
        screen.queryByText("settings.gitSettings.providers.default")
      ).not.toBeInTheDocument();
    });
  });

  describe("provider info rendering", () => {
    it("renders the provider name and baseUrl", () => {
      renderCard({ ...baseProvider, name: "My GitLab", baseUrl: "https://gitlab.x" });
      expect(screen.getByText("My GitLab")).toBeInTheDocument();
      expect(screen.getByText("https://gitlab.x")).toBeInTheDocument();
    });
  });

  describe("button interactions", () => {
    it("calls onEdit when settings button is clicked", () => {
      renderCard();
      fireEvent.click(screen.getByTestId("git-provider-edit-button"));
      expect(onEdit).toHaveBeenCalledTimes(1);
    });

    it("calls onTestConnection when test button is clicked", () => {
      renderCard();
      fireEvent.click(screen.getByTitle("settings.gitSettings.providers.test"));
      expect(onTestConnection).toHaveBeenCalledTimes(1);
    });
  });
});

describe("GitProviderCard — visual styling reflects isActive", () => {
  it("applies dimmed style when disabled", () => {
    const { container } = render(
      <GitProviderCard
        provider={{ ...baseProvider, isActive: false }}
        onEdit={vi.fn<() => void>()}
        onDelete={vi.fn<() => void>()}
        onTestConnection={vi.fn<() => void>()}
        t={mockT}
      />
    );
    expect(container.querySelector(".opacity-60")).toBeInTheDocument();
  });

  it("does NOT apply dimmed style when active", () => {
    const { container } = render(
      <GitProviderCard
        provider={{ ...baseProvider, isActive: true }}
        onEdit={vi.fn<() => void>()}
        onDelete={vi.fn<() => void>()}
        onTestConnection={vi.fn<() => void>()}
        t={mockT}
      />
    );
    expect(container.querySelector(".opacity-60")).not.toBeInTheDocument();
  });
});
