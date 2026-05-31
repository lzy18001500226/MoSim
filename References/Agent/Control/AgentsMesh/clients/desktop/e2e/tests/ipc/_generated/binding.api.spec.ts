// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · binding", () => {
  test("bindingAcceptBindingConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingAcceptBindingConnect", returnType: "any" });
  });

  test("bindingApproveScopesConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingApproveScopesConnect", returnType: "any" });
  });

  test("bindingCheckBindingConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingCheckBindingConnect", returnType: "any" });
  });

  test("bindingGetBoundPodsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingGetBoundPodsConnect", returnType: "any" });
  });

  test("bindingGetPendingBindingsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingGetPendingBindingsConnect", returnType: "any" });
  });

  test("bindingListBindingsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingListBindingsConnect", returnType: "any" });
  });

  test("bindingRejectBindingConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingRejectBindingConnect", returnType: "any" });
  });

  test("bindingRequestBindingConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingRequestBindingConnect", returnType: "any" });
  });

  test("bindingRequestScopesConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingRequestScopesConnect", returnType: "any" });
  });

  test("bindingUnbindConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "bindingUnbindConnect", returnType: "any" });
  });
});
