// src/types/context.ts

/**
 * Path to a context file (markdown) relative to context/
 *
 * Examples:
 * - "README.md"
 * - "concepts/core.md"
 * - "explorations/subsession-orchestration.md"
 */
export type ContextFilePath = string;

/**
 * Context file list item (lightweight, for browsing)
 * Returned by GET /context
 */
export interface ContextFileListItem {
  /**
   * File path relative to context/
   * Examples: "concepts/core.md", "explorations/cli.md", "README.md"
   */
  path: ContextFilePath;

  /** Human-readable title (extracted from first H1 or filename) */
  title: string;

  /** File size in bytes */
  size: number;

  /** Last modified timestamp (ISO 8601) */
  lastModified: string;
}

/**
 * Full context file details (includes content)
 * Returned by GET /context/:path
 */
export interface ContextFileDetail extends ContextFileListItem {
  /** Full markdown content */
  content: string;
}
