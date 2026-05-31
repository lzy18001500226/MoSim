// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · mesh", () => {
  test("meshBatchGetTicketPodsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshBatchGetTicketPodsConnect", returnType: "any" });
  });

  test("meshClearTopology", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshClearTopology", returnType: "void" });
  });

  test("meshCreatePodForTicketConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshCreatePodForTicketConnect", returnType: "any" });
  });

  test("meshFetchTopology", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshFetchTopology", returnType: "string" });
  });

  test("meshGetActiveNodesJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshGetActiveNodesJson", returnType: "string" });
  });

  test("meshGetChannelsForNodeJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshGetChannelsForNodeJson", returnType: "string" }, "");
  });

  test("meshGetEdgesForNodeJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshGetEdgesForNodeJson", returnType: "string" }, "");
  });

  test("meshGetMeshTopologyConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshGetMeshTopologyConnect", returnType: "any" });
  });

  test("meshGetNodeJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshGetNodeJson", returnType: "string" }, "");
  });

  test("meshGetNodesByRunnerJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshGetNodesByRunnerJson", returnType: "string" }, 0);
  });

  test("meshGetRunnerInfoJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshGetRunnerInfoJson", returnType: "string" }, 0);
  });

  test("meshGetTicketPodsConnect", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshGetTicketPodsConnect", returnType: "any" });
  });

  test("meshSelectedNode", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshSelectedNode", returnType: "string" });
  });

  test("meshSelectNode", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshSelectNode", returnType: "void" }, "");
  });

  test("meshTopologyJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "meshTopologyJson", returnType: "string" });
  });
});
