import { dbPool, getDb } from "@achat/database";

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL is not set");
}

const pool = dbPool(process.env.DATABASE_URL);
const db = getDb(pool);

export default db;
export type DataBase = typeof db;