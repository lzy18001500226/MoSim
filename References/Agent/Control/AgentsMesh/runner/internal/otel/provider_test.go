package otel

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCappedWriterRotatesAtLimit(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "test.jsonl")

	w, err := newCappedWriter(path, 100)
	if err != nil {
		t.Fatal(err)
	}
	defer w.Close()

	data := make([]byte, 60)
	for i := range data {
		data[i] = 'x'
	}

	if _, err := w.Write(data); err != nil {
		t.Fatal(err)
	}
	if w.size != 60 {
		t.Fatalf("expected size 60, got %d", w.size)
	}

	if _, err := w.Write(data); err != nil {
		t.Fatal(err)
	}
	// Should have rotated: size reset to 60, .old file exists
	if w.size != 60 {
		t.Fatalf("expected size 60 after rotation, got %d", w.size)
	}

	oldPath := path + ".old"
	if _, err := os.Stat(oldPath); os.IsNotExist(err) {
		t.Fatal(".old file not created after rotation")
	}

	info, err := os.Stat(oldPath)
	if err != nil {
		t.Fatal(err)
	}
	if info.Size() != 60 {
		t.Fatalf("expected .old file size 60, got %d", info.Size())
	}
}

func TestCappedWriterSmallWritesNoRotation(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "test.jsonl")

	w, err := newCappedWriter(path, 1000)
	if err != nil {
		t.Fatal(err)
	}
	defer w.Close()

	for i := 0; i < 10; i++ {
		if _, err := w.Write([]byte("hello\n")); err != nil {
			t.Fatal(err)
		}
	}

	if w.size != 60 {
		t.Fatalf("expected size 60, got %d", w.size)
	}

	oldPath := path + ".old"
	if _, err := os.Stat(oldPath); !os.IsNotExist(err) {
		t.Fatal(".old file should not exist when under limit")
	}
}

func TestProviderDisabledViaEnv(t *testing.T) {
	t.Setenv("OTEL_SDK_DISABLED", "true")
	p, err := InitProvider(t.Context(), "test", "1.0.0")
	if err != nil {
		t.Fatal(err)
	}
	if p.enabled {
		t.Fatal("provider should be disabled")
	}
}

func TestBuildSamplerDefault(t *testing.T) {
	t.Setenv("OTEL_TRACES_SAMPLER_ARG", "")
	s := buildSampler()
	if s == nil {
		t.Fatal("sampler should not be nil")
	}
}

func TestBuildSamplerCustom(t *testing.T) {
	t.Setenv("OTEL_TRACES_SAMPLER_ARG", "0.5")
	s := buildSampler()
	if s == nil {
		t.Fatal("sampler should not be nil")
	}
}
