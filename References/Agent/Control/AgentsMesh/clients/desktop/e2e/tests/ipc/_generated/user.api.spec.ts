// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · user", () => {
  test("userChangePasswordConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "userChangePasswordConnect", returnType: "Array<number>" }, []);
  });

  test("userDeleteIdentityConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "userDeleteIdentityConnect", returnType: "Array<number>" }, []);
  });

  test("userGetMeConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "userGetMeConnect", returnType: "Array<number>" }, []);
  });

  test("userListIdentitiesConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "userListIdentitiesConnect", returnType: "Array<number>" }, []);
  });

  test("userSearchUsersConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "userSearchUsersConnect", returnType: "Array<number>" }, []);
  });

  test("userUpdateMeConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "userUpdateMeConnect", returnType: "Array<number>" }, []);
  });
});
