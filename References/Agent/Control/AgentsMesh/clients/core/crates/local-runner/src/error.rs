use std::io;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum LocalRunnerError {
    #[error("local runner binary not installed at {path}")]
    BinaryNotFound { path: String },

    #[error("runner CLI exited with status {status}: {stderr}")]
    CliFailed { status: i32, stderr: String },

    #[error("runner CLI produced unparseable output: {0}")]
    UnexpectedOutput(String),

    #[error("io error: {0}")]
    Io(#[from] io::Error),

    #[error("invalid argument: {0}")]
    InvalidArgument(String),

    #[error("download failed: {0}")]
    Download(String),

    #[error("sha256 mismatch: expected {expected}, got {actual}")]
    ChecksumMismatch { expected: String, actual: String },

    #[error("archive extract failed: {0}")]
    Extract(String),

    #[error("no agentsmesh-runner entry found in archive")]
    BinaryMissingFromArchive,
}

pub type Result<T> = std::result::Result<T, LocalRunnerError>;
