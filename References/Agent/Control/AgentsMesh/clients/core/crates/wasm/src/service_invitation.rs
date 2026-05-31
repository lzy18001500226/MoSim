use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::InvitationService;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmInvitationService {
    inner: InvitationService,
}

#[wasm_bindgen]
impl WasmInvitationService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self { inner: InvitationService::new(client) }
    }

    // -------- Connect-RPC (binary wire) --------
    //
    // TS encodes the request via @bufbuild/protobuf .toBinary(), passes the
    // Uint8Array in, receives a Uint8Array back, decodes via .fromBinary().
    // No JSON intermediate; conventions §2.5 forbids it on the client.
    //
    // js_name is camelCase per Connect convention.

    #[wasm_bindgen(js_name = listInvitationsConnect)]
    pub async fn list_invitations_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.list_invitations_connect(request).await
    }

    #[wasm_bindgen(js_name = createInvitationConnect)]
    pub async fn create_invitation_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.create_invitation_connect(request).await
    }

    #[wasm_bindgen(js_name = revokeInvitationConnect)]
    pub async fn revoke_invitation_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.revoke_invitation_connect(request).await
    }

    #[wasm_bindgen(js_name = resendInvitationConnect)]
    pub async fn resend_invitation_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.resend_invitation_connect(request).await
    }

    #[wasm_bindgen(js_name = acceptInvitationConnect)]
    pub async fn accept_invitation_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.accept_invitation_connect(request).await
    }

    #[wasm_bindgen(js_name = listPendingInvitationsConnect)]
    pub async fn list_pending_invitations_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.list_pending_invitations_connect(request).await
    }

    #[wasm_bindgen(js_name = getInvitationByTokenConnect)]
    pub async fn get_invitation_by_token_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.get_invitation_by_token_connect(request).await
    }
}
