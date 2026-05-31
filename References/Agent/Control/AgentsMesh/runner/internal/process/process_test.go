//go:build darwin

package process

import (
	"os"
	"os/exec"
	"testing"
)

// --- Test Interface ---

func TestInspectorInterface(t *testing.T) {
	// Verify that DarwinInspector implements Inspector interface
	var _ Inspector = (*DarwinInspector)(nil)
}

// --- Test DefaultInspector ---

func TestDefaultInspector(t *testing.T) {
	inspector := DefaultInspector()

	if inspector == nil {
		t.Fatal("DefaultInspector returned nil")
	}
}

// --- Test DarwinInspector ---

func TestDarwinInspectorGetChildProcesses(t *testing.T) {
	inspector := &DarwinInspector{}

	// Test with current process - should not panic
	pid := os.Getpid()
	children := inspector.GetChildProcesses(pid)

	// Result may be nil or empty, but should not panic
	_ = children
}

func TestDarwinInspectorGetChildProcessesWithChild(t *testing.T) {
	inspector := &DarwinInspector{}

	// Start a child process that sleeps
	cmd := exec.Command("sleep", "10")
	if err := cmd.Start(); err != nil {
		t.Skipf("Failed to start child process: %v", err)
	}
	defer cmd.Process.Kill()

	// Get child processes of current process
	pid := os.Getpid()
	children := inspector.GetChildProcesses(pid)

	// Should have at least one child (the sleep process)
	if len(children) == 0 {
		t.Error("GetChildProcesses should return at least one child")
	}

	// The child should be in the list
	found := false
	for _, cpid := range children {
		if cpid == cmd.Process.Pid {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("Child process %d not found in children: %v", cmd.Process.Pid, children)
	}
}

func TestDarwinInspectorGetChildProcessesInvalidPid(t *testing.T) {
	inspector := &DarwinInspector{}

	// Test with invalid PID - should return nil
	children := inspector.GetChildProcesses(-1)

	if children != nil {
		t.Errorf("GetChildProcesses for invalid PID: got %v, want nil", children)
	}
}

func TestDarwinInspectorGetProcessName(t *testing.T) {
	inspector := &DarwinInspector{}

	// Test with current process
	pid := os.Getpid()
	name := inspector.GetProcessName(pid)

	// Should return a non-empty name
	if name == "" {
		t.Error("GetProcessName for current process should not be empty")
	}
}

func TestDarwinInspectorGetProcessNameInvalidPid(t *testing.T) {
	inspector := &DarwinInspector{}

	// Test with invalid PID - should return empty string
	name := inspector.GetProcessName(-1)

	if name != "" {
		t.Errorf("GetProcessName for invalid PID: got %v, want empty", name)
	}
}

func TestDarwinInspectorIsRunning(t *testing.T) {
	inspector := &DarwinInspector{}

	// Current process should be running
	pid := os.Getpid()
	if !inspector.IsRunning(pid) {
		t.Error("IsRunning should return true for current process")
	}
}

func TestDarwinInspectorIsRunningInvalidPid(t *testing.T) {
	inspector := &DarwinInspector{}

	// Very large PID that definitely doesn't exist
	// Note: -1 may behave differently on some systems
	isRunning := inspector.IsRunning(999999998)

	if isRunning {
		t.Error("IsRunning should return false for non-existent PID")
	}
}

func TestDarwinInspectorIsRunningNonExistentPid(t *testing.T) {
	inspector := &DarwinInspector{}

	// Very large PID that likely doesn't exist
	if inspector.IsRunning(999999999) {
		t.Error("IsRunning should return false for non-existent PID")
	}
}

func TestDarwinInspectorGetState(t *testing.T) {
	inspector := &DarwinInspector{}

	// Test with current process
	pid := os.Getpid()
	state := inspector.GetState(pid)

	// Should return a state (S for sleeping is common for test processes)
	if state == "" {
		t.Error("GetState for current process should not be empty")
	}

	// State should be a single character
	if len(state) > 1 {
		t.Errorf("GetState should return single char, got: %v", state)
	}
}

func TestDarwinInspectorGetStateInvalidPid(t *testing.T) {
	inspector := &DarwinInspector{}

	state := inspector.GetState(-1)

	if state != "" {
		t.Errorf("GetState for invalid PID: got %v, want empty", state)
	}
}

func TestDarwinInspectorHasOpenFiles(t *testing.T) {
	inspector := &DarwinInspector{}

	// Current process should have open files (at least test files)
	pid := os.Getpid()
	hasFiles := inspector.HasOpenFiles(pid)

	// The test process typically has open files
	_ = hasFiles // May or may not have files depending on test environment
}

func TestDarwinInspectorHasOpenFilesInvalidPid(t *testing.T) {
	inspector := &DarwinInspector{}

	hasFiles := inspector.HasOpenFiles(-1)

	if hasFiles {
		t.Error("HasOpenFiles should return false for invalid PID")
	}
}

// --- Benchmark Tests ---

func BenchmarkDarwinInspectorIsRunning(b *testing.B) {
	inspector := &DarwinInspector{}
	pid := os.Getpid()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		inspector.IsRunning(pid)
	}
}

func BenchmarkDarwinInspectorGetProcessName(b *testing.B) {
	inspector := &DarwinInspector{}
	pid := os.Getpid()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		inspector.GetProcessName(pid)
	}
}

func BenchmarkDarwinInspectorGetState(b *testing.B) {
	inspector := &DarwinInspector{}
	pid := os.Getpid()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		inspector.GetState(pid)
	}
}

func BenchmarkDarwinInspectorGetChildProcesses(b *testing.B) {
	inspector := &DarwinInspector{}
	pid := os.Getpid()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		inspector.GetChildProcesses(pid)
	}
}
