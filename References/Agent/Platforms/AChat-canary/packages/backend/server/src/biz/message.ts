import type { DataBase } from "@server/lib/database";
import {
  message as messageTable,
  conversation as conversationTable,
  type NewMessage,
  Conversation,
  type Message,
} from "@achat/database/schema";
import { eq } from "drizzle-orm";
import { createMiddleware } from "hono/factory";

/**
 */
class MessageImpl {
  constructor(private db: DataBase) {}

  async createMessage(value: NewMessage): Promise<Message> {
    return await this.db.transaction(async (tx) => {
      const conversationId =
        value.conversationId ??
        (
          await tx
            .insert(conversationTable)
            .values({
              organizationId: value.organizationId,
              userId: value.userId,
              modelId: value.modelId,
              title: "New Conversation",
            })
            .returning({
              id: conversationTable.id,
            })
        )[0].id;
      const message = (
        await tx
          .insert(messageTable)
          .values({
            ...value,
            conversationId,
          })
          .returning()
      )[0];
      await tx
        .update(conversationTable)
        .set({
          rootMessageId: message.id,
        })
        .where(eq(conversationTable.id, conversationId));
      if (!value.conversationId) {
        await tx
          .update(conversationTable)
          .set({
            rootMessageId: message.id,
          })
          .where(eq(conversationTable.id, conversationId));
      }
      return message;
    });
  }

  /**
   * Delete a single message (automatically deletes closure relationships, but not child nodes)
   * Because of the foreign key cascade deletion, deleting a message will automatically delete the related closure relationships
   * @param messageId - The ID of the message to delete
   * @returns The deleted message
   */
  async deleteMessage(messageId: string) {
    const deletedMessage = await this.db
      .delete(messageTable)
      .where(eq(messageTable.id, messageId))
      .returning();

    return deletedMessage[0] || null;
  }
}

export const injectMessageImpl = createMiddleware(async (c, next) => {
  c.set("messageImpl", new MessageImpl(c.get("db")));
  await next();
});

export default MessageImpl;
