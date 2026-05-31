import { describe, it, expect, beforeEach, vi } from "vitest";
import { act } from "@testing-library/react";

const orgSlug = "test-org";

vi.mock("@/stores/auth", async () => {
  const actual = await vi.importActual<typeof import("@/stores/auth")>("@/stores/auth");
  return {
    ...actual,
    readCurrentOrg: () => ({ id: 1, slug: orgSlug, name: "Test Org" }),
  };
});

const mocks = vi.hoisted(() => ({
  listChannels: vi.fn(),
  getChannel: vi.fn(),
  createChannel: vi.fn(),
  updateChannel: vi.fn(),
  archiveChannel: vi.fn(),
  unarchiveChannel: vi.fn(),
  joinChannelPod: vi.fn(),
  leaveChannelPod: vi.fn(),
  inviteChannelMembers: vi.fn(),
  listChannelMembers: vi.fn(),
  joinChannelConnect: vi.fn(),
  leaveChannelConnect: vi.fn(),
}));

vi.mock("@/lib/api/facade/channelConnect", () => ({
  listChannels: mocks.listChannels,
  getChannel: mocks.getChannel,
  createChannel: mocks.createChannel,
  updateChannel: mocks.updateChannel,
  archiveChannel: mocks.archiveChannel,
  unarchiveChannel: mocks.unarchiveChannel,
  joinChannelPod: mocks.joinChannelPod,
  leaveChannelPod: mocks.leaveChannelPod,
  inviteChannelMembers: mocks.inviteChannelMembers,
  listChannelMembers: mocks.listChannelMembers,
  joinChannel: mocks.joinChannelConnect,
  leaveChannel: mocks.leaveChannelConnect,
}));

import { useChannelStore, useChannelMessageStore, Channel } from "../channel";
import { getChannelService } from "@/lib/wasm-core";

const svc = () => getChannelService();
const getChannels = (): Channel[] => JSON.parse(svc().channels_json());
const getCurrentChannel = (): Channel | null => {
  const v = svc().current_channel_json();
  return v ? (typeof v === "string" ? JSON.parse(v) : v) : null;
};

const mockChannel: Channel = {
  id: 1, name: "general", description: "General discussion channel",
  visibility: "public", is_archived: false, is_member: true, member_count: 1,
  organization_id: 1, created_at: "2024-01-01T00:00:00Z", updated_at: "2024-01-01T00:00:00Z",
};
const mockChannel2: Channel = {
  id: 2, name: "dev-chat", description: "Development discussion",
  visibility: "public", is_archived: false, is_member: true, member_count: 1,
  organization_id: 1, created_at: "2024-01-02T00:00:00Z", updated_at: "2024-01-02T00:00:00Z",
};

describe("Channel Store (Connect adapter)", () => {
  const seedChannels = (channels: Channel[], currentChannel: Channel | null = null) => {
    svc().set_channels(JSON.stringify(channels));
    if (currentChannel) svc().set_current_channel(BigInt(currentChannel.id));
  };

  beforeEach(() => {
    vi.clearAllMocks();
    Object.values(mocks).forEach((m) => m.mockReset());
    useChannelStore.setState({
      _tick: 0, loading: false, channelLoading: false, error: null,
      selectedChannelId: null, searchQuery: "", showArchived: false, currentChannel: null,
    });
    useChannelMessageStore.setState({ cache: {}, _unreadTick: 0 });
  });

  describe("initial state", () => {
    it("should have default values", () => {
      const state = useChannelStore.getState();
      expect(getChannels()).toEqual([]);
      expect(getCurrentChannel()).toBeNull();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe("fetchChannels", () => {
    it("should fetch channels successfully", async () => {
      mocks.listChannels.mockResolvedValue({
        items: [mockChannel, mockChannel2], total: 2, limit: 0, offset: 0,
      });
      await act(async () => { await useChannelStore.getState().fetchChannels(); });
      expect(mocks.listChannels).toHaveBeenCalledWith(orgSlug, { includeArchived: undefined });
      expect(getChannels()).toHaveLength(2);
      expect(getChannels()[0].name).toBe("general");
    });

    it("should pass filters to service", async () => {
      mocks.listChannels.mockResolvedValue({ items: [], total: 0, limit: 0, offset: 0 });
      await act(async () => { await useChannelStore.getState().fetchChannels({ includeArchived: true }); });
      expect(mocks.listChannels).toHaveBeenCalledWith(orgSlug, { includeArchived: true });
    });

    it("should handle fetch error", async () => {
      mocks.listChannels.mockRejectedValue(new Error("Network error"));
      await act(async () => { await useChannelStore.getState().fetchChannels(); });
      expect(useChannelStore.getState().error).toBe("Network error");
    });
  });

  describe("fetchChannel", () => {
    it("should fetch single channel", async () => {
      seedChannels([mockChannel]);
      mocks.getChannel.mockResolvedValue(mockChannel);
      await act(async () => { await useChannelStore.getState().fetchChannel(1); });
      expect(mocks.getChannel).toHaveBeenCalledWith(orgSlug, 1);
    });

    it("should handle error", async () => {
      mocks.getChannel.mockRejectedValue({ message: "Channel not found" });
      await act(async () => { await useChannelStore.getState().fetchChannel(999); });
      expect(useChannelStore.getState().error).toBe("Channel not found");
    });
  });

  describe("createChannel", () => {
    it("should create and add to list", async () => {
      mocks.createChannel.mockResolvedValue(mockChannel);
      let result: Channel;
      await act(async () => {
        result = await useChannelStore.getState().createChannel({ name: "general", description: "General discussion channel" });
      });
      expect(result!).toEqual(mockChannel);
      expect(getChannels()).toContainEqual(mockChannel);
    });

    it("should convert camelCase to snake_case", async () => {
      mocks.createChannel.mockResolvedValue(mockChannel);
      await act(async () => {
        await useChannelStore.getState().createChannel({ name: "test", repositoryId: 1, ticketSlug: "PROJ-2" });
      });
      expect(mocks.createChannel).toHaveBeenCalledWith(orgSlug, {
        name: "test", description: undefined, document: undefined,
        repository_id: 1, ticket_slug: "PROJ-2", visibility: undefined, member_ids: undefined,
      });
    });

    it("should handle error", async () => {
      mocks.createChannel.mockRejectedValue(new Error("Create failed"));
      await expect(act(async () => { await useChannelStore.getState().createChannel({ name: "test" }); })).rejects.toThrow("Create failed");
    });
  });

  describe("updateChannel", () => {
    beforeEach(() => { seedChannels([mockChannel], mockChannel); });

    it("should update channel and currentChannel", async () => {
      const updated = { ...mockChannel, name: "updated" };
      mocks.updateChannel.mockResolvedValue(updated);
      await act(async () => { await useChannelStore.getState().updateChannel(1, { name: "updated" }); });
      expect(getChannels()[0].name).toBe("updated");
      expect(getCurrentChannel()?.name).toBe("updated");
    });

    it("should not update currentChannel if different id", async () => {
      const updated = { ...mockChannel2, name: "updated-dev" };
      mocks.updateChannel.mockResolvedValue(updated);
      seedChannels([mockChannel, mockChannel2], mockChannel);
      await act(async () => { await useChannelStore.getState().updateChannel(2, { name: "updated-dev" }); });
      expect(getCurrentChannel()?.name).toBe("general");
    });
  });

  describe("archive/unarchive", () => {
    it("should archive", async () => {
      seedChannels([mockChannel], mockChannel);
      mocks.archiveChannel.mockResolvedValue("ok");
      await act(async () => { await useChannelStore.getState().archiveChannel(1); });
      expect(getChannels()[0].is_archived).toBe(true);
    });

    it("should unarchive", async () => {
      const archived = { ...mockChannel, is_archived: true };
      seedChannels([archived], archived);
      mocks.unarchiveChannel.mockResolvedValue("ok");
      await act(async () => { await useChannelStore.getState().unarchiveChannel(1); });
      expect(getChannels()[0].is_archived).toBe(false);
    });
  });

  describe("join/leave channel", () => {
    it("should join and refresh", async () => {
      seedChannels([mockChannel], mockChannel);
      const updated = { ...mockChannel, pods: [{ pod_key: "pod-123", status: "running" }] };
      mocks.joinChannelPod.mockResolvedValue(undefined);
      mocks.getChannel.mockResolvedValue(updated);
      await act(async () => { await useChannelStore.getState().joinChannel(1, "pod-123"); });
      expect(mocks.joinChannelPod).toHaveBeenCalledWith(orgSlug, 1, "pod-123");
      expect(getChannels()[0].pods).toHaveLength(1);
    });

    it("should leave and refresh", async () => {
      seedChannels([{ ...mockChannel, pods: [{ pod_key: "pod-123", status: "running" }] }], mockChannel);
      const updated = { ...mockChannel, pods: [] };
      mocks.leaveChannelPod.mockResolvedValue(undefined);
      mocks.getChannel.mockResolvedValue(updated);
      await act(async () => { await useChannelStore.getState().leaveChannel(1, "pod-123"); });
      expect(mocks.leaveChannelPod).toHaveBeenCalledWith(orgSlug, 1, "pod-123");
      expect(getChannels()[0].pods).toHaveLength(0);
    });
  });

  describe("setCurrentChannel", () => {
    it("should set and clear", () => {
      svc().set_channels(JSON.stringify([mockChannel]));
      act(() => { useChannelStore.getState().setCurrentChannel(mockChannel); });
      expect(getCurrentChannel()).toEqual(mockChannel);
      act(() => { useChannelStore.getState().setCurrentChannel(null); });
      expect(getCurrentChannel()).toBeNull();
    });

    it("should not affect per-channel message cache", () => {
      useChannelMessageStore.setState({
        cache: { 1: { loading: false, loadingMore: false, error: "keep-me" } },
      });
      act(() => { useChannelStore.getState().setCurrentChannel(mockChannel); });
      expect(useChannelMessageStore.getState().cache[1]?.error).toBe("keep-me");
    });
  });

  describe("clearError", () => {
    it("should clear", () => {
      useChannelStore.setState({ error: "err" });
      act(() => { useChannelStore.getState().clearError(); });
      expect(useChannelStore.getState().error).toBeNull();
    });
  });
});
