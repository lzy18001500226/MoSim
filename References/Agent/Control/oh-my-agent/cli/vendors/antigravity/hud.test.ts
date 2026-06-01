import * as fs from "node:fs";
import * as os from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { installAntigravityHud } from "./hud.js";

const FAKE_HOME = "/tmp/fake-home";
const AGY_DIR = join(FAKE_HOME, ".gemini/antigravity-cli");
const SETTINGS = join(AGY_DIR, "settings.json");
const HOOKS_DIR = join(AGY_DIR, "hooks");
const VARIANT = "/repo/.agents/hooks/variants/antigravity.json";

const variantJson = JSON.stringify({
  events: {
    PreInvocation: [
      { hook: "keyword-detector.ts", timeout: 5 },
      { hook: "state-boundary.ts", timeout: 5 },
      { hook: "skill-injector.ts", timeout: 3 },
    ],
    PreToolUse: {
      hook: "test-filter.ts",
      matcher: "Bash",
      timeout: 5,
    },
    Stop: { hook: "persistent-mode.ts", timeout: 5 },
  },
  statusLine: { hook: "hud.ts" },
});

vi.mock("node:os", async () => {
  const actual = await vi.importActual<typeof import("node:os")>("node:os");
  return { ...actual, homedir: vi.fn(() => FAKE_HOME) };
});

vi.mock("node:fs", () => ({
  existsSync: vi.fn(),
  mkdirSync: vi.fn(),
  cpSync: vi.fn(),
  readdirSync: vi.fn(),
  readFileSync: vi.fn(),
  writeFileSync: vi.fn(),
  lstatSync: vi.fn(),
  rmSync: vi.fn(),
  unlinkSync: vi.fn(),
}));

describe("installAntigravityHud", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (os.homedir as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      FAKE_HOME,
    );
    (fs.readdirSync as unknown as ReturnType<typeof vi.fn>).mockReturnValue([]);
    (fs.lstatSync as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      () => {
        throw new Error("ENOENT");
      },
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("bails when agy config dir is absent", () => {
    (fs.existsSync as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
      false,
    );

    const result = installAntigravityHud("/repo");
    expect(result.installed).toBe(false);
    expect(result.reason).toMatch(/agy config dir not found/);
    expect(fs.writeFileSync).not.toHaveBeenCalled();
  });

  it("writes statusLine and PreToolUse/Stop hooks with absolute commands", () => {
    (fs.existsSync as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      (p: string) => {
        const norm = p.replace(/\\/g, "/");
        if (norm.endsWith(".gemini/antigravity-cli")) return true;
        if (norm.includes(".agents/hooks/core")) return true;
        if (norm.includes(".agents/hooks/variants/antigravity.json"))
          return true;
        return false; // settings.json missing -> start fresh
      },
    );
    (fs.readFileSync as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      (p: string) => {
        const norm = p.replace(/\\/g, "/");
        if (norm.includes(".agents/hooks/variants/antigravity.json"))
          return variantJson;
        return "{}";
      },
    );

    const result = installAntigravityHud("/repo");

    expect(result.installed).toBe(true);
    expect(fs.cpSync).toHaveBeenCalledWith(
      "/repo/.agents/hooks/core",
      HOOKS_DIR,
      { recursive: true, force: true, dereference: true },
    );

    const writeCall = (
      fs.writeFileSync as unknown as ReturnType<typeof vi.fn>
    ).mock.calls.find(
      (call: string[]) => typeof call[0] === "string" && call[0] === SETTINGS,
    );
    expect(writeCall).toBeTruthy();

    const settings = JSON.parse(writeCall?.[1] as string);
    expect(settings.statusLine.type).toBe("command");
    expect(settings.statusLine.command).toBe(
      `bun "${join(HOOKS_DIR, "hud.ts")}"`,
    );
    expect(settings.hooks.PreInvocation).toHaveLength(3);
    expect(settings.hooks.PreInvocation[0]).toMatchObject({
      name: "keyword-detector",
      type: "command",
      command: `bun "${join(HOOKS_DIR, "keyword-detector.ts")}"`,
      timeout: 5,
    });
    expect(settings.hooks.PreInvocation[1].command).toBe(
      `bun "${join(HOOKS_DIR, "state-boundary.ts")}"`,
    );
    expect(settings.hooks.PreInvocation[2].command).toBe(
      `bun "${join(HOOKS_DIR, "skill-injector.ts")}"`,
    );
    expect(settings.hooks.PreToolUse[0].matcher).toBe("Bash");
    expect(settings.hooks.PreToolUse[0].hooks[0].command).toBe(
      `bun "${join(HOOKS_DIR, "test-filter.ts")}"`,
    );
    expect(settings.hooks.Stop[0].command).toBe(
      `bun "${join(HOOKS_DIR, "persistent-mode.ts")}"`,
    );
  });

  it("preserves existing unrelated keys (colorScheme, toolPermission, trustedWorkspaces)", () => {
    (fs.existsSync as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      (p: string) => {
        const norm = p.replace(/\\/g, "/");
        if (norm.endsWith(".gemini/antigravity-cli")) return true;
        if (norm === SETTINGS) return true;
        if (norm.includes(".agents/hooks/core")) return true;
        if (norm.includes(".agents/hooks/variants/antigravity.json"))
          return true;
        return false;
      },
    );
    (fs.readFileSync as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      (p: string) =>
        p === VARIANT
          ? variantJson
          : JSON.stringify({
              colorScheme: "tokyo night",
              enableTelemetry: false,
              toolPermission: "always-proceed",
              trustedWorkspaces: ["/repo"],
            }),
    );

    installAntigravityHud("/repo");

    const writeCall = (
      fs.writeFileSync as unknown as ReturnType<typeof vi.fn>
    ).mock.calls.find(
      (call: string[]) => typeof call[0] === "string" && call[0] === SETTINGS,
    );
    const settings = JSON.parse(writeCall?.[1] as string);

    expect(settings.colorScheme).toBe("tokyo night");
    expect(settings.enableTelemetry).toBe(false);
    expect(settings.toolPermission).toBe("always-proceed");
    expect(settings.trustedWorkspaces).toEqual(["/repo"]);
    // and HUD wiring was added alongside
    expect(settings.statusLine).toBeDefined();
    expect(settings.hooks).toBeDefined();
  });

  it("is idempotent — second run produces the same settings", () => {
    (fs.existsSync as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      (p: string) => {
        const norm = p.replace(/\\/g, "/");
        if (norm.endsWith(".gemini/antigravity-cli")) return true;
        if (norm === SETTINGS) return true;
        if (norm.includes(".agents/hooks/core")) return true;
        if (norm.includes(".agents/hooks/variants/antigravity.json"))
          return true;
        return false;
      },
    );

    let snapshot = "{}";
    (fs.readFileSync as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      (p: string) => (p === SETTINGS ? snapshot : variantJson),
    );
    (
      fs.writeFileSync as unknown as ReturnType<typeof vi.fn>
    ).mockImplementation((p: string, content: string) => {
      if (p === SETTINGS) snapshot = content;
    });

    installAntigravityHud("/repo");
    const firstSnapshot = snapshot;
    installAntigravityHud("/repo");
    expect(snapshot).toBe(firstSnapshot);
  });
});
