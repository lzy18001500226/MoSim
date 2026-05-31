package mcp

import (
	"encoding/json"
	"testing"
)

// Tests for ReadResource result parsing

func TestReadResourceResultParsing(t *testing.T) {
	jsonStr := `{
		"contents": [
			{
				"uri": "file:///test.txt",
				"mimeType": "text/plain",
				"text": "Hello, World!"
			}
		]
	}`

	var result struct {
		Contents []struct {
			URI      string `json:"uri"`
			MimeType string `json:"mimeType,omitempty"`
			Text     string `json:"text,omitempty"`
			Blob     string `json:"blob,omitempty"`
		} `json:"contents"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		t.Fatalf("failed to unmarshal: %v", err)
	}

	if len(result.Contents) != 1 {
		t.Errorf("contents count: got %v, want 1", len(result.Contents))
	}

	if result.Contents[0].Text != "Hello, World!" {
		t.Errorf("text: got %v, want 'Hello, World!'", result.Contents[0].Text)
	}
}

func TestReadResourceResultParsingBlob(t *testing.T) {
	jsonStr := `{
		"contents": [
			{
				"uri": "file:///test.bin",
				"mimeType": "application/octet-stream",
				"blob": "SGVsbG8="
			}
		]
	}`

	var result struct {
		Contents []struct {
			URI      string `json:"uri"`
			MimeType string `json:"mimeType,omitempty"`
			Text     string `json:"text,omitempty"`
			Blob     string `json:"blob,omitempty"`
		} `json:"contents"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		t.Fatalf("failed to unmarshal: %v", err)
	}

	if result.Contents[0].Blob != "SGVsbG8=" {
		t.Errorf("blob: got %v, want 'SGVsbG8='", result.Contents[0].Blob)
	}
}

func TestReadResourceEmptyContents(t *testing.T) {
	jsonStr := `{"contents": []}`

	var result struct {
		Contents []struct {
			URI      string `json:"uri"`
			MimeType string `json:"mimeType,omitempty"`
			Text     string `json:"text,omitempty"`
		} `json:"contents"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		t.Fatalf("failed to unmarshal: %v", err)
	}

	if len(result.Contents) != 0 {
		t.Errorf("contents should be empty, got %v", len(result.Contents))
	}
}

func TestCallToolResultParsing(t *testing.T) {
	jsonStr := `{
		"content": [
			{
				"type": "text",
				"text": "Result text"
			}
		],
		"isError": false
	}`

	var result struct {
		Content []struct {
			Type string          `json:"type"`
			Text string          `json:"text,omitempty"`
			Data json.RawMessage `json:"data,omitempty"`
		} `json:"content"`
		IsError bool `json:"isError"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		t.Fatalf("failed to unmarshal: %v", err)
	}

	if result.IsError {
		t.Error("isError should be false")
	}

	if len(result.Content) != 1 {
		t.Errorf("content count: got %v, want 1", len(result.Content))
	}

	if result.Content[0].Text != "Result text" {
		t.Errorf("text: got %v, want 'Result text'", result.Content[0].Text)
	}
}

func TestCallToolResultIsError(t *testing.T) {
	jsonStr := `{
		"content": [
			{
				"type": "text",
				"text": "Error message"
			}
		],
		"isError": true
	}`

	var result struct {
		Content []struct {
			Type string `json:"type"`
			Text string `json:"text,omitempty"`
		} `json:"content"`
		IsError bool `json:"isError"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		t.Fatalf("failed to unmarshal: %v", err)
	}

	if !result.IsError {
		t.Error("isError should be true")
	}
}
