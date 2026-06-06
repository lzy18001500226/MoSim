import "dotenv/config";
import { init as initSentry } from "./lib/plugins/sentry";
initSentry();
import "zod-openapi/extend";

/* Server */
import type { Server as HttpServer } from "node:http";
import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { showRoutes } from "hono/dev";

/* API Documentation */
import { Scalar } from "@scalar/hono-api-reference";
import { openAPISpecs } from "hono-openapi";

/* Middleware */
import { sentry } from "@hono/sentry";
import { cors } from "hono/cors";
import { requestId } from "hono/request-id";
import type { ContentfulStatusCode } from "hono/utils/http-status";
import { v7 as uuidv7 } from "uuid";
import connInfoMiddleware from "./middleware/conn-info";
import loggerMiddleware from "./middleware/logger";

/* Error */
import { DatabaseError } from "pg";
import { UserFriendlyError } from "@achat/error";
import BizError, { BizCodeEnum } from "@achat/error/biz";

/* Business Routes */
import systemRouter from "./routes/system";
import userRouter from "./routes/user";
import adminRouter from "./routes/admin";

/* Context Extension */
import type { ConnInfo } from "hono/conninfo";
// import type { Redis } from "ioredis";
import type { Logger } from "winston";
import { auth, type Auth } from "./lib/auth";
import type { DataBase } from "./lib/database";
// import { inngestHandler } from "./queues";

declare module "hono" {
  interface ContextVariableMap {
    tenantId: string;
    db: DataBase;
    auth: Auth;
    logger: Logger;
    connInfo: ConnInfo & { ip: string };
  }
}

const app = new Hono().basePath("/api");
/* Error Handle */
app.onError((err, c) => {
  if (err instanceof BizError) {
    return c.json(
      {
        code: err.code,
        message: err.message,
      },
      err.statusCode as ContentfulStatusCode
    );
  }
  // if (err instanceof DatabaseError) {
  //   return c.json(
  //     {
  //       code: BizCodeEnum.DatabaseError,
  //       message: err.code,
  //     },
  //     500
  //   );
  // }
  console.error(err);
  return c.json(
    {
      message: "Internal Server Error",
    },
    500
  );
});

/*
================
== Middleware ==
================
*/
// 1. CORS
app.use(
  "*",
  cors({
    origin: ["http://localhost:3000"],
    allowHeaders: [
      "Content-Type",
      "Authorization",
      "Upgrade-Insecure-Requests",
    ],
    allowMethods: ["GET", "HEAD", "PUT", "POST", "DELETE", "PATCH", "OPTIONS"],
    exposeHeaders: ["Content-Length", "X-Kuma-Revision"],
    maxAge: 600,
    credentials: true,
  })
);
// 2. Request ID
app.use(
  requestId({
    generator: () => uuidv7(),
  })
);
// 3. Monitor
if (process.env.SENTRY_DSN) {
  app.use(
    sentry({
      dsn: process.env.SENTRY_DSN,
    })
  );
}
// 4. Connection Info
app.use(connInfoMiddleware);
// 5. Logger
app.use(loggerMiddleware);

/*
==============
=== Routes ===
==============
*/
// 1. Task Queue
// app.on(["GET", "PUT", "POST"], "/inngest", inngestHandler);
// 2. Authentication
app.on(["POST", "GET"], "/auth/:path{.+}", (c) => {
  // const auth = c.get("auth");
  return auth.handler(c.req.raw);
});
// 3. Business Routes
export const routes = new Hono()
  .route("/system", systemRouter)
  .route("/admin", adminRouter)
  .route("/user", userRouter);

app.route("/", routes);

// 4. API Documentation
app.get(
  "/docs",
  Scalar({
    theme: "purple",
    url: "/api/openapi",
  })
);

app.get(
  "/openapi",
  openAPISpecs(routes, {
    documentation: {
      info: {
        title: "AChat API",
        description:
          "Auth OpenAPI Document: <a href='/api/auth/reference'>/api/auth/reference</a>",
        version: "4.0.0",
      },
      servers: [{ url: "/api", description: "Local Server" }],
      "x-tagGroups": [
        {
          name: "System",
          tags: ["Health", "Setup"],
        },
        {
          name: "User",
          tags: ["Chat"],
        },
        {
          name: "Admin",
          tags: ["Model"],
        },
      ],
    },
  })
);

const run = async () => {
  const port = process.env.PORT ? Number(process.env.PORT) : 3001;
  const server = serve({ fetch: app.fetch, port }, ({ address, port }) => {
    console.log(`Server is running on ${address}:${port}...`);
    showRoutes(app);
  });
  // setupSocketIOServer(server as HttpServer);
};

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
