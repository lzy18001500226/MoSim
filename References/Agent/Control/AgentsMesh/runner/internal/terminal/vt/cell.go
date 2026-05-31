package vt

// Color represents a terminal color.
// It can be a default color, a 256-color palette index, or a true RGB color.
type Color struct {
	// ColorType: 0=default, 1=palette (256 colors), 2=RGB (true color)
	colorType uint8
	// For palette colors: the color index (0-255)
	// For RGB: packed as index (unused, use r/g/b fields)
	index uint8
	// RGB components (only used when colorType == 2)
	r, g, b uint8
}

// DefaultColor returns the default terminal color
func DefaultColor() Color {
	return Color{colorType: 0}
}

// PaletteColor creates a color from a 256-color palette index
func PaletteColor(index uint8) Color {
	return Color{colorType: 1, index: index}
}

// RGBColor creates a true color from RGB components
func RGBColor(r, g, b uint8) Color {
	return Color{colorType: 2, r: r, g: g, b: b}
}

// IsDefault returns true if this is the default color
func (c Color) IsDefault() bool {
	return c.colorType == 0
}

// IsPalette returns true if this is a palette color
func (c Color) IsPalette() bool {
	return c.colorType == 1
}

// IsRGB returns true if this is a true color
func (c Color) IsRGB() bool {
	return c.colorType == 2
}

// Index returns the palette index (only valid for palette colors)
func (c Color) Index() uint8 {
	return c.index
}

// RGB returns the RGB components (only valid for RGB colors)
func (c Color) RGB() (r, g, b uint8) {
	return c.r, c.g, c.b
}

// Equals compares two colors for equality
func (c Color) Equals(other Color) bool {
	if c.colorType != other.colorType {
		return false
	}
	switch c.colorType {
	case 0:
		return true
	case 1:
		return c.index == other.index
	case 2:
		return c.r == other.r && c.g == other.g && c.b == other.b
	default:
		return false
	}
}

// CellAttrs represents text attributes (bold, italic, etc.)
type CellAttrs uint16

const (
	AttrNone          CellAttrs = 0
	AttrBold          CellAttrs = 1 << 0
	AttrDim           CellAttrs = 1 << 1
	AttrItalic        CellAttrs = 1 << 2
	AttrUnderline     CellAttrs = 1 << 3
	AttrBlink         CellAttrs = 1 << 4
	AttrInverse       CellAttrs = 1 << 5
	AttrInvisible     CellAttrs = 1 << 6
	AttrStrikethrough CellAttrs = 1 << 7
	AttrOverline      CellAttrs = 1 << 8
)

// UnderlineStyle represents different underline styles
// Matches xterm.js UnderlineStyle enum
type UnderlineStyle uint8

const (
	UnderlineNone   UnderlineStyle = 0
	UnderlineSingle UnderlineStyle = 1
	UnderlineDouble UnderlineStyle = 2
	UnderlineCurly  UnderlineStyle = 3
	UnderlineDotted UnderlineStyle = 4
	UnderlineDashed UnderlineStyle = 5
)

// Has checks if the attribute is set
func (a CellAttrs) Has(attr CellAttrs) bool {
	return a&attr != 0
}

// Cell represents a single character cell in the terminal with its style.
// This structure is designed to match xterm.js BufferCell for accurate serialization.
type Cell struct {
	Char           rune
	Fg             Color
	Bg             Color
	Attrs          CellAttrs
	Width          uint8          // 0 = placeholder after CJK, 1 = normal, 2 = CJK wide char
	UnderlineStyle UnderlineStyle // Underline style (single, double, curly, etc.)
	UnderlineColor Color          // Underline color (for colored underlines)
}

// NewCell creates a new cell with default styling
func NewCell(ch rune) Cell {
	return Cell{
		Char:           ch,
		Fg:             DefaultColor(),
		Bg:             DefaultColor(),
		Attrs:          AttrNone,
		Width:          1,
		UnderlineStyle: UnderlineNone,
		UnderlineColor: DefaultColor(),
	}
}

// NewStyledCell creates a new cell with specified styling
func NewStyledCell(ch rune, fg, bg Color, attrs CellAttrs) Cell {
	return Cell{
		Char:           ch,
		Fg:             fg,
		Bg:             bg,
		Attrs:          attrs,
		Width:          1,
		UnderlineStyle: UnderlineNone,
		UnderlineColor: DefaultColor(),
	}
}

// NewFullStyledCell creates a new cell with all style options
func NewFullStyledCell(ch rune, fg, bg Color, attrs CellAttrs, width uint8, ulStyle UnderlineStyle, ulColor Color) Cell {
	return Cell{
		Char:           ch,
		Fg:             fg,
		Bg:             bg,
		Attrs:          attrs,
		Width:          width,
		UnderlineStyle: ulStyle,
		UnderlineColor: ulColor,
	}
}

// IsEmpty returns true if the cell is empty (space with default styling)
func (c Cell) IsEmpty() bool {
	return c.Char == ' ' && c.Fg.IsDefault() && c.Bg.IsDefault() && c.Attrs == AttrNone
}

// StyleEquals compares only the style (not the character)
func (c Cell) StyleEquals(other Cell) bool {
	return c.Fg.Equals(other.Fg) && c.Bg.Equals(other.Bg) && c.Attrs == other.Attrs &&
		c.UnderlineStyle == other.UnderlineStyle && c.UnderlineColor.Equals(other.UnderlineColor)
}

// IsAttributeDefault returns true if all attributes are at default values
func (c Cell) IsAttributeDefault() bool {
	return c.Fg.IsDefault() && c.Bg.IsDefault() && c.Attrs == AttrNone &&
		c.UnderlineStyle == UnderlineNone && c.UnderlineColor.IsDefault()
}

// GetWidth returns the cell width (0 for placeholder, 1 for normal, 2 for CJK)
func (c Cell) GetWidth() uint8 {
	if c.Width == 0 {
		return 0
	}
	return c.Width
}
