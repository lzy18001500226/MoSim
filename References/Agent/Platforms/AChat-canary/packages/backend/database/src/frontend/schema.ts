export { PgDialect } from 'drizzle-orm/pg-core';

import * as chat from "../schema/chat";

export const schema = {
  ...chat,
};