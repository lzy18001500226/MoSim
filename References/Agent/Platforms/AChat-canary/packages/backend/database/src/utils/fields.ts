import { type PgTable, getTableConfig } from "drizzle-orm/pg-core";

export const getQueryBuilderFields = <TTable extends PgTable>(
  table: TTable,
) => {
  const { columns } = getTableConfig(table);
  return columns.map((column) => ({
    name: column.name,
    label: column.name,
  }));
};
