use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn ticket_list_tickets_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.list_tickets_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_get_ticket_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.get_ticket_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_create_ticket_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.create_ticket_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_update_ticket_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.update_ticket_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_delete_ticket_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.delete_ticket_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_update_ticket_status_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.update_ticket_status_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_get_active_tickets_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.get_active_tickets_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_get_board_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.get_board_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_get_sub_tickets_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.get_sub_tickets_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_add_assignee_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.add_assignee_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_remove_assignee_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.remove_assignee_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_list_labels_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.list_labels_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_create_label_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.create_label_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_update_label_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.update_label_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_delete_label_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.delete_label_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_add_label_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.add_label_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_remove_label_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket.lock().await;
        svc.remove_label_connect(&request).await.map_err(err)
    }

    // ticket→pod lookup belongs to proto.mesh.v1 (MeshService), not
    // proto.ticket.v1. TicketService.get_ticket_pods forwards to the
    // Connect-RPC bridge then projects the proto MeshNode shape into
    // legacy PodListResponse JSON for the renderer.
    #[napi]
    pub async fn ticket_get_ticket_pods(&self, slug: String, active_only: Option<bool>) -> napi::Result<String> {
        let svc = self.ticket.lock().await;
        svc.get_ticket_pods(&slug, active_only).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_ticket_pods_json(&self, slug: String) -> napi::Result<String> {
        let svc = self.ticket.lock().await;
        Ok(svc.ticket_pods_json(&slug))
    }
}
