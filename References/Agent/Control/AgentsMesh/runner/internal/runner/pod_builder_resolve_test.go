package runner

import (
	"context"
	"strings"
	"testing"

	sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

func TestInjectTraceparentWithValidSpan(t *testing.T) {
	tp := sdktrace.NewTracerProvider()
	defer tp.Shutdown(context.Background())

	ctx, span := tp.Tracer("test").Start(context.Background(), "test-span")
	defer span.End()

	envVars := map[string]string{"PATH": "/usr/bin"}
	injectTraceparent(ctx, envVars)

	tp_val, ok := envVars["TRACEPARENT"]
	if !ok {
		t.Fatal("TRACEPARENT not injected")
	}
	if !strings.HasPrefix(tp_val, "00-") {
		t.Fatalf("TRACEPARENT has wrong format: %s", tp_val)
	}
	parts := strings.Split(tp_val, "-")
	if len(parts) != 4 {
		t.Fatalf("TRACEPARENT should have 4 parts, got %d: %s", len(parts), tp_val)
	}
	if len(parts[1]) != 32 {
		t.Fatalf("trace_id should be 32 hex chars, got %d", len(parts[1]))
	}
	if len(parts[2]) != 16 {
		t.Fatalf("span_id should be 16 hex chars, got %d", len(parts[2]))
	}
}

func TestInjectTraceparentWithoutSpan(t *testing.T) {
	envVars := map[string]string{"PATH": "/usr/bin"}
	injectTraceparent(context.Background(), envVars)

	if _, ok := envVars["TRACEPARENT"]; ok {
		t.Fatal("TRACEPARENT should not be injected without valid span")
	}
}

func TestBuildMergedEnvIncludesTermSettings(t *testing.T) {
	env := buildMergedEnv(map[string]string{})
	found := map[string]bool{}
	for _, e := range env {
		if strings.HasPrefix(e, "TERM=") {
			found["TERM"] = true
		}
		if strings.HasPrefix(e, "COLORTERM=") {
			found["COLORTERM"] = true
		}
	}
	if !found["TERM"] {
		t.Fatal("TERM not set in merged env")
	}
	if !found["COLORTERM"] {
		t.Fatal("COLORTERM not set in merged env")
	}
}

func TestBuildMergedEnvUserOverridesOS(t *testing.T) {
	env := buildMergedEnv(map[string]string{"MY_VAR": "custom_value"})
	for _, e := range env {
		if e == "MY_VAR=custom_value" {
			return
		}
	}
	t.Fatal("user env var not found in merged env")
}
