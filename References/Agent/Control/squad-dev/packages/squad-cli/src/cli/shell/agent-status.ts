/**
 * Shared agent status rendering — single source of truth for /agents command and AgentPanel.
 *
 * Status enum: 'working' | 'streaming' | 'idle' | 'error'
 */

import { getRoleEmoji } from './lifecycle.js';
import type { AgentSession } from './types.js';

/** Canonical status tag for display in both TUI and text contexts. */
export function getStatusTag(status: AgentSession['status']): string {
  switch (status) {
    case 'working':
      return '[WORK]';
    case 'streaming':
      return '[STREAM]';
    case 'error':
      return '[ERR]';
    case 'idle':
      return '[IDLE]';
  }
}

/** Format a single agent line for plain-text output (used by /agents and /status commands). */
export function formatAgentLine(agent: AgentSession): string {
  const emoji = getRoleEmoji(agent.role);
  const tag = getStatusTag(agent.status);
  return `  ${emoji} ${agent.name} ${tag} (${agent.role})`;
}
