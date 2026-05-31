package detector

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewPromptDetector(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})
	assert.NotNil(t, d)
	assert.Equal(t, 100, d.maxPromptLength)

	d2 := NewPromptDetector(PromptDetectorConfig{MaxPromptLength: 50})
	assert.Equal(t, 50, d2.maxPromptLength)
}

func TestPromptDetector_DetectPrompt_Empty(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	result := d.DetectPrompt(nil)
	assert.False(t, result.IsPrompt)

	result = d.DetectPrompt([]string{})
	assert.False(t, result.IsPrompt)
}

func TestPromptDetector_DetectPrompt_CommandPrompts(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	tests := []struct {
		name     string
		lines    []string
		wantType PromptType
	}{
		{"shell $", []string{"$ "}, PromptTypeCommand},
		{"shell #", []string{"# "}, PromptTypeCommand},
		{"shell %", []string{"user@host% "}, PromptTypeCommand},
		{"arrow >", []string{"> "}, PromptTypeCommand},
		{"triple >>>", []string{">>> "}, PromptTypeCommand},
		{"fancy ❯", []string{"path ❯ "}, PromptTypeCommand},
		{"fancy ➜", []string{"➜ "}, PromptTypeCommand},
		// "Enter value:" ends with ":", which is detected as command prompt (colon is in promptEndSymbols)
		{"colon prompt", []string{"Enter value:"}, PromptTypeCommand},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := d.DetectPrompt(tt.lines)
			assert.True(t, result.IsPrompt, "should detect prompt for %s", tt.name)
			assert.Equal(t, tt.wantType, result.PromptType)
		})
	}
}

func TestPromptDetector_DetectPrompt_ConfirmPrompts(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	tests := []struct {
		name     string
		lines    []string
		wantType PromptType
	}{
		{"y/n parens", []string{"Continue? (y/n)"}, PromptTypeConfirm},
		{"y/n brackets", []string{"Proceed? [y/n]"}, PromptTypeConfirm},
		{"yes/no parens", []string{"Are you sure? (yes/no)"}, PromptTypeConfirm},
		{"yes/no brackets", []string{"Confirm? [yes/no]"}, PromptTypeConfirm},
		// "y or n" contains "continue" which matches isContinuePrompt pattern first
		{"y or n", []string{"Do you want to continue? y or n"}, PromptTypeContinue},
		// Questions containing "continue" match isContinuePrompt pattern
		{"question continue", []string{"Do you want to continue?"}, PromptTypeContinue},
		// Questions containing "proceed" match isContinuePrompt pattern ("to proceed")
		{"question proceed", []string{"Would you like to proceed?"}, PromptTypeContinue},
		// "Are you sure?" contains "sure" which matches isConfirmPrompt
		{"question sure", []string{"Are you sure?"}, PromptTypeConfirm},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := d.DetectPrompt(tt.lines)
			assert.True(t, result.IsPrompt, "should detect prompt for %s", tt.name)
			assert.Equal(t, tt.wantType, result.PromptType)
		})
	}
}

func TestPromptDetector_DetectPrompt_PermissionPrompts(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	tests := []struct {
		name  string
		lines []string
	}{
		{"allow", []string{"Allow this action?"}},
		{"approve", []string{"Approve the changes?"}},
		{"grant permission", []string{"Grant permission?"}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := d.DetectPrompt(tt.lines)
			assert.True(t, result.IsPrompt, "should detect prompt for %s", tt.name)
			assert.Equal(t, PromptTypePermission, result.PromptType)
		})
	}
}

func TestPromptDetector_DetectPrompt_ContinuePrompts(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	tests := []struct {
		name  string
		lines []string
	}{
		{"press any key", []string{"Press any key to continue..."}},
		{"press enter", []string{"Press Enter to proceed"}},
		{"hit enter", []string{"Hit enter when ready"}},
		{"to continue", []string{"-- More -- (press space to continue)"}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := d.DetectPrompt(tt.lines)
			assert.True(t, result.IsPrompt, "should detect prompt for %s", tt.name)
			assert.Equal(t, PromptTypeContinue, result.PromptType)
		})
	}
}

func TestPromptDetector_DetectPrompt_InputPrompts(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	tests := []struct {
		name  string
		lines []string
	}{
		{"enter name", []string{"Please enter your name:"}},
		{"provide value", []string{"Please provide a value:"}},
		{"question mark", []string{"What is your choice?"}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := d.DetectPrompt(tt.lines)
			assert.True(t, result.IsPrompt, "should detect prompt for %s", tt.name)
		})
	}
}

func TestPromptDetector_DetectPrompt_NotPrompts(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	tests := []struct {
		name  string
		lines []string
	}{
		{"empty line", []string{""}},
		{"long output", []string{"This is a very long line of output that is clearly not a prompt because prompts are usually short and this line keeps going and going and going"}},
		{"normal output", []string{"Processing files..."}},
		{"log output", []string{"[INFO] Starting server"}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := d.DetectPrompt(tt.lines)
			assert.False(t, result.IsPrompt, "should not detect prompt for %s", tt.name)
		})
	}
}

func TestPromptDetector_DetectPrompt_MultipleLines(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	// Prompt at the bottom (most common)
	lines := []string{
		"Some output line 1",
		"Some output line 2",
		"Some output line 3",
		"Continue? (y/n)",
	}

	result := d.DetectPrompt(lines)
	assert.True(t, result.IsPrompt)
	assert.Equal(t, PromptTypeConfirm, result.PromptType)
	assert.Equal(t, 3, result.LineIndex) // Last line (0-indexed)
}

func TestPromptDetector_DetectPrompt_PromptNotAtBottom(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	// Prompt in the middle (checks bottom 5 lines)
	lines := []string{
		"Line 1",
		"Line 2",
		"Continue? (y/n)",
		"Line 4",
		"",
	}

	result := d.DetectPrompt(lines)
	assert.True(t, result.IsPrompt)
	assert.Equal(t, 2, result.LineIndex)
}

func TestPromptDetector_BoxDrawingPrompt(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	// Claude Code style box prompt
	lines := []string{
		"│ Do you want to continue? │",
		"│ > Yes                    │",
	}

	result := d.DetectPrompt(lines)
	assert.True(t, result.IsPrompt)
}

func TestIsPromptChar(t *testing.T) {
	promptChars := []rune{'>', '<', '$', '#', '%', '?', ':', '»', '›', '⟩', '❯', '➜', '→'}
	for _, c := range promptChars {
		assert.True(t, IsPromptChar(c), "should be prompt char: %c", c)
	}

	nonPromptChars := []rune{'a', 'Z', '0', ' ', '.', ','}
	for _, c := range nonPromptChars {
		assert.False(t, IsPromptChar(c), "should not be prompt char: %c", c)
	}
}

// Note: TestStripANSI is already defined in virtual_terminal_test.go

func TestPromptDetector_Confidence(t *testing.T) {
	d := NewPromptDetector(PromptDetectorConfig{})

	// High confidence: confirm prompt at last line, short
	result := d.DetectPrompt([]string{"(y/n)"})
	assert.True(t, result.IsPrompt)
	assert.GreaterOrEqual(t, result.Confidence, 0.9)

	// Medium confidence: command prompt
	result = d.DetectPrompt([]string{"$ "})
	assert.True(t, result.IsPrompt)
	assert.GreaterOrEqual(t, result.Confidence, 0.7)
}
