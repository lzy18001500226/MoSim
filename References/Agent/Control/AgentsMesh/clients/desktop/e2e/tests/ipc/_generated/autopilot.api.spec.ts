// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · autopilot", () => {
  test("autopilotAddController", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotAddController", returnType: "void" }, "");
  });

  test("autopilotAddIteration", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotAddIteration", returnType: "void" }, "", "");
  });

  test("autopilotControllersJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotControllersJson", returnType: "string" });
  });

  test("autopilotCurrentControllerJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotCurrentControllerJson", returnType: "string" });
  });

  test("autopilotGetControllerByPodKeyJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotGetControllerByPodKeyJson", returnType: "string" }, "");
  });

  test("autopilotGetIterationsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotGetIterationsJson", returnType: "string" }, "");
  });

  test("autopilotGetThinkingHistoryJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotGetThinkingHistoryJson", returnType: "string" }, "");
  });

  test("autopilotGetThinkingJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotGetThinkingJson", returnType: "string" }, "");
  });

  test("autopilotRemoveController", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotRemoveController", returnType: "void" }, "");
  });

  test("autopilotSetControllers", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotSetControllers", returnType: "void" }, "");
  });

  test("autopilotSetCurrentController", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotSetCurrentController", returnType: "void" }, "");
  });

  test("autopilotSetIterations", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotSetIterations", returnType: "void" }, "", "");
  });

  test("autopilotUpdateController", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotUpdateController", returnType: "void" }, "", "");
  });

  test("autopilotUpdateThinking", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "autopilotUpdateThinking", returnType: "void" }, "", "");
  });
});
