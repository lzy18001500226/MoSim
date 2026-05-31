package detector

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// Generic coding scenarios that apply to all agents

func TestGeneric_ShellPrompt(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 50, []string{
		"user@hostname:~/project$ ",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Shell prompt should be Waiting")
}

func TestGeneric_FancyPrompt(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 100, []string{
		"",
		"╭─ ~/projects/myapp",
		"╰─❯ ",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Fancy prompt should be Waiting")
}

func TestGeneric_PagerLess(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 500, []string{
		"package main",
		"",
		"func main() {",
		"    fmt.Println(\"Hello\")",
		"}",
		":",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Pager ':' should be Waiting")
}

func TestGeneric_PasswordPrompt(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 50, []string{
		"Password:",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Password prompt should be Waiting")
}

func TestGeneric_SudoPrompt(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 80, []string{
		"[sudo] password for user:",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Sudo prompt should be Waiting")
}

func TestGeneric_SSHPassphrase(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 100, []string{
		"Enter passphrase for key '/home/user/.ssh/id_rsa':",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "SSH passphrase should be Waiting")
}

func TestGeneric_NPMInit(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 150, []string{
		"This utility will walk you through creating a package.json file.",
		"",
		"package name: (my-project)",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "npm init should be Waiting")
}

func TestGeneric_LongOperation(t *testing.T) {
	d := NewMultiSignalDetector(MultiSignalConfig{
		IdleThreshold:    100 * time.Millisecond,
		ConfirmThreshold: 100 * time.Millisecond,
		MinStableTime:    100 * time.Millisecond,
		WaitingThreshold: 0.6,
	})

	// Output with gaps shorter than threshold
	d.OnOutput(500)
	d.OnScreenUpdate([]string{"Running: npm install", "added 50 packages"})
	d.DetectState()

	time.Sleep(80 * time.Millisecond)

	d.OnOutput(300)
	d.OnScreenUpdate([]string{"Running: npm install", "added 100 packages"})

	assert.Equal(t, StateExecuting, d.DetectState(), "Long operation should be Executing")
}

func TestGeneric_ErrorWithContinue(t *testing.T) {
	d := NewMultiSignalDetector(testDetectorConfig())

	simulateOutputAndScreen(d, 200, []string{
		"Error: Connection refused",
		"Stack trace:",
		"  at connect (net.go:123)",
		"",
		"Press Enter to continue or Ctrl+C to abort",
	})

	assert.Equal(t, StateWaiting, d.DetectState(), "Error continue should be Waiting")
}
