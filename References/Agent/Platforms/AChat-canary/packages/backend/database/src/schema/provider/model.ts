import {
  bigint,
  boolean,
  jsonb,
  pgTable,
  timestamp,
  uuid,
  varchar,
} from "drizzle-orm/pg-core";
import { organization } from "../auth/organization";
import { timeColumns } from "../../utils/columns";
import z from "zod";
import { createSelectSchema, createInsertSchema } from "drizzle-zod";
import { v7 as uuidv7 } from "uuid";

export const ProviderConfig = z.object({
  apiUrl: z.string().optional(),
  apiKey: z.string(),
});
export type ProviderConfig = z.infer<typeof ProviderConfig>;

export const provider = pgTable("provider", {
  id: uuid("id").primaryKey().$defaultFn(uuidv7),
  organizationId: uuid("organization_id")
    .notNull()
    .references(() => organization.id),
  /* 提供商名称（如 openai、azure、anthropic 等） */
  providerName: varchar("provider_name", { length: 255 }).notNull(),
  /* 类型（如 custom 等） */
  providerType: varchar("provider_type", { length: 50 }).notNull(),
  /* 加密后的配置信息（如 API Key） */
  /* 加密后的配置信息 */
  config: jsonb("config").$type<ProviderConfig>(),
  /* 配置是否有效 */
  isValid: boolean("is_valid").notNull().default(true),
  /* 配额类型 */
  quotaType: varchar("quota_type", { length: 50 }),
  /* 配额上限 */
  quotaLimit: bigint("quota_limit", { mode: "number" }),
  /* 已用配额 */
  quotaUsed: bigint("quota_used", { mode: "number" }).default(0),
  /* 最后使用时间 */
  lastUsed: timestamp("last_used"),

  ...timeColumns(),
});
export const Provider = createSelectSchema(provider);
export type Provider = typeof provider.$inferSelect;
export const NewProvider = createInsertSchema(provider);
export type NewProvider = typeof provider.$inferInsert;

export const providerModels = pgTable("provider_models", {
  /* 主键 */
  id: uuid("id").primaryKey().$defaultFn(uuidv7),
  /* 所属租户 */
  organizationId: uuid("organization_id")
    .notNull()
    .references(() => organization.id),
  /* 提供商 */
  providerId: uuid("provider_id")
    .notNull()
    .references(() => provider.id),
  /* 模型名称（如 gpt-3.5-turbo） */
  modelName: varchar("model_name").notNull(),
  /* 模型类型（如 chat、embedding、rerank、speech2text） */
  modelType: varchar("model_type", {
    enum: ["llm", "tts", "embedding", "rerank", "speech2text"],
  }).notNull(),
  /* 模型专属加密配置 */
  // config: jsonb("config"),
  /* 是否有效 */
  isValid: boolean("is_valid").notNull().default(true),

  ...timeColumns(),
});
export const ProviderModels = createSelectSchema(providerModels);
export type ProviderModels = typeof providerModels.$inferSelect;
export const NewProviderModels = createInsertSchema(providerModels);
export type NewProviderModels = typeof providerModels.$inferInsert;
// export const providerModelSettings = pgTable("provider_model_settings", {
//   /* 主键 */
//   id: uuid("id").primaryKey(),
//   /* 所属租户 */
//   organizationId: uuid("organization_id")
//     .notNull()
//     .references(() => organization.id),
//   /* 提供商名称 */
//   providerName: varchar("provider_name", { length: 255 }).notNull(),
//   /* 模型名称 */
//   modelName: varchar("model_name", { length: 255 }).notNull(),
//   /* 模型类型 */
//   modelType: varchar("model_type", {
//     enum: ["llm", "tts", "embedding", "rerank", "speech2text"],
//   }).notNull(),
//   /* 是否启用 */
//   enabled: boolean("enabled").notNull().default(true),
//   /* 是否开启负载均衡 */
//   loadBalancingEnabled: boolean("load_balancing_enabled").notNull().default(false),

//   ...timeColumns(),
// });

// /* 创建索引 */
// export const providerModelSettingsIndexes = {
//   organizationProviderTypeIdx: index("provider_model_settings_org_provider_type_idx").on(
//     providerModelSettings.organizationId,
//     providerModelSettings.providerName,
//     providerModelSettings.modelType
//   ),
// };
