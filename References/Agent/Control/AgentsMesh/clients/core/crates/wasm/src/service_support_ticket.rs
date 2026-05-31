use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::SupportTicketService;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmSupportTicketService(pub(crate) SupportTicketService);

#[wasm_bindgen]
impl WasmSupportTicketService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self(SupportTicketService::new(client))
    }

    // All RPCs are Connect-binary (conventions §2.5). Multipart upload is
    // gone — attachments take the presign → S3 PUT → associate handshake.

    #[wasm_bindgen(js_name = listSupportTicketsConnect)]
    pub async fn list_support_tickets_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_support_tickets_connect(request).await
    }

    #[wasm_bindgen(js_name = getSupportTicketConnect)]
    pub async fn get_support_ticket_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.get_support_ticket_connect(request).await
    }

    #[wasm_bindgen(js_name = getAttachmentUrlConnect)]
    pub async fn get_attachment_url_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.get_attachment_url_connect(request).await
    }

    #[wasm_bindgen(js_name = createSupportTicketConnect)]
    pub async fn create_support_ticket_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_support_ticket_connect(request).await
    }

    #[wasm_bindgen(js_name = addSupportTicketMessageConnect)]
    pub async fn add_support_ticket_message_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.add_support_ticket_message_connect(request).await
    }

    #[wasm_bindgen(js_name = presignAttachmentUploadConnect)]
    pub async fn presign_attachment_upload_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.presign_attachment_upload_connect(request).await
    }

    #[wasm_bindgen(js_name = associateAttachmentsConnect)]
    pub async fn associate_attachments_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.associate_attachments_connect(request).await
    }
}
