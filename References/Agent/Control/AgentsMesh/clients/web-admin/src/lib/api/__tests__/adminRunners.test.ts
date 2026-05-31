import { describe, it, expect, vi, beforeEach } from "vitest";

const mockCallConnect = vi.fn();
vi.mock("@/lib/connect/transport", () => ({
  callConnect: (...args: unknown[]) => mockCallConnect(...args),
  ConnectError: class ConnectError extends Error {},
}));

import {
  listRunners,
  getRunner,
  disableRunner,
  enableRunner,
  deleteRunner,
} from "../adminRunners";

function fakeRunnerProto(id: number, overrides: Record<string, unknown> = {}) {
  return {
    id: BigInt(id),
    organizationId: 1n,
    nodeId: `node-${id}`,
    description: undefined,
    status: "online",
    isEnabled: true,
    runnerVersion: undefined,
    currentPods: 0,
    maxConcurrentPods: 5,
    availableAgents: [],
    hostInfoJson: undefined,
    lastHeartbeat: undefined,
    createdAt: "",
    updatedAt: "",
    organization: undefined,
    ...overrides,
  };
}

describe("Admin API - Runners (Connect-RPC)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("listRunners forwards org_id as BigInt + maps response", async () => {
    mockCallConnect.mockResolvedValue({
      items: [fakeRunnerProto(7)],
      total: 1n,
      page: 1,
      pageSize: 20,
      totalPages: 1,
    });
    const result = await listRunners({ org_id: 5 });
    expect(mockCallConnect).toHaveBeenCalledWith(
      "proto.admin.v1.AdminService",
      "ListRunners",
      expect.anything(),
      expect.anything(),
      expect.objectContaining({ orgId: 5n }),
    );
    expect(result.data[0].id).toBe(7);
    expect(result.total).toBe(1);
  });

  it("getRunner passes BigInt runnerId + decodes host_info_json", async () => {
    mockCallConnect.mockResolvedValue(
      fakeRunnerProto(3, { hostInfoJson: JSON.stringify({ os: "linux" }) }),
    );
    const r = await getRunner(3);
    expect(mockCallConnect).toHaveBeenCalledWith(
      "proto.admin.v1.AdminService",
      "GetRunner",
      expect.anything(),
      expect.anything(),
      { runnerId: 3n },
    );
    expect(r.id).toBe(3);
    expect(r.host_info).toEqual({ os: "linux" });
  });

  it("disableRunner calls DisableRunner procedure", async () => {
    mockCallConnect.mockResolvedValue(fakeRunnerProto(1, { isEnabled: false }));
    await disableRunner(1);
    expect(mockCallConnect).toHaveBeenCalledWith(
      "proto.admin.v1.AdminService",
      "DisableRunner",
      expect.anything(),
      expect.anything(),
      { runnerId: 1n },
    );
  });

  it("enableRunner calls EnableRunner procedure", async () => {
    mockCallConnect.mockResolvedValue(fakeRunnerProto(1));
    await enableRunner(1);
    expect(mockCallConnect).toHaveBeenCalledWith(
      "proto.admin.v1.AdminService",
      "EnableRunner",
      expect.anything(),
      expect.anything(),
      { runnerId: 1n },
    );
  });

  it("deleteRunner returns message envelope", async () => {
    mockCallConnect.mockResolvedValue({ message: "Runner deleted successfully" });
    const result = await deleteRunner(1);
    expect(mockCallConnect).toHaveBeenCalledWith(
      "proto.admin.v1.AdminService",
      "DeleteRunner",
      expect.anything(),
      expect.anything(),
      { runnerId: 1n },
    );
    expect(result.message).toContain("deleted");
  });
});
