import { renderHook, waitFor, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { useAsyncData, useAsyncDataAll } from "../useAsyncData";

describe("useAsyncData", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should fetch data on mount", async () => {
    const mockData = { id: 1, name: "Test" };
    const fetcher = vi.fn().mockResolvedValue(mockData);

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    // Initially loading
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe(null);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // After load
    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBe(null);
    expect(result.current.isLoaded).toBe(true);
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("should handle fetch error", async () => {
    const error = new Error("Fetch failed");
    const fetcher = vi.fn().mockRejectedValue(error);

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toEqual(error);
  });

  it("should refetch when dependencies change", async () => {
    const fetcher = vi.fn().mockImplementation((id: number) =>
      Promise.resolve({ id })
    );

    let userId = 1;
    const { result, rerender } = renderHook(() =>
      useAsyncData(() => fetcher(userId), [userId])
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetcher).toHaveBeenCalledWith(1);

    // Change dependency
    userId = 2;
    rerender();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetcher).toHaveBeenCalledWith(2);
    expect(fetcher).toHaveBeenCalledTimes(2);
  });

  it("should not fetch when enabled is false", async () => {
    const fetcher = vi.fn().mockResolvedValue({ data: "test" });

    const { result } = renderHook(() =>
      useAsyncData(fetcher, [], { enabled: false })
    );

    // Should not be loading when disabled
    expect(result.current.loading).toBe(false);
    expect(fetcher).not.toHaveBeenCalled();
  });

  it("should fetch when enabled becomes true", async () => {
    const fetcher = vi.fn().mockResolvedValue({ data: "test" });

    let enabled = false;
    const { result, rerender } = renderHook(() =>
      useAsyncData(fetcher, [], { enabled })
    );

    expect(fetcher).not.toHaveBeenCalled();

    enabled = true;
    rerender();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("should call onSuccess callback", async () => {
    const onSuccess = vi.fn();
    const fetcher = vi.fn().mockResolvedValue({ data: "test" });

    const { result } = renderHook(() =>
      useAsyncData(fetcher, [], { onSuccess })
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(onSuccess).toHaveBeenCalledTimes(1);
  });

  it("should call onError callback", async () => {
    const error = new Error("Test error");
    const onError = vi.fn();
    const fetcher = vi.fn().mockRejectedValue(error);

    const { result } = renderHook(() =>
      useAsyncData(fetcher, [], { onError })
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(onError).toHaveBeenCalledWith(error);
  });

  it("should allow manual refetch", async () => {
    const fetcher = vi.fn().mockResolvedValue({ count: 1 });

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(fetcher).toHaveBeenCalledTimes(1);

    // Manual refetch
    await act(async () => {
      await result.current.refetch();
    });

    expect(fetcher).toHaveBeenCalledTimes(2);
  });

  it("should allow setting data directly", async () => {
    const fetcher = vi.fn().mockResolvedValue({ value: "initial" });

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ value: "initial" });

    // Set data directly
    act(() => {
      result.current.setData({ value: "updated" });
    });

    expect(result.current.data).toEqual({ value: "updated" });
  });

  it("should allow clearing error", async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error("Test error"));

    const { result } = renderHook(() => useAsyncData(fetcher, []));

    await waitFor(() => {
      expect(result.current.error).not.toBe(null);
    });

    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBe(null);
  });

  it("should keep previous data when keepPreviousData is true", async () => {
    let callCount = 0;
    const fetcher = vi.fn().mockImplementation(() => {
      callCount++;
      return Promise.resolve({ count: callCount });
    });

    let trigger = 0;
    const { result, rerender } = renderHook(() =>
      useAsyncData(fetcher, [trigger], { keepPreviousData: true })
    );

    await waitFor(() => {
      expect(result.current.data).toEqual({ count: 1 });
    });

    // Trigger refetch
    trigger = 1;
    rerender();

    // During loading, previous data should be kept
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toEqual({ count: 1 });

    await waitFor(() => {
      expect(result.current.data).toEqual({ count: 2 });
    });
  });

  it("should handle race conditions", async () => {
    let resolveFirst: (value: { id: number }) => void;
    let resolveSecond: (value: { id: number }) => void;

    const firstPromise = new Promise<{ id: number }>((resolve) => {
      resolveFirst = resolve;
    });
    const secondPromise = new Promise<{ id: number }>((resolve) => {
      resolveSecond = resolve;
    });

    let callCount = 0;
    const fetcher = vi.fn().mockImplementation(() => {
      callCount++;
      return callCount === 1 ? firstPromise : secondPromise;
    });

    let trigger = 0;
    const { result, rerender } = renderHook(() =>
      useAsyncData(fetcher, [trigger])
    );

    // Trigger second fetch before first completes
    trigger = 1;
    rerender();

    // Resolve second first
    resolveSecond!({ id: 2 });
    await waitFor(() => {
      expect(result.current.data).toEqual({ id: 2 });
    });

    // Resolve first after second (should be ignored)
    resolveFirst!({ id: 1 });

    // Data should still be from second fetch
    expect(result.current.data).toEqual({ id: 2 });
  });
});

describe("useAsyncDataAll", () => {
  it("should fetch multiple data sources in parallel", async () => {
    const usersData = [{ id: 1, name: "User" }];
    const postsData = [{ id: 1, title: "Post" }];

    const fetchers = {
      users: vi.fn().mockResolvedValue(usersData),
      posts: vi.fn().mockResolvedValue(postsData),
    };

    const { result } = renderHook(() => useAsyncDataAll(fetchers, []));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({
      users: usersData,
      posts: postsData,
    });
    expect(fetchers.users).toHaveBeenCalledTimes(1);
    expect(fetchers.posts).toHaveBeenCalledTimes(1);
  });

  it("should handle error in one of the fetchers", async () => {
    const error = new Error("Posts fetch failed");

    const fetchers = {
      users: vi.fn().mockResolvedValue([{ id: 1 }]),
      posts: vi.fn().mockRejectedValue(error),
    };

    const { result } = renderHook(() => useAsyncDataAll(fetchers, []));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toEqual(error);
    expect(result.current.data).toBe(null);
  });
});
