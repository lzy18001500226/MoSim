// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · apikey", () => {
  test("apikeyCreateConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "apikeyCreateConnect", returnType: "any" });
  });

  test("apikeyDeleteConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "apikeyDeleteConnect", returnType: "any" });
  });

  test("apikeyGetConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "apikeyGetConnect", returnType: "any" });
  });

  test("apikeyListConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "apikeyListConnect", returnType: "any" });
  });

  test("apikeyRevokeConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "apikeyRevokeConnect", returnType: "any" });
  });

  test("apikeyUpdateConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "apikeyUpdateConnect", returnType: "any" });
  });
});
