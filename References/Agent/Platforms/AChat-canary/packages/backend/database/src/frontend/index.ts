export { PgDialect } from 'drizzle-orm/pg-core';
import { drizzle as PgLiteDrizzle } from "drizzle-orm/pglite";
import { schema } from "./schema";
import migrations from "./export.json";

export const frontMigrations = migrations;

export const createPgLiteClient = (client: any) => {
  return PgLiteDrizzle(client, {
    schema,
  });
};

export default createPgLiteClient;