import { execSync } from "node:child_process";
import { getPostgresContainer } from "../helpers/env";

/**
 * Database fixture for E2E tests.
 * Executes SQL via `docker exec` against the dev PostgreSQL container.
 */
export class DbFixture {
  private container: string;

  constructor() {
    this.container = getPostgresContainer();
  }

  /**
   * Execute a SQL statement and return the output.
   */
  exec(sql: string): string {
    const escaped = sql.replace(/'/g, "'\\''");
    const cmd = `docker exec ${this.container} psql -U agentsmesh -d agentsmesh -t -A -c '${escaped}'`;
    return execSync(cmd, { encoding: "utf-8", timeout: 10_000 }).trim();
  }

  /**
   * Execute setup SQL (typically INSERT statements for test data).
   */
  setup(sql: string): void {
    this.exec(sql);
  }

  /**
   * Execute cleanup SQL (typically DELETE statements).
   */
  cleanup(sql: string): void {
    this.exec(sql);
  }

  /**
   * Query a single value from the database.
   */
  queryValue(sql: string): string | null {
    const result = this.exec(sql);
    return result || null;
  }
}
