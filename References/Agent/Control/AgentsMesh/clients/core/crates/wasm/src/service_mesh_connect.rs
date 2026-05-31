// Connect-RPC bridge methods for WasmMeshService. Binary in, binary out
// (conventions §2.5).
//
// TS encodes the request via @bufbuild/protobuf .toBinary(), passes the
// Uint8Array in, receives a Uint8Array back, decodes via .fromBinary().
// No JSON intermediate; conventions §2.5 forbids it on the client.
//
// Split from service_mesh.rs to honor the 200-line/file limit. Both
// `impl` blocks attach to WasmMeshService; wasm-bindgen handles multiple
// impl blocks as long as each is annotated.

use wasm_bindgen::prelude::*;

use crate::service_mesh::WasmMeshService;

#[wasm_bindgen]
impl WasmMeshService {
    #[wasm_bindgen(js_name = getMeshTopologyConnect)]
    pub async fn get_mesh_topology_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.get_mesh_topology_connect(request).await
    }

    #[wasm_bindgen(js_name = getTicketPodsConnect)]
    pub async fn get_ticket_pods_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.get_ticket_pods_connect(request).await
    }

    #[wasm_bindgen(js_name = batchGetTicketPodsConnect)]
    pub async fn batch_get_ticket_pods_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.batch_get_ticket_pods_connect(request).await
    }

    #[wasm_bindgen(js_name = createPodForTicketConnect)]
    pub async fn create_pod_for_ticket_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_pod_for_ticket_connect(request).await
    }
}
