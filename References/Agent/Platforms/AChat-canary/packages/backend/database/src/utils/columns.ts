import { timestamp } from "drizzle-orm/pg-core";

export const timeColumns = <
  T extends "both" | "create-only" | "update-only" = "both",
>(
  choose?: T,
) => {
  const createdAt = timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow();
  if (choose === "create-only") {
    return {
      createdAt: timestamp("created_at", { withTimezone: true })
        .notNull()
        .defaultNow(),
    } as T extends "create-only" ? { createdAt: typeof createdAt } : never;
  }

  const updatedAt = timestamp("updated_at", { withTimezone: true }).$onUpdate(
    () => new Date(),
  );
  if (!choose || choose === "both") {
    return {
      createdAt,
      updatedAt,
    } as T extends "both"
      ? { createdAt: typeof createdAt; updatedAt: typeof updatedAt }
      : never;
  }
  if (choose === "update-only") {
    return {
      updatedAt: timestamp("updated_at", { withTimezone: true }).$onUpdate(
        () => new Date(),
      ),
    } as T extends "update-only" ? { updatedAt: typeof updatedAt } : never;
  }

  throw new Error(`Invalid choose: ${choose}`);
};
