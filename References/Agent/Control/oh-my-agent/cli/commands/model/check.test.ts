import { describe, expect, it } from "vitest";
import type { ModelSpec } from "../../platform/model-registry.js";
import type { SourceModel } from "./check.js";
import { computeDiff, formatHumanReadable, formatJson } from "./check.js";

function makeSpec(
  cliModel: string,
  cli: ModelSpec["cli"] = "claude",
): ModelSpec {
  return {
    cli,
    cli_model: cliModel,
    supports: {
      effort: null,
      apply_patch: false,
      task_budget: false,
      prompt_cache: false,
      computer_use: false,
      native_dispatch_from: [],
      api_only: false,
    },
    auth_hint: "test",
  };
}

function makeSource(slug: string): SourceModel {
  return {
    slug,
    contextLength: 128000,
    pricingPrompt: "0.000001",
    pricingCompletion: "0.000002",
  };
}

describe("computeDiff", () => {
  it("reports NEW models when source has models not in registry", () => {
    const registered = new Map<string, ModelSpec>();
    const sourceModels: SourceModel[] = [
      makeSource("anthropic/claude-new-model"),
    ];

    const diff = computeDiff(registered, sourceModels);
    expect(diff.new).toHaveLength(1);
    expect(diff.new[0]?.slug).toBe("anthropic/claude-new-model");
    expect(diff.removed).toHaveLength(0);
    expect(diff.drifted).toHaveLength(0);
  });

  it("reports REMOVED models when registry has models not in source", () => {
    const registered = new Map<string, ModelSpec>([
      ["anthropic/claude-old-model", makeSpec("claude-old-model")],
    ]);
    const sourceModels: SourceModel[] = [];

    const diff = computeDiff(registered, sourceModels);
    expect(diff.removed).toHaveLength(1);
    expect(diff.removed[0]?.slug).toBe("anthropic/claude-old-model");
    expect(diff.new).toHaveLength(0);
    expect(diff.drifted).toHaveLength(0);
  });

  it("reports both NEW and REMOVED when each side has exclusive models", () => {
    const registered = new Map<string, ModelSpec>([
      ["anthropic/claude-old", makeSpec("claude-old")],
    ]);
    const sourceModels: SourceModel[] = [makeSource("anthropic/claude-new")];

    const diff = computeDiff(registered, sourceModels);
    expect(diff.new).toHaveLength(1);
    expect(diff.new[0]?.slug).toBe("anthropic/claude-new");
    expect(diff.removed).toHaveLength(1);
    expect(diff.drifted).toHaveLength(0);
  });

  it("reports no changes when source and registry match exactly", () => {
    const registered = new Map<string, ModelSpec>([
      ["anthropic/claude-sonnet-4-6", makeSpec("claude-sonnet-4-6")],
    ]);
    const sourceModels: SourceModel[] = [
      makeSource("anthropic/claude-sonnet-4-6"),
    ];

    const diff = computeDiff(registered, sourceModels);
    expect(diff.new).toHaveLength(0);
    expect(diff.removed).toHaveLength(0);
    expect(diff.drifted).toHaveLength(0);
  });

  it("handles empty inputs on both sides", () => {
    const diff = computeDiff(new Map(), []);
    expect(diff.new).toHaveLength(0);
    expect(diff.removed).toHaveLength(0);
    expect(diff.drifted).toHaveLength(0);
  });

  it("returns drifted as empty array (placeholder for future drift detection)", () => {
    const registered = new Map<string, ModelSpec>([
      ["anthropic/claude-sonnet-4-6", makeSpec("claude-sonnet-4-6")],
    ]);
    const sourceModels: SourceModel[] = [
      makeSource("anthropic/claude-sonnet-4-6"),
    ];

    const diff = computeDiff(registered, sourceModels);
    expect(Array.isArray(diff.drifted)).toBe(true);
    expect(diff.drifted).toHaveLength(0);
  });
});

describe("formatHumanReadable", () => {
  it("shows (no changes) when diff is empty", () => {
    const output = formatHumanReadable({ new: [], removed: [], drifted: [] });
    expect(output).toContain("no changes");
  });

  it("contains + prefix for new models", () => {
    const diff = computeDiff(new Map(), [makeSource("anthropic/claude-new")]);
    const output = formatHumanReadable(diff);
    expect(output).toContain("+");
    expect(output).toContain("anthropic/claude-new");
  });

  it("contains - prefix for removed models", () => {
    const registered = new Map<string, ModelSpec>([
      ["anthropic/claude-old", makeSpec("claude-old")],
    ]);
    const diff = computeDiff(registered, []);
    const output = formatHumanReadable(diff);
    expect(output).toContain("-");
    expect(output).toContain("anthropic/claude-old");
  });
});

describe("formatJson", () => {
  it("returns valid JSON string", () => {
    const diff = { new: [], removed: [], drifted: [] };
    const json = formatJson(diff);
    expect(() => JSON.parse(json)).not.toThrow();
  });

  it("includes new, removed, drifted keys", () => {
    const diff = { new: [], removed: [], drifted: [] };
    const parsed = JSON.parse(formatJson(diff));
    expect(parsed).toHaveProperty("new");
    expect(parsed).toHaveProperty("removed");
    expect(parsed).toHaveProperty("drifted");
  });

  it("serializes source models in new array", () => {
    const diff = {
      new: [makeSource("openai/gpt-new")],
      removed: [],
      drifted: [],
    };
    const parsed = JSON.parse(formatJson(diff));
    expect(parsed.new[0].slug).toBe("openai/gpt-new");
  });
});
