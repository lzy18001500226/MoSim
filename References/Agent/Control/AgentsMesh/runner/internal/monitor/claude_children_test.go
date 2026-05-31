package monitor

import (
	"testing"
	"time"
)

// Tests for active children detection

func TestMonitorHasActiveChildrenRunning(t *testing.T) {
	inspector := newMockInspector()
	monitor := NewMonitorWithInspector(time.Second, inspector)

	inspector.childProcesses[1] = []int{2}
	inspector.processStates[2] = "R" // Running state

	if !monitor.hasActiveChildren(1) {
		t.Error("hasActiveChildren should return true for running child")
	}
}

func TestMonitorHasActiveChildrenWithOpenFiles(t *testing.T) {
	inspector := newMockInspector()
	monitor := NewMonitorWithInspector(time.Second, inspector)

	inspector.childProcesses[1] = []int{2}
	inspector.processStates[2] = "S" // Sleeping
	inspector.hasOpenFilesMap[2] = true

	if !monitor.hasActiveChildren(1) {
		t.Error("hasActiveChildren should return true for child with open files")
	}
}

func TestMonitorHasActiveChildrenRecursive(t *testing.T) {
	inspector := newMockInspector()
	monitor := NewMonitorWithInspector(time.Second, inspector)

	inspector.childProcesses[1] = []int{2}
	inspector.processStates[2] = "S"
	inspector.childProcesses[2] = []int{3}
	inspector.processStates[3] = "R" // Grandchild is running

	if !monitor.hasActiveChildren(1) {
		t.Error("hasActiveChildren should return true for active grandchild")
	}
}

func TestMonitorHasActiveChildrenNone(t *testing.T) {
	inspector := newMockInspector()
	monitor := NewMonitorWithInspector(time.Second, inspector)

	inspector.childProcesses[1] = []int{2}
	inspector.processStates[2] = "S" // Sleeping
	inspector.hasOpenFilesMap[2] = false

	if monitor.hasActiveChildren(1) {
		t.Error("hasActiveChildren should return false when no active children")
	}
}

// Benchmark Tests

func BenchmarkMonitorCheckAllPods(b *testing.B) {
	inspector := newMockInspector()
	monitor := NewMonitorWithInspector(time.Second, inspector)

	// Register 10 pods
	for i := 0; i < 10; i++ {
		pid := 12345 + i
		inspector.isRunning[pid] = true
		monitor.RegisterPod("pod-"+string(rune('0'+i)), pid)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		monitor.checkAllPods()
	}
}

func BenchmarkMonitorGetStatus(b *testing.B) {
	monitor := NewMonitor(time.Second)
	monitor.RegisterPod("pod-1", 12345)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		monitor.GetStatus("pod-1")
	}
}
