package otel

import (
	"context"
	"testing"

	sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

func TestInitProviderDisabledViaEnv(t *testing.T) {
	t.Setenv("OTEL_SDK_DISABLED", "true")
	t.Setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

	p, err := InitProvider(context.Background(), "test-svc", "0.1.0")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if p.enabled {
		t.Error("provider should be disabled when OTEL_SDK_DISABLED=true")
	}
	if p.tp != nil {
		t.Error("TracerProvider should be nil when disabled")
	}
	if p.mp != nil {
		t.Error("MeterProvider should be nil when disabled")
	}
}

func TestInitProviderDisabledNoEndpoint(t *testing.T) {
	t.Setenv("OTEL_SDK_DISABLED", "false")
	t.Setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")

	p, err := InitProvider(context.Background(), "test-svc", "0.1.0")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if p.enabled {
		t.Error("provider should be disabled when OTEL_EXPORTER_OTLP_ENDPOINT is empty")
	}
}

func TestBuildSamplerDefault(t *testing.T) {
	t.Setenv("OTEL_TRACES_SAMPLER_ARG", "")

	s := buildSampler()
	if s == nil {
		t.Fatal("sampler should not be nil")
	}

	want := sdktrace.ParentBased(sdktrace.TraceIDRatioBased(defaultSamplingRatio)).Description()
	if s.Description() != want {
		t.Errorf("sampler description = %q, want %q", s.Description(), want)
	}
}

func TestBuildSamplerCustomRatio(t *testing.T) {
	t.Setenv("OTEL_TRACES_SAMPLER_ARG", "0.5")

	s := buildSampler()
	if s == nil {
		t.Fatal("sampler should not be nil")
	}

	want := sdktrace.ParentBased(sdktrace.TraceIDRatioBased(0.5)).Description()
	if s.Description() != want {
		t.Errorf("sampler description = %q, want %q", s.Description(), want)
	}
}

func TestBuildSamplerInvalidFallsBackToDefault(t *testing.T) {
	t.Setenv("OTEL_TRACES_SAMPLER_ARG", "not-a-number")

	s := buildSampler()
	if s == nil {
		t.Fatal("sampler should not be nil")
	}

	want := sdktrace.ParentBased(sdktrace.TraceIDRatioBased(defaultSamplingRatio)).Description()
	if s.Description() != want {
		t.Errorf("sampler description = %q, want %q (should fall back to default)", s.Description(), want)
	}
}
