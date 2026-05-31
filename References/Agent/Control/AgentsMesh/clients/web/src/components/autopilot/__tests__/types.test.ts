import { describe, it, expect } from "vitest";
import { normalizeDecisionType, type NormalizedDecisionType } from "../panel/types";

describe("normalizeDecisionType", () => {
  describe("uppercase backend types", () => {
    it("should normalize CONTINUE to continue", () => {
      expect(normalizeDecisionType("CONTINUE")).toBe("continue");
    });

    it("should normalize TASK_COMPLETED to completed", () => {
      expect(normalizeDecisionType("TASK_COMPLETED")).toBe("completed");
    });

    it("should normalize NEED_HUMAN_HELP to need_help", () => {
      expect(normalizeDecisionType("NEED_HUMAN_HELP")).toBe("need_help");
    });

    it("should normalize GIVE_UP to give_up", () => {
      expect(normalizeDecisionType("GIVE_UP")).toBe("give_up");
    });
  });

  describe("lowercase frontend types (passthrough)", () => {
    it("should passthrough continue", () => {
      expect(normalizeDecisionType("continue")).toBe("continue");
    });

    it("should passthrough completed", () => {
      expect(normalizeDecisionType("completed")).toBe("completed");
    });

    it("should passthrough need_help", () => {
      expect(normalizeDecisionType("need_help")).toBe("need_help");
    });

    it("should passthrough give_up", () => {
      expect(normalizeDecisionType("give_up")).toBe("give_up");
    });
  });

  describe("unknown types", () => {
    it("should default to continue for unknown types", () => {
      expect(normalizeDecisionType("UNKNOWN_TYPE")).toBe("continue");
    });

    it("should default to continue for empty string", () => {
      expect(normalizeDecisionType("")).toBe("continue");
    });

    it("should default to continue for random string", () => {
      expect(normalizeDecisionType("random_decision")).toBe("continue");
    });
  });

  describe("type safety", () => {
    it("should return correct type for all valid inputs", () => {
      const validTypes: NormalizedDecisionType[] = ["continue", "completed", "need_help", "give_up"];
      const inputs = [
        "CONTINUE", "TASK_COMPLETED", "NEED_HUMAN_HELP", "GIVE_UP",
        "continue", "completed", "need_help", "give_up",
      ];

      inputs.forEach((input) => {
        const result = normalizeDecisionType(input);
        expect(validTypes).toContain(result);
      });
    });
  });
});
