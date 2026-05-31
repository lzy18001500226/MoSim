// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · runner", () => {
  test("runnerAuthorizeRunner", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerAuthorizeRunner", returnType: "string" }, "");
  });

  test("runnerAvailableRunnersJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerAvailableRunnersJson", returnType: "string" });
  });

  test("runnerCurrentRunnerJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerCurrentRunnerJson", returnType: "string" });
  });

  test("runnerGetAuthStatus", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerGetAuthStatus", returnType: "string" }, "");
  });

  test("runnerGetRunnerJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerGetRunnerJson", returnType: "string" }, 0);
  });

  test("runnerListRunnerPods", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerListRunnerPods", returnType: "string" }, 0, "", 0, 0);
  });

  test("runnerRemoveRunnerLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerRemoveRunnerLocal", returnType: "void" }, 0);
  });

  test("runnerRunnersJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerRunnersJson", returnType: "string" });
  });

  test("runnerSetAvailableRunners", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerSetAvailableRunners", returnType: "void" }, "");
  });

  test("runnerSetCurrentRunner", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerSetCurrentRunner", returnType: "void" }, "");
  });

  test("runnerSetRunners", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerSetRunners", returnType: "void" }, "");
  });

  test("runnerUpdateRunner", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerUpdateRunner", returnType: "string" }, 0, "");
  });

  test("runnerUpdateRunnerLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerUpdateRunnerLocal", returnType: "void" }, 0, "");
  });

  test("runnerUpdateRunnerStatus", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "runnerUpdateRunnerStatus", returnType: "void" }, 0, "");
  });
});
