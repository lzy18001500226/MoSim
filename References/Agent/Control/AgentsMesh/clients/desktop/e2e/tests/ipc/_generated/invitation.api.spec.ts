// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · invitation", () => {
  test("invitationAcceptInvitationConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "invitationAcceptInvitationConnect", returnType: "Array<number>" }, []);
  });

  test("invitationCreateInvitationConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "invitationCreateInvitationConnect", returnType: "Array<number>" }, []);
  });

  test("invitationGetInvitationByTokenConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "invitationGetInvitationByTokenConnect", returnType: "Array<number>" }, []);
  });

  test("invitationListInvitationsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "invitationListInvitationsConnect", returnType: "Array<number>" }, []);
  });

  test("invitationListPendingInvitationsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "invitationListPendingInvitationsConnect", returnType: "Array<number>" }, []);
  });

  test("invitationResendInvitationConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "invitationResendInvitationConnect", returnType: "Array<number>" }, []);
  });

  test("invitationRevokeInvitationConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "invitationRevokeInvitationConnect", returnType: "Array<number>" }, []);
  });
});
