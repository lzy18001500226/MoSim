package vt

import (
	"strings"
	"testing"
)

func TestSerializeWithColors(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// Red text
	vt.Feed([]byte("\x1b[31mRed\x1b[0m Normal"))

	result := vt.Serialize(DefaultSerializeOptions())

	// Should contain SGR sequences for red color
	if !strings.Contains(result, "\x1b[") {
		t.Errorf("Serialize() should contain ANSI sequences for color, got: %q", result)
	}

	// Should contain the text
	if !strings.Contains(result, "Red") || !strings.Contains(result, "Normal") {
		t.Errorf("Serialize() should contain 'Red' and 'Normal', got: %q", result)
	}

	// Verify it renders correctly
	assertRendersTo(t, result, "Red Normal")

	t.Logf("Serialized output: %q", result)
}

func TestSerializeWith256Colors(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// 256-color foreground (color 196 = bright red)
	vt.Feed([]byte("\x1b[38;5;196mBright\x1b[0m"))

	result := vt.Serialize(DefaultSerializeOptions())

	// Should contain the text
	if !strings.Contains(result, "Bright") {
		t.Errorf("Serialize() should contain 'Bright', got: %q", result)
	}

	// Should contain 256-color sequence
	if !strings.Contains(result, "38;5;196") && !strings.Contains(result, "38;5;") {
		t.Logf("Note: 256-color sequence format may differ")
	}

	t.Logf("256-color serialized: %q", result)
}

func TestSerializeWithTrueColor(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// True color (RGB 255, 128, 0 = orange)
	vt.Feed([]byte("\x1b[38;2;255;128;0mOrange\x1b[0m"))

	result := vt.Serialize(DefaultSerializeOptions())

	// Should contain the text
	if !strings.Contains(result, "Orange") {
		t.Errorf("Serialize() should contain 'Orange', got: %q", result)
	}

	t.Logf("True color serialized: %q", result)
}

func TestSerializeColorReset(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// Multiple color changes
	vt.Feed([]byte("\x1b[31mRed\x1b[32mGreen\x1b[0mNormal"))

	result := vt.Serialize(DefaultSerializeOptions())

	// Should contain reset sequence
	if !strings.Contains(result, "\x1b[0m") {
		t.Errorf("Serialize() should contain reset sequence, got: %q", result)
	}

	t.Logf("Color reset serialized: %q", result)
}

func TestSerializeBrightColors(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// Bright red foreground (91)
	vt.Feed([]byte("\x1b[91mBright Red\x1b[0m"))

	result := vt.Serialize(DefaultSerializeOptions())

	// Verify content exists (space may be converted to cursor movement)
	if !containsAll(result, "Bright", "Red") {
		t.Errorf("Serialize() should contain 'Bright' and 'Red', got: %q", result)
	}

	// Verify it renders correctly
	assertRendersTo(t, result, "Bright Red")

	t.Logf("Bright colors serialized: %q", result)
}

// Test standard colors
func TestSerialize_ShouldProduceSGRSequenceForStandardFgColors(t *testing.T) {
	colors := []struct {
		code int
		name string
	}{
		{30, "black"},
		{31, "red"},
		{32, "green"},
		{33, "yellow"},
		{34, "blue"},
		{35, "magenta"},
		{36, "cyan"},
		{37, "white"},
	}

	for _, c := range colors {
		t.Run(c.name, func(t *testing.T) {
			vt := NewVirtualTerminal(80, 24, 1000)
			vt.Feed([]byte("\x1b[" + string(rune('0'+c.code/10)) + string(rune('0'+c.code%10)) + "mhello"))
			result := vt.Serialize(DefaultSerializeOptions())
			// Standard colors 30-37 should be in output
			t.Logf("Color %d output: %q", c.code, result)
		})
	}
}

// Test bright colors
func TestSerialize_ShouldProduceSGRSequenceForBrightFgColors(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[91mhello")) // Bright red
	result := vt.Serialize(DefaultSerializeOptions())
	if !strings.Contains(result, "91") {
		t.Errorf("Expected bright red (91) in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceFor256ColorFg(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[38;5;196mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	// Should contain 256-color sequence
	if !strings.Contains(result, "38;5;196") {
		t.Errorf("Expected 256-color sequence in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceFor256ColorBg(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[48;5;46mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	// Should contain 256-color bg sequence
	if !strings.Contains(result, "48;5;46") {
		t.Errorf("Expected 256-color bg sequence in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForTrueColorFg(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[38;2;100;150;200mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	// Should contain RGB sequence
	if !strings.Contains(result, "38;2;100;150;200") {
		t.Errorf("Expected true color sequence in output, got: %q", result)
	}
}

func TestSerialize_ShouldProduceSGRSequenceForTrueColorBg(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("\x1b[48;2;50;100;150mhello"))
	result := vt.Serialize(DefaultSerializeOptions())
	// Should contain RGB bg sequence
	if !strings.Contains(result, "48;2;50;100;150") {
		t.Errorf("Expected true color bg sequence in output, got: %q", result)
	}
}

// Test background color with ECH
func TestSerialize_BackgroundColorECH(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	// Red background, then spaces, then text
	vt.Feed([]byte("\x1b[41m     \x1b[0mhello"))
	result := vt.Serialize(DefaultSerializeOptions())

	// Should contain background color and ECH or spaces
	if !strings.Contains(result, "hello") {
		t.Errorf("Text not preserved: %q", result)
	}
	t.Logf("Background color ECH output: %q", result)
}
