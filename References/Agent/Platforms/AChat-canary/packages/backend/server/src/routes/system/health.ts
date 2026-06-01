import { describeRoute } from "hono-openapi";
import { accepts } from "hono/accepts";
import { Hono } from "hono";

const app = new Hono()
  .use(
    describeRoute({
      tags: ["Health"],
    })
  )
  .get(
    "/",
    describeRoute({
      description:
        "Health check endpoint that returns the system status in either plain text or JSON format",
      responses: {
        200: {
          description: "Successful response",
          content: {
            "text/plain": {
              schema: {
                type: "string",
                example: "ok",
              },
            },
            "application/json": {
              schema: {
                type: "object",
                properties: {
                  status: { type: "string", example: "ok" },
                },
              },
            },
          },
        },
      },
    }),
    (c) => {
      const accept = accepts(c, {
        header: "Accept",
        supports: ["text/plain", "application/json"],
        default: "text/plain",
      });
      if (accept === "application/json") {
        return c.json({
          status: "ok",
        });
      }
      return c.text("ok");
    }
  );

export default app;
