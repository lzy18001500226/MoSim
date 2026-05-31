use std::sync::Arc;

use agentsmesh_events::types::RealtimeEvent;
use agentsmesh_persistence::StorageBackend;

use crate::acp_session::AcpSessionManager;
use crate::autopilot_state::AutopilotState;
use crate::channel_state::ChannelState;
use crate::event_dispatch;
use crate::loop_state::LoopState;
use crate::mesh_state::MeshState;
use crate::pod_state::PodState;
use crate::repo_state::RepoState;
use crate::runner_state::RunnerState;
use crate::ticket_state::TicketState;

pub struct AppState {
    pub pods: PodState,
    pub channels: ChannelState,
    pub runners: RunnerState,
    pub tickets: TicketState,
    pub loops: LoopState,
    pub mesh: MeshState,
    pub autopilot: AutopilotState,
    pub acp: AcpSessionManager,
    pub repo: RepoState,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            pods: PodState::new(),
            channels: ChannelState::new(),
            runners: RunnerState::new(),
            tickets: TicketState::new(),
            loops: LoopState::new(),
            mesh: MeshState::default(),
            autopilot: AutopilotState::default(),
            acp: AcpSessionManager::new(),
            repo: RepoState::new(),
        }
    }

    pub fn with_storage(backend: Arc<dyn StorageBackend>) -> Self {
        Self {
            pods: PodState::with_storage(backend.clone()),
            channels: ChannelState::with_storage(backend.clone()),
            runners: RunnerState::with_storage(backend.clone()),
            tickets: TicketState::with_storage(backend.clone()),
            loops: LoopState::with_storage(backend.clone()),
            mesh: MeshState::default(),
            autopilot: AutopilotState::default(),
            acp: AcpSessionManager::new(),
            repo: RepoState::with_storage(backend),
        }
    }

    pub fn dispatch(&mut self, event: &RealtimeEvent) {
        event_dispatch::dispatch(self, event);
    }
}

impl Default for AppState {
    fn default() -> Self {
        Self::new()
    }
}
