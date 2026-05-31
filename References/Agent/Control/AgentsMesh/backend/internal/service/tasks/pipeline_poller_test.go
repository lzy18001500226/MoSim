package tasks

import (
	"testing"
)

func TestSplitKey(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected []string
	}{
		{
			name:     "simple key",
			input:    "12345:67890",
			expected: []string{"12345", "67890"},
		},
		{
			name:     "single part",
			input:    "single",
			expected: []string{"single"},
		},
		{
			name:     "three parts",
			input:    "a:b:c",
			expected: []string{"a", "b", "c"},
		},
		{
			name:     "empty string",
			input:    "",
			expected: nil,
		},
		{
			name:     "trailing colon",
			input:    "abc:",
			expected: []string{"abc"},
		},
		{
			name:     "leading colon",
			input:    ":abc",
			expected: []string{":abc"}, // Current implementation keeps colon attached
		},
		{
			name:     "multiple colons",
			input:    "a::b",
			expected: []string{"a", ":b"}, // Current implementation keeps colon attached
		},
		{
			name:     "project pipeline format",
			input:    "project-123:pipeline-456",
			expected: []string{"project-123", "pipeline-456"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := splitKey(tt.input)

			if len(result) != len(tt.expected) {
				t.Errorf("splitKey(%q) len = %d, want %d", tt.input, len(result), len(tt.expected))
				return
			}

			for i, v := range result {
				if v != tt.expected[i] {
					t.Errorf("splitKey(%q)[%d] = %q, want %q", tt.input, i, v, tt.expected[i])
				}
			}
		})
	}
}

func TestSplitKeyEdgeCases(t *testing.T) {
	t.Run("numeric ids", func(t *testing.T) {
		parts := splitKey("123:456")
		if len(parts) != 2 {
			t.Errorf("expected 2 parts, got %d", len(parts))
		}
		if parts[0] != "123" || parts[1] != "456" {
			t.Errorf("unexpected parts: %v", parts)
		}
	})

	t.Run("job prefix key", func(t *testing.T) {
		parts := splitKey("12345:job_67890")
		if len(parts) != 2 {
			t.Errorf("expected 2 parts, got %d", len(parts))
		}
		if parts[1] != "job_67890" {
			t.Errorf("expected 'job_67890', got %s", parts[1])
		}
	})

	t.Run("long ids", func(t *testing.T) {
		parts := splitKey("1234567890:9876543210")
		if len(parts) != 2 {
			t.Errorf("expected 2 parts, got %d", len(parts))
		}
	})
}
