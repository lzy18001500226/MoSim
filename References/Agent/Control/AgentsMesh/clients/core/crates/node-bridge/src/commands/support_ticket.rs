use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn support_ticket_list_support_tickets_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.support_ticket.lock().await;
        svc.list_support_tickets_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn support_ticket_get_support_ticket_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.support_ticket.lock().await;
        svc.get_support_ticket_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn support_ticket_get_attachment_url_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.support_ticket.lock().await;
        svc.get_attachment_url_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn support_ticket_create_support_ticket_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.support_ticket.lock().await;
        svc.create_support_ticket_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn support_ticket_add_support_ticket_message_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.support_ticket.lock().await;
        svc.add_support_ticket_message_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn support_ticket_presign_attachment_upload_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.support_ticket.lock().await;
        svc.presign_attachment_upload_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn support_ticket_associate_attachments_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.support_ticket.lock().await;
        svc.associate_attachments_connect(&request).await.map_err(err)
    }
}
