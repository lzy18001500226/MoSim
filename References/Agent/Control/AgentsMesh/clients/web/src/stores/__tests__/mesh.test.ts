import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { act } from "@testing-library/react";

const mockFetchTopology = vi.fn();
const mockSelectNode = vi.fn();
const mockSelectedNode = vi.fn();
const mockGetNodeJson = vi.fn();
const mockGetEdgesForNodeJson = vi.fn();
const mockGetChannelsForNodeJson = vi.fn();
const mockGetActiveNodesJson = vi.fn();
const mockGetNodesByRunnerJson = vi.fn();
const mockGetRunnerInfoJson = vi.fn();

const noopSvc = new Proxy({}, {
  get: () => () => "[]",
});

vi.mock("@/lib/wasm-core", () => ({
  getMeshService: () => ({
    fetch_topology: mockFetchTopology,
    select_node: mockSelectNode,
    selected_node: mockSelectedNode,
    get_node_json: mockGetNodeJson,
    get_edges_for_node_json: mockGetEdgesForNodeJson,
    get_channels_for_node_json: mockGetChannelsForNodeJson,
    get_active_nodes_json: mockGetActiveNodesJson,
    get_nodes_by_runner_json: mockGetNodesByRunnerJson,
    get_runner_info_json: mockGetRunnerInfoJson,
  }),
  getChannelService: () => noopSvc,
}));

import {
  useMeshStore,
  MeshTopology,
  MeshNode,
  MeshEdge,
  ChannelInfo,
} from "../mesh";

const mockNode1: MeshNode = {
  pod_key: "pod-abc",
  status: "running",
  agent_status: "executing",
  agent_slug: "claude-code",
  runner_id: 1,
};

const mockNode2: MeshNode = {
  pod_key: "pod-def",
  status: "running",
  agent_status: "waiting",
  agent_slug: "gpt-engineer",
  runner_id: 2,
};

const mockNode3: MeshNode = {
  pod_key: "pod-ghi",
  status: "terminated",
  agent_status: "idle",
  agent_slug: "claude-code",
  runner_id: 3,
};

const mockEdge: MeshEdge = {
  source: "pod-abc",
  target: "pod-def",
  binding_status: "active",
};

const mockChannel: ChannelInfo = {
  id: 1,
  name: "general",
  pod_keys: ["pod-abc", "pod-def"],
};

const mockTopology: MeshTopology = {
  nodes: [mockNode1, mockNode2, mockNode3],
  edges: [mockEdge],
  channels: [mockChannel],
  runners: [],
};

describe("Mesh Store", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useMeshStore.setState({
      _tick: 0,
      selectedNode: null,
      selectedChannel: null,
      loading: false,
      error: null,
      nodePositions: {},
    });
  });

  describe("initial state", () => {
    it("should have default values", () => {
      const state = useMeshStore.getState();

      expect(state.selectedNode).toBeNull();
      expect(state.selectedChannel).toBeNull();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.nodePositions).toEqual({});
    });
  });

  describe("fetchTopology", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it("should fetch topology successfully", async () => {
      mockFetchTopology.mockResolvedValue(undefined);

      act(() => {
        useMeshStore.getState().fetchTopology();
      });
      await act(async () => {
        vi.advanceTimersByTime(500);
      });

      const state = useMeshStore.getState();
      expect(mockFetchTopology).toHaveBeenCalled();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });

    it("should handle fetch error", async () => {
      mockFetchTopology.mockRejectedValue(new Error("Network error"));

      act(() => {
        useMeshStore.getState().fetchTopology();
      });
      await act(async () => {
        vi.advanceTimersByTime(500);
      });

      const state = useMeshStore.getState();
      expect(state.error).toBe("Network error");
      expect(state.loading).toBe(false);
    });

    it("should handle non-Error rejection", async () => {
      mockFetchTopology.mockRejectedValue("Unknown error");

      act(() => {
        useMeshStore.getState().fetchTopology();
      });
      await act(async () => {
        vi.advanceTimersByTime(500);
      });

      const state = useMeshStore.getState();
      expect(state.error).toBe("Failed to fetch topology");
    });
  });

  describe("selectNode", () => {
    it("should select a node", () => {
      mockSelectedNode.mockReturnValue("pod-abc");

      act(() => {
        useMeshStore.getState().selectNode("pod-abc");
      });

      expect(mockSelectNode).toHaveBeenCalledWith("pod-abc");
      const state = useMeshStore.getState();
      expect(state.selectedNode).toBe("pod-abc");
    });

    it("should clear selectedChannel when selecting node", () => {
      useMeshStore.setState({ selectedChannel: 1 });
      mockSelectedNode.mockReturnValue("pod-abc");

      act(() => {
        useMeshStore.getState().selectNode("pod-abc");
      });

      const state = useMeshStore.getState();
      expect(state.selectedNode).toBe("pod-abc");
      expect(state.selectedChannel).toBeNull();
    });

    it("should set to null", () => {
      useMeshStore.setState({ selectedNode: "pod-abc" });
      mockSelectedNode.mockReturnValue(null);

      act(() => {
        useMeshStore.getState().selectNode(null);
      });

      expect(mockSelectNode).toHaveBeenCalledWith(undefined);
      const state = useMeshStore.getState();
      expect(state.selectedNode).toBeNull();
    });
  });

  describe("selectChannel", () => {
    it("should select a channel", () => {
      act(() => {
        useMeshStore.getState().selectChannel(1);
      });

      const state = useMeshStore.getState();
      expect(state.selectedChannel).toBe(1);
    });

    it("should clear selectedNode when selecting channel", () => {
      useMeshStore.setState({ selectedNode: "pod-abc" });

      act(() => {
        useMeshStore.getState().selectChannel(1);
      });

      const state = useMeshStore.getState();
      expect(state.selectedChannel).toBe(1);
      expect(state.selectedNode).toBeNull();
    });

    it("should set to null", () => {
      useMeshStore.setState({ selectedChannel: 1 });

      act(() => {
        useMeshStore.getState().selectChannel(null);
      });

      const state = useMeshStore.getState();
      expect(state.selectedChannel).toBeNull();
    });
  });

  describe("updateNodePosition", () => {
    it("should save position for a node", () => {
      act(() => {
        useMeshStore.getState().updateNodePosition("runner-group-1", { x: 100, y: 200 });
      });

      const state = useMeshStore.getState();
      expect(state.nodePositions["runner-group-1"]).toEqual({ x: 100, y: 200 });
    });

    it("should update position for an existing node", () => {
      useMeshStore.setState({
        nodePositions: { "runner-group-1": { x: 50, y: 50 } },
      });

      act(() => {
        useMeshStore.getState().updateNodePosition("runner-group-1", { x: 300, y: 400 });
      });

      const state = useMeshStore.getState();
      expect(state.nodePositions["runner-group-1"]).toEqual({ x: 300, y: 400 });
    });

    it("should preserve positions of other nodes", () => {
      useMeshStore.setState({
        nodePositions: { "runner-group-1": { x: 10, y: 20 } },
      });

      act(() => {
        useMeshStore.getState().updateNodePosition("runner-group-2", { x: 500, y: 0 });
      });

      const state = useMeshStore.getState();
      expect(state.nodePositions["runner-group-1"]).toEqual({ x: 10, y: 20 });
      expect(state.nodePositions["runner-group-2"]).toEqual({ x: 500, y: 0 });
    });
  });

  describe("clearError", () => {
    it("should clear error", () => {
      useMeshStore.setState({ error: "Some error" });

      act(() => {
        useMeshStore.getState().clearError();
      });

      expect(useMeshStore.getState().error).toBeNull();
    });
  });

  describe("WASM state reader helpers", () => {
    it("getNodeByKey returns parsed node", () => {
      mockGetNodeJson.mockReturnValue(JSON.stringify(mockNode1));
      const result = useMeshStore.getState().getNodeByKey("pod-abc");
      expect(result).toEqual(mockNode1);
    });

    it("getNodeByKey returns undefined for missing node", () => {
      mockGetNodeJson.mockReturnValue(null);
      const result = useMeshStore.getState().getNodeByKey("missing");
      expect(result).toBeUndefined();
    });

    it("getEdgesForNode returns parsed edges", () => {
      mockGetEdgesForNodeJson.mockReturnValue(JSON.stringify([mockEdge]));
      const result = useMeshStore.getState().getEdgesForNode("pod-abc");
      expect(result).toEqual([mockEdge]);
    });

    it("getChannelsForNode returns parsed channels", () => {
      mockGetChannelsForNodeJson.mockReturnValue(JSON.stringify([mockChannel]));
      const result = useMeshStore.getState().getChannelsForNode("pod-abc");
      expect(result).toEqual([mockChannel]);
    });

    it("getActiveNodes returns parsed active nodes", () => {
      mockGetActiveNodesJson.mockReturnValue(JSON.stringify([mockNode1, mockNode2]));
      const result = useMeshStore.getState().getActiveNodes();
      expect(result).toEqual([mockNode1, mockNode2]);
    });

    it("getNodesByRunner returns parsed nodes", () => {
      mockGetNodesByRunnerJson.mockReturnValue(JSON.stringify([mockNode1]));
      const result = useMeshStore.getState().getNodesByRunner(1);
      expect(mockGetNodesByRunnerJson).toHaveBeenCalledWith(BigInt(1));
      expect(result).toEqual([mockNode1]);
    });

    it("getRunnerInfo returns parsed runner info", () => {
      const runner = { id: 1, name: "r1", status: "online", pod_keys: ["pod-abc"] };
      mockGetRunnerInfoJson.mockReturnValue(JSON.stringify(runner));
      const result = useMeshStore.getState().getRunnerInfo(1);
      expect(mockGetRunnerInfoJson).toHaveBeenCalledWith(BigInt(1));
      expect(result).toEqual(runner);
    });

    it("getRunnerInfo returns undefined for missing runner", () => {
      mockGetRunnerInfoJson.mockReturnValue(null);
      const result = useMeshStore.getState().getRunnerInfo(999);
      expect(result).toBeUndefined();
    });
  });
});
