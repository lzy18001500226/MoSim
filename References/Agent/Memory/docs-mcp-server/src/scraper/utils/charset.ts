/**
 * Utility functions for enhanced charset detection and handling.
 */

import { logger } from "../../utils/logger";

/**
 * Detects charset from HTML meta tags.
 * Looks for both <meta charset="..."> and <meta http-equiv="Content-Type" content="text/html; charset=...">
 */
export function detectCharsetFromHtml(htmlContent: string): string | undefined {
  // Match <meta charset="..."> (HTML5 style)
  const charsetMatch = htmlContent.match(
    /<meta\s+charset\s*=\s*["']?([^"'>\s]+)["']?[^>]*>/i,
  );
  if (charsetMatch) {
    return charsetMatch[1].toLowerCase();
  }

  // Match <meta http-equiv="Content-Type" content="...charset=..."> (HTML4 style)
  const httpEquivMatch = htmlContent.match(
    /<meta\s+http-equiv\s*=\s*["']?content-type["']?\s+content\s*=\s*["']?[^"'>]*charset=([^"'>\s;]+)/i,
  );
  if (httpEquivMatch) {
    return httpEquivMatch[1].toLowerCase();
  }

  return undefined;
}

/**
 * Determines the best charset to use for decoding content.
 * Prioritizes HTML meta tags over HTTP headers for HTML content.
 */
export function resolveCharset(
  httpCharset: string | undefined,
  htmlContent: string | Buffer,
  mimeType: string,
): string {
  // For non-HTML content, use HTTP charset or default to UTF-8
  if (!mimeType.includes("html")) {
    return httpCharset || "utf-8";
  }

  // For HTML content, try to detect charset from meta tags
  let htmlString: string;
  try {
    // Try to decode as UTF-8 first to look for meta tags
    htmlString =
      typeof htmlContent === "string" ? htmlContent : htmlContent.toString("utf-8");
  } catch {
    // If UTF-8 fails, use the HTTP charset or fall back to latin1 for meta tag detection
    htmlString =
      typeof htmlContent === "string"
        ? htmlContent
        : htmlContent.toString((httpCharset || "latin1") as BufferEncoding);
  }

  // Look for charset in HTML meta tags (usually in first 1024 bytes)
  const headContent = htmlString.substring(0, 1024);
  const metaCharset = detectCharsetFromHtml(headContent);

  if (metaCharset) {
    logger.debug(`Detected charset from HTML meta tag: ${metaCharset}`);
    return metaCharset;
  }

  if (httpCharset) {
    logger.debug(`Using charset from HTTP header: ${httpCharset}`);
    return httpCharset;
  }

  logger.debug("No charset detected, defaulting to UTF-8");
  return "utf-8";
}

/**
 * Common charset aliases and their canonical names.
 * Helps handle cases where servers use non-standard charset names.
 */
export const CHARSET_ALIASES: Record<string, string> = {
  "iso-8859-1": "latin1",
  "iso_8859-1": "latin1",
  "latin-1": "latin1",
  "windows-1252": "cp1252",
  "cp-1252": "cp1252",
  "ms-ansi": "cp1252",
  utf8: "utf-8",
  unicode: "utf-8",
  "us-ascii": "ascii",
  ascii: "ascii",
};

/**
 * Normalizes charset name to handle common aliases.
 */
export function normalizeCharset(charset: string): string {
  const normalized = charset.toLowerCase().trim();
  return CHARSET_ALIASES[normalized] || normalized;
}
