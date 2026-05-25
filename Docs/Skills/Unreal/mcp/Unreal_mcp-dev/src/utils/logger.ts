export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

const LOG_LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3
};

const LOG_LEVELS = new Set<LogLevel>(['debug', 'info', 'warn', 'error']);

export class Logger {
  private level: LogLevel;

  constructor(private scope: string, level: LogLevel = 'info') {
    const envLevel = (process.env.LOG_LEVEL || process.env.LOGLEVEL || level).toString().toLowerCase();
    this.level = LOG_LEVELS.has(envLevel as LogLevel)
      ? (envLevel as LogLevel)
      : 'info';
  }

  private shouldLog(level: LogLevel) {
    return LOG_LEVEL_ORDER[level] >= LOG_LEVEL_ORDER[this.level];
  }

  isEnabled(level: LogLevel): boolean {
    return this.shouldLog(level);
  }

  debug(...args: unknown[]) {
    if (!this.shouldLog('debug')) return;
    // Write to stderr to avoid corrupting MCP stdout stream
    console.error(`[${this.scope}]`, ...args);
  }
  info(...args: unknown[]) {
    if (!this.shouldLog('info')) return;
    // Write to stderr to avoid corrupting MCP stdout stream
    console.error(`[${this.scope}]`, ...args);
  }
  warn(...args: unknown[]) {
    if (!this.shouldLog('warn')) return;
    console.error(`[${this.scope}]`, ...args);
  }
  error(...args: unknown[]) {
    if (this.shouldLog('error')) console.error(`[${this.scope}]`, ...args);
  }
}
