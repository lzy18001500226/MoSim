//! Prometheus metrics collection and exposition.

mod registry;
mod server;

pub use registry::Metrics;
pub use server::start_metrics_server;
