import {
  integer,
  jsonb,
  pgTable,
  text,
  varchar,
} from "drizzle-orm/pg-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import { timeColumns } from "../utils/columns";

export const config = pgTable("config", {
  id: integer("id").primaryKey().generatedByDefaultAsIdentity({
    startWith: 1000,
  }),

  key: varchar("key").notNull(),
  value: jsonb("value").notNull().default({}),
  note: text("note"),

  ...timeColumns(),
});

export const Config = createSelectSchema(config);
export type Config = typeof config.$inferSelect;
export const NewConfig = createInsertSchema(config);
export type NewConfig = typeof config.$inferInsert;