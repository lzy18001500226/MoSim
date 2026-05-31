// Package tools provides MCP tools for collaboration and pod management.
package tools

import (
	"context"
	"encoding/json"
	"fmt"
)

// Tool represents a tool that can be invoked.
type Tool struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	InputSchema map[string]interface{} `json:"inputSchema"`
	Handler     ToolHandler            `json:"-"`
}

// ToolHandler is a function that handles tool invocations.
type ToolHandler func(ctx context.Context, args map[string]interface{}) (interface{}, error)

// ToolResult represents the result of a tool invocation.
type ToolResult struct {
	Content []ContentBlock `json:"content"`
	IsError bool           `json:"isError,omitempty"`
}

// ContentBlock represents a content block in the tool result.
type ContentBlock struct {
	Type string `json:"type"`
	Text string `json:"text,omitempty"`
}

// NewTextResult creates a text result.
func NewTextResult(text string) *ToolResult {
	return &ToolResult{
		Content: []ContentBlock{{Type: "text", Text: text}},
	}
}

// NewErrorResult creates an error result.
func NewErrorResult(err error) *ToolResult {
	return &ToolResult{
		Content: []ContentBlock{{Type: "text", Text: err.Error()}},
		IsError: true,
	}
}

// ToolRegistry manages tool registration and lookup.
type ToolRegistry struct {
	tools map[string]*Tool
}

// NewToolRegistry creates a new tool registry.
func NewToolRegistry() *ToolRegistry {
	return &ToolRegistry{
		tools: make(map[string]*Tool),
	}
}

// Register adds a tool to the registry.
func (r *ToolRegistry) Register(tool *Tool) {
	r.tools[tool.Name] = tool
}

// Get retrieves a tool by name.
func (r *ToolRegistry) Get(name string) (*Tool, bool) {
	tool, ok := r.tools[name]
	return tool, ok
}

// List returns all registered tools.
func (r *ToolRegistry) List() []*Tool {
	tools := make([]*Tool, 0, len(r.tools))
	for _, tool := range r.tools {
		tools = append(tools, tool)
	}
	return tools
}

// Invoke invokes a tool by name with arguments.
func (r *ToolRegistry) Invoke(ctx context.Context, name string, args map[string]interface{}) (*ToolResult, error) {
	tool, ok := r.tools[name]
	if !ok {
		return nil, fmt.Errorf("tool not found: %s", name)
	}

	result, err := tool.Handler(ctx, args)
	if err != nil {
		return NewErrorResult(err), nil
	}

	if tr, ok := result.(*ToolResult); ok {
		return tr, nil
	}

	// Convert other results to JSON text
	data, err := json.Marshal(result)
	if err != nil {
		return NewErrorResult(err), nil
	}

	return NewTextResult(string(data)), nil
}
