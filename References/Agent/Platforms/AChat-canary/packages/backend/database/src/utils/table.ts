import { pgTableCreator } from "drizzle-orm/pg-core";

export const shopTable = pgTableCreator((name) => `shop_${name}`);

export const proxyTable = pgTableCreator((name) => `proxy_${name}`);

export const userTable = pgTableCreator((name) => `user_${name}`);
