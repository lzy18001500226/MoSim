// Connect-RPC bridge methods for WasmBindingService. Binary in, binary out
// (conventions §2.5).
//
// TS encodes the request via @bufbuild/protobuf .toBinary(), passes the
// Uint8Array in, receives a Uint8Array back, decodes via .fromBinary().
// No JSON intermediate; conventions §2.5 forbids it on the client.
//
// Split from service_binding.rs to honor the 200-line/file limit. Both
// `impl` blocks attach to WasmBindingService; wasm-bindgen handles multiple
// impl blocks as long as each is annotated.
//
// Forwards to the api-client `*_connect` methods directly — service_binding
// already wraps Arc<ApiClient> (the legacy REST path doesn't use a Service),
// so introducing a separate BindingService indirection here during the
// dual-track window would not pull its weight.

use agentsmesh_types::proto_binding_v1 as bp;
use prost::Message;
use wasm_bindgen::prelude::*;

use crate::service_binding::WasmBindingService;

#[wasm_bindgen]
impl WasmBindingService {
    #[wasm_bindgen(js_name = requestBindingConnect)]
    pub async fn request_binding_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::RequestBindingRequest::decode(request)
            .map_err(|e| format!("decode RequestBindingRequest: {e}"))?;
        let resp = self
            .client_ref()
            .request_binding_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }

    #[wasm_bindgen(js_name = acceptBindingConnect)]
    pub async fn accept_binding_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::AcceptBindingRequest::decode(request)
            .map_err(|e| format!("decode AcceptBindingRequest: {e}"))?;
        let resp = self
            .client_ref()
            .accept_binding_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }

    #[wasm_bindgen(js_name = rejectBindingConnect)]
    pub async fn reject_binding_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::RejectBindingRequest::decode(request)
            .map_err(|e| format!("decode RejectBindingRequest: {e}"))?;
        let resp = self
            .client_ref()
            .reject_binding_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }

    #[wasm_bindgen(js_name = unbindConnect)]
    pub async fn unbind_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::UnbindRequest::decode(request)
            .map_err(|e| format!("decode UnbindRequest: {e}"))?;
        let resp = self
            .client_ref()
            .unbind_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }

    #[wasm_bindgen(js_name = requestScopesConnect)]
    pub async fn request_scopes_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::RequestScopesRequest::decode(request)
            .map_err(|e| format!("decode RequestScopesRequest: {e}"))?;
        let resp = self
            .client_ref()
            .request_binding_scopes_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }

    #[wasm_bindgen(js_name = approveScopesConnect)]
    pub async fn approve_scopes_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::ApproveScopesRequest::decode(request)
            .map_err(|e| format!("decode ApproveScopesRequest: {e}"))?;
        let resp = self
            .client_ref()
            .approve_binding_scopes_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }

    #[wasm_bindgen(js_name = listBindingsConnect)]
    pub async fn list_bindings_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::ListBindingsRequest::decode(request)
            .map_err(|e| format!("decode ListBindingsRequest: {e}"))?;
        let resp = self
            .client_ref()
            .list_bindings_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }

    #[wasm_bindgen(js_name = getPendingBindingsConnect)]
    pub async fn get_pending_bindings_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::GetPendingBindingsRequest::decode(request)
            .map_err(|e| format!("decode GetPendingBindingsRequest: {e}"))?;
        let resp = self
            .client_ref()
            .get_pending_bindings_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }

    #[wasm_bindgen(js_name = getBoundPodsConnect)]
    pub async fn get_bound_pods_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::GetBoundPodsRequest::decode(request)
            .map_err(|e| format!("decode GetBoundPodsRequest: {e}"))?;
        let resp = self
            .client_ref()
            .get_bound_pods_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }

    #[wasm_bindgen(js_name = checkBindingConnect)]
    pub async fn check_binding_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        let req = bp::CheckBindingRequest::decode(request)
            .map_err(|e| format!("decode CheckBindingRequest: {e}"))?;
        let resp = self
            .client_ref()
            .check_binding_connect(&req)
            .await
            .map_err(agentsmesh_services::wire)?;
        Ok(resp.encode_to_vec())
    }
}
