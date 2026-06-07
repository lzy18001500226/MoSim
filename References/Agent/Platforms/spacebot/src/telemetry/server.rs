//! HTTP server exposing the Prometheus /metrics endpoint.

use super::Metrics;
use crate::config::MetricsConfig;

use axum::Router;
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::routing::get;
use prometheus::Encoder as _;
use tokio::sync::watch;

use std::net::SocketAddr;

/// Spawn the metrics HTTP server as a background tokio task.
///
/// Returns the `JoinHandle` so the caller can hold it for lifetime management.
/// The server shuts down when `shutdown_rx` signals true.
pub async fn start_metrics_server(
    config: &MetricsConfig,
    shutdown_rx: watch::Receiver<bool>,
) -> anyhow::Result<tokio::task::JoinHandle<()>> {
    let raw_bind = config.bind.trim_start_matches('[').trim_end_matches(']');
    let bind_str = if raw_bind.contains(':') {
        format!("[{}]:{}", raw_bind, config.port)
    } else {
        format!("{}:{}", raw_bind, config.port)
    };
    let bind: SocketAddr = bind_str.parse().map_err(|error| {
        anyhow::anyhow!("invalid metrics bind address '{}': {}", bind_str, error)
    })?;

    let app = Router::new()
        .route("/metrics", get(metrics_handler))
        .route("/health", get(health_handler));

    let listener = tokio::net::TcpListener::bind(bind)
        .await
        .map_err(|error| anyhow::anyhow!("failed to bind metrics server to {}: {}", bind, error))?;

    tracing::info!(address = %bind, "metrics server started");

    let handle = tokio::spawn(async move {
        let mut shutdown_rx = shutdown_rx;
        let shutdown_signal = async move {
            let _ = shutdown_rx.wait_for(|shutdown| *shutdown).await;
        };

        if let Err(error) = axum::serve(listener, app)
            .with_graceful_shutdown(shutdown_signal)
            .await
        {
            tracing::error!(%error, "metrics server failed");
        }
    });

    Ok(handle)
}

async fn metrics_handler() -> impl IntoResponse {
    let metrics = Metrics::global();
    let encoder = prometheus::TextEncoder::new();
    let mut buffer = Vec::new();

    match encoder.encode(&metrics.registry.gather(), &mut buffer) {
        Ok(()) => match String::from_utf8(buffer) {
            Ok(text) => (
                StatusCode::OK,
                [("content-type", "text/plain; version=0.0.4; charset=utf-8")],
                text,
            )
                .into_response(),
            Err(error) => {
                tracing::warn!(%error, "metrics encoding produced invalid UTF-8");
                StatusCode::INTERNAL_SERVER_ERROR.into_response()
            }
        },
        Err(error) => {
            tracing::warn!(%error, "failed to encode metrics");
            StatusCode::INTERNAL_SERVER_ERROR.into_response()
        }
    }
}

async fn health_handler() -> impl IntoResponse {
    StatusCode::OK
}
