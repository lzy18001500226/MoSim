use std::pin::Pin;
use std::time::Duration;

use futures_util::future::{AbortHandle, Abortable};
use wasm_bindgen::prelude::*;

use super::traits::{BoxFuture, Runtime, TaskHandle};

pub struct WasmTaskHandle(AbortHandle);

impl TaskHandle for WasmTaskHandle {
    fn abort(&self) {
        self.0.abort();
    }
}

#[derive(Clone)]
pub struct WasmRuntime;

impl Runtime for WasmRuntime {
    type TaskHandle = WasmTaskHandle;

    fn spawn(
        &self,
        fut: Pin<Box<dyn std::future::Future<Output = ()> + 'static>>,
    ) -> Self::TaskHandle {
        let (abort_handle, abort_reg) = AbortHandle::new_pair();
        let abortable = Abortable::new(fut, abort_reg);
        wasm_bindgen_futures::spawn_local(async {
            let _ = abortable.await;
        });
        WasmTaskHandle(abort_handle)
    }

    fn sleep(&self, duration: Duration) -> BoxFuture<()> {
        let ms = duration.as_millis() as i32;
        Box::pin(async move {
            let promise = js_sys::Promise::new(&mut |resolve, _| {
                let global = js_sys::global();
                if let Ok(set_timeout) =
                    js_sys::Reflect::get(&global, &JsValue::from_str("setTimeout"))
                {
                    let func: js_sys::Function = set_timeout.into();
                    let _ = func.call2(&global, &resolve, &JsValue::from(ms));
                }
            });
            let _ = wasm_bindgen_futures::JsFuture::from(promise).await;
        })
    }
}
