package autopilot

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Tests for helper functions

func TestExtractResultFromJSON_Valid(t *testing.T) {
	input := `{"result": "This is the result text.", "session_id": "123"}`
	result := ExtractResultFromJSON(input)
	assert.Equal(t, "This is the result text.", result)
}

func TestExtractResultFromJSON_Empty(t *testing.T) {
	input := `{"result": "", "session_id": "123"}`
	result := ExtractResultFromJSON(input)
	assert.Empty(t, result)
}

func TestExtractResultFromJSON_NoResult(t *testing.T) {
	input := `{"session_id": "123"}`
	result := ExtractResultFromJSON(input)
	assert.Empty(t, result)
}

func TestExtractResultFromJSON_InvalidJSON(t *testing.T) {
	input := `not json at all`
	result := ExtractResultFromJSON(input)
	assert.Empty(t, result)
}

func TestFindDecisionMarker_CaseInsensitive(t *testing.T) {
	tests := []struct {
		input    string
		expected DecisionType
	}{
		{"TASK_COMPLETED", DecisionCompleted},
		{"task_completed", DecisionCompleted},
		{"Task_Completed", DecisionCompleted},
		{"CONTINUE", DecisionContinue},
		{"continue", DecisionContinue},
		{"NEED_HUMAN_HELP", DecisionNeedHumanHelp},
		{"need_human_help", DecisionNeedHumanHelp},
		{"GIVE_UP", DecisionGiveUp},
		{"give_up", DecisionGiveUp},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			result := FindDecisionMarker(tt.input)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestFindDecisionMarker_NoMarker(t *testing.T) {
	result := FindDecisionMarker("No marker here")
	assert.Empty(t, result)
}

func TestFindDecisionMarker_MarkerInMiddle(t *testing.T) {
	// Marker must be at start of line
	input := "Line 1\n  TASK_COMPLETED\nLine 3"
	result := FindDecisionMarker(input)
	assert.Equal(t, DecisionCompleted, result)
}

func TestExtractSummary_AfterMarker(t *testing.T) {
	input := "Prefix\nTASK_COMPLETED\nThis is the summary line.\nAnother line."
	result := ExtractSummary(input)
	assert.Contains(t, result, "This is the summary")
}

func TestExtractSummary_NoMarker(t *testing.T) {
	input := "Line 1\nLine 2\nLine 3"
	result := ExtractSummary(input)
	// Should return last 3 lines
	assert.Contains(t, result, "Line 1")
	assert.Contains(t, result, "Line 2")
	assert.Contains(t, result, "Line 3")
}

func TestExtractSummary_EmptyLines(t *testing.T) {
	input := "\n\n\nActual content"
	result := ExtractSummary(input)
	assert.Equal(t, "Actual content", result)
}

func TestExtractSummary_SkipsJSON(t *testing.T) {
	input := "Summary here\n{\"key\": \"value\"}\nMore summary"
	result := ExtractSummary(input)
	assert.NotContains(t, result, "{")
}

func TestExtractSummary_Truncation(t *testing.T) {
	// Create a very long line
	longLine := ""
	for i := 0; i < 50; i++ {
		longLine += "word "
	}

	input := "TASK_COMPLETED\n" + longLine

	result := ExtractSummary(input)
	assert.LessOrEqual(t, len(result), 203) // 200 + "..."
	if len(result) > 200 {
		assert.True(t, result[len(result)-3:] == "...")
	}
}

func TestExtractJSONBlock_Simple(t *testing.T) {
	input := `Some text {"key": "value"} more text`
	result := ExtractJSONBlock(input)
	assert.NotNil(t, result)
	assert.Equal(t, "value", result["key"])
}

func TestExtractJSONBlock_Nested(t *testing.T) {
	input := `Text {"outer": {"inner": 123}} end`
	result := ExtractJSONBlock(input)
	assert.NotNil(t, result)
	inner, ok := result["outer"].(map[string]interface{})
	assert.True(t, ok)
	assert.Equal(t, float64(123), inner["inner"])
}

func TestExtractJSONBlock_NoJSON(t *testing.T) {
	input := "No JSON here"
	result := ExtractJSONBlock(input)
	assert.Nil(t, result)
}

func TestExtractJSONBlock_Incomplete(t *testing.T) {
	input := `{"key": "value"`
	result := ExtractJSONBlock(input)
	assert.Nil(t, result)
}

func TestExtractJSONBlock_Invalid(t *testing.T) {
	input := `{invalid json}`
	result := ExtractJSONBlock(input)
	assert.Nil(t, result)
}

func TestExtractJSONBlock_FilesChanged(t *testing.T) {
	input := `{"files_changed": ["a.go", "b.go"]}`
	result := ExtractJSONBlock(input)
	assert.NotNil(t, result)
	files, ok := result["files_changed"].([]interface{})
	assert.True(t, ok)
	assert.Len(t, files, 2)
}

func TestExtractSessionID_JSON(t *testing.T) {
	input := `{"session_id": "abc-123-def", "result": "ok"}`
	result := ExtractSessionID(input)
	assert.Equal(t, "abc-123-def", result)
}

func TestExtractSessionID_Embedded(t *testing.T) {
	input := `Some text "session_id": "xyz-789" more text`
	result := ExtractSessionID(input)
	assert.Equal(t, "xyz-789", result)
}

func TestExtractSessionID_NoSessionID(t *testing.T) {
	input := `{"result": "ok"}`
	result := ExtractSessionID(input)
	assert.Empty(t, result)
}

func TestExtractSessionID_EmptyValue(t *testing.T) {
	input := `{"session_id": "", "result": "ok"}`
	result := ExtractSessionID(input)
	assert.Empty(t, result)
}
