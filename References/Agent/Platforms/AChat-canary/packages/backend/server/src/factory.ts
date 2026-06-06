import { createFactory } from "hono/factory";
import { auth, type AuthSession } from "./lib/auth";
import { authMiddleware } from "./middleware/auth";
import db from "./lib/database";

export const appFactory = createFactory<{
  Variables: {
    user: AuthSession["user"] | null;
    session: AuthSession["session"] | null;
  };
}>({
  initApp: (app) => {
    app.use(authMiddleware);
    app.use(async (c, next) => {
      c.set("db", db);
      c.set("auth", auth);
      await next();
    });
  },
});
