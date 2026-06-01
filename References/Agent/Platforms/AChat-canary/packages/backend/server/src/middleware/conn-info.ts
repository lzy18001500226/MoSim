import { getConnInfo } from "@hono/node-server/conninfo";
import type { Context, MiddlewareHandler, Next } from "hono";
import type { ConnInfo } from "hono/conninfo";

const connInfoMiddleware: MiddlewareHandler<{
  Variables: { connInfo: ConnInfo & { ip: string } };
}> = async (c: Context, next: Next) => {
  const connInfo = getConnInfo(c);
  const ip =
    c.req?.header("cf-connecting-ip") ||
    // c.req?.header("x-real-ip") || // traefik get bad on this header
    c.req
      ?.header("x-forwarded-for")
      ?.split(",")[0]
      .trim() ||
    c.req?.header("x-forwarded-for");
  connInfo.remote.address?.replace("::ffff:", "") || "127.0.0.1";
  c.set("connInfo", {
    ip,
    remote: connInfo.remote,
  });
  await next();
};

export default connInfoMiddleware;
