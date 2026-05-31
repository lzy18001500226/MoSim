// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · loop_svc", () => {
  test("loopSvcAddRun", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcAddRun", returnType: "void" }, "");
  });

  test("loopSvcAppendRuns", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcAppendRuns", returnType: "void" }, "");
  });

  test("loopSvcClearRuns", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcClearRuns", returnType: "void" });
  });

  test("loopSvcCurrentLoopJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcCurrentLoopJson", returnType: "string" });
  });

  test("loopSvcGetLoopBySlugJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcGetLoopBySlugJson", returnType: "string" }, "");
  });

  test("loopSvcLoopsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcLoopsJson", returnType: "string" });
  });

  test("loopSvcRunsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcRunsJson", returnType: "string" });
  });

  test("loopSvcSetCurrentLoop", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcSetCurrentLoop", returnType: "void" }, "");
  });

  test("loopSvcSetLoops", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcSetLoops", returnType: "void" }, "");
  });

  test("loopSvcSetRuns", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcSetRuns", returnType: "void" }, "");
  });

  test("loopSvcUpdateLoopLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcUpdateLoopLocal", returnType: "void" }, "", "");
  });

  test("loopSvcUpdateRunStatus", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "loopSvcUpdateRunStatus", returnType: "void" }, 0, "");
  });
});
