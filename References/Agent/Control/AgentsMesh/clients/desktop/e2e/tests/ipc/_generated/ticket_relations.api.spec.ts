// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · ticket_relations", () => {
  test("ticketRelationsCreateCommentConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsCreateCommentConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsCreateRelationConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsCreateRelationConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsDeleteCommentConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsDeleteCommentConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsDeleteRelationConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsDeleteRelationConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsLinkCommitConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsLinkCommitConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsListCommentsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsListCommentsConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsListCommitsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsListCommitsConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsListMergeRequestsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsListMergeRequestsConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsListRelationsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsListRelationsConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsUnlinkCommitConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsUnlinkCommitConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRelationsUpdateCommentConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRelationsUpdateCommentConnect", returnType: "Array<number>" }, []);
  });
});
