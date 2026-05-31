//go:build darwin

package process

import (
	"os/exec"
	"strconv"
	"strings"
)

// DefaultInspector returns the Darwin (macOS) Inspector.
func DefaultInspector() Inspector {
	return &DarwinInspector{}
}

// DarwinInspector implements Inspector for macOS.
type DarwinInspector struct{}

// GetChildProcesses returns PIDs of child processes using pgrep.
func (d *DarwinInspector) GetChildProcesses(pid int) []int {
	out, err := exec.Command("pgrep", "-P", strconv.Itoa(pid)).Output()
	if err != nil {
		return nil
	}

	var pids []int
	for _, line := range strings.Split(strings.TrimSpace(string(out)), "\n") {
		if line == "" {
			continue
		}
		if p, err := strconv.Atoi(line); err == nil {
			pids = append(pids, p)
		}
	}
	return pids
}

// GetProcessName returns the name of a process using ps.
func (d *DarwinInspector) GetProcessName(pid int) string {
	out, err := exec.Command("ps", "-o", "comm=", "-p", strconv.Itoa(pid)).Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
}

// IsRunning checks if a process is running using kill -0.
func (d *DarwinInspector) IsRunning(pid int) bool {
	err := exec.Command("kill", "-0", strconv.Itoa(pid)).Run()
	return err == nil
}

// GetState returns the state of a process using ps.
func (d *DarwinInspector) GetState(pid int) string {
	out, err := exec.Command("ps", "-o", "state=", "-p", strconv.Itoa(pid)).Output()
	if err != nil {
		return ""
	}
	state := strings.TrimSpace(string(out))
	if len(state) > 0 {
		return string(state[0])
	}
	return ""
}

// HasOpenFiles checks if a process has open file descriptors using lsof.
// Returns true if the process has files open beyond stdin/stdout/stderr.
func (d *DarwinInspector) HasOpenFiles(pid int) bool {
	// Use lsof to check for open files
	// -p: specify process ID
	// -Fn: output only file descriptor numbers
	out, err := exec.Command("lsof", "-p", strconv.Itoa(pid), "-Fn").Output()
	if err != nil {
		return false
	}

	// Count file descriptors (lines starting with 'f')
	// Exclude 0 (stdin), 1 (stdout), 2 (stderr)
	fdCount := 0
	for _, line := range strings.Split(string(out), "\n") {
		if strings.HasPrefix(line, "f") {
			fd := strings.TrimPrefix(line, "f")
			if fd != "0" && fd != "1" && fd != "2" && fd != "" {
				fdCount++
			}
		}
	}

	return fdCount > 0
}
