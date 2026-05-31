// Package terminal provides terminal state detection for AI agents.
package detector

import (
	"strings"
)

// PromptDetector detects input prompts in terminal output using generic patterns.
// It doesn't depend on specific Agent implementations, but instead detects
// structural features common to most CLI prompts.
type PromptDetector struct {
	// Configuration
	maxPromptLength int // maximum length of a prompt line
}

// PromptDetectorConfig contains configuration for PromptDetector.
type PromptDetectorConfig struct {
	// MaxPromptLength is the maximum length of a line to consider as a prompt (default: 100)
	MaxPromptLength int
}

// NewPromptDetector creates a new prompt detector.
func NewPromptDetector(cfg PromptDetectorConfig) *PromptDetector {
	if cfg.MaxPromptLength == 0 {
		cfg.MaxPromptLength = 100
	}
	return &PromptDetector{
		maxPromptLength: cfg.MaxPromptLength,
	}
}

// PromptResult contains the result of prompt detection.
type PromptResult struct {
	// IsPrompt indicates if a prompt was detected
	IsPrompt bool
	// Confidence is the detection confidence (0.0-1.0)
	Confidence float64
	// PromptType indicates the type of prompt detected
	PromptType PromptType
	// Line is the detected prompt line
	Line string
	// LineIndex is the index of the prompt line
	LineIndex int
}

// PromptType indicates the type of prompt detected.
type PromptType string

const (
	PromptTypeNone       PromptType = ""
	PromptTypeCommand    PromptType = "command"    // >, $, #, etc.
	PromptTypeConfirm    PromptType = "confirm"    // y/n, yes/no
	PromptTypePermission PromptType = "permission" // allow, approve, permit
	PromptTypeContinue   PromptType = "continue"   // press any key, enter to continue
	PromptTypeInput      PromptType = "input"      // generic input request
)

// DetectPrompt analyzes terminal lines and detects if there's an input prompt.
// It checks the bottom N non-empty lines of the terminal.
func (d *PromptDetector) DetectPrompt(lines []string) PromptResult {
	if len(lines) == 0 {
		return PromptResult{}
	}

	// Collect non-empty lines from bottom to top (for agents using alternate screen mode)
	var nonEmptyLines []struct {
		line  string
		index int
	}
	for i := len(lines) - 1; i >= 0 && len(nonEmptyLines) < 10; i-- {
		trimmed := strings.TrimSpace(lines[i])
		if len(trimmed) > 0 {
			nonEmptyLines = append(nonEmptyLines, struct {
				line  string
				index int
			}{line: lines[i], index: i})
		}
	}

	if len(nonEmptyLines) == 0 {
		return PromptResult{}
	}

	// Check the last few non-empty lines (most likely prompt is among them)
	linesToCheck := 5
	if len(nonEmptyLines) < linesToCheck {
		linesToCheck = len(nonEmptyLines)
	}

	for i := 0; i < linesToCheck; i++ {
		entry := nonEmptyLines[i]
		result := d.analyzeLine(entry.line, entry.index, i == 0) // i==0 means it's the last non-empty line
		if result.IsPrompt {
			return result
		}
	}

	return PromptResult{}
}

// analyzeLine analyzes a single line for prompt patterns.
func (d *PromptDetector) analyzeLine(line string, lineIndex int, isLastLine bool) PromptResult {
	// Trim trailing whitespace but preserve leading (for indentation detection)
	trimmedRight := strings.TrimRight(line, " \t\r\n")
	trimmed := strings.TrimSpace(line)

	// Empty lines are not prompts
	if len(trimmed) == 0 {
		return PromptResult{}
	}

	// Very long lines are unlikely to be prompts
	if len(trimmed) > d.maxPromptLength {
		return PromptResult{}
	}

	var confidence float64
	var promptType PromptType

	// Check for confirmation prompts (y/n, yes/no)
	if d.isConfirmPrompt(trimmed) {
		confidence = 0.9
		promptType = PromptTypeConfirm
	}

	// Check for permission prompts
	if d.isPermissionPrompt(trimmed) {
		confidence = 0.85
		promptType = PromptTypePermission
	}

	// Check for continue prompts
	if d.isContinuePrompt(trimmed) {
		confidence = 0.85
		promptType = PromptTypeContinue
	}

	// Check for keyboard shortcut prompts (e.g., "[Tab] Accept [Esc] Reject")
	if d.isKeyboardShortcutPrompt(trimmed) {
		if confidence == 0 {
			confidence = 0.85
			promptType = PromptTypeInput
		} else {
			confidence += 0.1
		}
	}

	// Check for command prompt symbols at the end
	if d.hasPromptSymbol(trimmedRight) {
		if confidence == 0 {
			confidence = 0.7
			promptType = PromptTypeCommand
		} else {
			confidence += 0.1 // Boost if also has other features
		}
	}

	// Check for generic input indicators
	if d.hasInputIndicator(trimmed) {
		if confidence == 0 {
			confidence = 0.6
			promptType = PromptTypeInput
		} else {
			confidence += 0.1
		}
	}

	// Boost confidence if it's the last line
	if isLastLine && confidence > 0 {
		confidence += 0.1
	}

	// Boost confidence for short lines (prompts are usually short)
	if len(trimmed) < 30 && confidence > 0 {
		confidence += 0.05
	}

	// Cap confidence at 1.0
	if confidence > 1.0 {
		confidence = 1.0
	}

	if confidence >= 0.5 {
		return PromptResult{
			IsPrompt:   true,
			Confidence: confidence,
			PromptType: promptType,
			Line:       line,
			LineIndex:  lineIndex,
		}
	}

	return PromptResult{}
}

// Note: StripANSI is defined in virtual_terminal.go to avoid redeclaration
