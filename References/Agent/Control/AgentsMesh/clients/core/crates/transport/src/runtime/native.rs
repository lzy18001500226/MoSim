use std::pin::Pin;
use std::time::Duration;

use super::traits::{BoxFuture, Runtime, TaskHandle};

pub struct TokioTaskHandle(tokio::task::JoinHandle<()>);

impl TaskHandle for TokioTaskHandle {
    fn abort(&self) {
        self.0.abort();
    }
}

#[derive(Clone)]
pub struct NativeRuntime;

impl Runtime for NativeRuntime {
    type TaskHandle = TokioTaskHandle;

    fn spawn(
        &self,
        fut: Pin<Box<dyn std::future::Future<Output = ()> + Send + 'static>>,
    ) -> Self::TaskHandle {
        TokioTaskHandle(tokio::spawn(fut))
    }

    fn sleep(&self, duration: Duration) -> BoxFuture<()> {
        Box::pin(tokio::time::sleep(duration))
    }
}
