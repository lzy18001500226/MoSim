use crate::error::Result;

pub trait StorageBackend: Send + Sync {
    fn get_raw(&self, table: &str, id: &str) -> Result<Option<Vec<u8>>>;

    fn put_raw(
        &self,
        table: &str,
        id: &str,
        indexed_fields: &[(&str, &str)],
        data: &[u8],
    ) -> Result<()>;

    fn put_raw_many(
        &self,
        table: &str,
        entries: &[(String, Vec<(String, String)>, Vec<u8>)],
    ) -> Result<()>;

    fn delete_raw(&self, table: &str, id: &str) -> Result<()>;

    fn list_raw(&self, table: &str) -> Result<Vec<(String, Vec<u8>)>>;

    fn query_raw(&self, table: &str, field: &str, value: &str) -> Result<Vec<(String, Vec<u8>)>>;

    fn query_range(
        &self,
        table: &str,
        field: &str,
        from: &str,
        limit: usize,
    ) -> Result<Vec<(String, Vec<u8>)>>;

    fn count(&self, table: &str) -> Result<usize>;

    fn clear(&self, table: &str) -> Result<()>;

    fn migrate(&self) -> Result<()>;
}
