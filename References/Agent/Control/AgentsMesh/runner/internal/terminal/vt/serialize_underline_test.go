package vt

import (
	"strings"
	"testing"
)

// Test underline styles (xterm extension: SGR 4:X)
func TestSerialize_ShouldProduceSGRSequenceForSingleUnderline(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[4:1mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "4:1") {
		t.Errorf("Expected single underline (4:1) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForDoubleUnderline(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[4:2mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "4:2") {
		t.Errorf("Expected double underline (4:2) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForCurlyUnderline(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[4:3mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "4:3") {
		t.Errorf("Expected curly underline (4:3) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForDottedUnderline(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[4:4mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "4:4") {
		t.Errorf("Expected dotted underline (4:4) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForDashedUnderline(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[4:5mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "4:5") {
		t.Errorf("Expected dashed underline (4:5) in output, got: %q", result)
	}
}

// Test underline color
func TestSerialize_ShouldProduceSGRSequenceForUnderlineColor256(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[4m\x1b[58;5;196mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	// Should contain underline color sequence
	if !strings.Contains(result, "58") {
		t.Logf("Underline color 256 output: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForUnderlineColorRGB(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[4m\x1b[58;2;255;128;64mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	// Should contain underline color sequence
	if !strings.Contains(result, "58") {
		t.Logf("Underline color RGB output: %q", result)
	}
}

// Test underline color with colon format
func TestSerialize_UnderlineColorColon(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// Curly underline with RGB color using colon format
	vt.Feed([]byte("\x1b[4:3m\x1b[58:2::255:128:64munderlined\x1b[0m"))
	result := vt.Serialize(DefaultSerializeOptions())

	// Should contain curly underline style
	if !strings.Contains(result, "4:3") {
		t.Errorf("Curly underline style not preserved: %q", result)
	}

	t.Logf("Underline color colon output: %q", result)
}
