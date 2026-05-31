use std::sync::Arc;
use std::sync::RwLock;

use agentsmesh_api_client::ApiClient;
use agentsmesh_state::mesh_state::MeshState;
use agentsmesh_types::proto_mesh_v1 as mp;

pub struct MeshService {
    client: Arc<ApiClient>,
    state: RwLock<MeshState>,
}

impl MeshService {
    pub fn new(client: Arc<ApiClient>, state: MeshState) -> Self {
        Self { client, state: RwLock::new(state) }
    }

    /// Crate-local accessor used by mesh_connect.rs to forward to the
    /// underlying api-client `*_connect` methods.
    pub(crate) fn client_ref(&self) -> &ApiClient {
        &self.client
    }

    pub fn topology_json(&self) -> Option<String> {
        self.state.read().unwrap().topology()
            .map(|t| serde_json::to_string(t).unwrap_or_default())
    }

    pub fn selected_node(&self) -> Option<String> {
        self.state.read().unwrap().selected_node().map(|s| s.to_string())
    }

    pub fn get_node_json(&self, pod_key: &str) -> Option<String> {
        self.state.read().unwrap().get_node_by_key(pod_key)
            .map(|n| serde_json::to_string(n).unwrap_or_default())
    }

    pub fn get_edges_for_node_json(&self, pod_key: &str) -> String {
        let binding = self.state.read().unwrap();
        let edges = binding.get_edges_for_node(pod_key);
        serde_json::to_string(&edges).unwrap_or_default()
    }

    pub fn get_channels_for_node_json(&self, pod_key: &str) -> String {
        let binding = self.state.read().unwrap();
        let chs = binding.get_channels_for_node(pod_key);
        serde_json::to_string(&chs).unwrap_or_default()
    }

    pub fn get_active_nodes_json(&self) -> String {
        let binding = self.state.read().unwrap();
        let nodes = binding.get_active_nodes();
        serde_json::to_string(&nodes).unwrap_or_default()
    }

    pub fn get_nodes_by_runner_json(&self, runner_id: i64) -> String {
        let binding = self.state.read().unwrap();
        let nodes = binding.get_nodes_by_runner(runner_id);
        serde_json::to_string(&nodes).unwrap_or_default()
    }

    pub fn get_runner_info_json(&self, runner_id: i64) -> Option<String> {
        self.state.read().unwrap().get_runner_info(runner_id)
            .map(|r| serde_json::to_string(r).unwrap_or_default())
    }

    pub fn clear_topology(&self) {
        self.state.write().unwrap().clear_topology();
    }

    pub fn select_node(&self, pod_key: Option<String>) {
        self.state.write().unwrap().select_node(pod_key);
    }

    pub async fn fetch_topology(&self) -> Result<String, String> {
        let req = mp::GetMeshTopologyRequest {
            org_slug: self.client.current_org_slug(),
        };
        let topo = self.client
            .get_mesh_topology_connect(&req)
            .await.map_err(crate::wire)?;
        self.state.write().unwrap().set_topology(topo.clone());
        serde_json::to_string(&topo).map_err(crate::wire)
    }
}

// =============================================================================
// Connect-RPC bridge methods. Binary in (prost-encoded), binary out — same wire
// the wasm/node-bridge layers speak.
// =============================================================================

use prost::Message;

macro_rules! connect_bridge {
    ($name:ident, $req:ident, $client_call:ident) => {
        pub async fn $name(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
            let req = mp::$req::decode(request_bytes)
                .map_err(|e| format!("decode {}: {e}", stringify!($req)))?;
            let resp = self.client_ref().$client_call(&req).await.map_err(crate::wire)?;
            Ok(resp.encode_to_vec())
        }
    };
}

impl MeshService {
    connect_bridge!(
        get_mesh_topology_connect,
        GetMeshTopologyRequest,
        get_mesh_topology_connect
    );
    connect_bridge!(
        get_ticket_pods_connect,
        GetTicketPodsRequest,
        get_ticket_pods_connect
    );
    connect_bridge!(
        batch_get_ticket_pods_connect,
        BatchGetTicketPodsRequest,
        batch_get_ticket_pods_connect
    );
    connect_bridge!(
        create_pod_for_ticket_connect,
        CreatePodForTicketRequest,
        create_pod_for_ticket_connect
    );
}
