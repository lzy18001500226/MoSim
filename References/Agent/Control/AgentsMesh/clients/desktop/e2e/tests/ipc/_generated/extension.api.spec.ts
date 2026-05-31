// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · extension", () => {
  test("extensionCreateSkillRegistryConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionCreateSkillRegistryConnect", returnType: "any" });
  });

  test("extensionDeleteSkillRegistryConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionDeleteSkillRegistryConnect", returnType: "any" });
  });

  test("extensionInstallCustomMcpServerConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionInstallCustomMcpServerConnect", returnType: "any" });
  });

  test("extensionInstallMcpFromMarketConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionInstallMcpFromMarketConnect", returnType: "any" });
  });

  test("extensionInstallSkillFromGithubConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionInstallSkillFromGithubConnect", returnType: "any" });
  });

  test("extensionInstallSkillFromMarketConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionInstallSkillFromMarketConnect", returnType: "any" });
  });

  test("extensionInstallSkillFromUploadedFileConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionInstallSkillFromUploadedFileConnect", returnType: "Array<number>" }, []);
  });

  test("extensionListMarketMcpServersConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionListMarketMcpServersConnect", returnType: "any" });
  });

  test("extensionListMarketSkillsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionListMarketSkillsConnect", returnType: "any" });
  });

  test("extensionListRepoMcpServersConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionListRepoMcpServersConnect", returnType: "any" });
  });

  test("extensionListRepoSkillsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionListRepoSkillsConnect", returnType: "any" });
  });

  test("extensionListSkillRegistriesConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionListSkillRegistriesConnect", returnType: "any" });
  });

  test("extensionListSkillRegistryOverridesConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionListSkillRegistryOverridesConnect", returnType: "any" });
  });

  test("extensionPresignSkillUploadConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionPresignSkillUploadConnect", returnType: "Array<number>" }, []);
  });

  test("extensionSyncSkillRegistryConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionSyncSkillRegistryConnect", returnType: "any" });
  });

  test("extensionTogglePlatformRegistryConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionTogglePlatformRegistryConnect", returnType: "any" });
  });

  test("extensionUninstallMcpServerConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionUninstallMcpServerConnect", returnType: "any" });
  });

  test("extensionUninstallSkillConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionUninstallSkillConnect", returnType: "any" });
  });

  test("extensionUpdateMcpServerConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionUpdateMcpServerConnect", returnType: "any" });
  });

  test("extensionUpdateSkillConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "extensionUpdateSkillConnect", returnType: "any" });
  });
});
