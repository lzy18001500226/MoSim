import fs from "node:fs/promises";
import { readMigrationFiles } from "drizzle-orm/migrator";
import { migrationsFolder } from "./drizzle.web.config";

const file = "./src/frontend/export.json";

// Read all migration files
const allMigrations = readMigrationFiles({
  migrationsFolder,
});


await fs.writeFile(
  `${file}`,
  JSON.stringify(allMigrations, null, 2),
  {
    flag: "w",
  }
);