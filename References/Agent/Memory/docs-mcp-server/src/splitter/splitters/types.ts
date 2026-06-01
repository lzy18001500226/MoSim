/**
 * Common configuration options for content splitters
 */
export interface ContentSplitterOptions {
  /** Maximum characters per chunk */
  chunkSize: number;
}

/**
 * Core interface for content splitters
 */
export interface ContentSplitter {
  /** Split content into chunks respecting size constraints */
  split(content: string): Promise<string[]>;
}
