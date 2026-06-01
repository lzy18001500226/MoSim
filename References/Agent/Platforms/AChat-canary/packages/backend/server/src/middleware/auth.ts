import type { AuthSession } from "@server/lib/auth";
import type { MiddlewareHandler } from "hono";
import { auth } from "@server/lib/auth";
import { BizCodeEnum } from "@achat/error/biz";
import BizError from "@achat/error/biz";

export const authMiddleware: MiddlewareHandler<{
  Variables: {
    user: AuthSession["user"] | null;
    session: AuthSession["session"] | null;
  };
}> = async (c, next) => {
  // const auth = c.get("auth");
  c.set("auth", auth);
  const session = await auth.api.getSession({ headers: c.req.raw.headers });

  if (!session) {
    c.set("user", null);
    c.set("session", null);
    return next();
  }

  c.set("user", session.user);
  c.set("session", session.session);
  return next();
};

export const authGuard =
  (
    role: "user" | "admin"
  ): MiddlewareHandler<{
    Variables: {
      user: AuthSession["user"];
      session: AuthSession["session"];
    };
  }> =>
  async (c, next) => {
    const user = c.var.user;
    if (!user) {
      throw new BizError(BizCodeEnum.Unauthorized);
    }
    if (role === "admin" && user.role !== "admin") {
      throw new BizError(BizCodeEnum.Forbidden);
    }
    return next();
  };
