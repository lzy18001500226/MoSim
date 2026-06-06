import { sql } from "drizzle-orm";
import type { NodePgDatabase } from "drizzle-orm/node-postgres";
import type { PgSequence } from "drizzle-orm/pg-core";

export class HiLoIdGenerator {
  private hi = 0;
  private lo = 0;
  private readonly maxLo: number;

  constructor(
    private readonly db: NodePgDatabase,
    private readonly sequence: PgSequence,
    maxLo = 1000
  ) {
    this.maxLo = maxLo;
    this.lo = maxLo; // 初始化时触发获取
  }

  private async fetchNextHi(): Promise<number> {
    const result = await this.db.execute(
      sql`SELECT nextval(${this.sequence.seqName}) as hi`
    );
    return Number(result.rows[0].hi);
  }

  public async nextId(): Promise<number> {
    if (this.lo >= this.maxLo) {
      this.hi = await this.fetchNextHi();
      this.lo = 0;
    }
    const id = this.hi * this.maxLo + this.lo;
    this.lo += 1;
    return id;
  }
}
