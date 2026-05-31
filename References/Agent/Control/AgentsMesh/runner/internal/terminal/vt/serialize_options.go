package vt

// SerializeRange specifies a range of lines to serialize
// Matches xterm.js ISerializeRange interface
type SerializeRange struct {
	// Start line (0-indexed, relative to start of history + screen buffer)
	Start int
	// End line (0-indexed, inclusive, relative to start of history + screen buffer)
	End int
}

// SerializeOptions configures how terminal state is serialized
type SerializeOptions struct {
	// ScrollbackLines limits how many scrollback lines to include.
	// 0 means include all available scrollback.
	ScrollbackLines int
	// ExcludeAltBuffer if true, excludes the alternate screen buffer content.
	ExcludeAltBuffer bool
	// ExcludeModes if true, excludes terminal mode settings.
	ExcludeModes bool
	// Range specifies a specific range of lines to serialize.
	// If set, ScrollbackLines is ignored.
	Range *SerializeRange
}

// DefaultSerializeOptions returns sensible defaults for serialization
func DefaultSerializeOptions() SerializeOptions {
	return SerializeOptions{
		ScrollbackLines:  1000,
		ExcludeAltBuffer: false,
		ExcludeModes:     true,
	}
}
