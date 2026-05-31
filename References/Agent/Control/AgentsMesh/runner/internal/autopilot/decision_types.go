// Package autopilot implements the AutopilotController for supervised Pod automation.
package autopilot

// DecisionType represents the type of decision made by Control.
type DecisionType string

const (
	DecisionCompleted     DecisionType = "TASK_COMPLETED"
	DecisionContinue      DecisionType = "CONTINUE"
	DecisionNeedHumanHelp DecisionType = "NEED_HUMAN_HELP"
	DecisionGiveUp        DecisionType = "GIVE_UP"
)

// ControlDecision represents the decision made by the control process.
type ControlDecision struct {
	Type         DecisionType // Decision type
	Summary      string       // Decision summary/reason
	Reasoning    string       // Detailed reasoning for the decision
	Confidence   float64      // Confidence level (0-1)
	FilesChanged []string     // List of changed files (for CONTINUE)

	// Progress tracking
	Progress *DecisionProgress // Progress information

	// Action taken
	Action *DecisionAction // Action taken in this iteration

	// Help request (when Type is NEED_HUMAN_HELP)
	HelpRequest *HelpRequestInfo // Detailed help request info
}

// DecisionProgress represents task progress information.
type DecisionProgress struct {
	Summary        string   // Brief progress summary
	CompletedSteps []string // Completed steps
	RemainingSteps []string // Remaining steps
	Percent        int      // Estimated progress percentage (0-100)
}

// DecisionAction represents the action taken in this iteration.
type DecisionAction struct {
	Type    string // observe, send_input, wait, none
	Content string // Action content/description
	Reason  string // Why this action was taken
}

// HelpRequestInfo contains detailed information for help requests.
type HelpRequestInfo struct {
	Reason          string           // Why help is needed
	Context         string           // Context information
	TerminalExcerpt string           // Relevant terminal output
	Suggestions     []HelpSuggestion // Suggested actions
}

// HelpSuggestion represents a suggested action for help request.
type HelpSuggestion struct {
	Action string // approve, skip, custom, etc.
	Label  string // Display label
}

// StructuredDecisionOutput represents the structured JSON output format from Control Agent.
type StructuredDecisionOutput struct {
	Decision struct {
		Type       string  `json:"type"`       // completed, continue, need_help, give_up
		Confidence float64 `json:"confidence"` // 0-1
		Reasoning  string  `json:"reasoning"`  // Detailed reasoning
	} `json:"decision"`
	Progress struct {
		Summary        string   `json:"summary"`
		CompletedSteps []string `json:"completed"`
		RemainingSteps []string `json:"remaining"`
		Percent        int      `json:"percent,omitempty"`
	} `json:"progress,omitempty"`
	Action struct {
		Type    string `json:"type"`    // observe, send_input, wait, none
		Content string `json:"content"` // Action content
		Reason  string `json:"reason"`  // Why this action
	} `json:"action,omitempty"`
	HelpRequest *struct {
		Reason          string `json:"reason"`
		Context         string `json:"context"`
		TerminalExcerpt string `json:"terminal_excerpt,omitempty"`
		Suggestions     []struct {
			Action string `json:"action"`
			Label  string `json:"label"`
		} `json:"suggestions,omitempty"`
	} `json:"help_request,omitempty"`
	FilesChanged []string `json:"files_changed,omitempty"`
}
