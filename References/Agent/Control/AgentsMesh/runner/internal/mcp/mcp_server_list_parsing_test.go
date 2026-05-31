package mcp

import (
	"encoding/json"
	"testing"
)

// Tests for Initialize, tools/list, resources/list response parsing

func TestInitializeResponseParsing(t *testing.T) {
	jsonStr := `{
		"protocolVersion": "2024-11-05",
		"capabilities": {
			"tools": {"listChanged": true},
			"resources": {"subscribe": true, "listChanged": true}
		},
		"serverInfo": {
			"name": "Test Server",
			"version": "1.0.0"
		}
	}`

	var result struct {
		ProtocolVersion string `json:"protocolVersion"`
		Capabilities    struct {
			Tools struct {
				ListChanged bool `json:"listChanged"`
			} `json:"tools"`
			Resources struct {
				Subscribe   bool `json:"subscribe"`
				ListChanged bool `json:"listChanged"`
			} `json:"resources"`
		} `json:"capabilities"`
		ServerInfo struct {
			Name    string `json:"name"`
			Version string `json:"version"`
		} `json:"serverInfo"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		t.Fatalf("failed to unmarshal: %v", err)
	}

	if result.ProtocolVersion != "2024-11-05" {
		t.Errorf("protocolVersion: got %v, want '2024-11-05'", result.ProtocolVersion)
	}

	if !result.Capabilities.Tools.ListChanged {
		t.Error("tools.listChanged should be true")
	}

	if result.ServerInfo.Name != "Test Server" {
		t.Errorf("serverInfo.name: got %v, want 'Test Server'", result.ServerInfo.Name)
	}
}

func TestToolsListResponseParsing(t *testing.T) {
	jsonStr := `{
		"tools": [
			{
				"name": "read_file",
				"description": "Read a file from disk",
				"inputSchema": {"type": "object"}
			},
			{
				"name": "write_file",
				"description": "Write a file to disk",
				"inputSchema": {"type": "object"}
			}
		]
	}`

	var result struct {
		Tools []Tool `json:"tools"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		t.Fatalf("failed to unmarshal: %v", err)
	}

	if len(result.Tools) != 2 {
		t.Errorf("tools count: got %v, want 2", len(result.Tools))
	}

	if result.Tools[0].Name != "read_file" {
		t.Errorf("tool name: got %v, want 'read_file'", result.Tools[0].Name)
	}
}

func TestResourcesListResponseParsing(t *testing.T) {
	jsonStr := `{
		"resources": [
			{
				"uri": "file:///home/user/docs",
				"name": "Documents",
				"description": "User documents",
				"mimeType": "inode/directory"
			}
		]
	}`

	var result struct {
		Resources []Resource `json:"resources"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		t.Fatalf("failed to unmarshal: %v", err)
	}

	if len(result.Resources) != 1 {
		t.Errorf("resources count: got %v, want 1", len(result.Resources))
	}

	if result.Resources[0].URI != "file:///home/user/docs" {
		t.Errorf("resource uri: got %v, want 'file:///home/user/docs'", result.Resources[0].URI)
	}
}
