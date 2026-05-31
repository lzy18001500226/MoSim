package slugkit

import "regexp"

const (
	MinLen = 2
	MaxLen = 100
)

var pattern = regexp.MustCompile(`^[a-z0-9]+(-[a-z0-9]+)*$`)

// Validate returns nil iff s satisfies the slug rule:
// lowercase letters/digits, hyphens between segments, length 2-100,
// not a reserved word.
func Validate(s string) error {
	if len(s) == 0 {
		return ErrEmpty
	}
	if len(s) < MinLen {
		return ErrTooShort
	}
	if len(s) > MaxLen {
		return ErrTooLong
	}
	if !pattern.MatchString(s) {
		return ErrInvalidFormat
	}
	if IsReserved(s) {
		return ErrReserved
	}
	return nil
}
