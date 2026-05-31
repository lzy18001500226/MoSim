import { describe, it, expect } from "vitest";
import type { SplitTreeNode, SplitTreeLeaf, SplitTreeSplit } from "../workspaceTypes";
import {
  findLastLeaf,
  findLeafByPaneId,
  findParentSplit,
  insertChildAt,
  removeLeaf,
  replaceNode,
  updateSizes,
} from "../workspaceSplitTree";

// --- Helpers ---

function leaf(paneId: string, id = `leaf-${paneId}`): SplitTreeLeaf {
  return { type: "leaf", id, paneId };
}

function split(
  direction: "horizontal" | "vertical",
  children: SplitTreeNode[],
  id = `split-${Math.random().toString(36).slice(2, 7)}`,
): SplitTreeSplit {
  const evenSize = 100 / children.length;
  return { type: "split", id, direction, children, sizes: children.map(() => evenSize) };
}

// --- Tests ---

describe("workspaceSplitTree", () => {
  describe("findLastLeaf", () => {
    it("should return leaf itself when node is a leaf", () => {
      const l = leaf("a");
      expect(findLastLeaf(l)).toBe(l);
    });

    it("should return rightmost leaf in a 2-child split", () => {
      const r = leaf("b");
      const tree = split("horizontal", [leaf("a"), r]);
      expect(findLastLeaf(tree)).toBe(r);
    });

    it("should return rightmost leaf in a 3-child split", () => {
      const r = leaf("c");
      const tree = split("horizontal", [leaf("a"), leaf("b"), r]);
      expect(findLastLeaf(tree)).toBe(r);
    });

    it("should return deepest rightmost leaf in nested tree", () => {
      const deepLeaf = leaf("deep");
      const tree = split("vertical", [
        leaf("a"),
        split("horizontal", [leaf("b"), deepLeaf]),
      ]);
      expect(findLastLeaf(tree)).toBe(deepLeaf);
    });
  });

  describe("findLeafByPaneId", () => {
    it("should find leaf in a 3-child split", () => {
      const target = leaf("b");
      const tree = split("horizontal", [leaf("a"), target, leaf("c")]);
      expect(findLeafByPaneId(tree, "b")).toBe(target);
    });

    it("should find leaf in deeply nested tree", () => {
      const target = leaf("deep");
      const tree = split("vertical", [
        split("horizontal", [leaf("a"), leaf("b")]),
        split("horizontal", [target, leaf("c")]),
      ]);
      expect(findLeafByPaneId(tree, "deep")).toBe(target);
    });

    it("should return null for non-existent paneId", () => {
      const tree = split("horizontal", [leaf("a"), leaf("b")]);
      expect(findLeafByPaneId(tree, "nope")).toBeNull();
    });
  });

  describe("findParentSplit", () => {
    it("should return null when target is the root", () => {
      const l = leaf("a");
      expect(findParentSplit(l, l.id)).toBeNull();
    });

    it("should return null when root is a split and target is the root itself", () => {
      const tree = split("horizontal", [leaf("a"), leaf("b")], "root");
      expect(findParentSplit(tree, "root")).toBeNull();
    });

    it("should find parent of a direct child", () => {
      const child = leaf("a");
      const tree = split("horizontal", [child, leaf("b")], "root");
      const parent = findParentSplit(tree, child.id);
      expect(parent).not.toBeNull();
      expect(parent!.id).toBe("root");
    });

    it("should find parent of a deeply nested child", () => {
      const target = leaf("deep", "deep-id");
      const inner = split("horizontal", [target, leaf("c")], "inner");
      const tree = split("vertical", [leaf("a"), inner], "root");

      const parent = findParentSplit(tree, "deep-id");
      expect(parent).not.toBeNull();
      expect(parent!.id).toBe("inner");
    });

    it("should find parent in a 3-child split", () => {
      const target = leaf("b", "b-id");
      const tree = split("horizontal", [leaf("a"), target, leaf("c")], "root");

      const parent = findParentSplit(tree, "b-id");
      expect(parent).not.toBeNull();
      expect(parent!.id).toBe("root");
    });
  });

  describe("insertChildAt", () => {
    it("should insert after first child", () => {
      const tree = split("horizontal", [leaf("a"), leaf("b")], "root");
      const newChild = leaf("c");
      const result = insertChildAt(tree, "root", newChild, 0, [33, 33, 34]);

      expect(result.type).toBe("split");
      if (result.type === "split") {
        expect(result.children).toHaveLength(3);
        expect((result.children[0] as SplitTreeLeaf).paneId).toBe("a");
        expect((result.children[1] as SplitTreeLeaf).paneId).toBe("c");
        expect((result.children[2] as SplitTreeLeaf).paneId).toBe("b");
        expect(result.sizes).toEqual([33, 33, 34]);
      }
    });

    it("should insert at the end", () => {
      const tree = split("horizontal", [leaf("a"), leaf("b")], "root");
      const newChild = leaf("c");
      const result = insertChildAt(tree, "root", newChild, 1, [33, 33, 34]);

      if (result.type === "split") {
        expect(result.children).toHaveLength(3);
        expect((result.children[2] as SplitTreeLeaf).paneId).toBe("c");
      }
    });

    it("should insert into a nested split by id", () => {
      const inner = split("horizontal", [leaf("a"), leaf("b")], "inner");
      const tree = split("vertical", [inner, leaf("c")], "root");
      const newChild = leaf("d");
      const result = insertChildAt(tree, "inner", newChild, 0, [33, 33, 34]);

      if (result.type === "split") {
        const modifiedInner = result.children[0];
        expect(modifiedInner.type).toBe("split");
        if (modifiedInner.type === "split") {
          expect(modifiedInner.children).toHaveLength(3);
        }
      }
    });

    it("should not modify tree when splitId not found", () => {
      const tree = split("horizontal", [leaf("a"), leaf("b")], "root");
      const result = insertChildAt(tree, "nonexistent", leaf("c"), 0, [33, 33, 34]);
      // Structure unchanged (though sizes param is ignored)
      if (result.type === "split") {
        expect(result.children).toHaveLength(2);
      }
    });
  });

  describe("removeLeaf", () => {
    it("should collapse 2-child split to remaining child", () => {
      const remaining = leaf("b", "b-id");
      const target = leaf("a", "a-id");
      const tree = split("horizontal", [target, remaining], "root");

      const result = removeLeaf(tree, "a-id");
      expect(result).not.toBeNull();
      expect(result!.type).toBe("leaf");
      expect((result as SplitTreeLeaf).paneId).toBe("b");
    });

    it("should remove from 3-child split and normalize sizes", () => {
      const tree: SplitTreeSplit = {
        type: "split", id: "root", direction: "horizontal",
        children: [leaf("a", "a-id"), leaf("b", "b-id"), leaf("c", "c-id")],
        sizes: [50, 30, 20],
      };

      const result = removeLeaf(tree, "b-id");
      expect(result).not.toBeNull();
      if (result!.type === "split") {
        expect(result!.children).toHaveLength(2);
        // [50, 20] → normalize to [71.4, 28.6]
        expect(result!.sizes[0]).toBeCloseTo(71.4, 0);
        expect(result!.sizes[1]).toBeCloseTo(28.6, 0);
      }
    });

    it("should remove deeply nested leaf and collapse inner split", () => {
      // Split-V [ Split-H[A, B], C ]
      // Remove A → Split-H collapses to B → Split-V[B, C]
      const inner = split("horizontal", [leaf("a", "a-id"), leaf("b", "b-id")], "inner");
      const tree = split("vertical", [inner, leaf("c", "c-id")], "root");

      const result = removeLeaf(tree, "a-id");
      expect(result).not.toBeNull();
      if (result!.type === "split") {
        expect(result!.children).toHaveLength(2);
        // inner collapsed: first child is now leaf B
        expect(result!.children[0].type).toBe("leaf");
        expect((result!.children[0] as SplitTreeLeaf).paneId).toBe("b");
        expect(result!.children[1].type).toBe("leaf");
        expect((result!.children[1] as SplitTreeLeaf).paneId).toBe("c");
      }
    });

    it("should return null when removing the only leaf", () => {
      const result = removeLeaf(leaf("a", "a-id"), "a-id");
      expect(result).toBeNull();
    });

    it("should not modify tree when leafId not found", () => {
      const tree = split("horizontal", [leaf("a", "a-id"), leaf("b", "b-id")], "root");
      const result = removeLeaf(tree, "nonexistent");
      expect(result).not.toBeNull();
      if (result!.type === "split") {
        expect(result!.children).toHaveLength(2);
      }
    });
  });

  describe("replaceNode", () => {
    it("should replace a leaf in N-child split", () => {
      const tree = split("horizontal", [leaf("a", "a-id"), leaf("b", "b-id"), leaf("c", "c-id")], "root");
      const replacement = split("vertical", [leaf("x"), leaf("y")], "new-split");
      const result = replaceNode(tree, "b-id", replacement);

      if (result.type === "split") {
        expect(result.children[1].type).toBe("split");
        expect((result.children[1] as SplitTreeSplit).id).toBe("new-split");
      }
    });
  });

  describe("updateSizes", () => {
    it("should update sizes on N-child split", () => {
      const tree = split("horizontal", [leaf("a"), leaf("b"), leaf("c")], "root");
      const result = updateSizes(tree, "root", [20, 50, 30]);

      if (result.type === "split") {
        expect(result.sizes).toEqual([20, 50, 30]);
      }
    });

    it("should update sizes on nested split", () => {
      const inner = split("horizontal", [leaf("a"), leaf("b")], "inner");
      const tree = split("vertical", [inner, leaf("c")], "root");
      const result = updateSizes(tree, "inner", [70, 30]);

      if (result.type === "split") {
        const modifiedInner = result.children[0];
        if (modifiedInner.type === "split") {
          expect(modifiedInner.sizes).toEqual([70, 30]);
        }
      }
    });
  });
});
