package vt

import (
	"bytes"
	"regexp"
	"strings"
)

// ANSI escape sequence pattern (for simple stripping)
var ansiPattern = regexp.MustCompile(`\x1b\[[?>=]?[0-9;]*[a-zA-Z]|\x1b\][^\x07]*\x07|\x1b[PX^_][^\x1b]*\x1b\\`)

// GetDisplay returns the current screen content
func (vt *VirtualTerminal) GetDisplay() string {
	vt.mu.RLock()
	defer vt.mu.RUnlock()

	if !vt.hasData {
		return ""
	}

	var lines []string
	for rowIdx, row := range vt.screen {
		var lineBuilder strings.Builder
		for colIdx, ch := range row {
			// Skip placeholder cells (width 0 after wide chars)
			if vt.cells[rowIdx][colIdx].Width == 0 {
				continue
			}
			lineBuilder.WriteRune(ch)
		}
		line := strings.TrimRight(lineBuilder.String(), " ")
		lines = append(lines, line)
	}

	// Remove trailing empty lines
	for len(lines) > 0 && lines[len(lines)-1] == "" {
		lines = lines[:len(lines)-1]
	}

	return strings.Join(lines, "\n")
}

// GetOutput returns recent terminal output (history + current screen)
func (vt *VirtualTerminal) GetOutput(lines int) string {
	vt.mu.RLock()
	defer vt.mu.RUnlock()

	if !vt.hasData {
		return ""
	}

	var result []string
	result = append(result, vt.history...)

	for rowIdx, row := range vt.screen {
		var lineBuilder strings.Builder
		for colIdx, ch := range row {
			// Skip placeholder cells (width 0 after wide chars)
			if vt.cells[rowIdx][colIdx].Width == 0 {
				continue
			}
			lineBuilder.WriteRune(ch)
		}
		line := strings.TrimRight(lineBuilder.String(), " ")
		if line != "" {
			result = append(result, line)
		}
	}

	if len(result) > lines {
		result = result[len(result)-lines:]
	}

	return strings.Join(result, "\n")
}

// GetScreenSnapshot returns a snapshot of the current screen
func (vt *VirtualTerminal) GetScreenSnapshot() string {
	return vt.GetDisplay()
}

// Clear clears the terminal and history
func (vt *VirtualTerminal) Clear() {
	vt.mu.Lock()
	defer vt.mu.Unlock()

	vt.initScreen()
	vt.history = make([]string, 0)
	vt.historyStyled = make([][]Cell, 0)
	vt.historyIsWrapped = make([]bool, 0)
	vt.hasData = false
}

// SetOnFirstData sets a callback to be called when VT receives first PTY data.
// The callback is called in a goroutine to avoid blocking PTY reading.
// This is useful for triggering actions like sending a terminal snapshot to relay
// after the VT has accumulated its initial content.
func (vt *VirtualTerminal) SetOnFirstData(callback func()) {
	vt.onFirstDataMu.Lock()
	defer vt.onFirstDataMu.Unlock()
	vt.onFirstData = callback
}

// SetOSCHandler sets a callback to be called when OSC sequences are detected.
// The callback is called synchronously during Feed() processing.
// Supported OSC types:
//   - OSC 777: Desktop notification (iTerm2/Kitty format: "notify;title;body")
//   - OSC 9: Desktop notification (ConEmu/Windows Terminal format: "message")
//   - OSC 0/2: Window/tab title
func (vt *VirtualTerminal) SetOSCHandler(handler OSCHandler) {
	vt.mu.Lock()
	defer vt.mu.Unlock()
	vt.oscHandler = handler
}

// CursorPosition returns the current cursor position
func (vt *VirtualTerminal) CursorPosition() (row, col int) {
	vt.mu.RLock()
	defer vt.mu.RUnlock()
	return vt.cursorY, vt.cursorX
}

// Cols returns the terminal width
func (vt *VirtualTerminal) Cols() int {
	vt.mu.RLock()
	defer vt.mu.RUnlock()
	return vt.cols
}

// Rows returns the terminal height
func (vt *VirtualTerminal) Rows() int {
	vt.mu.RLock()
	defer vt.mu.RUnlock()
	return vt.rows
}

// IsAltScreen returns true if the terminal is currently using alternate screen buffer
// (typically used by TUI applications like Claude Code, vim, less, etc.)
func (vt *VirtualTerminal) IsAltScreen() bool {
	vt.mu.RLock()
	defer vt.mu.RUnlock()
	return vt.useAltScreen
}

// IsEmpty returns true if the terminal has no content (no history and screen is blank)
func (vt *VirtualTerminal) IsEmpty() bool {
	vt.mu.RLock()
	defer vt.mu.RUnlock()

	// Check if there's any history
	if len(vt.history) > 0 {
		return false
	}

	// Check if any cell on the screen has content
	// vt.screen stores runes directly, not Cell structs
	for y := 0; y < vt.rows; y++ {
		for x := 0; x < vt.cols; x++ {
			ch := vt.screen[y][x]
			if ch != 0 && ch != ' ' {
				return false
			}
		}
	}
	return true
}

// StripANSI removes ANSI escape sequences from text
func StripANSI(text string) string {
	return ansiPattern.ReplaceAllString(text, "")
}

// StripANSIBytes removes ANSI escape sequences from bytes
func StripANSIBytes(data []byte) []byte {
	return bytes.ReplaceAll(
		bytes.ReplaceAll(data, []byte("\x1b["), []byte("")),
		[]byte("\x1b"), []byte(""),
	)
}

// GetCellsRow returns a copy of the cells for a given row
// Used by serializer to access styled cell data
func (vt *VirtualTerminal) GetCellsRow(row int) []Cell {
	vt.mu.RLock()
	defer vt.mu.RUnlock()
	return vt.getCellsRowNoLock(row)
}

// getCellsRowNoLock returns a copy of the cells for a given row without locking (caller must hold lock)
func (vt *VirtualTerminal) getCellsRowNoLock(row int) []Cell {
	if row < 0 || row >= len(vt.cells) {
		return nil
	}
	result := make([]Cell, len(vt.cells[row]))
	copy(result, vt.cells[row])
	return result
}

// IsLineWrapped returns true if the given line is wrapped from the previous line
func (vt *VirtualTerminal) IsLineWrapped(row int) bool {
	vt.mu.RLock()
	defer vt.mu.RUnlock()
	return vt.isLineWrappedNoLock(row)
}

// isLineWrappedNoLock returns true if the given line is wrapped without locking (caller must hold lock)
func (vt *VirtualTerminal) isLineWrappedNoLock(row int) bool {
	if row < 0 || row >= len(vt.isWrapped) {
		return false
	}
	return vt.isWrapped[row]
}

// GetCurrentStyle returns the current text style (used for cursor style serialization)
func (vt *VirtualTerminal) GetCurrentStyle() (fg, bg Color, attrs CellAttrs, ulStyle UnderlineStyle, ulColor Color) {
	vt.mu.RLock()
	defer vt.mu.RUnlock()
	return vt.currentFg, vt.currentBg, vt.currentAttrs, vt.currentUnderlineStyle, vt.currentUnderlineColor
}

// getCurrentStyleNoLock returns the current text style without locking (caller must hold lock)
func (vt *VirtualTerminal) getCurrentStyleNoLock() (fg, bg Color, attrs CellAttrs, ulStyle UnderlineStyle, ulColor Color) {
	return vt.currentFg, vt.currentBg, vt.currentAttrs, vt.currentUnderlineStyle, vt.currentUnderlineColor
}

// GetHistoryStyledRow returns a copy of styled history cells for a given history index
// Index is relative to history start (0 = oldest history line)
func (vt *VirtualTerminal) GetHistoryStyledRow(index int) []Cell {
	vt.mu.RLock()
	defer vt.mu.RUnlock()

	if index < 0 || index >= len(vt.historyStyled) {
		return nil
	}
	result := make([]Cell, len(vt.historyStyled[index]))
	copy(result, vt.historyStyled[index])
	return result
}

// GetHistoryStyledLength returns the number of styled history lines
func (vt *VirtualTerminal) GetHistoryStyledLength() int {
	vt.mu.RLock()
	defer vt.mu.RUnlock()
	return len(vt.historyStyled)
}

// IsHistoryLineWrapped returns true if the given history line was wrapped
func (vt *VirtualTerminal) IsHistoryLineWrapped(index int) bool {
	vt.mu.RLock()
	defer vt.mu.RUnlock()

	if index < 0 || index >= len(vt.historyIsWrapped) {
		return false
	}
	return vt.historyIsWrapped[index]
}
