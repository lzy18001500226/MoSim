// Package process provides process inspection utilities.
package process

// Inspector provides methods to inspect process information.
// This interface abstracts system-specific process inspection,
// allowing for platform-specific implementations and easy testing.
type Inspector interface {
	// GetChildProcesses returns PIDs of child processes.
	GetChildProcesses(pid int) []int

	// GetProcessName returns the name of a process.
	GetProcessName(pid int) string

	// IsRunning checks if a process is running.
	IsRunning(pid int) bool

	// GetState returns the state of a process (R, S, D, etc.).
	GetState(pid int) string

	// HasOpenFiles checks if a process has open file descriptors (excluding stdin/out/err).
	// This helps detect if a process is actively doing I/O.
	HasOpenFiles(pid int) bool
}

// DefaultInspector returns the appropriate Inspector for the current platform.
// Platform-specific implementations are in darwin.go, linux.go, etc.
