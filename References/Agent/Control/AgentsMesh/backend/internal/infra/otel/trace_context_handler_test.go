package otel

import (
	"context"
	"log/slog"
	"sync"
	"testing"

	sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

type captureHandler struct {
	mu      sync.Mutex
	records []slog.Record
	attrs   []slog.Attr
	group   string
}

func (h *captureHandler) Enabled(_ context.Context, _ slog.Level) bool { return true }

func (h *captureHandler) Handle(_ context.Context, r slog.Record) error {
	h.mu.Lock()
	defer h.mu.Unlock()
	h.records = append(h.records, r)
	return nil
}

func (h *captureHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
	return &captureHandler{attrs: attrs}
}

func (h *captureHandler) WithGroup(name string) slog.Handler {
	return &captureHandler{group: name}
}

func (h *captureHandler) lastRecord() (slog.Record, bool) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if len(h.records) == 0 {
		return slog.Record{}, false
	}
	return h.records[len(h.records)-1], true
}

func TestTraceContextHandlerInjectsTraceFields(t *testing.T) {
	inner := &captureHandler{}
	handler := NewTraceContextHandler(inner)

	tp := sdktrace.NewTracerProvider()
	defer tp.Shutdown(context.Background())

	ctx, span := tp.Tracer("test").Start(context.Background(), "test-span")
	defer span.End()

	logger := slog.New(handler)
	logger.InfoContext(ctx, "hello with trace")

	rec, ok := inner.lastRecord()
	if !ok {
		t.Fatal("no record captured")
	}

	var hasTraceID, hasSpanID bool
	rec.Attrs(func(a slog.Attr) bool {
		switch a.Key {
		case "trace_id":
			hasTraceID = true
			if a.Value.String() == "" || a.Value.String() == "00000000000000000000000000000000" {
				t.Errorf("trace_id should be non-zero, got %q", a.Value.String())
			}
		case "span_id":
			hasSpanID = true
			if a.Value.String() == "" || a.Value.String() == "0000000000000000" {
				t.Errorf("span_id should be non-zero, got %q", a.Value.String())
			}
		}
		return true
	})

	if !hasTraceID {
		t.Error("expected trace_id attribute to be injected")
	}
	if !hasSpanID {
		t.Error("expected span_id attribute to be injected")
	}
}

func TestTraceContextHandlerNoInjectionWithoutSpan(t *testing.T) {
	inner := &captureHandler{}
	handler := NewTraceContextHandler(inner)

	logger := slog.New(handler)
	logger.InfoContext(context.Background(), "hello without trace")

	rec, ok := inner.lastRecord()
	if !ok {
		t.Fatal("no record captured")
	}

	rec.Attrs(func(a slog.Attr) bool {
		if a.Key == "trace_id" || a.Key == "span_id" {
			t.Errorf("unexpected attribute %q injected when no span in context", a.Key)
		}
		return true
	})
}

func TestTraceContextHandlerWithAttrs(t *testing.T) {
	inner := &captureHandler{}
	handler := NewTraceContextHandler(inner)

	derived := handler.WithAttrs([]slog.Attr{slog.String("key", "val")})

	tch, ok := derived.(*traceContextHandler)
	if !ok {
		t.Fatal("WithAttrs should return a *traceContextHandler")
	}
	captInner, ok := tch.inner.(*captureHandler)
	if !ok {
		t.Fatal("inner handler should be a *captureHandler")
	}
	if len(captInner.attrs) != 1 || captInner.attrs[0].Key != "key" {
		t.Errorf("attrs not propagated, got %v", captInner.attrs)
	}
}

func TestTraceContextHandlerWithGroup(t *testing.T) {
	inner := &captureHandler{}
	handler := NewTraceContextHandler(inner)

	derived := handler.WithGroup("mygroup")

	tch, ok := derived.(*traceContextHandler)
	if !ok {
		t.Fatal("WithGroup should return a *traceContextHandler")
	}
	captInner, ok := tch.inner.(*captureHandler)
	if !ok {
		t.Fatal("inner handler should be a *captureHandler")
	}
	if captInner.group != "mygroup" {
		t.Errorf("group not propagated, got %q", captInner.group)
	}
}
