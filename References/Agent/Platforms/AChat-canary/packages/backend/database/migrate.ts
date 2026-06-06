import "dotenv/config";

import { migrate } from "drizzle-orm/node-postgres/migrator";
import { drizzle } from "drizzle-orm/node-postgres";

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL is not set");
}
const db = drizzle(process.env.DATABASE_URL);

export async function runMigrate() {
  console.log("⏳ Running migrations...");

  const start = Date.now();

  await migrate(db, { migrationsFolder: "drizzle" });

  const end = Date.now();

  console.log(`✅ Migrations completed in ${end - start}ms`);
}

runMigrate()
  .then(() => {
    process.exit(0);
  })
  .catch((err) => {
    console.error("❌ Migration failed");
    console.error(err);
    process.exit(1);
  });
