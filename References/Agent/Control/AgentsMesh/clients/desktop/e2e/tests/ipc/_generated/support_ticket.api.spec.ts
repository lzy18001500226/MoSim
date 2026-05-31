// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · support_ticket", () => {
  test("supportTicketAddSupportTicketMessageConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "supportTicketAddSupportTicketMessageConnect", returnType: "any" });
  });

  test("supportTicketAssociateAttachmentsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "supportTicketAssociateAttachmentsConnect", returnType: "any" });
  });

  test("supportTicketCreateSupportTicketConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "supportTicketCreateSupportTicketConnect", returnType: "any" });
  });

  test("supportTicketGetAttachmentUrlConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "supportTicketGetAttachmentUrlConnect", returnType: "Array<number>" }, []);
  });

  test("supportTicketGetSupportTicketConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "supportTicketGetSupportTicketConnect", returnType: "Array<number>" }, []);
  });

  test("supportTicketListSupportTicketsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "supportTicketListSupportTicketsConnect", returnType: "Array<number>" }, []);
  });

  test("supportTicketPresignAttachmentUploadConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "supportTicketPresignAttachmentUploadConnect", returnType: "any" });
  });
});
