import BizError, { BizCodeEnum } from "@achat/error/biz";
import { anthropic, createAnthropic } from "@ai-sdk/anthropic";
import type { AuthSession } from "@server/lib/auth";
import {
  createProviderRegistry,
  type ProviderRegistryProvider,
  type Provider,
} from "ai";
import { createMiddleware } from "hono/factory";

const injectModelProvider = createMiddleware<{
  Variables: {
    user: AuthSession["user"];
    session: AuthSession["session"];
    modelProvider: ProviderRegistryProvider<Record<string, Provider>, "/">;
  };
}>(async (c, next) => {
  const user = c.get("user");
  const session = c.get("session");
  // const organizationId = session.activeOrganizationId;
  // if (!organizationId) {
  //   throw new BizError(BizCodeEnum.OrganizationNotFound);
  // }
  // const providers = await c.get("db").query.provider.findMany({
  //   where: (t, { eq }) => eq(t.organizationId, organizationId),
  // });
  // const registryProviders = providers.map((provider) => {
  //   if (provider.providerType === "anthropic") {
  //     return {
  //       anthropic: createAnthropic({
  //         apiKey: provider.config?.apiKey,
  //       }),
  //     };
  //   }
  //   return {};
  // });
  // const modelProvider = createProviderRegistry(registryProviders, {
  //   separator: "/",
  // });
  const modelProvider = createProviderRegistry(
    {
      anthropic,
    },
    {
      separator: "/",
    }
  );
  c.set("modelProvider", modelProvider);
  return next();
});

export default injectModelProvider;
