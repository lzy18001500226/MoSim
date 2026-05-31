package detector

import (
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// False positive prevention tests - should NOT detect as waiting

func TestFP_ProgressBar(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateContinuousOutput(d, 5, 50, []string{
		"Downloading packages...",
		"[████████████░░░░░░░░░░░░░░░░░░] 40%",
		"Speed: 1.5MB/s ETA: 2min",
	})

	assert.Equal(t, StateExecuting, d.DetectState(), "Progress bar should be Executing")
}

func TestFP_LogWithQuestionMark(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateContinuousOutput(d, 5, 100, []string{
		"2024-01-15 10:30:01 [INFO] Processing request...",
		"2024-01-15 10:30:02 [WARN] Unknown parameter: maxRetries?",
		"2024-01-15 10:30:03 [INFO] Retrying connection...",
	})

	assert.Equal(t, StateExecuting, d.DetectState(), "Log output should be Executing")
}

func TestFP_CodeWithOperators(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateContinuousOutput(d, 3, 80, []string{
		"func compare(a, b int) bool {",
		"    if a > b {",
		"        return true",
		"    }",
		"    return a >= b && b > 0",
		"}",
	})

	assert.Equal(t, StateExecuting, d.DetectState(), "Code with '>' should be Executing")
}

func TestFP_StreamingWithPauses(t *testing.T) {
	d := NewMultiSignalDetector(MultiSignalConfig{
		IdleThreshold:    100 * time.Millisecond,
		ConfirmThreshold: 100 * time.Millisecond,
		MinStableTime:    100 * time.Millisecond,
		WaitingThreshold: 0.6,
	})

	responses := []string{"Here's how", " to implement", " a search", ":"}

	for _, chunk := range responses {
		d.OnOutput(len(chunk))
		d.OnScreenUpdate([]string{strings.Join(responses, "")})
		time.Sleep(60 * time.Millisecond)
		d.DetectState()
	}

	assert.Equal(t, StateExecuting, d.GetState(), "Streaming should be Executing")
}

func TestFP_CompilerWarnings(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateContinuousOutput(d, 4, 150, []string{
		"src/main.ts:10:5 - warning: Type 'string | undefined' is not assignable",
		"src/main.ts:15:3 - warning: Object is possibly 'undefined'",
		"Found 2 warnings",
	})

	assert.Equal(t, StateExecuting, d.DetectState(), "Compiler warnings should be Executing")
}

func TestFP_JsonOutput(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateContinuousOutput(d, 3, 100, []string{
		"{",
		`  "status": "processing",`,
		`  "progress": 50,`,
		`  "message": "What is the answer?"`,
		"}",
	})

	assert.Equal(t, StateExecuting, d.DetectState(), "JSON output should be Executing")
}

func TestFP_MarkdownOutput(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateContinuousOutput(d, 4, 80, []string{
		"# How to use this API?",
		"",
		"> Note: This is a blockquote",
		"",
		"1. First step",
		"2. Second step",
	})

	assert.Equal(t, StateExecuting, d.DetectState(), "Markdown should be Executing")
}

func TestFP_TestResults(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateContinuousOutput(d, 5, 100, []string{
		"=== RUN   TestSomething",
		"--- PASS: TestSomething (0.01s)",
		"=== RUN   TestAnother",
		"    test.go:10: Is this correct?",
		"--- PASS: TestAnother (0.02s)",
	})

	assert.Equal(t, StateExecuting, d.DetectState(), "Test output should be Executing")
}
