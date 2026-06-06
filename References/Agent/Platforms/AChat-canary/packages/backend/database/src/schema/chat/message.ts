import {
  index,
  integer,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uuid,
  type AnyPgColumn,
} from "drizzle-orm/pg-core";
import { conversation } from "./conversation";
import { timeColumns } from "../../utils/columns";
import { user } from "../auth/user";
import { organization } from "../auth/organization";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import { z } from "zod";
import { providerModels } from "../provider/model";
import { v7 as uuidv7 } from "uuid";

export const MessageRole = z.enum(["user", "system", "assistant", "tool"]);
export const message = pgTable("message", {
  id: uuid("id").primaryKey().$defaultFn(uuidv7),
  conversationId: uuid("conversation_id")
    .references((): AnyPgColumn => conversation.id)
    .notNull(),
  organizationId: uuid("organization_id")
    .notNull()
    .references(() => organization.id, {
      onDelete: "cascade",
    }),
  userId: uuid("user_id")
    .notNull()
    .references(() => user.id),
  modelId: uuid("model_id").references(() => providerModels.id, {
    onDelete: "set null",
  }),
  content: text("content").notNull(), // Raw text
  role: text("role", {
    enum: MessageRole._def.values,
  }).notNull(),
  //   status: varchar("status", { enum: ["pending", "processed", "failed"] }),
  //   usage: jsonb("usage"),
  ...timeColumns(),
  deletedAt: timestamp("deleted_at", { withTimezone: true }),
});
export const Message = createSelectSchema(message);
export type Message = typeof message.$inferSelect;
export const NewMessage = createInsertSchema(message, {
  conversationId: (s) => s.optional(),
}).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type NewMessage = z.infer<typeof NewMessage>;

export const messageClosure = pgTable(
  "message_closure",
  {
    conversationId: uuid("conversation_id")
      .references(() => conversation.id)
      .notNull(),
    ancestor: uuid("ancestor")
      .references(() => message.id, { onDelete: "cascade" })
      .notNull(),
    descendant: uuid("descendant")
      .references(() => message.id, { onDelete: "cascade" })
      .notNull(),
    depth: integer("depth").notNull(),
  },
  (t) => [
    primaryKey({ columns: [t.ancestor, t.descendant] }),
    index().on(t.conversationId),
    index().on(t.ancestor),
    index().on(t.descendant),
  ]
);
export const MessageClosure = createSelectSchema(messageClosure);
export type MessageClosure = typeof messageClosure.$inferSelect;
export const NewMessageClosure = createInsertSchema(messageClosure);
export type NewMessageClosure = typeof messageClosure.$inferInsert;
