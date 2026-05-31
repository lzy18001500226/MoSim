mod traits;

#[cfg(not(target_arch = "wasm32"))]
mod native;
#[cfg(target_arch = "wasm32")]
mod wasm;

pub use traits::{timeout, BoxFuture, Elapsed, Runtime, TaskHandle};

#[cfg(not(target_arch = "wasm32"))]
pub use native::NativeRuntime as PlatformRuntime;
#[cfg(target_arch = "wasm32")]
pub use wasm::WasmRuntime as PlatformRuntime;
