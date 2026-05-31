package vt

// processCSI processes a CSI (Control Sequence Introducer) byte
func (vt *VirtualTerminal) processCSI(b byte) {
	// Collect raw sequence for SGR parsing
	vt.escRawSeq = append(vt.escRawSeq, b)

	switch {
	case b >= '0' && b <= '9':
		// Digit - build parameter
		if len(vt.escParams) == 0 {
			vt.escParams = []int{0}
		}
		vt.escParams[len(vt.escParams)-1] = vt.escParams[len(vt.escParams)-1]*10 + int(b-'0')

	case b == ';':
		// Parameter separator
		vt.escParams = append(vt.escParams, 0)

	case b == ':':
		// Subparameter separator (e.g., for SGR 4:3 underline style)
		// Handled in handleSGR by parsing escRawSeq

	case b == '?':
		// Private mode indicator
		vt.escPrivate = b

	case b >= 0x40 && b <= 0x7e:
		// Final byte - execute command
		vt.executeCSI(b)
		vt.escState = stateNormal

	default:
		// Intermediate byte or unknown
		vt.escBuffer = append(vt.escBuffer, b)
	}
}

// executeCSI executes a CSI command
func (vt *VirtualTerminal) executeCSI(cmd byte) {
	// Default parameter value helper
	param := func(idx, def int) int {
		if idx < len(vt.escParams) && vt.escParams[idx] > 0 {
			return vt.escParams[idx]
		}
		return def
	}

	switch cmd {
	case 'A': // CUU - Cursor Up
		n := param(0, 1)
		vt.cursorY -= n
		if vt.cursorY < 0 {
			vt.cursorY = 0
		}

	case 'B': // CUD - Cursor Down
		n := param(0, 1)
		vt.cursorY += n
		if vt.cursorY >= vt.rows {
			vt.cursorY = vt.rows - 1
		}

	case 'C': // CUF - Cursor Forward (Right)
		n := param(0, 1)
		vt.cursorX += n
		if vt.cursorX >= vt.cols {
			vt.cursorX = vt.cols - 1
		}

	case 'D': // CUB - Cursor Back (Left)
		n := param(0, 1)
		vt.cursorX -= n
		if vt.cursorX < 0 {
			vt.cursorX = 0
		}

	case 'E': // CNL - Cursor Next Line
		n := param(0, 1)
		vt.cursorX = 0
		vt.cursorY += n
		if vt.cursorY >= vt.rows {
			vt.cursorY = vt.rows - 1
		}

	case 'F': // CPL - Cursor Previous Line
		n := param(0, 1)
		vt.cursorX = 0
		vt.cursorY -= n
		if vt.cursorY < 0 {
			vt.cursorY = 0
		}

	case 'G': // CHA - Cursor Horizontal Absolute
		col := param(0, 1)
		vt.cursorX = col - 1
		if vt.cursorX < 0 {
			vt.cursorX = 0
		}
		if vt.cursorX >= vt.cols {
			vt.cursorX = vt.cols - 1
		}

	case 'H', 'f': // CUP/HVP - Cursor Position
		row := param(0, 1)
		col := 1
		if len(vt.escParams) > 1 {
			col = param(1, 1)
		}
		vt.cursorY = row - 1
		vt.cursorX = col - 1
		vt.clampCursor()

	case 'J': // ED - Erase in Display
		vt.eraseInDisplay(param(0, 0))

	case 'K': // EL - Erase in Line
		vt.eraseInLine(param(0, 0))

	case 'L': // IL - Insert Lines
		vt.insertLines(param(0, 1))

	case 'M': // DL - Delete Lines
		vt.deleteLines(param(0, 1))

	case 'P': // DCH - Delete Characters
		vt.deleteChars(param(0, 1))

	case '@': // ICH - Insert Characters
		vt.insertChars(param(0, 1))

	case 'X': // ECH - Erase Characters
		n := param(0, 1)
		for i := 0; i < n && vt.cursorX+i < vt.cols; i++ {
			vt.screen[vt.cursorY][vt.cursorX+i] = ' '
			vt.cells[vt.cursorY][vt.cursorX+i] = NewCell(' ')
		}

	case 'S': // SU - Scroll Up
		n := param(0, 1)
		for i := 0; i < n; i++ {
			vt.scroll()
		}

	case 'T': // SD - Scroll Down
		n := param(0, 1)
		for i := 0; i < n; i++ {
			vt.scrollDown()
		}

	case 's': // SCP - Save Cursor Position
		vt.savedCursorX = vt.cursorX
		vt.savedCursorY = vt.cursorY

	case 'u': // RCP - Restore Cursor Position
		vt.cursorX = vt.savedCursorX
		vt.cursorY = vt.savedCursorY

	case 'h': // SM - Set Mode
		if vt.escPrivate == '?' {
			vt.handlePrivateMode(true)
		}

	case 'l': // RM - Reset Mode
		if vt.escPrivate == '?' {
			vt.handlePrivateMode(false)
		}

	case 'm': // SGR - Select Graphic Rendition
		vt.handleSGR()

	case 'r': // DECSTBM - Set Top and Bottom Margins
		// Ignore scrolling region for simplified implementation

	case 'c': // DA - Device Attributes
		// Ignore device attribute request

	case 'n': // DSR - Device Status Report
		// Ignore status report request
	}
}

// clampCursor ensures cursor is within screen bounds
func (vt *VirtualTerminal) clampCursor() {
	if vt.cursorY < 0 {
		vt.cursorY = 0
	}
	if vt.cursorY >= vt.rows {
		vt.cursorY = vt.rows - 1
	}
	if vt.cursorX < 0 {
		vt.cursorX = 0
	}
	if vt.cursorX >= vt.cols {
		vt.cursorX = vt.cols - 1
	}
}

// eraseInDisplay handles ED command
func (vt *VirtualTerminal) eraseInDisplay(n int) {
	switch n {
	case 0: // Erase from cursor to end of screen
		vt.clearLine(vt.cursorY, vt.cursorX, vt.cols)
		for i := vt.cursorY + 1; i < vt.rows; i++ {
			vt.clearLine(i, 0, vt.cols)
		}
	case 1: // Erase from start to cursor
		for i := 0; i < vt.cursorY; i++ {
			vt.clearLine(i, 0, vt.cols)
		}
		vt.clearLine(vt.cursorY, 0, vt.cursorX+1)
	case 2, 3: // Erase entire screen
		for i := 0; i < vt.rows; i++ {
			vt.clearLine(i, 0, vt.cols)
		}
	}
}

// eraseInLine handles EL command
func (vt *VirtualTerminal) eraseInLine(n int) {
	switch n {
	case 0: // Erase from cursor to end of line
		vt.clearLine(vt.cursorY, vt.cursorX, vt.cols)
	case 1: // Erase from start of line to cursor
		vt.clearLine(vt.cursorY, 0, vt.cursorX+1)
	case 2: // Erase entire line
		vt.clearLine(vt.cursorY, 0, vt.cols)
	}
}

// handlePrivateMode handles DEC private mode sequences
func (vt *VirtualTerminal) handlePrivateMode(set bool) {
	for _, p := range vt.escParams {
		switch p {
		case 1049, 47: // Alternative screen buffer
			if set {
				vt.enterAltScreen()
			} else {
				vt.exitAltScreen()
			}
		case 25: // DECTCEM - Show/hide cursor (ignore for text-only)
		case 1: // DECCKM - Application cursor keys (ignore)
		case 7: // DECAWM - Auto-wrap mode (we always wrap)
		case 12: // Start blinking cursor (ignore)
		case 2004: // Bracketed paste mode (ignore)
		}
	}
}
