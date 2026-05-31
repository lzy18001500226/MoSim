use napi_derive::napi;
use crate::AppState;

#[napi]
impl AppState {
    #[napi]
    pub async fn pod_pods_json(&self) -> napi::Result<String> {
        let svc = self.pod.lock().await;
            Ok(svc.pods_json())
    }

    #[napi]
    pub async fn pod_current_pod_json(&self) -> napi::Result<String> {
        let svc = self.pod.lock().await;
            Ok(svc.current_pod_json().unwrap_or_default())
    }

    #[napi]
    pub async fn pod_get_pod_json(&self, pod_key: String) -> napi::Result<String> {
        let svc = self.pod.lock().await;
            Ok(svc.get_pod_json(&pod_key).unwrap_or_default())
    }

    #[napi]
    pub async fn pod_update_pod_status(&self, pod_key: String, status: String, agent_status: Option<String>, error_code: Option<String>, error_message: Option<String>, timestamp: Option<i64>) -> napi::Result<()> {
        let svc = self.pod.lock().await;
            svc.update_pod_status(&pod_key, &status, agent_status, error_code, error_message, timestamp);
            Ok(())
    }

    #[napi]
    pub async fn pod_update_pod_title(&self, pod_key: String, title: String, timestamp: Option<i64>) -> napi::Result<()> {
        let svc = self.pod.lock().await;
            svc.update_pod_title(&pod_key, &title, timestamp);
            Ok(())
    }

    #[napi]
    pub async fn pod_update_pod_alias(&self, pod_key: String, alias: String) -> napi::Result<()> {
        let svc = self.pod.lock().await;
            svc.update_pod_alias(&pod_key, &alias);
            Ok(())
    }

    #[napi]
    pub async fn pod_update_agent_status(&self, pod_key: String, agent_status: String) -> napi::Result<()> {
        let svc = self.pod.lock().await;
            svc.update_agent_status(&pod_key, &agent_status);
            Ok(())
    }

    #[napi]
    pub async fn pod_remove_pod(&self, pod_key: String) -> napi::Result<()> {
        let svc = self.pod.lock().await;
            svc.remove_pod(&pod_key);
            Ok(())
    }
}
