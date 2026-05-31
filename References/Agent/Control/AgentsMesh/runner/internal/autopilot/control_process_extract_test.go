package autopilot

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Tests for extraction functions in control process

func TestExtractSummary(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{
			name:     "simple summary",
			input:    "This is a summary.\nMore details here.",
			expected: "This is a summary. More details here.",
		},
		{
			name:     "skip json lines",
			input:    "Summary line\n{\"key\": \"value\"}\nAnother line",
			expected: "Summary line Another line",
		},
		{
			name:     "fallback last 3 lines",
			input:    "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7",
			expected: "Line 5 Line 6 Line 7",
		},
		{
			name:     "long summary truncated",
			input:    "This is a very long line that exceeds 200 characters. " + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
			expected: "This is a very long line that exceeds 200 characters. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim venia...",
		},
		{
			name:     "extract after TASK_COMPLETED",
			input:    "Some noise\nTASK_COMPLETED\nThis is the actual summary",
			expected: "This is the actual summary",
		},
		{
			name:     "extract after CONTINUE",
			input:    "Prefix text\nCONTINUE\nSent instruction to worker",
			expected: "Sent instruction to worker",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := ExtractSummary(tt.input)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestExtractJSONBlock(t *testing.T) {
	tests := []struct {
		name        string
		input       string
		expectNil   bool
		expectKey   string
		expectValue interface{}
	}{
		{
			name:        "simple json",
			input:       `Some text {"key": "value"} more text`,
			expectNil:   false,
			expectKey:   "key",
			expectValue: "value",
		},
		{
			name:        "nested json",
			input:       `Text {"outer": {"inner": 123}} end`,
			expectNil:   false,
			expectKey:   "outer",
			expectValue: map[string]interface{}{"inner": float64(123)},
		},
		{
			name:      "no json",
			input:     "No JSON content here",
			expectNil: true,
		},
		{
			name:      "incomplete json",
			input:     `Start {"key": "value" without closing`,
			expectNil: true,
		},
		{
			name:      "invalid json",
			input:     `{invalid json content}`,
			expectNil: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := ExtractJSONBlock(tt.input)
			if tt.expectNil {
				assert.Nil(t, result)
			} else {
				assert.NotNil(t, result)
				assert.Equal(t, tt.expectValue, result[tt.expectKey])
			}
		})
	}
}

func TestExtractSessionID(t *testing.T) {
	tests := []struct {
		name      string
		input     string
		expected  string
		shouldSet bool
	}{
		{
			name:      "json format",
			input:     `{"session_id": "abc-123-def", "result": "ok"}`,
			expected:  "abc-123-def",
			shouldSet: true,
		},
		{
			name:      "embedded in text",
			input:     `Response text "session_id": "xyz-789" more text`,
			expected:  "xyz-789",
			shouldSet: true,
		},
		{
			name:      "no session_id",
			input:     `{"result": "ok"}`,
			expected:  "",
			shouldSet: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := ExtractSessionID(tt.input)

			if tt.shouldSet {
				assert.Equal(t, tt.expected, result)
			} else {
				assert.Empty(t, result)
			}
		})
	}
}
