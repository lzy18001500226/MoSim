package autopilot

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// createMCPConfigFile creates an MCP configuration file for the Control Agent.
// This allows the Control Agent to use MCP tools directly instead of curl.
// Returns the path to the created config file, or empty string on error.
func createMCPConfigFile(workDir, podKey string, mcpPort int) (string, error) {
	// Create .mcp.json in the working directory
	configPath := filepath.Join(workDir, ".mcp.json")

	// MCP config structure for Claude Code
	// Using HTTP transport to connect to our local MCP server
	config := map[string]interface{}{
		"mcpServers": map[string]interface{}{
			"autopilot-control": map[string]interface{}{
				"type": "http",
				"url":  fmt.Sprintf("http://127.0.0.1:%d/mcp", mcpPort),
				"headers": map[string]string{
					"Content-Type": "application/json",
					"X-Pod-Key":    podKey,
				},
			},
		},
	}

	// Write config file
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return "", err
	}

	if err := os.WriteFile(configPath, data, 0644); err != nil {
		return "", err
	}

	return configPath, nil
}
