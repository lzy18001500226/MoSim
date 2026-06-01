/**
 * Tests for the top-level --global flag and preAction hook in cli.ts.
 *
 * Strategy: build a minimal Commander program that mirrors the preAction wiring
 * from cli.ts. The install-context module is mocked via vi.mock with
 * importOriginal so that real types are preserved and vi.mocked() works
 * without explicit casts. _resetInstallContext is called in beforeEach/afterEach
 * to prevent "context already set" leakage across test cases.
 */

import { Command } from "commander";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("./platform/install-context.js", async (importOriginal) => {
  const real =
    await importOriginal<typeof import("./platform/install-context.js")>();
  return {
    ...real,
    resolveInstallContext: vi.fn(real.resolveInstallContext),
    setInstallContext: vi.fn(real.setInstallContext),
  };
});

import {
  _resetInstallContext,
  getInstallContext,
  resolveInstallContext,
  setInstallContext,
} from "./platform/install-context.js";

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Builds a minimal Commander program that replicates the preAction wiring
 * from cli.ts, with a single no-op subcommand for triggering the hook.
 */
function buildTestProgram() {
  const program = new Command();

  program
    .name("oma-test")
    .option("-g, --global", "operate on the user's HOME install (~/.agents/)");

  // Mirror the exact preAction hook from cli.ts
  program.hook("preAction", () => {
    const opts = program.opts<{ global?: boolean }>();
    const ctx = resolveInstallContext({ global: opts.global === true });
    setInstallContext(ctx);
  });

  program
    .command("noop")
    .description("no-op subcommand for testing")
    .action(() => {
      // intentionally empty
    });

  return program;
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("cli preAction hook — --global flag wiring", () => {
  beforeEach(() => {
    vi.mocked(resolveInstallContext).mockClear();
    vi.mocked(setInstallContext).mockClear();
    _resetInstallContext();
    delete process.env.OMA_HOME;
    delete process.env.OMA_INSTALL_GLOBAL;
  });

  afterEach(() => {
    _resetInstallContext();
    delete process.env.OMA_HOME;
    delete process.env.OMA_INSTALL_GLOBAL;
  });

  it("calls resolveInstallContext with { global: false } when --global is absent", async () => {
    const program = buildTestProgram();
    await program.parseAsync(["node", "oma", "noop"]);

    expect(vi.mocked(resolveInstallContext)).toHaveBeenCalledOnce();
    expect(vi.mocked(resolveInstallContext)).toHaveBeenCalledWith({
      global: false,
    });
  });

  it("calls resolveInstallContext with { global: true } when --global is present", async () => {
    const program = buildTestProgram();
    await program.parseAsync(["node", "oma", "--global", "noop"]);

    expect(vi.mocked(resolveInstallContext)).toHaveBeenCalledOnce();
    expect(vi.mocked(resolveInstallContext)).toHaveBeenCalledWith({
      global: true,
    });
  });

  it("calls resolveInstallContext with { global: true } when -g shorthand is used", async () => {
    const program = buildTestProgram();
    await program.parseAsync(["node", "oma", "-g", "noop"]);

    expect(vi.mocked(resolveInstallContext)).toHaveBeenCalledOnce();
    expect(vi.mocked(resolveInstallContext)).toHaveBeenCalledWith({
      global: true,
    });
  });

  it("calls setInstallContext exactly once before the subcommand action fires", async () => {
    const actionOrder: string[] = [];

    vi.mocked(setInstallContext).mockImplementationOnce(() => {
      actionOrder.push("setInstallContext");
    });

    const program = buildTestProgram();
    const noopCmd = program.commands.find((c) => c.name() === "noop");
    noopCmd?.action(() => {
      actionOrder.push("subcommandAction");
    });

    await program.parseAsync(["node", "oma", "noop"]);

    expect(vi.mocked(setInstallContext)).toHaveBeenCalledOnce();
    expect(actionOrder).toEqual(["setInstallContext", "subcommandAction"]);
  });

  it("stores project-mode context via the real setInstallContext when --global absent", async () => {
    vi.mocked(resolveInstallContext).mockImplementationOnce(() => ({
      installRoot: "/tmp/project",
      mode: "project",
    }));

    const program = buildTestProgram();
    await program.parseAsync(["node", "oma", "noop"]);

    expect(getInstallContext()).toEqual({
      installRoot: "/tmp/project",
      mode: "project",
    });
  });

  it("stores global-mode context via the real setInstallContext when --global is set", async () => {
    vi.mocked(resolveInstallContext).mockImplementationOnce(() => ({
      installRoot: "/home/testuser",
      mode: "global",
    }));

    const program = buildTestProgram();
    await program.parseAsync(["node", "oma", "--global", "noop"]);

    expect(getInstallContext()).toEqual({
      installRoot: "/home/testuser",
      mode: "global",
    });
  });
});
