package config

import (
	"os"
	"path/filepath"
	"testing"
)

// Tests for config validation

func TestConfigValidateMissingServerURL(t *testing.T) {
	cfg := &Config{
		ServerURL: "",
	}

	err := cfg.Validate()
	if err == nil {
		t.Error("expected error for missing server_url")
	}
}

func TestConfigValidateMissingGRPCConfig(t *testing.T) {
	cfg := &Config{
		ServerURL: "https://localhost",
		// No gRPC config
	}

	err := cfg.Validate()
	if err == nil {
		t.Error("expected error for missing gRPC config")
	}
}

func TestConfigValidateWithGRPCConfig(t *testing.T) {
	tmpDir := t.TempDir()

	// Create test certificate files
	certFile := filepath.Join(tmpDir, "runner.crt")
	keyFile := filepath.Join(tmpDir, "runner.key")
	caFile := filepath.Join(tmpDir, "ca.crt")

	os.WriteFile(certFile, []byte("cert"), 0600)
	os.WriteFile(keyFile, []byte("key"), 0600)
	os.WriteFile(caFile, []byte("ca"), 0644)

	cfg := &Config{
		ServerURL:         "https://localhost",
		GRPCEndpoint:      "localhost:9443",
		CertFile:          certFile,
		KeyFile:           keyFile,
		CAFile:            caFile,
		MaxConcurrentPods: 5,
		WorkspaceRoot:     tmpDir,
	}

	err := cfg.Validate()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
}

func TestConfigValidateInvalidMaxPods(t *testing.T) {
	tmpDir := t.TempDir()

	// Create test certificate files
	certFile := filepath.Join(tmpDir, "runner.crt")
	keyFile := filepath.Join(tmpDir, "runner.key")
	caFile := filepath.Join(tmpDir, "ca.crt")

	os.WriteFile(certFile, []byte("cert"), 0600)
	os.WriteFile(keyFile, []byte("key"), 0600)
	os.WriteFile(caFile, []byte("ca"), 0644)

	cfg := &Config{
		ServerURL:         "https://localhost",
		GRPCEndpoint:      "localhost:9443",
		CertFile:          certFile,
		KeyFile:           keyFile,
		CAFile:            caFile,
		MaxConcurrentPods: 0,
	}

	err := cfg.Validate()
	if err == nil {
		t.Error("expected error for invalid max_concurrent_pods")
	}
}

func TestConfigValidateCreatesWorkspaceDir(t *testing.T) {
	tmpDir := t.TempDir()
	workspaceDir := filepath.Join(tmpDir, "new_workspace")

	// Create test certificate files
	certFile := filepath.Join(tmpDir, "runner.crt")
	keyFile := filepath.Join(tmpDir, "runner.key")
	caFile := filepath.Join(tmpDir, "ca.crt")

	os.WriteFile(certFile, []byte("cert"), 0600)
	os.WriteFile(keyFile, []byte("key"), 0600)
	os.WriteFile(caFile, []byte("ca"), 0644)

	cfg := &Config{
		ServerURL:         "https://localhost",
		GRPCEndpoint:      "localhost:9443",
		CertFile:          certFile,
		KeyFile:           keyFile,
		CAFile:            caFile,
		MaxConcurrentPods: 5,
		WorkspaceRoot:     workspaceDir,
	}

	err := cfg.Validate()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	// Directory should be created
	if _, err := os.Stat(workspaceDir); os.IsNotExist(err) {
		t.Error("workspace directory was not created")
	}
}

func TestConfigValidateGRPCMissingFiles(t *testing.T) {
	cfg := &Config{
		ServerURL:    "https://localhost",
		GRPCEndpoint: "localhost:9443",
		CertFile:     "/nonexistent/cert",
		KeyFile:      "/nonexistent/key",
		CAFile:       "/nonexistent/ca",
	}

	err := cfg.Validate()
	if err == nil {
		t.Error("expected error for missing certificate files")
	}
}
