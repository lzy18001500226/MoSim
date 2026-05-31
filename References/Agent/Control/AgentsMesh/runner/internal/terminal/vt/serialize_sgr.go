package vt

import "fmt"

// equalFlags compares cell flags for equality
func equalFlags(cell, oldCell Cell) bool {
	if cell.Attrs != oldCell.Attrs {
		return false
	}
	// If underline is set, also check underline style and color
	if cell.Attrs.Has(AttrUnderline) {
		if cell.UnderlineStyle != oldCell.UnderlineStyle {
			return false
		}
		if !cell.UnderlineColor.Equals(oldCell.UnderlineColor) {
			return false
		}
	}
	return true
}

// buildFgColorSGR builds SGR parameters for foreground color
func buildFgColorSGR(c Color) []string {
	if c.IsDefault() {
		return []string{"39"}
	}
	if c.IsPalette() {
		idx := c.Index()
		if idx < 8 {
			return []string{fmt.Sprintf("%d", 30+idx)}
		} else if idx < 16 {
			return []string{fmt.Sprintf("%d", 90+idx-8)}
		}
		return []string{"38", "5", fmt.Sprintf("%d", idx)}
	}
	if c.IsRGB() {
		r, g, b := c.RGB()
		return []string{"38", "2", fmt.Sprintf("%d", r), fmt.Sprintf("%d", g), fmt.Sprintf("%d", b)}
	}
	return nil
}

// buildBgColorSGR builds SGR parameters for background color
func buildBgColorSGR(c Color) []string {
	if c.IsDefault() {
		return []string{"49"}
	}
	if c.IsPalette() {
		idx := c.Index()
		if idx < 8 {
			return []string{fmt.Sprintf("%d", 40+idx)}
		} else if idx < 16 {
			return []string{fmt.Sprintf("%d", 100+idx-8)}
		}
		return []string{"48", "5", fmt.Sprintf("%d", idx)}
	}
	if c.IsRGB() {
		r, g, b := c.RGB()
		return []string{"48", "2", fmt.Sprintf("%d", r), fmt.Sprintf("%d", g), fmt.Sprintf("%d", b)}
	}
	return nil
}

// buildFlagsSGR builds SGR parameters for text attribute changes
func buildFlagsSGR(cell, oldCell Cell) []string {
	var sgrSeq []string

	// Inverse
	if cell.Attrs.Has(AttrInverse) != oldCell.Attrs.Has(AttrInverse) {
		if cell.Attrs.Has(AttrInverse) {
			sgrSeq = append(sgrSeq, "7")
		} else {
			sgrSeq = append(sgrSeq, "27")
		}
	}

	// Bold
	if cell.Attrs.Has(AttrBold) != oldCell.Attrs.Has(AttrBold) {
		if cell.Attrs.Has(AttrBold) {
			sgrSeq = append(sgrSeq, "1")
		} else {
			sgrSeq = append(sgrSeq, "22")
		}
	}

	// Underline (with style support)
	underlineChanged := false
	if cell.Attrs.Has(AttrUnderline) != oldCell.Attrs.Has(AttrUnderline) {
		underlineChanged = true
	} else if cell.Attrs.Has(AttrUnderline) && oldCell.Attrs.Has(AttrUnderline) {
		if cell.UnderlineStyle != oldCell.UnderlineStyle ||
			!cell.UnderlineColor.Equals(oldCell.UnderlineColor) {
			underlineChanged = true
		}
	}

	if underlineChanged {
		if !cell.Attrs.Has(AttrUnderline) {
			sgrSeq = append(sgrSeq, "24")
		} else {
			style := cell.UnderlineStyle
			if style == UnderlineNone {
				style = UnderlineSingle
			}
			sgrSeq = append(sgrSeq, fmt.Sprintf("4:%d", style))

			if !cell.UnderlineColor.IsDefault() {
				if cell.UnderlineColor.IsRGB() {
					r, g, b := cell.UnderlineColor.RGB()
					sgrSeq = append(sgrSeq, fmt.Sprintf("58:2::%d:%d:%d", r, g, b))
				} else if cell.UnderlineColor.IsPalette() {
					sgrSeq = append(sgrSeq, fmt.Sprintf("58:5:%d", cell.UnderlineColor.Index()))
				}
			}
		}
	}

	// Overline
	if cell.Attrs.Has(AttrOverline) != oldCell.Attrs.Has(AttrOverline) {
		if cell.Attrs.Has(AttrOverline) {
			sgrSeq = append(sgrSeq, "53")
		} else {
			sgrSeq = append(sgrSeq, "55")
		}
	}

	// Blink
	if cell.Attrs.Has(AttrBlink) != oldCell.Attrs.Has(AttrBlink) {
		if cell.Attrs.Has(AttrBlink) {
			sgrSeq = append(sgrSeq, "5")
		} else {
			sgrSeq = append(sgrSeq, "25")
		}
	}

	// Invisible
	if cell.Attrs.Has(AttrInvisible) != oldCell.Attrs.Has(AttrInvisible) {
		if cell.Attrs.Has(AttrInvisible) {
			sgrSeq = append(sgrSeq, "8")
		} else {
			sgrSeq = append(sgrSeq, "28")
		}
	}

	// Italic
	if cell.Attrs.Has(AttrItalic) != oldCell.Attrs.Has(AttrItalic) {
		if cell.Attrs.Has(AttrItalic) {
			sgrSeq = append(sgrSeq, "3")
		} else {
			sgrSeq = append(sgrSeq, "23")
		}
	}

	// Dim
	if cell.Attrs.Has(AttrDim) != oldCell.Attrs.Has(AttrDim) {
		if cell.Attrs.Has(AttrDim) {
			sgrSeq = append(sgrSeq, "2")
		} else {
			sgrSeq = append(sgrSeq, "22")
		}
	}

	// Strikethrough
	if cell.Attrs.Has(AttrStrikethrough) != oldCell.Attrs.Has(AttrStrikethrough) {
		if cell.Attrs.Has(AttrStrikethrough) {
			sgrSeq = append(sgrSeq, "9")
		} else {
			sgrSeq = append(sgrSeq, "29")
		}
	}

	return sgrSeq
}
