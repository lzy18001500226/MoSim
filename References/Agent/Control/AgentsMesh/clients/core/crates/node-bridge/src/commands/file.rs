use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn file_upload_file(&self, file_data: Vec<u8>, filename: String, content_type: String) -> napi::Result<String> {
        let svc = self.file.lock().await;
            svc.upload_file(file_data, &filename, &content_type).await.map_err(err)
    }
}
