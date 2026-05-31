package otel

import (
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/metric/noop"
)

var (
	PodActiveCount   metric.Int64UpDownCounter = noop.Int64UpDownCounter{}
	GRPCReconnects   metric.Int64Counter       = noop.Int64Counter{}
	RelayReconnects  metric.Int64Counter       = noop.Int64Counter{}
	PodBuildDuration metric.Float64Histogram   = noop.Float64Histogram{}
)

func InitMetrics() {
	m := otel.Meter("agentsmesh-runner")
	PodActiveCount, _ = m.Int64UpDownCounter("agentsmesh.runner.pod.active")
	GRPCReconnects, _ = m.Int64Counter("agentsmesh.runner.grpc.reconnects")
	RelayReconnects, _ = m.Int64Counter("agentsmesh.runner.relay.reconnects")
	PodBuildDuration, _ = m.Float64Histogram("agentsmesh.runner.pod.build.duration",
		metric.WithUnit("ms"))
}
