type StubFn = (...args: unknown[]) => Promise<unknown>;
export type LocalRunnerStubMap = Record<string, StubFn>;

const STUB_DELAY_MS = 50;

function delay(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

export function createLocalRunnerStubs(): LocalRunnerStubMap {
  const state = {
    installed: false,
    registered: false,
    serviceInstalled: false,
    running: false,
  };

  return {
    localRunnerBinaryPath: async () => "/tmp/test/.agentsmesh/bin/agentsmesh-runner",
    localRunnerHostTarget: async () => "darwin_arm64",
    localRunnerFallbackVersion: async () => "0.0.0-test",
    localRunnerIsInstalled: async () => state.installed,
    localRunnerInstalledVersion: async () => (state.installed ? "0.0.0-test" : null),
    localRunnerInstallBinary: async (..._args: unknown[]) => {
      await delay(STUB_DELAY_MS);
      state.installed = true;
    },
    localRunnerIsRegistered: async () => state.registered,
    localRunnerLocalNodeId: async () => (state.registered ? "test-mac" : null),
    localRunnerRegister: async (...args: unknown[]) => {
      const token = args[0];
      if (typeof token !== "string" || !token) throw new Error("empty token");
      await delay(STUB_DELAY_MS);
      state.registered = true;
    },
    localRunnerServiceInstall: async () => {
      await delay(STUB_DELAY_MS);
      state.serviceInstalled = true;
    },
    localRunnerServiceUninstall: async () => {
      state.serviceInstalled = false;
      state.running = false;
    },
    localRunnerServiceStart: async () => {
      await delay(STUB_DELAY_MS);
      if (!state.serviceInstalled) throw new Error("service not installed");
      state.running = true;
    },
    localRunnerServiceStop: async () => {
      state.running = false;
    },
    localRunnerServiceStatus: async () => {
      if (state.running) return "running";
      if (state.serviceInstalled) return "stopped";
      return "not_installed";
    },
  };
}
