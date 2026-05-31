import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CreatePodForm } from "../index";
import {
  mockSetPrompt,
  mockSetAlias,
  defaultPodCreationData,
  defaultFormState,
  defaultConfigOptions,
  mockRunner,
  mockAgent,
  mockRepository,
  clearAllMocks,
} from "./test-utils";

vi.mock("../../hooks", () => ({
  usePodCreationData: vi.fn(() => defaultPodCreationData),
  useCreatePodForm: vi.fn(() => defaultFormState),
}));

vi.mock("@/components/ide/hooks", () => ({
  useConfigOptions: vi.fn(() => defaultConfigOptions),
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => key,
}));

vi.mock("@/components/ide/ConfigForm", () => ({
  ConfigForm: () => <div data-testid="config-form">Config Form</div>,
}));

vi.mock("@/lib/terminal-size", () => ({
  estimateWorkspaceTerminalSize: () => ({ cols: 80, rows: 24 }),
}));

// Mock Collapsible to always render children (no collapse animation in tests)
vi.mock("@/components/ui/collapsible", () => ({
  Collapsible: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CollapsibleTrigger: ({ children }: { children: React.ReactNode }) => <button>{children}</button>,
  CollapsibleContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock("@/stores/podCreation", () => ({
  usePodCreationStore: () => ({
    lastAgentSlug: null,
    lastRepositoryId: null,
    lastCredentialName: "",
    lastRuntimeBundleNames: [],
    lastBranchName: null,
    setLastChoices: vi.fn(),
    clearLastChoices: vi.fn(),
    _hasHydrated: true,
    setHasHydrated: vi.fn(),
  }),
}));

import { usePodCreationData, useCreatePodForm } from "../../hooks";
import { useConfigOptions } from "@/components/ide/hooks";

describe("CreatePodForm - Agent Configuration", () => {
  beforeEach(() => {
    clearAllMocks();
    vi.clearAllMocks();
  });

  const setupAgentSelectedState = (overrides = {}) => {
    const mockSetSelectedRepository = vi.fn();
    const mockSetSelectedBranch = vi.fn();
    const mockSetSelectedCredentialName = vi.fn();
    const mockSetSelectedRuntimeBundleNames = vi.fn();

    vi.mocked(usePodCreationData).mockReturnValue({
      ...defaultPodCreationData,
      runners: [mockRunner],
      repositories: [mockRepository, { ...mockRepository, id: 2, slug: "org/repo2" }],
      selectedRunner: mockRunner,
      availableAgents: [mockAgent],
    });

    vi.mocked(useCreatePodForm).mockReturnValue({
      ...defaultFormState,
      selectedAgent: "claude-code",
      envBundles: [
        { id: 1, agent_slug: "claude-code", name: "My Credentials", kind: "credential", kind_primary: false },
        { id: 2, agent_slug: "claude-code", name: "Default Creds", kind: "credential", kind_primary: true },
        { id: 3, agent_slug: "claude-code", name: "dev-preferences", kind: "runtime", kind_primary: false },
      ],
      setSelectedRepository: mockSetSelectedRepository,
      setSelectedBranch: mockSetSelectedBranch,
      setSelectedCredentialName: mockSetSelectedCredentialName,
      setSelectedRuntimeBundleNames: mockSetSelectedRuntimeBundleNames,
      selectedAgentSlug: "claude-code",
      isValid: true,
      ...overrides,
    });

    return {
      mockSetSelectedRepository,
      mockSetSelectedBranch,
      mockSetSelectedCredentialName,
      mockSetSelectedRuntimeBundleNames,
    };
  };

  describe("API credential single-select", () => {
    it("renders the credential dropdown with the default-auth option", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByLabelText("ide.createPod.selectCredential")).toBeInTheDocument();
      expect(screen.getByText("ide.createPod.useAgentDefaultAuth")).toBeInTheDocument();
    });

    it("lists every credential-kind bundle as a select option", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      const select = screen.getByLabelText("ide.createPod.selectCredential") as HTMLSelectElement;
      const options = Array.from(select.options).map((o) => o.value);
      expect(options).toContain("My Credentials");
      expect(options).toContain("Default Creds");
      // Runtime bundles should NOT appear in the credential dropdown.
      expect(options).not.toContain("dev-preferences");
    });

    it("calls setSelectedCredentialName when a credential is picked", () => {
      const { mockSetSelectedCredentialName } = setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      fireEvent.change(screen.getByLabelText("ide.createPod.selectCredential"), {
        target: { value: "My Credentials" },
      });
      expect(mockSetSelectedCredentialName).toHaveBeenCalledWith("My Credentials");
    });

    it("shows no-credential hint when nothing is selected", () => {
      setupAgentSelectedState({ selectedCredentialName: "" });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByText("ide.createPod.noCredentialHint")).toBeInTheDocument();
    });
  });

  describe("Runtime bundle multi-select", () => {
    it("renders the runtime bundle picker", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByText("ide.createPod.selectRuntimeBundles")).toBeInTheDocument();
    });

    it("lists only runtime-kind bundles as checkbox rows (excludes credentials)", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      // Runtime bundle shows up.
      expect(screen.getByText("dev-preferences")).toBeInTheDocument();
      // Credential bundles only appear in the credential select <option> elements
      // — never as checkbox rows. There must be exactly zero checkboxes labeled
      // with a credential name.
      const checkboxes = screen.getAllByRole("checkbox");
      const checkboxLabels = checkboxes.map((cb) => cb.getAttribute("aria-label") ?? "");
      expect(checkboxLabels.every((l) => !l.includes("My Credentials"))).toBe(true);
    });

    it("toggles selection through the runtime row checkbox", () => {
      const { mockSetSelectedRuntimeBundleNames } = setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      const checkboxes = screen.getAllByRole("checkbox");
      // Only one runtime bundle in this fixture; click it.
      fireEvent.click(checkboxes[0]);
      expect(mockSetSelectedRuntimeBundleNames).toHaveBeenCalledWith(["dev-preferences"]);
    });

    it("shows merge-order hint when a runtime bundle is selected", () => {
      setupAgentSelectedState({ selectedRuntimeBundleNames: ["dev-preferences"] });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByText("ide.createPod.multiBundleHint")).toBeInTheDocument();
    });

    it("shows loading state while bundles load", () => {
      setupAgentSelectedState({ loadingBundles: true });
      const { container } = render(<CreatePodForm config={{ scenario: "workspace" }} />);
      // Both pickers render the same loading affordance.
      expect(screen.getAllByText("common.loading").length).toBeGreaterThan(0);
      expect(container.querySelectorAll(".animate-spin").length).toBeGreaterThan(0);
    });
  });

  describe("repository selection", () => {
    it("should render repository select when agent is selected", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByLabelText("ide.createPod.selectRepository")).toBeInTheDocument();
    });

    it("should render repositories in select", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByText("org/repo1")).toBeInTheDocument();
      expect(screen.getByText("org/repo2")).toBeInTheDocument();
    });

    it("should call setSelectedRepository when changed", () => {
      const { mockSetSelectedRepository } = setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      fireEvent.change(screen.getByLabelText("ide.createPod.selectRepository"), { target: { value: "1" } });
      expect(mockSetSelectedRepository).toHaveBeenCalledWith(1);
    });

    it("should call setSelectedRepository with null when deselected", () => {
      const { mockSetSelectedRepository } = setupAgentSelectedState({ selectedRepository: 1 });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      fireEvent.change(screen.getByLabelText("ide.createPod.selectRepository"), { target: { value: "" } });
      expect(mockSetSelectedRepository).toHaveBeenCalledWith(null);
    });
  });

  describe("branch input", () => {
    it("should render branch input when repository is selected", () => {
      setupAgentSelectedState({ selectedRepository: 1 });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByLabelText("ide.createPod.branch")).toBeInTheDocument();
    });

    it("should not render branch input when no repository is selected", () => {
      setupAgentSelectedState({ selectedRepository: null });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.queryByLabelText("ide.createPod.branch")).not.toBeInTheDocument();
    });

    it("should call setSelectedBranch when changed", () => {
      const { mockSetSelectedBranch } = setupAgentSelectedState({ selectedRepository: 1 });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      fireEvent.change(screen.getByLabelText("ide.createPod.branch"), { target: { value: "feature/test" } });
      expect(mockSetSelectedBranch).toHaveBeenCalledWith("feature/test");
    });

    it("should show branch validation error", () => {
      setupAgentSelectedState({
        selectedRepository: 1,
        validationErrors: { branch: "Branch is required" },
      });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByText("Branch is required")).toBeInTheDocument();
    });
  });

  describe("prompt textarea", () => {
    it("should render prompt textarea when agent is selected", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByLabelText("ide.createPod.prompt")).toBeInTheDocument();
    });

    it("should use custom placeholder when provided", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace", promptPlaceholder: "Custom placeholder" }} />);
      expect(screen.getByPlaceholderText("Custom placeholder")).toBeInTheDocument();
    });

    it("should call setPrompt when changed", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      fireEvent.change(screen.getByLabelText("ide.createPod.prompt"), { target: { value: "New prompt" } });
      expect(mockSetPrompt).toHaveBeenCalledWith("New prompt");
    });
  });

  describe("alias input", () => {
    it("should render alias input when agent is selected", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByLabelText("ide.createPod.alias")).toBeInTheDocument();
    });

    it("should call setAlias when changed", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      fireEvent.change(screen.getByLabelText("ide.createPod.alias"), { target: { value: "my-pod" } });
      expect(mockSetAlias).toHaveBeenCalledWith("my-pod");
    });

    it("should show alias value from form state", () => {
      setupAgentSelectedState({ alias: "existing-alias" });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByLabelText("ide.createPod.alias")).toHaveValue("existing-alias");
    });

    it("should have maxLength of 100", () => {
      setupAgentSelectedState();
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByLabelText("ide.createPod.alias")).toHaveAttribute("maxLength", "100");
    });

    it("should not render alias input when no agent is selected", () => {
      vi.mocked(useCreatePodForm).mockReturnValue(defaultFormState);
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.queryByLabelText("ide.createPod.alias")).not.toBeInTheDocument();
    });
  });

  describe("config options", () => {
    it("should show loading state for config", () => {
      setupAgentSelectedState();
      vi.mocked(useConfigOptions).mockReturnValue({ ...defaultConfigOptions, loading: true });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByText("ide.createPod.loadingPlugins")).toBeInTheDocument();
    });

    it("should render config form when config fields are available", () => {
      setupAgentSelectedState();
      vi.mocked(useConfigOptions).mockReturnValue({
        ...defaultConfigOptions,
        fields: [{ name: "model", type: "select" }],
      });
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.getByText("ide.createPod.pluginConfig")).toBeInTheDocument();
      expect(screen.getByTestId("config-form")).toBeInTheDocument();
    });

    it("should not render config form when no config fields available", () => {
      setupAgentSelectedState();
      vi.mocked(useConfigOptions).mockReturnValue(defaultConfigOptions);
      render(<CreatePodForm config={{ scenario: "workspace" }} />);
      expect(screen.queryByText("ide.createPod.pluginConfig")).not.toBeInTheDocument();
    });
  });
});
