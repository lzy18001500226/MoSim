use napi_derive::napi;
use crate::AppState;

#[napi]
impl AppState {
    #[napi]
    pub async fn channel_channel_pods_json(&self, id: i64) -> napi::Result<String> {
        let svc = self.channel.lock().await;
        Ok(svc.channel_pods_json(id))
    }

    #[napi]
    pub async fn channel_channel_members_json(&self, id: i64) -> napi::Result<String> {
        let svc = self.channel.lock().await;
        Ok(svc.channel_members_json(id))
    }

    // Mirrors services::channel::ChannelService::set_channel_pods_local —
    // exposed so the main process's IPC alias for join/leave/getPods can
    // populate the cache after a Connect call (desktop e2e D-001/D-002).
    #[napi]
    pub async fn channel_set_channel_pods_local(&self, channel_id: i64, json: String) -> napi::Result<()> {
        let svc = self.channel.lock().await;
        svc.set_channel_pods_local(channel_id, &json);
        Ok(())
    }
}
