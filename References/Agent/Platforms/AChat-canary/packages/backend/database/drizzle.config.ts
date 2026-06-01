import "dotenv/config";

import { type Config, defineConfig } from "drizzle-kit";

export const dbUrl = process.env.DATABASE_URL;

if (!dbUrl) {
  throw "DATABASE_URL is not set";
}

export const drizzleConfig: Config = {
  dialect: "postgresql",
  schema: "./src/schema/schema.ts",
  out: "./drizzle/migrations/",
  dbCredentials: {
    url: dbUrl,
  },
  verbose: process.env.NODE_ENV === "development",
  breakpoints: false,
  strict: true,
};

export default defineConfig(drizzleConfig);
