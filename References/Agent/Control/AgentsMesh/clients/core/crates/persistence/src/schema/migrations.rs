#[cfg(not(target_arch = "wasm32"))]
use rusqlite::Connection;

#[cfg(not(target_arch = "wasm32"))]
use crate::error::{PersistenceError, Result};
#[cfg(not(target_arch = "wasm32"))]
use crate::schema::tables::{CURRENT_VERSION, SCHEMA_V1};

#[cfg(not(target_arch = "wasm32"))]
pub fn run_migrations(conn: &Connection) -> Result<()> {
    let current = get_version(conn)?;
    if current >= CURRENT_VERSION {
        return Ok(());
    }
    if current == 0 {
        apply_v1(conn)?;
    }
    set_version(conn, CURRENT_VERSION)?;
    Ok(())
}

#[cfg(not(target_arch = "wasm32"))]
fn get_version(conn: &Connection) -> Result<u32> {
    let has_table: bool = conn
        .query_row(
            "SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_version')",
            [],
            |row| row.get(0),
        )
        .map_err(|e| PersistenceError::Migration(e.to_string()))?;

    if !has_table {
        return Ok(0);
    }

    conn.query_row(
        "SELECT COALESCE(MAX(version), 0) FROM schema_version",
        [],
        |row| row.get(0),
    )
    .map_err(|e| PersistenceError::Migration(e.to_string()))
}

#[cfg(not(target_arch = "wasm32"))]
fn set_version(conn: &Connection, version: u32) -> Result<()> {
    conn.execute(
        "INSERT OR REPLACE INTO schema_version (version) VALUES (?1)",
        [version],
    )
    .map_err(|e| PersistenceError::Migration(e.to_string()))?;
    Ok(())
}

#[cfg(not(target_arch = "wasm32"))]
fn apply_v1(conn: &Connection) -> Result<()> {
    for sql in SCHEMA_V1 {
        conn.execute_batch(sql)
            .map_err(|e| PersistenceError::Migration(e.to_string()))?;
    }
    Ok(())
}
