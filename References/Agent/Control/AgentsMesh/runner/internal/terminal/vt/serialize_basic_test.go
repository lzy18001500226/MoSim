package vt

import (
	"strings"
	"testing"
)

// Helper: check if serialized output renders to expected text when parsed
func assertRendersTo(t *testing.T, serialized, expectedText string) {
	t.Helper()
	// Create a fresh VT, feed the serialized output, and compare display
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte(serialized))
	got := vt.GetDisplay()
	if got != expectedText {
		t.Errorf("Serialized output renders to %q, want %q\nSerialized: %q", got, expectedText, serialized)
	}
}

// Helper: check if string contains all substrings
func containsAll(s string, substrings ...string) bool {
	for _, sub := range substrings {
		if !strings.Contains(s, sub) {
			return false
		}
	}
	return true
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func TestSerializeBasicText(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("Hello, World!"))

	result := vt.Serialize(DefaultSerializeOptions())

	// xterm.js uses cursor movement optimization for spaces
	// So "Hello, World!" may become "Hello,\x1b[1CWorld!"
	// We verify by re-parsing that it renders correctly
	assertRendersTo(t, result, "Hello, World!")
}

func TestSerializeMultipleLines(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("Line 1\nLine 2\nLine 3"))

	result := vt.Serialize(DefaultSerializeOptions())

	// Should contain all lines (text content)
	if !containsAll(result, "Line", "1", "2", "3") {
		t.Errorf("Serialize() should contain line content, got: %q", result)
	}

	// Should have line separators
	if !strings.Contains(result, "\r\n") {
		t.Errorf("Serialize() should contain line separators, got: %q", result)
	}

	// Verify it renders correctly
	assertRendersTo(t, result, "Line 1\nLine 2\nLine 3")
}

func TestSerializeWithHistory(t *testing.T) {
	vt := NewVirtualTerminal(80, 5, 100)
	// Feed enough lines to push some to history
	for i := 1; i <= 10; i++ {
		vt.Feed([]byte("Line " + string(rune('0'+i)) + "\n"))
	}

	opts := DefaultSerializeOptions()
	opts.ScrollbackLines = 5
	result := vt.Serialize(opts)

	// Should contain recent history and screen content
	if result == "" {
		t.Error("Serialize() should not be empty with history")
	}

	t.Logf("History serialized (truncated): %q", result[:min(len(result), 200)])
}

func TestSerializeCursorPosition(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("Hello"))
	// Move cursor to position (1, 3) = row 1, col 3
	vt.Feed([]byte("\x1b[1;3H"))

	result := vt.Serialize(DefaultSerializeOptions())

	// Should contain "Hello"
	if !strings.Contains(result, "Hello") {
		t.Errorf("Serialize() should contain 'Hello', got: %q", result)
	}

	// Should end with a cursor position sequence (CUP or cursor movement)
	if !strings.Contains(result, "\x1b[") {
		t.Errorf("Serialize() should contain cursor position sequence, got: %q", result)
	}

	t.Logf("Cursor position serialized: %q", result)
}

func TestSerializeEmpty(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// No data fed

	result := vt.Serialize(DefaultSerializeOptions())

	if result != "" {
		t.Errorf("Serialize() should be empty for terminal with no data, got: %q", result)
	}
}

func TestSerializeSimple(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[31mRed\x1b[0m Normal"))

	result := vt.SerializeSimple(100)

	// SerializeSimple should contain plain text
	if !strings.Contains(result, "Red") || !strings.Contains(result, "Normal") {
		t.Errorf("SerializeSimple() should contain 'Red' and 'Normal', got: %q", result)
	}
}

func TestSerializeUTF8(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("你好世界 🚀"))

	result := vt.Serialize(DefaultSerializeOptions())

	if !strings.Contains(result, "你好世界") || !strings.Contains(result, "🚀") {
		t.Errorf("Serialize() should preserve UTF-8 characters, got: %q", result)
	}
}

func TestSerializeBoxDrawing(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("┌─────┐\n│ Box │\n└─────┘"))

	result := vt.Serialize(DefaultSerializeOptions())

	if !containsAll(result, "┌─────┐", "└─────┘") {
		t.Errorf("Serialize() should preserve box drawing characters, got: %q", result)
	}
}

// Test round-trip: serialize then parse should produce same visual output
func TestSerialize_RoundTrip(t *testing.T) {
	testCases := []struct {
		name  string
		input string
	}{
		{"plain text", "Hello, World!"},
		{"colored text", "\x1b[31mRed\x1b[0m and \x1b[32mGreen\x1b[0m"},
		{"bold italic", "\x1b[1mBold\x1b[0m \x1b[3mItalic\x1b[0m"},
		{"256 color", "\x1b[38;5;196mRed\x1b[0m"},
		{"true color", "\x1b[38;2;255;128;0mOrange\x1b[0m"},
		{"multi line", "Line1\r\nLine2\r\nLine3"},
		{"CJK", "你好世界"},
		{"mixed", "\x1b[1;31mBold Red\x1b[0m Normal"},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Parse original
			vt1 := NewVirtualTerminal(80, 24, 1000)
			vt1.Feed([]byte(tc.input))
			original := vt1.GetDisplay()

			// Serialize
			serialized := vt1.Serialize(DefaultSerializeOptions())

			// Parse serialized
			vt2 := NewVirtualTerminal(80, 24, 1000)
			vt2.Feed([]byte(serialized))
			roundTripped := vt2.GetDisplay()

			// Compare visual output
			if original != roundTripped {
				t.Errorf("Round-trip failed:\nOriginal:     %q\nSerialized:   %q\nRound-trip:   %q",
					original, serialized, roundTripped)
			}
		})
	}
}
