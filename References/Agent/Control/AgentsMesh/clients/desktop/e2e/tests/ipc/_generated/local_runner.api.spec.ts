// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · local_runner", () => {
  test("localRunnerBinaryPath", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerBinaryPath", returnType: "string" });
  });

  test("localRunnerFallbackVersion", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerFallbackVersion", returnType: "any" });
  });

  test("localRunnerHostTarget", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerHostTarget", returnType: "string | null" });
  });

  test("localRunnerInstallBinary", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerInstallBinary", returnType: "void" }, "", "");
  });

  test("localRunnerInstalledVersion", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerInstalledVersion", returnType: "string | null" });
  });

  test("localRunnerIsInstalled", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerIsInstalled", returnType: "boolean" });
  });

  test("localRunnerIsRegistered", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerIsRegistered", returnType: "boolean" });
  });

  test("localRunnerLocalNodeId", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerLocalNodeId", returnType: "string | null" });
  });

  test("localRunnerRegister", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerRegister", returnType: "void" }, "");
  });

  test("localRunnerServiceInstall", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerServiceInstall", returnType: "void" });
  });

  test("localRunnerServiceStart", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerServiceStart", returnType: "void" });
  });

  test("localRunnerServiceStatus", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerServiceStatus", returnType: "string" });
  });

  test("localRunnerServiceStop", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerServiceStop", returnType: "void" });
  });

  test("localRunnerServiceUninstall", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "localRunnerServiceUninstall", returnType: "void" });
  });
});
