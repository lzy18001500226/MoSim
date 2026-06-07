import { describe, expect, it } from "vitest";
import {
  DEFAULT_EXCLUSION_PATTERNS,
  DEFAULT_FILE_EXCLUSIONS,
  DEFAULT_FOLDER_EXCLUSIONS,
  getEffectiveExclusionPatterns,
} from "./defaultPatterns";

describe("defaultPatterns", () => {
  describe("DEFAULT_FILE_EXCLUSIONS", () => {
    it("should have file exclusion patterns defined", () => {
      expect(DEFAULT_FILE_EXCLUSIONS).toBeDefined();
      expect(DEFAULT_FILE_EXCLUSIONS.length).toBeGreaterThan(0);
    });

    it("should include sample common documentation files", () => {
      expect(DEFAULT_FILE_EXCLUSIONS).toContain("**/CHANGELOG.md");
      expect(DEFAULT_FILE_EXCLUSIONS).toContain("**/LICENSE");
      expect(DEFAULT_FILE_EXCLUSIONS).toContain("**/CODE_OF_CONDUCT.md");
    });
  });

  describe("DEFAULT_FOLDER_EXCLUSIONS", () => {
    it("should have folder exclusion patterns defined", () => {
      expect(DEFAULT_FOLDER_EXCLUSIONS).toBeDefined();
      expect(DEFAULT_FOLDER_EXCLUSIONS.length).toBeGreaterThan(0);
    });

    it("should include sample archive and i18n folder patterns", () => {
      expect(DEFAULT_FOLDER_EXCLUSIONS).toContain("**/archive/**");
      expect(DEFAULT_FOLDER_EXCLUSIONS).toContain("**/deprecated/**");
      expect(DEFAULT_FOLDER_EXCLUSIONS).toContain("**/i18n/zh*/**");
    });
  });

  describe("DEFAULT_EXCLUSION_PATTERNS", () => {
    it("should combine file and folder patterns", () => {
      expect(DEFAULT_EXCLUSION_PATTERNS).toHaveLength(
        DEFAULT_FILE_EXCLUSIONS.length + DEFAULT_FOLDER_EXCLUSIONS.length,
      );
      expect(DEFAULT_EXCLUSION_PATTERNS.length).toBeGreaterThan(0);
    });
  });

  describe("getEffectiveExclusionPatterns", () => {
    it("should return default patterns when no user patterns provided", () => {
      const result = getEffectiveExclusionPatterns(undefined);
      expect(result).toEqual(DEFAULT_EXCLUSION_PATTERNS);
    });

    it("should return user patterns when provided", () => {
      const userPatterns = ["custom/*", "user-specific.md"];
      const result = getEffectiveExclusionPatterns(userPatterns);
      expect(result).toEqual(userPatterns);
      expect(result).not.toEqual(DEFAULT_EXCLUSION_PATTERNS);
    });

    it("should return empty array if user explicitly provides empty array", () => {
      const result = getEffectiveExclusionPatterns([]);
      expect(result).toEqual([]);
      expect(result).not.toEqual(DEFAULT_EXCLUSION_PATTERNS);
    });
  });
});
