import { defineConfig } from "drizzle-kit";
import { drizzleConfig } from "./drizzle.config";

export const migrationsFolder = "./drizzle/frontend/migrations";

export default defineConfig({
  ...drizzleConfig,
  schema: "./src/frontend/schema.ts",
  out: migrationsFolder,
  verbose: true,
});
