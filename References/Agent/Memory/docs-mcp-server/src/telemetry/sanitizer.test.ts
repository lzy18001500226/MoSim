import { describe, expect, it } from "vitest";
import {
  analyzeSearchQuery,
  extractCliFlags,
  extractHostname,
  extractProtocol,
  sanitizeError,
  sanitizeErrorMessage,
} from "./sanitizer";

describe("extractHostname", () => {
  it("should extract hostname from various URL formats", () => {
    expect(extractHostname("https://example.com/path")).toBe("example.com");
    expect(extractHostname("http://subdomain.example.com")).toBe("subdomain.example.com");
    expect(extractHostname("https://docs.example.com/api/v1")).toBe("docs.example.com");
    expect(extractHostname("invalid-url")).toBe("invalid-hostname");
    expect(extractHostname("")).toBe("invalid-hostname");
  });
});

describe("extractProtocol", () => {
  it("should extract protocol from URLs", () => {
    expect(extractProtocol("https://example.com")).toBe("https");
    expect(extractProtocol("http://example.com")).toBe("http");
    expect(extractProtocol("file:///path/to/file")).toBe("file");
    expect(extractProtocol("invalid-url")).toBe("unknown");
    expect(extractProtocol("")).toBe("unknown");
  });
});

describe("analyzeSearchQuery", () => {
  it("should analyze search query characteristics", () => {
    const result1 = analyzeSearchQuery("react hooks");
    expect(result1.length).toBe(11);
    expect(result1.wordCount).toBe(2);
    expect(result1.hasSpecialChars).toBe(false);
    expect(result1.hasCodeTerms).toBe(false);

    const result2 = analyzeSearchQuery("get-user-info()");
    expect(result2.hasSpecialChars).toBe(true);

    const result3 = analyzeSearchQuery("function test");
    expect(result3.hasCodeTerms).toBe(true);
  });
});

describe("sanitizeErrorMessage", () => {
  it("should sanitize error messages removing sensitive info", () => {
    expect(sanitizeErrorMessage("Error in /Users/john/project/file.js")).toBe(
      "Error in [path]",
    );

    expect(
      sanitizeErrorMessage("Failed to read file:///Users/john/documents/secret.txt"),
    ).toBe("Failed to read [file-url]");

    expect(sanitizeErrorMessage("Cannot access ./local/config.json")).toBe(
      "Cannot access .[path]",
    );

    expect(sanitizeErrorMessage("api_key=secret123 invalid")).toBe(
      "api_key=[redacted] invalid",
    );
  });
});

describe("sanitizeError", () => {
  it("should sanitize Error objects", () => {
    const error = new Error("File not found: /Users/john/secret.txt");
    const result = sanitizeError(error);

    expect(result.type).toBe("Error");
    expect(result.message).toBe("File not found: [path]");
    expect(result.hasStack).toBe(true);
  });

  it("should handle TypeError objects", () => {
    const error = new TypeError("Cannot read property of undefined");
    const result = sanitizeError(error);

    expect(result.type).toBe("TypeError");
    expect(result.message).toBe("Cannot read property of undefined");
    expect(result.hasStack).toBe(true);
  });
});

describe("extractCliFlags", () => {
  it("should extract CLI flags", () => {
    const args = ["node", "script.js", "--verbose", "--port=3000", "file.txt"];
    const result = extractCliFlags(args);

    expect(result).toEqual(["--verbose", "--port=3000"]);
    expect(result.length).toBe(2);
  });

  it("should handle no flags", () => {
    const args = ["node", "script.js", "file.txt"];
    const result = extractCliFlags(args);

    expect(result).toEqual([]);
    expect(result.length).toBe(0);
  });

  it("should handle single dash flags", () => {
    const args = ["node", "script.js", "-v", "--help"];
    const result = extractCliFlags(args);

    expect(result).toEqual(["-v", "--help"]);
    expect(result.length).toBe(2);
  });
});
