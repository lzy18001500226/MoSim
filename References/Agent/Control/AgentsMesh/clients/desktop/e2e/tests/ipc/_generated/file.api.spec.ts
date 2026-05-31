// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · file", () => {
  test("fileUploadFile", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "fileUploadFile", returnType: "string" }, [], "", "");
  });
});
