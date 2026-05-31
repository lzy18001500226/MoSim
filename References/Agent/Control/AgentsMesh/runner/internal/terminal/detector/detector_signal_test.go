package detector

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// Signal weight and behavior tests

func TestSignal_ActivityDominant(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	// Continuous small outputs
	for i := 0; i < 20; i++ {
		d.OnOutput(10)
		time.Sleep(20 * time.Millisecond)
	}

	// Screen shows prompt-like content
	d.OnScreenUpdate([]string{"Processing...", ">"})

	assert.Equal(t, StateExecuting, d.DetectState(), "Active output should override prompt")
}

func TestSignal_StabilityRequired(t *testing.T) {
	d := NewMultiSignalDetector(MultiSignalConfig{
		IdleThreshold:    30 * time.Millisecond,
		ConfirmThreshold: 30 * time.Millisecond,
		MinStableTime:    100 * time.Millisecond,
		WaitingThreshold: 0.6,
	})

	d.OnOutput(100)
	d.OnScreenUpdate([]string{">", ""})
	time.Sleep(50 * time.Millisecond)
	d.OnScreenUpdate([]string{"> ", ""})
	time.Sleep(50 * time.Millisecond)
	d.OnScreenUpdate([]string{">  ", ""})

	assert.NotEqual(t, StateWaiting, d.DetectState(), "Unstable screen should prevent waiting")
}

func TestSignal_PromptBoost(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 50, []string{
		"Are you sure you want to delete all files? (yes/no)",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Strong prompt should help reach threshold")

	result := d.GetLastPromptResult()
	assert.True(t, result.IsPrompt)
	assert.Equal(t, PromptTypeConfirm, result.PromptType)
}

func TestSignal_OSCWaitingIndicator(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	d.OnOutput(100)
	d.OnOSCTitle("claude ✳ myproject")
	simulateOutputAndScreen(d, 0, []string{"Ready.", "", ">"})

	assert.Equal(t, StateWaiting, d.DetectState(), "OSC with ✳ should help detect Waiting")
}

func TestSignal_OSCOverriddenByOutput(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	d.OnOSCTitle("claude ✳ myproject")
	simulateContinuousOutput(d, 5, 100, []string{"Processing..."})

	assert.Equal(t, StateExecuting, d.DetectState(), "Active output should override OSC")
}

func TestTransition_QuickWaitingDetection(t *testing.T) {
	d := NewMultiSignalDetector(MultiSignalConfig{
		IdleThreshold:    30 * time.Millisecond,
		ConfirmThreshold: 30 * time.Millisecond,
		MinStableTime:    30 * time.Millisecond,
		WaitingThreshold: 0.6,
	})

	startTime := time.Now()
	d.OnOutput(100)
	d.OnScreenUpdate([]string{"Continue? (y/n)"})

	var state AgentState
	for time.Since(startTime) < 500*time.Millisecond {
		time.Sleep(20 * time.Millisecond)
		d.OnScreenUpdate([]string{"Continue? (y/n)"})
		state = d.DetectState()
		if state == StateWaiting {
			break
		}
	}

	elapsed := time.Since(startTime)
	assert.Equal(t, StateWaiting, state, "Should detect waiting")
	assert.Less(t, elapsed, 200*time.Millisecond, "Should detect within 200ms")
}

func TestTransition_QuickExecutingResume(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	// Get to waiting state
	simulateOutputAndScreen(d, 100, []string{">", ""})
	d.DetectState()
	assert.Equal(t, StateWaiting, d.GetState())

	// New output - should resume immediately
	startTime := time.Now()
	d.OnOutput(50)
	elapsed := time.Since(startTime)

	assert.Equal(t, StateExecuting, d.GetState(), "Should return to Executing")
	assert.Less(t, elapsed, 5*time.Millisecond, "Should be instant")
}

func TestRegression_QuickBursts(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	for round := 0; round < 3; round++ {
		for i := 0; i < 5; i++ {
			d.OnOutput(20)
		}
		d.OnScreenUpdate([]string{"Line " + string(rune('A'+round))})
		time.Sleep(30 * time.Millisecond)
		d.DetectState()
	}

	assert.Equal(t, StateExecuting, d.GetState(), "Quick bursts should stay Executing")
}
