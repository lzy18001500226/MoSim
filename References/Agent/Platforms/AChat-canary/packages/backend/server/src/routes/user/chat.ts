import { appFactory } from "@server/factory";
import { createDataStream, streamText } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { stream, streamSSE } from "hono/streaming";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";
// import { createOpenAI } from '@ai-sdk/openai';
import { createProviderRegistry } from "ai";
import { describeRoute } from "hono-openapi";
import type { MiddlewareHandler } from "hono";
import { BizCodeEnum } from "@achat/error/biz";
import BizError from "@achat/error/biz";
import injectModelProvider from "@server/lib/provider-registry";
import { authGuard } from "@server/middleware/auth";
import { eq } from "drizzle-orm";
import {
  message as messageTable,
  messageClosure as messageClosureTable,
  type Conversation,
  conversation as conversationTable,
} from "@achat/database/schema";
const app = appFactory
  .createApp()
  // .use(
  //   describeRoute({
  //     tags: ["Chat"],
  //   })
  // )
  .use(authGuard("user"))
  .post(
    "/conversation/:id?",
    describeRoute({
      description: "Create a new conversation",
      responses: {
        200: {
          description: "Successful response",
          content: {
            "application/json": {},
          },
        },
      },
    }),
    zValidator(
      "param",
      z.object({
        id: z.string().optional(),
      })
    ),
    zValidator(
      "json",
      z.object({
        prompt: z.string(),
        providerModelId: z.string().uuid(),
      })
    ),
    injectModelProvider,
    async (c) => {
      const db = c.get("db");
      const user = c.get("user");

      const { id: conversationId } = c.req.valid("param");
      const input = c.req.valid("json");

      // let conversation: Conversation;
      // if (conversationId) {
      //   conversation = await db.insert(conversationTable).values({
      //     userId: user.id,
      //     modelId: c.get("modelId"),
      //   });
      // }

      // conversation = await db.query.conversation.findMany({
      //   where: (t, { eq }) => eq(t.userId, user.id),
      // });
      // if (!conversation) {
      //   throw new BizError(BizCodeEnum.ConversationNotFound);
      // }

      const result = streamText({
        model: anthropic("claude-3-5-sonnet-latest"),
        prompt: input.prompt,
        onFinish: (message) => {
          console.log(message);
        },
      });

      // Mark the response as a v1 data stream:
      c.header("X-Vercel-AI-Data-Stream", "v1");
      // c.header("Content-Type", "text/plain; charset=utf-8");

      return streamSSE(c, async (stream) => {
        const dataStream = result.toDataStream();
        for await (const chunk of dataStream) {
          stream.write(chunk);
        }
      });
    }
  )
  .get(
    "/conversation",
    describeRoute({
      description: "Get all conversations",
      responses: {
        200: {
          description: "Successful response",
          content: {
            "application/json": {},
          },
        },
      },
    }),
    async (c) => {
      const db = c.get("db");
      const user = c.get("user");
      const conversation = await db.query.conversation.findMany({
        where: (t, { eq }) => eq(t.userId, user.id),
      });
      return c.json(conversation);
    }
  )
  .get(
    "/conversation/:id",
    describeRoute({
      description: "Get a conversation by id ",
      responses: {
        200: {
          description: "Successful response",
          content: {
            "application/json": {},
          },
        },
      },
    }),
    (c) => {
      return c.json({
        status: "ok",
      });
    }
  )
  .get(
    "/conversation/:id/messages",
    describeRoute({
      description: "Get a conversation by id ",
      responses: {
        200: {
          description: "Successful response",
          content: {
            "application/json": {},
          },
        },
      },
    }),
    async (c) => {
      const db = c.get("db");
      const conversationId = c.req.param("id");
      const messages = await db
        .select({
          id: messageTable.id,
          conversationId: messageTable.conversationId,
          content: messageTable.content,
          role: messageTable.role,
          createdAt: messageTable.createdAt,
          updatedAt: messageTable.updatedAt,
          depth: messageClosureTable.depth,
        })
        .from(messageTable)
        .innerJoin(
          messageClosureTable,
          eq(messageTable.id, messageClosureTable.descendant)
        )
        .where(eq(messageTable.conversationId, conversationId));

      return c.json({ data: messages });
    }
  );

// .put(
//   "/message/:id",
//   describeRoute({
//     description: "Update a message",
//     responses: {
//       200: {
//         description: "Successful response",
//         content: {
//           "application/json": {},
//         },
//       },
//     },
//   }),
//   async (c) => {
//     const id = c.req.param("id");
//     return c.json({
//       status: "ok",
//     });
//   }
// )
// .delete(
//   "/message/:id",
//   describeRoute({
//     description: "Delete a message",
//     responses: {
//       200: {
//         description: "Successful response",
//         content: {
//           "application/json": {},
//         },
//       },
//     },
//   }),
//   async (c) => {
//     const id = c.req.param("id");
//     return c.json({
//       status: "ok",
//     });
//   }
// );

export default app;
