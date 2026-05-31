use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::OrgApiService;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmOrgApiService(pub(crate) OrgApiService);

#[wasm_bindgen]
impl WasmOrgApiService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self(OrgApiService::new(client))
    }

    // -------- Connect-RPC (binary wire) --------
    //
    // TS encodes the request via @bufbuild/protobuf .toBinary(), passes the
    // Uint8Array in, receives a Uint8Array back, decodes via .fromBinary().
    // No JSON intermediate; conventions §2.5 forbids it on the client.
    //
    // js_name is camelCase; the `Connect` suffix marks the migration lane so
    // the legacy JSON methods can coexist until all 26 services flip.

    #[wasm_bindgen(js_name = listMyOrgsConnect)]
    pub async fn list_my_orgs_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_my_orgs_connect(request).await
    }

    #[wasm_bindgen(js_name = createOrgConnect)]
    pub async fn create_org_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_org_connect(request).await
    }

    #[wasm_bindgen(js_name = createPersonalOrgConnect)]
    pub async fn create_personal_org_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_personal_org_connect(request).await
    }

    #[wasm_bindgen(js_name = getOrgConnect)]
    pub async fn get_org_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.get_org_connect(request).await
    }

    #[wasm_bindgen(js_name = updateOrgConnect)]
    pub async fn update_org_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.update_org_connect(request).await
    }

    #[wasm_bindgen(js_name = deleteOrgConnect)]
    pub async fn delete_org_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.delete_org_connect(request).await
    }

    #[wasm_bindgen(js_name = listMembersConnect)]
    pub async fn list_members_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_members_connect(request).await
    }

    #[wasm_bindgen(js_name = inviteMemberConnect)]
    pub async fn invite_member_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.invite_member_connect(request).await
    }

    #[wasm_bindgen(js_name = removeMemberConnect)]
    pub async fn remove_member_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.remove_member_connect(request).await
    }

    #[wasm_bindgen(js_name = updateMemberRoleConnect)]
    pub async fn update_member_role_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.update_member_role_connect(request).await
    }
}
