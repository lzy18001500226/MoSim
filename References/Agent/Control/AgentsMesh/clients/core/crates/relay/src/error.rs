use agentsmesh_types::ServiceError;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum RelayError {
    #[error("connection error: {0}")]
    Connection(String),

    #[error("not connected: {0}")]
    NotConnected(String),

    #[error("send error: {0}")]
    Send(String),

    #[error("protocol error: {0}")]
    Protocol(#[from] agentsmesh_protocol::ProtocolError),
}

impl From<&RelayError> for ServiceError {
    fn from(e: &RelayError) -> Self {
        ServiceError::Network {
            message: e.to_string(),
        }
    }
}

impl From<RelayError> for ServiceError {
    fn from(e: RelayError) -> Self {
        ServiceError::from(&e)
    }
}
