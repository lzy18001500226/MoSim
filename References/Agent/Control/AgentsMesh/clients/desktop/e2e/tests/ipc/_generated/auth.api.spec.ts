// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · auth", () => {
  test("authApplySession", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authApplySession", returnType: "void" }, "");
  });

  test("authBootstrap", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authBootstrap", returnType: "any" });
  });

  test("authClearSession", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authClearSession", returnType: "void" });
  });

  test("authFetchOrganizations", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authFetchOrganizations", returnType: "string" });
  });

  test("authGetCurrentOrgJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authGetCurrentOrgJson", returnType: "string | null" });
  });

  test("authGetCurrentUserJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authGetCurrentUserJson", returnType: "string | null" });
  });

  test("authGetExpiresAt", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authGetExpiresAt", returnType: "any" });
  });

  test("authGetOrganizationsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authGetOrganizationsJson", returnType: "string" });
  });

  test("authGetToken", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authGetToken", returnType: "string | null" });
  });

  test("authIsAuthenticated", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authIsAuthenticated", returnType: "boolean" });
  });

  test("authLogin", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authLogin", returnType: "string" }, "", "");
  });

  test("authLogout", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authLogout", returnType: "void" });
  });

  test("authRefreshToken", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authRefreshToken", returnType: "string" });
  });

  test("authSetCurrentOrg", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authSetCurrentOrg", returnType: "void" }, "");
  });

  test("authSetOrganizations", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authSetOrganizations", returnType: "void" }, "");
  });

  test("authSwitchOrg", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "authSwitchOrg", returnType: "void" }, "");
  });
});
