use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn ticket_relations_list_relations_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.list_relations_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_create_relation_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.create_relation_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_delete_relation_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.delete_relation_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_list_commits_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.list_commits_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_link_commit_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.link_commit_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_unlink_commit_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.unlink_commit_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_list_merge_requests_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.list_merge_requests_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_list_comments_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.list_comments_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_create_comment_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.create_comment_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_update_comment_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.update_comment_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn ticket_relations_delete_comment_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.ticket_relations.lock().await;
        svc.delete_comment_connect(&request).await.map_err(err)
    }
}
