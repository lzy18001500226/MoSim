// src/types/report.ts

import type { ContextFilePath } from './context';
import type { TaskID } from './id';

/**
 * Path to a report file relative to context/reports/
 *
 * Structure: context/reports/<session-id>/<task-id>.md
 *
 * Examples:
 * - "01933e4a-7b89-7c35-a8f3-9d2e1c4b5a6f/0193a1b2-3c4d-7e5f-a8f3-9d2e1c4b5a6f.md"
 * - "01934c2d-1234-7c35-a8f3-9d2e1c4b5a6f/0193b3c4-5d6e-7f8a-b9c0-d1e2f3a4b5c6.md"
 */
export type ReportPath = string;

/**
 * Template type for report generation
 *
 * Different templates structure the report differently:
 * - "standard": Default template with learnings, decisions, blockers
 * - "technical": Deep dive into technical decisions and trade-offs
 * - "summary": Brief summary of work completed
 * - "custom": User-defined template
 */
export type ReportTemplate = 'standard' | 'technical' | 'summary' | 'custom';

/**
 * Report metadata
 *
 * Reports are auto-generated after task completion, capturing:
 * - What was learned during the task
 * - Key decisions made
 * - Concepts that emerged
 * - Blockers encountered
 */
export interface Report {
  /**
   * File path relative to context/reports/
   * This serves as the unique identifier.
   *
   * Format: "<session-id>/<task-id>.md"
   */
  path: ReportPath;

  /** Task this report belongs to */
  task_id: TaskID;

  /** Template used for report generation */
  template: ReportTemplate;

  /** Markdown content of the report */
  content: string;

  /**
   * Context files extracted or referenced in this report
   * Can reference existing context files or suggest new ones
   */
  contextFiles: ContextFilePath[];

  /** When the report was generated */
  generated_at: string;

  /** File metadata */
  created_at: string;
  last_updated: string;
}
