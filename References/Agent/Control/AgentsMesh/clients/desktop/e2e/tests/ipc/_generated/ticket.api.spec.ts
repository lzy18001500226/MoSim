// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · ticket", () => {
  test("ticketAddAssigneeConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketAddAssigneeConnect", returnType: "Array<number>" }, []);
  });

  test("ticketAddLabel", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketAddLabel", returnType: "void" }, "");
  });

  test("ticketAddLabelConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketAddLabelConnect", returnType: "Array<number>" }, []);
  });

  test("ticketAddTicket", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketAddTicket", returnType: "void" }, "");
  });

  test("ticketAppendColumnTickets", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketAppendColumnTickets", returnType: "void" }, "", "");
  });

  test("ticketBoardColumnsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketBoardColumnsJson", returnType: "string" });
  });

  test("ticketCreateLabelConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketCreateLabelConnect", returnType: "Array<number>" }, []);
  });

  test("ticketCreateTicketConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketCreateTicketConnect", returnType: "Array<number>" }, []);
  });

  test("ticketCurrentTicketJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketCurrentTicketJson", returnType: "string" });
  });

  test("ticketDeleteLabelConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketDeleteLabelConnect", returnType: "Array<number>" }, []);
  });

  test("ticketDeleteTicketConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketDeleteTicketConnect", returnType: "Array<number>" }, []);
  });

  test("ticketFilterTicketsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketFilterTicketsJson", returnType: "string" }, "", "", "", "");
  });

  test("ticketGetActiveTicketsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketGetActiveTicketsConnect", returnType: "Array<number>" }, []);
  });

  test("ticketGetBoardConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketGetBoardConnect", returnType: "Array<number>" }, []);
  });

  test("ticketGetSubTicketsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketGetSubTicketsConnect", returnType: "Array<number>" }, []);
  });

  test("ticketGetTicketBySlugJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketGetTicketBySlugJson", returnType: "string" }, "");
  });

  test("ticketGetTicketConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketGetTicketConnect", returnType: "Array<number>" }, []);
  });

  test("ticketGetTicketPods", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketGetTicketPods", returnType: "string" }, "", false);
  });

  test("ticketLabelsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketLabelsJson", returnType: "string" });
  });

  test("ticketListLabelsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketListLabelsConnect", returnType: "Array<number>" }, []);
  });

  test("ticketListTicketsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketListTicketsConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRemoveAssigneeConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRemoveAssigneeConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRemoveLabel", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRemoveLabel", returnType: "void" }, 0);
  });

  test("ticketRemoveLabelConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRemoveLabelConnect", returnType: "Array<number>" }, []);
  });

  test("ticketRemoveTicket", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketRemoveTicket", returnType: "void" }, "");
  });

  test("ticketSetBoardColumns", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketSetBoardColumns", returnType: "void" }, "");
  });

  test("ticketSetCurrentTicket", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketSetCurrentTicket", returnType: "void" }, "");
  });

  test("ticketSetLabels", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketSetLabels", returnType: "void" }, "");
  });

  test("ticketSetTickets", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketSetTickets", returnType: "void" }, "");
  });

  test("ticketTicketPodsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketTicketPodsJson", returnType: "string" }, "");
  });

  test("ticketTicketsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketTicketsJson", returnType: "string" });
  });

  test("ticketUpdateLabelConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketUpdateLabelConnect", returnType: "Array<number>" }, []);
  });

  test("ticketUpdateTicketConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketUpdateTicketConnect", returnType: "Array<number>" }, []);
  });

  test("ticketUpdateTicketLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketUpdateTicketLocal", returnType: "void" }, "", "");
  });

  test("ticketUpdateTicketStatusConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketUpdateTicketStatusConnect", returnType: "Array<number>" }, []);
  });

  test("ticketUpdateTicketStatusLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "ticketUpdateTicketStatusLocal", returnType: "void" }, "", "");
  });
});
