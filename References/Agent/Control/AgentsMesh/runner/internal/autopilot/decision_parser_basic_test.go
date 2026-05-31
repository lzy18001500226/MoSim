package autopilot

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Tests for basic decision parsing

func TestDecisionParser_NewDecisionParser(t *testing.T) {
	dp := NewDecisionParser()
	assert.NotNil(t, dp)
}

func TestDecisionParser_ParseDecision_AllTypes(t *testing.T) {
	dp := NewDecisionParser()

	tests := []struct {
		name         string
		input        string
		expectedType DecisionType
	}{
		{
			name:         "TASK_COMPLETED",
			input:        "Analysis done.\nTASK_COMPLETED\nAll tasks finished.",
			expectedType: DecisionCompleted,
		},
		{
			name:         "CONTINUE",
			input:        "Making progress.\nCONTINUE\nMoving to next step.",
			expectedType: DecisionContinue,
		},
		{
			name:         "NEED_HUMAN_HELP",
			input:        "Encountered issue.\nNEED_HUMAN_HELP\nNeed credentials.",
			expectedType: DecisionNeedHumanHelp,
		},
		{
			name:         "GIVE_UP",
			input:        "Cannot proceed.\nGIVE_UP\nTask impossible.",
			expectedType: DecisionGiveUp,
		},
		{
			name:         "No marker defaults to CONTINUE",
			input:        "Just some text without any marker.",
			expectedType: DecisionContinue,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			decision := dp.ParseDecision(tt.input)
			assert.Equal(t, tt.expectedType, decision.Type)
		})
	}
}

func TestDecisionParser_ParseDecision_WithFilesChanged(t *testing.T) {
	dp := NewDecisionParser()

	input := `Task done.
TASK_COMPLETED
{"files_changed": ["main.go", "utils.go", "test.go"]}
Summary here.`

	decision := dp.ParseDecision(input)

	assert.Equal(t, DecisionCompleted, decision.Type)
	assert.Len(t, decision.FilesChanged, 3)
	assert.Contains(t, decision.FilesChanged, "main.go")
	assert.Contains(t, decision.FilesChanged, "utils.go")
	assert.Contains(t, decision.FilesChanged, "test.go")
}

func TestDecisionParser_ParseDecision_JSONOutput(t *testing.T) {
	dp := NewDecisionParser()

	// Claude Code JSON output format
	input := `{"result": "Analysis done.\nTASK_COMPLETED\nAll finished.", "session_id": "abc-123"}`

	decision := dp.ParseDecision(input)

	assert.Equal(t, DecisionCompleted, decision.Type)
}

func TestDecisionType_String(t *testing.T) {
	assert.Equal(t, "TASK_COMPLETED", string(DecisionCompleted))
	assert.Equal(t, "CONTINUE", string(DecisionContinue))
	assert.Equal(t, "NEED_HUMAN_HELP", string(DecisionNeedHumanHelp))
	assert.Equal(t, "GIVE_UP", string(DecisionGiveUp))
}

func TestDecisionParser_FallbackToKeyword(t *testing.T) {
	dp := NewDecisionParser()

	// Non-structured output should fall back to keyword parsing
	input := `观察终端输出后，任务已完成。
TASK_COMPLETED
所有功能已实现并测试通过。`

	decision := dp.ParseDecision(input)

	assert.Equal(t, DecisionCompleted, decision.Type)
	assert.Contains(t, decision.Summary, "所有功能已实现")
}

func TestMapDecisionType(t *testing.T) {
	tests := []struct {
		input    string
		expected DecisionType
	}{
		{"completed", DecisionCompleted},
		{"COMPLETED", DecisionCompleted},
		{"task_completed", DecisionCompleted},
		{"continue", DecisionContinue},
		{"CONTINUE", DecisionContinue},
		{"need_help", DecisionNeedHumanHelp},
		{"NEED_HUMAN_HELP", DecisionNeedHumanHelp},
		{"give_up", DecisionGiveUp},
		{"giveup", DecisionGiveUp},
		{"unknown", DecisionContinue}, // Default
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			result := mapDecisionType(tt.input)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestTruncateSummary(t *testing.T) {
	short := "Short text"
	assert.Equal(t, short, truncateSummary(short, 200))

	long := ""
	for i := 0; i < 50; i++ {
		long += "word "
	}
	result := truncateSummary(long, 50)
	assert.Equal(t, 53, len(result)) // 50 + "..."
	assert.True(t, result[len(result)-3:] == "...")
}
