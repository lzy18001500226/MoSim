import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CredentialFormFields } from "../CredentialFormFields";
import { getCredentialFormSpec } from "../AgentCredentialsSettings/credentialForms";

const mockT = (key: string) => {
  const translations: Record<string, string> = {
    "common.optional": "Optional",
    "settings.agentCredentials.secretPlaceholder": "Leave empty to keep existing",
    "settings.agentCredentials.secretEditHint": "Leave empty to keep the existing value",
    "settings.credentialForm.anthropic.apiKey": "Anthropic API Key",
    "settings.credentialForm.anthropic.authToken": "Anthropic Auth Token",
    "settings.credentialForm.anthropic.baseUrl": "Anthropic Base URL",
    "settings.credentialForm.anthropic.authMethod": "Authentication",
    "settings.credentialForm.anthropic.authMethodHint": "Provide either one",
    "settings.credentialForm.openai.apiKey": "OpenAI API Key",
    "settings.credentialForm.google.apiKey": "Google API Key",
    "settings.credentialForm.customEnv.title": "Custom Environment Variables",
    "settings.credentialForm.customEnv.addButton": "Add Variable",
    "settings.credentialForm.customEnv.keyPlaceholder": "ENV_NAME",
    "settings.credentialForm.customEnv.valuePlaceholder": "Value",
    "settings.credentialForm.customEnv.remove": "Remove",
    "settings.credentialForm.customEnv.keyInvalid": "Invalid env var name",
    "settings.credentialForm.customEnv.keyConflict": "Conflicts with declared field",
    "settings.credentialForm.customEnv.keyDuplicate": "Duplicate env var name",
    "settings.credentialForm.loopal.customEnvHint": "More provider keys",
  };
  return translations[key] || key;
};

describe("CredentialFormFields - claude-code (XOR auth)", () => {
  const claudeSpec = getCredentialFormSpec("claude-code");

  function renderClaude(overrides?: {
    selectedOneOf?: Record<string, string>;
    values?: Record<string, string>;
    onOneOfChange?: () => void;
    onValueChange?: () => void;
  }) {
    return render(
      <CredentialFormFields
        spec={claudeSpec}
        values={overrides?.values ?? {}}
        onValueChange={overrides?.onValueChange ?? vi.fn()}
        selectedOneOf={overrides?.selectedOneOf ?? {}}
        onOneOfChange={overrides?.onOneOfChange ?? vi.fn()}
        customEnv={[]}
        onCustomEnvChange={vi.fn()}
        isEditing={false}
        t={mockT}
      />
    );
  }

  it("renders Base URL first, then the auth radio group", () => {
    renderClaude();
    expect(screen.getByLabelText("Anthropic Base URL")).toBeInTheDocument();
    expect(screen.getByRole("radiogroup", { name: "Authentication" })).toBeInTheDocument();
  });

  it("defaults to ANTHROPIC_API_KEY when no selection is provided", () => {
    renderClaude();
    expect(screen.getByLabelText("Anthropic API Key")).toBeInTheDocument();
    expect(document.getElementById("cred-ANTHROPIC_API_KEY")).toBeInTheDocument();
    expect(document.getElementById("cred-ANTHROPIC_AUTH_TOKEN")).toBeNull();
  });

  it("renders Auth Token input when selectedOneOf points to it", () => {
    renderClaude({ selectedOneOf: { anthropic_auth: "ANTHROPIC_AUTH_TOKEN" } });
    expect(document.getElementById("cred-ANTHROPIC_AUTH_TOKEN")).toBeInTheDocument();
    expect(document.getElementById("cred-ANTHROPIC_API_KEY")).toBeNull();
  });

  it("calls onOneOfChange when radio is clicked", () => {
    const onOneOfChange = vi.fn();
    renderClaude({ onOneOfChange });
    const radio = screen
      .getByTestId("oneof-option-anthropic_auth-ANTHROPIC_AUTH_TOKEN")
      .querySelector("input")!;
    fireEvent.click(radio);
    expect(onOneOfChange).toHaveBeenCalledWith("anthropic_auth", "ANTHROPIC_AUTH_TOKEN");
  });

  it("does not render the custom env section (allowCustomEnv=false)", () => {
    renderClaude();
    expect(screen.queryByText("Custom Environment Variables")).toBeNull();
  });
});

describe("CredentialFormFields - loopal (custom env)", () => {
  const loopalSpec = getCredentialFormSpec("loopal");

  it("renders three distinct provider labels", () => {
    render(
      <CredentialFormFields
        spec={loopalSpec}
        values={{}}
        onValueChange={vi.fn()}
        selectedOneOf={{}}
        onOneOfChange={vi.fn()}
        customEnv={[]}
        onCustomEnvChange={vi.fn()}
        isEditing={false}
        t={mockT}
      />
    );
    expect(screen.getByLabelText("Anthropic API Key")).toBeInTheDocument();
    expect(screen.getByLabelText("OpenAI API Key")).toBeInTheDocument();
    expect(screen.getByLabelText("Google API Key")).toBeInTheDocument();
  });

  it("renders custom env section with hint", () => {
    render(
      <CredentialFormFields
        spec={loopalSpec}
        values={{}}
        onValueChange={vi.fn()}
        selectedOneOf={{}}
        onOneOfChange={vi.fn()}
        customEnv={[]}
        onCustomEnvChange={vi.fn()}
        isEditing={false}
        t={mockT}
      />
    );
    expect(screen.getByText("Custom Environment Variables")).toBeInTheDocument();
    expect(screen.getByText("More provider keys")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Add Variable/ })).toBeInTheDocument();
  });

  it("renders existing custom env entries and adds new ones", () => {
    const onCustomEnvChange = vi.fn();
    render(
      <CredentialFormFields
        spec={loopalSpec}
        values={{}}
        onValueChange={vi.fn()}
        selectedOneOf={{}}
        onOneOfChange={vi.fn()}
        customEnv={[{ id: "1", key: "XAI_API_KEY", value: "xai-secret" }]}
        onCustomEnvChange={onCustomEnvChange}
        isEditing={false}
        t={mockT}
      />
    );
    const keyInput = screen.getAllByLabelText("ENV_NAME")[0] as HTMLInputElement;
    expect(keyInput.value).toBe("XAI_API_KEY");

    fireEvent.click(screen.getByRole("button", { name: /Add Variable/ }));
    expect(onCustomEnvChange).toHaveBeenCalled();
    const [, callArg] = onCustomEnvChange.mock.calls[0];
    void callArg;
    const newList = onCustomEnvChange.mock.calls[0][0];
    expect(newList).toHaveLength(2);
  });

  it("flags custom env key that conflicts with a declared field", () => {
    render(
      <CredentialFormFields
        spec={loopalSpec}
        values={{}}
        onValueChange={vi.fn()}
        selectedOneOf={{}}
        onOneOfChange={vi.fn()}
        customEnv={[{ id: "1", key: "OPENAI_API_KEY", value: "" }]}
        onCustomEnvChange={vi.fn()}
        isEditing={false}
        t={mockT}
      />
    );
    expect(screen.getByText("Conflicts with declared field")).toBeInTheDocument();
  });

  it("flags malformed custom env key", () => {
    render(
      <CredentialFormFields
        spec={loopalSpec}
        values={{}}
        onValueChange={vi.fn()}
        selectedOneOf={{}}
        onOneOfChange={vi.fn()}
        customEnv={[{ id: "1", key: "lowercase", value: "v" }]}
        onCustomEnvChange={vi.fn()}
        isEditing={false}
        t={mockT}
      />
    );
    expect(screen.getByText("Invalid env var name")).toBeInTheDocument();
  });
});

describe("CredentialFormFields - empty spec", () => {
  it("renders nothing when fields are empty and custom env disabled", () => {
    // Construct a synthetic empty spec rather than relying on a builtin —
    // e2e-echo used to be `fields: []; allowCustomEnv: false`, but it now
    // exposes a sample field for EnvBundle end-to-end tests.
    const emptySpec = {
      agentSlug: "test-empty-spec",
      fields: [],
      allowCustomEnv: false,
    };
    const { container } = render(
      <CredentialFormFields
        spec={emptySpec}
        values={{}}
        onValueChange={vi.fn()}
        selectedOneOf={{}}
        onOneOfChange={vi.fn()}
        customEnv={[]}
        onCustomEnvChange={vi.fn()}
        isEditing={false}
        t={mockT}
      />
    );
    expect(container.innerHTML).toBe("");
  });
});
