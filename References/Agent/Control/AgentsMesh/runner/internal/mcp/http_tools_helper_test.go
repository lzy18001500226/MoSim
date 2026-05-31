package mcp

import (
	"testing"
)

// TestHTTPToolsCoverage provides additional tests for http_tools.go functions

func TestGetStringArgEmpty(t *testing.T) {
	args := map[string]interface{}{
		"empty": "",
	}
	result := getStringArg(args, "empty")
	if result != "" {
		t.Errorf("expected empty string, got %v", result)
	}
}

func TestGetStringArgNonString(t *testing.T) {
	args := map[string]interface{}{
		"number": 42,
	}
	result := getStringArg(args, "number")
	if result != "" {
		t.Errorf("expected empty string for non-string, got %v", result)
	}
}

func TestGetIntArgFloat(t *testing.T) {
	args := map[string]interface{}{
		"float": 42.5,
	}
	result := getIntArg(args, "float")
	if result != 42 {
		t.Errorf("expected 42 for float64, got %v", result)
	}
}

func TestGetIntPtrArgFloat(t *testing.T) {
	args := map[string]interface{}{
		"float": 42.5,
	}
	result := getIntPtrArg(args, "float")
	if result == nil {
		t.Error("expected non-nil result")
	} else if *result != 42 {
		t.Errorf("expected 42, got %v", *result)
	}
}

func TestGetBoolArgNonBool(t *testing.T) {
	args := map[string]interface{}{
		"string": "true",
	}
	result := getBoolArg(args, "string")
	if result {
		t.Error("expected false for non-bool")
	}
}

func TestGetStringSliceArgInvalidItems(t *testing.T) {
	args := map[string]interface{}{
		"mixed": []interface{}{"a", 123, "b"},
	}
	result := getStringSliceArg(args, "mixed")
	// Should only include string items
	if len(result) != 2 {
		t.Errorf("expected 2 strings, got %v", len(result))
	}
}

func TestGetStringSliceArgNonSlice(t *testing.T) {
	args := map[string]interface{}{
		"string": "not a slice",
	}
	result := getStringSliceArg(args, "string")
	if result != nil {
		t.Errorf("expected nil for non-slice, got %v", result)
	}
}

func TestGetMapArg(t *testing.T) {
	args := map[string]interface{}{
		"config": map[string]interface{}{
			"key1": "value1",
			"key2": 123,
		},
	}
	result := getMapArg(args, "config")
	if result == nil {
		t.Error("expected non-nil result")
	}
	if result["key1"] != "value1" {
		t.Errorf("expected key1=value1, got %v", result["key1"])
	}
	if result["key2"] != 123 {
		t.Errorf("expected key2=123, got %v", result["key2"])
	}
}

func TestGetMapArgNonMap(t *testing.T) {
	args := map[string]interface{}{
		"string": "not a map",
	}
	result := getMapArg(args, "string")
	if result != nil {
		t.Errorf("expected nil for non-map, got %v", result)
	}
}

func TestGetMapArgMissing(t *testing.T) {
	args := map[string]interface{}{}
	result := getMapArg(args, "missing")
	if result != nil {
		t.Errorf("expected nil for missing key, got %v", result)
	}
}

func TestGetMapArgEmptyMap(t *testing.T) {
	args := map[string]interface{}{
		"empty": map[string]interface{}{},
	}
	result := getMapArg(args, "empty")
	if result == nil {
		t.Error("expected non-nil result for empty map")
	}
	if len(result) != 0 {
		t.Errorf("expected empty map, got %v", result)
	}
}

// Tests for getInt64PtrArg edge cases
func TestGetInt64PtrArgFloat(t *testing.T) {
	args := map[string]interface{}{
		"float": float64(42.5),
	}
	result := getInt64PtrArg(args, "float")
	if result == nil {
		t.Error("expected non-nil result")
	} else if *result != 42 {
		t.Errorf("expected 42, got %v", *result)
	}
}

func TestGetInt64PtrArgInt(t *testing.T) {
	args := map[string]interface{}{
		"int": int(42),
	}
	result := getInt64PtrArg(args, "int")
	if result == nil {
		t.Error("expected non-nil result")
	} else if *result != 42 {
		t.Errorf("expected 42, got %v", *result)
	}
}

func TestGetInt64PtrArgMissing(t *testing.T) {
	args := map[string]interface{}{}
	result := getInt64PtrArg(args, "missing")
	if result != nil {
		t.Errorf("expected nil for missing key, got %v", result)
	}
}

func TestGetInt64PtrArgString(t *testing.T) {
	args := map[string]interface{}{
		"string": "42",
	}
	result := getInt64PtrArg(args, "string")
	if result != nil {
		t.Errorf("expected nil for string type, got %v", result)
	}
}

func TestGetIntArgMissing(t *testing.T) {
	args := map[string]interface{}{}
	result := getIntArg(args, "missing")
	if result != 0 {
		t.Errorf("expected 0 for missing key, got %v", result)
	}
}

func TestGetIntPtrArgMissing(t *testing.T) {
	args := map[string]interface{}{}
	result := getIntPtrArg(args, "missing")
	if result != nil {
		t.Errorf("expected nil for missing key, got %v", result)
	}
}

func TestGetIntPtrArgString(t *testing.T) {
	args := map[string]interface{}{
		"string": "42",
	}
	result := getIntPtrArg(args, "string")
	if result != nil {
		t.Errorf("expected nil for string type, got %v", result)
	}
}
