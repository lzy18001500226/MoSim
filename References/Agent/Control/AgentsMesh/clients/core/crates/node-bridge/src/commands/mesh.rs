use napi::bindgen_prelude::Buffer;
use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn mesh_topology_json(&self) -> napi::Result<String> {
        let svc = self.mesh.lock().await;
            Ok(svc.topology_json().unwrap_or_default())
    }

    #[napi]
    pub async fn mesh_selected_node(&self) -> napi::Result<String> {
        let svc = self.mesh.lock().await;
            Ok(svc.selected_node().unwrap_or_default())
    }

    #[napi]
    pub async fn mesh_get_node_json(&self, pod_key: String) -> napi::Result<String> {
        let svc = self.mesh.lock().await;
            Ok(svc.get_node_json(&pod_key).unwrap_or_default())
    }

    #[napi]
    pub async fn mesh_get_edges_for_node_json(&self, pod_key: String) -> napi::Result<String> {
        let svc = self.mesh.lock().await;
            Ok(svc.get_edges_for_node_json(&pod_key))
    }

    #[napi]
    pub async fn mesh_get_channels_for_node_json(&self, pod_key: String) -> napi::Result<String> {
        let svc = self.mesh.lock().await;
            Ok(svc.get_channels_for_node_json(&pod_key))
    }

    #[napi]
    pub async fn mesh_get_active_nodes_json(&self) -> napi::Result<String> {
        let svc = self.mesh.lock().await;
            Ok(svc.get_active_nodes_json())
    }

    #[napi]
    pub async fn mesh_get_nodes_by_runner_json(&self, runner_id: i64) -> napi::Result<String> {
        let svc = self.mesh.lock().await;
            Ok(svc.get_nodes_by_runner_json(runner_id))
    }

    #[napi]
    pub async fn mesh_get_runner_info_json(&self, runner_id: i64) -> napi::Result<String> {
        let svc = self.mesh.lock().await;
            Ok(svc.get_runner_info_json(runner_id).unwrap_or_default())
    }

    #[napi]
    pub async fn mesh_clear_topology(&self) -> napi::Result<()> {
        let svc = self.mesh.lock().await;
            svc.clear_topology();
            Ok(())
    }

    #[napi]
    pub async fn mesh_select_node(&self, pod_key: Option<String>) -> napi::Result<()> {
        let svc = self.mesh.lock().await;
            svc.select_node(pod_key);
            Ok(())
    }

    #[napi]
    pub async fn mesh_fetch_topology(&self) -> napi::Result<String> {
        let svc = self.mesh.lock().await;
            svc.fetch_topology().await.map_err(err)
    }

    // ----- Connect-RPC bridge (binary in / binary out, conventions §2.5) -----

    #[napi]
    pub async fn mesh_get_mesh_topology_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.mesh.lock().await;
        let bytes = svc.get_mesh_topology_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn mesh_get_ticket_pods_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.mesh.lock().await;
        let bytes = svc.get_ticket_pods_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn mesh_batch_get_ticket_pods_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.mesh.lock().await;
        let bytes = svc.batch_get_ticket_pods_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn mesh_create_pod_for_ticket_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.mesh.lock().await;
        let bytes = svc.create_pod_for_ticket_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

}
