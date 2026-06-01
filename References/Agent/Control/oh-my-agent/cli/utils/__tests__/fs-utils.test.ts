import * as fs from "node:fs";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { clearConflictingEntries, clearNonDirectory } from "../fs-utils.js";

vi.mock("node:fs", () => ({
  existsSync: vi.fn(),
  lstatSync: vi.fn(),
  unlinkSync: vi.fn(),
  readdirSync: vi.fn(),
}));

describe("fs-utils", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("clearNonDirectory", () => {
    it("should unlink if path is not a directory", () => {
      (fs.lstatSync as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        isDirectory: () => false,
      });

      clearNonDirectory("/some/path");

      expect(fs.unlinkSync).toHaveBeenCalledWith("/some/path");
    });

    it("should not unlink if path is a directory", () => {
      (fs.lstatSync as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        isDirectory: () => true,
      });

      clearNonDirectory("/some/dir");

      expect(fs.unlinkSync).not.toHaveBeenCalled();
    });

    it("should do nothing if path does not exist", () => {
      (fs.lstatSync as unknown as ReturnType<typeof vi.fn>).mockImplementation(
        () => {
          throw new Error("ENOENT");
        },
      );

      clearNonDirectory("/non/existent");

      expect(fs.unlinkSync).not.toHaveBeenCalled();
    });
  });

  describe("clearConflictingEntries", () => {
    it("should clear entries in destDir that are directories in sourceDir", () => {
      (fs.existsSync as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
        true,
      );
      (fs.readdirSync as unknown as ReturnType<typeof vi.fn>).mockReturnValue([
        { name: "conflict", isDirectory: () => true },
        { name: "ok", isDirectory: () => false },
      ]);
      (fs.lstatSync as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
        isDirectory: () => false, // dest version is a file/symlink
      });

      clearConflictingEntries("/source", "/dest");

      expect(fs.unlinkSync).toHaveBeenCalledWith(join("/dest", "conflict"));
      expect(fs.unlinkSync).not.toHaveBeenCalledWith(join("/dest", "ok"));
    });

    it("should skip if destDir does not exist", () => {
      (fs.existsSync as unknown as ReturnType<typeof vi.fn>).mockReturnValue(
        false,
      );

      clearConflictingEntries("/source", "/dest");

      expect(fs.readdirSync).not.toHaveBeenCalled();
    });
  });
});
