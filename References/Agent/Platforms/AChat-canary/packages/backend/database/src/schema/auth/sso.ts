import { pgTable, text, uuid } from "drizzle-orm/pg-core";
import { user } from "./user";
import { organization } from "./organization";

export const ssoProvider = pgTable("sso_provider", {
  id: uuid("id").primaryKey(),
  issuer: text("issuer").notNull(),
  domain: text("domain").notNull(),
  oidcConfig: text("oidc_config").notNull(),
  userId: uuid("user_id")
    .notNull()
    .references(() => user.id),
  providerId: uuid("provider_id").notNull(),
  organizationId: uuid("organization_id").references(() => organization.id),
});
