import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@/test/test-utils";
import {
  setupProviderMocks,
  mockRepositoryCreate,
  stableRepoSvc,
} from "./ImportRepositoryModal.utils";

// Stable references so React's useCallback([currentOrg]) doesn't churn.
// vi.hoisted survives vi.mock's factory hoisting.
const stable = vi.hoisted(() => ({
  org: { id: 1, name: "TestOrg", slug: "test-org" },
  user: { id: 1, email: "u@e.com", username: "u" },
}));

// useImportWizard.handleImport bails on !currentOrg; provide a non-null org.
vi.mock("@/stores/auth", () => ({
  useCurrentOrg: () => stable.org,
  useCurrentUser: () => stable.user,
  useAuthOrganizations: () => [],
  useAuthStore: () => ({ currentOrg: stable.org }),
  useIsAuthenticated: () => true,
  readCurrentUser: () => stable.user,
  readCurrentOrg: () => stable.org,
  readOrganizations: () => [],
}));

import { ImportRepositoryModal } from "../ImportRepositoryModal";

describe("ImportRepositoryModal - Confirmation Step", () => {
  const mockOnClose = vi.fn();
  const mockOnImported = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    setupProviderMocks();
    mockRepositoryCreate();
  });

  it("should navigate to confirm step after selecting repository", async () => {
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("My GitHub")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("My GitHub"));

    await waitFor(() => {
      expect(screen.getByText("org/my-project")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("org/my-project"));

    await waitFor(() => {
      expect(screen.getByText("Confirm Import")).toBeInTheDocument();
    });
  });

  it("should show repository details in confirm step", async () => {
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("My GitHub")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("My GitHub"));

    await waitFor(() => {
      expect(screen.getByText("org/my-project")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("org/my-project"));

    await waitFor(() => {
      expect(screen.getByText("my-project")).toBeInTheDocument();
      expect(screen.getByText(/Ticket Prefix/)).toBeInTheDocument();
    });
  });

  it("should show visibility options in confirm step", async () => {
    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("My GitHub")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("My GitHub"));

    await waitFor(() => {
      expect(screen.getByText("org/my-project")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("org/my-project"));

    await waitFor(() => {
      expect(screen.getByText("Visibility")).toBeInTheDocument();
      expect(screen.getByText("Organization")).toBeInTheDocument();
      expect(screen.getByText("Private (only you)")).toBeInTheDocument();
    });
  });

  it("should allow setting ticket prefix", async () => {
    mockRepositoryCreate();

    render(
      <ImportRepositoryModal open={true} onClose={mockOnClose} onImported={mockOnImported} />
    );

    await waitFor(() => {
      expect(screen.getByText("My GitHub")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("My GitHub"));

    await waitFor(() => {
      expect(screen.getByText("org/my-project")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("org/my-project"));

    await waitFor(() => {
      expect(screen.getByPlaceholderText("PROJ")).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText("PROJ"), {
      target: { value: "TEST" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Import Repository" }));

    await waitFor(() => {
      // useImportWizard.handleImport calls getRepositoryService().create(JSON.stringify({...}))
      // — assert on the parsed JSON payload.
      expect(stableRepoSvc.create).toHaveBeenCalled();
      const arg = stableRepoSvc.create.mock.calls[0][0];
      expect(JSON.parse(arg as string)).toEqual(
        expect.objectContaining({ ticket_prefix: "TEST" }),
      );
    });
  });
});
