package aggregator

import "unicode/utf8"

// alignToUTF8Boundary adjusts an offset to the next valid UTF-8 character boundary.
// This prevents truncating in the middle of a multi-byte UTF-8 character.
func alignToUTF8Boundary(data []byte, offset int) int {
	if offset >= len(data) {
		return len(data)
	}
	// If we're at the start of a valid UTF-8 character, we're done
	if utf8.RuneStart(data[offset]) {
		return offset
	}
	// Otherwise, advance until we find the start of a valid UTF-8 character
	for offset < len(data) && !utf8.RuneStart(data[offset]) {
		offset++
	}
	return offset
}

// findLastValidUTF8Boundary finds the last position in data that ends on a valid UTF-8 boundary.
// This is used to avoid sending incomplete multi-byte characters at the end of a message.
func findLastValidUTF8Boundary(data []byte) int {
	if len(data) == 0 {
		return 0
	}

	// Check if data already ends on a valid UTF-8 boundary
	for i := len(data) - 1; i >= 0 && i >= len(data)-4; i-- {
		if utf8.RuneStart(data[i]) {
			// Found the start of a UTF-8 character
			// Check if the remaining bytes form a complete character
			r, size := utf8.DecodeRune(data[i:])
			if r != utf8.RuneError || size == len(data)-i {
				// Complete character or valid single byte
				return len(data)
			}
			// Incomplete character - truncate before it
			return i
		}
	}

	// All bytes in the last 4 positions are continuation bytes
	for i := len(data) - 1; i >= 0; i-- {
		if utf8.RuneStart(data[i]) {
			return i
		}
	}

	// No valid UTF-8 start byte found - return all data
	return len(data)
}
