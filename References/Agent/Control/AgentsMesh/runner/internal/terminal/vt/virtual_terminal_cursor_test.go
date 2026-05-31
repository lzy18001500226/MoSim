package vt

import (
	"testing"
)

func TestCursorUp(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("Line 1\nLine 2"))
	vt.Feed([]byte("\x1b[1A")) // Cursor up 1
	vt.Feed([]byte("X"))
	display := vt.GetDisplay()
	// Cursor is at col 6 (after "Line 2"), then move up to line 0
	// and write X at that position (col 6)
	expected := "Line 1X\nLine 2"
	if display != expected {
		t.Errorf("expected '%s', got '%s'", expected, display)
	}
}

func TestCursorDown(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("Line 1"))
	vt.Feed([]byte("\x1b[1B")) // Cursor down 1
	vt.Feed([]byte("X"))
	display := vt.GetDisplay()
	expected := "Line 1\n      X"
	if display != expected {
		t.Errorf("expected '%s', got '%s'", expected, display)
	}
}

func TestCursorForward(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("AB"))
	vt.Feed([]byte("\x1b[3C")) // Cursor forward 3
	vt.Feed([]byte("X"))
	display := vt.GetDisplay()
	expected := "AB   X"
	if display != expected {
		t.Errorf("expected '%s', got '%s'", expected, display)
	}
}

func TestCursorBack(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("ABCD"))
	vt.Feed([]byte("\x1b[2D")) // Cursor back 2
	vt.Feed([]byte("XY"))
	display := vt.GetDisplay()
	if display != "ABXY" {
		t.Errorf("expected 'ABXY', got '%s'", display)
	}
}

func TestCursorPosition(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("ABC\nDEF\nGHI"))
	vt.Feed([]byte("\x1b[2;2H")) // Row 2, Col 2
	vt.Feed([]byte("X"))
	display := vt.GetDisplay()
	expected := "ABC\nDXF\nGHI"
	if display != expected {
		t.Errorf("expected '%s', got '%s'", expected, display)
	}
}

func TestSaveCursorRestore(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("AB"))
	vt.Feed([]byte("\x1b[s")) // Save cursor
	vt.Feed([]byte("CD"))
	vt.Feed([]byte("\x1b[u")) // Restore cursor
	vt.Feed([]byte("XY"))
	display := vt.GetDisplay()
	if display != "ABXY" {
		t.Errorf("expected 'ABXY', got '%s'", display)
	}
}

func TestCursorPosition_Method(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("ABC\nDEF"))
	row, col := vt.CursorPosition()
	if row != 1 || col != 3 {
		t.Errorf("expected cursor at (1, 3), got (%d, %d)", row, col)
	}
}

func TestDecSaveCursorRestore(t *testing.T) {
	vt := NewVirtualTerminal(80, 24, 1000)
	vt.Feed([]byte("AB"))
	vt.Feed([]byte("\x1b7")) // DEC Save cursor
	vt.Feed([]byte("CD"))
	vt.Feed([]byte("\x1b8")) // DEC Restore cursor
	vt.Feed([]byte("XY"))
	display := vt.GetDisplay()
	if display != "ABXY" {
		t.Errorf("expected 'ABXY', got '%s'", display)
	}
}
