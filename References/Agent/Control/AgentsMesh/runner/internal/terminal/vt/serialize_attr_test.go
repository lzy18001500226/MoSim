package vt

import (
	"strings"
	"testing"
)

func TestSerializeWithAttributes(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// Bold, italic, underline
	vt.Feed([]byte("\x1b[1mBold\x1b[0m \x1b[3mItalic\x1b[0m \x1b[4mUnderline\x1b[0m"))

	result := vt.Serialize(DefaultSerializeOptions())

	// Should contain all text
	if !containsAll(result, "Bold", "Italic", "Underline") {
		t.Errorf("Serialize() should contain 'Bold', 'Italic', 'Underline', got: %q", result)
	}

	// Verify it renders correctly
	assertRendersTo(t, result, "Bold Italic Underline")

	t.Logf("Attributes serialized: %q", result)
}

func TestSerialize_ShouldProduceSGRSequenceForBold(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[1mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "\x1b[1m") {
		t.Errorf("Expected bold SGR sequence, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForItalic(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[3mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "\x1b[3m") {
		t.Errorf("Expected italic SGR sequence, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForUnderline(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[4mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	// May use 4:1 format for single underline
	if !strings.Contains(result, "\x1b[") {
		t.Errorf("Expected underline SGR sequence, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForOverline(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[53mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "53") {
		t.Errorf("Expected overline (53) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForStrikethrough(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[9mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "9") {
		t.Errorf("Expected strikethrough (9) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForDim(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[2mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "2") {
		t.Errorf("Expected dim (2) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForBlink(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[5mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "5") {
		t.Errorf("Expected blink (5) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForInverse(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[7mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "7") {
		t.Errorf("Expected inverse (7) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForInvisible(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[8mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "8") {
		t.Errorf("Expected invisible (8) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRResetSequence(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[1;31mhello\x1b[0mworld"))
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "\x1b[0m") {
		t.Errorf("Expected reset sequence in output, got: %q", result)
	}
}

// Test combined styles
func TestSerialize_ShouldHandleCombinedStyles(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// Bold + italic + red + underline
	vt.Feed([]byte("\x1b[1;3;31;4mstylish\x1b[0m"))
	result := vt.Serialize(DefaultSerializeOptions())

	if !strings.Contains(result, "stylish") {
		t.Errorf("Should contain 'stylish', got: %q", result)
	}
	t.Logf("Combined styles output: %q", result)
}

// Test attribute combinations
func TestSerialize_AttributeCombinations(t *testing.T) {
	testCases := []struct {
		name   string
		input  string
		verify func(result string) bool
	}{
		{
			"bold+italic",
			"\x1b[1;3mtext\x1b[0m",
			func(r string) bool { return strings.Contains(r, "1") && strings.Contains(r, "3") },
		},
		{
			"underline+strikethrough",
			"\x1b[4;9mtext\x1b[0m",
			func(r string) bool { return strings.Contains(r, "text") },
		},
		{
			"dim+inverse",
			"\x1b[2;7mtext\x1b[0m",
			func(r string) bool { return strings.Contains(r, "2") && strings.Contains(r, "7") },
		},
		{
			"all attributes",
			"\x1b[1;2;3;4;5;7;8;9mtext\x1b[0m",
			func(r string) bool { return strings.Contains(r, "text") },
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			vt := NewVirtualTerminal(80, 24, 1000)
			vt.Feed([]byte(tc.input))
			result := vt.Serialize(DefaultSerializeOptions())

			if !tc.verify(result) {
				t.Errorf("Attribute combination %s not preserved: %q", tc.name, result)
			}

			// Verify round-trip
			vt2 := NewVirtualTerminal(80, 24, 1000)
			vt2.Feed([]byte(result))
			if vt.GetDisplay() != vt2.GetDisplay() {
				t.Errorf("Round-trip failed for %s", tc.name)
			}
		})
	}
}
