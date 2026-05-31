use std::path::PathBuf;
use agentsmesh_auth::PersistentStorage;

pub struct FileStorage {
    dir: PathBuf,
}

impl FileStorage {
    pub fn new(dir: PathBuf) -> Self { Self { dir } }
    fn path(&self, key: &str) -> PathBuf { self.dir.join(format!("{key}.json")) }
}

impl PersistentStorage for FileStorage {
    fn get(&self, key: &str) -> Option<String> {
        std::fs::read_to_string(self.path(key)).ok()
    }
    fn set(&self, key: &str, value: &str) {
        let path = self.path(key);
        // Namespaced keys (e.g. `agentsmesh-auth/https_agentsmesh_ai/session`)
        // map to nested paths — without this, `fs::write` fails silently when
        // the parent dir is missing, and bootstrap reads back None forever.
        if let Some(parent) = path.parent() {
            let _ = std::fs::create_dir_all(parent);
        }
        let _ = std::fs::write(path, value);
    }
    fn remove(&self, key: &str) {
        let _ = std::fs::remove_file(self.path(key));
    }
}
