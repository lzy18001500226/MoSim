import { drizzle } from "drizzle-orm/node-postgres";
import * as schema from "./schema";
import pg from "pg";

export const dbPool = (databaseUrl: string) =>
  new pg.Pool({
    connectionString: databaseUrl,
  });

export const getDb = (pool: pg.Pool) =>
  drizzle(pool, {
    schema: {
      ...schema,
    },
  });

export type DataBase = ReturnType<typeof drizzle<typeof schema>>;
