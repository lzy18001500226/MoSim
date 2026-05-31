use std::collections::HashMap;
use std::sync::RwLock;

use crate::backend::StorageBackend;
use crate::error::{PersistenceError, Result};

type IndexedFields = Vec<(String, String)>;
type TableData = HashMap<String, (IndexedFields, Vec<u8>)>;

pub struct InMemoryBackend {
    tables: RwLock<HashMap<String, TableData>>,
}

impl InMemoryBackend {
    pub fn new() -> Self {
        Self {
            tables: RwLock::new(HashMap::new()),
        }
    }

    fn with_table<F, R>(&self, table: &str, f: F) -> Result<R>
    where
        F: FnOnce(&TableData) -> R,
    {
        let tables = self.tables.read().map_err(|e| PersistenceError::Storage(e.to_string()))?;
        let empty = HashMap::new();
        let tbl = tables.get(table).unwrap_or(&empty);
        Ok(f(tbl))
    }

    fn with_table_mut<F, R>(&self, table: &str, f: F) -> Result<R>
    where
        F: FnOnce(&mut TableData) -> R,
    {
        let mut tables =
            self.tables.write().map_err(|e| PersistenceError::Storage(e.to_string()))?;
        let tbl = tables.entry(table.to_string()).or_default();
        Ok(f(tbl))
    }
}

impl Default for InMemoryBackend {
    fn default() -> Self {
        Self::new()
    }
}

impl StorageBackend for InMemoryBackend {
    fn get_raw(&self, table: &str, id: &str) -> Result<Option<Vec<u8>>> {
        self.with_table(table, |tbl| tbl.get(id).map(|(_, data)| data.clone()))
    }

    fn put_raw(
        &self,
        table: &str,
        id: &str,
        indexed_fields: &[(&str, &str)],
        data: &[u8],
    ) -> Result<()> {
        let fields: IndexedFields = indexed_fields
            .iter()
            .map(|(k, v)| (k.to_string(), v.to_string()))
            .collect();
        self.with_table_mut(table, |tbl| {
            tbl.insert(id.to_string(), (fields, data.to_vec()));
        })
    }

    fn put_raw_many(
        &self,
        table: &str,
        entries: &[(String, Vec<(String, String)>, Vec<u8>)],
    ) -> Result<()> {
        self.with_table_mut(table, |tbl| {
            for (id, fields, data) in entries {
                tbl.insert(id.clone(), (fields.clone(), data.clone()));
            }
        })
    }

    fn delete_raw(&self, table: &str, id: &str) -> Result<()> {
        self.with_table_mut(table, |tbl| {
            tbl.remove(id);
        })
    }

    fn list_raw(&self, table: &str) -> Result<Vec<(String, Vec<u8>)>> {
        self.with_table(table, |tbl| {
            tbl.iter()
                .map(|(id, (_, data))| (id.clone(), data.clone()))
                .collect()
        })
    }

    fn query_raw(&self, table: &str, field: &str, value: &str) -> Result<Vec<(String, Vec<u8>)>> {
        self.with_table(table, |tbl| {
            tbl.iter()
                .filter(|(_, (fields, _))| {
                    fields.iter().any(|(k, v)| k == field && v == value)
                })
                .map(|(id, (_, data))| (id.clone(), data.clone()))
                .collect()
        })
    }

    fn query_range(
        &self,
        table: &str,
        field: &str,
        from: &str,
        limit: usize,
    ) -> Result<Vec<(String, Vec<u8>)>> {
        self.with_table(table, |tbl| {
            let mut matches: Vec<_> = tbl
                .iter()
                .filter(|(_, (fields, _))| {
                    fields
                        .iter()
                        .any(|(k, v)| k == field && v.as_str() >= from)
                })
                .map(|(id, (_, data))| (id.clone(), data.clone()))
                .collect();
            matches.sort_by(|a, b| a.0.cmp(&b.0));
            matches.truncate(limit);
            matches
        })
    }

    fn count(&self, table: &str) -> Result<usize> {
        self.with_table(table, |tbl| tbl.len())
    }

    fn clear(&self, table: &str) -> Result<()> {
        self.with_table_mut(table, |tbl| {
            tbl.clear();
        })
    }

    fn migrate(&self) -> Result<()> {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn put_and_get() {
        let backend = InMemoryBackend::new();
        backend
            .put_raw("pods", "p1", &[("status", "running")], b"data1")
            .unwrap();
        let result = backend.get_raw("pods", "p1").unwrap();
        assert_eq!(result, Some(b"data1".to_vec()));
    }

    #[test]
    fn get_missing_returns_none() {
        let backend = InMemoryBackend::new();
        assert_eq!(backend.get_raw("pods", "nope").unwrap(), None);
    }

    #[test]
    fn delete_removes_entry() {
        let backend = InMemoryBackend::new();
        backend.put_raw("t", "k", &[], b"v").unwrap();
        backend.delete_raw("t", "k").unwrap();
        assert_eq!(backend.get_raw("t", "k").unwrap(), None);
    }

    #[test]
    fn query_by_field() {
        let backend = InMemoryBackend::new();
        backend
            .put_raw("pods", "p1", &[("status", "running")], b"d1")
            .unwrap();
        backend
            .put_raw("pods", "p2", &[("status", "stopped")], b"d2")
            .unwrap();
        backend
            .put_raw("pods", "p3", &[("status", "running")], b"d3")
            .unwrap();

        let results = backend.query_raw("pods", "status", "running").unwrap();
        assert_eq!(results.len(), 2);
    }

    #[test]
    fn count_and_clear() {
        let backend = InMemoryBackend::new();
        backend.put_raw("t", "a", &[], b"1").unwrap();
        backend.put_raw("t", "b", &[], b"2").unwrap();
        assert_eq!(backend.count("t").unwrap(), 2);

        backend.clear("t").unwrap();
        assert_eq!(backend.count("t").unwrap(), 0);
    }

    #[test]
    fn put_raw_many() {
        let backend = InMemoryBackend::new();
        let entries = vec![
            ("a".into(), vec![], b"d1".to_vec()),
            ("b".into(), vec![], b"d2".to_vec()),
        ];
        backend.put_raw_many("t", &entries).unwrap();
        assert_eq!(backend.count("t").unwrap(), 2);
    }

    #[test]
    fn query_range_with_limit() {
        let backend = InMemoryBackend::new();
        for i in 0..5 {
            let id = format!("k{i}");
            let val = format!("{i}");
            backend
                .put_raw("t", &id, &[("sort", &val)], b"d")
                .unwrap();
        }
        let results = backend.query_range("t", "sort", "2", 2).unwrap();
        assert_eq!(results.len(), 2);
    }
}
