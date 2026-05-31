use crate::core::AgentsMeshCore;

#[uniffi::export]
impl AgentsMeshCore {
    pub fn relay_placeholder(&self) -> String {
        "relay integration pending".into()
    }
}
