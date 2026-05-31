#[derive(Debug, thiserror::Error)]
pub enum PersistenceError {
    #[error("not found: {entity_type} {id}")]
    NotFound { entity_type: String, id: String },

    #[error("storage error: {0}")]
    Storage(String),

    #[error("serialization error: {0}")]
    Serialization(String),

    #[error("migration error: {0}")]
    Migration(String),
}

pub type Result<T> = std::result::Result<T, PersistenceError>;

impl From<serde_json::Error> for PersistenceError {
    fn from(e: serde_json::Error) -> Self {
        PersistenceError::Serialization(e.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn error_display() {
        let err = PersistenceError::NotFound {
            entity_type: "Pod".into(),
            id: "pod-1".into(),
        };
        assert_eq!(err.to_string(), "not found: Pod pod-1");
    }

    #[test]
    fn storage_error_display() {
        let err = PersistenceError::Storage("disk full".into());
        assert!(err.to_string().contains("disk full"));
    }

    #[test]
    fn serde_json_error_converts() {
        let bad_json = "not json";
        let serde_err = serde_json::from_str::<serde_json::Value>(bad_json).unwrap_err();
        let err: PersistenceError = serde_err.into();
        assert!(matches!(err, PersistenceError::Serialization(_)));
    }
}
