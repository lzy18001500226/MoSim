import { PGlite } from "@electric-sql/pglite";
import { drizzle } from "drizzle-orm/pglite";
import RedisMock from "ioredis-mock";
import { afterAll, afterEach, beforeEach, vi } from "vitest";
import * as schema from "@achat/database/schema";

vi.mock("ioredis", () => ({
  Redis: RedisMock,
}));

vi.mock("@achat/database/schema", () => ({
  configTable: {
    key: "key",
    value: "value",
  },
}));

vi.mock("@server/lib/db", async (importOriginal) => {
  const client = new PGlite();
  const db = drizzle(client, { schema });
  return {
    ...(await importOriginal<typeof import("@server/lib/database")>()),
    db,
    client,
  };
});

// Apply migrations before each test
beforeEach(async () => {
  // await applyMigrations();
});

// Clean up the database after each test
afterEach(async () => {
  // await db.execute(sql`drop schema if exists public cascade`);
  // await db.execute(sql`create schema public`);
  // await db.execute(sql`drop schema if exists drizzle cascade`);
});

// Free up resources after all tests are done
afterAll(async () => {
  // client.close();
});