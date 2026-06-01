import iconv from "iconv-lite";
import { normalizeCharset } from "./charset";

/**
 * Decodes a Buffer or string to a JavaScript string using the specified charset.
 * The charset should be the encoding as reported by the source (e.g., HTTP header).
 * The result is always a valid JS string (Unicode/UTF-16).
 *
 * If the charset is missing or unsupported, falls back to UTF-8.
 *
 * @param content The content to decode (Buffer or string)
 * @param charset The source encoding (e.g., 'utf-8', 'iso-8859-1', 'utf-16le', etc.)
 * @returns The decoded string
 */
export function convertToString(content: string | Buffer, charset?: string): string {
  if (typeof content === "string") return content;

  const normalizedCharset = charset ? normalizeCharset(charset) : "utf-8";

  try {
    return iconv.decode(content, normalizedCharset);
  } catch {
    // Fallback to utf-8 if decoding fails
    try {
      return iconv.decode(content, "utf-8");
    } catch {
      // Last resort: decode as latin1 which can handle any byte sequence
      return iconv.decode(content, "latin1");
    }
  }
}
