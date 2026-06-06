import { appFactory } from "@server/factory";
import { describeRoute } from "hono-openapi";
import { resolver, validator as zValidator } from "hono-openapi/zod";
import { z } from "zod";
import BizError, { BizCodeEnum } from "@achat/error/biz";

let isSetup: boolean | undefined = undefined;

const app = appFactory
  .createApp()
  .use(
    describeRoute({
      tags: ["Setup"],
    })
  )
  .get(
    "/status",
    describeRoute({
      description: "Check if initial setup has been completed",
      responses: {
        200: {
          description: "Setup status",
          content: {
            "application/json": {
              schema: resolver(
                z.object({
                  isSetup: z.boolean(),
                })
              ),
            },
          },
        },
      },
    }),
    async (c) => {
      const db = c.get("db");

      if (isSetup !== undefined) {
        return c.json({
          isSetup,
        });
      }

      // Check if there's already an admin user
      const adminUser = await db.query.user.findFirst({
        where: (t, { eq }) => eq(t.role, "admin"),
      });

      isSetup = !!adminUser;

      return c.json({
        isSetup,
      });
    }
  )
  .post(
    "/admin",
    describeRoute({
      description: "Create the initial admin account",
      responses: {
        200: {
          description: "Admin account created successfully",
          content: {
            "application/json": {
              schema: {
                type: "object",
                properties: {
                  success: { type: "boolean" },
                  message: { type: "string" },
                },
              },
            },
          },
        },
        409: {
          description: "Admin already exists",
        },
      },
    }),
    zValidator(
      "json",
      z.object({
        name: z.string().min(2).max(100),
        email: z.string().email(),
        password: z.string().min(8).max(128),
      })
    ),
    async (c) => {
      if (isSetup) {
        throw new BizError(BizCodeEnum.Conflict);
      }

      const { name, email, password } = c.req.valid("json");
      const auth = c.get("auth");
      const db = c.get("db");

      // Check if there's already an admin user
      const existingAdmin = await db.query.user.findFirst({
        where: (t, { eq }) => eq(t.role, "admin"),
      });

      if (existingAdmin) {
        throw new BizError(BizCodeEnum.EmailAlreadyUsed);
      }

      // Create the admin user using better-auth API
      const result = await auth.api.createUser({
        body: {
          name,
          email,
          password,
          role: "admin",
        },
      });

      if (!result || !result.user) {
        throw new BizError(BizCodeEnum.RegisterFailed);
      }

      return c.json(result.user);
    }
  );

export default app;
