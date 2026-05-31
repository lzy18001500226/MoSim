package detector

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Cursor AI specific scenario tests
// Cursor has both inline and chat modes

func TestCursor_ChatPrompt(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 200, []string{
		"Cursor AI Chat",
		"",
		"Ask me anything about your code...",
		"",
		"You: ",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Cursor 'You:' prompt should be Waiting")
}

func TestCursor_Generating(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateContinuousOutput(d, 5, 100, []string{
		"You: Explain this function",
		"",
		"Cursor: ",
		"This function implements a",
	})

	assert.Equal(t, StateExecuting, d.GetState(), "Generating response should be Executing")
}

func TestCursor_AcceptReject(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 300, []string{
		"Suggested changes:",
		"",
		"+ import logging",
		"+ logger = logging.getLogger(__name__)",
		"",
		"[Tab] Accept  [Esc] Reject  [e] Edit",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Accept/Reject prompt should be Waiting")
}

func TestCursor_CommandPalette(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 150, []string{
		"Command Palette",
		"",
		"> ",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Command palette should be Waiting")
}

func TestCursor_InlineEdit(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateContinuousOutput(d, 4, 80, []string{
		"Editing inline...",
		"",
		"[Generating suggestion...]",
	})

	assert.Equal(t, StateExecuting, d.GetState(), "Inline edit should be Executing")
}

func TestCursor_DiffReview(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 250, []string{
		"Review changes:",
		"",
		"--- a/main.py",
		"+++ b/main.py",
		"@@ -1,3 +1,5 @@",
		"+import sys",
		" def main():",
		"",
		"Apply? (y)es / (n)o / (e)dit:",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Diff review should be Waiting")
}
