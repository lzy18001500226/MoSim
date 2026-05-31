package runner

import (
	"testing"
)

// --- Test HostInfo ---

func TestHostInfoScanNil(t *testing.T) {
	var hi HostInfo
	err := hi.Scan(nil)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if hi != nil {
		t.Error("expected nil HostInfo")
	}
}

func TestHostInfoScanValid(t *testing.T) {
	var hi HostInfo
	err := hi.Scan([]byte(`{"os": "darwin", "arch": "arm64"}`))
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if hi["os"] != "darwin" {
		t.Errorf("expected os 'darwin', got %v", hi["os"])
	}
	if hi["arch"] != "arm64" {
		t.Errorf("expected arch 'arm64', got %v", hi["arch"])
	}
}

func TestHostInfoScanInvalidType(t *testing.T) {
	var hi HostInfo
	err := hi.Scan("not bytes")
	if err == nil {
		t.Error("expected error for invalid type")
	}
}

func TestHostInfoScanInvalidJSON(t *testing.T) {
	var hi HostInfo
	err := hi.Scan([]byte(`invalid json`))
	if err == nil {
		t.Error("expected error for invalid JSON")
	}
}

func TestHostInfoValueNil(t *testing.T) {
	var hi HostInfo
	val, err := hi.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val != nil {
		t.Error("expected nil value")
	}
}

func TestHostInfoValueValid(t *testing.T) {
	hi := HostInfo{"os": "linux", "version": "5.4"}
	val, err := hi.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val == nil {
		t.Error("expected non-nil value")
	}
}
