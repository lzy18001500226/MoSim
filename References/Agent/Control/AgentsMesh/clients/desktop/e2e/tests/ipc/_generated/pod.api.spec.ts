// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · pod", () => {
  test("podCurrentPodJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "podCurrentPodJson", returnType: "string" });
  });

  test("podGetPodJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "podGetPodJson", returnType: "string" }, "");
  });

  test("podPodsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "podPodsJson", returnType: "string" });
  });

  test("podRemovePod", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "podRemovePod", returnType: "void" }, "");
  });

  test("podUpdateAgentStatus", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "podUpdateAgentStatus", returnType: "void" }, "", "");
  });

  test("podUpdatePodAlias", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "podUpdatePodAlias", returnType: "void" }, "", "");
  });

  test("podUpdatePodStatus", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "podUpdatePodStatus", returnType: "void" }, "", "", "", "", "", 0);
  });

  test("podUpdatePodTitle", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "podUpdatePodTitle", returnType: "void" }, "", "", 0);
  });
});
