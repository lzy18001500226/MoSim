/**
 * Generate a filename-safe ISO 8601 timestamp.
 * Replaces colons with hyphens for Windows compatibility.
 */
export function safeTimestamp(): string {
  return new Date().toISOString().replace(/:/g, '-').replace(/\.\d{3}Z$/, 'Z');
}
