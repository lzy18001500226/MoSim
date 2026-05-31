pub const SCHEMA_V1: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS kv_store (
        tbl TEXT NOT NULL,
        key TEXT NOT NULL,
        data BLOB NOT NULL,
        PRIMARY KEY (tbl, key)
    )",
    "CREATE TABLE IF NOT EXISTS kv_index (
        tbl TEXT NOT NULL,
        key TEXT NOT NULL,
        field TEXT NOT NULL,
        value TEXT NOT NULL,
        PRIMARY KEY (tbl, key, field),
        FOREIGN KEY (tbl, key) REFERENCES kv_store(tbl, key) ON DELETE CASCADE
    )",
    "CREATE INDEX IF NOT EXISTS idx_kv_index_lookup ON kv_index(tbl, field, value)",
    "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)",
];

pub const CURRENT_VERSION: u32 = 1;
