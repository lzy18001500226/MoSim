use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn invitation_list_invitations_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.invitation.lock().await;
        svc.list_invitations_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn invitation_create_invitation_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.invitation.lock().await;
        svc.create_invitation_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn invitation_revoke_invitation_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.invitation.lock().await;
        svc.revoke_invitation_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn invitation_resend_invitation_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.invitation.lock().await;
        svc.resend_invitation_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn invitation_accept_invitation_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.invitation.lock().await;
        svc.accept_invitation_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn invitation_list_pending_invitations_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.invitation.lock().await;
        svc.list_pending_invitations_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn invitation_get_invitation_by_token_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.invitation.lock().await;
        svc.get_invitation_by_token_connect(&request).await.map_err(err)
    }
}
