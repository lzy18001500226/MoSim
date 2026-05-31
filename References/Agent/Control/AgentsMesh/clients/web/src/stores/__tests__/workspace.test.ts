import { describe, it, expect, beforeEach } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { useWorkspaceStore } from "../workspace";

describe("Workspace Store", () => {
  beforeEach(() => {
    localStorage.clear();
    useWorkspaceStore.setState({
      panes: [],
      activePane: null,
      splitTree: null,
      mobileActiveIndex: 0,
      terminalFontSize: 14,
      _hasHydrated: false,
    });
  });

  describe("initial state", () => {
    it("should have default values", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      expect(result.current.panes).toEqual([]);
      expect(result.current.activePane).toBeNull();
      expect(result.current.splitTree).toBeNull();
      expect(result.current.mobileActiveIndex).toBe(0);
      expect(result.current.terminalFontSize).toBe(14);
    });
  });

  describe("panes management", () => {
    it("should add a new pane", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let paneId: string;
      act(() => {
        paneId = result.current.addPane("pod-123");
      });

      expect(result.current.panes).toHaveLength(1);
      expect(result.current.panes[0].podKey).toBe("pod-123");
      expect(result.current.activePane).toBe(paneId!);
    });

    it("should add a new pane with podKey", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-123");
      });

      expect(result.current.panes[0].podKey).toBe("pod-123");
    });

    it("should create a split tree leaf for first pane", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-123");
      });

      expect(result.current.splitTree).not.toBeNull();
      expect(result.current.splitTree!.type).toBe("leaf");
    });

    it("should create a split node when adding second pane", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-1");
        result.current.addPane("pod-2");
      });

      expect(result.current.splitTree).not.toBeNull();
      expect(result.current.splitTree!.type).toBe("split");
      if (result.current.splitTree!.type === "split") {
        expect(result.current.splitTree!.direction).toBe("horizontal");
        expect(result.current.splitTree!.children).toHaveLength(2);
      }
    });

    it("should add third pane to same group with even sizes", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-1");
        result.current.addPane("pod-2");
        result.current.addPane("pod-3");
      });

      expect(result.current.panes).toHaveLength(3);
      const tree = result.current.splitTree;
      expect(tree).not.toBeNull();
      expect(tree!.type).toBe("split");
      if (tree!.type === "split") {
        expect(tree!.children).toHaveLength(3);
        const evenSize = 100 / 3;
        tree!.sizes.forEach((s) => expect(s).toBeCloseTo(evenSize, 1));
      }
    });

    it("should return existing pane id if pod already open", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let firstId: string;
      let secondId: string;
      act(() => {
        firstId = result.current.addPane("pod-123");
        secondId = result.current.addPane("pod-123");
      });

      expect(firstId!).toBe(secondId!);
      expect(result.current.panes).toHaveLength(1);
    });

    it("should remove a pane", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let paneId: string;
      act(() => {
        paneId = result.current.addPane("pod-123");
      });

      expect(result.current.panes).toHaveLength(1);

      act(() => {
        result.current.removePane(paneId!);
      });

      expect(result.current.panes).toHaveLength(0);
      expect(result.current.activePane).toBeNull();
      expect(result.current.splitTree).toBeNull();
    });

    it("should set next pane as active when active pane is removed", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let firstId: string;
      act(() => {
        firstId = result.current.addPane("pod-1");
        result.current.addPane("pod-2");
      });

      expect(result.current.panes).toHaveLength(2);
      expect(result.current.activePane).toBe(result.current.panes[1].id);

      act(() => {
        result.current.removePane(result.current.panes[1].id);
      });

      expect(result.current.panes).toHaveLength(1);
      expect(result.current.activePane).toBe(firstId!);
    });

    it("should clear all panes", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-1");
        result.current.addPane("pod-2");
        result.current.addPane("pod-3");
      });

      expect(result.current.panes).toHaveLength(3);

      act(() => {
        result.current.clearAllPanes();
      });

      expect(result.current.panes).toHaveLength(0);
      expect(result.current.activePane).toBeNull();
      expect(result.current.mobileActiveIndex).toBe(0);
      expect(result.current.splitTree).toBeNull();
    });
  });

  describe("active pane", () => {
    it("should set active pane", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let firstId: string;
      act(() => {
        firstId = result.current.addPane("pod-1");
        result.current.addPane("pod-2");
      });

      act(() => {
        result.current.setActivePane(firstId!);
      });

      expect(result.current.activePane).toBe(firstId!);
    });

    it("should set active pane to null", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-1");
        result.current.setActivePane(null);
      });

      expect(result.current.activePane).toBeNull();
    });
  });

  describe("split tree", () => {
    it("should split pane horizontally", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let paneId: string;
      act(() => {
        paneId = result.current.addPane("pod-1");
      });

      act(() => {
        result.current.splitPane(paneId!, "horizontal", "pod-2");
      });

      expect(result.current.splitTree).not.toBeNull();
      expect(result.current.splitTree!.type).toBe("split");
      if (result.current.splitTree!.type === "split") {
        expect(result.current.splitTree!.direction).toBe("horizontal");
        expect(result.current.splitTree!.children[1].type).toBe("leaf");
        if (result.current.splitTree!.children[1].type === "leaf") {
          expect(result.current.splitTree!.children[1].paneId).not.toBe("");
        }
      }
      expect(result.current.panes).toHaveLength(2);
      expect(result.current.panes[1].podKey).toBe("pod-2");
      expect(result.current.activePane).toBe(result.current.panes[1].id);
    });

    it("should split pane vertically", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let paneId: string;
      act(() => {
        paneId = result.current.addPane("pod-1");
      });

      act(() => {
        result.current.splitPane(paneId!, "vertical", "pod-3");
      });

      expect(result.current.splitTree!.type).toBe("split");
      if (result.current.splitTree!.type === "split") {
        expect(result.current.splitTree!.direction).toBe("vertical");
      }
      expect(result.current.panes).toHaveLength(2);
      expect(result.current.panes[1].podKey).toBe("pod-3");
    });

    it("should bubble same-direction split into parent group with halved target size", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let pane1Id: string;
      act(() => {
        pane1Id = result.current.addPane("pod-1");
        result.current.addPane("pod-2");
      });

      // Split pane-1 right (same direction as parent horizontal group)
      act(() => {
        result.current.splitPane(pane1Id!, "horizontal", "pod-3");
      });

      const tree = result.current.splitTree;
      expect(tree!.type).toBe("split");
      if (tree!.type === "split") {
        // Should have 3 children in the same group (bubbled up)
        expect(tree!.children).toHaveLength(3);
        expect(tree!.direction).toBe("horizontal");
        // Sizes: [25, 25, 50] — first pane halved, second unchanged
        expect(tree!.sizes[0]).toBeCloseTo(25, 1);
        expect(tree!.sizes[1]).toBeCloseTo(25, 1);
        expect(tree!.sizes[2]).toBeCloseTo(50, 1);
      }
    });

    it("should nest cross-direction split as new sub-split", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let pane1Id: string;
      act(() => {
        pane1Id = result.current.addPane("pod-1");
        result.current.addPane("pod-2");
      });

      // Split pane-1 down (cross-direction from parent horizontal)
      act(() => {
        result.current.splitPane(pane1Id!, "vertical", "pod-3");
      });

      const tree = result.current.splitTree;
      expect(tree!.type).toBe("split");
      if (tree!.type === "split") {
        // Root still has 2 children
        expect(tree!.children).toHaveLength(2);
        expect(tree!.direction).toBe("horizontal");
        // First child is now a vertical sub-split
        const sub = tree!.children[0];
        expect(sub.type).toBe("split");
        if (sub.type === "split") {
          expect(sub.direction).toBe("vertical");
          expect(sub.children).toHaveLength(2);
          expect(sub.sizes).toEqual([50, 50]);
        }
      }
    });

    it("should remove pane from 3-child group and normalize sizes proportionally", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-1");
        result.current.addPane("pod-2");
        result.current.addPane("pod-3");
      });

      // Manually set uneven sizes
      const tree = result.current.splitTree;
      if (tree?.type === "split") {
        act(() => {
          result.current.updateSplitSizes(tree.id, [50, 30, 20]);
        });
      }

      // Remove second pane — sizes should normalize [50, 20] → [71.4, 28.6]
      const secondPaneId = result.current.panes[1].id;
      act(() => {
        result.current.removePane(secondPaneId);
      });

      expect(result.current.panes).toHaveLength(2);
      const newTree = result.current.splitTree;
      expect(newTree!.type).toBe("split");
      if (newTree!.type === "split") {
        expect(newTree!.children).toHaveLength(2);
        expect(newTree!.sizes[0]).toBeCloseTo(71.4, 0);
        expect(newTree!.sizes[1]).toBeCloseTo(28.6, 0);
      }
    });

    it("should update split sizes", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-1");
        result.current.addPane("pod-2");
      });

      const tree = result.current.splitTree;
      expect(tree).not.toBeNull();
      expect(tree!.type).toBe("split");

      act(() => {
        result.current.updateSplitSizes(tree!.id, [30, 70]);
      });

      if (result.current.splitTree!.type === "split") {
        expect(result.current.splitTree!.sizes).toEqual([30, 70]);
      }
    });

    it("should create new split when splitPane on root leaf", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let paneId: string;
      act(() => {
        paneId = result.current.addPane("pod-1");
      });

      expect(result.current.splitTree!.type).toBe("leaf");

      act(() => {
        result.current.splitPane(paneId!, "vertical", "pod-2");
      });

      const tree = result.current.splitTree;
      expect(tree!.type).toBe("split");
      if (tree!.type === "split") {
        expect(tree!.direction).toBe("vertical");
        expect(tree!.children).toHaveLength(2);
        expect(tree!.sizes).toEqual([50, 50]);
      }
    });

    it("should grow same-direction group across multiple splits (2→5)", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let paneId: string;
      act(() => {
        paneId = result.current.addPane("pod-1");
      });

      // Split right 4 times — each bubbles into same horizontal group
      for (let i = 2; i <= 5; i++) {
        act(() => {
          result.current.splitPane(paneId!, "horizontal", `pod-${i}`);
        });
      }

      expect(result.current.panes).toHaveLength(5);
      const tree = result.current.splitTree;
      expect(tree!.type).toBe("split");
      if (tree!.type === "split") {
        expect(tree!.children).toHaveLength(5);
        expect(tree!.direction).toBe("horizontal");
        // All sizes should be positive
        tree!.sizes.forEach((s) => expect(s).toBeGreaterThan(0));
      }
    });

    it("should collapse 2-child split to leaf when one pane removed", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      let firstId: string;
      act(() => {
        firstId = result.current.addPane("pod-1");
        result.current.addPane("pod-2");
      });

      expect(result.current.splitTree!.type).toBe("split");

      // Remove second pane — should collapse split to leaf
      act(() => {
        result.current.removePane(result.current.panes[1].id);
      });

      expect(result.current.splitTree!.type).toBe("leaf");
      if (result.current.splitTree!.type === "leaf") {
        expect(result.current.splitTree!.paneId).toBe(firstId!);
      }
    });

    it("should handle addPane when activePane is null but tree exists", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-1");
        result.current.setActivePane(null);
      });

      expect(result.current.activePane).toBeNull();
      expect(result.current.splitTree).not.toBeNull();

      // Add second pane with null activePane — should wrap root
      act(() => {
        result.current.addPane("pod-2");
      });

      expect(result.current.panes).toHaveLength(2);
      const tree = result.current.splitTree;
      expect(tree!.type).toBe("split");
      if (tree!.type === "split") {
        expect(tree!.children).toHaveLength(2);
        expect(tree!.direction).toBe("horizontal");
      }
    });

    it("should remove pane by podKey via removePaneByPodKey", () => {
      const { result } = renderHook(() => useWorkspaceStore());

      act(() => {
        result.current.addPane("pod-1");
        result.current.addPane("pod-2");
      });

      expect(result.current.panes).toHaveLength(2);

      act(() => {
        result.current.removePaneByPodKey("pod-1");
      });

      expect(result.current.panes).toHaveLength(1);
      expect(result.current.panes[0].podKey).toBe("pod-2");
    });
  });
});

// NOTE: Relay Connection Pool tests live in relayConnection.test.ts.
