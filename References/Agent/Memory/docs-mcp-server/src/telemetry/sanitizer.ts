/**
 * Data sanitization utilities for privacy-first telemetry.
 * Simplified to only include essential functions we actually use.
 */

/**
 * Extracts hostname from URL for aggregated analytics without exposing paths.
 * Examples:
 * - https://docs.python.org/3/library/os.html -> docs.python.org
 * - https://github.com/owner/repo -> github.com
 * - http://localhost:3000/api -> localhost
 */
export function extractHostname(url: string): string {
  try {
    const parsed = new URL(url);
    return parsed.hostname;
  } catch {
    return "invalid-hostname";
  }
}

/**
 * Extracts protocol from URL or file path for privacy-safe analytics.
 * Examples:
 * - https://github.com/owner/repo -> "https"
 * - file:///local/path -> "file"
 * - /local/path -> "file" (detected as local file)
 * - C:\local\path -> "file" (detected as local file)
 */
export function extractProtocol(urlOrPath: string): string {
  try {
    const parsed = new URL(urlOrPath);
    return parsed.protocol.replace(":", "");
  } catch {
    // If URL parsing fails, check if it looks like a local file path
    if (urlOrPath.startsWith("/") || /^[A-Za-z]:/.test(urlOrPath)) {
      return "file";
    }
    return "unknown";
  }
}

/**
 * Analyzes search query patterns without storing content.
 * Returns metadata about the query for usage analytics.
 */
export function analyzeSearchQuery(query: string): {
  length: number;
  wordCount: number;
  hasCodeTerms: boolean;
  hasSpecialChars: boolean;
} {
  return {
    length: query.length,
    wordCount: query.trim().split(/\s+/).length,
    hasCodeTerms:
      /\b(function|class|import|export|const|let|var|def|async|await)\b/i.test(query),
    hasSpecialChars: /[^\w\s]/.test(query),
  };
}

/**
 * Sanitizes error messages to remove sensitive information while preserving diagnostic value.
 * Examples:
 * - "Failed to fetch https://secret.com/api" -> "Failed to fetch [url]"
 * - "File not found: /home/user/secret.txt" -> "File not found: [path]"
 */
export function sanitizeErrorMessage(message: string): string {
  return message
    .replace(/https?:\/\/[^\s]+/gi, "[url]")
    .replace(/file:\/\/[^\s]+/gi, "[file-url]")
    .replace(/\/[^\s]*\.[a-z]{2,4}/gi, "[path]")
    .replace(/[A-Za-z]:\\[^\s]+/g, "[path]")
    .replace(/Bearer\s+[^\s]+/gi, "Bearer [token]")
    .replace(/api[_-]?key[=:]\s*[^\s]+/gi, "api_key=[redacted]")
    .replace(/token[=:]\s*[^\s]+/gi, "token=[redacted]")
    .substring(0, 200); // Limit length
}

/**
 * Sanitizes error information for telemetry collection.
 * Simple approach: just track error type and sanitized message.
 */
export function sanitizeError(error: Error): {
  type: string;
  message: string;
  hasStack: boolean;
} {
  return {
    type: error.constructor.name,
    message: sanitizeErrorMessage(error.message),
    hasStack: Boolean(error.stack),
  };
}

/**
 * Extract CLI flags from process arguments for telemetry (without values)
 * Examples:
 * - ["--verbose", "--max-depth", "3"] -> ["--verbose", "--max-depth"]
 */
export function extractCliFlags(argv: string[]): string[] {
  return argv.filter((arg) => arg.startsWith("--") || arg.startsWith("-"));
}
