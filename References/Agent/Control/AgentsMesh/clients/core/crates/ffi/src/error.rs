use agentsmesh_api_client::ApiError;
use agentsmesh_auth::AuthError;
use agentsmesh_types::ServiceError;

/// Structured error surface for the FFI boundary.
/// Mirrors `agentsmesh_types::ServiceError` one-for-one so Swift/Kotlin
/// can `switch` on typed variants instead of parsing JSON.
#[derive(Debug, thiserror::Error, uniffi::Error)]
pub enum CoreError {
    #[error("HTTP {status}: {message}")]
    Http {
        status: u16,
        code: Option<String>,
        message: String,
    },

    #[error("auth expired")]
    AuthExpired,

    #[error("network: {message}")]
    Network { message: String },

    #[error("invalid json: {message}")]
    InvalidJson { message: String },

    #[error("{resource} not found")]
    NotFound {
        resource: String,
        id: Option<String>,
    },

    #[error("not connected: {pod_key}")]
    NotConnected { pod_key: String },

    #[error("{message}")]
    Unknown { message: String },
}

impl From<ServiceError> for CoreError {
    fn from(e: ServiceError) -> Self {
        match e {
            ServiceError::Http {
                status,
                code,
                message,
            } => Self::Http {
                status,
                code,
                message,
            },
            ServiceError::AuthExpired => Self::AuthExpired,
            ServiceError::Network { message } => Self::Network { message },
            ServiceError::InvalidJson { message } => Self::InvalidJson { message },
            ServiceError::ResourceNotFound { resource, id } => Self::NotFound { resource, id },
            ServiceError::Unknown { message } => Self::Unknown { message },
        }
    }
}

// Funnel through ServiceError so the mapping lives in one place and stays in
// sync with the WASM/node-bridge wire format (`ServiceError::to_wire`).
impl From<AuthError> for CoreError {
    fn from(e: AuthError) -> Self {
        ServiceError::from(e).into()
    }
}

impl From<ApiError> for CoreError {
    fn from(e: ApiError) -> Self {
        ServiceError::from(&e).into()
    }
}

impl From<serde_json::Error> for CoreError {
    fn from(e: serde_json::Error) -> Self {
        Self::InvalidJson {
            message: e.to_string(),
        }
    }
}
