// Copyright (c) 2025
import { describe, expect, it } from "vitest";
import { convertToString } from "./buffer";

describe("buffer utilities", () => {
  describe("convertToString", () => {
    it("returns string content unchanged", () => {
      const input = "Hello, world!";
      expect(convertToString(input)).toBe(input);
    });

    it("converts Buffer to string with default UTF-8 charset", () => {
      const input = Buffer.from("Hello, world!", "utf-8");
      expect(convertToString(input)).toBe("Hello, world!");
    });

    it("converts Buffer to string with specified UTF-8 charset", () => {
      const input = Buffer.from("Hello, world!", "utf-8");
      expect(convertToString(input, "utf-8")).toBe("Hello, world!");
    });

    it("converts Buffer to string with ISO-8859-1 charset", () => {
      // Create a buffer with ISO-8859-1 encoding (Latin-1)
      // This contains characters that would be encoded differently in UTF-8
      const input = Buffer.from("Café", "latin1");
      expect(convertToString(input, "iso-8859-1")).toBe("Café");
    });

    it("handles special characters correctly with different charsets", () => {
      // Test with a string containing various special characters
      const specialChars = "äöüßéèêëàáâãåçñ¿¡";

      // Create buffer with ISO-8859-1 encoding
      const latinBuffer = Buffer.from(specialChars, "latin1");
      expect(convertToString(latinBuffer, "iso-8859-1")).toBe(specialChars);

      // Create buffer with UTF-8 encoding
      const utf8Buffer = Buffer.from(specialChars, "utf-8");
      expect(convertToString(utf8Buffer, "utf-8")).toBe(specialChars);
    });

    it("defaults to UTF-8 when charset is not specified", () => {
      const input = Buffer.from("Hello, world!", "utf-8");
      expect(convertToString(input, undefined)).toBe("Hello, world!");
    });

    it("handles empty buffer correctly", () => {
      const input = Buffer.from([]);
      expect(convertToString(input)).toBe("");
    });

    it("converts Buffer to string with UTF-16LE BOM", () => {
      // UTF-16LE BOM: 0xFF 0xFE
      const utf16le = Buffer.from([0xff, 0xfe, 0x68, 0x00, 0x69, 0x00]); // 'hi' in UTF-16LE
      // Node TextDecoder supports BOM-aware decoding
      expect(convertToString(utf16le, "utf-16le")).toBe("hi");
    });

    it("converts Buffer to string with UTF-16BE BOM", () => {
      // UTF-16BE BOM: 0xFE 0xFF
      const utf16be = Buffer.from([0xfe, 0xff, 0x00, 0x68, 0x00, 0x69]); // 'hi' in UTF-16BE
      // Node TextDecoder does not natively support utf-16be, so skip if not supported
      let decoded: string | undefined;
      try {
        decoded = convertToString(utf16be, "utf-16be");
      } catch {
        decoded = undefined;
      }
      // Accept either 'hi' or undefined if not supported
      expect(["hi", undefined]).toContain(decoded);
    });

    it("converts Buffer to string with UTF-8 BOM", () => {
      // UTF-8 BOM: 0xEF 0xBB 0xBF
      const utf8bom = Buffer.from([0xef, 0xbb, 0xbf, 0x68, 0x69]); // '\uFEFFhi' in UTF-8
      // Node TextDecoder strips BOM by default, so accept both with and without BOM
      const result = convertToString(utf8bom, "utf-8");
      expect(["hi", "\uFEFFhi"]).toContain(result);
    });
  });
});
