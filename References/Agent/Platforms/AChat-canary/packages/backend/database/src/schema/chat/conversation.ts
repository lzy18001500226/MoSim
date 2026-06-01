import {
  pgTable,
  timestamp,
  uuid,
  varchar,
  type AnyPgColumn,
} from "drizzle-orm/pg-core";
import { organization } from "../auth/organization";
import { user } from "../auth/user";
import { timeColumns } from "../../utils/columns";
import { createSelectSchema, createInsertSchema } from "drizzle-zod";
import { message } from "./message";
import { providerModels } from "../provider/model";
import { v7 as uuidv7 } from "uuid";

export const conversation = pgTable("conversation", {
  id: uuid("id").primaryKey().$defaultFn(uuidv7),
  organizationId: uuid("organization_id")
    .notNull()
    .references(() => organization.id),
  userId: uuid("user_id")
    .notNull()
    .references(() => user.id),
  modelId: uuid("model_id").references(() => providerModels.id, {
    onDelete: "set null",
  }),

  title: varchar("title", { length: 255 }).notNull(),

  // modelId: integer("model_id").references(() => models.id), // AI model used
  rootMessageId: uuid("root_message_id").references(
    (): AnyPgColumn => message.id,
    {
      onDelete: "set null",
    }
  ),
  ...timeColumns(),
  deletedAt: timestamp("deleted_at", { withTimezone: true }),
});
export const Conversation = createSelectSchema(conversation);
export type Conversation = typeof conversation.$inferSelect;
export const NewConversation = createInsertSchema(conversation);
export type NewConversation = typeof conversation.$inferInsert;
