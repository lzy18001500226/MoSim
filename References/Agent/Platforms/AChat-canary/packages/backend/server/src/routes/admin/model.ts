import BizError, { BizCodeEnum } from "@achat/error/biz";
import { appFactory } from "@server/factory";
import { authGuard } from "@server/middleware/auth";
import { describeRoute } from "hono-openapi";

const app = appFactory
  .createApp()
  .use(authGuard("admin"))
  .post(
    "/provider",
    describeRoute({
      description: "Install a model provider in the organization",
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
      const session = c.get("session");
      if (!session.activeOrganizationId) {
        throw new BizError(BizCodeEnum.OrganizationNotFound);
      }
    }
  )
  .get(
    "/provider",
    describeRoute({
      description: "Get all model providers",
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
    async (c) => {
      const db = c.get("db");
      const user = c.get("user");
      const session = c.get("session");
      if (!session.activeOrganizationId) {
        throw new BizError(BizCodeEnum.OrganizationNotFound);
      }
      const providers = await db.query.provider.findMany({
        where: (t, { and, eq }) =>
          and(
            session.activeOrganizationId
              ? eq(t.organizationId, session.activeOrganizationId)
              : undefined,
            eq(t.isValid, true)
          ),
      });
      return c.json(providers);
    }
  )
  .post(
    "/provider",
    describeRoute({
      description: "Update a model provider in the organization",
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
      const session = c.get("session");
      if (!session.activeOrganizationId) {
        throw new BizError(BizCodeEnum.OrganizationNotFound);
      }
    }
  );

export default app;
