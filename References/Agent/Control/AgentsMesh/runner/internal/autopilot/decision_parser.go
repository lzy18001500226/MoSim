package autopilot

import (
	"encoding/json"
)

// DecisionParser parses Control Process output to extract decisions.
type DecisionParser struct{}

// NewDecisionParser creates a new DecisionParser instance.
func NewDecisionParser() *DecisionParser {
	return &DecisionParser{}
}

// ParseDecision extracts a ControlDecision from the control process output.
// First tries to parse structured JSON output, then falls back to keyword-based parsing.
// For JSON output (from --output-format json), extracts the "result" field first.
func (dp *DecisionParser) ParseDecision(output string) *ControlDecision {
	// Try to extract result from JSON output (Claude Code --output-format json)
	textContent := ExtractResultFromJSON(output)
	if textContent == "" {
		textContent = output // Fallback to raw output
	}

	// Try structured JSON parsing first
	if decision := dp.parseStructuredDecision(textContent); decision != nil {
		return decision
	}

	// Fallback to keyword-based parsing
	return dp.parseKeywordDecision(textContent, output)
}

// parseStructuredDecision attempts to parse structured JSON decision output.
func (dp *DecisionParser) parseStructuredDecision(content string) *ControlDecision {
	// Try to extract a JSON block from the content
	jsonData := ExtractJSONBlock(content)
	if jsonData == nil {
		return nil
	}

	// Check if this looks like a structured decision
	decisionField, hasDecision := jsonData["decision"]
	if !hasDecision {
		return nil
	}

	// Re-parse with proper struct
	jsonStr := extractJSONString(content)
	if jsonStr == "" {
		return nil
	}

	var structured StructuredDecisionOutput
	if err := json.Unmarshal([]byte(jsonStr), &structured); err != nil {
		return nil
	}

	// Convert to ControlDecision
	decision := &ControlDecision{
		Type:       mapDecisionType(structured.Decision.Type),
		Reasoning:  structured.Decision.Reasoning,
		Confidence: structured.Decision.Confidence,
	}

	// Map decision type to decisionField to ensure proper handling
	_ = decisionField

	// Set summary from reasoning or first line
	if structured.Decision.Reasoning != "" {
		decision.Summary = truncateSummary(structured.Decision.Reasoning, 200)
	}

	// Set progress
	if structured.Progress.Summary != "" || len(structured.Progress.CompletedSteps) > 0 {
		decision.Progress = &DecisionProgress{
			Summary:        structured.Progress.Summary,
			CompletedSteps: structured.Progress.CompletedSteps,
			RemainingSteps: structured.Progress.RemainingSteps,
			Percent:        structured.Progress.Percent,
		}
	}

	// Set action
	if structured.Action.Type != "" {
		decision.Action = &DecisionAction{
			Type:    structured.Action.Type,
			Content: structured.Action.Content,
			Reason:  structured.Action.Reason,
		}
	}

	// Set help request
	if structured.HelpRequest != nil {
		decision.HelpRequest = &HelpRequestInfo{
			Reason:          structured.HelpRequest.Reason,
			Context:         structured.HelpRequest.Context,
			TerminalExcerpt: structured.HelpRequest.TerminalExcerpt,
		}
		for _, s := range structured.HelpRequest.Suggestions {
			decision.HelpRequest.Suggestions = append(decision.HelpRequest.Suggestions, HelpSuggestion{
				Action: s.Action,
				Label:  s.Label,
			})
		}
	}

	// Set files changed
	decision.FilesChanged = structured.FilesChanged

	return decision
}

// parseKeywordDecision uses keyword-based parsing (legacy fallback).
func (dp *DecisionParser) parseKeywordDecision(textContent, originalOutput string) *ControlDecision {
	decision := &ControlDecision{
		Type:    DecisionContinue, // Default
		Summary: ExtractSummary(textContent),
	}

	// Check for decision markers at the start of lines
	decisionType := FindDecisionMarker(textContent)
	if decisionType != "" {
		decision.Type = decisionType
	}

	// Try to parse any JSON blocks that might contain structured data
	if jsonData := ExtractJSONBlock(originalOutput); jsonData != nil {
		if files, ok := jsonData["files_changed"].([]interface{}); ok {
			for _, f := range files {
				if s, ok := f.(string); ok {
					decision.FilesChanged = append(decision.FilesChanged, s)
				}
			}
		}
	}

	return decision
}
