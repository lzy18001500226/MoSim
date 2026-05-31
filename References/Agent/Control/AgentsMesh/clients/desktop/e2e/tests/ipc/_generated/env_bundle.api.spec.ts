// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · env_bundle", () => {
  test("envBundleCreateEnvBundleConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "envBundleCreateEnvBundleConnect", returnType: "any" });
  });

  test("envBundleDeleteEnvBundleConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "envBundleDeleteEnvBundleConnect", returnType: "any" });
  });

  test("envBundleGetEnvBundleConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "envBundleGetEnvBundleConnect", returnType: "any" });
  });

  test("envBundleListEnvBundlesConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "envBundleListEnvBundlesConnect", returnType: "any" });
  });

  test("envBundleSetPrimaryEnvBundleConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "envBundleSetPrimaryEnvBundleConnect", returnType: "any" });
  });

  test("envBundleUpdateEnvBundleConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "envBundleUpdateEnvBundleConnect", returnType: "any" });
  });
});
