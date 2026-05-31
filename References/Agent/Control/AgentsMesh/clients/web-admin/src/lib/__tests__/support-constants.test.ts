import { describe, it, expect } from "vitest";
import {
  statusLabels,
  statusVariants,
  categoryLabels,
  categoryVariants,
  priorityLabels,
  priorityVariants,
} from "../support-constants";

describe("Support Constants", () => {
  describe("statusLabels", () => {
    it("should define labels for all statuses", () => {
      expect(statusLabels).toEqual({
        open: "Open",
        in_progress: "In Progress",
        resolved: "Resolved",
        closed: "Closed",
      });
    });
  });

  describe("statusVariants", () => {
    it("should map each status to a valid badge variant", () => {
      expect(statusVariants.open).toBe("destructive");
      expect(statusVariants.in_progress).toBe("warning");
      expect(statusVariants.resolved).toBe("success");
      expect(statusVariants.closed).toBe("secondary");
    });

    it("should have a variant for every label key", () => {
      const labelKeys = Object.keys(statusLabels);
      const variantKeys = Object.keys(statusVariants);
      expect(variantKeys).toEqual(expect.arrayContaining(labelKeys));
    });
  });

  describe("categoryLabels", () => {
    it("should define labels for all categories", () => {
      expect(categoryLabels).toEqual({
        bug: "Bug",
        feature_request: "Feature Request",
        usage_question: "Usage Question",
        account: "Account",
        other: "Other",
      });
    });
  });

  describe("categoryVariants", () => {
    it("should map each category to a valid badge variant", () => {
      expect(categoryVariants.bug).toBe("destructive");
      expect(categoryVariants.feature_request).toBe("default");
      expect(categoryVariants.usage_question).toBe("secondary");
      expect(categoryVariants.account).toBe("outline");
      expect(categoryVariants.other).toBe("secondary");
    });

    it("should have a variant for every label key", () => {
      const labelKeys = Object.keys(categoryLabels);
      const variantKeys = Object.keys(categoryVariants);
      expect(variantKeys).toEqual(expect.arrayContaining(labelKeys));
    });
  });

  describe("priorityLabels", () => {
    it("should define labels for all priorities", () => {
      expect(priorityLabels).toEqual({
        low: "Low",
        medium: "Medium",
        high: "High",
      });
    });
  });

  describe("priorityVariants", () => {
    it("should map each priority to a valid badge variant", () => {
      expect(priorityVariants.low).toBe("secondary");
      expect(priorityVariants.medium).toBe("warning");
      expect(priorityVariants.high).toBe("destructive");
    });

    it("should have a variant for every label key", () => {
      const labelKeys = Object.keys(priorityLabels);
      const variantKeys = Object.keys(priorityVariants);
      expect(variantKeys).toEqual(expect.arrayContaining(labelKeys));
    });
  });
});
