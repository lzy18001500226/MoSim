package vt

import "github.com/mattn/go-runewidth"

// runeWidthCond is configured for terminal use (East Asian Ambiguous = narrow)
var runeWidthCond = func() *runewidth.Condition {
	c := runewidth.NewCondition()
	c.EastAsianWidth = false // Treat ambiguous as narrow (width 1)
	return c
}()

// processChar processes a single character
func (vt *VirtualTerminal) processChar(ch rune) {
	switch ch {
	case '\n':
		vt.newLine()
	case '\r':
		vt.cursorX = 0
	case '\b':
		if vt.cursorX > 0 {
			vt.cursorX--
		}
	case '\t':
		// Move to next tab stop (every 8 columns)
		vt.cursorX = ((vt.cursorX / 8) + 1) * 8
		if vt.cursorX >= vt.cols {
			vt.cursorX = vt.cols - 1
		}
	case '\x1b':
		// Start of escape sequence - handled by stripping later
	default:
		if ch >= ' ' && ch != '\x7f' {
			vt.putChar(ch)
		}
	}
}

// putChar puts a character at the current cursor position
func (vt *VirtualTerminal) putChar(ch rune) {
	// Get character width (1 for normal, 2 for CJK wide chars)
	width := runeWidthCond.RuneWidth(ch)
	if width == 0 {
		width = 1 // Control chars and combining chars treated as width 1
	}

	// Handle line wrap when cursor reaches end of line
	// For wide chars, need to check if there's room for both cells
	if vt.cursorX+width > vt.cols {
		// Mark the next line as wrapped (soft wrap)
		if vt.cursorY+1 < vt.rows {
			vt.isWrapped[vt.cursorY+1] = true
		}
		vt.newLine()
	}

	if vt.cursorY >= 0 && vt.cursorY < vt.rows && vt.cursorX >= 0 && vt.cursorX < vt.cols {
		// Handle overwriting wide characters:
		currentCell := vt.cells[vt.cursorY][vt.cursorX]

		// If we're writing on a placeholder (width 0), clear the previous wide char
		if currentCell.Width == 0 && vt.cursorX > 0 {
			vt.screen[vt.cursorY][vt.cursorX-1] = ' '
			vt.cells[vt.cursorY][vt.cursorX-1] = NewCell(' ')
		}

		// If we're overwriting a wide char (width 2), clear its placeholder
		if currentCell.Width == 2 && vt.cursorX+1 < vt.cols {
			vt.screen[vt.cursorY][vt.cursorX+1] = ' '
			vt.cells[vt.cursorY][vt.cursorX+1] = NewCell(' ')
		}

		// If we're writing a wide char and it will overlap with something
		if width == 2 && vt.cursorX+1 < vt.cols {
			nextCell := vt.cells[vt.cursorY][vt.cursorX+1]
			// If next cell is placeholder of a wide char, clear the wide char before it
			if nextCell.Width == 0 && vt.cursorX > 0 {
				// The wide char is at cursorX (which we're overwriting anyway)
			}
			// If next cell is a wide char, clear it and its placeholder
			if nextCell.Width == 2 {
				vt.screen[vt.cursorY][vt.cursorX+1] = ' '
				vt.cells[vt.cursorY][vt.cursorX+1] = NewCell(' ')
				if vt.cursorX+2 < vt.cols && vt.cells[vt.cursorY][vt.cursorX+2].Width == 0 {
					vt.screen[vt.cursorY][vt.cursorX+2] = ' '
					vt.cells[vt.cursorY][vt.cursorX+2] = NewCell(' ')
				}
			}
		}

		vt.screen[vt.cursorY][vt.cursorX] = ch
		// Update styled cell with full style information
		vt.cells[vt.cursorY][vt.cursorX] = NewFullStyledCell(
			ch,
			vt.currentFg,
			vt.currentBg,
			vt.currentAttrs,
			uint8(width),
			vt.currentUnderlineStyle,
			vt.currentUnderlineColor,
		)
		vt.cursorX++

		// For wide characters (CJK), add placeholder cell
		if width == 2 && vt.cursorX < vt.cols {
			vt.screen[vt.cursorY][vt.cursorX] = 0 // Placeholder
			vt.cells[vt.cursorY][vt.cursorX] = NewFullStyledCell(
				0, // No character
				vt.currentFg,
				vt.currentBg,
				vt.currentAttrs,
				0, // Width 0 = placeholder
				vt.currentUnderlineStyle,
				vt.currentUnderlineColor,
			)
			vt.cursorX++
		}
	} else {
		vt.cursorX++
	}
}

// newLine moves to the next line, scrolling if necessary
func (vt *VirtualTerminal) newLine() {
	vt.cursorX = 0
	vt.cursorY++
	if vt.cursorY >= vt.rows {
		vt.scroll()
		vt.cursorY = vt.rows - 1
	}
}
