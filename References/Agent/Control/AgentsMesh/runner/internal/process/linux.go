//go:build linux

package process

import (
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
)

// DefaultInspector returns the Linux Inspector.
func DefaultInspector() Inspector {
	return &LinuxInspector{}
}

// LinuxInspector implements Inspector for Linux using /proc filesystem.
type LinuxInspector struct{}

// GetChildProcesses returns PIDs of child processes using /proc.
func (l *LinuxInspector) GetChildProcesses(pid int) []int {
	// Read /proc/<pid>/task/<tid>/children for each thread
	taskDir := filepath.Join("/proc", strconv.Itoa(pid), "task")
	entries, err := os.ReadDir(taskDir)
	if err != nil {
		// Fallback to pgrep
		return l.getChildrenViaPgrep(pid)
	}

	var pids []int
	seen := make(map[int]bool)

	for _, entry := range entries {
		childrenFile := filepath.Join(taskDir, entry.Name(), "children")
		data, err := os.ReadFile(childrenFile)
		if err != nil {
			continue
		}
		for _, pidStr := range strings.Fields(string(data)) {
			if p, err := strconv.Atoi(pidStr); err == nil && !seen[p] {
				pids = append(pids, p)
				seen[p] = true
			}
		}
	}

	if len(pids) == 0 {
		return l.getChildrenViaPgrep(pid)
	}
	return pids
}

func (l *LinuxInspector) getChildrenViaPgrep(pid int) []int {
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

// GetProcessName returns the name of a process using /proc/<pid>/comm.
func (l *LinuxInspector) GetProcessName(pid int) string {
	data, err := os.ReadFile(filepath.Join("/proc", strconv.Itoa(pid), "comm"))
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(data))
}

// IsRunning checks if a process is running by checking /proc/<pid>.
func (l *LinuxInspector) IsRunning(pid int) bool {
	_, err := os.Stat(filepath.Join("/proc", strconv.Itoa(pid)))
	return err == nil
}

// GetState returns the state of a process from /proc/<pid>/stat.
func (l *LinuxInspector) GetState(pid int) string {
	data, err := os.ReadFile(filepath.Join("/proc", strconv.Itoa(pid), "stat"))
	if err != nil {
		return ""
	}

	// Format: pid (comm) state ...
	// Find the closing paren to skip the command name (which may contain spaces)
	content := string(data)
	closeParenIdx := strings.LastIndex(content, ")")
	if closeParenIdx == -1 || closeParenIdx+2 >= len(content) {
		return ""
	}

	// State is the first field after ")"
	fields := strings.Fields(content[closeParenIdx+1:])
	if len(fields) > 0 {
		return fields[0]
	}
	return ""
}

// HasOpenFiles checks if a process has open file descriptors using /proc/<pid>/fd.
func (l *LinuxInspector) HasOpenFiles(pid int) bool {
	fdDir := filepath.Join("/proc", strconv.Itoa(pid), "fd")
	entries, err := os.ReadDir(fdDir)
	if err != nil {
		return false
	}

	// Count fds excluding 0, 1, 2 (stdin, stdout, stderr)
	for _, entry := range entries {
		fd := entry.Name()
		if fd != "0" && fd != "1" && fd != "2" {
			return true
		}
	}
	return false
}
