import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
  cleanup,
} from "@testing-library/react";
import { APIKeysSettings } from "../APIKeysSettings";
import type { ApiKey } from "@/lib/api/facade/apikey";
import { create } from "@bufbuild/protobuf";
import { ApiKeySchema } from "@proto/apikey/v1/api_key_pb";

interface UpdateInput {
  name?: string;
  description?: string;
  scopes?: string[];
  isEnabled?: boolean;
}

const { mockListApiKeys, mockCreateApiKey } = vi.hoisted(() => ({
  mockListApiKeys: vi.fn(),
  mockCreateApiKey: vi.fn(),
}));
vi.mock("@/lib/api/facade/apikey", () => ({
  listApiKeys: mockListApiKeys,
  createApiKey: mockCreateApiKey,
  updateApiKey: vi.fn(),
  revokeApiKey: vi.fn(),
}));

const { stableOrg } = vi.hoisted(() => ({
  stableOrg: { id: 10, slug: "test-org", name: "Test Org", role: "owner" },
}));
vi.mock("@/stores/auth", () => ({
  useCurrentOrg: () => stableOrg,
}));

const mockConfirm = vi.fn();
vi.mock("@/components/ui/confirm-dialog", () => ({
  ConfirmDialog: () => null,
  useConfirmDialog: () => ({
    dialogProps: {
      open: false,
      onOpenChange: vi.fn(),
      title: "",
      onConfirm: vi.fn(),
    },
    confirm: mockConfirm,
    isOpen: false,
  }),
}));

vi.mock("../apikeys", () => ({
  APIKeyCard: ({
    apiKey,
    onEdit,
    onRevoke,
  }: {
    apiKey: ApiKey;
    onEdit: (key: ApiKey) => void;
    onRevoke: (id: bigint) => void;
    t: unknown;
  }) => (
    <div data-testid={`api-key-card-${apiKey.id}`}>
      <span data-testid="key-name">{apiKey.name}</span>
      <button data-testid={`edit-${apiKey.id}`} onClick={() => onEdit(apiKey)}>
        Edit
      </button>
      <button
        data-testid={`revoke-${apiKey.id}`}
        onClick={() => onRevoke(apiKey.id)}
      >
        Revoke
      </button>
    </div>
  ),
  CreateAPIKeyDialog: ({
    open,
    onOpenChange,
    onCreate,
  }: {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onCreate: (data: {
      name: string;
      scopes: string[];
    }) => Promise<void>;
    t: unknown;
  }) => {
    if (!open) return null;
    return (
      <div data-testid="create-dialog">
        <button
          data-testid="create-dialog-submit"
          onClick={() =>
            onCreate({ name: "New Key", scopes: ["pods:read"] })
          }
        >
          Submit
        </button>
        <button
          data-testid="create-dialog-close"
          onClick={() => onOpenChange(false)}
        >
          Close
        </button>
      </div>
    );
  },
  APIKeySecretDialog: ({
    rawKey,
    open,
    onOpenChange,
  }: {
    rawKey: string;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    t: unknown;
  }) => {
    if (!open) return null;
    return (
      <div data-testid="secret-dialog">
        <span data-testid="raw-key">{rawKey}</span>
        <button
          data-testid="secret-dialog-close"
          onClick={() => onOpenChange(false)}
        >
          Done
        </button>
      </div>
    );
  },
  EditAPIKeyDialog: ({
    apiKey,
    open,
    onOpenChange,
    onSave,
  }: {
    apiKey: ApiKey;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSave: (id: bigint, data: UpdateInput) => Promise<void>;
    t: unknown;
  }) => {
    if (!open) return null;
    return (
      <div data-testid="edit-dialog">
        <span data-testid="editing-key-name">{apiKey.name}</span>
        <button
          data-testid="edit-dialog-save"
          onClick={() => onSave(apiKey.id, { name: "Updated" })}
        >
          Save
        </button>
        <button
          data-testid="edit-dialog-close"
          onClick={() => onOpenChange(false)}
        >
          Close
        </button>
      </div>
    );
  },
}));

const mockT = vi.fn((key: string) => key);

async function renderAndWaitForLoad(): Promise<ReturnType<typeof render>> {
  let result: ReturnType<typeof render>;
  await act(async () => {
    result = render(<APIKeysSettings t={mockT} />);
  });
  return result!;
}

const sampleKeys: ApiKey[] = [
  create(ApiKeySchema, {
    id: BigInt(1),
    organizationId: BigInt(10),
    name: "CI/CD Key",
    keyPrefix: "am_ci",
    scopes: ["pods:read", "pods:write"],
    isEnabled: true,
    createdBy: BigInt(1),
    createdAt: "2024-01-01T00:00:00Z",
    updatedAt: "2024-01-01T00:00:00Z",
  }),
  create(ApiKeySchema, {
    id: BigInt(2),
    organizationId: BigInt(10),
    name: "Monitoring Key",
    keyPrefix: "am_mon",
    scopes: ["tickets:read"],
    isEnabled: false,
    createdBy: BigInt(1),
    createdAt: "2024-02-01T00:00:00Z",
    updatedAt: "2024-02-01T00:00:00Z",
  }),
];

describe("APIKeysSettings - flows", () => {
  beforeEach(() => {
    cleanup();
    vi.clearAllMocks();
    mockListApiKeys.mockResolvedValue({ items: sampleKeys, total: 2, limit: 50, offset: 0 });
    mockConfirm.mockResolvedValue(true);
  });

  afterEach(() => {
    cleanup();
  });

  describe("create flow", () => {
    it("should open create dialog when create button is clicked", async () => {
      await renderAndWaitForLoad();

      await act(async () => {
        fireEvent.click(screen.getByText("settings.apiKeys.createKey"));
      });

      expect(screen.getByTestId("create-dialog")).toBeInTheDocument();
    });

    it("should close create dialog when close is clicked", async () => {
      await renderAndWaitForLoad();

      await act(async () => {
        fireEvent.click(screen.getByText("settings.apiKeys.createKey"));
      });

      expect(screen.getByTestId("create-dialog")).toBeInTheDocument();

      await act(async () => {
        fireEvent.click(screen.getByTestId("create-dialog-close"));
      });

      expect(
        screen.queryByTestId("create-dialog")
      ).not.toBeInTheDocument();
    });

    it("should show secret dialog after successful creation", async () => {
      vi.mocked(mockCreateApiKey).mockResolvedValue({
        apiKey: create(ApiKeySchema, {
          id: BigInt(3), organizationId: BigInt(10), name: "New Key", keyPrefix: "am_new",
          scopes: [], isEnabled: true, createdBy: BigInt(1),
          createdAt: "2024-03-01T00:00:00Z", updatedAt: "2024-03-01T00:00:00Z",
        }),
        rawKey: "am_new_secret123",
      });

      await renderAndWaitForLoad();

      await act(async () => {
        fireEvent.click(screen.getByText("settings.apiKeys.createKey"));
      });

      await act(async () => {
        fireEvent.click(screen.getByTestId("create-dialog-submit"));
      });

      await waitFor(() => {
        expect(screen.getByTestId("secret-dialog")).toBeInTheDocument();
      });
      expect(screen.getByTestId("raw-key")).toHaveTextContent(
        "am_new_secret123"
      );
    });

    it("should close secret dialog when done is clicked", async () => {
      vi.mocked(mockCreateApiKey).mockResolvedValue({
        apiKey: create(ApiKeySchema, {
          id: BigInt(3), organizationId: BigInt(10), name: "New Key", keyPrefix: "am_new",
          scopes: [], isEnabled: true, createdBy: BigInt(1),
          createdAt: "2024-03-01T00:00:00Z", updatedAt: "2024-03-01T00:00:00Z",
        }),
        rawKey: "am_new_secret123",
      });

      await renderAndWaitForLoad();

      await act(async () => {
        fireEvent.click(screen.getByText("settings.apiKeys.createKey"));
      });

      await act(async () => {
        fireEvent.click(screen.getByTestId("create-dialog-submit"));
      });

      await waitFor(() => {
        expect(screen.getByTestId("secret-dialog")).toBeInTheDocument();
      });

      await act(async () => {
        fireEvent.click(screen.getByTestId("secret-dialog-close"));
      });

      expect(
        screen.queryByTestId("secret-dialog")
      ).not.toBeInTheDocument();
    });

    it("should refresh key list after creation", async () => {
      vi.mocked(mockCreateApiKey).mockResolvedValue({
        apiKey: create(ApiKeySchema, {
          id: BigInt(3), organizationId: BigInt(10), name: "New Key", keyPrefix: "am_new",
          scopes: [], isEnabled: true, createdBy: BigInt(1),
          createdAt: "2024-03-01T00:00:00Z", updatedAt: "2024-03-01T00:00:00Z",
        }),
        rawKey: "am_new_secret123",
      });

      await renderAndWaitForLoad();

      expect(mockListApiKeys).toHaveBeenCalledTimes(1);

      await act(async () => {
        fireEvent.click(screen.getByText("settings.apiKeys.createKey"));
      });

      await act(async () => {
        fireEvent.click(screen.getByTestId("create-dialog-submit"));
      });

      await waitFor(() => {
        expect(mockListApiKeys).toHaveBeenCalledTimes(2);
      });
    });
  });
});
