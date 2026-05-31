pub mod channel_repo;
pub mod loop_repo;
pub mod message_repo;
pub mod pod_repo;
pub mod runner_repo;
pub mod ticket_repo;

pub use channel_repo::{ChannelRepo, ChannelRow};
pub use loop_repo::{LoopRepo, LoopRow, LoopRunRow};
pub use message_repo::{MessageRepo, MessageRow};
pub use pod_repo::PodRepo;
pub use runner_repo::RunnerRepo;
pub use ticket_repo::TicketRepo;

use crate::error::Result;

pub(crate) fn deserialize_rows<T: serde::de::DeserializeOwned>(rows: Vec<(String, Vec<u8>)>) -> Result<Vec<T>> {
    rows.iter().map(|(_, data)| Ok(serde_json::from_slice(data)?)).collect()
}
