// node-bridge: forward proto.binding.v1.BindingService Connect-RPC calls
// from the Desktop renderer (Electron main process) through napi to the
// shared Rust binding service. Binary in / binary out (Buffer ↔ Vec<u8>);
// the renderer encodes/decodes with @bufbuild/protobuf, identical to the
// web/wasm path.

use napi::bindgen_prelude::Buffer;
use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn binding_request_binding_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.request_binding_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn binding_accept_binding_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.accept_binding_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn binding_reject_binding_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.reject_binding_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn binding_unbind_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.unbind_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn binding_request_scopes_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.request_scopes_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn binding_approve_scopes_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.approve_scopes_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn binding_list_bindings_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.list_bindings_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn binding_get_pending_bindings_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.get_pending_bindings_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn binding_get_bound_pods_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.get_bound_pods_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }

    #[napi]
    pub async fn binding_check_binding_connect(&self, request: Buffer) -> napi::Result<Buffer> {
        let svc = self.binding.lock().await;
        let bytes = svc.check_binding_connect(request.as_ref()).await.map_err(err)?;
        Ok(bytes.into())
    }
}
