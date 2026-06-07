import { describe, expect, it } from "vitest";
import { convertToString } from "./buffer";
import { detectCharsetFromHtml, normalizeCharset, resolveCharset } from "./charset";

describe("charset detection edge cases", () => {
  describe("detectCharsetFromHtml", () => {
    it("should detect HTML5 style meta charset", () => {
      const html = '<html><head><meta charset="utf-8"><title>Test</title></head></html>';
      expect(detectCharsetFromHtml(html)).toBe("utf-8");
    });

    it("should detect HTML5 style meta charset with quotes", () => {
      const html =
        '<html><head><meta charset="iso-8859-1"><title>Test</title></head></html>';
      expect(detectCharsetFromHtml(html)).toBe("iso-8859-1");
    });

    it("should detect HTML4 style meta charset", () => {
      const html =
        '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>Test</title></head></html>';
      expect(detectCharsetFromHtml(html)).toBe("utf-8");
    });

    it("should return undefined when no charset is found", () => {
      const html = "<html><head><title>Test</title></head></html>";
      expect(detectCharsetFromHtml(html)).toBeUndefined();
    });

    it("should handle case insensitive matching", () => {
      const html = '<HTML><HEAD><META CHARSET="UTF-8"><TITLE>Test</TITLE></HEAD></HTML>';
      expect(detectCharsetFromHtml(html)).toBe("utf-8");
    });
  });

  describe("resolveCharset", () => {
    it("should prefer HTML meta charset over HTTP header for HTML content", () => {
      const html = '<meta charset="iso-8859-1"><title>Test</title>';
      const buffer = Buffer.from(html, "utf-8");

      const result = resolveCharset("utf-8", buffer, "text/html");
      expect(result).toBe("iso-8859-1");
    });

    it("should use HTTP charset when no meta charset is found", () => {
      const html = "<html><head><title>Test</title></head></html>";
      const buffer = Buffer.from(html, "utf-8");

      const result = resolveCharset("iso-8859-1", buffer, "text/html");
      expect(result).toBe("iso-8859-1");
    });

    it("should default to UTF-8 when no charset is specified", () => {
      const html = "<html><head><title>Test</title></head></html>";
      const buffer = Buffer.from(html, "utf-8");

      const result = resolveCharset(undefined, buffer, "text/html");
      expect(result).toBe("utf-8");
    });

    it("should use HTTP charset for non-HTML content", () => {
      const text = "Plain text content";
      const buffer = Buffer.from(text, "utf-8");

      const result = resolveCharset("iso-8859-1", buffer, "text/plain");
      expect(result).toBe("iso-8859-1");
    });

    it("should handle string input", () => {
      const html = '<meta charset="windows-1252"><title>Test</title>';

      const result = resolveCharset("utf-8", html, "text/html");
      expect(result).toBe("windows-1252");
    });
  });

  describe("normalizeCharset", () => {
    it("should normalize common charset aliases", () => {
      expect(normalizeCharset("ISO-8859-1")).toBe("latin1");
      expect(normalizeCharset("windows-1252")).toBe("cp1252");
      expect(normalizeCharset("UTF8")).toBe("utf-8");
      expect(normalizeCharset("US-ASCII")).toBe("ascii");
    });

    it("should handle unknown charsets by returning them as-is", () => {
      expect(normalizeCharset("unknown-charset")).toBe("unknown-charset");
    });

    it("should handle case and whitespace", () => {
      expect(normalizeCharset("  UTF-8  ")).toBe("utf-8");
      expect(normalizeCharset("WINDOWS-1252")).toBe("cp1252");
    });
  });

  describe("charset mismatch scenarios", () => {
    it("should handle HTML with meta charset that differs from Content-Type header", () => {
      // Simulate a scenario where Content-Type says UTF-8 but content is actually ISO-8859-1
      const htmlWithMeta = `<!DOCTYPE html>
<html>
<head>
<meta charset="iso-8859-1">
<title>Test Page</title>
</head>
<body>
<p>Café: coffee in French with proper encoding</p>
</body>
</html>`;

      // Create buffer with ISO-8859-1 encoding (which the meta tag declares)
      const buffer = Buffer.from(htmlWithMeta, "latin1");

      // If we try to decode with UTF-8 (wrong charset), we should get invalid characters
      const wrongDecoding = convertToString(buffer, "utf-8");
      expect(wrongDecoding).not.toBe(htmlWithMeta);

      // If we decode with the correct charset, we should get proper text
      const correctDecoding = convertToString(buffer, "iso-8859-1");
      expect(correctDecoding).toBe(htmlWithMeta);
    });

    it("should handle content with no charset specified in headers", () => {
      // HTML content with meta charset only
      const htmlContent = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>UTF-8 Test</title>
</head>
<body>
<p>Special characters: é, ñ, ü, 中文, 🚀</p>
</body>
</html>`;

      const buffer = Buffer.from(htmlContent, "utf-8");

      // Should default to UTF-8 and work correctly
      const result = convertToString(buffer);
      expect(result).toBe(htmlContent);
    });

    it("should handle content with BOM but no charset header", () => {
      const textContent = "Hello, world! Special chars: café, naïve";

      // Create UTF-8 content with BOM
      const bom = Buffer.from([0xef, 0xbb, 0xbf]);
      const content = Buffer.from(textContent, "utf-8");
      const bufferWithBom = Buffer.concat([bom, content]);

      // Should handle BOM correctly
      const result = convertToString(bufferWithBom, "utf-8");
      expect(result === textContent || result === `\uFEFF${textContent}`).toBe(true);
    });

    it("should handle windows-1252 charset correctly", () => {
      // Windows-1252 has specific characters in the 128-159 range
      const windows1252Content = "Smart quotes: \"Hello\" and 'World'";

      // These characters are encoded differently in Windows-1252 vs UTF-8
      const buffer = Buffer.from(windows1252Content, "binary");

      // When charset is properly specified, should decode correctly
      const result = convertToString(buffer, "windows-1252");
      expect(result).toContain("Hello");
      expect(result).toContain("World");
    });

    it("should gracefully handle invalid charset specifications", () => {
      const content = "Simple ASCII content";
      const buffer = Buffer.from(content, "utf-8");

      // Should fallback to UTF-8 for invalid charset
      const result = convertToString(buffer, "invalid-charset-name");
      expect(result).toBe(content);
    });
  });
});
