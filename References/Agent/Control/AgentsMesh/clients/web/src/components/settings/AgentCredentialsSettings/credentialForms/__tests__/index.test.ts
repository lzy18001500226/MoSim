import { describe, it, expect } from "vitest";
import {
  getCredentialFormSpec,
  getEnvKeysFromSpec,
  findFieldByEnvKey,
  getEnvKeyLabel,
} from "../index";

describe("credentialForms registry", () => {
  it("returns claude-code spec with Base URL first and ONEOF auth group", () => {
    const spec = getCredentialFormSpec("claude-code");
    expect(spec.agentSlug).toBe("claude-code");
    expect(spec.allowCustomEnv).toBe(false);
    expect(spec.fields[0].kind).toBe("text");
    expect(spec.fields[0]).toMatchObject({ envKey: "ANTHROPIC_BASE_URL" });
    expect(spec.fields[1].kind).toBe("oneof");
    if (spec.fields[1].kind === "oneof") {
      expect(spec.fields[1].options.map((o) => o.envKey)).toEqual([
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
      ]);
    }
  });

  it("loopal exposes three distinct provider keys + custom env", () => {
    const spec = getCredentialFormSpec("loopal");
    expect(spec.allowCustomEnv).toBe(true);
    const envKeys = spec.fields
      .filter((f) => f.kind !== "oneof")
      .map((f) => ("envKey" in f ? f.envKey : ""));
    expect(envKeys).toEqual([
      "ANTHROPIC_API_KEY",
      "OPENAI_API_KEY",
      "GOOGLE_API_KEY",
    ]);
  });

  it("codex-cli has one declared field + allows custom env", () => {
    const spec = getCredentialFormSpec("codex-cli");
    expect(spec.fields).toHaveLength(1);
    expect(spec.allowCustomEnv).toBe(true);
  });

  it.each(["gemini-cli", "aider", "opencode", "e2e-echo"])(
    "%s spec exists with matching agentSlug",
    (slug) => {
      const spec = getCredentialFormSpec(slug);
      expect(spec.agentSlug).toBe(slug);
    }
  );

  it("falls back to pure custom-env form for unknown slug", () => {
    const spec = getCredentialFormSpec("custom-user-agent-xyz");
    expect(spec).toEqual({
      agentSlug: "custom-user-agent-xyz",
      fields: [],
      allowCustomEnv: true,
    });
  });
});

describe("getEnvKeysFromSpec", () => {
  it("flattens oneof options alongside simple fields", () => {
    const spec = getCredentialFormSpec("claude-code");
    const keys = getEnvKeysFromSpec(spec);
    expect(keys).toEqual(
      new Set(["ANTHROPIC_BASE_URL", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"])
    );
  });
});

describe("findFieldByEnvKey", () => {
  it("returns the oneof field when envKey is one of its options", () => {
    const spec = getCredentialFormSpec("claude-code");
    const field = findFieldByEnvKey(spec, "ANTHROPIC_AUTH_TOKEN");
    expect(field?.kind).toBe("oneof");
  });

  it("returns the simple field when envKey matches directly", () => {
    const spec = getCredentialFormSpec("claude-code");
    const field = findFieldByEnvKey(spec, "ANTHROPIC_BASE_URL");
    expect(field?.kind).toBe("text");
  });

  it("returns undefined for unknown envKey", () => {
    const spec = getCredentialFormSpec("loopal");
    expect(findFieldByEnvKey(spec, "UNKNOWN_KEY")).toBeUndefined();
  });
});

describe("getEnvKeyLabel", () => {
  const t = (key: string): string => {
    const map: Record<string, string> = {
      "settings.credentialForm.anthropic.apiKey": "Anthropic API Key",
      "settings.credentialForm.openai.apiKey": "OpenAI API Key",
      "settings.credentialForm.google.apiKey": "Google API Key",
    };
    return map[key] ?? key;
  };

  it("returns translated label for declared env keys", () => {
    expect(getEnvKeyLabel("loopal", "OPENAI_API_KEY", t)).toBe("OpenAI API Key");
    expect(getEnvKeyLabel("loopal", "GOOGLE_API_KEY", t)).toBe("Google API Key");
  });

  it("resolves oneof option labels", () => {
    expect(getEnvKeyLabel("claude-code", "ANTHROPIC_API_KEY", t)).toBe("Anthropic API Key");
  });

  it("falls back to raw env name for unknown keys or missing translation", () => {
    expect(getEnvKeyLabel("loopal", "XAI_API_KEY", t)).toBe("XAI_API_KEY");
    const noT = (k: string) => k;
    expect(getEnvKeyLabel("loopal", "OPENAI_API_KEY", noT)).toBe("OPENAI_API_KEY");
  });
});
