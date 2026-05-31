package vt

import "strings"

// handleSGR handles SGR (Select Graphic Rendition) sequences
// Supports standard SGR parameters and colon-separated sub-parameters for:
// - Underline styles: 4:0 (none), 4:1 (single), 4:2 (double), 4:3 (curly), 4:4 (dotted), 4:5 (dashed)
// - Underline color: 58;5;n (palette) or 58;2;r;g;b (RGB)
// - Overline: 53 (on), 55 (off)
func (vt *VirtualTerminal) handleSGR() {
	// Parse raw sequence for colon-separated parameters
	rawSeq := string(vt.escRawSeq)
	if len(rawSeq) > 0 && rawSeq[len(rawSeq)-1] == 'm' {
		rawSeq = rawSeq[:len(rawSeq)-1]
	}

	// If no params, treat as reset
	if rawSeq == "" || rawSeq == "0" {
		vt.resetStyle()
		return
	}

	// Split by semicolon to get parameter groups
	parts := strings.Split(rawSeq, ";")

	i := 0
	for i < len(parts) {
		part := parts[i]

		// Check for colon-separated sub-parameters (e.g., "4:3" for curly underline)
		if strings.Contains(part, ":") {
			i = vt.handleSGRWithSubParams(parts, i, part)
			continue
		}

		// Standard parameter (no colon)
		i = vt.handleSGRStandard(parts, i, parseIntOrZero(part))
	}
}

// resetStyle resets all style attributes to default
func (vt *VirtualTerminal) resetStyle() {
	vt.currentFg = DefaultColor()
	vt.currentBg = DefaultColor()
	vt.currentAttrs = AttrNone
	vt.currentUnderlineStyle = UnderlineNone
	vt.currentUnderlineColor = DefaultColor()
}

// handleSGRWithSubParams handles colon-separated SGR parameters
func (vt *VirtualTerminal) handleSGRWithSubParams(parts []string, i int, part string) int {
	subParts := strings.Split(part, ":")
	mainParam := parseIntOrZero(subParts[0])

	switch mainParam {
	case 4: // Underline with style
		vt.handleUnderlineStyle(subParts)
	case 58: // Underline color with colon format
		vt.handleUnderlineColorColon(subParts)
	}
	return i + 1
}

// handleUnderlineStyle handles SGR 4:X underline style
func (vt *VirtualTerminal) handleUnderlineStyle(subParts []string) {
	if len(subParts) > 1 {
		style := parseIntOrZero(subParts[1])
		switch style {
		case 0:
			vt.currentAttrs &^= AttrUnderline
			vt.currentUnderlineStyle = UnderlineNone
		case 1:
			vt.currentAttrs |= AttrUnderline
			vt.currentUnderlineStyle = UnderlineSingle
		case 2:
			vt.currentAttrs |= AttrUnderline
			vt.currentUnderlineStyle = UnderlineDouble
		case 3:
			vt.currentAttrs |= AttrUnderline
			vt.currentUnderlineStyle = UnderlineCurly
		case 4:
			vt.currentAttrs |= AttrUnderline
			vt.currentUnderlineStyle = UnderlineDotted
		case 5:
			vt.currentAttrs |= AttrUnderline
			vt.currentUnderlineStyle = UnderlineDashed
		}
	} else {
		vt.currentAttrs |= AttrUnderline
		vt.currentUnderlineStyle = UnderlineSingle
	}
}

// handleUnderlineColorColon handles SGR 58:5:n or 58:2::r:g:b
func (vt *VirtualTerminal) handleUnderlineColorColon(subParts []string) {
	if len(subParts) >= 3 && subParts[1] == "5" {
		// Palette color: 58:5:n
		idx := parseIntOrZero(subParts[2])
		vt.currentUnderlineColor = PaletteColor(uint8(idx))
	} else if len(subParts) >= 5 && subParts[1] == "2" {
		// RGB color: 58:2::r:g:b (note: empty element after 2)
		startIdx := 2
		if subParts[2] == "" {
			startIdx = 3 // Skip empty colorspace element
		}
		if len(subParts) >= startIdx+3 {
			r := parseIntOrZero(subParts[startIdx])
			g := parseIntOrZero(subParts[startIdx+1])
			b := parseIntOrZero(subParts[startIdx+2])
			vt.currentUnderlineColor = RGBColor(uint8(r), uint8(g), uint8(b))
		}
	}
}

// handleSGRStandard handles standard SGR parameters
func (vt *VirtualTerminal) handleSGRStandard(parts []string, i int, p int) int {
	switch p {
	case 0:
		vt.resetStyle()
	case 1:
		vt.currentAttrs |= AttrBold
	case 2:
		vt.currentAttrs |= AttrDim
	case 3:
		vt.currentAttrs |= AttrItalic
	case 4:
		vt.currentAttrs |= AttrUnderline
		vt.currentUnderlineStyle = UnderlineSingle
	case 5:
		vt.currentAttrs |= AttrBlink
	case 7:
		vt.currentAttrs |= AttrInverse
	case 8:
		vt.currentAttrs |= AttrInvisible
	case 9:
		vt.currentAttrs |= AttrStrikethrough
	case 21:
		vt.currentAttrs |= AttrUnderline
		vt.currentUnderlineStyle = UnderlineDouble
	case 22:
		vt.currentAttrs &^= AttrBold | AttrDim
	case 23:
		vt.currentAttrs &^= AttrItalic
	case 24:
		vt.currentAttrs &^= AttrUnderline
		vt.currentUnderlineStyle = UnderlineNone
	case 25:
		vt.currentAttrs &^= AttrBlink
	case 27:
		vt.currentAttrs &^= AttrInverse
	case 28:
		vt.currentAttrs &^= AttrInvisible
	case 29:
		vt.currentAttrs &^= AttrStrikethrough
	case 30, 31, 32, 33, 34, 35, 36, 37:
		vt.currentFg = PaletteColor(uint8(p - 30))
	case 38:
		return vt.parseExtendedColorFromParts(parts, i, true)
	case 39:
		vt.currentFg = DefaultColor()
	case 40, 41, 42, 43, 44, 45, 46, 47:
		vt.currentBg = PaletteColor(uint8(p - 40))
	case 48:
		return vt.parseExtendedColorFromParts(parts, i, false)
	case 49:
		vt.currentBg = DefaultColor()
	case 53:
		vt.currentAttrs |= AttrOverline
	case 55:
		vt.currentAttrs &^= AttrOverline
	case 58:
		return vt.parseUnderlineColorFromParts(parts, i)
	case 59:
		vt.currentUnderlineColor = DefaultColor()
	case 90, 91, 92, 93, 94, 95, 96, 97:
		vt.currentFg = PaletteColor(uint8(p - 90 + 8))
	case 100, 101, 102, 103, 104, 105, 106, 107:
		vt.currentBg = PaletteColor(uint8(p - 100 + 8))
	}
	return i + 1
}

// parseIntOrZero parses string as int, returns 0 on error
func parseIntOrZero(s string) int {
	var result int
	for _, c := range s {
		if c >= '0' && c <= '9' {
			result = result*10 + int(c-'0')
		}
	}
	return result
}

// parseExtendedColorFromParts parses 256-color or true color sequences from parts
func (vt *VirtualTerminal) parseExtendedColorFromParts(parts []string, i int, isForeground bool) int {
	if i+1 >= len(parts) {
		return i + 1
	}

	mode := parseIntOrZero(parts[i+1])
	switch mode {
	case 5: // 256-color mode: 38;5;n
		if i+2 < len(parts) {
			idx := parseIntOrZero(parts[i+2])
			if isForeground {
				vt.currentFg = PaletteColor(uint8(idx))
			} else {
				vt.currentBg = PaletteColor(uint8(idx))
			}
			return i + 3
		}
	case 2: // True color (RGB): 38;2;r;g;b
		if i+4 < len(parts) {
			r := parseIntOrZero(parts[i+2])
			g := parseIntOrZero(parts[i+3])
			b := parseIntOrZero(parts[i+4])
			if isForeground {
				vt.currentFg = RGBColor(uint8(r), uint8(g), uint8(b))
			} else {
				vt.currentBg = RGBColor(uint8(r), uint8(g), uint8(b))
			}
			return i + 5
		}
	}
	return i + 2
}

// parseUnderlineColorFromParts parses underline color from semicolon-separated parts
// Format: 58;5;n or 58;2;r;g;b
func (vt *VirtualTerminal) parseUnderlineColorFromParts(parts []string, i int) int {
	if i+1 >= len(parts) {
		return i + 1
	}

	mode := parseIntOrZero(parts[i+1])
	switch mode {
	case 5: // 256-color mode: 58;5;n
		if i+2 < len(parts) {
			idx := parseIntOrZero(parts[i+2])
			vt.currentUnderlineColor = PaletteColor(uint8(idx))
			return i + 3
		}
	case 2: // True color (RGB): 58;2;r;g;b
		if i+4 < len(parts) {
			r := parseIntOrZero(parts[i+2])
			g := parseIntOrZero(parts[i+3])
			b := parseIntOrZero(parts[i+4])
			vt.currentUnderlineColor = RGBColor(uint8(r), uint8(g), uint8(b))
			return i + 5
		}
	}
	return i + 2
}
