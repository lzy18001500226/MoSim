package monitor

import (
	"sync"
)

// mockInspector is a mock implementation of process.Inspector for testing
type mockInspector struct {
	isRunning       map[int]bool
	processNames    map[int]string
	childProcesses  map[int][]int
	processStates   map[int]string
	hasOpenFilesMap map[int]bool
	mu              sync.Mutex
}

func newMockInspector() *mockInspector {
	return &mockInspector{
		isRunning:       make(map[int]bool),
		processNames:    make(map[int]string),
		childProcesses:  make(map[int][]int),
		processStates:   make(map[int]string),
		hasOpenFilesMap: make(map[int]bool),
	}
}

func (m *mockInspector) GetChildProcesses(pid int) []int {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.childProcesses[pid]
}

func (m *mockInspector) GetProcessName(pid int) string {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.processNames[pid]
}

func (m *mockInspector) IsRunning(pid int) bool {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.isRunning[pid]
}

func (m *mockInspector) GetState(pid int) string {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.processStates[pid]
}

func (m *mockInspector) HasOpenFiles(pid int) bool {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.hasOpenFilesMap[pid]
}
