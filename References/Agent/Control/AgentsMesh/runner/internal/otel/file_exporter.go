package otel

import (
	"os"
	"path/filepath"
	"runtime"
	"sync"
	"time"

	"go.opentelemetry.io/otel/exporters/stdout/stdoutmetric"
	"go.opentelemetry.io/otel/exporters/stdout/stdouttrace"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

const maxOTelFileSize = 50 * 1024 * 1024 // 50MB per file

func otelFileDir() string {
	if runtime.GOOS == "windows" {
		return filepath.Join(os.TempDir(), "agentsmesh")
	}
	return "/tmp/agentsmesh"
}

func initFileTracerProvider(res *resource.Resource) (*sdktrace.TracerProvider, *cappedWriter, error) {
	dir := otelFileDir()
	os.MkdirAll(dir, 0755)

	w, err := newCappedWriter(filepath.Join(dir, "traces.jsonl"), maxOTelFileSize)
	if err != nil {
		return nil, nil, err
	}

	exporter, err := stdouttrace.New(stdouttrace.WithWriter(w))
	if err != nil {
		w.Close()
		return nil, nil, err
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter, sdktrace.WithBatchTimeout(5*time.Second)),
		sdktrace.WithResource(res),
		sdktrace.WithSampler(buildSampler()),
	)
	return tp, w, nil
}

func initFileMeterProvider() (*sdkmetric.MeterProvider, *cappedWriter, error) {
	dir := otelFileDir()
	os.MkdirAll(dir, 0755)

	w, err := newCappedWriter(filepath.Join(dir, "metrics.jsonl"), maxOTelFileSize)
	if err != nil {
		return nil, nil, err
	}

	exporter, err := stdoutmetric.New(stdoutmetric.WithWriter(w))
	if err != nil {
		w.Close()
		return nil, nil, err
	}

	return sdkmetric.NewMeterProvider(
		sdkmetric.WithReader(sdkmetric.NewPeriodicReader(exporter, sdkmetric.WithInterval(30*time.Second))),
	), w, nil
}

type cappedWriter struct {
	file    *os.File
	path    string
	maxSize int64
	size    int64
	mu      sync.Mutex
}

func newCappedWriter(path string, maxSize int64) (*cappedWriter, error) {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return nil, err
	}
	info, _ := f.Stat()
	var size int64
	if info != nil {
		size = info.Size()
	}
	return &cappedWriter{file: f, path: path, maxSize: maxSize, size: size}, nil
}

func (w *cappedWriter) Write(p []byte) (int, error) {
	w.mu.Lock()
	defer w.mu.Unlock()

	if w.size+int64(len(p)) > w.maxSize {
		w.file.Close()
		_ = os.Rename(w.path, w.path+".old")
		f, err := os.Create(w.path)
		if err != nil {
			// Reopen old file to avoid nil w.file
			f, reopenErr := os.OpenFile(w.path+".old", os.O_WRONLY|os.O_APPEND, 0644)
			if reopenErr != nil {
				return 0, err
			}
			w.file = f
			return 0, err
		}
		w.file = f
		w.size = 0
	}
	n, err := w.file.Write(p)
	w.size += int64(n)
	return n, err
}

func (w *cappedWriter) Close() error {
	return w.file.Close()
}
