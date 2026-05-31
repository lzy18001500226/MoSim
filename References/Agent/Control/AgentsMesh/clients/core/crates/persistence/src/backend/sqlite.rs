use std::sync::Mutex;

use rusqlite::{Connection, OptionalExtension};

use crate::backend::StorageBackend;
use crate::error::{PersistenceError, Result};
use crate::schema::migrations;

pub struct SqliteBackend {
    conn: Mutex<Connection>,
}

impl SqliteBackend {
    pub fn open(path: &str) -> Result<Self> {
        let conn =
            Connection::open(path).map_err(|e| PersistenceError::Storage(e.to_string()))?;
        conn.execute_batch("PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;")
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        Ok(Self {
            conn: Mutex::new(conn),
        })
    }

    pub fn open_in_memory() -> Result<Self> {
        let conn = Connection::open_in_memory()
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        conn.execute_batch("PRAGMA foreign_keys=ON;")
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        Ok(Self {
            conn: Mutex::new(conn),
        })
    }

    fn lock(&self) -> Result<std::sync::MutexGuard<'_, Connection>> {
        self.conn
            .lock()
            .map_err(|e| PersistenceError::Storage(e.to_string()))
    }
}

impl StorageBackend for SqliteBackend {
    fn get_raw(&self, table: &str, id: &str) -> Result<Option<Vec<u8>>> {
        let conn = self.lock()?;
        let mut stmt = conn
            .prepare("SELECT data FROM kv_store WHERE tbl = ?1 AND key = ?2")
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        let result: Option<Vec<u8>> = stmt
            .query_row(rusqlite::params![table, id], |row| row.get(0))
            .optional()
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        Ok(result)
    }

    fn put_raw(
        &self,
        table: &str,
        id: &str,
        indexed_fields: &[(&str, &str)],
        data: &[u8],
    ) -> Result<()> {
        let conn = self.lock()?;
        conn.execute(
            "INSERT OR REPLACE INTO kv_store (tbl, key, data) VALUES (?1, ?2, ?3)",
            rusqlite::params![table, id, data],
        )
        .map_err(|e| PersistenceError::Storage(e.to_string()))?;

        conn.execute(
            "DELETE FROM kv_index WHERE tbl = ?1 AND key = ?2",
            rusqlite::params![table, id],
        )
        .map_err(|e| PersistenceError::Storage(e.to_string()))?;

        for (field, value) in indexed_fields {
            conn.execute(
                "INSERT INTO kv_index (tbl, key, field, value) VALUES (?1, ?2, ?3, ?4)",
                rusqlite::params![table, id, field, value],
            )
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        }
        Ok(())
    }

    fn put_raw_many(
        &self,
        table: &str,
        entries: &[(String, Vec<(String, String)>, Vec<u8>)],
    ) -> Result<()> {
        let conn = self.lock()?;
        let tx = conn
            .unchecked_transaction()
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;

        for (id, fields, data) in entries {
            tx.execute(
                "INSERT OR REPLACE INTO kv_store (tbl, key, data) VALUES (?1, ?2, ?3)",
                rusqlite::params![table, id, data],
            )
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;

            tx.execute(
                "DELETE FROM kv_index WHERE tbl = ?1 AND key = ?2",
                rusqlite::params![table, id],
            )
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;

            for (field, value) in fields {
                tx.execute(
                    "INSERT INTO kv_index (tbl, key, field, value) VALUES (?1, ?2, ?3, ?4)",
                    rusqlite::params![table, id, field, value],
                )
                .map_err(|e| PersistenceError::Storage(e.to_string()))?;
            }
        }
        tx.commit()
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        Ok(())
    }

    fn delete_raw(&self, table: &str, id: &str) -> Result<()> {
        let conn = self.lock()?;
        conn.execute(
            "DELETE FROM kv_store WHERE tbl = ?1 AND key = ?2",
            rusqlite::params![table, id],
        )
        .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        Ok(())
    }

    fn list_raw(&self, table: &str) -> Result<Vec<(String, Vec<u8>)>> {
        let conn = self.lock()?;
        let mut stmt = conn
            .prepare("SELECT key, data FROM kv_store WHERE tbl = ?1")
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        let rows = stmt
            .query_map(rusqlite::params![table], |row| {
                Ok((row.get::<_, String>(0)?, row.get::<_, Vec<u8>>(1)?))
            })
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;

        let mut result = Vec::new();
        for row in rows {
            result.push(row.map_err(|e| PersistenceError::Storage(e.to_string()))?);
        }
        Ok(result)
    }

    fn query_raw(&self, table: &str, field: &str, value: &str) -> Result<Vec<(String, Vec<u8>)>> {
        let conn = self.lock()?;
        let mut stmt = conn
            .prepare(
                "SELECT s.key, s.data FROM kv_store s \
                 INNER JOIN kv_index i ON s.tbl = i.tbl AND s.key = i.key \
                 WHERE s.tbl = ?1 AND i.field = ?2 AND i.value = ?3",
            )
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        let rows = stmt
            .query_map(rusqlite::params![table, field, value], |row| {
                Ok((row.get::<_, String>(0)?, row.get::<_, Vec<u8>>(1)?))
            })
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;

        let mut result = Vec::new();
        for row in rows {
            result.push(row.map_err(|e| PersistenceError::Storage(e.to_string()))?);
        }
        Ok(result)
    }

    fn query_range(
        &self,
        table: &str,
        field: &str,
        from: &str,
        limit: usize,
    ) -> Result<Vec<(String, Vec<u8>)>> {
        let conn = self.lock()?;
        let mut stmt = conn
            .prepare(
                "SELECT s.key, s.data FROM kv_store s \
                 INNER JOIN kv_index i ON s.tbl = i.tbl AND s.key = i.key \
                 WHERE s.tbl = ?1 AND i.field = ?2 AND i.value >= ?3 \
                 ORDER BY i.value ASC LIMIT ?4",
            )
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        let rows = stmt
            .query_map(
                rusqlite::params![table, field, from, limit as i64],
                |row| Ok((row.get::<_, String>(0)?, row.get::<_, Vec<u8>>(1)?)),
            )
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;

        let mut result = Vec::new();
        for row in rows {
            result.push(row.map_err(|e| PersistenceError::Storage(e.to_string()))?);
        }
        Ok(result)
    }

    fn count(&self, table: &str) -> Result<usize> {
        let conn = self.lock()?;
        let count: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM kv_store WHERE tbl = ?1",
                rusqlite::params![table],
                |row| row.get(0),
            )
            .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        Ok(count as usize)
    }

    fn clear(&self, table: &str) -> Result<()> {
        let conn = self.lock()?;
        conn.execute(
            "DELETE FROM kv_store WHERE tbl = ?1",
            rusqlite::params![table],
        )
        .map_err(|e| PersistenceError::Storage(e.to_string()))?;
        Ok(())
    }

    fn migrate(&self) -> Result<()> {
        let conn = self.lock()?;
        migrations::run_migrations(&conn)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn setup() -> SqliteBackend {
        let backend = SqliteBackend::open_in_memory().unwrap();
        backend.migrate().unwrap();
        backend
    }

    #[test]
    fn roundtrip() {
        let b = setup();
        b.put_raw("pods", "p1", &[("status", "running")], b"hello")
            .unwrap();
        assert_eq!(b.get_raw("pods", "p1").unwrap(), Some(b"hello".to_vec()));
    }

    #[test]
    fn missing_key() {
        let b = setup();
        assert_eq!(b.get_raw("pods", "nope").unwrap(), None);
    }

    #[test]
    fn delete() {
        let b = setup();
        b.put_raw("t", "k", &[], b"v").unwrap();
        b.delete_raw("t", "k").unwrap();
        assert_eq!(b.get_raw("t", "k").unwrap(), None);
    }

    #[test]
    fn query_by_index() {
        let b = setup();
        b.put_raw("pods", "p1", &[("status", "running")], b"d1")
            .unwrap();
        b.put_raw("pods", "p2", &[("status", "stopped")], b"d2")
            .unwrap();
        let results = b.query_raw("pods", "status", "running").unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].0, "p1");
    }

    #[test]
    fn count_and_clear() {
        let b = setup();
        b.put_raw("t", "a", &[], b"1").unwrap();
        b.put_raw("t", "b", &[], b"2").unwrap();
        assert_eq!(b.count("t").unwrap(), 2);
        b.clear("t").unwrap();
        assert_eq!(b.count("t").unwrap(), 0);
    }

    #[test]
    fn put_many_transactional() {
        let b = setup();
        let entries = vec![
            ("a".into(), vec![], b"d1".to_vec()),
            ("b".into(), vec![("f".into(), "v".into())], b"d2".to_vec()),
        ];
        b.put_raw_many("t", &entries).unwrap();
        assert_eq!(b.count("t").unwrap(), 2);
        let q = b.query_raw("t", "f", "v").unwrap();
        assert_eq!(q.len(), 1);
    }

    #[test]
    fn migrate_idempotent() {
        let b = setup();
        b.migrate().unwrap();
        b.put_raw("t", "k", &[], b"v").unwrap();
        assert_eq!(b.get_raw("t", "k").unwrap(), Some(b"v".to_vec()));
    }

    #[test]
    fn query_range_basic_and_limit() {
        let b = setup();
        for i in 0..5 {
            let id = format!("k{i}");
            let val = format!("{i}");
            b.put_raw("t", &id, &[("sort", &val)], b"d").unwrap();
        }
        assert_eq!(b.query_range("t", "sort", "2", 10).unwrap().len(), 3);
        assert_eq!(b.query_range("t", "sort", "0", 2).unwrap().len(), 2);
    }

    #[test]
    fn query_range_no_match() {
        let b = setup();
        b.put_raw("t", "k1", &[("sort", "1")], b"d").unwrap();
        let results = b.query_range("t", "sort", "9", 10).unwrap();
        assert!(results.is_empty());
    }

    #[test]
    fn list_raw_returns_all() {
        let b = setup();
        b.put_raw("t", "a", &[], b"1").unwrap();
        b.put_raw("t", "b", &[], b"2").unwrap();
        b.put_raw("other", "c", &[], b"3").unwrap();
        let rows = b.list_raw("t").unwrap();
        assert_eq!(rows.len(), 2);
    }

    #[test]
    fn list_raw_empty_table() {
        let b = setup();
        assert!(b.list_raw("empty").unwrap().is_empty());
    }

    #[test]
    fn index_updated_on_overwrite() {
        let b = setup();
        b.put_raw("pods", "p1", &[("status", "running")], b"d1").unwrap();
        b.put_raw("pods", "p1", &[("status", "stopped")], b"d2").unwrap();
        assert!(b.query_raw("pods", "status", "running").unwrap().is_empty());
        assert_eq!(b.query_raw("pods", "status", "stopped").unwrap().len(), 1);
    }

    #[test]
    fn put_many_with_indexed_fields() {
        let b = setup();
        let entries = vec![
            ("p1".into(), vec![("status".into(), "running".into())], b"d1".to_vec()),
            ("p2".into(), vec![("status".into(), "stopped".into())], b"d2".to_vec()),
            ("p3".into(), vec![("status".into(), "running".into())], b"d3".to_vec()),
        ];
        b.put_raw_many("pods", &entries).unwrap();
        assert_eq!(b.query_raw("pods", "status", "running").unwrap().len(), 2);
        assert_eq!(b.count("pods").unwrap(), 3);
    }

    #[test]
    fn delete_cascades_index() {
        let b = setup();
        b.put_raw("pods", "p1", &[("status", "running")], b"d1").unwrap();
        b.delete_raw("pods", "p1").unwrap();
        assert!(b.query_raw("pods", "status", "running").unwrap().is_empty());
    }

    #[test]
    fn multiple_indexed_fields() {
        let b = setup();
        b.put_raw("pods", "p1", &[("status", "running"), ("runner", "r1")], b"d1").unwrap();
        assert_eq!(b.query_raw("pods", "status", "running").unwrap().len(), 1);
        assert_eq!(b.query_raw("pods", "runner", "r1").unwrap().len(), 1);
    }

    #[test]
    fn count_empty_table() {
        let b = setup();
        assert_eq!(b.count("nonexistent").unwrap(), 0);
    }

    #[test]
    fn clear_only_affects_target_table() {
        let b = setup();
        b.put_raw("t1", "a", &[], b"1").unwrap();
        b.put_raw("t2", "b", &[], b"2").unwrap();
        b.clear("t1").unwrap();
        assert_eq!(b.count("t1").unwrap(), 0);
        assert_eq!(b.count("t2").unwrap(), 1);
    }
}
