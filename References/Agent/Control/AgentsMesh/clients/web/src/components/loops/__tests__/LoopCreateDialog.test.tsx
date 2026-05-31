import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { LoopCreateDialog } from "../LoopCreateDialog";
import type { LoopData } from "@/lib/viewModels/loop";

// --- store / data hook mocks ---------------------------------------------

const mockCreateLoop = vi.fn();
const mockUpdateLoop = vi.fn();
vi.mock("@/stores/loop", () => ({
  useLoopStore: (selector: (s: Record<string, unknown>) => unknown) =>
    selector({ createLoop: mockCreateLoop, updateLoop: mockUpdateLoop }),
}));

const mockAvailableAgents = [
  { name: "Claude Code", slug: "claude-code", is_builtin: true, is_active: true },
];
vi.mock("@/components/pod/hooks", () => ({
  usePodCreationData: () => ({
    runners: [],
    repositories: [],
    loading: false,
    selectedRunner: null,
    setSelectedRunnerId: vi.fn(),
    availableAgents: mockAvailableAgents,
    agents: mockAvailableAgents,
    error: null,
  }),
}));

vi.mock("@/components/ide/hooks", () => ({
  useConfigOptions: () => ({
    fields: [],
    loading: false,
    config: {},
    updateConfig: vi.fn(),
    resetConfig: vi.fn(),
  }),
}));

// --- EnvBundleService mock --------------------------------------------------
// useLoopEnvBundles calls listEnvBundles({kind:"credential"}) + listEnvBundles({kind:"runtime"})
// in parallel. The mock dispatches by kind so each query returns its own list.

const { mockListEnvBundles } = vi.hoisted(() => ({
  mockListEnvBundles: vi.fn(),
}));
vi.mock("@/lib/api/facade/envBundleConnect", () => ({
  listEnvBundles: mockListEnvBundles,
}));

// --- Stubs for visual/dialog/intl/toast deps -------------------------------

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => key,
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

vi.mock("@/components/ide/ConfigForm", () => ({
  ConfigForm: () => <div data-testid="config-form" />,
}));

vi.mock("@/components/ui/responsive-dialog", () => ({
  ResponsiveDialog: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="dialog">{children}</div>
  ),
  ResponsiveDialogContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  ResponsiveDialogHeader: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  ResponsiveDialogTitle: ({ children }: { children: React.ReactNode }) => <h2>{children}</h2>,
  ResponsiveDialogBody: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  ResponsiveDialogFooter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock("@/components/pod/CreatePodForm/AdvancedOptions", () => ({
  AdvancedOptions: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// --- Test data --------------------------------------------------------------

const bundleWork = {
  id: BigInt(1),
  agentSlug: "claude-code",
  name: "Work",
  kind: "credential",
  kindPrimary: true,
  isActive: true,
  configuredFields: ["ANTHROPIC_API_KEY"],
  createdAt: "2026-01-01T00:00:00Z",
  updatedAt: "2026-01-01T00:00:00Z",
};

const bundlePersonal = {
  id: BigInt(2),
  agentSlug: "claude-code",
  name: "Personal",
  kind: "credential",
  kindPrimary: false,
  isActive: true,
  configuredFields: ["ANTHROPIC_API_KEY"],
  createdAt: "x",
  updatedAt: "x",
};

const bundleDevPreferences = {
  id: BigInt(3),
  agentSlug: "claude-code",
  name: "dev-preferences",
  kind: "runtime",
  kindPrimary: false,
  isActive: true,
  configuredFields: ["ANTHROPIC_MODEL", "LOG_LEVEL"],
  createdAt: "x",
  updatedAt: "x",
};

const bundleProxyStaging = {
  id: BigInt(4),
  agentSlug: "claude-code",
  name: "proxy-staging",
  kind: "runtime",
  kindPrimary: false,
  isActive: true,
  configuredFields: ["HTTPS_PROXY"],
  createdAt: "x",
  updatedAt: "x",
};

function fillRequiredFields() {
  fireEvent.change(screen.getByPlaceholderText("daily-code-review"), {
    target: { value: "Nightly CI" },
  });
  const prompt = screen.getByPlaceholderText("loops.promptPlaceholder") as HTMLTextAreaElement;
  fireEvent.change(prompt, { target: { value: "run tests" } });
}

async function waitForBundlesLoaded() {
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 0));
  });
}

function mockBundleList(creds: unknown[], runtimes: unknown[] = []) {
  mockListEnvBundles.mockImplementation(async (opts?: { kind?: string }) => {
    if (opts?.kind === "credential") return { items: creds, total: creds.length };
    if (opts?.kind === "runtime") return { items: runtimes, total: runtimes.length };
    return { items: [], total: 0 };
  });
}

// ---------------------------------------------------------------------------

describe("LoopCreateDialog — EnvBundle binding", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockBundleList([bundleWork], [bundleDevPreferences]);
    mockCreateLoop.mockResolvedValue({ loop: { slug: "nightly-ci" } });
    mockUpdateLoop.mockResolvedValue({ slug: "nightly-ci" });
  });

  it("renders both credential single-select AND runtime multi-select after an agent is chosen", async () => {
    const { container } = render(
      <LoopCreateDialog open onOpenChange={() => {}} onCreated={() => {}} />
    );

    const agentSelect = container.querySelector("#agent-select") as HTMLSelectElement;
    expect(agentSelect).toBeTruthy();
    fireEvent.change(agentSelect, { target: { value: "claude-code" } });

    await waitForBundlesLoaded();

    // Credential picker is a labeled <select>; runtime picker uses checkbox list.
    expect(screen.getByLabelText("ide.createPod.selectCredential")).toBeInTheDocument();
    expect(screen.getByText("ide.createPod.selectRuntimeBundles")).toBeInTheDocument();
    // The credential bundle appears as a <select> <option>; the runtime bundle as a checkbox.
    expect(screen.getByText("dev-preferences")).toBeInTheDocument();
  });

  it("submits used_env_bundles=[credName] when only a credential is selected", async () => {
    const { container } = render(
      <LoopCreateDialog open onOpenChange={() => {}} onCreated={() => {}} />
    );

    const agentSelect = container.querySelector("#agent-select") as HTMLSelectElement;
    fireEvent.change(agentSelect, { target: { value: "claude-code" } });
    await waitForBundlesLoaded();

    fillRequiredFields();

    fireEvent.change(screen.getByLabelText("ide.createPod.selectCredential"), {
      target: { value: "Work" },
    });

    const createBtn = screen.getByRole("button", { name: "loops.createLoop" });
    await act(async () => {
      fireEvent.click(createBtn);
    });

    await waitFor(() => expect(mockCreateLoop).toHaveBeenCalledTimes(1));
    const payload = mockCreateLoop.mock.calls[0][0];
    expect(payload.used_env_bundles).toEqual(["Work"]);
  });

  it("submits used_env_bundles=[] when no bundle is selected (default auth + no runtime)", async () => {
    const { container } = render(
      <LoopCreateDialog open onOpenChange={() => {}} onCreated={() => {}} />
    );

    const agentSelect = container.querySelector("#agent-select") as HTMLSelectElement;
    fireEvent.change(agentSelect, { target: { value: "claude-code" } });
    await waitForBundlesLoaded();

    fillRequiredFields();
    // Force-clear the credential select (auto-default may have set a primary).
    fireEvent.change(screen.getByLabelText("ide.createPod.selectCredential"), {
      target: { value: "" },
    });

    const createBtn = screen.getByRole("button", { name: "loops.createLoop" });
    await act(async () => {
      fireEvent.click(createBtn);
    });

    await waitFor(() => expect(mockCreateLoop).toHaveBeenCalledTimes(1));
    const payload = mockCreateLoop.mock.calls[0][0];
    expect(payload.used_env_bundles).toEqual([]);
  });

  it("merges credential first then runtime bundles when both are selected", async () => {
    mockBundleList([bundleWork], [bundleDevPreferences, bundleProxyStaging]);
    const { container } = render(
      <LoopCreateDialog open onOpenChange={() => {}} onCreated={() => {}} />
    );

    const agentSelect = container.querySelector("#agent-select") as HTMLSelectElement;
    fireEvent.change(agentSelect, { target: { value: "claude-code" } });
    await waitForBundlesLoaded();
    fillRequiredFields();

    // Pick a credential.
    fireEvent.change(screen.getByLabelText("ide.createPod.selectCredential"), {
      target: { value: "Work" },
    });
    // Pick two runtimes in a specific order.
    fireEvent.click(screen.getByRole("checkbox", { name: /proxy-staging/i }));
    fireEvent.click(screen.getByRole("checkbox", { name: /dev-preferences/i }));

    const createBtn = screen.getByRole("button", { name: "loops.createLoop" });
    await act(async () => {
      fireEvent.click(createBtn);
    });

    await waitFor(() => expect(mockCreateLoop).toHaveBeenCalledTimes(1));
    const payload = mockCreateLoop.mock.calls[0][0];
    // Credential first, then runtime in selection order.
    expect(payload.used_env_bundles).toEqual(["Work", "proxy-staging", "dev-preferences"]);
  });

  it("edit mode: reconciles used_env_bundles back into credential + runtime state", async () => {
    mockBundleList([bundleWork, bundlePersonal], [bundleDevPreferences]);
    const editLoop: LoopData = {
      id: 5,
      organization_id: 1,
      slug: "nightly",
      name: "Nightly",
      permission_mode: "bypassPermissions",
      prompt_template: "run tests",
      agent_slug: "claude-code",
      used_env_bundles: ["Work", "dev-preferences"],
      execution_mode: "autopilot",
      status: "enabled",
      sandbox_strategy: "persistent",
      session_persistence: true,
      concurrency_policy: "skip",
      max_concurrent_runs: 1,
      max_retained_runs: 0,
      timeout_minutes: 60,
      created_by_id: 1,
      total_runs: 0,
      successful_runs: 0,
      failed_runs: 0,
      active_run_count: 0,
      autopilot_config: {},
      created_at: "x",
      updated_at: "x",
    };

    render(
      <LoopCreateDialog open onOpenChange={() => {}} onCreated={() => {}} editLoop={editLoop} />
    );

    await waitForBundlesLoaded();

    const credSelect = screen.getByLabelText("ide.createPod.selectCredential") as HTMLSelectElement;
    expect(credSelect.value).toBe("Work");

    const runtimeCheckbox = screen.getByRole("checkbox", {
      name: /dev-preferences/i,
    }) as HTMLInputElement;
    expect(runtimeCheckbox.checked).toBe(true);
  });

  it("edit mode: updating bundle picks survives the round-trip to updateLoop", async () => {
    mockBundleList([bundleWork, bundlePersonal], [bundleDevPreferences]);
    const editLoop: LoopData = {
      id: 5,
      organization_id: 1,
      slug: "nightly",
      name: "Nightly",
      permission_mode: "bypassPermissions",
      prompt_template: "run tests",
      agent_slug: "claude-code",
      used_env_bundles: ["Work"],
      execution_mode: "autopilot",
      status: "enabled",
      sandbox_strategy: "persistent",
      session_persistence: true,
      concurrency_policy: "skip",
      max_concurrent_runs: 1,
      max_retained_runs: 0,
      timeout_minutes: 60,
      created_by_id: 1,
      total_runs: 0,
      successful_runs: 0,
      failed_runs: 0,
      active_run_count: 0,
      autopilot_config: {},
      created_at: "x",
      updated_at: "x",
    };

    render(
      <LoopCreateDialog open onOpenChange={() => {}} onCreated={() => {}} editLoop={editLoop} />
    );

    await waitForBundlesLoaded();

    // Swap credential Work → Personal.
    fireEvent.change(screen.getByLabelText("ide.createPod.selectCredential"), {
      target: { value: "Personal" },
    });
    // Add a runtime bundle.
    fireEvent.click(screen.getByRole("checkbox", { name: /dev-preferences/i }));

    const saveBtn = screen.getByRole("button", { name: "common.save" });
    await act(async () => {
      fireEvent.click(saveBtn);
    });

    await waitFor(() => expect(mockUpdateLoop).toHaveBeenCalledTimes(1));
    const [slug, payload] = mockUpdateLoop.mock.calls[0];
    expect(slug).toBe("nightly");
    expect(payload.used_env_bundles).toEqual(["Personal", "dev-preferences"]);
  });
});
